"""
Layer 3: Headless browser fallback (Playwright).

Only used when:
  - Page is JS-heavy (SPA, lazy-loaded content)
  - HTTP scrape returned ~empty text
  - Caller explicitly requested rendered

Maintains a single browser context across calls — each call gets a fresh page.
Browser launch is expensive (1-2s); subsequent pages are fast (~200ms).

Optional dependency: pip install playwright && playwright install chromium
The whole module degrades gracefully if Playwright isn't installed.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .http_client import ScrapeResult
from .utils import clean_html, default_headers, rate_limiter

logger = logging.getLogger(__name__)


_browser = None
_context = None
_browser_lock = asyncio.Lock()
_AVAILABLE: Optional[bool] = None  # tri-state: None=untested, True/False=tested


def is_available() -> bool:
    """Cheap check whether Playwright is installed."""
    global _AVAILABLE
    if _AVAILABLE is not None:
        return _AVAILABLE
    try:
        import playwright  # noqa: F401
        _AVAILABLE = True
    except ImportError:
        _AVAILABLE = False
    return _AVAILABLE


async def _ensure_browser():
    """Launch browser + context once. Reused across all rendered fetches."""
    global _browser, _context
    if not is_available():
        return None, None

    async with _browser_lock:
        if _browser is None:
            from playwright.async_api import async_playwright
            playwright = await async_playwright().start()
            _browser = await playwright.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            _context = await _browser.new_context(
                user_agent=default_headers()["User-Agent"],
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                # Block heavy resources to speed up rendering
                java_script_enabled=True,
            )
            # Block images, fonts, media — we want HTML content only
            await _context.route(
                "**/*",
                lambda route: route.abort()
                if route.request.resource_type in ("image", "media", "font")
                else route.continue_(),
            )
            logger.info("Playwright browser launched (headless chromium)")
    return _browser, _context


async def fetch_rendered(
    url: str,
    *,
    wait_for_selector: Optional[str] = None,
    wait_seconds: float = 2.0,
    max_text_chars: int = 8000,
) -> ScrapeResult:
    """
    Fetch a URL via headless browser, returning the rendered HTML's clean text.
    """
    if not is_available():
        return ScrapeResult(
            url=url, status=0, success=False,
            error="playwright not installed", source="playwright",
        )

    await rate_limiter.wait(url)
    browser, context = await _ensure_browser()
    if context is None:
        return ScrapeResult(url=url, status=0, success=False, error="no browser context", source="playwright")

    page = await context.new_page()
    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        if wait_for_selector:
            try:
                await page.wait_for_selector(wait_for_selector, timeout=5000)
            except Exception:
                pass
        else:
            await page.wait_for_timeout(int(wait_seconds * 1000))

        html = await page.content()
        title = await page.title()
        text = clean_html(html, max_chars=max_text_chars)
        status = resp.status if resp else 0

        return ScrapeResult(
            url=url,
            status=status,
            text=text,
            title=title[:500] if title else "",
            success=200 <= status < 300,
            source="playwright",
        )
    except Exception as e:
        logger.warning(f"Playwright fetch failed for {url}: {e}")
        return ScrapeResult(url=url, status=0, success=False, error=str(e), source="playwright")
    finally:
        await page.close()


async def close_browser() -> None:
    global _browser, _context
    try:
        if _context is not None:
            await _context.close()
            _context = None
        if _browser is not None:
            await _browser.close()
            _browser = None
    except Exception as e:
        logger.warning(f"Browser close failed: {e}")
