# -*- coding: utf-8 -*-
"""Fetch aihot daily JSON and generate HTML dashboard."""
import json, urllib.request, urllib.error, datetime, os, sys

CACHE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(CACHE_DIR, "aihot_daily.json")
GEN_SCRIPT = os.path.join(CACHE_DIR, "gen_html.py")

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def today_utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

errors = []

try:
    # Try today's daily first
    data = fetch(f"https://aihot.virxact.com/api/public/daily/{today_utc()}")
    print(f"OK: fetched daily for {data.get('date', today_utc())}")
except Exception as e:
    errors.append(f"today failed: {e}")
    try:
        # Fallback to latest daily
        data = fetch("https://aihot.virxact.com/api/public/daily")
        print(f"OK: fallback to latest daily for {data.get('date', 'unknown')}")
    except Exception as e2:
        errors.append(f"fallback failed: {e2}")
        print("ERRORS:", errors)
        sys.exit(1)

# Save JSON cache
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"SAVED JSON: {JSON_PATH}")

# Run gen_html.py
exec(open(GEN_SCRIPT, encoding="utf-8").read())
