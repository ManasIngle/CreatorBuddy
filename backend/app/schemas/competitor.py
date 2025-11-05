from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class CompetitorResponse(BaseModel):
    id: UUID
    channel_id: UUID
    youtube_channel_id: str
    title: str
    subscriber_count: int
    avg_views: float
    avg_engagement_rate: float
    niche_overlap_score: float
    why_they_succeed: Optional[str]
    best_formats: List[str]
    emotional_triggers_used: List[str]
    content_gaps: List[str]
    hook_patterns: List[str]
    upload_frequency_days: Optional[float]
    thumbnail_style: Optional[str]
    last_analyzed_at: Optional[datetime]
    analysis_status: str
    created_at: datetime

    class Config:
        from_attributes = True