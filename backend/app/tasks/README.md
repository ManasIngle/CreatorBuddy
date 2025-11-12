# Tasks Module

This module contains Celery task definitions for the CreatorIQ platform. These tasks handle long-running background operations like channel analysis, competitor scanning, and trend refresh.

## Overview

**Note:** For MVP, the platform uses FastAPI BackgroundTasks instead of Celery for simplicity. This module is set up for future migration to distributed task processing when scalability requires it.

## File Structure

```
backend/app/tasks/
├── __init__.py              # Package marker
├── celery_app.py           # Celery configuration
├── channel_tasks.py        # Channel analysis tasks
├── competitor_tasks.py     # Competitor analysis tasks
└── trend_tasks.py          # Trend refresh tasks
```

---

## celery_app.py

**File:** [`celery_app.py`](backend/app/tasks/celery_app.py)

### Celery Configuration

```python
celery_app = Celery(
    "creatoriq",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.channel_tasks",
        "app.tasks.competitor_tasks",
        "app.tasks.trend_tasks"
    ]
)
```

### Configuration Settings

```python
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,           # Acknowledge after completion
    worker_prefetch_multiplier=1,  # One task per worker at a time
)
```

### Beat Schedule

Daily trend refresh is scheduled:
```python
beat_schedule={
    "refresh-trends-daily": {
        "task": "app.tasks.trend_tasks.refresh_trends",
        "schedule": 86400.0,  # Every 24 hours
    }
}
```

---

## channel_tasks.py

**File:** [`channel_tasks.py`](backend/app/tasks/channel_tasks.py)

### Task: `run_full_channel_analysis`

**Celery Task Name:** `app.tasks.channel_tasks.run_full_channel_analysis`

**Signature:**
```python
run_full_channel_analysis(channel_id: str, uploads_playlist_id: str = None)
```

**Purpose:** Full analysis of a YouTube channel.

**Migration Path:**
1. Install Redis and configure REDIS_URL
2. Start Celery worker: `celery -A app.tasks.celery_app worker`
3. Start Celery beat: `celery -A app.tasks.celery_app beat`
4. Replace `BackgroundTasks.add_task()` with `.delay()`

**Current Implementation:** Stub for future migration. Full logic in [`routers/channels.py:run_full_channel_analysis()`](backend/app/routers/channels.py:22).

---

### Helper Functions

#### `get_optimized_transcript(transcript_text: str) -> str`

Optimizes transcript for AI consumption.

**Parameters:**
- `transcript_text` (str): Raw transcript

**Returns:** Truncated, cleaned transcript (max 10000 chars)

---

#### `get_top_videos_for_analysis(video_stats: list, max_videos: int = 5, include_transcript_for: int = 3) -> list`

Selects and prepares top videos for AI analysis.

**Parameters:**
- `video_stats` (list): Video stat dicts sorted by views
- `max_videos` (int, default=5): Max videos to include
- `include_transcript_for` (int, default=3): How many top videos include transcript

**Returns:**
```python
[
    {
        'youtube_video_id': '...',
        'title': 'Video title',
        'views': 100000,
        'likes': 5000,
        'duration_seconds': 600,
        'transcript_excerpt': '...'  # Only for top N
    }
]
```

---

#### `compress_channel_context(channel_data: dict, video_stats: list) -> dict`

Compresses channel and video data for efficient AI analysis.

**Parameters:**
- `channel_data` (dict): Full channel data from YouTube API
- `video_stats` (list): Video stats list

**Returns:**
```python
{
    'title': 'Channel Name',
    'subscriber_count': 100000,
    'total_videos': 50,
    'top_videos': [
        {'title': '...', 'views': 100000, 'likes': 5000, 'duration_min': 10}
    ]
}
```

---

#### `should_fetch_transcript(video_views: int, rank: int, max_transcripts: int = 5) -> bool`

Determines if transcript should be fetched for a video.

**Parameters:**
- `video_views` (int): View count
- `rank` (int): Position in sorted list
- `max_transcripts` (int, default=5): Max transcripts to fetch

**Returns:** True if transcript should be fetched

**Logic:**
- Always fetch for top N videos
- Always fetch if >1M views (viral potential)

---

#### `get_comment_analysis_limit(channel_subscriber_count: int) -> int`

Determines comments to analyze based on channel size.

**Parameters:**
- `channel_subscriber_count` (int): Number of subscribers

**Returns:**
- `50` if >1M subs
- `30` if >100K subs
- `20` if >10K subs
- `10` otherwise

---

## competitor_tasks.py

**File:** [`competitor_tasks.py`](backend/app/tasks/competitor_tasks.py)

### Task: `run_competitor_analysis`

**Celery Task Name:** `app.tasks.competitor_tasks.run_competitor_analysis`

**Signature:**
```python
run_competitor_analysis(competitor_id: str, youtube_channel_id: str, niche: str, channel_id: str)
```

**Purpose:** Analyze competitor channel for intelligence.

**Current Implementation:** Stub for future migration. Full logic in [`routers/competitors.py:run_competitor_analysis()`](backend/app/routers/competitors.py:18).

---

## trend_tasks.py

**File:** [`trend_tasks.py`](backend/app/tasks/trend_tasks.py)

### Task: `refresh_trends`

**Celery Task Name:** `app.tasks.trend_tasks.refresh_trends`

**Signature:**
```python
refresh_trends()
```

**Purpose:** Daily refresh of trending topics.

**Schedule:** Every 24 hours (configured in beat_schedule)

**Current Implementation:** Placeholder. Would use YouTube search to find emerging trends.

---

## Migration Guide

### When to Migrate

Consider migrating from BackgroundTasks to Celery when:
- You need distributed task processing across multiple servers
- You need task scheduling (beat)
- You need task monitoring and retry UI
- Background tasks are timing out
- You need task prioritization

### Migration Steps

1. **Install Dependencies:**
```bash
pip install celery[redis]
```

2. **Start Redis:**
```bash
docker run -d -p 6379:6379 redis
```

3. **Configure Environment:**
```bash
export REDIS_URL=redis://localhost:6379/0
```

4. **Start Worker:**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

5. **Start Beat (for scheduled tasks):**
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

6. **Update Router Code:**
Replace:
```python
background_tasks.add_task(run_full_channel_analysis, channel_id, playlist_id)
```

With:
```python
run_full_channel_analysis.delay(channel_id, playlist_id)
```

---

## Testing Celery Tasks

### Unit Testing

```python
from unittest.mock import patch, MagicMock
from app.tasks.channel_tasks import run_full_channel_analysis

def test_channel_analysis_task():
    with patch('app.tasks.channel_tasks.Channel') as mock_channel:
        with patch('app.tasks.channel_tasks.db') as mock_db:
            mock_channel.id = "test-uuid"
            mock_channel.youtube_channel_id = "UCxxxxxxx"
            
            # Call task directly (synchronously for testing)
            run_full_channel_analysis("test-uuid", "UUxxxxxxx")
            
            # Assert behavior
            mock_channel.analysis_status.assert_called_with("running")
```

### Integration Testing

```python
import pytest
from app.tasks.celery_app import celery_app

@pytest.fixture
def celery_config():
    return {
        'broker_url': 'redis://localhost:6379/0',
        'result_backend': 'redis://localhost:6379/0',
    }

def test_task_execution():
    result = run_full_channel_analysis.delay("test-uuid", None)
    assert result.get(timeout=30) is not None  # Wait 30s max
```

---

## Monitoring

### Flower (Celery Monitoring)

```bash
pip install flower
celery -A app.tasks.celery_app flower --port=5555
```

Visit http://localhost:5555 for task monitoring.

### CLI Commands

```bash
# List scheduled tasks
celery -A app.tasks.celery_app inspect scheduled

# List active tasks
celery -A app.tasks.celery_app inspect active

# List workers
celery -A app.tasks.celery_app inspect active

# Purge pending tasks
celery -A app.tasks.celery_app purge
```

---

## Error Handling

### Retry Configuration

Add to task decorator:
```python
@celery_app.task(
    name="app.tasks.channel_tasks.run_full_channel_analysis",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def run_full_channel_analysis(channel_id: str, uploads_playlist_id: str = None):
    ...
```

### Task Failure Handling

```python
@celery_app.task(
    bind=True,
    max_retries=3
)
def run_full_channel_analysis(self, channel_id: str, ...):
    try:
        # Task logic
        pass
    except Exception as e:
        # Update status to failed
        self.retry(exc=e, countdown=60)
```

---

## Performance Considerations

| Task | Duration | Resources |
|------|----------|-----------|
| Channel analysis | 2-5 min | High (YouTube API, AI) |
| Competitor analysis | 1-3 min | Medium |
| Trend refresh | 30 sec | Low |

### Prefetch Settings

```python
worker_prefetch_multiplier=1  # One task per worker at a time
```

This prevents memory issues when tasks are CPU-intensive.

---

## Task Signatures Reference

| Task | Signature | Schedule |
|------|-----------|----------|
| Channel analysis | `run_full_channel_analysis(channel_id, uploads_playlist_id?)` | On-demand |
| Competitor analysis | `run_competitor_analysis(competitor_id, youtube_id, niche, channel_id)` | On-demand |
| Trend refresh | `refresh_trends()` | Daily |