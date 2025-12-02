from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(100), nullable=False)     # channel_analysis|competitor_scan|gap_detect
    entity_id = Column(UUID(as_uuid=True), nullable=True)  # channel_id or competitor_id
    status = Column(String(50), default="queued")      # queued|running|done|failed
    progress_pct = Column(Integer, default=0)          # 0-100
    result_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    celery_task_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        """Debugging representation of the AnalysisJob model."""
        return (
            f"<AnalysisJob(id={self.id}, job_type={self.job_type}, "
            f"status={self.status}, progress_pct={self.progress_pct})>"
        )