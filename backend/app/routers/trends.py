from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.channel import Channel
from app.models.trend import Trend
from app.utils.auth_utils import get_current_user
from app.schemas.intelligence import TrendResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[TrendResponse], tags=["trends"])
def list_trends(
    niche: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List trending topics, optionally filtered by niche.
    
    - **niche**: Optional niche filter
    
    Returns trends sorted by velocity score (fastest growing first).
    """
    query = db.query(Trend)
    if niche:
        query = query.filter(Trend.niche.ilike(f"%{niche}%"))
    return query.order_by(Trend.velocity_score.desc()).limit(50).all()

@router.get("/{trend_id}", response_model=TrendResponse, tags=["trends"])
def get_trend(
    trend_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific trend.
    
    - **trend_id**: UUID of the trend
    """
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend