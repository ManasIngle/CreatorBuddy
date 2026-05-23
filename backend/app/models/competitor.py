from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False, index=True)
    youtube_channel_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    subscriber_count = Column(Integer, default=0)
    avg_views = Column(Float, default=0.0)
    avg_engagement_rate = Column(Float, default=0.0)
    niche_overlap_score = Column(Float, default=0.0)  # 0-1 how similar to creator

    # AI intelligence
    why_they_succeed = Column(Text, nullable=True)
    best_formats = Column(JSON, default=list)           # ["tutorial", "review", "story"]
    emotional_triggers_used = Column(JSON, default=list)
    content_gaps = Column(JSON, default=list)           # topics they are missing
    hook_patterns = Column(JSON, default=list)
    upload_frequency_days = Column(Float, nullable=True)
    thumbnail_style = Column(Text, nullable=True)
    last_analyzed_at = Column(DateTime, nullable=True)
    analysis_status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    channel = relationship("Channel", back_populates="competitors")

    def __repr__(self):
        """Debugging representation of the Competitor model."""
        return (
            f"<Competitor(id={self.id}, youtube_channel_id={self.youtube_channel_id}, "
            f"title={self.title[:30] if self.title else None}..., "
            f"analysis_status={self.analysis_status})>"
        )