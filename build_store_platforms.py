"""Step 9a. Turns eval\\store_probe.csv into backend\\store_platforms.json (the list of stores the
generic scraper may use). Only stores that passed the probe AND whose robots.txt allows search.
Run from E:\\JaChai:  .\\backend\\.venv\\Scripts\\python.exe build_store_platforms.py"""
import csv, json, re, sys
from pathlib import Path
from urllib.parse import quote_plus

SAMPLE = [("mobile", "phone"), ("laptop", "laptop"), ("appliance", "fan"), ("cycle", "cycle"),
          ("jewel", "ring"), ("saree", "saree"), ("fashion", "shirt"), ("sneaker", "shoes"),
          ("watch", "watch"), ("beauty", "cream"), ("sportswear", "shirt"), ("snack", "rice")]

def sample_term(cat):
    c = (cat or "").lower()
    return next((t for k, t in SAMPLE if k in c), "product")

src = Path("eval/store_probe.csv")
if not src.exists():
    sys.exit("eval\\store_probe.csv not found. Run probe_stores.py first.")

ready, pending, seen = [], [], set()
for r in csv.DictReader(src.open(encoding="utf-8-sig")):
    v, dom = r["verdict"], r["domain"]
    if not dom:
        continue
    term = sample_term(r["category"])
    tmpl = re.sub(r"(?<==)" + re.escape(quote_plus(term)) + r"(?=&|$)", "{q}", r["search_url"] or "")
    entry = {"name": r["name"], "category": r["category"], "domain": dom,
             "platform": "generic" if r["platform"] in ("unknown", "nextjs-js", "") else r["platform"],
             "search_url_template": tmpl, "sample_term": term}
    if v.startswith("scrapeable") and r["robots_ok"] == "True" and "{q}" in tmpl:
        key = (dom, r["category"])
        if key in seen:
            continue
        seen.add(key)
        ready.append(entry)
    elif v.startswith("prices present") or v.startswith("needs JS"):
        pending.append({**entry, "verdict": v})

out = Path("backend/store_platforms.json")
out.write_text(json.dumps({"ready": ready, "pending": pending}, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print(f"ready: {len(ready)}  pending (later): {len(pending)}")
print("ready by platform:", dict(Counter(e['platform'] for e in ready)))
print("ready by category:")
for k, n in Counter(e['category'] for e in ready).most_common():
    print(f"  {n:3d}  {k}")
print("saved", out)
