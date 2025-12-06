HOOK_GENERATION_PROMPT = """Generate {count} YouTube hook variations. Be concise.

TOPIC: {topic}
NICHE: {niche}
CREATOR STYLE: {creator_style}

Use different techniques: curiosity gap, shocking statement, bold promise, story opener, direct challenge.
Each hook: 60-100 words, compelling enough to stop scrolling.

Return JSON:
{{
  "hooks": [
    {{
      "text": "The hook text...",
      "type": "curiosity_gap",
      "emotional_trigger": "fear/curiosity/excitement",
      "predicted_retention_boost": 8.5,
      "explanation": "Why this works"
    }}
  ]
}}

Return ONLY the JSON."""

HOOK_SCORING_PROMPT = """Score this YouTube hook (0-10). Be concise.

HOOK: {hook_text}
NICHE: {niche}

Score: pattern interrupt, curiosity/suspense, promise clarity, authenticity.

Return JSON:
{{
  "overall_score": 7.5,
  "pattern_interrupt": 8,
  "curiosity_level": 7,
  "promise_clarity": 8,
  "authenticity": 7,
  "improvement_suggestion": "How to make it stronger"
}}

Return ONLY the JSON."""