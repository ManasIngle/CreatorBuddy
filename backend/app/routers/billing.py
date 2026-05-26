"""
Billing router — Stripe-ready structure.

Phase 0: stubs that return meaningful errors so the frontend can already
         wire up billing UI flows without breaking.

Phase 2: uncomment Stripe SDK calls, add webhook handler, update User model
         with stripe_customer_id + stripe_subscription_id.

Stripe docs: https://stripe.com/docs/billing/subscriptions/build-subscriptions
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.auth_utils import get_current_user
from app.services.token_budget import TokenBudgetManager
from app.deps import PLAN_LIMITS

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class UsageResponse(BaseModel):
    plan: str
    tokens_used: int
    token_limit: int
    percentage: float
    remaining: int
    status: str   # ok | warning | critical
    can_proceed: bool
    requests_count: int


class CheckoutRequest(BaseModel):
    plan: str                     # starter | pro | agency
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: Optional[str] = None


class PortalResponse(BaseModel):
    portal_url: str


# ---------------------------------------------------------------------------
# Usage endpoint (works today, no Stripe needed)
# ---------------------------------------------------------------------------

@router.get("/usage", response_model=UsageResponse, tags=["billing"])
def get_usage(
    current_user: User = Depends(get_current_user),
):
    """
    Return current token usage for the authenticated user.
    Used by the frontend usage bar in settings and the sidebar.
    """
    plan = current_user.plan or "free"
    usage = TokenBudgetManager.get_usage(str(current_user.id), plan)
    return UsageResponse(**usage)


# ---------------------------------------------------------------------------
# Stripe checkout (stub — Phase 2)
# ---------------------------------------------------------------------------

@router.post("/create-checkout", response_model=CheckoutResponse, tags=["billing"])
def create_checkout_session(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Checkout session for plan upgrade.

    Phase 2 implementation:
        import stripe; stripe.api_key = settings.STRIPE_API_KEY
        session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            mode="subscription",
            line_items=[{"price": STRIPE_PRICE_IDS[req.plan], "quantity": 1}],
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            metadata={"user_id": str(current_user.id), "plan": req.plan},
        )
        return CheckoutResponse(checkout_url=session.url, session_id=session.id)
    """
    if req.plan not in ("starter", "pro", "agency"):
        raise HTTPException(status_code=400, detail="Invalid plan. Choose starter, pro, or agency.")

    # Stub: inform caller that Stripe is not yet wired
    raise HTTPException(
        status_code=503,
        detail={
            "code": "BILLING_NOT_CONFIGURED",
            "message": "Billing is not yet enabled. Contact support to upgrade.",
        },
    )


@router.post("/create-portal", response_model=PortalResponse, tags=["billing"])
def create_billing_portal(
    current_user: User = Depends(get_current_user),
):
    """
    Create a Stripe Customer Portal session for managing subscription.
    Phase 2: uncomment Stripe call below.
    """
    raise HTTPException(
        status_code=503,
        detail={
            "code": "BILLING_NOT_CONFIGURED",
            "message": "Billing portal is not yet enabled.",
        },
    )


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Stripe webhook handler.
    Phase 2 events to handle:
      - checkout.session.completed → update user.plan + store stripe_customer_id
      - customer.subscription.updated → update plan
      - customer.subscription.deleted → downgrade to free

    Verify signature with: stripe.Webhook.construct_event(body, sig, STRIPE_WEBHOOK_SECRET)
    """
    # Phase 2: implement event handling
    return {"received": True}
