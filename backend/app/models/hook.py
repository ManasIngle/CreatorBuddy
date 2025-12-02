from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Hook(Base):
    __tablename__ = "hooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=True)
    hook_text = Column(Text, nullable=False)
    hook_type = Column(String(100), nullable=False)   # curiosity|shock|story|question|contrarian
    niche = Column(String(255), nullable=True)
    emotional_trigger = Column(String(100), nullable=True)
    predicted_retention_boost = Column(Float, nullable=True) # 0-100 %
    source_video_id = Column(String(20), nullable=True)     # YouTube ID if learned from video
    is_ai_generated = Column(Boolean, default=True)
    performance_score = Column(Float, nullable=True)        # updated if creator uses this
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Debugging representation of the Hook model."""
        return (
            f"<Hook(id={self.id}, hook_type={self.hook_type}, "
            f"hook_text={self.hook_text[:30] if self.hook_text else None}..., "
            f"predicted_retention_boost={self.predicted_retention_boost}%)>"
        )