"""
Local scraping subsystem.

Replaces Firecrawl as the primary scraping backend with a layered strategy:

  Layer 1: Source-specific clients (Reddit JSON, Wikipedia REST, HN Algolia,
           Google News RSS, YouTube suggestions). Free, structured, fast.
  Layer 2: Generic HTTP scraping (httpx + selectolax, UA rotation, polite
           rate limits, robots.txt respect).
  Layer 3: Headless browser (Playwright) — only for JS-rendered pages.
  Layer 4: Firecrawl — ultimate fallback if configured.

Public API:
    from app.services.local_scraper import scraper

    # Source-specific, structured
    posts = await scraper.reddit_hot("youtube_growth", limit=25)
    qa    = await scraper.search_quora_like("how to grow on youtube")
    news  = await scraper.google_news("ai video editing")

    # Generic
    page = await scraper.fetch_url("https://example.com/blog/post")

    # Smart router — picks the right strategy by URL
    page = await scraper.smart_fetch("https://www.reddit.com/r/youtube/...")
"""

from .router import scraper

__all__ = ["scraper"]
