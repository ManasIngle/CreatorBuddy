"""
Smart scraper router — picks the cheapest strategy that works for each URL.

Decision tree:
    1. URL matches a known source pattern (reddit.com, wikipedia.org, hn,
       news.google.com, youtube suggest)  →  use the structured client.
    2. Generic HTTP fetch via httpx + selectolax. Sufficient for ~70% of pages.
    3. If response is ~empty (likely JS-rendered SPA), retry with Playwright.
    4. If everything failed AND FIRECRAWL_API_KEY is set, last-resort Firecrawl.

Public surface mirrors what existing code expects from `scraper_service`,
so callers don't need to change.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Any
from urllib.parse import urlparse, quote_plus

from . import sources
from .http_client import fetch_url, ScrapeResult, batch_fetch
from . import browser

logger = logging.getLogger(__name__)

# When HTTP returns less than this many chars of clean text, escalate to browser
_THIN_RESPONSE_THRESHOLD = 200


class SmartScraper:
    """
    The class CreatorIQ engines should use. Mirrors the surface of the
    existing scraper_service.ScraperService for drop-in replacement.
    """

    # ------------------------------------------------------------------
    # Generic fetchers
    # ------------------------------------------------------------------

    async def fetch_url(self, url: str, *, render_if_empty: bool = True) -> ScrapeResult:
        """
        Generic URL fetch. Tries HTTP first; escalates to headless browser if
        the response looks JS-rendered (very little extracted text).
        """
        result = await fetch_url(url)
        if (
            render_if_empty
            and result.success
            and len(result.text) < _THIN_RESPONSE_THRESHOLD
            and browser.is_available()
        ):
            logger.info(f"HTTP returned thin text ({len(result.text)} chars), escalating to browser: {url}")
            rendered = await browser.fetch_rendered(url)
            if rendered.success and len(rendered.text) > len(result.text):
                return rendered
        if not result.success:
            return await self._firecrawl_fallback(url, result)
        return result

    async def smart_fetch(self, url: str) -> ScrapeResult:
        """
        Route by URL pattern to the most efficient backend.
        Returns ScrapeResult — caller uses .text, .title, .source.
        """
        host = urlparse(url).netloc.lower()
        if "reddit.com" in host:
            # The .json endpoint is the structured way; if caller passed a thread URL,
            # convert to JSON form
            if not url.endswith(".json"):
                url = url.rstrip("/") + ".json"
            data = await self._reddit_url(url)
            return ScrapeResult(url=url, status=200, text=str(data)[:8000], success=bool(data), source="reddit")
        if "wikipedia.org" in host:
            return await self.fetch_url(url, render_if_empty=False)
        return await self.fetch_url(url)

    # ------------------------------------------------------------------
    # Drop-in replacements for existing scraper_service methods
    # These mirror the signatures the engines already call.
    # ------------------------------------------------------------------

    async def scrape_reddit_trends(self, subreddit: str, limit: int = 25) -> list[dict]:
        return [{
            "subreddit": subreddit,
            "data": await sources.reddit_hot(subreddit, limit=limit),
            "scraped_at": datetime.utcnow().isoformat(),
            "source": "reddit_json",
        }]

    async def scrape_audience_discourse(self, topic: str) -> dict:
        # Pull from multiple Q&A-shaped sources concurrently
        reddit_q, hn, stack = await asyncio.gather(
            sources.reddit_search(topic, limit=20),
            sources.hackernews_search(topic, hits=20),
            sources.stackexchange_search(topic, limit=15),
            return_exceptions=True,
        )
        questions = [
            *(p.get("title", "") for p in (reddit_q if not isinstance(reddit_q, Exception) else []) if isinstance(p, dict)),
            *(h.get("title", "") for h in (hn if not isinstance(hn, Exception) else []) if isinstance(h, dict)),
            *(q.get("title", "") for q in (stack if not isinstance(stack, Exception) else []) if isinstance(q, dict)),
        ]
        return {
            "topic": topic,
            "questions": [q for q in questions if q.endswith("?")][:30],
            "discussions": [
                {"source": "reddit", "data": reddit_q if not isinstance(reddit_q, Exception) else []},
                {"source": "hackernews", "data": hn if not isinstance(hn, Exception) else []},
                {"source": "stackexchange", "data": stack if not isinstance(stack, Exception) else []},
            ],
            "scraped_at": datetime.utcnow().isoformat(),
        }

    async def scrape_forum_discussions(self, topic: str, forum_type: str = "reddit") -> list[dict]:
        if forum_type == "reddit":
            return await sources.reddit_search(topic, limit=25)
        if forum_type == "stackoverflow":
            return await sources.stackexchange_search(topic, site="stackoverflow", limit=25)
        if forum_type == "hackernews":
            return await sources.hackernews_search(topic, hits=25)
        # Fallback: search reddit
        return await sources.reddit_search(topic, limit=25)

    async def scrape_trend_aggregator(self, topic: str) -> list[dict]:
        """News + reddit + youtube suggestions as a single trend snapshot."""
        news, reddit, suggestions = await asyncio.gather(
            sources.google_news(topic, limit=20),
            sources.reddit_search(topic, limit=15, sort="hot"),
            sources.youtube_suggest(topic),
            return_exceptions=True,
        )
        items = []
        if not isinstance(news, Exception):
            for n in news:
                items.append({**n, "source_type": "news"})
        if not isinstance(reddit, Exception):
            for r in reddit:
                items.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "source_type": "reddit",
                    "score": r.get("score", 0),
                })
        if not isinstance(suggestions, Exception):
            for s in suggestions:
                items.append({"title": s, "source_type": "youtube_suggest"})
        return items

    async def scrape_content_ideas(self, niche: str) -> list[dict]:
        wiki, hn, suggest = await asyncio.gather(
            sources.wikipedia_search(niche, limit=10),
            sources.hackernews_search(niche, hits=10),
            sources.youtube_suggest(niche),
            return_exceptions=True,
        )
        ideas = []
        if not isinstance(wiki, Exception):
            for w in wiki:
                ideas.append({
                    "source": "wikipedia",
                    "title": w.get("title"),
                    "snippet": w.get("snippet"),
                    "url": w.get("url"),
                    "type": "encyclopedic",
                })
        if not isinstance(hn, Exception):
            for h in hn:
                ideas.append({
                    "source": "hackernews",
                    "title": h.get("title"),
                    "url": h.get("url"),
                    "type": "discussion",
                    "popularity": h.get("points", 0),
                })
        if not isinstance(suggest, Exception):
            for s in suggest:
                ideas.append({"source": "youtube_suggest", "title": s, "type": "search_query"})
        return ideas

    async def scrape_seo_data(self, keyword: str) -> dict:
        """SEO surrogate: YT suggest + HN + Wikipedia. No Google scrape needed."""
        suggest, hn, wiki = await asyncio.gather(
            sources.youtube_suggest(keyword),
            sources.hackernews_search(keyword, hits=20),
            sources.wikipedia_search(keyword, limit=5),
            return_exceptions=True,
        )
        return {
            "keyword": keyword,
            "rising_queries": suggest if not isinstance(suggest, Exception) else [],
            "top_discussions": hn if not isinstance(hn, Exception) else [],
            "encyclopedic_refs": wiki if not isinstance(wiki, Exception) else [],
            "scraped_at": datetime.utcnow().isoformat(),
        }

    async def scrape_social_proof(self, name: str) -> dict:
        """Mentions across reddit + hn — closest free equivalent."""
        reddit, hn = await asyncio.gather(
            sources.reddit_search(name, limit=15),
            sources.hackernews_search(name, hits=15),
            return_exceptions=True,
        )
        return {
            "creator": name,
            "mentions": [
                *({"source": "reddit", "data": r} for r in (reddit if not isinstance(reddit, Exception) else [])),
                *({"source": "hackernews", "data": h} for h in (hn if not isinstance(hn, Exception) else [])),
            ],
            "scraped_at": datetime.utcnow().isoformat(),
        }

    async def scrape_youtube_intelligence(self, channel_url: str) -> dict:
        """YouTube channel pages are JS-heavy → use rendered fetch if possible."""
        result = await self.fetch_url(channel_url, render_if_empty=True)
        return {
            "channel_url": channel_url,
            "content": result.text,
            "title": result.title,
            "success": result.success,
            "source": result.source,
            "scraped_at": datetime.utcnow().isoformat(),
        }

    async def scrape_channel_research(self, channel_url: str) -> dict:
        """Generic channel research — fetch page + extract."""
        result = await self.fetch_url(channel_url)
        return {
            "url": channel_url,
            "scraped_at": datetime.utcnow().isoformat(),
            "content": {"markdown": result.text, "title": result.title},
            "success": result.success,
            "sources_used": [channel_url] if result.success else [],
        }

    async def multi_source_research(self, topic: str, niche: str) -> dict:
        """Aggregate everything we can find about a topic."""
        results = await asyncio.gather(
            self.scrape_trend_aggregator(topic),
            self.scrape_content_ideas(niche),
            self.scrape_audience_discourse(topic),
            sources.reddit_search(topic, limit=15),
            return_exceptions=True,
        )
        flat = []
        for r in results:
            if isinstance(r, Exception):
                continue
            if isinstance(r, list):
                flat.extend(r)
            elif isinstance(r, dict):
                flat.append(r)
        return {
            "topic": topic,
            "niche": niche,
            "sources": flat,
            "scraped_at": datetime.utcnow().isoformat(),
            "success": bool(flat),
        }

    # ------------------------------------------------------------------
    # Internal — Firecrawl ultimate fallback
    # ------------------------------------------------------------------

    async def _firecrawl_fallback(self, url: str, prior: ScrapeResult) -> ScrapeResult:
        """If both HTTP and browser failed AND key is set, try Firecrawl."""
        if not os.getenv("FIRECRAWL_API_KEY"):
            return prior
        try:
            # Lazy import — Firecrawl is optional
            from firecrawl import FirecrawlApp  # type: ignore
            fc = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
            data = await asyncio.to_thread(fc.scrape_url, url)
            text = (data.get("markdown") or data.get("content") or "")[:8000]
            if text:
                return ScrapeResult(
                    url=url, status=200, text=text, title=data.get("metadata", {}).get("title", "")[:500],
                    success=True, source="firecrawl",
                )
        except Exception as e:
            logger.warning(f"Firecrawl fallback also failed for {url}: {e}")
        return prior

    async def _reddit_url(self, url: str) -> list[dict]:
        """Hit a Reddit URL ending in .json directly."""
        from .http_client import get_client
        from .utils import default_headers, rate_limiter
        await rate_limiter.wait(url)
        try:
            client = await get_client()
            resp = await client.get(
                url,
                headers={**default_headers(), "Accept": "application/json"},
            )
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            logger.warning(f"Reddit JSON fetch failed for {url}: {e}")
            return []


# Module-level singleton — what callers import
scraper = SmartScraper()
