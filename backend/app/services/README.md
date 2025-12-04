# Services Module

This module contains all backend service integrations for the CreatorIQ platform. Services handle external API calls, caching, async operations, and AI model interactions.

## Overview

The services layer acts as an abstraction between the routers/controllers and external APIs. Each service is designed for:
- **Resilience**: Retry logic, circuit breakers, fallbacks
- **Cost Optimization**: Model routing, token tracking, budget management
- **Performance**: Connection pooling, caching, async operations
- **Observability**: Logging, token usage tracking

## File Structure

```
backend/app/services/
├── __init__.py              # Package marker
├── openrouter_service.py    # LLM API via OpenRouter
├── openai_service.py        # Direct OpenAI API (fallback/embeddings)
├── youtube_service.py       # YouTube Data API v3
├── scraper_service.py       # Firecrawl web scraping
├── redis_cache.py           # Redis caching layer
├── context_optimizer.py     # Token counting and text compression
├── token_budget.py          # Per-user token budget tracking
├── async_http.py           # Async HTTP client with pooling
├── embedding_service.py    # Content embedding utilities
└── whisper_service.py       # Audio transcription (placeholder)
```

---

## openrouter_service.py

**File:** [`openrouter_service.py`](backend/app/services/openrouter_service.py)

### Overview

Unified LLM API service via [OpenRouter.ai](https://openrouter.ai). OpenRouter provides access to multiple LLM providers (OpenAI, Anthropic, Meta, Google, etc.) through a single API with unified pricing.

### Configuration

```python
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
```

### Model Costs (per million tokens)

| Model | Input Cost | Output Cost |
|-------|-----------|-------------|
| `openai/gpt-4o-mini` | $0.15 | $0.60 |
| `openai/gpt-4o` | $2.50 | $10.00 |
| `anthropic/claude-3-haiku` | $0.25 | $1.25 |
| `anthropic/claude-3-sonnet` | $3.00 | $15.00 |
| `meta-llama/llama-3-8b-instruct` | $0.20 | $0.20 |
| `mistralai/mixtral-8x7b` | $0.24 | $0.24 |
| `google/gemini-pro` | $0.25 | $1.00 |

### Default Models

```python
DEFAULT_LLM_MODEL = "openai/gpt-4o-mini"
DEFAULT_VISION_MODEL = "anthropic/claude-3-haiku"
DEFAULT_EMBEDDING_MODEL = "openai/gpt-4o-mini"
```

### Functions

#### `call_openai(system_prompt, user_prompt, model=None, max_tokens=2000, response_format=None, complexity=None, user_id=None, operation='unknown') -> str`

Central OpenRouter API call with retry logic.

**Parameters:**
- `system_prompt` (str): System instructions for the AI
- `user_prompt` (str): User query/prompt
- `model` (str, optional): OpenRouter model ID (e.g., "openai/gpt-4o-mini"). Auto-selected based on complexity if not provided.
- `max_tokens` (int, default=2000): Maximum response length
- `response_format` (str, optional): Set to `"json"` for JSON object responses
- `complexity` (str, optional): Model selection hint - `"ultra_cheap"`, `"simple"`, `"medium"`, `"complex"`
- `user_id` (str, optional): User ID for token tracking
- `operation` (str, default="unknown"): Operation name for logging

**Returns:**
- `str`: The AI response text

**Complexity Routing:**
- `"ultra_cheap"`: Uses `meta-llama/llama-3-8b-instruct` for simple extractions
- `"simple"`: Uses `openai/gpt-4o-mini` for basic transformations
- `"medium"`: Uses `DEFAULT_LLM_MODEL`
- `"complex"`: Uses `openai/gpt-4o` for nuanced analysis

**Retry Logic:**
- Retries up to 3 times with exponential backoff (4-10 second delays)

**Example:**
```python
from app.services.openrouter_service import call_openai

response = call_openai(
    system_prompt="You are a YouTube expert.",
    user_prompt="Analyze this title: 'How to Code in Python'",
    complexity="simple",
    user_id=user.id,
    operation="title_analysis"
)
```

---

#### `call_openai_vision(image_url, prompt, model=None) -> str`

Vision-capable LLM call for image analysis (thumbnail analysis, screenshot reading).

**Parameters:**
- `image_url` (str): URL or base64 data URI of the image
- `prompt` (str): Question/instruction about the image
- `model` (str, optional): Vision-capable model. Defaults to `DEFAULT_VISION_MODEL`

**Returns:**
- `str`: AI's analysis of the image

**Example:**
```python
analysis = call_openai_vision(
    image_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    prompt="Rate this thumbnail 1-10 for click-through potential. Explain why."
)
```

---

#### `call_openai_streaming(system_prompt, user_prompt, model=None, max_tokens=2000, callback=None) -> str`

Streaming LLM call for real-time response generation (progress indicators, live updates).

**Parameters:**
- `system_prompt` (str): System instructions
- `user_prompt` (str): User query
- `model` (str, optional): Model ID
- `max_tokens` (int, default=2000): Maximum response length
- `callback` (callable, optional): Function called with each content chunk

**Returns:**
- `str`: Complete response text

**Example:**
```python
def on_chunk(content):
    print(content, end='', flush=True)

full_response = call_openai_streaming(
    system_prompt="Continue the story.",
    user_prompt="Once upon a time...",
    callback=on_chunk
)
```

---

#### `get_embedding(text, model=None) -> list`

Generate text embedding for similarity search.

**Parameters:**
- `text` (str): Text to embed (max ~8000 chars due to token limits)
- `model` (str, optional): Embedding model. Defaults to `DEFAULT_EMBEDDING_MODEL`

**Returns:**
- `list`: 1536-dimensional embedding vector (or model's native dimension)

**Note:** OpenRouter has limited embedding support. Falls back to direct OpenAI API.

---

#### `safe_json_loads(response_text) -> Dict[str, Any]`

Safely parse JSON from AI response with common fixes.

**Parameters:**
- `response_text` (str): Raw response text

**Returns:**
- `Dict[str, Any]`: Parsed JSON or empty dict on failure

**Fixes Applied:**
- Removes markdown code blocks (\`\`\`json, \`\`\`)
- Strips whitespace
- Returns `{}` if parsing fails

---

#### `get_model_info(model) -> Dict[str, Any]`

Get information about a model including estimated costs.

**Parameters:**
- `model` (str): Model identifier

**Returns:**
```python
{
    "model": "openai/gpt-4o-mini",
    "estimated_cost_per_1m_tokens": {
        "input": 0.15,
        "output": 0.60
    }
}
```

---

#### `get_cost_estimate(model, input_tokens, output_tokens) -> float`

Calculate estimated cost for a model and token counts.

**Parameters:**
- `model` (str): Model identifier
- `input_tokens` (int): Number of input tokens
- `output_tokens` (int): Number of output tokens

**Returns:**
- `float`: Estimated cost in USD

---

## openai_service.py

**File:** [`openai_service.py`](backend/app/services/openai_service.py)

### Overview

Direct OpenAI API access. Used as fallback for embeddings and when OpenRouter is unavailable. Primarily uses `gpt-4o-mini` for cost efficiency.

### Functions

#### `call_openai(system_prompt, user_prompt, model='gpt-4o-mini', max_tokens=2000, response_format=None) -> str`

Standard OpenAI chat completion.

**Parameters:**
- `system_prompt` (str): System instructions
- `user_prompt` (str): User query
- `model` (str, default="gpt-4o-mini"): OpenAI model ID
- `max_tokens` (int, default=2000): Max response tokens
- `response_format` (str, optional): Set to `"json"` for JSON mode

**Returns:**
- `str`: AI response

---

#### `call_openai_vision(image_url, prompt, model='gpt-4o') -> str`

Vision call using GPT-4o. Required for thumbnail analysis quality.

**Parameters:**
- `image_url` (str): Image URL
- `prompt` (str): Analysis prompt
- `model` (str, default="gpt-4o"): Vision model

**Returns:**
- `str`: Analysis result

---

#### `get_embedding(text) -> list`

Generate text embedding using `text-embedding-3-small`.

**Parameters:**
- `text` (str): Text to embed (truncated to 8000 chars)

**Returns:**
- `list`: 1536-dim embedding vector

---

## youtube_service.py

**File:** [`youtube_service.py`](backend/app/services/youtube_service.py)

### Overview

YouTube Data API v3 integration for fetching channel/video data, transcripts, and comments.

### Dependencies

```python
googleapiclient.discovery import build
google.oauth2.credentials import Credentials
youtube_transcript_api import YouTubeTranscriptApi
```

### Functions

#### `get_youtube_client(access_token=None) -> Resource`

Get YouTube API client.

**Parameters:**
- `access_token` (str, optional): OAuth access token for authenticated requests

**Returns:**
- `Resource`: YouTube API client

**Note:**
- With `access_token`: Uses OAuth (for user's own channel private data)
- Without `access_token`: Uses API key (public data only)

---

#### `fetch_channel_details(channel_id) -> Dict[str, Any]`

Fetch channel metadata and statistics.

**API Reference:** [channels.list](https://developers.google.com/youtube/v3/docs/channels/list)

**Parameters:**
- `channel_id` (str): YouTube channel ID (UCxxxxxxx format)

**Returns:**
```python
{
    "youtube_channel_id": "UCxxxxxxx",
    "title": "Channel Title",
    "description": "Channel description...",
    "thumbnail_url": "https://i.ytimg.com/...",
    "subscriber_count": 100000,
    "video_count": 500,
    "view_count": 10000000,
    "country": "US",
    "uploads_playlist_id": "UUxxxxxxx"  # For fetching uploads
}
```

**Quota Cost:** 1 unit

---

#### `fetch_channel_videos(uploads_playlist_id, max_results=50) -> List[Dict]`

Fetch video IDs from a channel's uploads playlist.

**API Reference:** [playlistItems.list](https://developers.google.com/youtube/v3/docs/playlistItems/list)

**Parameters:**
- `uploads_playlist_id` (str): Playlist ID from `fetch_channel_details`
- `max_results` (int, default=50): Maximum videos to fetch

**Returns:**
```python
[
    {
        "youtube_video_id": "dQw4w9WgXcQ",
        "title": "Video Title",
        "published_at": "2024-01-15T10:30:00Z",
        "thumbnail_url": "https://i.ytimg.com/..."
    },
    ...
]
```

**Quota Cost:** 1 unit per page (50 results)

---

#### `fetch_video_statistics(video_ids) -> List[Dict]`

Fetch detailed stats for up to 50 videos.

**API Reference:** [videos.list](https://developers.google.com/youtube/v3/docs/videos/list)

**Parameters:**
- `video_ids` (List[str]): List of YouTube video IDs (max 50 per batch)

**Returns:**
```python
[
    {
        "youtube_video_id": "dQw4w9WgXcQ",
        "title": "Video Title",
        "description": "...",
        "tags": ["tag1", "tag2"],
        "category_id": "22",
        "published_at": "2024-01-15T10:30:00Z",
        "thumbnail_url": "...",
        "view_count": 100000,
        "like_count": 5000,
        "comment_count": 500,
        "duration_seconds": 3723
    },
    ...
]
```

**Quota Cost:** 1 unit per 50 videos

---

#### `fetch_video_comments(video_id, max_results=100) -> List[str]`

Fetch top-level comment texts for audience analysis.

**API Reference:** [commentThreads.list](https://developers.google.com/youtube/v3/docs/commentThreads/list)

**Parameters:**
- `video_id` (str): YouTube video ID
- `max_results` (int, default=100): Max comments

**Returns:**
- `List[str]`: Comment texts

**Quota Cost:** 1 unit per page

**Note:** Returns empty list if comments disabled. Logs warning on failure.

---

#### `fetch_transcript(video_id) -> Optional[str]`

Fetch auto-generated or manual transcript.

**Parameters:**
- `video_id` (str): YouTube video ID

**Returns:**
- `str`: Full transcript text, or `None` if unavailable

**Note:** Uses `youtube-transcript-api` library. Falls back gracefully if transcript unavailable.

---

#### `search_competitor_channels(niche, max_results=10) -> List[Dict]`

Search for competitor channels by niche keyword.

**API Reference:** [search.list](https://developers.google.com/youtube/v3/docs/search/list)

**Parameters:**
- `niche` (str): Search keyword
- `max_results` (int, default=10): Max results

**Returns:**
```python
[
    {
        "youtube_channel_id": "UCyyyyyyy",
        "title": "Competitor Channel",
        "description": "..."
    },
    ...
]
```

**Quota Cost:** 100 units per request — **use sparingly**

---

### Rate Limits

| Endpoint | Quota Cost | Notes |
|----------|-----------|-------|
| channels.list | 1 | Per channel |
| playlistItems.list | 1 | Per 50 items |
| videos.list | 1 | Per 50 videos |
| commentThreads.list | 1 | Per page |
| search.list | 100 | **Expensive** - cache results |

**Default quota:** 10,000 units/day. Monitor at [Google Cloud Console](https://console.cloud.google.com).

---

## scraper_service.py

**File:** [`scraper_service.py`](backend/app/services/scraper_service.py)

### Overview

Advanced web scraping service using Firecrawl for intelligent crawling. Falls back to basic httpx scraping when Firecrawl is unavailable.

### Dependencies

```python
firecrawl import FirecrawlClient  # Optional
httpx                           # Fallback
```

### Configuration

```python
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")  # Optional
timeout = 30  # Max 30 seconds per scrape
max_results = 10
```

### Class: `ScraperService`

#### Constructor: `__init__()`

Initializes Firecrawl client if API key is available.

**Fallback Behavior:**
- Without `FIRECRAWL_API_KEY`: Uses `httpx.AsyncClient` for basic HTML fetching
- Firecrawl provides better JS rendering and structured output

---

#### `async scrape_channel_research(channel_url) -> dict`

Scrape competitor's website, social profiles, and public content.

**Parameters:**
- `channel_url` (str): URL to scrape

**Returns:**
```python
{
    "url": "https://example.com",
    "scraped_at": "2024-01-15T10:30:00Z",
    "content": {
        "markdown": "...",
        "metadata": {...}
    },
    "success": True,
    "sources_used": ["https://example.com"]
}
```

---

#### `async scrape_trend_aggregator(topic) -> list`

Scrape multiple sources for trend data (Reddit, news).

**Sources:**
- Reddit search results
- Google News

**Parameters:**
- `topic` (str): Trend topic

**Returns:**
```python
[
    {
        "source": "https://www.reddit.com/search.json?q=...",
        "content": "...",
        "scraped_at": "2024-01-15T10:30:00Z"
    },
    ...
]
```

---

#### `async scrape_content_ideas(niche) -> list`

Scrape for content inspiration.

**Sources:**
- Wikipedia search
- Reddit forums

**Returns:**
```python
[
    {
        "source": "https://en.wikipedia.org/wiki/...",
        "content": "...",
        "type": "content_idea",
        "scraped_at": "2024-01-15T10:30:00Z"
    },
    ...
]
```

---

#### `async scrape_audience_discourse(topic) -> dict`

Scrape Q&A sites, forums for audience questions.

**Sources:**
- Quora
- Reddit

**Returns:**
```python
{
    "topic": "python tutorial",
    "questions": [],
    "pain_points": [],
    "discussions": [
        {
            "source": "https://www.quora.com/...",
            "content": "...",
            "scraped_at": "2024-01-15T10:30:00Z"
        }
    ],
    "scraped_at": "2024-01-15T10:30:00Z"
}
```

---

#### `async scrape_seo_data(keyword) -> dict`

Scrape SERP features, top results for keyword.

**Returns:**
```python
{
    "keyword": "python tutorial",
    "serp_features": [],
    "top_results": [
        {
            "source": "https://www.google.com/search?q=...",
            "content": "...",
            "scraped_at": "2024-01-15T10:30:00Z"
        }
    ],
    "related_keywords": [],
    "scraped_at": "2024-01-15T10:30:00Z"
}
```

---

#### `async multi_source_research(topic, niche) -> dict`

Aggregate data from multiple sources concurrently.

**Parameters:**
- `topic` (str): Research topic
- `niche` (str): Content niche

**Returns:**
```python
{
    "topic": "...",
    "niche": "...",
    "sources": [...],
    "insights": {},
    "scraped_at": "2024-01-15T10:30:00Z",
    "success": True
}
```

**Note:** Uses `asyncio.gather` for concurrent scraping.

---

## redis_cache.py

**File:** [`redis_cache.py`](backend/app/services/redis_cache.py)

### Overview

Async Redis caching layer with connection pooling, TTL support, and cache invalidation helpers.

### Dependencies

```python
redis.asyncio import Redis
```

### Class: `RedisCache`

Singleton async Redis client.

#### `async initialize()`

Initialize Redis connection pool.

**Connection Settings:**
```python
max_connections=50
socket_timeout=5
socket_connect_timeout=5
retry_on_timeout=True
```

---

#### `async close()`

Close Redis connection.

---

#### `async get(key) -> Optional[Any]`

Get value from cache.

**Parameters:**
- `key` (str): Cache key

**Returns:**
- Cached value (auto-deserialized from JSON) or `None`

---

#### `async set(key, value, ttl=3600, nx=False) -> bool`

Set value in cache with TTL.

**Parameters:**
- `key` (str): Cache key
- `value` (Any): Value to cache (auto-serialized to JSON)
- `ttl` (int, default=3600): Time-to-live in seconds
- `nx` (bool, default=False): Only set if key doesn't exist (`SETNX`)

**Returns:**
- `bool`: True if successful

---

#### `async delete(key) -> bool`

Delete key from cache.

---

#### `async delete_pattern(pattern) -> int`

Delete all keys matching pattern.

**Parameters:**
- `pattern` (str): Redis pattern with wildcards (e.g., `"channel:*"`)

**Returns:**
- `int`: Number of keys deleted

---

#### `async exists(key) -> bool`

Check if key exists.

---

#### `async increment(key, amount=1) -> Optional[int]`

Increment counter atomically.

---

### Class: `CacheKeys`

Cache key prefix constants.

```python
CHANNEL = "channel"
COMPETITOR = "competitor"
VIDEO = "video"
TRENDS = "trends"
SCRIPT = "script"
HOOK = "hook"
GAP = "gap"
AUDIENCE = "audience"
YOUTUBE_STATS = "yt:stats"
YOUTUBE_CHANNEL = "yt:channel"
```

---

### Class: `CacheInvalidator`

Cache invalidation helpers.

#### `static async invalidate_channel(channel_id)`

Invalidate all cache entries for a channel.

**Patterns Deleted:**
- `channel:{channel_id}*`
- `video:channel:{channel_id}*`
- `competitor:channel:{channel_id}*`

---

#### `static async invalidate_user(user_id)`

Invalidate all cache entries for a user.

**Patterns Deleted:**
- `channel:user:{user_id}*`
- `script:user:{user_id}*`

---

#### `static async invalidate_youtube_data(channel_id)`

Invalidate YouTube API cached data.

**Patterns Deleted:**
- `yt:stats:{channel_id}*`
- `yt:channel:{channel_id}*`

---

### Cache Key Generation

Keys are generated using MD5 hash of arguments:

```python
def _generate_key(prefix, *args, **kwargs) -> str:
    key_data = f"{prefix}:{args}:{json.dumps(kwargs, sort_keys=True)}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()[:16]
    return f"{prefix}:{key_hash}"
```

**Example:**
```
Input:  prefix="video", channel_id="abc123"
Output: "video:a1b2c3d4e5f6g7h8"
```

---

## context_optimizer.py

**File:** [`context_optimizer.py`](backend/app/services/context_optimizer.py)

### Overview

Token counting, text truncation, summarization, and compression for AI context optimization. Reduces costs while preserving insight quality.

### Dependencies

```python
tiktoken  # Token counting
```

### Constants

```python
ENCODING = tiktoken.get_encoding("cl100k_base")  # GPT-4/Claude encoding
DEFAULT_MAX_INPUT_TOKENS = 4000
TARGET_AVG_INPUT_TOKENS = 500
MAX_TRANSCRIPT_CHARS = 10000
```

---

### Functions

#### `count_tokens(text) -> int`

Count tokens using tiktoken.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `int`: Token count (falls back to `len(text)//4` on error)

---

#### `truncate_to_token_limit(text, max_tokens=4000) -> str`

Hard truncate text to fit token limit.

**Parameters:**
- `text` (str): Input text
- `max_tokens` (int, default=4000): Maximum tokens

**Returns:**
- `str`: Truncated text

**Note:** Uses binary search for efficient exact-limit truncation.

---

#### `summarize_text(text, max_tokens=150) -> str`

AI-powered summarization for long content.

**Parameters:**
- `text` (str): Long text to summarize
- `max_tokens` (int, default=150): Target output tokens

**Returns:**
- `str`: 2-3 sentence summary

**Note:** Falls back to hard truncate if AI call fails.

---

#### `extract_key_points(text, num_points=5) -> List[str]`

Extract N key points using AI.

**Parameters:**
- `text` (str): Input text
- `num_points` (int, default=5): Number of points

**Returns:**
- `List[str]`: List of extracted key points

**Output Format:**
```json
["Point 1 about...",
 "Point 2 about...",
 "Point 3 about..."]
```

---

#### `compress_video_context(video_data, include_transcript=True) -> str`

Compress single video data for AI analysis.

**Parameters:**
- `video_data` (dict): Video details
- `include_transcript` (bool, default=True): Include transcript excerpt

**Returns:**
```
"Title | Views: 100,000 | Likes: 5,000 | Duration: 10min
Transcript: First 500 chars..."
```

---

#### `compress_videos_for_analysis(videos, max_videos=5) -> str`

Compress multiple videos into single context.

**Parameters:**
- `videos` (List[dict]): List of video data
- `max_videos` (int, default=5): Max videos to include

**Returns:**
```
"Title1 | Views: X | Likes: X | Duration: Xmin
Title2 | Views: X | Likes: X | Duration: Xmin
..."
```

---

#### `optimize_transcript_for_ai(transcript, max_chars=10000) -> str`

Optimize transcript for AI consumption.

**Operations:**
- Remove excessive whitespace
- Truncate to max_chars

---

#### `get_token_budget_status(used_tokens, limit_tokens) -> dict`

Get budget status with recommendations.

**Returns:**
```python
{
    "used": 1500000,
    "limit": 2000000,
    "percentage": 75.0,
    "remaining": 500000,
    "status": "warning",  # "ok" | "warning" | "critical"
    "recommendation": "Consider reducing context size"
}
```

---

## token_budget.py

**File:** [`token_budget.py`](backend/app/services/token_budget.py)

### Overview

Per-user token budget tracking based on subscription plan. Enforces limits and provides usage monitoring.

### Token Limits Per Plan (Monthly)

```python
TOKEN_LIMITS = {
    "free": 100_000,
    "starter": 500_000,
    "pro": 2_000_000,
    "enterprise": 10_000_000
}
```

### Alert Thresholds

```python
WARNING_THRESHOLD = 0.70  # 70%
CRITICAL_THRESHOLD = 0.90  # 90%
```

---

### Class: `TokenBudgetManager`

#### `classmethod get_user_plan(user_id, db) -> str`

Get user's subscription plan from database.

---

#### `classmethod get_token_limit(plan) -> int`

Get token limit for plan.

---

#### `classmethod track_tokens(user_id, input_tokens, output_tokens=0)`

Track token usage after AI API call.

**Note:** Updates in-memory cache. In production, periodically persists to database.

---

#### `classmethod get_usage(user_id, plan, period_type='monthly') -> dict`

Get current usage stats.

**Returns:**
```python
{
    "user_id": "...",
    "plan": "pro",
    "period_type": "monthly",
    "tokens_used": 1500000,
    "token_limit": 2000000,
    "percentage": 75.0,
    "remaining": 500000,
    "requests_count": 150,
    "status": "warning",
    "can_proceed": True
}
```

---

#### `classmethod check_budget(user_id, plan, estimated_tokens) -> bool`

Check if user has sufficient budget.

---

### Convenience Functions

```python
track_usage(user_id, input_tokens, output_tokens)
get_user_budget_status(user_id, plan)
can_use_tokens(user_id, plan, estimated_tokens)
```

---

## async_http.py

**File:** [`async_http.py`](backend/app/services/async_http.py)

### Overview

Async HTTP client with connection pooling for non-blocking I/O operations. Used for concurrent external API calls.

### Dependencies

```python
httpx  # Async HTTP client
```

---

### Class: `AsyncHTTPClient`

Singleton async HTTP client.

#### `async initialize()`

Initialize with connection pooling.

**Pool Settings:**
```python
max_keepalive_connections=20
max_connections=50
keepalive_expiry=30.0
timeout=httpx.Timeout(
    connect=10.0,
    read=30.0,
    write=30.0,
    pool=30.0
)
```

---

#### `async get(url, params=None, headers=None, timeout=None) -> httpx.Response`

Async GET request.

---

#### `async post(url, json=None, data=None, headers=None, timeout=None) -> httpx.Response`

Async POST request.

---

#### `async batch_get(urls, max_concurrent=5, timeout=None) -> List[httpx.Response]`

Batch GET with concurrency limit.

**Parameters:**
- `urls` (List[str]): URLs to fetch
- `max_concurrent` (int, default=5): Max concurrent requests
- `timeout` (float, optional): Request timeout

**Returns:**
- `List[httpx.Response]`: Responses in same order as URLs (None for failures)

---

### Class: `YouTubeAPIClient`

Async wrapper for YouTube API (sync library, run in executor).

#### `async fetch_channel_details_async(channel_id) -> dict`

Fetch channel details asynchronously.

---

#### `async fetch_videos_parallel(uploads_playlist_id, max_results=50) -> List[dict]`

Fetch channel videos with parallel statistics fetching.

**Process:**
1. Fetch video IDs from uploads playlist
2. Fetch statistics in parallel batches (3 at a time)

**Quota Consideration:** Fetches 50 videos at a time for statistics.

---

## embedding_service.py

**File:** [`embedding_service.py`](backend/app/services/embedding_service.py)

### Overview

Content embedding utilities for similarity search.

---

### Functions

#### `get_content_embedding(text) -> List[float]`

Generate embedding for content similarity.

**Returns:**
- `List[float]`: 1536-dim embedding (zero vector fallback on failure)

---

#### `compute_similarity(embedding1, embedding2) -> float`

Compute cosine similarity between two embeddings.

---

#### `find_similar_content(query_embedding, content_embeddings, threshold=0.7) -> List[int]`

Find indices of content with similarity above threshold.

---

## whisper_service.py

**File:** [`whisper_service.py`](backend/app/services/whisper_service.py)

### Overview

Placeholder for OpenAI Whisper API transcription. Currently using `youtube-transcript-api` which is free and covers most videos.

### Function: `async transcribe_audio(audio_url, language=None) -> str`

**Status:** `NotImplementedError`

**Note:** Use `youtube_transcript_api` instead for transcript extraction.

---

## Configuration Requirements

### Environment Variables

```bash
# OpenRouter (LLM API)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_SITE_URL=https://creatoriq.app
OPENROUTER_SITE_NAME=CreatorIQ

# OpenAI (Embeddings fallback)
OPENAI_API_KEY=sk-...

# YouTube API
YOUTUBE_API_KEY=AIza...

# Redis
REDIS_URL=redis://localhost:6379/0

# Firecrawl (Optional)
FIRECRAWL_API_KEY=fc-...
```

### External Service Requirements

| Service | Required | Purpose |
|---------|----------|---------|
| OpenRouter | Yes | LLM API access |
| OpenAI | Yes | Embeddings |
| YouTube API | Yes | Channel/video data |
| Redis | Yes | Caching |
| Firecrawl | No | Web scraping |
| pgvector | Yes | Vector storage |

---

## Error Handling

### Retry Logic

Most services use Tenacity for retry with exponential backoff:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai(...):
    ...
```

### Circuit Breaker Pattern

See [`app/utils/resilience.py`](backend/app/utils/resilience.py) for circuit breaker implementation.

### Graceful Degradation

- **Scraper Service**: Falls back to basic httpx if Firecrawl unavailable
- **Embeddings**: Falls back to direct OpenAI if OpenRouter fails
- **Redis**: Returns `None` on cache failures, continues without cache
- **YouTube**: Returns empty results on API failures

---

## Testing Notes

### Mocking External APIs

```python
from unittest.mock import patch

# Mock OpenRouter
with patch('app.services.openrouter_service.client.chat.completions.create') as mock:
    mock.return_value.choices[0].message.content = '{"result": "test"}'
    result = call_openai("system", "user")
    assert result == '{"result": "test"}'

# Mock YouTube API
with patch('app.services.youtube_service.build') as mock:
    mock.return_value.channels().list().execute.return_value = {...}
    channel = fetch_channel_details("UCxxxxxxx")
```

### Integration Testing

For Redis-dependent tests:
```python
@pytest.fixture
async def redis_cache():
    cache = RedisCache()
    await cache.initialize()
    yield cache
    await cache.close()
```

---

## Dependencies Summary

| File | Key Dependencies |
|------|-----------------|
| `openrouter_service.py` | `openai` (OpenRouter client), `tenacity` |
| `openai_service.py` | `openai`, `tenacity` |
| `youtube_service.py` | `googleapiclient`, `youtube_transcript_api` |
| `scraper_service.py` | `firecrawl`, `httpx`, `asyncio` |
| `redis_cache.py` | `redis.asyncio` |
| `context_optimizer.py` | `tiktoken` |
| `token_budget.py` | None (in-memory) |
| `async_http.py` | `httpx`, `asyncio` |
| `embedding_service.py` | `openrouter_service` |
| `whisper_service.py` | Placeholder |