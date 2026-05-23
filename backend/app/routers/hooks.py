from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.hook import Hook
from app.utils.auth_utils import get_current_user
from app.intelligence.hook_engine import HookEngine
from app.schemas.intelligence import HookGenerateRequest, HookResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
hook_engine = HookEngine()

@router.post("/generate", response_model=List[HookResponse], status_code=201, tags=["hooks"])
def generate_hooks(
    request: HookGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate multiple hook variations for a given topic.
    
    - **channel_id**: UUID of the channel to personalize for
    - **topic**: The video topic
    - **count**: Number of hooks to generate (default 5)
    
    Returns hook variations using different psychological techniques.
    """
    channel = db.query(Channel).filter(
        Channel.id == request.channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Enforce daily/monthly token budget limits
    from app.services.token_budget import TokenBudgetManager
    usage = TokenBudgetManager.get_usage(str(current_user.id), current_user.plan or "free")
    if not usage["can_proceed"]:
        raise HTTPException(
            status_code=403,
            detail="Token budget exceeded for the current billing period. Please upgrade your plan."
        )

    hooks_data = hook_engine.generate_hooks_for_topic(
        topic=request.topic,
        channel=channel,
        count=request.count
    )

    # Save generated hooks to database
    saved_hooks = []
    for hook_data in hooks_data:
        hook = Hook(
            channel_id=channel.id,
            hook_text=hook_data.get("text", ""),
            hook_type=hook_data.get("type", "unknown"),
            niche=channel.niche,
            emotional_trigger=hook_data.get("emotional_trigger"),
            predicted_retention_boost=hook_data.get("predicted_retention_boost"),
            is_ai_generated=True
        )
        db.add(hook)
        saved_hooks.append(hook)

    db.commit()
    for hook in saved_hooks:
        db.refresh(hook)

    logger.info(f"Generated {len(saved_hooks)} hooks for channel {channel.id}")
    return saved_hooks

@router.get("/", response_model=List[HookResponse], tags=["hooks"])
def list_hooks(
    channel_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all hooks, optionally filtered by channel.
    
    - **channel_id**: Optional UUID to filter by channel
    """
    query = db.query(Hook)
    
    if channel_id:
        # Verify channel ownership
        channel = db.query(Channel).filter(
            Channel.id == channel_id,
            Channel.user_id == current_user.id
        ).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        query = query.filter(Hook.channel_id == channel_id)
    
    return query.order_by(Hook.created_at.desc()).limit(100).all()

@router.get("/{hook_id}", response_model=HookResponse, tags=["hooks"])
def get_hook(
    hook_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific hook by ID.
    
    - **hook_id**: UUID of the hook
    """
    hook = db.query(Hook).filter(Hook.id == hook_id).first()
    if not hook:
        raise HTTPException(status_code=404, detail="Hook not found")
    return hook