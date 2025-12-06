AUDIENCE_ANALYSIS_PROMPT = """Analyze this channel's audience. Be concise.

CHANNEL: {channel_name}
NICHE: {niche}

COMMENT SAMPLES:
{comments}

ENGAGEMENT PATTERNS:
{engagement_patterns}

Identify: demographics, what they care about, frequent questions, pain points, what resonates.

Return JSON:
{{
  "audience_type": "Primary audience description",
  "audience_pain_points": ["pain point 1", "pain point 2"],
  "content_themes": ["theme they engage with most"],
  "recommended_topics": ["topics that would resonate"],
  "what_resonates": "What gets highest engagement",
  "frustrations": ["common frustrations from comments"]
}}

Return ONLY the JSON object."""