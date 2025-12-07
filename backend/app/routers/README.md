# Routers Module

This module contains all FastAPI API endpoints (routers) for the CreatorIQ platform.

## Overview

Routers define REST API endpoints organized by domain. Each router handles:
- HTTP request/response handling
- Authentication via JWT
- Authorization checks
- Input validation
- Background task orchestration
- Response formatting

## File Structure

```
backend/app/routers/
├── __init__.py          # Package marker
├── auth.py              # Authentication endpoints
├── channels.py          # Channel management
├── competitors.py       # Competitor tracking
├── gaps.py              # Content gap detection
├── hooks.py             # Hook generation/retrieval
├── scripts.py           # Script generation
├── audience.py          # Audience insights
├── research.py           # Deep research endpoints
├── thumbnails.py        # Thumbnail analysis
└── trends.py            # Trend listing
```

---

## auth.py

**File:** [`auth.py`](backend/app/routers/auth.py)

### Router: `/api/v1/auth`

Authentication and user management endpoints.

---

#### `POST /register` - Register new user

**Auth Required:** No

**Request Body:** `UserCreate`
```python
{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Creator"  # optional
}
```

**Response:** `UserResponse` (201 Created)
```python
{
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Creator",
    "plan": "free",
    "is_active": True,
    "is_verified": False,
    "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**
- `400`: Email already registered

---

#### `POST /login` - User login

**Auth Required:** No (OAuth2 form)

**Request:** OAuth2 password flow form data
```
username: user@example.com
password: securepassword
```

**Response:** `TokenResponse`
```python
{
    "access_token": "eyJhbGc...",
    "token_type": "bearer"
}
```

**Error Responses:**
- `401`: Invalid credentials
- `403`: Account inactive

---

#### `GET /me` - Get current user

**Auth Required:** Yes (Bearer token)

**Response:** `UserResponse`

---

#### `POST /google/callback` - Google OAuth callback

**Auth Required:** No

**Request Params:**
- `code`: Authorization code from Google

**Response:**
```python
{
    "access_token": "eyJhbGc...",
    "token_type": "bearer",
    "user": {...}
}
```

**Scopes Required:** `openid`, `email`, `profile`, `https://www.googleapis.com/auth/youtube.readonly`

---

## channels.py

**File:** [`channels.py`](backend/app/routers/channels.py)

### Router: `/api/v1/channels`

Channel management and analysis endpoints.

---

#### `POST /connect` - Connect YouTube channel

**Auth Required:** Yes

**Request Body:** `ConnectChannelRequest`
```python
{
    "youtube_channel_id": "UCxxxxxxx"  # or @handle
}
```

**Response:** `ChannelResponse` (201 Created)

**Background Process:**
- Fetches channel data from YouTube API
- Queues full channel analysis
- Creates AnalysisJob record

**Analysis Duration:** 2-3 minutes

---

#### `GET /` - List user's channels

**Auth Required:** Yes

**Query Params:**
- `page` (int, default=1): Page number
- `page_size` (int, default=50, max=100): Items per page

**Response:** `ChannelListResponse`
```python
{
    "items": [...],
    "total": 10,
    "page": 1,
    "page_size": 50,
    "pages": 1
}
```

**Features:**
- ETag caching (5 min TTL)
- Conditional GET support via `If-None-Match` header

---

#### `GET /{channel_id}` - Get channel details

**Auth Required:** Yes

**Response:** `ChannelResponse`

**Features:**
- ETag caching (10 min TTL)
- 304 Not Modified support

---

#### `POST /{channel_id}/re-analyze` - Trigger re-analysis

**Auth Required:** Yes

**Response:**
```python
{
    "message": "Re-analysis queued"
}
```

**Background Process:**
- Invalidates channel cache
- Re-runs full channel analysis
- Updates all video data and AI insights

---

## competitors.py

**File:** [`competitors.py`](backend/app/routers/competitors.py)

### Router: `/api/v1/competitors`

Competitor tracking endpoints.

---

#### `POST /{channel_id}/add` - Add competitor

**Auth Required:** Yes

**Query Params:**
- `youtube_channel_id` (str): Competitor's YouTube channel ID

**Response:** `CompetitorResponse` (201 Created)

**Background Process:**
- Creates competitor record with "pending" status
- Queues competitor analysis

---

#### `GET /{channel_id}` - List competitors

**Auth Required:** Yes

**Response:** `List[CompetitorResponse]`

---

#### `GET /{channel_id}/{competitor_id}` - Get competitor detail

**Auth Required:** Yes

**Response:** `CompetitorResponse`

---

#### `DELETE /{channel_id}/{competitor_id}` - Remove competitor

**Auth Required:** Yes

**Response:** 204 No Content

---

## gaps.py

**File:** [`gaps.py`](backend/app/routers/gaps.py)

### Router: `/api/v1/gaps`

Content gap detection endpoints.

---

#### `POST /{channel_id}/detect` - Trigger gap detection

**Auth Required:** Yes

**Response:**
```python
{
    "message": "Gap detection queued"
}
```

**Background Process:**
- Analyzes user's videos vs competitor coverage
- Identifies 5-8 content opportunities
- Creates ContentGap records

**Duration:** 30-60 seconds

---

#### `GET /{channel_id}` - List content gaps

**Auth Required:** Yes

**Response:** `List[ContentGapResponse]`

**Sorting:** By opportunity_score descending

---

#### `POST /{channel_id}/gaps/{gap_id}/acted-on` - Mark gap as acted on

**Auth Required:** Yes

**Response:**
```python
{
    "message": "Gap marked as acted on"
}
```

---

## hooks.py

**File:** [`hooks.py`](backend/app/routers/hooks.py)

### Router: `/api/v1/hooks`

Hook generation and retrieval endpoints.

---

#### `POST /generate` - Generate hook variations

**Auth Required:** Yes

**Request Body:** `HookGenerateRequest`
```python
{
    "channel_id": "uuid",
    "topic": "How to start a YouTube channel",
    "count": 5  # default
}
```

**Response:** `List[HookResponse]` (201 Created)

**Saves:** Generated hooks are stored in database

---

#### `GET /` - List hooks

**Auth Required:** Yes

**Query Params:**
- `channel_id` (Optional[str]): Filter by channel

**Response:** `List[HookResponse]`

---

#### `GET /{hook_id}` - Get hook detail

**Auth Required:** Yes

**Response:** `HookResponse`

---

## scripts.py

**File:** [`scripts.py`](backend/app/routers/scripts.py)

### Router: `/api/v1/scripts`

Script generation endpoints.

---

#### `POST /generate` - Generate full script

**Auth Required:** Yes

**Request Body:** `ScriptCreateRequest`
```python
{
    "topic": "How to code in Python",
    "channel_id": "uuid",  # optional
    "target_duration_minutes": 10,  # default
    "format_type": "educational"  # educational|story|list|review
}
```

**Response:** `ScriptResponse` (201 Created)

**Generation Steps:**
1. Generate title suggestions (3 options)
2. Generate opening hook
3. Generate full script with provided hook

**Duration:** 15-30 seconds (blocking call)

---

#### `GET /` - List scripts

**Auth Required:** Yes

**Response:** `List[ScriptResponse]`

**Sorting:** Newest first

---

#### `GET /{script_id}` - Get script detail

**Auth Required:** Yes

**Response:** `ScriptResponse`

---

#### `DELETE /{script_id}` - Delete script

**Auth Required:** Yes

**Response:** 204 No Content

---

## audience.py

**File:** [`audience.py`](backend/app/routers/audience.py)

### Router: `/api/v1/audience`

Audience insights endpoints.

---

#### `GET /{channel_id}` - Get audience insights

**Auth Required:** Yes

**Response:** `AudienceInsightResponse`
```python
{
    "audience_type": "tech-savvy millennials",
    "audience_pain_points": [...],
    "content_themes": [...],
    "recommended_topics": [...]
}
```

---

## research.py

**File:** [`research.py`](backend/app/routers/research.py)

### Router: `/api/v1/research`

Deep research and web scraping endpoints.

**Prefix:** `/api/v1/research`

---

#### `POST /topic` - Research topic

**Auth Required:** No

**Request Body:**
```python
{
    "topic": "AI video editing",
    "niche": "technology",
    "depth": "standard"  # quick|standard|deep
}
```

**Response:**
```python
{
    "topic": "AI video editing",
    "niche": "technology",
    "scraped_data": {...},
    "ai_synthesis": "...",
    "status": "success"
}
```

---

#### `POST /competitor` - Research competitor

**Request Body:**
```python
{
    "competitor_name": "Tech Creator",
    "competitor_url": "https://...",  # optional
    "include_social": True
}
```

---

#### `POST /trends` - Aggregate trends

**Request Body:**
```python
{
    "niche": "technology",
    "time_range": "week",  # day|week|month
    "sources": ["reddit", "news"]  # optional
}
```

---

#### `POST /audience` - Research audience

**Request Body:**
```python
{
    "topic": "python tutorial",
    "include_forums": True,
    "include_reddit": True,
    "include_quora": True
}
```

---

#### `POST /deep-research` - Comprehensive research

**Request Body:**
```python
{
    "topic": "AI tools",
    "niche": "productivity",
    "sources_count": 10
}
```

---

#### `GET /sources` - List scraping sources

**Response:**
```python
{
    "sources": [
        {"name": "Reddit", "status": "active", "types": ["trends", "discussions"]},
        ...
    ],
    "firecrawl_active": True
}
```

---

## thumbnails.py

**File:** [`thumbnails.py`](backend/app/routers/thumbnails.py)

### Router: `/api/v1/thumbnails`

Thumbnail analysis endpoints.

---

#### `POST /analyze` - Analyze thumbnail (vision)

**Auth Required:** Yes

**Request Body:** `ThumbnailAnalyzeRequest`
```python
{
    "thumbnail_url": "https://i.ytimg.com/...",
    "video_title": "How to Code in Python"
}
```

**Response:** `ThumbnailAnalyzeResponse`

**Note:** Uses GPT-4o vision - higher cost

---

#### `POST /recommend` - Get thumbnail recommendation

**Auth Required:** Yes

**Request Body:** `ThumbnailRecommendRequest`
```python
{
    "topic": "Python tutorial",
    "title": "Learn Python in 30 Days",
    "channel_id": "uuid"
}
```

**Response:** `ThumbnailRecommendResponse`

---

## trends.py

**File:** [`trends.py`](backend/app/routers/trends.py)

### Router: `/api/v1/trends`

Trend listing endpoints.

---

#### `GET /` - List trends

**Auth Required:** Yes

**Query Params:**
- `niche` (Optional[str]): Filter by niche

**Response:** `List[TrendResponse]`

**Sorting:** By velocity_score descending

---

#### `GET /{trend_id}` - Get trend detail

**Auth Required:** Yes

**Response:** `TrendResponse`

---

## Authentication

All authenticated endpoints require:
```
Authorization: Bearer <jwt_token>
```

JWT tokens are obtained via `/api/v1/auth/login` or `/api/v1/auth/google/callback`.

## Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid JWT |
| 403 | Forbidden | User doesn't own resource |
| 404 | Not Found | Resource doesn't exist |
| 429 | Rate Limit Exceeded | Too many requests |
| 500 | Internal Error | Server error |
| 502 | Bad Gateway | External API failure |

## Rate Limits

| Endpoint Type | Limit |
|---------------|-------|
| Auth endpoints | 20/min |
| Read endpoints | 100/min |
| Write endpoints | 30/min |
| Script generation | 10/min |
| Heavy analysis | 5/min |

Rate limit headers included in responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After` (on 429)

## Response Format

### Success
```python
# Single item
{"id": "uuid", "name": "...", ...}

# List
[{"id": "uuid", ...}, ...]

# Paginated
{
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 50,
    "pages": 2
}
```

### Error
```python
{
    "detail": "Error message describing the issue"
}
```

---

## Testing

### Request Examples

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secret"

# Get channels
curl http://localhost:8000/api/v1/channels \
  -H "Authorization: Bearer $TOKEN"

# Connect channel
curl -X POST http://localhost:8000/api/v1/channels/connect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"youtube_channel_id": "UCxxxxxxx"}'
```

### Mocking Authentication

```python
from unittest.mock import patch
from app.utils.auth_utils import get_current_user
from app.models.user import User

def test_protected_endpoint():
    mock_user = User(id="test-uuid", email="test@example.com")
    
    with patch('app.routers.channels.get_current_user', return_value=mock_user):
        response = client.get("/channels/", headers={"Authorization": "Bearer test"})
        assert response.status_code == 200
```

---

## Dependencies

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.utils.auth_utils import get_current_user
from app.models.user import User
from app.database import get_db
from app.schemas.* import *