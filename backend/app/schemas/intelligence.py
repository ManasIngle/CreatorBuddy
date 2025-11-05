from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class CreatorProfileResponse(BaseModel):
    niche: str
    niche_tags: List[str]
    audience_type: str
    personality_summary: str
    speaking_style: str
    storytelling_structure: str
    content_themes: List[str]
    audience_pain_points: List[str]
    creator_strength: str
    growth_opportunity: str

class HookGenerateRequest(BaseModel):
    channel_id: UUID
    topic: str
    count: int = 5

class HookResponse(BaseModel):
    id: UUID
    channel_id: Optional[UUID]
    hook_text: str
    hook_type: str
    niche: Optional[str]
    emotional_trigger: Optional[str]
    predicted_retention_boost: Optional[float]
    source_video_id: Optional[str]
    is_ai_generated: bool
    performance_score: Optional[float]
    created_at: str

    class Config:
        from_attributes = True

class ThumbnailAnalyzeRequest(BaseModel):
    thumbnail_url: str
    video_title: str

class ThumbnailAnalyzeResponse(BaseModel):
    ctr_prediction: float
    emotional_impact: float
    curiosity_intensity: float
    text_clarity: float
    color_contrast: float
    simplicity: float
    alignment_score: float
    primary_emotion: str
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]

class ThumbnailRecommendRequest(BaseModel):
    topic: str
    title: str
    channel_id: str

class ThumbnailRecommendResponse(BaseModel):
    concept: str
    layout: str
    recommended_emotion: str
    color_palette: List[str]
    text_overlay: str
    background_style: str
    psychological_hook: str
    differentiation_from_competitors: str

class TrendResponse(BaseModel):
    id: UUID
    topic: str
    niche: Optional[str]
    velocity_score: float
    saturation_score: float
    opportunity_window: str
    first_detected_at: str
    peak_predicted_at: Optional[str]
    evidence: List[str]
    recommended_action: Optional[str]
    updated_at: str

    class Config:
        from_attributes = True

class AudienceInsightResponse(BaseModel):
    audience_type: str
    audience_pain_points: List[str]
    content_themes: List[str]
    recommended_topics: List[str]