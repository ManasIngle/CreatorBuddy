from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.utils.auth_utils import get_current_user
from app.intelligence.thumbnail_engine import ThumbnailEngine
from app.schemas.intelligence import (
    ThumbnailAnalyzeRequest, 
    ThumbnailAnalyzeResponse,
    ThumbnailRecommendRequest,
    ThumbnailRecommendResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
thumbnail_engine = ThumbnailEngine()

@router.post("/analyze", response_model=ThumbnailAnalyzeResponse, tags=["thumbnails"])
async def analyze_thumbnail(
    request: ThumbnailAnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a thumbnail image using AI vision.
    
    - **thumbnail_url**: Direct URL to the thumbnail image
    - **video_title**: Title of the video for context
    
    Returns CTR prediction and detailed scoring of thumbnail elements.
    Requires GPT-4o vision which has higher cost.
    """
    try:
        result = thumbnail_engine.analyze_thumbnail(
            thumbnail_url=request.thumbnail_url,
            video_title=request.video_title
        )
        return result
    except Exception as e:
        logger.error(f"Thumbnail analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/recommend", response_model=ThumbnailRecommendResponse, tags=["thumbnails"])
def recommend_thumbnail(
    request: ThumbnailRecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI recommendations for thumbnail design concept.
    
    - **topic**: Video topic
    - **title**: Video title
    - **channel_id**: UUID of the channel for competitor context
    
    Returns design directions including layout, colors, emotion, and text.
    """
    channel = db.query(Channel).filter(
        Channel.id == request.channel_id,
        Channel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # Get competitor thumbnail styles (simplified - would normally fetch from competitors)
    competitor_styles = [
        f"Typical {channel.niche or 'content'} thumbnail style"
    ]

    try:
        result = thumbnail_engine.recommend_thumbnail_concept(
            topic=request.topic,
            title=request.title,
            niche=channel.niche or "general",
            top_competitor_styles=competitor_styles
        )
        return result
    except Exception as e:
        logger.error(f"Thumbnail recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")