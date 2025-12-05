from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.competitor import Competitor
from app.models.video import Video
from app.services.youtube_service import (
    fetch_channel_details, fetch_channel_videos,
    fetch_video_statistics
)
from app.services.openrouter_service import call_openai, safe_json_loads
from app.services.scraper_service import scraper_service
from app.prompts.competitor_prompts import (
    COMPETITOR_INTELLIGENCE_PROMPT
)
from app.services.context_optimizer import (
    compress_videos_for_analysis,
    truncate_to_token_limit
)
from app.utils.cache_manager import scraped_data_cache
import json
import logging

logger = logging.getLogger(__name__)


class CompetitorEngine:

    def analyze_competitor(
        self,
        competitor_youtube_id: str,
        creator_niche: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Full competitor analysis with optimized context.
        Uses fewer videos and compressed data to reduce tokens.
        """
        # Step 1: Channel data
        channel_data = fetch_channel_details(competitor_youtube_id)

        # Step 2: Videos - fetch 20, use top 10
        videos = fetch_channel_videos(
            channel_data["uploads_playlist_id"],
            max_results=20
        )
        video_ids = [v["youtube_video_id"] for v in videos]
        video_stats = fetch_video_statistics(video_ids)

        # Sort by views to get top performers
        video_stats.sort(key=lambda x: x["view_count"], reverse=True)
        top_videos = video_stats[:10]  # Reduced from 10 to 5 in compression

        # Step 3: Compress video context for AI (use top 5 only)
        video_context = compress_videos_for_analysis(top_videos, max_videos=5)
        video_context = truncate_to_token_limit(video_context, 1500)

        # Step 4: AI analysis
        prompt_context = COMPETITOR_INTELLIGENCE_PROMPT.format(
            competitor_name=channel_data["title"],
            subscriber_count=channel_data["subscriber_count"],
            top_videos=video_context,
            creator_niche=creator_niche
        )

        try:
            ai_response = call_openai(
                system_prompt="You are a YouTube growth strategist. Return JSON only. Be concise.",
                user_prompt=prompt_context,
                response_format="json",
                complexity="medium"
            )
            intelligence = safe_json_loads(ai_response)
        except Exception as e:
            logger.error(f"Competitor AI analysis failed: {e}")
            intelligence = {
                "why_they_succeed": "",
                "best_formats": [],
                "emotional_triggers": [],
                "content_gaps": [],
                "hook_patterns": [],
                "thumbnail_style": ""
            }

        # Calculate derived metrics
        total_views = sum(v["view_count"] for v in video_stats)
        avg_views = total_views / len(video_stats) if video_stats else 0

        return {
            **channel_data,
            "avg_views": avg_views,
            "why_they_succeed": intelligence.get("why_they_succeed", ""),
            "best_formats": intelligence.get("best_formats", []),
            "emotional_triggers_used": intelligence.get("emotional_triggers", []),
            "content_gaps": intelligence.get("content_gaps", []),
            "hook_patterns": intelligence.get("hook_patterns", []),
            "thumbnail_style": intelligence.get("thumbnail_style", "")
        }

    async def enhanced_competitor_analysis(
        self,
        competitor_youtube_id: str,
        creator_niche: str,
        db: Session,
        include_web_scrape: bool = True
    ) -> Dict[str, Any]:
        """
        Enhanced competitor analysis with aggressive web scraping.
        Scrapes competitor's web presence for comprehensive intelligence.
        """
        # Step 1: Get base analysis from YouTube data
        base_analysis = self.analyze_competitor(
            competitor_youtube_id,
            creator_niche,
            db
        )

        if not include_web_scrape:
            return base_analysis

        # Step 2: Scrape competitor's web presence
        scraped_intel = {
            "website_content": {},
            "social_mentions": {},
            "seo_data": {},
            "content_strategy": {}
        }

        competitor_name = base_analysis.get("title", "")

        # Scrape competitor website if available
        if base_analysis.get("custom_url"):
            website_url = f"https://www.youtube.com/{base_analysis['custom_url']}"
            scraped_intel["website_content"] = await scraper_service.scrape_channel_research(website_url)

        # Scrape social proof
        social_proof = await scraper_service.scrape_social_proof(competitor_name)
        scraped_intel["social_mentions"] = social_proof

        # Scrape SEO data
        seo_data = await scraper_service.scrape_seo_data(competitor_name)
        scraped_intel["seo_data"] = seo_data

        # Step 3: AI synthesis of scraped data
        synthesis_prompt = f"""
        Analyze this competitor's web presence and provide additional insights:

        Competitor: {competitor_name}
        YouTube Analysis: {str(base_analysis)[:2000]}
        Social Mentions: {str(social_proof)[:2000]}
        SEO Data: {str(seo_data)[:1500]}

        Provide:
        1. Brand voice and messaging
        2. Content themes across platforms
        3. Engagement strategies
        4. Collaboration patterns
        5. Monetization approaches
        """

        try:
            synthesis = await call_openai(
                system_prompt="You are a competitor analysis expert. Return concise JSON.",
                user_prompt=synthesis_prompt,
                response_format="json",
                complexity="medium"
            )
            additional_intel = safe_json_loads(synthesis)
        except Exception as e:
            logger.error(f"Scraped data synthesis failed: {e}")
            additional_intel = {}

        return {
            **base_analysis,
            "web_scraped_intelligence": scraped_intel,
            "brand_voice": additional_intel.get("brand_voice", ""),
            "content_themes": additional_intel.get("content_themes", []),
            "engagement_strategies": additional_intel.get("engagement_strategies", []),
            "collaboration_patterns": additional_intel.get("collaboration_patterns", []),
            "monetization_approaches": additional_intel.get("monetization_approaches", []),
            "scrape_timestamp": scraped_data_cache.topic_cache._cache and True or False
        }