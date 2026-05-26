"""
Jobs router — polling endpoint for long-running analysis tasks.

Frontend polls GET /jobs/{job_id} every 3s while status is non-terminal.
TanStack Query handles this via refetchInterval set to false once done.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis_job import AnalysisJob
from app.models.user import User
from app.utils.auth_utils import get_current_user
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter()


class JobResponse(BaseModel):
    id: str
    job_type: str
    entity_id: Optional[str]
    status: str          # queued | running | done | failed
    progress_pct: int
    current_step: Optional[str]
    result_summary: Optional[str]
    error_message: Optional[str]
    celery_task_id: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    model_config = {"from_attributes": True}


@router.get("/{job_id}", response_model=JobResponse, tags=["jobs"])
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the current status of an analysis job.

    Poll this endpoint every 3 seconds until status is 'done' or 'failed'.

    Status values:
    - **queued**: Job is waiting to be picked up by a worker
    - **running**: Worker is actively processing
    - **done**: Completed successfully — fetch the entity for results
    - **failed**: Processing error — check error_message
    """
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id format")

    job = db.query(AnalysisJob).filter(AnalysisJob.id == uid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Return the job — no ownership check because job IDs are non-guessable UUIDs
    # and the payload contains no sensitive user data.
    return JobResponse(
        id=str(job.id),
        job_type=job.job_type,
        entity_id=str(job.entity_id) if job.entity_id else None,
        status=job.status,
        progress_pct=job.progress_pct or 0,
        current_step=getattr(job, "current_step", None),
        result_summary=job.result_summary,
        error_message=job.error_message,
        celery_task_id=job.celery_task_id,
        created_at=job.created_at.isoformat() if job.created_at else "",
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )
