"""
Smoke test: hit each free-model tier with a tiny request to confirm
the key works and the fallback chain is healthy.

Usage:
    cd backend && source venv/bin/activate
    python ../scripts/smoke_test_openrouter.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.openrouter_service import call_openai

TIERS = ["simple", "medium", "complex"]
PROMPT = "Reply with only the word 'OK'."

for tier in TIERS:
    print(f"\n=== {tier} ===")
    try:
        out = call_openai(
            system_prompt="You answer with the exact word requested. No preamble.",
            user_prompt=PROMPT,
            complexity=tier,
            max_tokens=10,
            cache_ttl=0,  # bypass cache for the test
            operation=f"smoke_{tier}",
        )
        print(f"  → {out!r}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
