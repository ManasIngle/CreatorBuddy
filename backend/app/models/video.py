from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.database import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("channels.id"), nullable=False)
    youtube_video_id = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)              # full transcript text
    hook_text = Column(Text, nullable=True)               # first 30 seconds transcript
    thumbnail_url = Column(Text, nullable=True)
    duration_seconds = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)          # (likes+comments)/views
    estimated_retention_rate = Column(Float, nullable=True)
    tags = Column(JSON, default=list)
    category_id = Column(String(10), nullable=True)
    published_at = Column(DateTime, nullable=False)

    # AI-extracted intelligence
    hook_quality_score = Column(Float, nullable=True)     # 0-10
    emotional_triggers = Column(JSON, default=list)       # ["curiosity", "fear", "excitement"]
    storytelling_type = Column(String(100), nullable=True)# "problem-solution", "listicle", etc
    pacing_score = Column(Float, nullable=True)           # 0-10
    is_viral = Column(Boolean, default=False)             # view_count > 10x channel avg

    # pgvector embedding of title+transcript for similarity search
    content_embedding = Column(Vector(1536), nullable=True)

    is_competitor_video = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    channel = relationship("Channel", back_populates="videos")

    def __repr__(self):
        """Debugging representation of the Video model."""
        return (
            f"<Video(id={self.id}, youtube_video_id={self.youtube_video_id}, "
            f"title={self.title[:30] if self.title else None}..., "
            f"views={self.view_count}, is_viral={self.is_viral})>"
        )