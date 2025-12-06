TITLE_SUGGESTIONS_PROMPT = """Generate 3 YouTube title options. Be concise.

TOPIC: {topic}
NICHE: {niche}
CHANNEL STYLE: {channel_style}
CHANNEL SIZE: {subscriber_count:,} subs

Rules: Under 60 chars, curiosity gap or emotional hook, no empty clickbait.
Mix: one question, one statement, one contrarian.

Return JSON:
{{
  "titles": [
    {{"title": "...", "type": "question", "hook_type": "curiosity"}},
    {{"title": "...", "type": "statement", "hook_type": "value"}},
    {{"title": "...", "type": "contrarian", "hook_type": "challenge"}}
  ]
}}

Return ONLY the JSON."""

SCRIPT_HOOK_PROMPT = """Write a powerful 30-second YouTube hook. Be concise.

TITLE: {title}
TOPIC: {topic}
NICHE: {niche}
CREATOR STYLE: {creator_style}
STORYTELLING: {storytelling_structure}

Requirements:
- Capture attention in first 3 seconds
- Pattern interrupt or curiosity gap
- Specific value promise
- Natural for creator's voice
- 80-120 words max
- No generic openers
- Start with strongest sentence

Write ONLY the hook. No labels."""

FULL_SCRIPT_PROMPT = """Write a complete YouTube script. Be efficient.

TITLE: {title}
TOPIC: {topic}
HOOK: {hook}
NICHE: {niche}
CREATOR: {creator_personality}
STYLE: {speaking_style}
STRUCTURE: {storytelling_structure}
LENGTH: {target_duration} min (~{target_duration}00 words)
FORMAT: {format_type}
AUDIENCE: {audience_type}

Structure:
1. HOOK (use provided, word for word)
2. CONTEXT (30 sec - why it matters now)
3. MAIN (use {format_type} format, 3-5 sections with transitions, retention loops)
4. CTA (30 sec - single clear call to action)
5. OUTRO (15 sec - brief, energetic)

Formatting:
- [PAUSE] for breath marks
- [EMPHASIS] before stressed words
- [B-ROLL: description] for visual cutaways
- **bold** for on-screen text
- Write as creator speaks, not essay

Write the complete script now."""

HOOK_ANALYSIS_PROMPT = """Analyze these {count} viral hooks from {niche}. Be concise.

HOOKS:
{hooks}

Identify patterns with: name, psychological mechanism, template, example.

Return JSON:
{{
  "patterns": [
    {{
      "name": "Pattern Name",
      "psychology": "Why it works",
      "template": "Template with [VARIABLES]",
      "example": "Example from hooks"
    }}
  ]
}}

Return ONLY the JSON."""