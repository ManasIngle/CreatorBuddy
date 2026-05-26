"""
Shared utilities for the local scraper:
  - User-Agent rotation
  - Per-domain polite rate limiting (token bucket)
  - HTML → clean text extraction (selectolax preferred, html.parser fallback)
  - robots.txt checking with cache
"""
from __future__ import annotations

import asyncio
import logging
import random
import re
import time
from collections import defaultdict
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# User-Agent pool — pretend to be popular browsers, rotate per request
# ---------------------------------------------------------------------------

_UA_POOL = [
    # Chrome desktop
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    # Firefox
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.2; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    # Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
]


def random_ua() -> str:
    return random.choice(_UA_POOL)


def default_headers() -> dict:
    """Sensible browser-like default headers."""
    return {
        "User-Agent": random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


# ---------------------------------------------------------------------------
# Per-domain polite rate limiter
# ---------------------------------------------------------------------------

class DomainRateLimiter:
    """
    Async token bucket per domain. Default: 1 request per second per domain.
    Some hosts get tighter limits (Reddit, Wikipedia) by their ToS.
    """

    DEFAULT_DELAY_SECS = 1.0
    PER_DOMAIN_DELAY: dict[str, float] = {
        "reddit.com":     2.0,   # Reddit's API ToS — be polite
        "www.reddit.com": 2.0,
        "old.reddit.com": 2.0,
        "wikipedia.org":  1.5,
        "google.com":     3.0,   # easy to get rate limited / captcha'd
        "news.google.com": 3.0,
        "youtube.com":    2.0,
        "quora.com":      4.0,
    }

    def __init__(self):
        self._last_hit: dict[str, float] = defaultdict(float)
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, url: str) -> None:
        domain = self._domain(url)
        delay = self._delay_for(domain)
        async with self._locks[domain]:
            elapsed = time.monotonic() - self._last_hit[domain]
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)
            self._last_hit[domain] = time.monotonic()

    @staticmethod
    def _domain(url: str) -> str:
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

    def _delay_for(self, domain: str) -> float:
        # Match longest suffix
        for d, delay in self.PER_DOMAIN_DELAY.items():
            if domain == d or domain.endswith("." + d):
                return delay
        return self.DEFAULT_DELAY_SECS


# ---------------------------------------------------------------------------
# HTML → clean text
# ---------------------------------------------------------------------------

# Tags whose content we never want
_DROP_TAGS = {"script", "style", "noscript", "iframe", "head", "meta", "link", "svg", "nav", "footer"}

_WS_RE = re.compile(r"\s+")
_BLANK_LINES_RE = re.compile(r"\n\s*\n+")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def clean_html(html: str, max_chars: int = 8000) -> str:
    """
    Extract clean, readable text from HTML.
    Tries selectolax (fast C parser); falls back to stdlib html.parser.
    """
    if not html:
        return ""
    # Strip comments first — both parsers can choke on weird ones
    html = _COMMENT_RE.sub("", html)

    # Try selectolax (fast)
    try:
        from selectolax.parser import HTMLParser
        tree = HTMLParser(html)
        for tag in _DROP_TAGS:
            for node in tree.css(tag):
                node.decompose()
        text = tree.body.text(separator="\n", strip=True) if tree.body else tree.text(separator="\n", strip=True)
    except Exception:
        text = _stdlib_html_to_text(html)

    # Collapse whitespace
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    text = "\n".join(lines)
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text[:max_chars]


def _stdlib_html_to_text(html: str) -> str:
    """Fallback HTML→text using stdlib html.parser."""
    from html.parser import HTMLParser as StdlibHTMLParser

    class Extractor(StdlibHTMLParser):
        def __init__(self):
            super().__init__()
            self.parts: list[str] = []
            self._skip_depth = 0

        def handle_starttag(self, tag, attrs):
            if tag in _DROP_TAGS:
                self._skip_depth += 1

        def handle_endtag(self, tag):
            if tag in _DROP_TAGS and self._skip_depth > 0:
                self._skip_depth -= 1

        def handle_data(self, data):
            if self._skip_depth == 0:
                t = data.strip()
                if t:
                    self.parts.append(t)

    e = Extractor()
    try:
        e.feed(html)
    except Exception:
        pass
    return "\n".join(e.parts)


# ---------------------------------------------------------------------------
# robots.txt — respectful crawling
# ---------------------------------------------------------------------------

class RobotsCache:
    """
    Caches robots.txt parses for 1 hour per host.
    Returns True if a URL is allowed for our UA.
    """
    _cache: dict[str, tuple[float, RobotFileParser]] = {}
    _TTL = 3600

    @classmethod
    async def allowed(cls, url: str, user_agent: str = "*") -> bool:
        try:
            parsed = urlparse(url)
            host = f"{parsed.scheme}://{parsed.netloc}"
            now = time.time()
            if host in cls._cache:
                ts, rp = cls._cache[host]
                if now - ts < cls._TTL:
                    return rp.can_fetch(user_agent, url)

            robots_url = f"{host}/robots.txt"
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.get(robots_url, headers={"User-Agent": user_agent})
                    rp = RobotFileParser()
                    if resp.status_code == 200:
                        rp.parse(resp.text.splitlines())
                    else:
                        # If no robots.txt, default to allow
                        rp.parse([])
                    cls._cache[host] = (now, rp)
                    return rp.can_fetch(user_agent, url)
            except Exception:
                # Network error — fail open (allow). We'd rather scrape than miss data.
                return True
        except Exception:
            return True


# ---------------------------------------------------------------------------
# Singletons used across the scraper
# ---------------------------------------------------------------------------

rate_limiter = DomainRateLimiter()
