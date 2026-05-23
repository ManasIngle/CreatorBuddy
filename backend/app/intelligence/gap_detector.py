from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.models.competitor import Competitor
from app.models.video import Video
from app.models.content_gap import ContentGap
from app.services.openrouter_service import call_openai, safe_json_loads
from app.services.scraper_service import scraper_service
from app.prompts.gap_prompts import GAP_DETECTION_PROMPT
from app.services.context_optimizer import (
    extract_key_points,
    truncate_to_token_limit
)
from app.utils.cache_manager import scraped_data_cache
import logging

logger = logging.getLogger(__name__)


class GapDetector:

    def detect_gaps(self, channel: Channel, db: Session) -> List[Dict]:
        """
        Gap detection with optimized context.
        Uses topic extraction instead of full content where possible.
        """
        # Get existing channel videos (titles only for efficiency)
        existing_videos = db.query(Video).filter(
            Video.channel_id == channel.id,
            Video.is_competitor_video == False
        ).order_by(Video.view_count.desc()).limit(20).all()
        creator_topics = [v.title for v in existing_videos][:15]  # Limit to 15

        # Get competitor coverage - use only top 3 videos per competitor
        competitors = db.query(Competitor).filter(
            Competitor.channel_id == channel.id
        ).all()
        competitor_coverage = []
        for comp in competitors[:5]:  # Limit to 5 competitors
            competitor_videos = db.query(Video).filter(
                Video.channel_id == channel.id,
                Video.is_competitor_video == True
            ).order_by(Video.view_count.desc()).limit(3).all()  # Reduced to 3
            titles = [v.title for v in competitor_videos]
            competitor_coverage.append(f"{comp.title}: {', '.join(titles)}")

        # Build compact AI prompt
        prompt = GAP_DETECTION_PROMPT.format(
            niche=channel.niche or "general content",
            creator_topics="\n".join(creator_topics),
            competitor_coverage="\n".join(competitor_coverage) if competitor_coverage else "No competitor data",
            audience_questions=""  # populated from comment analysis
        )
        
        # Truncate prompt to safe token limit
        prompt = truncate_to_token_limit(prompt, 1500)

        try:
            ai_response = call_openai(
                system_prompt="You are a content strategist. Return JSON only. Be concise.",
                user_prompt=prompt,
                response_format="json",
                complexity="medium",
                max_tokens=800
            )
            gaps = safe_json_loads(ai_response)
            if isinstance(gaps, dict) and "gaps" in gaps:
                gaps = gaps["gaps"]
            return gaps if isinstance(gaps, list) else []
        except Exception as e:
            logger.error(f"Gap detection failed: {e}")
            return []

    async def enhanced_gap_detection(
        self,
        channel: Channel,
        db: Session,
        include_web_scrape: bool = True
    ) -> Dict:
        """
        Enhanced gap detection with web scraping.
        Scrapes Reddit, Quora, forums, and news for unanswered questions
        and emerging topics.
        """
        # Get base gap analysis
        base_gaps = self.detect_gaps(channel, db)

        if not include_web_scrape:
            return {"base_gaps": base_gaps, "scraped_gaps": []}

        # Scrape external sources for additional gaps
        scraped_insights = {
            "reddit_gaps": [],
            "quora_gaps": [],
            "forum_gaps": [],
            "news_gaps": [],
            "wikipedia_gaps": []
        }

        niche = channel.niche or "general content"

        # Scrape Reddit for unanswered questions
        reddit_trends = await scraper_service.scrape_reddit_trends(
            niche.replace(" ", ""),
            limit=20
        )
        scraped_insights["reddit_gaps"] = reddit_trends

        # Scrape Quora for questions
        discourse = await scraper_service.scrape_audience_discourse(niche)
        scraped_insights["quora_gaps"] = discourse.get("discussions", [])

        # Scrape forum discussions
        forum_discussions = await scraper_service.scrape_forum_discussions(niche)
        scraped_insights["forum_gaps"] = forum_discussions

        # Scrape content ideas for topic gaps
        content_ideas = await scraper_service.scrape_content_ideas(niche)
        scraped_insights["content_ideas"] = content_ideas

        # AI synthesis to find additional gaps
        synthesis_prompt = f"""
        Analyze scraped web data to find content gaps in the '{niche}' niche.

        Base Gaps Detected: {str(base_gaps)[:1500]}
        Reddit Discussions: {str(reddit_trends)[:1500]}
        Forum Questions: {str(forum_discussions)[:1000]}
        Content Ideas: {str(content_ideas)[:1000]}

        Find:
        1. Questions no one is answering
        2. Topics with outdated information
        3. Emerging trends not covered yet
        4. Contradictory information to clarify
        5. Long-tail topics with low competition
        """

        try:
            synthesis = await call_openai(
                system_prompt="You are a content strategist. Return JSON with gaps array.",
                user_prompt=synthesis_prompt,
                response_format="json",
                complexity="medium"
            )
            additional_gaps = safe_json_loads(synthesis)
            scraped_gaps = additional_gaps.get("gaps", [])
        except Exception as e:
            logger.error(f"Scraped gap synthesis failed: {e}")
            scraped_gaps = []

        return {
            "base_gaps": base_gaps,
            "scraped_gaps": scraped_gaps,
            "web_insights": scraped_insights,
            "total_opportunities": len(base_gaps) + len(scraped_gaps)
        }