CREATOR_PROFILE_PROMPT = """Analyze this YouTube creator. Be concise.

CHANNEL: {channel_name} | {subscriber_count:,} subs

VIDEO SAMPLES:
{video_samples}

Return JSON only:
{{
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
}}"""