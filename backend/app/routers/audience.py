from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.utils.auth_utils import get_current_user
from app.intelligence.audience_engine import AudienceEngine
from app.schemas.intelligence import AudienceInsightResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
audience_engine = AudienceEngine()

@router.get("/{channel_id}", response_model=AudienceInsightResponse, tags=["audience"])
def get_audience_insights(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated audience insights for a channel.
    
    - **channel_id**: UUID of the channel
    
    Returns audience type, pain points, content themes, and recommendations.
    """
    channel = db.query(Channel).filter(
        Channel.id == channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    try:
        insights = audience_engine.get_audience_insights(channel)
        return {
            "audience_type": insights.get("audience_type", channel.audience_type or "general audience"),
            "audience_pain_points": insights.get("audience_pain_points", []),
            "content_themes": insights.get("content_themes", channel.niche_tags or []),
            "recommended_topics": insights.get("recommended_topics", [])
        }
    except Exception as e:
        logger.error(f"Audience insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")