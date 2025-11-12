from celery import Celery
from app.config import settings

# Celery app configuration
# Note: For MVP, we use FastAPI BackgroundTasks instead of Celery
# This Celery app is set up for future migration when you need distributed task processing

celery_app = Celery(
    "creatoriq",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.channel_tasks", "app.tasks.competitor_tasks", "app.tasks.trend_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "refresh-trends-daily": {
            "task": "app.tasks.trend_tasks.refresh_trends",
            "schedule": 86400.0,  # every 24 hours
        }
    }
)