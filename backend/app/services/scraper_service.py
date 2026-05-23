"""
Web Scraping Service for CreatorIQ Platform
Provides aggressive web scraping capabilities for real-time intelligence gathering
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime, timedelta
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
import re
from html.parser import HTMLParser
from app.utils.cache_manager import scraped_data_cache

logger = logging.getLogger(__name__)


class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.ignore_tags = {"script", "style", "head", "title", "meta", "link", "noscript"}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        if self.current_tag == tag:
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            text = data.strip()
            if text:
                self.result.append(text)

    def get_text(self):
        return "\n".join(self.result)


def clean_html(html_content: str) -> str:
    """Extract clean, readable text from raw HTML to feed to the LLM."""
    try:
        # Strip comments
        html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        text = parser.get_text()
        # Compress multiple blank lines
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        return text[:8000]  # Limit to 8k of clean text
    except Exception as e:
        logger.warning(f"HTML cleanup failed: {e}")
        return html_content[:4000]  # Fallback to truncated raw html



class ScraperService:
    """
    Advanced web scraping service for gathering intelligence from multiple sources.
    Uses Firecrawl for intelligent crawling and scraping capabilities.
    """
    
    def __init__(self):
        self.firecrawl_api_key = None
        self.timeout = 30  # Max 30 seconds per scrape
        self.max_results = 10
        self._init_firecrawl()
    
    def _init_firecrawl(self):
        """Initialize Firecrawl client if API key is available"""
        try:
            from firecrawl import FirecrawlClient
            import os
            api_key = os.getenv("FIRECRAWL_API_KEY")
            if api_key:
                self.firecrawl = FirecrawlClient(api_key=api_key)
                logger.info("Firecrawl client initialized successfully")
            else:
                logger.warning("FIRECRAWL_API_KEY not set - scraping will use fallback methods")
                self.firecrawl = None
        except ImportError:
            logger.warning("Firecrawl not installed - using fallback scraping methods")
            self.firecrawl = None
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _scrape_with_firecrawl(self, url: str, formats: list = ["markdown"]) -> Optional[dict]:
        """Scrape a single URL using Firecrawl"""
        if not self.firecrawl:
            return None
        try:
            result = await asyncio.wait_for(
                self.firecrawl.scrape_url(url, formats=formats),
                timeout=self.timeout
            )
            return result
        except Exception as e:
            logger.error(f"Firecrawl scrape failed for {url}: {str(e)}")
            return None
    
    async def _fallback_scrape(self, url: str) -> Optional[dict]:
        """Fallback scraping using httpx when Firecrawl is unavailable"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return {
                    "markdown": clean_html(response.text),
                    "metadata": {
                        "title": url,
                        "description": "",
                        "source": url
                    }
                }
        except Exception as e:
            logger.error(f"Fallback scrape failed for {url}: {str(e)}")
            return None
    
    async def scrape_channel_research(self, channel_url: str) -> dict:
        """
        Scrape competitor's website, social profiles, and public content
        Returns structured intelligence data
        """
        result = {
            "url": channel_url,
            "scraped_at": datetime.utcnow().isoformat(),
            "content": {},
            "success": False,
            "sources_used": []
        }
        
        # Try Firecrawl first, then fallback
        if self.firecrawl:
            data = await self._scrape_with_firecrawl(channel_url)
            if data:
                result["content"] = data
                result["success"] = True
                result["sources_used"].append(channel_url)
        else:
            data = await self._fallback_scrape(channel_url)
            if data:
                result["content"] = data
                result["success"] = True
                result["sources_used"].append(channel_url)
        
        return result
    
    async def scrape_trend_aggregator(self, topic: str) -> list:
        """
        Scrape multiple sources for trend data (Reddit, Twitter, news)
        Returns list of trend data points
        """
        cached = scraped_data_cache.trend_cache.get(topic)
        if cached is not None:
            logger.debug(f"Cache hit for trend aggregator: {topic}")
            return cached

        trends = []
        
        # Sources to scrape for trends
        sources = [
            f"https://www.reddit.com/search.json?q={topic}&sort=hot",
            f"https://news.google.com/search?q={topic}&hl=en-US&gl=US&ceid=US:en",
        ]
        
        for source_url in sources:
            try:
                if self.firecrawl:
                    data = await self._scrape_with_firecrawl(source_url)
                    if data and "markdown" in data:
                        trends.append({
                            "source": source_url,
                            "content": data["markdown"][:2000],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                else:
                    data = await self._fallback_scrape(source_url)
                    if data:
                        trends.append({
                            "source": source_url,
                            "content": data.get("markdown", "")[:2000],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
            except Exception as e:
                logger.error(f"Trend scrape failed for {source_url}: {str(e)}")
                continue
        
        scraped_data_cache.trend_cache.set(topic, trends)
        return trends
    
    async def scrape_content_ideas(self, niche: str) -> list:
        """
        Scrape for content inspiration (Wikipedia, forums, blogs)
        Returns list of content ideas with sources
        """
        cache_key = f"ideas:{niche}"
        cached = scraped_data_cache.topic_cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for content ideas: {niche}")
            return cached

        ideas = []
        
        # Sources to scrape for trends
        sources = [
            f"https://en.wikipedia.org/wiki/Special:Search?search={niche}",
            f"https://www.google.com/search?q={niche}+site:forums.reddit.com",
        ]
        
        for source_url in sources:
            try:
                if self.firecrawl:
                    data = await self._scrape_with_firecrawl(source_url)
                    if data and "markdown" in data:
                        ideas.append({
                            "source": source_url,
                            "content": data["markdown"][:3000],
                            "type": "content_idea",
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                else:
                    data = await self._fallback_scrape(source_url)
                    if data:
                        ideas.append({
                            "source": source_url,
                            "content": data.get("markdown", "")[:3000],
                            "type": "content_idea",
                            "scraped_at": datetime.utcnow().isoformat()
                        })
            except Exception as e:
                logger.error(f"Content ideas scrape failed: {str(e)}")
                continue
        
        scraped_data_cache.topic_cache.set(cache_key, ideas)
        return ideas
    
    async def scrape_audience_discourse(self, topic: str) -> dict:
        """
        Scrape discussions, Q&A sites, forums for audience questions
        Returns structured audience discourse data
        """
        cached = scraped_data_cache.audience_cache.get(topic)
        if cached is not None:
            logger.debug(f"Cache hit for audience discourse: {topic}")
            return cached

        discourse = {
            "topic": topic,
            "questions": [],
            "pain_points": [],
            "discussions": [],
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        sources = [
            f"https://www.quora.com/search?q={topic}",
            f"https://www.reddit.com/r/{topic}/hot.json",
        ]
        
        for source_url in sources:
            try:
                if self.firecrawl:
                    data = await self._scrape_with_firecrawl(source_url)
                    if data and "markdown" in data:
                        discourse["discussions"].append({
                            "source": source_url,
                            "content": data["markdown"][:2500],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                else:
                    data = await self._fallback_scrape(source_url)
                    if data:
                        discourse["discussions"].append({
                            "source": source_url,
                            "content": data.get("markdown", "")[:2500],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
            except Exception as e:
                logger.error(f"Discourse scrape failed: {str(e)}")
                continue
        
        scraped_data_cache.audience_cache.set(topic, discourse)
        return discourse
    
    async def scrape_social_proof(self, creator_name: str) -> dict:
        """
        Scrape testimonials, reviews, engagement metrics
        Returns social proof data
        """
        social_proof = {
            "creator": creator_name,
            "testimonials": [],
            "mentions": [],
            "engagement_metrics": {},
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        sources = [
            f"https://www.google.com/search?q={creator_name}+review",
            f"https://www.google.com/search?q={creator_name}+testimonial",
        ]
        
        for source_url in sources:
            try:
                if self.firecrawl:
                    data = await self._scrape_with_firecrawl(source_url)
                    if data and "markdown" in data:
                        social_proof["mentions"].append({
                            "source": source_url,
                            "content": data["markdown"][:2000],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
                else:
                    data = await self._fallback_scrape(source_url)
                    if data:
                        social_proof["mentions"].append({
                            "source": source_url,
                            "content": data.get("markdown", "")[:2000],
                            "scraped_at": datetime.utcnow().isoformat()
                        })
            except Exception as e:
                logger.error(f"Social proof scrape failed: {str(e)}")
                continue
        
        return social_proof
    
    async def scrape_seo_data(self, keyword: str) -> dict:
        """
        Scrape search results, SERP features, keyword difficulty
        Returns SEO data for the keyword
        """
        seo_data = {
            "keyword": keyword,
            "serp_features": [],
            "top_results": [],
            "related_keywords": [],
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        try:
            source_url = f"https://www.google.com/search?q={keyword}&hl=en"
            if self.firecrawl:
                data = await self._scrape_with_firecrawl(source_url)
                if data and "markdown" in data:
                    seo_data["top_results"].append({
                        "source": source_url,
                        "content": data["markdown"][:4000],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
            else:
                data = await self._fallback_scrape(source_url)
                if data:
                    seo_data["top_results"].append({
                        "source": source_url,
                        "content": data.get("markdown", "")[:4000],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            logger.error(f"SEO scrape failed: {str(e)}")
        
        return seo_data
    
    async def scrape_youtube_intelligence(self, channel_url: str) -> dict:
        """
        Scrape YouTube channel page for content strategy insights
        """
        intel = {
            "channel_url": channel_url,
            "video_titles": [],
            "descriptions": [],
            "tags": [],
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        try:
            if self.firecrawl:
                data = await self._scrape_with_firecrawl(channel_url)
                if data and "markdown" in data:
                    intel["content"] = data["markdown"][:5000]
                    intel["success"] = True
            else:
                data = await self._fallback_scrape(channel_url)
                if data:
                    intel["content"] = data.get("markdown", "")[:5000]
                    intel["success"] = True
        except Exception as e:
            logger.error(f"YouTube intelligence scrape failed: {str(e)}")
            intel["success"] = False
        
        return intel
    
    async def scrape_reddit_trends(self, subreddit: str, limit: int = 25) -> list:
        """
        Scrape Reddit for trending posts in a subreddit
        """
        trends = []
        
        try:
            source_url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
            if self.firecrawl:
                data = await self._scrape_with_firecrawl(source_url, formats=["json"])
                if data:
                    trends.append({
                        "subreddit": subreddit,
                        "data": data,
                        "scraped_at": datetime.utcnow().isoformat()
                    })
            else:
                data = await self._fallback_scrape(source_url)
                if data:
                    trends.append({
                        "subreddit": subreddit,
                        "data": data.get("markdown", "")[:3000],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            logger.error(f"Reddit trends scrape failed: {str(e)}")
        
        return trends
    
    async def scrape_forum_discussions(self, topic: str, forum_type: str = "general") -> list:
        """
        Scrape forum discussions for audience insights
        """
        discussions = []
        
        forum_urls = {
            "reddit": f"https://www.reddit.com/search.json?q={topic}&sort=hot",
            "quora": f"https://www.quora.com/search?q={topic}",
            "stackoverflow": f"https://stackoverflow.com/search?q={topic}",
        }
        
        source_url = forum_urls.get(forum_type, forum_urls["reddit"])
        
        try:
            if self.firecrawl:
                data = await self._scrape_with_firecrawl(source_url)
                if data and "markdown" in data:
                    discussions.append({
                        "forum_type": forum_type,
                        "topic": topic,
                        "content": data["markdown"][:3000],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
            else:
                data = await self._fallback_scrape(source_url)
                if data:
                    discussions.append({
                        "forum_type": forum_type,
                        "topic": topic,
                        "content": data.get("markdown", "")[:3000],
                        "scraped_at": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            logger.error(f"Forum discussions scrape failed: {str(e)}")
        
        return discussions
    
    async def multi_source_research(self, topic: str, niche: str) -> dict:
        """
        Aggregate data from multiple sources for comprehensive research
        """
        research = {
            "topic": topic,
            "niche": niche,
            "sources": [],
            "insights": {},
            "scraped_at": datetime.utcnow().isoformat(),
            "success": False
        }
        
        # Scrape multiple sources concurrently
        tasks = [
            self.scrape_trend_aggregator(topic),
            self.scrape_content_ideas(niche),
            self.scrape_audience_discourse(topic),
            self.scrape_reddit_trends(niche.replace(" ", ""), 10),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Multi-source research task {i} failed: {str(result)}")
                continue
            if isinstance(result, list):
                research["sources"].extend(result)
            elif isinstance(result, dict):
                if "discussions" in result:
                    research["sources"].append(result)
        
        if research["sources"]:
            research["success"] = True
        
        return research


# Global instance
scraper_service = ScraperService()