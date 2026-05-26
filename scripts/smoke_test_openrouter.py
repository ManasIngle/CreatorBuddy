"""
Smoke test: hit each tier with a tiny request to confirm
the keys work and the fallback chain is healthy.

Usage:
    cd backend && source venv/bin/activate
    python ../scripts/smoke_test_openrouter.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.openrouter_service import call_openai, _minimax_client
from app.config import settings

TIERS = ["simple", "medium", "complex"]
PROMPT = "Reply with only the word 'OK'."

print(f"OpenRouter key: {'✓ set' if settings.OPENROUTER_API_KEY else '✗ MISSING'}")
print(f"MiniMax key:    {'✓ set' if settings.MINIMAX_API_KEY else '✗ not configured (free tier only)'}")
if _minimax_client:
    print(f"  → MiniMax client active ({settings.MINIMAX_MODEL})")
print()

for tier in TIERS:
    print(f"=== {tier} ===")
    try:
        out = call_openai(
            system_prompt="You answer with the exact word requested. No preamble.",
            user_prompt=PROMPT,
            complexity=tier,
            max_tokens=20,
            cache_ttl=0,  # bypass cache for the test
            operation=f"smoke_{tier}",
        )
        print(f"  → {out!r}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
    print()

# Direct MiniMax call if configured
if _minimax_client:
    print("=== MiniMax direct ===")
    try:
        out = call_openai(
            system_prompt="You answer with the exact word requested. No preamble.",
            user_prompt=PROMPT,
            model=settings.MINIMAX_MODEL,
            max_tokens=20,
            cache_ttl=0,
            operation="smoke_minimax_direct",
        )
        print(f"  → {out!r}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
