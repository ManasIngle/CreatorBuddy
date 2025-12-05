# Intelligence Module

This module contains AI-powered analysis engines for the CreatorIQ platform. Each engine specializes in a specific aspect of YouTube creator intelligence.

## Overview

The intelligence layer uses large language models (via OpenRouter) to analyze YouTube data and generate actionable insights. Engines are designed to:
- **Minimize API costs** through context optimization
- **Provide fallback data** when AI calls fail
- **Support enhanced modes** with web scraping for deeper analysis
- **Track token usage** for budget management

## File Structure

```
backend/app/intelligence/
├── __init__.py              # Package marker
├── creator_analyzer.py      # Creator profile building
├── competitor_engine.py     # Competitor analysis pipeline
├── gap_detector.py          # Content gap detection
├── script_generator.py      # Script generation
├── hook_engine.py           # Hook patterns and generation
├── thumbnail_engine.py      # Vision-based thumbnail analysis
├── audience_engine.py       # Audience psychology analysis
├── trend_engine.py          # Real-time trend detection
├── retention_engine.py      # Retention analysis
└── viral_engine.py          # Viral pattern detection
```

---

## creator_analyzer.py

**File:** [`creator_analyzer.py`](backend/app/intelligence/creator_analyzer.py)

### Class: `CreatorAnalyzer`

Builds comprehensive creator profiles from YouTube channel data.

---

#### `analyze_creator(channel_title, top_video_data, subscriber_count) -> Dict`

Analyzes a creator's channel and builds a profile with niche, audience, and content insights.

**Parameters:**
- `channel_title` (str): Name of the YouTube channel
- `top_video_data` (List[Dict]): List of video dicts with keys: `title`, `views`, `transcript_excerpt`
- `subscriber_count` (int): Number of subscribers

**Returns:**
```python
{
    "niche": "technology",
    "niche_tags": ["tech", "programming", "tutorials"],
    "audience_type": "tech enthusiasts, ages 18-35",
    "personality_summary": "Educational but casual presenter...",
    "speaking_style": "conversational, fast-paced",
    "storytelling_structure": "problem-solution",
    "content_themes": ["productivity", "coding", "reviews"],
    "audience_pain_points": ["time management", "tool overwhelm"],
    "creator_strength": "Clear explanations of complex topics",
    "growth_opportunity": "More long-form deep dives"
}
```

**Context Optimization:**
- Uses top 5 videos only
- Transcript included only if < 500 chars
- Total context truncated to 2000 tokens

**Prompt Used:** [`creator_prompts.CREATOR_PROFILE_PROMPT`](backend/app/prompts/creator_prompts.py)

---

## competitor_engine.py

**File:** [`competitor_engine.py`](backend/app/intelligence/competitor_engine.py)

### Class: `CompetitorEngine`

Analyzes competitor channels for actionable intelligence.

---

#### `analyze_competitor(competitor_youtube_id, creator_niche, db) -> Dict[str, Any]`

Full competitor analysis with YouTube API data.

**Parameters:**
- `competitor_youtube_id` (str): Competitor's YouTube channel ID
- `creator_niche` (str): User's channel niche for comparison
- `db` (Session): Database session

**Returns:**
```python
{
    "youtube_channel_id": "UCyyyyyyy",
    "title": "Competitor Channel",
    "description": "...",
    "thumbnail_url": "...",
    "subscriber_count": 500000,
    "video_count": 300,
    "view_count": 50000000,
    "country": "US",
    "uploads_playlist_id": "UUyyyyyyy",
    "avg_views": 166666.67,
    "why_they_succeed": "Consistent upload schedule, strong personal brand",
    "best_formats": ["tutorial", "review"],
    "emotional_triggers_used": ["curiosity", "excitement"],
    "content_gaps": ["beginner content", "short tutorials"],
    "hook_patterns": ["question hooks", "shock value"],
    "thumbnail_style": "Bold text, face close-up, bright colors"
}
```

**Process:**
1. Fetch channel details via YouTube API
2. Fetch top 20 videos, get top 10 by views
3. Compress to top 5 for AI analysis
4. Return combined data with AI insights

---

#### `async enhanced_competitor_analysis(competitor_youtube_id, creator_niche, db, include_web_scrape=True) -> Dict[str, Any]`

Enhanced analysis with web scraping for comprehensive intelligence.

**Parameters:**
- `competitor_youtube_id` (str): Competitor's channel ID
- `creator_niche` (str): User's niche for context
- `db` (Session): Database session
- `include_web_scrape` (bool, default=True): Enable web scraping

**Additional Scraped Data:**
- Website content (if custom_url available)
- Social mentions and testimonials
- SEO data
- AI-synthesized insights on brand voice, content themes

**Returns:** Base analysis plus:
```python
{
    "web_scraped_intelligence": {...},
    "brand_voice": "Professional but approachable",
    "content_themes": [...],
    "engagement_strategies": [...],
    "collaboration_patterns": [...],
    "monetization_approaches": [...],
    "scrape_timestamp": "2024-01-15T10:30:00Z"
}
```

---

## gap_detector.py

**File:** [`gap_detector.py`](backend/app/intelligence/gap_detector.py)

### Class: `GapDetector`

Identifies content opportunities by analyzing what competitors cover vs. what's missing.

---

#### `detect_gaps(channel, db) -> List[Dict]`

Detects content gaps based on existing videos and competitor coverage.

**Parameters:**
- `channel` (Channel): User's channel model instance
- `db` (Session): Database session

**Returns:**
```python
[
    {
        "topic": "AI video editing tools comparison",
        "reason": "High demand but low competition",
        "opportunity_score": 8.5,
        "competition_level": "low",
        "suggested_angle": "Practical workflow showcase"
    },
    ...
]
```

**Analysis Method:**
1. Gets user's top 20 video titles (limit 15)
2. Gets top 3 videos from top 5 competitors
3. AI identifies topics user hasn't covered that competitors do
4. Truncates prompt to 1500 tokens for cost efficiency

**Prompt Used:** [`gap_prompts.GAP_DETECTION_PROMPT`](backend/app/prompts/gap_prompts.py)

---

#### `async enhanced_gap_detection(channel, db, include_web_scrape=True) -> Dict`

Enhanced gap detection with web scraping for broader opportunity discovery.

**Parameters:**
- `channel` (Channel): User's channel
- `db` (Session): Database session
- `include_web_scrape` (bool, default=True): Enable web scraping

**Web Sources Scraped:**
- Reddit for unanswered questions
- Quora for audience discourse
- Forums for common discussions
- Wikipedia for related topics

**Returns:**
```python
{
    "base_gaps": [...],      # From YouTube analysis
    "scraped_gaps": [...],   # From web scraping
    "web_insights": {
        "reddit_gaps": [...],
        "quora_gaps": [...],
        "forum_gaps": [...],
        "content_ideas": [...]
    },
    "total_opportunities": 15
}
```

---

## script_generator.py

**File:** [`script_generator.py`](backend/app/intelligence/script_generator.py)

### Class: `ScriptGenerator`

Generates video scripts with hooks, outlines, and full scripts.

---

#### `generate_titles(topic, channel) -> List[Dict]`

Generates 3 title suggestions optimized for CTR.

**Parameters:**
- `topic` (str): Video topic
- `channel` (Channel): User's channel for style context

**Returns:**
```python
[
    {"title": "The Ultimate Guide to X", "type": "definitive"},
    {"title": "X Mistakes You Must Avoid", "type": "problem-avoidance"},
    {"title": "How I Mastered X in 30 Days", "type": "transformation"}
]
```

**Prompt Used:** [`script_prompts.TITLE_SUGGESTIONS_PROMPT`](backend/app/prompts/script_prompts.py)

---

#### `generate_hook(topic, channel, title) -> str`

Generates an opening hook (first 30 seconds) for a video.

**Parameters:**
- `topic` (str): Video topic
- `channel` (Channel): User's channel for style context
- `title` (str): Selected video title

**Returns:**
- `str`: Hook text (~100-200 words)

**Prompt Used:** [`script_prompts.SCRIPT_HOOK_PROMPT`](backend/app/prompts/script_prompts.py)

---

#### `generate_full_script(topic, title, hook, channel, target_duration_minutes=10, format_type='educational') -> Dict[str, str]`

Generates a complete video script.

**Parameters:**
- `topic` (str): Video topic
- `title` (str): Video title
- `hook` (str): Opening hook text
- `channel` (Channel): User's channel for style context
- `target_duration_minutes` (int, default=10): Target video length
- `format_type` (str, default="educational"): Format: `educational`, `story`, `list`, `review`

**Returns:**
```python
{
    "full_script": "Full script text with timestamps...",
    "estimated_duration": "10 minutes"
}
```

**Note:** Uses `max_tokens=4000` for full script generation.

**Prompt Used:** [`script_prompts.FULL_SCRIPT_PROMPT`](backend/app/prompts/script_prompts.py)

---

## hook_engine.py

**File:** [`hook_engine.py`](backend/app/intelligence/hook_engine.py)

### Class: `HookEngine`

Analyzes viral hooks and generates new hook variations.

---

#### `analyze_viral_hooks(channel, db) -> List[Dict]`

Analyzes a channel's viral videos to extract hook patterns.

**Parameters:**
- `channel` (Channel): User's channel
- `db` (Session): Database session

**Returns:**
```python
[
    {
        "hook_type": "curiosity",
        "pattern": " rhetorical question followed by stat",
        "example": "Did you know 90% of creators quit before...",
        "predicted_retention_boost": 25.0
    },
    ...
]
```

**Requirements:**
- Needs at least 3 viral videos with hook text
- Analyzes top 10 viral videos (reduced from 20 for efficiency)
- Uses top 8 hooks for analysis

**Prompt Used:** [`script_prompts.HOOK_ANALYSIS_PROMPT`](backend/app/prompts/script_prompts.py)

---

#### `generate_hooks_for_topic(topic, channel, count=5) -> List[Dict]`

Generates multiple hook variations for a given topic.

**Parameters:**
- `topic` (str): Video topic
- `channel` (Channel): User's channel for style context
- `count` (int, default=5): Number of hook variations

**Returns:**
```python
[
    {
        "hook_text": "What if I told you...",
        "hook_type": "curiosity",
        "emotional_trigger": "curiosity"
    },
    ...
]
```

**Prompt Used:** [`hook_prompts.HOOK_GENERATION_PROMPT`](backend/app/prompts/hook_prompts.py)

---

## thumbnail_engine.py

**File:** [`thumbnail_engine.py`](backend/app/intelligence/thumbnail_engine.py)

### Class: `ThumbnailEngine`

Analyzes thumbnails using vision models and recommends thumbnail concepts.

---

#### `analyze_thumbnail(thumbnail_url, video_title) -> Dict`

Analyzes a thumbnail image using GPT-4o vision.

**Parameters:**
- `thumbnail_url` (str): URL to the thumbnail image
- `video_title` (str): Title of the video for context

**Returns:**
```python
{
    "ctr_prediction": 7.5,
    "emotional_impact": 8.0,
    "curiosity_intensity": 7.0,
    "text_clarity": 8.5,
    "color_contrast": 9.0,
    "simplicity": 7.5,
    "alignment_score": 8.0,
    "primary_emotion": "excitement",
    "strengths": ["Bold colors", "Clear text overlay"],
    "weaknesses": ["Too cluttered", "Face barely visible"],
    "improvement_suggestions": ["Zoom in on face", "Reduce text to 3 words"]
}
```

**Vision Model:** Uses `call_openai_vision` with vision-capable model.

**Prompt Used:** [`thumbnail_prompts.THUMBNAIL_ANALYSIS_PROMPT`](backend/app/prompts/thumbnail_prompts.py)

---

#### `recommend_thumbnail_concept(topic, title, niche, top_competitor_styles) -> Dict`

Recommends a thumbnail concept without requiring an image.

**Parameters:**
- `topic` (str): Video topic
- `title` (str): Video title
- `niche` (str): Content niche
- `top_competitor_styles` (List[str]): List of competitor thumbnail styles

**Returns:**
```python
{
    "concept": "Close-up face with reaction expression",
    "layout": "Centered face, text at bottom",
    "recommended_emotion": "surprise",
    "color_palette": ["red", "white", "black"],
    "text_overlay": "You won't believe...",
    "background_style": "Blurred action shot",
    "psychological_hook": "Curiosity gap",
    "differentiation_from_competitors": "Use reaction shot instead of product shot"
}
```

**Prompt Used:** [`thumbnail_prompts.THUMBNAIL_RECOMMENDATION_PROMPT`](backend/app/prompts/thumbnail_prompts.py)

---

## audience_engine.py

**File:** [`audience_engine.py`](backend/app/intelligence/audience_engine.py)

### Class: `AudienceEngine`

Analyzes audience composition, pain points, and interests.

---

#### `analyze_audience(channel, db) -> Dict`

Analyzes audience based on comments and engagement patterns.

**Parameters:**
- `channel` (Channel): User's channel
- `db` (Session): Database session

**Returns:**
```python
{
    "audience_type": "tech-savvy millennials",
    "audience_pain_points": ["information overload", "tool fatigue"],
    "content_themes": ["productivity", "automation", "AI tools"],
    "recommended_topics": ["AI tutorials", "workflow automation"]
}
```

**Prompt Used:** [`audience_prompts.AUDIENCE_ANALYSIS_PROMPT`](backend/app/prompts/audience_prompts.py)

---

#### `get_audience_insights(channel) -> Dict`

Quick audience insights from channel profile (no AI call).

**Parameters:**
- `channel` (Channel): User's channel

**Returns:** Basic insights from channel data without AI analysis.

---

#### `async enhanced_audience_analysis(channel, db, include_web_scrape=True) -> Dict`

Enhanced analysis with web scraping for deeper audience understanding.

**Parameters:**
- `channel` (Channel): User's channel
- `db` (Session): Database session
- `include_web_scrape` (bool, default=True): Enable web scraping

**Web Sources Scraped:**
- Community discussions (Quora, Reddit)
- Forum discussions
- Trending topics

**Returns:** Base analysis plus:
```python
{
    "scraped_insights": {...},
    "trending_topics": [...],
    "key_questions": [...],
    "content_opportunities": [...],
    "engagement_recommendations": [...]
}
```

---

## trend_engine.py

**File:** [`trend_engine.py`](backend/app/intelligence/trend_engine.py)

### Class: `TrendEngine`

Real-time trend detection using web scraping and AI analysis.

---

#### `async detect_trends(niche, time_range='week') -> List[Dict]`

Detects trends in a niche using web scraping.

**Parameters:**
- `niche` (str): The niche to analyze
- `time_range` (str, default="week"): Time range: `day`, `week`, `month`

**Returns:**
```python
[
    {
        "topic": "AI video editing",
        "velocity_score": 8.5,
        "saturation_score": 3.0,
        "opportunity_window": "open",
        "evidence": ["40 videos in 7 days", "Search +65%"],
        "trend_direction": "rising"
    },
    ...
]
```

**Sources:** Reddit, news, forums (cached for efficiency)

**Global Instance:** `trend_engine = TrendEngine()`

---

#### `async enhanced_trend_detection(niche, include_twitter=True, include_youtube=True) -> Dict`

Comprehensive trend detection with platform-specific analysis.

**Returns:**
```python
{
    "niche": "technology",
    "trends": [...],
    "additional_insights": {
        "real_time_trends": [...],
        "bursting_topics": [...],
        "sustained_growth": [...],
        "platform_specific": {...}
    },
    "analyzed_at": "2024-01-15T10:30:00Z",
    "sources": ["reddit", "news", "forums", "community"]
}
```

---

#### `async get_breaking_topics(niche) -> List[Dict]`

Gets breaking/popping topics from real-time sources.

**Returns:** Top 20 breaking topics from multiple sources.

---

#### `async get_rising_searches(keyword) -> List[str]`

Gets rising search queries for a keyword (YouTube suggest style).

**Returns:** List of rising search queries.

---

## retention_engine.py

**File:** [`retention_engine.py`](backend/app/intelligence/retention_engine.py)

### Class: `RetentionEngine`

Analyzes video transcripts to identify retention patterns and drop-off points.

---

#### `analyze_retention(video_title, transcript, duration_seconds) -> Dict`

Analyzes transcript to predict viewer retention and identify issues.

**Parameters:**
- `video_title` (str): Title of the video
- `transcript` (str): Full video transcript
- `duration_seconds` (int): Video duration

**Returns:**
```python
{
    "retention_hooks": [
        {"timestamp": "0:00", "text": "Did you know...", "retention_boost": 25}
    ],
    "drop_off_points": [
        {"timestamp": "3:45", "reason": "Topic change without transition", "severity": "high"}
    ],
    "pacing_score": 7.5,
    "pacing_notes": "Good pacing overall, minor slow section at 5:00",
    "retention_tips": [
        "Add visual cue before topic change at 3:45",
        "Highlight key moment at 7:00"
    ]
}
```

**Transcript Limit:** First 5000 characters (for token efficiency).

**Prompt Used:** [`retention_prompts.RETENTION_ANALYSIS_PROMPT`](backend/app/prompts/retention_prompts.py)

---

## viral_engine.py

**File:** [`viral_engine.py`](backend/app/intelligence/viral_engine.py)

### Class: `ViralEngine`

Analyzes why videos went viral and identifies replicable patterns.

---

#### `analyze_viral_pattern(video_title, view_count, like_count, comment_count, engagement_rate, thumbnail_description, hook_text) -> Dict`

Analyzes a viral video to identify success factors.

**Parameters:**
- `video_title` (str): Title of the video
- `view_count` (int): Total views
- `like_count` (int): Number of likes
- `comment_count` (int): Number of comments
- `engagement_rate` (float): (likes + comments) / views
- `thumbnail_description` (str): Description of the thumbnail
- `hook_text` (str): Opening hook text

**Returns:**
```python
{
    "viral_driver": "Strong emotional hook + timely topic",
    "emotional_triggers": ["curiosity", "excitement", "surprise"],
    "replicable_pattern": "Open with counterintuitive claim, deliver proof within 30 seconds",
    "why_it_worked": "Tapped into trending topic with unique angle",
    "advice_for_creator": "Apply the counterintuitive hook structure to your next video"
}
```

**Prompt Used:** [`retention_prompts.VIRAL_PATTERN_PROMPT`](backend/app/prompts/retention_prompts.py)

---

## Dependencies

### External Services

| Service | Purpose |
|---------|---------|
| OpenRouter | LLM API for all AI analysis |
| YouTube API | Channel/video data for analysis |
| Redis | Caching scraped trend data |
| Firecrawl | Web scraping for enhanced analysis |

### Internal Dependencies

```python
from app.services.openrouter_service import call_openai, call_openai_vision, safe_json_loads
from app.services.scraper_service import scraper_service
from app.services.context_optimizer import compress_videos_for_analysis, truncate_to_token_limit
from app.prompts.* import *  # Prompt templates
from app.utils.cache_manager import scraped_data_cache
from app.models.* import *    # Database models
```

---

## Context Optimization

All engines implement context optimization to reduce token usage:

1. **Video Limits:** Most engines use 5-10 videos (reduced from full channel data)
2. **Transcript Truncation:** Long transcripts truncated to 5000-10000 chars
3. **Token Counting:** Uses `context_optimizer.count_tokens()` before API calls
4. **Hard Truncation:** Prompts truncated to 1500-2000 token limits

---

## Error Handling

All AI calls have fallback responses:

```python
try:
    response = call_openai(...)
    return safe_json_loads(response)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    return {...}  # Default/fallback response
```

**Fallback Response Patterns:**
- Empty lists `[]` for list returns
- Empty strings `""` for single-value returns
- Default dicts with `"unknown"` or `"unknown"` values

---

## Usage Examples

### Basic Creator Analysis

```python
from app.intelligence.creator_analyzer import CreatorAnalyzer

analyzer = CreatorAnalyzer()
top_videos = [
    {"title": "Video 1", "views": 100000, "transcript_excerpt": "..."},
    {"title": "Video 2", "views": 80000, "transcript_excerpt": "..."},
]

profile = analyzer.analyze_creator(
    channel_title="Tech Channel",
    top_video_data=top_videos,
    subscriber_count=100000
)
```

### Competitor Analysis

```python
from app.intelligence.competitor_engine import CompetitorEngine

engine = CompetitorEngine()
analysis = engine.analyze_competitor(
    competitor_youtube_id="UCxxxxxxx",
    creator_niche="technology",
    db=session
)
```

### Enhanced Gap Detection with Scraping

```python
from app.intelligence.gap_detector import GapDetector

detector = GapDetector()
gaps = await detector.enhanced_gap_detection(
    channel=user_channel,
    db=session,
    include_web_scrape=True
)
```

### Trend Detection

```python
from app.intelligence.trend_engine import trend_engine

trends = await trend_engine.detect_trends("technology", time_range="week")
```

---

## Testing Notes

### Mocking AI Calls

```python
from unittest.mock import patch

# Mock OpenRouter calls
with patch('app.intelligence.creator_analyzer.call_openai') as mock:
    mock.return_value = '{"niche": "tech", "audience_type": "developers"}'
    
    analyzer = CreatorAnalyzer()
    profile = analyzer.analyze_creator("Test Channel", [...], 1000)
    
    assert profile["niche"] == "tech"
```

### Mocking Web Scraping

```python
with patch('app.intelligence.trend_engine.scraper_service') as mock:
    mock.scrape_reddit_trends.return_value = [...]
    mock.scrape_trend_aggregator.return_value = [...]
    
    engine = TrendEngine()
    trends = await engine.detect_trends("niche")
```

---

## Performance Considerations

| Engine | Token Cost | Latency | Notes |
|--------|-----------|---------|-------|
| CreatorAnalyzer | Medium | ~2-3s | Uses 5 videos |
| CompetitorEngine | Medium-High | ~3-5s | Uses 5 videos + API calls |
| GapDetector | Low-Medium | ~2-3s | Uses titles only |
| ScriptGenerator | High | ~5-10s | Full script needs 4000 tokens |
| HookEngine | Low | ~2s | Simple prompt |
| ThumbnailEngine | Medium | ~3s | Vision API is slower |
| AudienceEngine | Medium | ~3s | With scraping option |
| TrendEngine | Medium | ~5-10s | Concurrent scraping |
| RetentionEngine | Low | ~2s | Transcript-limited |
| ViralEngine | Low | ~2s | Simple metrics input |