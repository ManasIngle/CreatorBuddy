"""One-off: list current free models on OpenRouter using the user's key."""
import json, sys
data = json.load(sys.stdin)
models = data["data"]
free = [m for m in models if m.get("pricing", {}).get("prompt") == "0" and m.get("pricing", {}).get("completion") == "0"]
print(f"Total models: {len(models)}")
print(f"Free models:  {len(free)}")
print()
for m in sorted(free, key=lambda x: x["id"]):
    mods = ",".join(m.get("architecture", {}).get("input_modalities", []))
    ctx = m.get("context_length", "?")
    print(f"{m['id']:65s} ctx={ctx:>8} mods={mods}")
