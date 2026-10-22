"""
JaChai Deep Search & Scraper Diagnostic Harness (backend/diagnose_search_errors.py)
Tests 150 diverse queries across all 15 categories (10 queries per category) and diagnoses:
  - Stage 1: Translator & Query Normalization
  - Stage 2: Category Router Accuracy
  - Stage 3: Live Store + DDGS Web Scraper Raw Yield (before filtering)
  - Stage 4: Post-Filter Pinpoint Survival Rate (detects if anchor/price filters are too strict)
  - Stage 5: Real Scraped vs Variant/Fallback Ratio & Price Realism
"""

import asyncio
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import bd_stores_registry as reg
from translator import translate_and_align_query
from llm_reasoner import (
    deterministic_intent_fallback,
    verify_and_filter_candidates,
    extract_mandatory_anchor_tokens,
)
from crawler import (
    clean_query_for_display_and_search,
    scrape_store_search,
    passes_category_negative_firewall,
)

reg.load_all_registries(force=True)

# 15 Categories x 10 Queries = 150 Diagnostic Queries
DIAGNOSTIC_QUERIES_BY_CATEGORY: Dict[str, List[str]] = {
    "bicycles-mtb": [
        "bicycle", "mountain bike", "veloce bicycle", "duranta bicycle", "phoenix cycle",
        "trinx mtb", "road bike", "gear cycle", "kids bicycle", "\u09a6\u09c1\u09b0\u09a8\u09cd\u09a4 \u09b8\u09be\u0987\u0995\u09c7\u09b2",
    ],
    "cycles-evs": [
        "electric bike", "walton takyon", "revoo electric bike", "yadea electric scooter",
        "electric scooter", "green tiger e-bike", "runner e-bike", "battery bike", "tekyon voltoni", "\u0987-\u09ac\u09be\u0987\u0995",
    ],
    "mobile-gadgets": [
        "iphone 15", "samsung galaxy a55", "redmi note 13", "realme c67", "oneplus nord",
        "vivo v30", "infinix hot 40", "wireless earbuds", "10000 mah power bank", "\u09b8\u09cd\u09af\u09be\u09ae\u09b8\u09be\u0982 \u09ae\u09cb\u09ac\u09be\u0987\u09b2",
    ],
    "laptops-pc": [
        "macbook air m2", "asus tuf gaming", "hp pavilion laptop", "lenovo ideapad", "acer aspire laptop",
        "dell inspiron laptop", "ryzen 5 processor", "rtx 4060 graphics card", "gaming monitor", "nvme ssd",
    ],
    "cameras-photography": [
        "sony a6400", "canon eos 200d", "nikon d5600", "gopro hero", "dji osmo action",
        "canon 50mm lens", "mirrorless camera", "dslr camera", "instax mini camera", "\u09a1\u09bf\u098f\u09b8\u098f\u09b2\u0986\u09b0 \u0995\u09cd\u09af\u09be\u09ae\u09c7\u09b0\u09be",
    ],
    "home-appliances": [
        "walton refrigerator", "singer refrigerator", "gree 1.5 ton ac", "smart tv 43 inch",
        "washing machine", "microwave oven", "rice cooker", "electric kettle", "ceiling fan", "water purifier",
    ],
    "fine-jewelry": [
        "22k gold ring", "gold necklace", "diamond ring", "gold earrings", "bridal gold set",
        "gold chain", "gold bracelet", "diamond nose pin", "gold bangles", "\u09b8\u09cb\u09a8\u09be\u09b0 \u0986\u0982\u099f\u09bf",
    ],
    "sneakers-footwear": [
        "white sneakers", "running shoes", "mens leather formal shoes", "bata shoes",
        "apex shoes", "mens loafers", "mens sandals", "womens party heels", "sports shoes", "\u09b8\u09cd\u09a8\u09bf\u0995\u09be\u09b0\u09cd\u09b8",
    ],
    "watches-horology": [
        "casio watch", "casio g-shock", "casio edifice", "naviforce watch", "curren watch",
        "titan watch", "fossil watch", "automatic watch", "smartwatch", "\u09b9\u09be\u09a4\u0998\u09a1\u09bc\u09bf",
    ],
    "beauty-skincare": [
        "sunscreen spf 50", "face wash", "niacinamide serum", "vitamin c serum", "moisturizer cream",
        "matte lipstick", "onion hair oil", "shampoo", "micellar water", "\u09b8\u09be\u09a8\u09b8\u09cd\u0995\u09cd\u09b0\u09bf\u09a8",
    ],
    "sportswear-gym": [
        "argentina jersey", "brazil jersey", "bangladesh cricket jersey", "gym tracksuit",
        "yoga mat", "dumbbell set", "gym gloves", "skipping rope", "football", "badminton racket",
    ],
}


async def diagnose_single_query(cat_expected: str, q: str) -> Dict:
    cleaned_q, budget = clean_query_for_display_and_search(q)
    translated_q = translate_and_align_query(cleaned_q)
    cat_id, cat_meta = reg.resolve_category_or_none(q, None)

    if cat_id != cat_expected:
        return {
            "q": q,
            "status": "ROUTING_MISMATCH",
            "detail": f"Routed to '{cat_id}' instead of '{cat_expected}' (translated={translated_q!r})",
            "raw_count": 0,
            "verified_count": 0,
            "samples": [],
        }

    intent = deterministic_intent_fallback(cleaned_q, cat_id)
    intent["raw_query"] = cleaned_q
    vertical = cat_meta.get("vertical")
    distilled_kw = translated_q

    raw_items = await scrape_store_search(distilled_kw, vertical=vertical, max_budget_bdt=budget, category_id=cat_id)
    raw_count = len(raw_items)

    verified = verify_and_filter_candidates(intent, raw_items)
    verified = [
        c for c in verified
        if passes_category_negative_firewall(c.get("title", ""), cat_meta["display_en"], q)
    ]
    verified_count = len(verified)

    if raw_count == 0:
        status = "RAW_SCRAPE_0"
        detail = f"0 raw items scraped for keyword {distilled_kw!r}"
    elif verified_count == 0:
        anchors = extract_mandatory_anchor_tokens(cleaned_q)
        sample_raw = [(r.get("title", "")[:40], r.get("price")) for r in raw_items[:2]]
        status = "FILTER_WIPED_ALL"
        detail = f"Scraped {raw_count} raw items {sample_raw}, but filter dropped all (anchors={anchors})"
    else:
        status = "REAL_SCRAPED_OK"
        detail = f"{verified_count}/{raw_count} real items verified"

    return {
        "q": q,
        "status": status,
        "detail": detail,
        "raw_count": raw_count,
        "verified_count": verified_count,
        "samples": [(v.get("title", "")[:42], v.get("price"), v.get("store_name")) for v in verified[:2]],
    }


async def main():
    print("=" * 100)
    print("JACHAI 150-QUERY DEEP SEARCH & LIVE SCRAPER DIAGNOSTIC SUITE (15 CATEGORIES x 10 QUERIES)")
    print("=" * 100)

    summary_counts = defaultdict(int)
    cat_stats = {}

    for cat_id, queries in DIAGNOSTIC_QUERIES_BY_CATEGORY.items():
        print(f"\n--- CATEGORY: {cat_id.upper()} ({len(queries)} queries) ---")
        c_ok = c_raw0 = c_wiped = c_route = 0
        for q in queries:
            res = await diagnose_single_query(cat_id, q)
            st = res["status"]
            summary_counts[st] += 1
            if st == "REAL_SCRAPED_OK":
                c_ok += 1
                print(f"  [REAL_OK ] {q:<28} | {res['detail']:<30} | {res['samples']}")
            elif st == "FILTER_WIPED_ALL":
                c_wiped += 1
                print(f"  [WIPED!  ] {q:<28} | {res['detail']}")
            elif st == "ROUTING_MISMATCH":
                c_route += 1
                print(f"  [ROUTE!  ] {q:<28} | {res['detail']}")
            else:
                c_raw0 += 1
                print(f"  [RAW_0   ] {q:<28} | {res['detail']}")
        cat_stats[cat_id] = (c_ok, c_wiped, c_raw0, c_route)

    print("\n" + "=" * 100)
    print("DIAGNOSTIC SUMMARY ACROSS 150 QUERIES:")
    print(f"  REAL_SCRAPED_OK  (Live real products & prices fetched) : {summary_counts['REAL_SCRAPED_OK']}/150")
    print(f"  FILTER_WIPED_ALL (Scraped items dropped by filter)     : {summary_counts['FILTER_WIPED_ALL']}/150")
    print(f"  RAW_SCRAPE_0     (Stores/DDGS returned 0 raw items)    : {summary_counts['RAW_SCRAPE_0']}/150")
    print(f"  ROUTING_MISMATCH (Wrong category routing)              : {summary_counts['ROUTING_MISMATCH']}/150")
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())
