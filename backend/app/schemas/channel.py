from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class ConnectChannelRequest(BaseModel):
    youtube_channel_id: str  # channel ID (UC...) or handle (@username)

class ChannelResponse(BaseModel):
    id: UUID
    youtube_channel_id: str
    title: str
    description: Optional[str]
    subscriber_count: int
    video_count: int
    view_count: int
    thumbnail_url: Optional[str]
    country: Optional[str]
    niche: Optional[str]
    niche_tags: List[str]
    audience_type: Optional[str]
    personality_summary: Optional[str]
    speaking_style: Optional[str]
    storytelling_structure: Optional[str]
    avg_views: float
    avg_engagement_rate: float
    avg_retention_rate: float
    upload_frequency_days: Optional[float]
    best_upload_day: Optional[str]
    best_upload_hour: Optional[int]
    last_analyzed_at: Optional[datetime]
    analysis_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationMeta(BaseModel):
    """Pagination metadata for list responses."""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool
    next: Optional[str] = None
    prev: Optional[str] = None


class ChannelListResponse(BaseModel):
    """
    Paginated list of channels with metadata.
    
    Includes:
    - items: List of ChannelResponse objects
    - pagination: Pagination metadata
    """
    items: List[ChannelResponse]
    pagination: PaginationMeta