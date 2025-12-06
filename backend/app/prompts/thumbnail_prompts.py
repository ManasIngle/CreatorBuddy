THUMBNAIL_ANALYSIS_PROMPT = """Analyze this YouTube thumbnail. Score 0-10, be concise.

VIDEO: {video_title}

Score:
1. Emotional impact - What emotion does it convey?
2. Curiosity intensity - Does it make you wonder?
3. Text clarity - Readable and impactful?
4. Color contrast - Stands out in feed?
5. Simplicity - Clear focal point?
6. Title alignment - Matches the title?

Return JSON:
{{
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
}}

Return ONLY the JSON."""

THUMBNAIL_RECOMMENDATION_PROMPT = """Design a thumbnail concept. Be concise.

TOPIC: {topic}
TITLE: {title}
NICHE: {niche}
COMPETITOR STYLES: {competitor_styles}

Create concept that stands out but fits niche expectations.

Return JSON:
{{
  "concept": "High-level description",
  "layout": "Element arrangement",
  "recommended_emotion": "Facial expression or emotion",
  "color_palette": ["#FF4444", "#FFFFFF"],
  "text_overlay": "2-4 words max",
  "background_style": "Background description",
  "psychological_hook": "Why it generates clicks",
  "differentiation_from_competitors": "How it stands out"
}}

Return ONLY the JSON."""