from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.competitor import Competitor
from app.utils.auth_utils import get_current_user
from app.intelligence.competitor_engine import CompetitorEngine
from app.schemas.competitor import CompetitorResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
competitor_engine = CompetitorEngine()

def run_competitor_analysis(competitor_id: str, youtube_channel_id: str, niche: str, channel_id: str):
    """
    Background task for competitor analysis.
    """
    from app.database import SessionLocal
    from app.models.competitor import Competitor
    from app.models.channel import Channel
    from app.intelligence.competitor_engine import CompetitorEngine
    from datetime import datetime

    db = SessionLocal()
    try:
        comp = db.query(Competitor).filter(Competitor.id == competitor_id).first()
        if not comp:
            return

        comp.analysis_status = "running"
        db.commit()

        analyzer = CompetitorEngine()
        result = analyzer.analyze_competitor(
            competitor_youtube_id=youtube_channel_id,
            creator_niche=niche,
            db=db
        )

        comp.title = result.get("title", comp.title)
        comp.subscriber_count = result.get("subscriber_count", 0)
        comp.avg_views = result.get("avg_views", 0)
        comp.why_they_succeed = result.get("why_they_succeed", "")
        comp.best_formats = result.get("best_formats", [])
        comp.emotional_triggers_used = result.get("emotional_triggers_used", [])
        comp.content_gaps = result.get("content_gaps", [])
        comp.hook_patterns = result.get("hook_patterns", [])
        comp.thumbnail_style = result.get("thumbnail_style", "")
        comp.last_analyzed_at = datetime.utcnow()
        comp.analysis_status = "done"
        db.commit()

        logger.info(f"Competitor analysis complete for {competitor_id}")

    except Exception as e:
        logger.error(f"Competitor analysis failed for {competitor_id}: {e}")
        if comp:
            comp.analysis_status = "failed"
            db.commit()
    finally:
        db.close()

@router.post("/{channel_id}/add", response_model=CompetitorResponse, status_code=201, tags=["competitors"])
def add_competitor(
    channel_id: str,
    youtube_channel_id: str = Query(..., description="YouTube channel ID to add as competitor"),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a competitor channel and queue analysis.
    
    - **channel_id**: UUID of the user's channel
    - **youtube_channel_id**: YouTube channel ID (UC...) to add as competitor
    
    Analysis runs in background and typically takes 1-2 minutes.
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Check if already added
    existing = db.query(Competitor).filter(
        Competitor.channel_id == channel_id,
        Competitor.youtube_channel_id == youtube_channel_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Competitor already added")

    # Enforce plan limits for competitor tracking count
    comp_count = db.query(Competitor).filter(Competitor.channel_id == channel_id).count()
    plan_comp_limits = {
        "free": 3,
        "starter": 5,
        "pro": 10,
        "agency": 25
    }
    user_plan = current_user.plan or "free"
    limit = plan_comp_limits.get(user_plan, 3)
    if comp_count >= limit:
        raise HTTPException(
            status_code=403,
            detail=f"Competitor limit reached for {user_plan.capitalize()} plan ({limit} competitor{'s' if limit > 1 else ''}). Please upgrade to add more."
        )

    comp = Competitor(
        channel_id=channel_id,
        youtube_channel_id=youtube_channel_id,
        title="Fetching...",
        analysis_status="pending"
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)

    background_tasks.add_task(
        run_competitor_analysis,
        str(comp.id),
        youtube_channel_id,
        channel.niche or "",
        channel_id
    )
    logger.info(f"Competitor analysis queued: {comp.id}")

    return comp

@router.get("/{channel_id}", response_model=List[CompetitorResponse], tags=["competitors"])
def list_competitors(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all competitors for a channel.
    
    - **channel_id**: UUID of the user's channel
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db.query(Competitor).filter(Competitor.channel_id == channel_id).all()

@router.get("/{channel_id}/{competitor_id}", response_model=CompetitorResponse, tags=["competitors"])
def get_competitor_detail(
    channel_id: str,
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed analysis of a specific competitor.
    
    - **channel_id**: UUID of the user's channel
    - **competitor_id**: UUID of the competitor
    """
    # Verify channel ownership
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    comp = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.channel_id == channel_id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return comp

@router.delete("/{channel_id}/{competitor_id}", status_code=204, tags=["competitors"])
def delete_competitor(
    channel_id: str,
    competitor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a competitor from tracking.
    
    - **channel_id**: UUID of the user's channel
    - **competitor_id**: UUID of the competitor to remove
    """
    # Verify channel ownership
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    comp = db.query(Competitor).filter(
        Competitor.id == competitor_id,
        Competitor.channel_id == channel_id
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    db.delete(comp)
    db.commit()
    logger.info(f"Competitor deleted: {competitor_id}")