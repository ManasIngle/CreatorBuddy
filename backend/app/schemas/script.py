from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class ScriptCreateRequest(BaseModel):
    topic: str
    channel_id: Optional[UUID] = None
    target_duration_minutes: int = 10
    format_type: str = "educational"  # educational|story|list|review

class ScriptResponse(BaseModel):
    id: UUID
    user_id: UUID
    channel_id: Optional[UUID]
    topic: str
    target_duration_minutes: int
    format_type: str
    tone: str
    title_suggestions: List[str]
    hook: Optional[str]
    full_script: Optional[str]
    cta_text: Optional[str]
    short_form_adaptation: Optional[str]
    thumbnail_concept: Optional[str]
    retention_notes: Optional[str]
    generation_status: str
    created_at: datetime

    class Config:
        from_attributes = True