"""
Email service — transactional emails for CreatorIQ.

Phase 2: wire up Resend (https://resend.com) or AWS SES.
Current state: structured stubs that log instead of sending so the rest
of the codebase can import and call these without breaking.

Usage:
    from app.services.email_service import send_welcome_email
    await send_welcome_email(user.email, user.full_name or "Creator")
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Detect whether a real provider is configured
_RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
_FROM_ADDRESS: str = os.getenv("EMAIL_FROM", "noreply@creatoriq.io")
_PROVIDER: str = "resend" if _RESEND_API_KEY else "log"


# ---------------------------------------------------------------------------
# Internal dispatcher
# ---------------------------------------------------------------------------

async def _send(to: str, subject: str, html: str, text: str) -> bool:
    """
    Send an email via the configured provider.
    Returns True on success, False on failure (never raises).
    """
    if _PROVIDER == "resend":
        try:
            import resend
            resend.api_key = _RESEND_API_KEY
            resend.Emails.send({
                "from": _FROM_ADDRESS,
                "to": to,
                "subject": subject,
                "html": html,
                "text": text,
            })
            logger.info(f"Email sent via Resend: {subject!r} → {to}")
            return True
        except Exception as e:
            logger.error(f"Resend email failed: {e}")
            return False
    else:
        # Development fallback — just log
        logger.info(
            f"[EMAIL LOG] To={to!r} Subject={subject!r}\n"
            f"--- text ---\n{text[:300]}"
        )
        return True


# ---------------------------------------------------------------------------
# Public email functions
# ---------------------------------------------------------------------------

async def send_welcome_email(to: str, name: str) -> bool:
    subject = "Welcome to CreatorIQ 🎬"
    text = (
        f"Hey {name},\n\n"
        "You're in. Here's how to get the most out of CreatorIQ in your first 10 minutes:\n\n"
        "1. Connect your YouTube channel (takes 30 seconds)\n"
        "2. Add 2-3 competitors to build your analysis baseline\n"
        "3. Run gap detection to find your next video topic\n"
        "4. Generate a full script — ready to film\n\n"
        "Any questions? Reply to this email.\n\n"
        "— The CreatorIQ team"
    )
    html = text.replace("\n", "<br>")
    return await _send(to, subject, html, text)


async def send_analysis_complete_email(to: str, name: str, channel_title: str) -> bool:
    subject = f"Your analysis is ready — {channel_title}"
    text = (
        f"Hey {name},\n\n"
        f"We've finished analyzing \"{channel_title}\".\n\n"
        "Your creator profile, competitor gaps, and content opportunities are ready. "
        "Log in to see your results.\n\n"
        "https://creatoriq.io/dashboard\n\n"
        "— CreatorIQ"
    )
    html = text.replace("\n", "<br>")
    return await _send(to, subject, html, text)


async def send_script_ready_email(to: str, name: str, topic: str) -> bool:
    subject = f"Your script is ready: {topic[:60]}"
    text = (
        f"Hey {name},\n\n"
        f"Your script for \"{topic}\" is done and waiting for you.\n\n"
        "https://creatoriq.io/scripts\n\n"
        "— CreatorIQ"
    )
    html = text.replace("\n", "<br>")
    return await _send(to, subject, html, text)


async def send_plan_limit_warning_email(
    to: str, name: str, plan: str, resource: str, pct_used: float
) -> bool:
    subject = f"You've used {pct_used:.0f}% of your {plan.capitalize()} plan"
    text = (
        f"Hey {name},\n\n"
        f"You've used {pct_used:.0f}% of your {resource} allowance on the {plan.capitalize()} plan.\n\n"
        "Upgrade to keep creating without interruption:\n"
        "https://creatoriq.io/settings\n\n"
        "— CreatorIQ"
    )
    html = text.replace("\n", "<br>")
    return await _send(to, subject, html, text)
