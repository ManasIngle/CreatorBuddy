# Prompts Module

This module contains all AI prompt templates used by the intelligence engines. Prompts are optimized for token efficiency and structured JSON output.

## Overview

Prompts are stored as template strings with placeholders that get filled in at runtime. Each prompt is designed to:
- Produce structured JSON output
- Minimize token usage while preserving quality
- Guide the AI to specific analysis patterns
- Work with the complexity routing system

## File Structure

```
backend/app/prompts/
├── __init__.py              # Package marker
├── script_prompts.py        # Script generation prompts
├── hook_prompts.py         # Hook generation/scoring prompts
├── creator_prompts.py      # Creator profile analysis
├── competitor_prompts.py   # Competitor analysis
├── gap_prompts.py          # Content gap detection
├── audience_prompts.py      # Audience analysis
├── retention_prompts.py    # Retention and viral analysis
└── thumbnail_prompts.py    # Thumbnail analysis/recommendation
```

---

## script_prompts.py

**File:** [`script_prompts.py`](backend/app/prompts/script_prompts.py)

### Prompt Templates

---

#### `TITLE_SUGGESTIONS_PROMPT`

Generates 3 YouTube title options.

**Variables:**
- `{topic}`: Video topic
- `{niche}`: Content niche
- `{channel_style}`: Creator's style description
- `{subscriber_count}`: Channel subscriber count

**Token Estimate:** ~150 tokens input

**Output Format:**
```json
{
  "titles": [
    {"title": "...", "type": "question", "hook_type": "curiosity"},
    {"title": "...", "type": "statement", "hook_type": "value"},
    {"title": "...", "type": "contrarian", "hook_type": "challenge"}
  ]
}
```

**Rules:**
- Under 60 characters each
- Mix of question, statement, contrarian types
- Curiosity gap or emotional hook
- No empty clickbait

---

#### `SCRIPT_HOOK_PROMPT`

Generates a 30-second opening hook.

**Variables:**
- `{title}`: Video title
- `{topic}`: Video topic
- `{niche}`: Content niche
- `{creator_style}`: Creator's speaking style
- `{storytelling_structure}`: Narrative pattern

**Token Estimate:** ~200 tokens input

**Output:** Plain hook text (80-120 words)

**Requirements:**
- Capture attention in first 3 seconds
- Pattern interrupt or curiosity gap
- Specific value promise
- Natural for creator's voice
- No generic openers
- Start with strongest sentence

---

#### `FULL_SCRIPT_PROMPT`

Generates complete video script.

**Variables:**
- `{title}`: Video title
- `{topic}`: Video topic
- `{hook}`: Pre-generated hook text
- `{niche}`: Content niche
- `{creator_personality}`: Creator personality summary
- `{speaking_style}`: Speaking style description
- `{storytelling_structure}`: Narrative structure type
- `{target_duration}`: Target minutes
- `{format_type}`: Format (educational, story, list, review)
- `{audience_type}`: Target audience

**Token Estimate:** ~400 tokens input + 4000 output

**Output:** Complete script with timestamps and formatting

**Structure:**
1. HOOK (use provided, word for word)
2. CONTEXT (30 sec - why it matters now)
3. MAIN (format-specific, 3-5 sections with transitions)
4. CTA (30 sec - single clear call to action)
5. OUTRO (15 sec - brief, energetic)

**Formatting:**
- `[PAUSE]` for breath marks
- `[EMPHASIS]` before stressed words
- `[B-ROLL: description]` for visual cutaways
- `**bold**` for on-screen text
- Write as creator speaks, not essay

---

#### `HOOK_ANALYSIS_PROMPT`

Analyzes viral hooks to extract patterns.

**Variables:**
- `{count}`: Number of hooks
- `{niche}`: Content niche
- `{hooks}`: Hook texts separated by `---`

**Token Estimate:** ~500 tokens input

**Output Format:**
```json
{
  "patterns": [
    {
      "name": "Pattern Name",
      "psychology": "Why it works",
      "template": "Template with [VARIABLES]",
      "example": "Example from hooks"
    }
  ]
}
```

---

## hook_prompts.py

**File:** [`hook_prompts.py`](backend/app/prompts/hook_prompts.py)

### Prompt Templates

---

#### `HOOK_GENERATION_PROMPT`

Generates hook variations for a topic.

**Variables:**
- `{topic}`: Video topic
- `{niche}`: Content niche
- `{creator_style}`: Creator's style
- `{count}`: Number of hooks to generate

**Token Estimate:** ~150 tokens input

**Output Format:**
```json
{
  "hooks": [
    {
      "text": "The hook text...",
      "type": "curiosity_gap",
      "emotional_trigger": "fear/curiosity/excitement",
      "predicted_retention_boost": 8.5,
      "explanation": "Why this works"
    }
  ]
}
```

**Techniques Used:**
- Curiosity gap
- Shocking statement
- Bold promise
- Story opener
- Direct challenge

---

#### `HOOK_SCORING_PROMPT`

Scores a hook 0-10.

**Variables:**
- `{hook_text}`: The hook to score
- `{niche}`: Content niche

**Token Estimate:** ~100 tokens input

**Output Format:**
```json
{
  "overall_score": 7.5,
  "pattern_interrupt": 8,
  "curiosity_level": 7,
  "promise_clarity": 8,
  "authenticity": 7,
  "improvement_suggestion": "How to make it stronger"
}
```

**Scoring Dimensions:**
- Pattern interrupt
- Curiosity/suspense
- Promise clarity
- Authenticity

---

## creator_prompts.py

**File:** [`creator_prompts.py`](backend/app/prompts/creator_prompts.py)

### Prompt Templates

---

#### `CREATOR_PROFILE_PROMPT`

Analyzes creator channel to build profile.

**Variables:**
- `{channel_name}`: Channel name
- `{subscriber_count}`: Subscriber count
- `{video_samples}`: Video data (title | views | likes | duration)

**Token Estimate:** ~600 tokens input

**Output Format:**
```json
{
  "niche": "Primary niche (2-4 words)",
  "niche_tags": ["tag1", "tag2", "tag3"],
  "audience_type": "Primary audience description",
  "personality_summary": "2 sentences on personality/brand",
  "speaking_style": "formal/casual, fast/slow, style",
  "storytelling_structure": "Pattern used (problem-solution, etc)",
  "content_themes": ["recurring theme 1", "recurring theme 2"],
  "audience_pain_points": ["pain point 1", "pain point 2"],
  "creator_strength": "What they do better than most",
  "growth_opportunity": "Single biggest content opportunity"
}
```

---

## competitor_prompts.py

**File:** [`competitor_prompts.py`](backend/app/prompts/competitor_prompts.py)

### Prompt Templates

---

#### `COMPETITOR_INTELLIGENCE_PROMPT`

Analyzes competitor channel.

**Variables:**
- `{competitor_name}`: Competitor channel name
- `{subscriber_count}`: Subscriber count
- `{creator_niche}`: User's niche for comparison
- `{top_videos}`: Compressed video data

**Token Estimate:** ~500 tokens input

**Output Format:**
```json
{
  "why_they_succeed": "2-3 sentence explanation",
  "best_formats": ["format1", "format2"],
  "emotional_triggers": ["trigger1", "trigger2"],
  "content_gaps": ["3-5 topics NOT covered"],
  "hook_patterns": ["2-3 patterns in their openings"],
  "thumbnail_style": "colors, faces, text placement, emotion",
  "upload_pattern": "frequency and consistency"
}
```

---

#### `COMPETITOR_GAP_PROMPT`

Identifies content gaps from competitor analysis.

**Variables:**
- `{niche}`: Content niche
- `{creator_topics}`: User's covered topics
- `{competitor_coverage}`: What competitors cover
- `{audience_questions}`: Audience questions

**Token Estimate:** ~400 tokens input

**Output Format:** JSON array of gaps with:
- `topic`: Specific topic (5-10 words)
- `reason`: Why it's valuable
- `opportunity_score`: 0-10
- `competition_level`: low/medium/high
- `suggested_angle`: Unique take
- `suggested_title`: Compelling title
- `trend_direction`: rising/stable/declining

---

## gap_prompts.py

**File:** [`gap_prompts.py`](backend/app/prompts/gap_prompts.py)

### Prompt Templates

---

#### `GAP_DETECTION_PROMPT`

Finds content gaps for a creator.

**Variables:**
- `{niche}`: Content niche
- `{creator_topics}`: User's topics (15 max)
- `{competitor_coverage}`: Competitor topics
- `{audience_questions}`: Questions from comments

**Token Estimate:** ~400 tokens input

**Output Format:** JSON array of 5-8 gaps:
```json
[
  {
    "topic": "Specific topic (5-10 words)",
    "reason": "Why it's a real opportunity",
    "opportunity_score": 7.5,
    "competition_level": "low/medium/high",
    "suggested_angle": "Unique take",
    "suggested_title": "Compelling title",
    "trend_direction": "rising/stable/declining",
    "source_type": "competitor_gap/audience_question/search_trend"
  }
]
```

**Criteria:**
- Audience demands it
- Competitors not covering well
- Creator hasn't made it

---

## audience_prompts.py

**File:** [`audience_prompts.py`](backend/app/prompts/audience_prompts.py)

### Prompt Templates

---

#### `AUDIENCE_ANALYSIS_PROMPT`

Analyzes channel audience.

**Variables:**
- `{channel_name}`: Channel name
- `{niche}`: Content niche
- `{comments}`: Comment samples
- `{engagement_patterns}`: Engagement data

**Token Estimate:** ~400 tokens input

**Output Format:**
```json
{
  "audience_type": "Primary audience description",
  "audience_pain_points": ["pain point 1", "pain point 2"],
  "content_themes": ["theme they engage with most"],
  "recommended_topics": ["topics that would resonate"],
  "what_resonates": "What gets highest engagement",
  "frustrations": ["common frustrations from comments"]
}
```

---

## retention_prompts.py

**File:** [`retention_prompts.py`](backend/app/prompts/retention_prompts.py)

### Prompt Templates

---

#### `RETENTION_ANALYSIS_PROMPT`

Analyzes video for retention patterns.

**Variables:**
- `{title}`: Video title
- `{duration_seconds}`: Video duration
- `{transcript}`: Video transcript (limited to 5000 chars)

**Token Estimate:** ~2000 tokens input

**Output Format:**
```json
{
  "retention_hooks": [
    {
      "timestamp_range": "0-30",
      "technique": "What keeps viewers",
      "why_it_works": "Psychological explanation"
    }
  ],
  "drop_off_points": [
    {
      "timestamp_range": "2:00-2:30",
      "reason": "Why viewers drop here",
      "suggestion": "How to fix"
    }
  ],
  "pacing_score": 7.5,
  "pacing_notes": "Overall pacing description",
  "retention_tips": ["Tip 1", "Tip 2"]
}
```

---

#### `VIRAL_PATTERN_PROMPT`

Analyzes why video went viral.

**Variables:**
- `{title}`: Video title
- `{view_count}`: Total views
- `{like_count}`: Like count
- `{comment_count}`: Comment count
- `{engagement_rate}`: Engagement percentage
- `{thumbnail_description}`: Thumbnail description
- `{hook_text}`: Opening hook

**Token Estimate:** ~300 tokens input

**Output Format:**
```json
{
  "viral_driver": "Primary factor",
  "emotional_triggers": ["trigger 1", "trigger 2"],
  "replicable_pattern": "Pattern to reuse",
  "why_it_worked": "2-3 sentence explanation",
  "advice_for_creator": "What to do more of"
}
```

---

## thumbnail_prompts.py

**File:** [`thumbnail_prompts.py`](backend/app/prompts/thumbnail_prompts.py)

### Prompt Templates

---

#### `THUMBNAIL_ANALYSIS_PROMPT`

Analyzes thumbnail using vision.

**Variables:**
- `{video_title}`: Video title

**Token Estimate:** ~100 tokens (with vision)

**Output Format:**
```json
{
  "ctr_prediction": 7.5,
  "emotional_impact": 8,
  "curiosity_intensity": 7,
  "text_clarity": 6,
  "color_contrast": 8,
  "simplicity": 7,
  "alignment_score": 8,
  "primary_emotion": "shock",
  "strengths": ["Strong face expression"],
  "weaknesses": ["Text overlaps face"],
  "improvement_suggestions": ["Move text to bottom third"]
}
```

**Scoring Dimensions:**
- Emotional impact
- Curiosity intensity
- Text clarity
- Color contrast
- Simplicity
- Title alignment

---

#### `THUMBNAIL_RECOMMENDATION_PROMPT`

Recommends thumbnail concept.

**Variables:**
- `{topic}`: Video topic
- `{title}`: Video title
- `{niche}`: Content niche
- `{competitor_styles}`: Competitor thumbnail styles

**Token Estimate:** ~200 tokens input

**Output Format:**
```json
{
  "concept": "High-level description",
  "layout": "Element arrangement",
  "recommended_emotion": "Facial expression or emotion",
  "color_palette": ["#FF4444", "#FFFFFF"],
  "text_overlay": "2-4 words max",
  "background_style": "Background description",
  "psychological_hook": "Why it generates clicks",
  "differentiation_from_competitors": "How it stands out"
}
```

---

## Token Estimates Summary

| Prompt | Input Tokens | Output Tokens | Complexity |
|--------|-------------|---------------|------------|
| `TITLE_SUGGESTIONS` | ~150 | ~200 | Simple |
| `SCRIPT_HOOK` | ~200 | ~150 | Medium |
| `FULL_SCRIPT` | ~400 | ~4000 | Complex |
| `HOOK_ANALYSIS` | ~500 | ~500 | Medium |
| `HOOK_GENERATION` | ~150 | ~600 | Medium |
| `HOOK_SCORING` | ~100 | ~200 | Simple |
| `CREATOR_PROFILE` | ~600 | ~400 | Medium |
| `COMPETITOR_INTELLIGENCE` | ~500 | ~400 | Medium |
| `COMPETITOR_GAP` | ~400 | ~600 | Medium |
| `GAP_DETECTION` | ~400 | ~600 | Medium |
| `AUDIENCE_ANALYSIS` | ~400 | ~400 | Medium |
| `RETENTION_ANALYSIS` | ~2000 | ~500 | Complex |
| `VIRAL_PATTERN` | ~300 | ~300 | Medium |
| `THUMBNAIL_ANALYSIS` | ~100+image | ~400 | Medium |
| `THUMBNAIL_RECOMMENDATION` | ~200 | ~300 | Simple |

---

## Prompt Engineering Guidelines

### Structure
1. **Task definition** - What the AI should do
2. **Context** - Relevant information
3. **Rules** - Constraints and requirements
4. **Output format** - JSON structure expected
5. **Examples** - When needed for clarity

### Token Optimization
- Keep prompts under 600 tokens when possible
- Use compressed video context (no full transcripts)
- Limit transcript excerpts to 5000 chars
- Use markdown code blocks for JSON examples

### Quality Tips
- Be specific about output structure
- Include scoring scales when relevant
- Add "Be concise" for efficiency
- Use "Return ONLY the JSON" to prevent explanation
- Include 1-2 examples for complex outputs

---

## Testing Prompts

```python
from app.prompts.script_prompts import TITLE_SUGGESTIONS_PROMPT
from app.services.openrouter_service import call_openai

def test_title_prompt():
    prompt = TITLE_SUGGESTIONS_PROMPT.format(
        topic="How to start a YouTube channel",
        niche="content creation",
        channel_style="Educational but fun",
        subscriber_count=10000
    )
    
    result = call_openai(
        system_prompt="You are a YouTube title expert. Return JSON only.",
        user_prompt=prompt,
        response_format="json",
        complexity="simple"
    )
    
    import json
    titles = json.loads(result)
    assert "titles" in titles
    assert len(titles["titles"]) == 3
```

---

## Adding New Prompts

1. Create template string with `{}` placeholders
2. Document variables and their types
3. Document output format
4. Estimate token usage
5. Test with `call_openai`
6. Add to appropriate prompts file