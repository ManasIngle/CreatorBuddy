COMPETITOR_INTELLIGENCE_PROMPT = """Analyze competitor channel. Be concise.

COMPETITOR: {competitor_name} | {subscriber_count:,} subs
NICHE: {creator_niche}

TOP VIDEOS:
{top_videos}

Return JSON:
{{
  "why_they_succeed": "2-3 sentence explanation",
  "best_formats": ["format1", "format2"],
  "emotional_triggers": ["trigger1", "trigger2"],
  "content_gaps": ["3-5 topics NOT covered"],
  "hook_patterns": ["2-3 patterns in their openings"],
  "thumbnail_style": "colors, faces, text placement, emotion",
  "upload_pattern": "frequency and consistency"
}}

Return ONLY the JSON object."""

COMPETITOR_GAP_PROMPT = """Identify 5-8 content gaps for this niche. Be very concise.

NICHE: {niche}
CREATOR TOPICS: {creator_topics}
COMPETITORS: {competitor_coverage}
AUDIENCE QUESTIONS: {audience_questions}

Find topics where: audience wants it, competitors not covering well, fits creator style.

Return JSON array:
[{{
  "topic": "specific topic",
  "reason": "why it's valuable",
  "opportunity_score": 7.5,
  "competition_level": "low",
  "suggested_angle": "how to approach uniquely",
  "suggested_title": "YouTube title",
  "trend_direction": "rising"
}}]

Return ONLY the JSON array."""