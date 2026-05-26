"""
Realistic engine-shaped test: generate JSON like a real engine call would.
This is the actual call shape used by creator_analyzer, gap_detector, etc.
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.openrouter_service import call_openai, safe_json_loads

print("\n=== JSON-mode test (medium tier) — like creator profile analysis ===")
try:
    out = call_openai(
        system_prompt="You analyze YouTube creators. Return JSON only. No preamble. No reasoning aloud.",
        user_prompt=(
            "Channel: 'How to YouTube' has 50,000 subscribers and posts videos like "
            "'Best Camera for Vlogging 2026' and 'Editing Tips That Actually Work'. "
            "Return JSON: {niche, audience_type, content_themes (array of 3 strings)}"
        ),
        response_format="json",
        complexity="medium",
        max_tokens=300,
        cache_ttl=0,
        operation="smoke_engine_creator",
    )
    print(f"Raw output:\n{out}\n")
    parsed = safe_json_loads(out)
    print(f"Parsed: {json.dumps(parsed, indent=2)}")
    assert "niche" in parsed, "Missing 'niche' field"
    print("✓ JSON parse + required fields OK")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n=== Title generation (simple tier) — like script_generator ===")
try:
    out = call_openai(
        system_prompt="You are a YouTube title expert. Return JSON only. No preamble.",
        user_prompt=(
            "Generate 3 titles for a video about 'how to grow on YouTube as a beginner'. "
            "Return JSON: {titles: [{title, ctr_prediction (1-10)}]}"
        ),
        response_format="json",
        complexity="simple",
        max_tokens=300,
        cache_ttl=0,
        operation="smoke_engine_titles",
    )
    print(f"Raw output:\n{out}\n")
    parsed = safe_json_loads(out)
    print(f"Parsed: {json.dumps(parsed, indent=2)}")
    titles = parsed.get("titles", [])
    assert len(titles) >= 1, "No titles returned"
    print(f"✓ Generated {len(titles)} titles")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")

print("\n=== Hook generation (simple tier) — like script_generator.generate_hook ===")
try:
    out = call_openai(
        system_prompt="You write viral YouTube hooks. Return only the hook text, one paragraph, no preamble.",
        user_prompt="Topic: 'why most YouTubers fail'. Tone: conversational. Format: storytelling.",
        complexity="simple",
        max_tokens=200,
        cache_ttl=0,
        operation="smoke_engine_hook",
    )
    print(f"Hook: {out!r}")
    assert out and len(out) > 20, "Hook too short"
    print(f"✓ Hook generated ({len(out)} chars)")
except Exception as e:
    print(f"✗ FAILED: {type(e).__name__}: {e}")
