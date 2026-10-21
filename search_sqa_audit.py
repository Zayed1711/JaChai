import os
import re
import sys
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(".").resolve()
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

TAKA = "\u09f3"
REPORT = []
FAULTS = []

def log(msg=""):
    print(msg)
    REPORT.append(str(msg))

def add_fault(group, query, issue, actual, expected):
    FAULTS.append({
        "group": group,
        "query": query,
        "issue": issue,
        "actual": actual,
        "expected": expected
    })

log("=" * 112)
log(" JACHAI DEEP SEARCH, PRICE-REALISM & ROUTING SQA DIAGNOSTIC SUITE (v3.0)")
log("=" * 112)

# ==============================================================================
# PART 1: CODEBASE FORENSICS (LOCATE EXACT LINES FOR 2000 TAKA & SMARTWATCH BUGS)
# ==============================================================================
log("\n[PART 1] CODEBASE FORENSICS: Scanning backend/*.py for Fallback & Routing Traps...")
log("-" * 112)

py_files = [
    BACKEND / "main.py",
    BACKEND / "bd_stores_registry.py",
    BACKEND / "crawler.py",
    BACKEND / "predetermined_catalog.py",
    BACKEND / "translator.py",
    BACKEND / "adapters.py"
]

forensic_patterns = [
    ("Synthetic Title ('Official Bangladesh Edition')", r"Official Bangladesh Edition"),
    ("Hardcoded 2000 / 2650 Fallback Price", r"\b(2000|2650)\b"),
    ("Smartwatch Routing Keyword", r"smart\s*watch"),
    ("Unsplash / Living Room Fallback Image", r"images\.unsplash\.com/photo-[^\s\"\'\)]+"),
]

for pf in py_files:
    if not pf.exists():
        continue
    lines = pf.read_text(encoding="utf-8", errors="ignore").splitlines()
    for label, pat in forensic_patterns:
        matches = []
        for idx, line in enumerate(lines, 1):
            if re.search(pat, line, re.IGNORECASE):
                matches.append(f"L{idx}: {line.strip()[:95]}")
        if matches:
            log(f"  * [{pf.name}] -> {label} ({len(matches)} hit(s)):")
            for m in matches[:6]:
                log(f"      {m}")

# ==============================================================================
# PART 2: 50-QUERY LIVE SEARCH, CATEGORY ROUTING & PRICE-FLOOR AUDIT
# ==============================================================================
log("\n" + "=" * 112)
log("[PART 2] 50-QUERY SEARCH ENGINE, ROUTING & PRICE-FLOOR REALISM AUDIT")
log("=" * 112)

from fastapi.testclient import TestClient
import main as backend_main
from translator import translate_and_align_query
from bd_stores_registry import resolve_category_or_none

client = TestClient(backend_main.app)

# Format: (Group, Query, Expected_Category, Min_Realistic_Price_BDT, Max_Realistic_Price_BDT)
TEST_MATRIX = [
    # GROUP A: iPhones & Flagship Smartphones (Must NEVER be 2,000 BDT!)
    ("A. Smartphones", "iphone 14", "mobile-gadgets", 55000, 160000),
    ("A. Smartphones", "iphone 14 pro max", "mobile-gadgets", 75000, 220000),
    ("A. Smartphones", "iphone 13", "mobile-gadgets", 45000, 140000),
    ("A. Smartphones", "iphone 15", "mobile-gadgets", 65000, 180000),
    ("A. Smartphones", "iphone 15 pro max", "mobile-gadgets", 95000, 250000),
    ("A. Smartphones", "iphone 16", "mobile-gadgets", 80000, 220000),
    ("A. Smartphones", "iphone 12", "mobile-gadgets", 35000, 110000),
    ("A. Smartphones", "iphone 11", "mobile-gadgets", 25000, 85000),
    ("A. Smartphones", "samsung galaxy s24 ultra", "mobile-gadgets", 85000, 220000),
    ("A. Smartphones", "xiaomi redmi note 13", "mobile-gadgets", 15000, 45000),
    ("A. Smartphones", "google pixel 8 pro", "mobile-gadgets", 55000, 150000),

    # GROUP B: Mobile Accessories (Should be low-price, distinct from actual phones)
    ("B. Accessories", "iphone 14 back cover", "mobile-gadgets", 100, 5000),
    ("B. Accessories", "iphone 15 fast charger 20w", "mobile-gadgets", 500, 6000),
    ("B. Accessories", "airpods pro 2", "mobile-gadgets", 1500, 40000),
    ("B. Accessories", "anker power bank 20000mah", "mobile-gadgets", 1200, 12000),

    # GROUP C: Smartwatches & Wearables (MUST route to mobile-gadgets, NOT watches-horology!)
    ("C. Smartwatches", "smartwatch", "mobile-gadgets", 800, 120000),
    ("C. Smartwatches", "smart watch", "mobile-gadgets", 800, 120000),
    ("C. Smartwatches", "apple watch series 9", "mobile-gadgets", 25000, 95000),
    ("C. Smartwatches", "samsung galaxy watch 6", "mobile-gadgets", 15000, 65000),
    ("C. Smartwatches", "amazfit bip 5", "mobile-gadgets", 3000, 15000),
    ("C. Smartwatches", "haylou solar plus", "mobile-gadgets", 2000, 10000),
    ("C. Smartwatches", "colmi p71 smartwatch", "mobile-gadgets", 1000, 5000),
    ("C. Smartwatches", "kieslect kr pro", "mobile-gadgets", 2500, 12000),
    ("C. Smartwatches", "xiaomi mi band 8", "mobile-gadgets", 2000, 8000),

    # GROUP D: Traditional Analog / Mechanical Watches (MUST route to watches-horology)
    ("D. Analog Watches", "casio edifice chronograph", "watches-horology", 3000, 45000),
    ("D. Analog Watches", "seiko 5 automatic watch", "watches-horology", 8000, 65000),
    ("D. Analog Watches", "titan analog mens watch", "watches-horology", 2000, 35000),
    ("D. Analog Watches", "fossil leather chronograph watch", "watches-horology", 4000, 40000),

    # GROUP E: Laptops, PC Components & High-Ticket Electronics (Price Sanity Check)
    ("E. Laptops & PC", "macbook air m2", "laptops-pc", 85000, 220000),
    ("E. Laptops & PC", "hp pavilion 15 laptop", "laptops-pc", 45000, 140000),
    ("E. Laptops & PC", "asus tuf gaming laptop", "laptops-pc", 65000, 220000),
    ("E. Laptops & PC", "rtx 4060 graphics card", "laptops-pc", 32000, 75000),
    ("E. Laptops & PC", "samsung 980 pro 1tb ssd", "laptops-pc", 7000, 25000),
    ("E. Laptops & PC", "nzxt h510 pc case", "laptops-pc", 4000, 20000),
    ("E. Laptops & PC", "deepcool ak400 cpu cooler", "laptops-pc", 2000, 8000),

    # GROUP F: Cameras, Home Appliances, Cycles, EVs & Gold (High-Ticket Realism)
    ("F. High-Ticket", "canon eos 200d dslr camera", "cameras-photography", 35000, 120000),
    ("F. High-Ticket", "sony a6400 mirrorless body", "cameras-photography", 55000, 150000),
    ("F. High-Ticket", "walton wfc-3f5 refrigerator", "home-appliances", 25000, 95000),
    ("F. High-Ticket", "gree 1.5 ton inverter ac", "home-appliances", 45000, 120000),
    ("F. High-Ticket", "vision room air cooler", "home-appliances", 5000, 25000),
    ("F. High-Ticket", "duranta mtb gear cycle", "bicycles-mtb", 8000, 35000),
    ("F. High-Ticket", "walton takyon electric bike", "cycles-evs", 45000, 160000),
    ("F. High-Ticket", "22k gold chain necklace", "fine-jewelry", 25000, 350000),

    # GROUP G: Lifestyle, Fashion, Saree, Sportswear, Grocery & Beauty
    ("G. Lifestyle", "jamdani saree", "saree-boutiques", 1200, 50000),
    ("G. Lifestyle", "mens cotton panjabi", "fashion-apparel", 500, 8000),
    ("G. Lifestyle", "oxidised jhumka earrings", "fashion-jewelry", 100, 3000),
    ("G. Lifestyle", "nike air max running shoes", "sneakers-footwear", 1500, 25000),
    ("G. Lifestyle", "barca home kit jersey", "sportswear-gym", 400, 5000),
    ("G. Lifestyle", "rupchanda mustard oil 1 litre", "grocery-snacks", 150, 1000),
    ("G. Lifestyle", "khati gawa ghee", "grocery-snacks", 400, 3500),
    ("G. Lifestyle", "bridal facial kit", "beauty-skincare", 300, 8000),
]

log(f"  {'Group':<16} | {'Query':<27} | {'Cat Route':<19} | {'Min Price':<10} | {'Top Title':<30} | {'Result'}")
log("  " + "-" * 118)

passed_count = 0
for grp, q, exp_cat, min_ok, max_ok in TEST_MATRIX:
    rewritten = translate_and_align_query(q)
    got_cat, _ = resolve_category_or_none(rewritten)

    # Call actual /api/v1/search/live endpoint
    resp = client.get("/api/v1/search/live", params={"q": q})
    items = []
    if resp.status_code == 200:
        data = resp.json()
        items = data if isinstance(data, list) else (data.get("results") or data.get("products") or data.get("cards") or data.get("items") or [])

    if not items:
        log(f"  {grp:<16} | {q:<27} | {str(got_cat):<19} | {'0 items':<10} | {'NONE':<30} | FAIL (0 results)")
        add_fault(grp, q, "Returned 0 search results", "0 items", f">=1 item in {exp_cat}")
        continue

    first = items[0]
    title = str(first.get("name") or first.get("title") or first.get("product_name") or "Unknown")
    cat_in_card = str(first.get("category_slug") or first.get("category") or got_cat or "")
    img_url = str(first.get("image_url") or first.get("image") or "")

    # Extract lowest price shown on card
    lowest_price = first.get("lowest_price") or first.get("starting_price") or first.get("current_price") or first.get("price")
    if lowest_price is None and first.get("offers"):
        offer_prices = [o.get("current_price") or o.get("price") or 0 for o in first.get("offers", []) if isinstance(o, dict)]
        offer_prices = [p for p in offer_prices if p > 0]
        lowest_price = min(offer_prices) if offer_prices else 0
    lowest_price = float(lowest_price or 0)

    issues = []
    # Check 1: Category routing
    if got_cat != exp_cat:
        issues.append(f"Route:{got_cat}!=exp:{exp_cat}")
    # Check 2: Price realism
    if lowest_price < min_ok or lowest_price > max_ok:
        issues.append(f"Price:{TAKA}{lowest_price:,.0f} outside [{TAKA}{min_ok:,}-{TAKA}{max_ok:,}]")
    # Check 3: Synthetic "(Official Bangladesh Edition)" trap
    if "Official Bangladesh Edition" in title:
        issues.append("SyntheticFallbackTitle")
    # Check 4: Living room sofa image trap (photo-1586023492125 or generic interior)
    if "1586023492125" in img_url:
        issues.append("LivingRoomSofaImage")

    price_str = f"{TAKA}{lowest_price:,.0f}"
    if not issues:
        passed_count += 1
        log(f"  {grp:<16} | {q:<27} | {str(got_cat):<19} | {price_str:<10} | {title[:30]:<30} | PASS")
    else:
        issue_str = "; ".join(issues)
        log(f"  {grp:<16} | {q:<27} | {str(got_cat):<19} | {price_str:<10} | {title[:30]:<30} | FAIL -> {issue_str}")
        add_fault(grp, q, issue_str, f"Title='{title}', Price={price_str}, Cat={got_cat}, Img={img_url[:40]}", f"Cat={exp_cat}, Price={TAKA}{min_ok:,}-{TAKA}{max_ok:,}")

log("\n" + "=" * 112)
log(f" SEARCH SQA AUDIT SUMMARY: {passed_count}/{len(TEST_MATRIX)} Queries Passed ({len(FAULTS)} Faults Detected)")
log("=" * 112)

for idx, f in enumerate(FAULTS, 1):
    log(f"  {idx:02d}. [{f['group']}] Query: '{f['query']}'")
    log(f"      * Defect   : {f['issue']}")
    log(f"      * Actual   : {f['actual']}")
    log(f"      * Expected : {f['expected']}")

Path("search_sqa_report.txt").write_text("\n".join(REPORT), encoding="utf-8")
print("\n[SAVED] Full Search SQA Report -> E:\\JaChai\\search_sqa_report.txt")
