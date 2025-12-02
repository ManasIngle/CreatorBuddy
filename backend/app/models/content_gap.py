from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class ContentGap(Base):
    __tablename__ = "content_gaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False)
    topic = Column(String(500), nullable=False)
    reason = Column(Text, nullable=False)               # Why this gap exists
    opportunity_score = Column(Float, default=0.0)     # 0-10 how valuable
    competition_level = Column(String(20), default="medium") # low|medium|high
    estimated_search_demand = Column(String(20), default="medium")
    suggested_angle = Column(Text, nullable=True)       # How creator should approach it
    suggested_title = Column(String(500), nullable=True)
    supporting_evidence = Column(JSON, default=list)   # ["Competitor X has no video on Y"]
    trend_direction = Column(String(20), default="stable") # rising|stable|declining
    source_type = Column(String(50), default="competitor_gap") # competitor_gap|search|comment|trend
    is_acted_on = Column(Boolean, default=False)       # has creator made a video on this?
    created_at = Column(DateTime, default=datetime.utcnow)

    channel = relationship("Channel", back_populates="content_gaps")

    def __repr__(self):
        """Debugging representation of the ContentGap model."""
        return (
            f"<ContentGap(id={self.id}, topic={self.topic[:30] if self.topic else None}..., "
            f"opportunity_score={self.opportunity_score}, is_acted_on={self.is_acted_on})>"
        )