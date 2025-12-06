RETENTION_ANALYSIS_PROMPT = """Analyze this video for retention patterns. Be concise.

TITLE: {title}
DURATION: {duration_seconds} seconds
TRANSCRIPT: {transcript}

Identify: retention hooks, drop-off points, pacing issues, what works.

Return JSON:
{{
  "retention_hooks": [
    {{
      "timestamp_range": "0-30",
      "technique": "What keeps viewers",
      "why_it_works": "Psychological explanation"
    }}
  ],
  "drop_off_points": [
    {{
      "timestamp_range": "2:00-2:30",
      "reason": "Why viewers drop here",
      "suggestion": "How to fix"
    }}
  ],
  "pacing_score": 7.5,
  "pacing_notes": "Overall pacing description",
  "retention_tips": ["Tip 1", "Tip 2"]
}}

Return ONLY the JSON object."""

VIRAL_PATTERN_PROMPT = """Analyze why this video went viral. Be concise.

TITLE: {title}
VIEWS: {view_count:,} | LIKES: {like_count:,} | COMMENTS: {comment_count:,}
ENGAGEMENT: {engagement_rate}%
THUMBNAIL: {thumbnail_description}
HOOK: {hook_text}

Identify: viral driver, emotional triggers, replicable pattern, why it resonated.

Return JSON:
{{
  "viral_driver": "Primary factor",
  "emotional_triggers": ["trigger 1", "trigger 2"],
  "replicable_pattern": "Pattern to reuse",
  "why_it_worked": "2-3 sentence explanation",
  "advice_for_creator": "What to do more of"
}}

Return ONLY the JSON object."""