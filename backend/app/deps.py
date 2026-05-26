"""
Shared FastAPI dependencies.

These are the building blocks for every route that needs:
  - Ownership checks (prevents IDOR — user A can't read user B's data)
  - Plan gating (enforces subscription limits at the API layer)
  - Rate limiting (per-user, per-operation)

Usage pattern in routes:
    @router.post("/generate")
    def generate(
        channel: Channel = Depends(get_owned_channel_by_param("channel_id")),
        _: None = Depends(plan_gate("scripts_per_month")),
        user: User = Depends(get_current_user),
    ):
        ...
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.channel import Channel
from app.models.competitor import Competitor
from app.models.script import Script
from app.models.user import User
from app.utils.auth_utils import get_current_user

# ---------------------------------------------------------------------------
# Plan limits — single source of truth.
# -1 means unlimited.
# ---------------------------------------------------------------------------
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {
        "channels": 1,
        "competitors": 3,
        "scripts_per_month": 3,
        "tokens_per_month": 100_000,
    },
    "starter": {
        "channels": 1,
        "competitors": 5,
        "scripts_per_month": 15,
        "tokens_per_month": 500_000,
    },
    "pro": {
        "channels": 5,
        "competitors": 10,
        "scripts_per_month": -1,
        "tokens_per_month": 2_000_000,
    },
    "agency": {
        "channels": 25,
        "competitors": 25,
        "scripts_per_month": -1,
        "tokens_per_month": 10_000_000,
    },
}


def get_plan_limit(plan: str, key: str) -> int:
    """Return the limit for a given plan and resource key. -1 = unlimited."""
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"]).get(key, 0)


# ---------------------------------------------------------------------------
# Ownership helpers
# ---------------------------------------------------------------------------

def get_owned_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Channel:
    """
    Fetch a channel that belongs to the current user.
    Raises 404 for both "not found" and "belongs to another user" — never
    leak whether a resource exists for a different user.
    """
    try:
        uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid channel_id format")

    channel = (
        db.query(Channel)
        .filter(Channel.id == uid, Channel.user_id == current_user.id)
        .first()
    )
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return channel


def get_owned_script(
    script_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Script:
    """Fetch a script that belongs to the current user."""
    try:
        uid = UUID(script_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid script_id format")

    script = (
        db.query(Script)
        .filter(Script.id == uid, Script.user_id == current_user.id)
        .first()
    )
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


def get_owned_competitor(
    channel_id: str,
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Competitor:
    """Fetch a competitor that belongs to one of the current user's channels."""
    try:
        ch_uid = UUID(channel_id)
        co_uid = UUID(competitor_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verify channel ownership first
    channel = (
        db.query(Channel)
        .filter(Channel.id == ch_uid, Channel.user_id == current_user.id)
        .first()
    )
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    competitor = (
        db.query(Competitor)
        .filter(Competitor.id == co_uid, Competitor.channel_id == ch_uid)
        .first()
    )
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return competitor


# ---------------------------------------------------------------------------
# Plan-gating dependencies
# ---------------------------------------------------------------------------

def check_channel_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Raise 403 if user has reached their plan's channel limit."""
    plan = current_user.plan or "free"
    limit = get_plan_limit(plan, "channels")
    if limit == -1:
        return
    count = db.query(Channel).filter(Channel.user_id == current_user.id).count()
    if count >= limit:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLAN_LIMIT_EXCEEDED",
                "message": f"Channel limit ({limit}) reached on {plan.capitalize()} plan.",
                "limit": limit,
                "current": count,
                "upgrade_to": _next_plan(plan),
            },
        )


def check_competitor_limit(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Raise 403 if channel has reached its plan's competitor limit."""
    plan = current_user.plan or "free"
    limit = get_plan_limit(plan, "competitors")
    if limit == -1:
        return
    try:
        ch_uid = UUID(channel_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid channel_id")

    count = (
        db.query(Competitor)
        .filter(Competitor.channel_id == ch_uid)
        .count()
    )
    if count >= limit:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLAN_LIMIT_EXCEEDED",
                "message": f"Competitor limit ({limit}) reached on {plan.capitalize()} plan.",
                "limit": limit,
                "current": count,
                "upgrade_to": _next_plan(plan),
            },
        )


def check_script_monthly_limit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Raise 403 if user has reached their monthly script generation limit."""
    from datetime import datetime

    plan = current_user.plan or "free"
    limit = get_plan_limit(plan, "scripts_per_month")
    if limit == -1:
        return

    month_start = datetime.utcnow().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    count = (
        db.query(Script)
        .filter(
            Script.user_id == current_user.id,
            Script.created_at >= month_start,
        )
        .count()
    )
    if count >= limit:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "PLAN_LIMIT_EXCEEDED",
                "message": f"Monthly script limit ({limit}) reached on {plan.capitalize()} plan.",
                "limit": limit,
                "current": count,
                "upgrade_to": _next_plan(plan),
            },
        )


def check_token_budget(
    current_user: User = Depends(get_current_user),
) -> None:
    """Raise 429 if user's monthly token budget is exhausted."""
    from app.services.token_budget import TokenBudgetManager

    plan = current_user.plan or "free"
    usage = TokenBudgetManager.get_usage(str(current_user.id), plan)
    if not usage["can_proceed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "BUDGET_EXCEEDED",
                "message": "Monthly token budget exhausted. Upgrade your plan or wait for the next reset.",
                "used": usage["tokens_used"],
                "limit": usage["token_limit"],
                "upgrade_to": _next_plan(plan),
            },
        )


# ---------------------------------------------------------------------------
# Rate limiting dependency
# ---------------------------------------------------------------------------

def rate_limit(operation: str):
    """
    Dependency factory for per-user rate limiting.
    Usage: Depends(rate_limit("script_generate"))
    """
    # Limits per minute per user
    RATE_LIMITS: dict[str, int] = {
        "auth": 20,
        "script_generate": 10,
        "hook_generate": 20,
        "research": 5,
        "analysis": 5,
        "default": 100,
    }

    def _check(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> None:
        from app.utils.rate_limiter import check_rate_limit

        limit = RATE_LIMITS.get(operation, RATE_LIMITS["default"])
        key = f"rl:{operation}:{current_user.id}"
        allowed = check_rate_limit(key, limit, window_seconds=60)
        if not allowed:
            raise HTTPException(
                status_code=429,
                headers={"Retry-After": "60"},
                detail={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Too many requests for '{operation}'. Retry after 60 seconds.",
                    "limit": limit,
                    "window": "60s",
                },
            )

    return _check


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _next_plan(current: str) -> Optional[str]:
    order = ["free", "starter", "pro", "agency"]
    try:
        idx = order.index(current)
        return order[idx + 1] if idx < len(order) - 1 else None
    except ValueError:
        return "starter"
