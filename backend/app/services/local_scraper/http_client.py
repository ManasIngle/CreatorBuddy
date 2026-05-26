"""
Layer 2: Generic async HTTP scraper.

Uses a single httpx AsyncClient with HTTP/2, connection pooling,
random User-Agent, and the shared per-domain rate limiter.

Returns ScrapeResult — a simple dict-like structure with text, html, status, url.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .utils import default_headers, rate_limiter, clean_html, RobotsCache

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    url: str
    status: int
    html: str = ""
    text: str = ""
    title: str = ""
    success: bool = False
    source: str = "http"      # http | reddit | wikipedia | hn | youtube | rss | playwright | firecrawl
    error: Optional[str] = None
    extras: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Shared httpx client (pooled, HTTP/2, lazy-init)
# ---------------------------------------------------------------------------

_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock()


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        async with _client_lock:
            if _client is None:
                _client = httpx.AsyncClient(
                    timeout=httpx.Timeout(20.0, connect=10.0),
                    follow_redirects=True,
                    http2=True,
                    limits=httpx.Limits(
                        max_connections=50,
                        max_keepalive_connections=20,
                        keepalive_expiry=30.0,
                    ),
                )
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# ---------------------------------------------------------------------------
# Core fetch
# ---------------------------------------------------------------------------

class TransientHTTPError(Exception):
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(TransientHTTPError),
    reraise=True,
)
async def _do_fetch(url: str, headers: Optional[dict] = None) -> httpx.Response:
    client = await get_client()
    h = headers or default_headers()
    resp = await client.get(url, headers=h)
    # 429/503 → retry with backoff
    if resp.status_code in (429, 502, 503, 504):
        raise TransientHTTPError(f"{resp.status_code} on {url}")
    return resp


async def fetch_url(
    url: str,
    *,
    extract_text: bool = True,
    respect_robots: bool = True,
    headers: Optional[dict] = None,
    max_text_chars: int = 8000,
) -> ScrapeResult:
    """
    Fetch a single URL with rate limiting, retry, and clean text extraction.

    Set respect_robots=False only if you've verified the source allows it
    (Reddit JSON, Wikipedia API etc. are explicitly designed to be hit).
    """
    if respect_robots:
        ok = await RobotsCache.allowed(url, user_agent="CreatorIQBot")
        if not ok:
            return ScrapeResult(url=url, status=0, success=False, error="blocked by robots.txt")

    await rate_limiter.wait(url)

    try:
        resp = await _do_fetch(url, headers=headers)
        html = resp.text
        title = ""
        text = ""
        if extract_text:
            text = clean_html(html, max_chars=max_text_chars)
            # Pull <title> cheaply
            try:
                from selectolax.parser import HTMLParser
                tree = HTMLParser(html)
                if tree.tags("title"):
                    title = tree.tags("title")[0].text(strip=True)[:500]
            except Exception:
                pass

        return ScrapeResult(
            url=url,
            status=resp.status_code,
            html=html if not extract_text else "",   # don't keep both — saves memory
            text=text,
            title=title,
            success=200 <= resp.status_code < 300,
            source="http",
        )
    except TransientHTTPError as e:
        logger.warning(f"Transient HTTP error after retries: {e}")
        return ScrapeResult(url=url, status=0, success=False, error=str(e), source="http")
    except httpx.HTTPError as e:
        logger.warning(f"HTTP error fetching {url}: {e}")
        return ScrapeResult(url=url, status=0, success=False, error=str(e), source="http")
    except Exception as e:
        logger.error(f"Unexpected fetch error for {url}: {e}")
        return ScrapeResult(url=url, status=0, success=False, error=str(e), source="http")


async def batch_fetch(urls: list[str], concurrency: int = 5) -> list[ScrapeResult]:
    """
    Fetch many URLs concurrently with a hard concurrency limit.
    Per-domain rate limiting still enforced inside fetch_url.
    """
    sem = asyncio.Semaphore(concurrency)

    async def _one(u: str) -> ScrapeResult:
        async with sem:
            return await fetch_url(u)

    return await asyncio.gather(*[_one(u) for u in urls])
