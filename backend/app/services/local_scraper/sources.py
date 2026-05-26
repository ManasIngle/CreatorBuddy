"""
Layer 1: Source-specific clients for high-value endpoints.

Each function returns structured data — never raw HTML. Callers pass the
output straight to the LLM, no scraping cleanup needed.

Sources covered:
  - Reddit (JSON endpoints — public, no auth)
  - Wikipedia (REST API)
  - HackerNews (Algolia search API)
  - Google News (RSS feed — no scraping required)
  - YouTube search suggestions (suggest endpoint)
  - StackExchange (Quora alternative for Q&A)
"""
from __future__ import annotations

import logging
from typing import Optional
from urllib.parse import quote_plus
import xml.etree.ElementTree as ET

from .http_client import fetch_url, get_client
from .utils import rate_limiter, default_headers

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reddit — JSON endpoints
# ---------------------------------------------------------------------------

async def reddit_hot(subreddit: str, limit: int = 25) -> list[dict]:
    """
    Top hot posts in a subreddit using the public .json endpoint.
    No auth, ToS-compliant if you respect rate limits (we do).
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    return await _reddit_listing(url)


async def reddit_search(query: str, limit: int = 25, sort: str = "relevance") -> list[dict]:
    """Search across all of Reddit."""
    url = f"https://www.reddit.com/search.json?q={quote_plus(query)}&limit={limit}&sort={sort}"
    return await _reddit_listing(url)


async def reddit_top_questions(subreddit: str, time_range: str = "month", limit: int = 50) -> list[dict]:
    """
    Top question-style posts (titles ending in '?' get filtered & ranked first).
    Useful for audience pain-point detection.
    """
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={time_range}&limit={limit}"
    posts = await _reddit_listing(url)
    questions = [p for p in posts if p.get("title", "").rstrip().endswith("?")]
    return questions or posts


async def _reddit_listing(url: str) -> list[dict]:
    await rate_limiter.wait(url)
    try:
        client = await get_client()
        # Reddit blocks default urllib UA — use ours, plus required Accept
        resp = await client.get(
            url,
            headers={**default_headers(), "Accept": "application/json"},
        )
        if resp.status_code != 200:
            logger.warning(f"Reddit returned {resp.status_code} for {url}")
            return []
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            posts.append({
                "title": d.get("title", ""),
                "selftext": (d.get("selftext", "") or "")[:1000],
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "score": d.get("score", 0),
                "num_comments": d.get("num_comments", 0),
                "subreddit": d.get("subreddit", ""),
                "author": d.get("author", ""),
                "created_utc": d.get("created_utc", 0),
                "is_self": d.get("is_self", False),
            })
        return posts
    except Exception as e:
        logger.error(f"Reddit fetch failed for {url}: {e}")
        return []


# ---------------------------------------------------------------------------
# Wikipedia — REST API
# ---------------------------------------------------------------------------

async def wikipedia_summary(topic: str) -> Optional[dict]:
    """Get the page summary for a topic."""
    title = quote_plus(topic.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return None
        d = resp.json()
        return {
            "title": d.get("title", ""),
            "extract": d.get("extract", ""),
            "url": d.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "thumbnail": d.get("thumbnail", {}).get("source"),
        }
    except Exception as e:
        logger.error(f"Wikipedia fetch failed for {topic}: {e}")
        return None


async def wikipedia_search(query: str, limit: int = 10) -> list[dict]:
    """Search Wikipedia for related pages."""
    url = (
        "https://en.wikipedia.org/w/api.php?"
        f"action=query&list=search&format=json&srlimit={limit}&srsearch={quote_plus(query)}"
    )
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [
            {
                "title": r.get("title", ""),
                "snippet": _strip_html_tags(r.get("snippet", "")),
                "url": f"https://en.wikipedia.org/?curid={r.get('pageid')}",
            }
            for r in data.get("query", {}).get("search", [])
        ]
    except Exception as e:
        logger.error(f"Wikipedia search failed for {query}: {e}")
        return []


# ---------------------------------------------------------------------------
# HackerNews — Algolia search API
# ---------------------------------------------------------------------------

async def hackernews_search(query: str, hits: int = 30, sort: str = "by_popularity") -> list[dict]:
    """
    Search HackerNews using Algolia's free public API.
    sort: "by_popularity" (top stories) or "by_date" (newest).
    """
    endpoint = "search" if sort == "by_popularity" else "search_by_date"
    url = f"https://hn.algolia.com/api/v1/{endpoint}?query={quote_plus(query)}&hitsPerPage={hits}&tags=story"
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [
            {
                "title": h.get("title", ""),
                "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                "points": h.get("points", 0),
                "num_comments": h.get("num_comments", 0),
                "author": h.get("author", ""),
                "created_at": h.get("created_at", ""),
            }
            for h in data.get("hits", [])
        ]
    except Exception as e:
        logger.error(f"HN search failed for {query}: {e}")
        return []


# ---------------------------------------------------------------------------
# Google News — RSS (no scraping required)
# ---------------------------------------------------------------------------

async def google_news(query: str, limit: int = 25) -> list[dict]:
    """
    Google News RSS feed. Public, no API key needed.
    Returns recent articles for a query.
    """
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return []
        return _parse_rss(resp.text, limit=limit)
    except Exception as e:
        logger.error(f"Google News failed for {query}: {e}")
        return []


def _parse_rss(xml_text: str, limit: int = 25) -> list[dict]:
    """Lightweight RSS 2.0 parser using stdlib ElementTree."""
    try:
        root = ET.fromstring(xml_text)
        items = []
        for item in root.findall(".//item")[:limit]:
            items.append({
                "title": (item.findtext("title") or "").strip(),
                "url": (item.findtext("link") or "").strip(),
                "published": (item.findtext("pubDate") or "").strip(),
                "description": _strip_html_tags(item.findtext("description") or "")[:500],
                "source": (item.findtext("{http://www.google.com/}source") or "").strip(),
            })
        return items
    except ET.ParseError as e:
        logger.warning(f"RSS parse failed: {e}")
        return []


# ---------------------------------------------------------------------------
# YouTube search suggestions (no API key, free)
# ---------------------------------------------------------------------------

async def youtube_suggest(query: str) -> list[str]:
    """
    YouTube search suggestion API. Free, no key, semi-official.
    Used to find rising-search keywords for trend detection.
    """
    url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={quote_plus(query)}"
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return []
        # Response is JSONP-ish: window.google.ac.h([…])
        text = resp.text.strip()
        # Strip JSONP wrapper if present
        if text.startswith("window.google.ac"):
            text = text[text.index("(") + 1 : text.rindex(")")]
        import json
        data = json.loads(text)
        # data[1] is the list of [suggestion, _, …] tuples
        suggestions = []
        for row in data[1] if len(data) > 1 else []:
            if isinstance(row, list) and row:
                suggestions.append(row[0])
            elif isinstance(row, str):
                suggestions.append(row)
        return suggestions[:20]
    except Exception as e:
        logger.error(f"YouTube suggest failed for {query}: {e}")
        return []


# ---------------------------------------------------------------------------
# StackExchange — Q&A platform (Quora alternative we can actually use)
# ---------------------------------------------------------------------------

async def stackexchange_search(query: str, site: str = "stackoverflow", limit: int = 25) -> list[dict]:
    """
    StackExchange search API. Free with quota, no auth required for basic use.
    site: stackoverflow | superuser | webmasters | etc.
    """
    url = (
        f"https://api.stackexchange.com/2.3/search/advanced?"
        f"site={site}&q={quote_plus(query)}&order=desc&sort=votes&pagesize={limit}"
    )
    try:
        await rate_limiter.wait(url)
        client = await get_client()
        # StackExchange responses are gzipped — httpx handles that automatically
        resp = await client.get(url, headers=default_headers())
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [
            {
                "title": q.get("title", ""),
                "url": q.get("link", ""),
                "score": q.get("score", 0),
                "answer_count": q.get("answer_count", 0),
                "view_count": q.get("view_count", 0),
                "tags": q.get("tags", []),
                "is_answered": q.get("is_answered", False),
            }
            for q in data.get("items", [])
        ]
    except Exception as e:
        logger.error(f"StackExchange search failed for {query}: {e}")
        return []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_html_tags(s: str) -> str:
    """Quick HTML tag strip — safe enough for one-line snippets."""
    import re
    return re.sub(r"<[^>]+>", "", s).strip()
