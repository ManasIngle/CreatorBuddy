from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.database import Base

class Channel(Base):
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    youtube_channel_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    thumbnail_url = Column(Text, nullable=True)
    country = Column(String(10), nullable=True)
    niche = Column(String(255), nullable=True)           # AI-detected niche
    niche_tags = Column(JSON, default=list)              # ["tech", "programming", "tutorials"]
    audience_type = Column(String(255), nullable=True)  # AI-detected audience persona
    personality_summary = Column(Text, nullable=True)   # AI-generated creator persona
    speaking_style = Column(Text, nullable=True)        # AI-detected speaking style
    storytelling_structure = Column(Text, nullable=True)
    avg_views = Column(Float, default=0.0)
    avg_engagement_rate = Column(Float, default=0.0)
    avg_retention_rate = Column(Float, default=0.0)
    upload_frequency_days = Column(Float, nullable=True) # avg days between uploads
    best_upload_day = Column(String(20), nullable=True)
    best_upload_hour = Column(Integer, nullable=True)
    last_analyzed_at = Column(DateTime, nullable=True)
    analysis_status = Column(String(50), default="pending") # pending|running|done|failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # pgvector embedding of channel's content style
    content_embedding = Column(Vector(1536), nullable=True)

    user = relationship("User", back_populates="channels")
    videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="channel", cascade="all, delete-orphan")
    content_gaps = relationship("ContentGap", back_populates="channel", cascade="all, delete-orphan")

    def __repr__(self):
        """Debugging representation of the Channel model."""
        return (
            f"<Channel(id={self.id}, youtube_channel_id={self.youtube_channel_id}, "
            f"title={self.title[:30] if self.title else None}..., "
            f"analysis_status={self.analysis_status})>"
        )