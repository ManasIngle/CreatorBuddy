from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ContentGapResponse(BaseModel):
    id: UUID
    channel_id: UUID
    topic: str
    reason: str
    opportunity_score: float
    competition_level: str
    estimated_search_demand: str
    suggested_angle: Optional[str]
    suggested_title: Optional[str]
    supporting_evidence: List[str]
    trend_direction: str
    source_type: str
    is_acted_on: bool
    created_at: datetime

    class Config:
        from_attributes = True