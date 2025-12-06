GAP_DETECTION_PROMPT = """Find 5-8 content gaps for this creator. Be concise.

NICHE: {niche}
CREATOR TOPICS: {creator_topics}
COMPETITOR COVERAGE: {competitor_coverage}
AUDIENCE QUESTIONS: {audience_questions}

Find topics where: audience demands it, competitors not covering well, creator hasn't made it.

Return JSON array:
[{{
  "topic": "Specific topic (5-10 words)",
  "reason": "Why it's a real opportunity",
  "opportunity_score": 7.5,
  "competition_level": "low/medium/high",
  "suggested_angle": "Unique take",
  "suggested_title": "Compelling title",
  "trend_direction": "rising/stable/declining",
  "source_type": "competitor_gap/audience_question/search_trend"
}}]

Return ONLY the JSON array."""