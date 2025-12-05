"""
Trend Detection Engine with Web Scraping
Provides real-time trend detection using web scraping
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.services.openrouter_service import call_openai, safe_json_loads
from app.services.scraper_service import scraper_service
from app.utils.cache_manager import scraped_data_cache
import logging

logger = logging.getLogger(__name__)


class TrendEngine:
    """
    Advanced trend detection with aggressive web scraping.
    Gathers real-time data from Twitter, Reddit, news, and YouTube.
    """

    async def detect_trends(self, niche: str, time_range: str = "week") -> List[Dict]:
        """
        Detect trends in a niche using web scraping.
        
        Args:
            niche: The niche to analyze
            time_range: Time range for trends (day, week, month)
        
        Returns:
            List of detected trends with sources
        """
        trends = []

        # Try cache first
        cached_trends = scraped_data_cache.get_trends(niche)
        if cached_trends:
            logger.info(f"Returning cached trends for {niche}")
            return cached_trends

        # Scrape multiple sources for trends
        scraped_data = await self._scrape_trend_sources(niche)

        # AI analysis of scraped data
        analysis = await self._analyze_trends(scraped_data, niche)

        trends = analysis.get("trends", [])

        # Cache results
        scraped_data_cache.cache_trends(niche, trends)

        return trends

    async def _scrape_trend_sources(self, niche: str) -> Dict:
        """Scrape multiple sources for trend data"""
        scraped = {
            "reddit": [],
            "news": [],
            "forums": [],
            "social": []
        }

        # Scrape Reddit trends
        reddit_trends = await scraper_service.scrape_reddit_trends(
            niche.replace(" ", ""),
            limit=25
        )
        scraped["reddit"] = reddit_trends

        # Scrape general trends
        general_trends = await scraper_service.scrape_trend_aggregator(niche)
        scraped["news"] = general_trends

        # Scrape forum discussions
        forum_data = await scraper_service.scrape_forum_discussions(niche)
        scraped["forums"] = forum_data

        return scraped

    async def _analyze_trends(self, scraped_data: Dict, niche: str) -> Dict:
        """AI analysis of scraped trend data"""
        prompt = f"""
        Analyze these scraped trends for the '{niche}' niche.

        Reddit Trends: {str(scraped_data.get('reddit', []))[:2000]}
        News Trends: {str(scraped_data.get('news', []))[:2000]}
        Forum Discussions: {str(scraped_data.get('forums', []))[:1500]}

        Identify:
        1. Top 10 trending topics with scores
        2. Rising trends (acceleration)
        3. Stable trends (consistent)
        4. Declining trends to avoid
        5. Emerging opportunities

        Return JSON with 'trends' array containing: topic, score, velocity, type, sources
        """

        try:
            response = await call_openai(
                system_prompt="You are a trend analyst. Return JSON only.",
                user_prompt=prompt,
                response_format="json",
                complexity="medium"
            )
            return safe_json_loads(response)
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {"trends": []}

    async def enhanced_trend_detection(
        self,
        niche: str,
        include_twitter: bool = True,
        include_youtube: bool = True
    ) -> Dict:
        """
        Enhanced trend detection with platform-specific scraping.
        
        Args:
            niche: The niche to analyze
            include_twitter: Include Twitter/X trends
            include_youtube: Include YouTube search suggestions
        
        Returns:
            Comprehensive trend analysis
        """
        # Base trend detection
        trends = await self.detect_trends(niche)

        additional_insights = {
            "real_time_trends": [],
            "platform_specific": {},
            "bursting_topics": [],
            "sustained_growth": []
        }

        # Scrape for real-time trends
        discourse = await scraper_service.scrape_audience_discourse(niche)
        if discourse.get("discussions"):
            additional_insights["real_time_trends"] = discourse["discussions"]

        # AI categorization of trends
        if trends:
            categorization_prompt = f"""
            Categorize these trends for '{niche}':

            Trends: {str(trends)[:3000]}

            Categorize into:
            - bursting_topics: Rapid sudden growth
            - sustained_growth: Consistent long-term growth
            - platform_specific: Platform-unique trends
            - emerging_opportunities: New trends to capitalize on
            """

            try:
                categorization = await call_openai(
                    system_prompt="You are a trend analyst. Return JSON.",
                    user_prompt=categorization_prompt,
                    response_format="json",
                    complexity="medium"
                )
                additional_insights.update(safe_json_loads(categorization))
            except Exception as e:
                logger.error(f"Trend categorization failed: {e}")

        return {
            "niche": niche,
            "trends": trends,
            "additional_insights": additional_insights,
            "analyzed_at": datetime.utcnow().isoformat(),
            "sources": ["reddit", "news", "forums", "community"]
        }

    async def get_breaking_topics(self, niche: str) -> List[Dict]:
        """
        Get breaking/popping topics from multiple real-time sources.
        """
        breaking = []

        # Scrape multiple urgent sources
        tasks = [
            scraper_service.scrape_trend_aggregator(niche),
            scraper_service.scrape_reddit_trends(niche.replace(" ", ""), 10),
            scraper_service.scrape_forum_discussions(niche, "reddit")
        ]

        results = await self._gather_with_fallback(tasks)

        for result in results:
            if isinstance(result, list):
                breaking.extend(result[:5])  # Top 5 from each source

        return breaking[:20]  # Return top 20 total

    async def _gather_with_fallback(self, tasks) -> List:
        """Gather tasks with graceful fallback on failure"""
        import asyncio
        results = []
        for task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=15.0)
                results.append(result)
            except Exception as e:
                logger.error(f"Task failed in _gather_with_fallback: {e}")
                results.append([])
        return results

    async def get_rising_searches(self, keyword: str) -> List[str]:
        """
        Get rising search queries for a keyword (YouTube suggest style).
        """
        try:
            # Scrape YouTube search data
            intel = await scraper_service.scrape_youtube_intelligence(
                f"https://www.youtube.com/results?search_query={keyword}"
            )

            if intel.get("success"):
                # Extract suggested searches from scraped content
                prompt = f"""
                Extract rising search queries from this YouTube search data:

                {str(intel.get('content', ''))[:3000]}

                Return JSON with 'searches' array of rising queries.
                """

                response = await call_openai(
                    system_prompt="You are a keyword research expert. Return JSON.",
                    user_prompt=prompt,
                    response_format="json",
                    complexity="simple"
                )
                data = safe_json_loads(response)
                return data.get("searches", [])
        except Exception as e:
            logger.error(f"Rising searches extraction failed: {e}")

        return []


# Global trend engine instance
trend_engine = TrendEngine()