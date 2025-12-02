from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Script(Base):
    __tablename__ = "scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=True)

    # Input context
    topic = Column(String(500), nullable=False)
    target_duration_minutes = Column(Integer, default=10)
    format_type = Column(String(100), default="educational") # educational|story|list|review
    tone = Column(String(100), default="conversational")

    # Generated output
    title_suggestions = Column(JSON, default=list)      # 3 title options
    hook = Column(Text, nullable=True)                  # opening 30-sec hook
    full_script = Column(Text, nullable=True)
    cta_text = Column(Text, nullable=True)
    short_form_adaptation = Column(Text, nullable=True) # 60s version
    thumbnail_concept = Column(Text, nullable=True)
    retention_notes = Column(Text, nullable=True)       # what to watch for during editing

    generation_status = Column(String(50), default="pending") # pending|generating|done|failed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scripts")

    def __repr__(self):
        """Debugging representation of the Script model."""
        return (
            f"<Script(id={self.id}, topic={self.topic[:30] if self.topic else None}..., "
            f"generation_status={self.generation_status}, format_type={self.format_type})>"
        )