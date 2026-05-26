from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.content_gap import ContentGap
from app.utils.auth_utils import get_current_user
from app.intelligence.gap_detector import GapDetector
from app.schemas.content_gap import ContentGapResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
detector = GapDetector()

@router.post("/{channel_id}/detect", tags=["gaps"])
def detect_content_gaps(
    channel_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger content gap detection for a channel. Runs in background.
    
    - **channel_id**: UUID of the channel to analyze
    
    Detection identifies topics your audience wants that competitors aren't covering.
    Takes approximately 30-60 seconds to complete.
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    user_id_str = str(current_user.id)

    def run_detection():
        from app.database import SessionLocal
        from app.intelligence.gap_detector import GapDetector
        from app.models.content_gap import ContentGap
        
        db = SessionLocal()
        try:
            # Re-fetch channel in this session
            from app.models.channel import Channel
            channel = db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                return
            
            detector = GapDetector()
            gaps = detector.detect_gaps(channel, db, user_id=user_id_str)
            
            for gap_data in gaps:
                gap = ContentGap(
                    channel_id=channel_id,
                    topic=gap_data.get("topic", ""),
                    reason=gap_data.get("reason", ""),
                    opportunity_score=gap_data.get("opportunity_score", 5.0),
                    competition_level=gap_data.get("competition_level", "medium"),
                    suggested_angle=gap_data.get("suggested_angle"),
                    suggested_title=gap_data.get("suggested_title"),
                    trend_direction=gap_data.get("trend_direction", "stable"),
                    source_type=gap_data.get("source_type", "competitor_gap")
                )
                db.add(gap)
            db.commit()
            logger.info(f"Gap detection complete for channel {channel_id}")
        except Exception as e:
            logger.error(f"Gap detection failed for {channel_id}: {e}")
        finally:
            db.close()

    background_tasks.add_task(run_detection)
    return {"message": "Gap detection queued"}

@router.get("/{channel_id}", response_model=List[ContentGapResponse], tags=["gaps"])
def list_gaps(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all content gaps for a channel, sorted by opportunity score.
    
    - **channel_id**: UUID of the channel
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db.query(ContentGap).filter(
        ContentGap.channel_id == channel_id
    ).order_by(ContentGap.opportunity_score.desc()).all()

@router.post("/{channel_id}/gaps/{gap_id}/acted-on", tags=["gaps"])
def mark_gap_acted_on(
    channel_id: str,
    gap_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a content gap as acted on (video created).
    
    - **channel_id**: UUID of the channel
    - **gap_id**: UUID of the gap to mark
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    gap = db.query(ContentGap).filter(
        ContentGap.id == gap_id,
        ContentGap.channel_id == channel_id
    ).first()
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")

    gap.is_acted_on = True
    db.commit()
    return {"message": "Gap marked as acted on"}