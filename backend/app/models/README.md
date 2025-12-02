# Models Module

This module defines all SQLAlchemy ORM models for the CreatorIQ platform. These models represent the core data structures stored in PostgreSQL with pgvector extensions for vector similarity search.

## Overview

The models use PostgreSQL as the database backend with [pgvector](https://github.com/pgvector/pgvector) extension for embedding storage and similarity search. All models inherit from `Base` defined in [`app.database`](backend/app/database.py).

## File Structure

```
backend/app/models/
├── __init__.py          # Package marker
├── user.py              # User model
├── channel.py           # Channel model
├── video.py             # Video model
├── competitor.py        # Competitor model
├── content_gap.py       # ContentGap model
├── script.py            # Script model
├── hook.py              # Hook model
├── trend.py             # Trend model
└── analysis_job.py      # AnalysisJob model
```

## Database Configuration

All models use the shared `Base` from:
```python
from app.database import Base
```

---

## User Model

**File:** [`user.py`](backend/app/models/user.py)

### Table Name
`users`

### Purpose
Represents a CreatorIQ user account. Supports both password-based and OAuth (Google) authentication.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `email` | String(255) | Unique, Not Null, Indexed | User's email address |
| `hashed_password` | String(255) | Nullable | bcrypt hashed password (null for OAuth-only users) |
| `full_name` | String(255) | Nullable | User's display name |
| `avatar_url` | Text | Nullable | Profile picture URL |
| `plan` | String(50) | Default "free" | Subscription tier: `free`, `starter`, `pro`, `agency` |
| `is_active` | Boolean | Default True | Whether account is active |
| `is_verified` | Boolean | Default False | Email verification status |
| `created_at` | DateTime | Auto | Account creation timestamp |
| `updated_at` | DateTime | Auto | Last update timestamp |
| `google_access_token` | Text | Nullable | OAuth access token |
| `google_refresh_token` | Text | Nullable | OAuth refresh token |
| `google_token_expiry` | DateTime | Nullable | OAuth token expiration |

### Relationships

```python
channels = relationship("Channel", back_populates="user", cascade="all, delete-orphan")
scripts = relationship("Script", back_populates="user", cascade="all, delete-orphan")
```

- **channels**: One-to-Many with `Channel` - User's connected YouTube channels
- **scripts**: One-to-Many with `Script` - User's generated scripts

### Indexes

- `email` - Unique index for fast lookups and login

### Example Usage

```python
from app.models.user import User

# Create user
user = User(
    email="creator@example.com",
    full_name="John Creator",
    plan="pro"
)

# Query user
found_user = session.query(User).filter(User.email == "creator@example.com").first()

# Check OAuth status
if user.google_refresh_token:
    # User signed up via Google OAuth
    pass
```

---

## Channel Model

**File:** [`channel.py`](backend/app/models/channel.py)

### Table Name
`channels`

### Purpose
Represents a YouTube channel connected by a user. Contains AI-analyzed metadata, content embeddings, and performance metrics.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `user_id` | UUID | ForeignKey("users.id"), Not Null | Owner user |
| `youtube_channel_id` | String(100) | Unique, Not Null, Indexed | YouTube channel ID (UCxxxxxxx format) |
| `title` | String(500) | Not Null | Channel title |
| `description` | Text | Nullable | Channel description |
| `subscriber_count` | Integer | Default 0 | Current subscriber count |
| `video_count` | Integer | Default 0 | Total video count |
| `view_count` | Integer | Default 0 | Total lifetime views |
| `thumbnail_url` | Text | Nullable | Channel thumbnail URL |
| `country` | String(10) | Nullable | Country code (e.g., "US") |
| `niche` | String(255) | Nullable | AI-detected content niche |
| `niche_tags` | JSON | Default list | Array of niche tags |
| `audience_type` | String(255) | Nullable | AI-detected audience persona |
| `personality_summary` | Text | Nullable | AI-generated creator persona description |
| `speaking_style` | Text | Nullable | AI-detected speaking style |
| `storytelling_structure` | Text | Nullable | AI-detected storytelling approach |
| `avg_views` | Float | Default 0.0 | Average views per video |
| `avg_engagement_rate` | Float | Default 0.0 | Average (likes+comments)/views |
| `avg_retention_rate` | Float | Default 0.0 | Average estimated retention |
| `upload_frequency_days` | Float | Nullable | Average days between uploads |
| `best_upload_day` | String(20) | Nullable | Day of week with best performance |
| `best_upload_hour` | Integer | Nullable | Hour of day (0-23) with best performance |
| `last_analyzed_at` | DateTime | Nullable | Last AI analysis timestamp |
| `analysis_status` | String(50) | Default "pending" | Status: `pending`, `running`, `done`, `failed` |
| `created_at` | DateTime | Auto | Record creation timestamp |
| `content_embedding` | Vector(1536) | Nullable | pgvector embedding of channel's content style |

### Relationships

```python
user = relationship("User", back_populates="channels")
videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")
competitors = relationship("Competitor", back_populates="channel", cascade="all, delete-orphan")
content_gaps = relationship("ContentGap", back_populates="channel", cascade="all, delete-orphan")
```

### Indexes

- `youtube_channel_id` - Unique index

### Performance Considerations

- `content_embedding` uses pgvector Vector(1536) for OpenAI ada-002 embeddings
- Vector similarity search enables "channels like this" recommendations

### Example Usage

```python
from app.models.channel import Channel

# Create channel
channel = Channel(
    user_id=user_id,
    youtube_channel_id="UCxxxxxxx",
    title="Tech Creator Pro",
    niche="technology"
)

# Query channels by niche
tech_channels = session.query(Channel).filter(
    Channel.niche_tags.contains(["tech"])
).all()

# Find similar channels using vector similarity
from sqlalchemy import func
similar = session.query(Channel).filter(
    func.cosine_distance(Channel.content_embedding, target_embedding) < 0.5
).all()
```

---

## Video Model

**File:** [`video.py`](backend/app/models/video.py)

### Table Name
`videos`

### Purpose
Represents a YouTube video with AI-extracted intelligence including transcripts, engagement metrics, and content embeddings.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `channel_id` | UUID | ForeignKey("channels.id"), Not Null | Parent channel |
| `youtube_video_id` | String(20) | Unique, Not Null, Indexed | YouTube video ID (11 chars) |
| `title` | String(500) | Not Null | Video title |
| `description` | Text | Nullable | Video description |
| `transcript` | Text | Nullable | Full transcript text from YouTube |
| `hook_text` | Text | Nullable | First ~30 seconds of transcript |
| `thumbnail_url` | Text | Nullable | Video thumbnail URL |
| `duration_seconds` | Integer | Default 0 | Video duration |
| `view_count` | Integer | Default 0 | Total views |
| `like_count` | Integer | Default 0 | Like count |
| `comment_count` | Integer | Default 0 | Comment count |
| `engagement_rate` | Float | Default 0.0 | Calculated (likes+comments)/views |
| `estimated_retention_rate` | Float | Nullable | AI-estimated retention 0-100% |
| `tags` | JSON | Default list | YouTube tags |
| `category_id` | String(10) | Nullable | YouTube category ID |
| `published_at` | DateTime | Not Null | Publish timestamp |
| `hook_quality_score` | Float | Nullable | AI score 0-10 |
| `emotional_triggers` | JSON | Default list | Detected emotions: curiosity, fear, excitement |
| `storytelling_type` | String(100) | Nullable | Format type: problem-solution, listicle, story |
| `pacing_score` | Float | Nullable | AI score 0-10 |
| `is_viral` | Boolean | Default False | True if views > 10x channel average |
| `content_embedding` | Vector(1536) | Nullable | pgvector embedding of title+transcript |
| `is_competitor_video` | Boolean | Default False | True if from competitor channel |
| `created_at` | DateTime | Auto | Record creation timestamp |

### Relationships

```python
channel = relationship("Channel", back_populates="videos")
```

### Indexes

- `youtube_video_id` - Unique index

### AI-Extracted Intelligence

The following fields are populated by AI analysis (see [`app/intelligence`](backend/app/intelligence)):

- `hook_quality_score`: Quality of opening hook (0-10)
- `emotional_triggers`: What emotions the video leverages
- `storytelling_type`: Narrative structure type
- `pacing_score`: Editing/speaking pacing quality
- `is_viral`: Boolean flag for viral content detection

### Performance Considerations

- `content_embedding` supports semantic video search
- `transcript` can be large (many MB for long videos) - consider compression

### Example Usage

```python
from app.models.video import Video
from sqlalchemy import func

# Create video
video = Video(
    channel_id=channel.id,
    youtube_video_id="dQw4w9WgXcQ",
    title="Amazing Video Title",
    view_count=100000,
    published_at=datetime(2024, 1, 15)
)

# Find viral videos
viral = session.query(Video).filter(Video.is_viral == True).all()

# Find high-engagement educational videos
best_edu = session.query(Video).filter(
    Video.storytelling_type == "educational",
    Video.engagement_rate > 0.05
).order_by(Video.engagement_rate.desc()).limit(10)

# Semantic search for similar videos
results = session.query(Video).filter(
    func.cosine_distance(Video.content_embedding, query_embedding) < 0.3
).all()
```

---

## Competitor Model

**File:** [`competitor.py`](backend/app/models/competitor.py)

### Table Name
`competitors`

### Purpose
Represents a competitor YouTube channel being tracked for competitive analysis. Linked to a user's channel for comparison.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `channel_id` | UUID | ForeignKey("channels.id"), Not Null | User's channel this competitor belongs to |
| `youtube_channel_id` | String(100) | Not Null, Indexed | Competitor's YouTube channel ID |
| `title` | String(500) | Not Null | Channel title |
| `subscriber_count` | Integer | Default 0 | Subscriber count |
| `avg_views` | Float | Default 0.0 | Average views per video |
| `avg_engagement_rate` | Float | Default 0.0 | Average engagement rate |
| `niche_overlap_score` | Float | Default 0.0 | Similarity to user's channel (0-1) |
| `why_they_succeed` | Text | Nullable | AI analysis of success factors |
| `best_formats` | JSON | Default list | Content formats: tutorial, review, story |
| `emotional_triggers_used` | JSON | Default list | Emotions leveraged |
| `content_gaps` | JSON | Default list | Topics competitor is missing |
| `hook_patterns` | JSON | Default list | Recurring hook patterns |
| `upload_frequency_days` | Float | Nullable | Days between uploads |
| `thumbnail_style` | Text | Nullable | Thumbnail aesthetic description |
| `last_analyzed_at` | DateTime | Nullable | Last AI analysis timestamp |
| `analysis_status` | String(50) | Default "pending" | Status: pending, running, done, failed |
| `created_at` | DateTime | Auto | Record creation timestamp |

### Relationships

```python
channel = relationship("Channel", back_populates="competitors")
```

### Indexes

- `youtube_channel_id` - Index for fast lookups

### Example Usage

```python
from app.models.competitor import Competitor

# Create competitor entry
competitor = Competitor(
    channel_id=user_channel.id,
    youtube_channel_id="UCyyyyyyy",
    title="Tech Reviews Daily",
    niche_overlap_score=0.85
)

# Find competitors with high overlap
similar = session.query(Competitor).filter(
    Competitor.niche_overlap_score > 0.7
).all()

# Get top competitors by engagement
top_competitors = session.query(Competitor).order_by(
    Competitor.avg_engagement_rate.desc()
).limit(5)
```

---

## ContentGap Model

**File:** [`content_gap.py`](backend/app/models/content_gap.py)

### Table Name
`content_gaps`

### Purpose
Represents an identified content opportunity for a user's channel. AI-generated insights on topics, angles, and market demand.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `channel_id` | UUID | ForeignKey("channels.id"), Not Null | User's channel |
| `topic` | String(500) | Not Null | Content gap topic |
| `reason` | Text | Not Null | Why this gap exists |
| `opportunity_score` | Float | Default 0.0 | Value score 0-10 |
| `competition_level` | String(20) | Default "medium" | `low`, `medium`, `high` |
| `estimated_search_demand` | String(20) | Default "medium" | `low`, `medium`, `high` |
| `suggested_angle` | Text | Nullable | How to approach this topic |
| `suggested_title` | String(500) | Nullable | Potential video title |
| `supporting_evidence` | JSON | Default list | Evidence strings |
| `trend_direction` | String(20) | Default "stable" | `rising`, `stable`, `declining` |
| `source_type` | String(50) | Default "competitor_gap" | Origin: competitor_gap, search, comment, trend |
| `is_acted_on` | Boolean | Default False | Creator has made video on this |
| `created_at` | DateTime | Auto | Record creation timestamp |

### Relationships

```python
channel = relationship("Channel", back_populates="content_gaps")
```

### Source Types

- `competitor_gap`: Topic competitors haven't covered
- `search`: High search demand but low competition
- `comment`: Common questions in comments
- `trend`: Emerging trend opportunity

### Example Usage

```python
from app.models.content_gap import ContentGap

# Create content gap
gap = ContentGap(
    channel_id=user_channel.id,
    topic="AI video editing 2024",
    reason="Competitors focus on AI text tools, not video",
    opportunity_score=8.5,
    competition_level="low",
    suggested_angle="Show practical workflow, not tool list",
    trend_direction="rising"
)

# Find high-opportunity gaps not yet acted on
gaps = session.query(ContentGap).filter(
    ContentGap.opportunity_score > 7.0,
    ContentGap.is_acted_on == False,
    ContentGap.trend_direction == "rising"
).all()

# Prioritize by trend direction
rising_gaps = session.query(ContentGap).filter(
    ContentGap.channel_id == channel.id,
    ContentGap.trend_direction == "rising"
).order_by(ContentGap.opportunity_score.desc()).all()
```

---

## Script Model

**File:** [`script.py`](backend/app/models/script.py)

### Table Name
`scripts`

### Purpose
Represents an AI-generated video script with title suggestions, hook, full script, CTA, and short-form adaptation.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `user_id` | UUID | ForeignKey("users.id"), Not Null | Owner user |
| `channel_id` | UUID | ForeignKey("channels.id"), Nullable | Associated channel (optional context) |
| `topic` | String(500) | Not Null | Video topic |
| `target_duration_minutes` | Integer | Default 10 | Target video length |
| `format_type` | String(100) | Default "educational" | `educational`, `story`, `list`, `review` |
| `tone` | String(100) | Default "conversational" | Script tone |
| `title_suggestions` | JSON | Default list | 3 title options |
| `hook` | Text | Nullable | Opening 30-second hook |
| `full_script` | Text | Nullable | Complete script text |
| `cta_text` | Text | Nullable | Call-to-action text |
| `short_form_adaptation` | Text | Nullable | 60-second version for Shorts/Reels |
| `thumbnail_concept` | Text | Nullable | Thumbnail idea description |
| `retention_notes` | Text | Nullable | Editing tips for retention |
| `generation_status` | String(50) | Default "pending" | Status: pending, generating, done, failed |
| `created_at` | DateTime | Auto | Record creation timestamp |

### Relationships

```python
user = relationship("User", back_populates="scripts")
```

### Generation Status Flow

```
pending → generating → done
                    ↘ failed
```

### Example Usage

```python
from app.models.script import Script

# Create script request
script = Script(
    user_id=user.id,
    channel_id=channel.id,
    topic="How to start a YouTube channel",
    target_duration_minutes=12,
    format_type="educational",
    tone="friendly"
)

# Get completed scripts for a channel
completed = session.query(Script).filter(
    Script.channel_id == channel.id,
    Script.generation_status == "done"
).all()

# Get script with all outputs
full_script = session.query(Script).filter(
    Script.id == script_id,
    Script.full_script.isnot(None)
).first()
```

---

## Hook Model

**File:** [`hook.py`](backend/app/models/hook.py)

### Table Name
`hooks`

### Purpose
Represents a video hook (opening sequence) with AI analysis of type, emotional triggers, and predicted performance.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `channel_id` | UUID | ForeignKey("channels.id"), Nullable | Associated channel |
| `hook_text` | Text | Not Null | The hook text/description |
| `hook_type` | String(100) | Not Null | Type classification |
| `niche` | String(255) | Nullable | Content niche |
| `emotional_trigger` | String(100) | Nullable | Primary emotion: curiosity, fear, excitement |
| `predicted_retention_boost` | Float | Nullable | Predicted retention boost 0-100% |
| `source_video_id` | String(20) | Nullable | YouTube video ID if learned from video |
| `is_ai_generated` | Boolean | Default True | True if AI-generated |
| `performance_score` | Float | Nullable | Real performance score (updated when used) |
| `created_at` | DateTime | Auto | Record creation timestamp |

### Hook Types

- `curiosity`: Piques viewer interest
- `shock`: Surprising statement/fact
- `story`: Narrative opening
- `question`: Rhetorical or direct question
- `contrarian`: Opposite viewpoint

### Example Usage

```python
from app.models.hook import Hook

# Create hook from viral video analysis
hook = Hook(
    channel_id=channel.id,
    hook_text="What if I told you 90% of creators make this mistake...",
    hook_type="curiosity",
    niche="youtube_tips",
    emotional_trigger="curiosity",
    predicted_retention_boost=25.0,
    source_video_id="dQw4w9WgXcQ"
)

# Get hooks by type for channel
curiosity_hooks = session.query(Hook).filter(
    Hook.channel_id == channel.id,
    Hook.hook_type == "curiosity"
).all()

# Find best performing hook patterns
top_hooks = session.query(Hook).filter(
    Hook.performance_score.isnot(None)
).order_by(Hook.performance_score.desc()).limit(20)
```

---

## Trend Model

**File:** [`trend.py`](backend/app/models/trend.py)

### Table Name
`trends`

### Purpose
Represents a trending topic with velocity, saturation, and opportunity scoring. Global trends tracked across the platform.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `topic` | String(500) | Not Null | Trend topic keyword |
| `niche` | String(255) | Nullable | Related niche |
| `velocity_score` | Float | Default 0.0 | Growth speed 0-10 |
| `saturation_score` | Float | Default 0.0 | Market crowdedness 0-10 |
| `opportunity_window` | String(50) | Default "open" | `open`, `closing`, `closed` |
| `first_detected_at` | DateTime | Auto | Initial detection |
| `peak_predicted_at` | DateTime | Nullable | AI-predicted peak time |
| `evidence` | JSON | Default list | Evidence strings |
| `recommended_action` | Text | Nullable | AI recommendation |
| `updated_at` | DateTime | Auto | Last update |

### Example Usage

```python
from app.models.trend import Trend

# Create trend entry
trend = Trend(
    topic="AI video editing",
    niche="technology",
    velocity_score=8.5,
    saturation_score=3.0,
    opportunity_window="open",
    evidence=["40 videos in 7 days", "Search trend +65%"],
    recommended_action="Create tutorial before market saturates"
)

# Find open opportunities
opportunities = session.query(Trend).filter(
    Trend.opportunity_window == "open",
    Trend.velocity_score > 5.0
).all()

# Get trends by niche
tech_trends = session.query(Trend).filter(
    Trend.niche == "technology"
).order_by(Trend.velocity_score.desc()).all()
```

---

## AnalysisJob Model

**File:** [`analysis_job.py`](backend/app/models/analysis_job.py)

### Table Name
`analysis_jobs`

### Purpose
Tracks long-running AI analysis tasks. Links Celery task IDs to job status for polling and monitoring.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key, Auto-generated | Unique identifier |
| `job_type` | String(100) | Not Null | Type of analysis |
| `entity_id` | UUID | Nullable | channel_id or competitor_id |
| `status` | String(50) | Default "queued" | Status: queued, running, done, failed |
| `progress_pct` | Integer | Default 0 | Progress 0-100 |
| `result_summary` | Text | Nullable | Brief result description |
| `error_message` | Text | Nullable | Error details if failed |
| `celery_task_id` | String(255) | Nullable | Celery task ID for linking |
| `created_at` | DateTime | Auto | Job creation time |
| `started_at` | DateTime | Nullable | When processing began |
| `completed_at` | DateTime | Nullable | When job finished |

### Job Types

- `channel_analysis`: Full channel intelligence analysis
- `competitor_scan`: Competitor channel analysis
- `gap_detect`: Content gap detection

### Status Flow

```
queued → running → done
              ↘ failed
```

### Example Usage

```python
from app.models.analysis_job import AnalysisJob

# Create analysis job
job = AnalysisJob(
    job_type="channel_analysis",
    entity_id=channel.id,
    celery_task_id="abc-123-def"
)

# Poll for completion
def wait_for_job(job_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        job = session.query(AnalysisJob).get(job_id)
        if job.status in ("done", "failed"):
            return job
        time.sleep(2)
    return None

# Get running jobs for channel
running = session.query(AnalysisJob).filter(
    AnalysisJob.entity_id == channel.id,
    AnalysisJob.status == "running"
).all()
```

---

## Dependencies

The models module depends on:

```python
from app.database import Base  # SQLAlchemy declarative base
from sqlalchemy import ...       # Column types
from sqlalchemy.orm import ...  # Relationship utilities
from pgvector.sqlalchemy import Vector  # Vector type for embeddings
```

### External Requirements

- **PostgreSQL** with `pgvector` extension enabled
- **SQLAlchemy** 2.x for ORM operations
- **uuid** for UUID generation

### Database Migration

Models use Alembic for migrations. Migration files are in:
```
backend/alembic/versions/
```

To create a migration after model changes:
```bash
cd backend
alembic revision --autogenerate -m "Add content_embedding to Channel"
```

---

## Testing Notes

### Unit Testing Models

```python
import pytest
from app.models.user import User
from app.database import Base, engine

@pytest.fixture
def test_user():
    return User(
        email="test@example.com",
        full_name="Test User",
        plan="free"
    )

def test_user_repr(test_user):
    assert "test@example.com" in repr(test_user)

def test_user_plan_default():
    user = User(email="test2@example.com")
    assert user.plan == "free"
```

### Test Database Setup

For testing, use an in-memory SQLite or separate PostgreSQL test database:
```python
TEST_DATABASE_URL = "postgresql://test_user:pass@localhost/creatoriq_test"
```

---

## Indexes Summary

| Model | Field(s) | Type | Purpose |
|-------|----------|------|---------|
| User | email | Unique | Login lookups |
| Channel | youtube_channel_id | Unique | YouTube API lookups |
| Video | youtube_video_id | Unique | YouTube API lookups |
| Competitor | youtube_channel_id | Index | Competitor lookups |

---

## Relationship Diagram

```
User (1) ──────< Channel (M) >──────< Video (M)
  │                 │
  │                 ├────< Competitor (M)
  │                 ├────< ContentGap (M)
  │                 │
  │                 └────< Hook (M, optional)

User (1) ──────< Script (M)

Trend (1) - standalone global table
AnalysisJob (1) - standalone job tracking