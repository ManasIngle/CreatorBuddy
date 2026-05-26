"""
Legacy scraper_service module — now a thin compatibility shim over
app.services.local_scraper.

The real implementation lives in local_scraper/. This module exists only
so existing imports (`from app.services.scraper_service import scraper_service`)
keep working without changes to engines.

For new code, prefer:
    from app.services.local_scraper import scraper
"""
from __future__ import annotations

import logging
import re
from html.parser import HTMLParser

from app.services.local_scraper import scraper as scraper_service  # noqa: F401  (re-export)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Re-export legacy helpers so any code that imported them from this module
# keeps working. Both exist in local_scraper.utils now.
# ---------------------------------------------------------------------------

class HTMLTextExtractor(HTMLParser):
    """Kept for backwards compatibility. Prefer local_scraper.utils.clean_html."""

    def __init__(self):
        super().__init__()
        self.result: list[str] = []
        self.ignore_tags = {"script", "style", "head", "title", "meta", "link", "noscript"}
        self.current_tag: str | None = None

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

    def get_text(self) -> str:
        return "\n".join(self.result)


def clean_html(html_content: str) -> str:
    """Backwards-compat wrapper. Forwards to the new local_scraper implementation."""
    from app.services.local_scraper.utils import clean_html as _new_clean_html
    return _new_clean_html(html_content, max_chars=8000)


# Public name expected by older code
__all__ = ["scraper_service", "HTMLTextExtractor", "clean_html"]
