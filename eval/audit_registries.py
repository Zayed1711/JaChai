#!/usr/bin/env python3
"""Audit JaChai registry CSVs. Usage: python eval/audit_registries.py registries/
Run it before every commit that touches a CSV. Exit code 1 if any hard error."""
import csv, re, sys, collections
from pathlib import Path
from urllib.parse import urlparse

d = Path(sys.argv[1] if len(sys.argv) > 1 else "registries")
files = sorted(d.glob("*.csv"))
readme = next(iter(d.glob("*README.md")), None)
claimed = {}
if readme:
    for name, n in re.findall(r"`([^`]+\.csv)`[^\n]*?\((\d+) stores\)", readme.read_text(encoding="utf-8")):
        claimed[name] = int(n)


def short(p):  # strip upload prefix like "1ba0e91e-"
    return re.sub(r"^[0-9a-f]{8}-", "", p.name)


def domain(w):
    w = (w or "").strip().lower()
    if not w:
        return ""
    if "//" not in w:
        w = "//" + w
    return urlparse(w).netloc.removeprefix("www.")


def base_name(n):
    return re.sub(r"\s*\(@[^)]*\)\s*$", "", n).strip().lower()


def fb_kind(v):
    v = v.strip()
    if v.startswith("http") and "profile.php?id=" in v: return "url-profile-id"
    if v.startswith("http"): return "url"
    if v.startswith("@"): return "handle"
    return "plain-name"


errors = hard = 0
rows_all, cats, kinds = [], {}, collections.Counter()
print(f"{'file':34}{'rows':>5}{'README':>7}{'no-site':>8}  fb kinds")
for f in files:
    raw = f.read_bytes()
    text = raw.decode("utf-8-sig")
    rows = [r for r in csv.DictReader(text.splitlines()) if any((v or "").strip() for v in r.values())]
    name = short(f)
    cats[name] = collections.Counter(r["Category"] for r in rows)
    nosite = sum(1 for r in rows if not (r["Website"] or "").strip())
    fk = collections.Counter(fb_kind(r["Facebook page"]) for r in rows if r["Facebook page"].strip())
    kinds.update(fk)
    print(f"{name:34}{len(rows):>5}{claimed.get(name, '-'):>7}{nosite:>8}  {dict(fk)}")
    for r in rows:
        r["_file"] = name
    rows_all += rows
    if raw.startswith(b"\xef\xbb\xbf"):
        print("   BOM present")

print("\n== Category strings per file (compare with keys in CATEGORY_NEGATIVE_FIREWALL) ==")
for n, c in cats.items():
    print(f"  {n:34} {list(c)}")

print("\n== Leading/trailing whitespace in fields ==")
ws = collections.Counter()
for r in rows_all:
    for k, v in r.items():
        if k != "_file" and v and v != v.strip():
            ws[(r["_file"], k)] += 1
for (fn, col), n in ws.items():
    print(f"  {fn}: column {col!r}: {n} rows")
if not ws: print("  none")

print("\n== Architecture_Mode distinct raw values ==")
print("  ", collections.Counter(r["Architecture_Mode"] for r in rows_all))

print("\n== Websites that contain a path, or look non-domain ==")
for r in rows_all:
    w = (r["Website"] or "").strip()
    if w and ("/" in w or " " in w or "." not in w):
        print(f"  {r['_file']}: {r['Name']!r} -> {w}")

print("\n== Same website domain used by more than one row ==")
by_dom = collections.defaultdict(list)
for r in rows_all:
    dm = domain(r["Website"])
    if dm: by_dom[dm].append(f"{r['Name'].strip()} [{r['_file'].removesuffix('.csv')}]")
for dm, v in by_dom.items():
    if len(v) > 1: print(f"  {dm}: {v}"); errors += 1

print("\n== Same store name in more than one row ==")
by_name = collections.defaultdict(list)
for r in rows_all:
    by_name[base_name(r["Name"])].append(r["_file"].removesuffix(".csv"))
for n, v in by_name.items():
    if len(v) > 1: print(f"  {n!r}: {v}"); errors += 1

print("\n== Same Facebook page in more than one row ==")
by_fb = collections.defaultdict(list)
for r in rows_all:
    k = r["Facebook page"].strip().lower().rstrip("/")
    if k: by_fb[k].append(f"{r['Name'].strip()} [{r['_file'].removesuffix('.csv')}]")
for k, v in by_fb.items():
    if len(v) > 1: print(f"  {k}: {v}")

print("\n== Facebook field kinds across all rows ==")
print("  ", dict(kinds))
unusable = [r for r in rows_all if fb_kind(r["Facebook page"]) == "plain-name" and not (r["Website"] or "").strip()]
print(f"\nRows with NO website and NO usable Facebook URL (nothing to crawl or link): {len(unusable)}")

print(f"\nTotal rows: {len(rows_all)}  (README claims {sum(claimed.values()) or '?'})")
sys.exit(1 if hard else 0)
