from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.models.video import Video
from app.services.openrouter_service import call_openai, safe_json_loads
from app.services.scraper_service import scraper_service
from app.prompts.audience_prompts import AUDIENCE_ANALYSIS_PROMPT
from app.utils.cache_manager import scraped_data_cache
import logging

logger = logging.getLogger(__name__)

class AudienceEngine:

    def analyze_audience(self, channel: Channel, db: Session) -> Dict:
        """
        Analyze the channel's audience based on comments and engagement patterns.
        """
        # Get top videos for comment analysis
        top_videos = db.query(Video).filter(
            Video.channel_id == channel.id
        ).order_by(Video.engagement_rate.desc()).limit(5).all()

        # Build context for AI
        video_context = []
        for v in top_videos:
            video_context.append(
                f"Title: {v.title} | Views: {v.view_count:,} | "
                f"Engagement: {v.engagement_rate:.2%}"
            )

        prompt = f"""
        Analyze this YouTube creator's audience.

        CHANNEL: {channel.title}
        NICHE: {channel.niche or 'general'}
        AUDIENCE TYPE: {channel.audience_type or 'unknown'}

        TOP PERFORMING VIDEOS:
        {chr(10).join(video_context)}

        Based on the channel's content focus and engagement patterns, identify:
        """

        try:
            response = call_openai(
                system_prompt="You are an audience analyst. Return JSON only.",
                user_prompt=prompt,
                response_format="json"
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Audience analysis failed: {e}")
            return {
                "audience_type": "general audience",
                "audience_pain_points": [],
                "content_themes": [],
                "recommended_topics": []
            }

    def get_audience_insights(self, channel: Channel) -> Dict:
        """Get audience insights based on channel profile."""
        return {
            "audience_type": channel.audience_type or "general audience",
            "audience_pain_points": [],
            "content_themes": channel.niche_tags or [],
            "recommended_topics": []
        }

    async def enhanced_audience_analysis(
        self,
        channel: Channel,
        db: Session,
        include_web_scrape: bool = True
    ) -> Dict:
        """
        Enhanced audience analysis with web scraping.
        Scrapes community discussions, fan forums, and related subreddits.
        """
        # Get base audience analysis
        base_analysis = self.analyze_audience(channel, db)

        if not include_web_scrape:
            return base_analysis

        scraped_insights = {
            "community_questions": [],
            "forum_discussions": [],
            "reddit_insights": [],
            "trending_topics": []
        }

        niche = channel.niche or "general"

        # Scrape community discussions
        discourse = await scraper_service.scrape_audience_discourse(niche)
        scraped_insights["community_questions"] = discourse.get("questions", [])

        # Scrape forum discussions
        forum_data = await scraper_service.scrape_forum_discussions(niche)
        scraped_insights["forum_discussions"] = forum_data

        # Scrape Reddit for audience insights
        reddit_data = await scraper_service.scrape_reddit_trends(niche.replace(" ", ""))
        scraped_insights["reddit_insights"] = reddit_data

        # Scrape trend aggregator
        trends = await scraper_service.scrape_trend_aggregator(niche)
        scraped_insights["trending_topics"] = trends

        # AI synthesis of scraped data
        synthesis_prompt = f"""
        Analyze scraped audience data for the '{niche}' niche.

        Base Audience Analysis: {str(base_analysis)[:1500]}
        Community Questions: {str(discourse.get('discussions', []))[:1500]}
        Forum Discussions: {str(forum_data)[:1000]}
        Reddit Insights: {str(reddit_data)[:1000]}

        Provide:
        1. Key audience questions and concerns
        2. Trending topics audiences care about
        3. Unmet needs and pain points
        4. Content opportunities
        5. Engagement strategies that would resonate
        """

        try:
            synthesis = await call_openai(
                system_prompt="You are an audience research expert. Return JSON.",
                user_prompt=synthesis_prompt,
                response_format="json",
                complexity="medium"
            )
            additional_insights = safe_json_loads(synthesis)
        except Exception as e:
            logger.error(f"Scraped audience synthesis failed: {e}")
            additional_insights = {}

        return {
            **base_analysis,
            "scraped_insights": scraped_insights,
            "trending_topics": additional_insights.get("trending_topics", []),
            "key_questions": additional_insights.get("key_questions", []),
            "content_opportunities": additional_insights.get("content_opportunities", []),
            "engagement_recommendations": additional_insights.get("engagement_recommendations", [])
        }