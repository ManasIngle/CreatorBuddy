from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class Trend(Base):
    __tablename__ = "trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(500), nullable=False)
    niche = Column(String(255), nullable=True)
    velocity_score = Column(Float, default=0.0)        # how fast it's growing (0-10)
    saturation_score = Column(Float, default=0.0)      # how crowded (0-10)
    opportunity_window = Column(String(50), default="open") # open|closing|closed
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    peak_predicted_at = Column(DateTime, nullable=True)
    evidence = Column(JSON, default=list)              # ["10 videos in last 3 days", "search +40%"]
    recommended_action = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        """Debugging representation of the Trend model."""
        return (
            f"<Trend(id={self.id}, topic={self.topic[:30] if self.topic else None}..., "
            f"velocity_score={self.velocity_score}, opportunity_window={self.opportunity_window})>"
        )