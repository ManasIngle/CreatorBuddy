"""
Content Gap Detector — embedding-first, LLM-only-at-synthesis.

Strategy (§4.4 of IMPLEMENTATION.md):
1. Embed all creator video titles  → stored on Video.content_embedding
2. Find competitor titles whose nearest creator-title cosine distance > threshold
   (pgvector ANN query — pure SQL, no LLM)
3. Optionally enrich with scraped Reddit/Quora questions
4. ONE LLM call to cluster, score, and name the gaps

Cost: ~$0.001/run vs ~$0.005 for the old pure-LLM approach.
Quality: higher — the candidate set is data-driven, not vibes-driven.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.channel import Channel
from app.models.competitor import Competitor
from app.models.video import Video
from app.models.content_gap import ContentGap
from app.services.openrouter_service import call_openai, safe_json_loads
from app.services.embedding_service import get_content_embedding
from app.services.scraper_service import scraper_service
from app.prompts.gap_prompts import GAP_DETECTION_PROMPT
from app.services.context_optimizer import truncate_to_token_limit
from app.utils.cache_manager import scraped_data_cache

logger = logging.getLogger(__name__)

# Cosine distance threshold — competitor titles farther than this from ANY
# creator title are "uncovered" topics. 0.4 ≈ semantically unrelated.
_GAP_DISTANCE_THRESHOLD = 0.4

# How many candidate uncovered competitor titles to feed into the LLM
_MAX_CANDIDATE_TITLES = 30

# How many final gaps to request
_MAX_GAPS = 8


class GapDetector:
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_gaps(self, channel: Channel, db: Session, user_id: Optional[str] = None) -> List[Dict]:
        """
        Embedding-based gap detection.  Fast, cheap, data-driven.

        Falls back to title-only LLM approach if embeddings aren't available yet
        (e.g. right after initial channel analysis before embeddings are computed).
        """
        candidates = self._find_uncovered_by_embeddings(channel, db)

        if not candidates:
            # Fallback: no embeddings yet — use title lists
            logger.info(
                f"No embeddings for channel {channel.id}, falling back to title-based detection"
            )
            candidates = self._find_uncovered_by_titles(channel, db)

        if not candidates:
            return []

        return self._synthesize_gaps(candidates, channel, extra_context="", user_id=user_id)

    async def enhanced_gap_detection(
        self,
        channel: Channel,
        db: Session,
        include_web_scrape: bool = True,
        user_id: Optional[str] = None,
    ) -> Dict:
        """
        Enhanced gap detection that layers web scraping on top of embedding-based detection.
        Scrapes Reddit, Quora, and forums for unanswered questions, then combines with
        embedding candidates before the single LLM synthesis call.
        """
        # Step 1: get embedding-based candidates (fast, no LLM)
        candidates = self._find_uncovered_by_embeddings(channel, db)
        if not candidates:
            candidates = self._find_uncovered_by_titles(channel, db)

        scraped_context = ""
        scraped_insights: Dict = {}

        if include_web_scrape and channel.niche:
            niche = channel.niche
            # Scrape in parallel — each source is independent
            import asyncio
            reddit_task = scraper_service.scrape_reddit_trends(
                niche.replace(" ", ""), limit=20
            )
            discourse_task = scraper_service.scrape_audience_discourse(niche)
            forum_task = scraper_service.scrape_forum_discussions(niche)

            reddit, discourse, forum = await asyncio.gather(
                reddit_task, discourse_task, forum_task, return_exceptions=True
            )

            scraped_insights = {
                "reddit_gaps": reddit if not isinstance(reddit, Exception) else [],
                "quora_gaps": (
                    discourse.get("discussions", [])
                    if not isinstance(discourse, Exception)
                    else []
                ),
                "forum_gaps": forum if not isinstance(forum, Exception) else [],
            }

            # Build a compact text snippet for the LLM synthesis step
            reddit_text = str(scraped_insights["reddit_gaps"])[:800]
            quora_text = str(scraped_insights["quora_gaps"])[:600]
            scraped_context = (
                f"\nReddit discussions: {reddit_text}"
                f"\nQuora questions: {quora_text}"
            )

        # Step 2: ONE LLM call using enriched context
        gaps = self._synthesize_gaps(candidates, channel, extra_context=scraped_context, user_id=user_id)

        return {
            "base_gaps": gaps,
            "scraped_insights": scraped_insights,
            "total_opportunities": len(gaps),
            "method": "embedding+scrape" if scraped_context else "embedding",
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_uncovered_by_embeddings(
        self, channel: Channel, db: Session
    ) -> List[str]:
        """
        Use pgvector to find competitor video titles that are semantically
        far from all of the creator's own videos.

        The SQL uses <=> (cosine distance). A distance > threshold means the
        creator hasn't made content on that topic.

        Returns a list of title strings (not DB rows) to keep the caller lean.
        """
        try:
            # Check whether any embeddings exist for this channel
            sample = (
                db.query(Video.content_embedding)
                .filter(
                    Video.channel_id == channel.id,
                    Video.is_competitor_video.is_(False),
                    Video.content_embedding.isnot(None),
                )
                .first()
            )
            if sample is None:
                return []

            # Raw SQL — SQLAlchemy ORM doesn't have first-class pgvector filter support
            result = db.execute(
                text(
                    """
                    SELECT cv.title
                    FROM videos cv
                    WHERE cv.channel_id = :channel_id
                      AND cv.is_competitor_video = true
                      AND cv.content_embedding IS NOT NULL
                      AND NOT EXISTS (
                          SELECT 1 FROM videos mv
                          WHERE mv.channel_id = :channel_id
                            AND mv.is_competitor_video = false
                            AND mv.content_embedding IS NOT NULL
                            AND (cv.content_embedding <=> mv.content_embedding) < :threshold
                      )
                    ORDER BY cv.view_count DESC
                    LIMIT :limit
                    """
                ),
                {
                    "channel_id": str(channel.id),
                    "threshold": _GAP_DISTANCE_THRESHOLD,
                    "limit": _MAX_CANDIDATE_TITLES,
                },
            )
            titles = [row[0] for row in result.fetchall()]
            logger.info(
                f"Embedding gap detection found {len(titles)} uncovered titles "
                f"for channel {channel.id}"
            )
            return titles

        except Exception as e:
            logger.warning(f"Embedding gap detection failed: {e}")
            return []

    def _find_uncovered_by_titles(
        self, channel: Channel, db: Session
    ) -> List[str]:
        """
        Fallback when embeddings aren't available.
        Returns competitor titles not also present in creator's catalog (naive string match).
        """
        creator_titles = set(
            t
            for (t,) in db.query(Video.title)
            .filter(
                Video.channel_id == channel.id,
                Video.is_competitor_video.is_(False),
            )
            .limit(50)
            .all()
        )

        competitor_titles = [
            t
            for (t,) in db.query(Video.title)
            .filter(
                Video.channel_id == channel.id,
                Video.is_competitor_video.is_(True),
            )
            .order_by(Video.view_count.desc())
            .limit(_MAX_CANDIDATE_TITLES * 2)
            .all()
            if t not in creator_titles
        ]
        return competitor_titles[:_MAX_CANDIDATE_TITLES]

    def _synthesize_gaps(
        self,
        candidate_titles: List[str],
        channel: Channel,
        extra_context: str = "",
        user_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Single LLM call that clusters candidates into N gaps, scores each,
        and suggests an angle + title.

        This is the ONLY LLM call in the entire gap-detection pipeline.
        """
        if not candidate_titles:
            return []

        titles_block = "\n".join(f"- {t}" for t in candidate_titles)
        titles_block = truncate_to_token_limit(titles_block, 1200)

        prompt = (
            f"Niche: {channel.niche or 'general content'}\n"
            f"Creator already covers: {', '.join([v.title for v in []])}\n\n"
            f"Competitor video titles NOT covered by the creator:\n{titles_block}"
            f"{extra_context}\n\n"
            f"Identify the {_MAX_GAPS} highest-opportunity content gaps. "
            f"Group related titles into single gap themes. For each gap provide: "
            f"topic, reason, opportunity_score (1-10), competition_level (low/medium/high), "
            f"trend_direction (rising/stable/declining), suggested_angle, suggested_title."
        )

        try:
            response = call_openai(
                system_prompt=(
                    "You are a YouTube content strategist. "
                    "Return JSON only with a 'gaps' array. No preamble."
                ),
                user_prompt=prompt,
                response_format="json",
                complexity="medium",
                max_tokens=800,
                operation="gap_detection",
                user_id=user_id,
                cache_ttl=43200,  # 12h — gaps are relatively stable
            )
            data = safe_json_loads(response)
            gaps = data.get("gaps", []) if isinstance(data, dict) else []
            return gaps if isinstance(gaps, list) else []
        except Exception as e:
            logger.error(f"Gap synthesis LLM call failed: {e}")
            return []
