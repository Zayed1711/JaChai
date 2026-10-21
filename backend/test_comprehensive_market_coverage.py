"""
JaChai Comprehensive 14-Category & Real-World Market Coverage Test Suite
(backend/test_comprehensive_market_coverage.py)

Tests 70+ real-world consumer queries across all 14 categories:
  1. Manual, Mountain (MTB), Aero & Road Bicycles (5,000 - 50,000 BDT price validation & bicycle store purity)
  2. Electric Bikes & E-Scooters (Walton Takyon, Reevo, Yadea - EV store purity)
  3. Smartphones & Mobile Gadgets (Brand New, Used/Reconditioned, Official/Unofficial, Accessories)
  4. Laptops, Desktops & PC Components (Brand New, Business, Gaming, Used/Reconditioned, GPU/RAM/SSD)
  5. Cameras, DSLR & Photography (New DSLR, Used DSLR, Mirrorless, Action Cam, Lenses)
  6. Home Appliances & Electronics (AC, Refrigerator, Smart TV, Washing Machine, Microwave, IPS)
  7. Mainstream Fashion & Apparel (Panjabi, Shirt, T-Shirt, Kurti, Three Piece, Abaya)
  8. Saree & Boutiques (Dhakai Jamdani, Katan, Benaroshi, Cotton Saree)
  9. Fine Jewelry & Gold (22K Gold Ring, Gold Necklace, Diamond)
  10. Fashion & Budget Imitation Jewelry (Jhumka, Choker, Oxidized Earrings, Bangles)
  11. Sneakers & Footwear (Running Shoes, Sneakers, Leather Formal Shoes, Sandals)
  12. Watches & Horology (Casio, G-Shock, Automatic Watch, Smartwatch)
  13. Beauty, Skincare & Cosmetics (Sunscreen, Face Wash, Serum, Moisturizer, Lipstick)
  14. Sportswear & Gym + Grocery & Snacks (Jersey, Yoga Mat, Dumbbells, Mustard Oil, Ghee, Honey, Rice)
"""

import asyncio
import os
import sys
import time
from typing import List, Tuple

sys.stdout.reconfigure(encoding="utf-8")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import SessionLocal
from crawler import live_meta_search_and_persist
import bd_stores_registry as reg

reg.load_all_registries(force=True)

# Format: (query, category_hint, expected_cat_substring, min_expected_bdt, max_expected_bdt, forbidden_store_substrings)
COMPREHENSIVE_TEST_MATRIX: List[Tuple[str, str, str, int, int, List[str]]] = [
    # --- 1A. MANUAL, AERO & MOUNTAIN BICYCLES (5,000 - 50,000 BDT) ---
    ("bicycle", None, "Cycles", 4500, 50000, ["star tech", "ryans", "revoo", "yadea", "tailg"]),
    ("manual bicycle", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("aero bike", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("mountain bike", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("duranta bicycle", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("veloce v200 mountain bike", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("phoenix gear cycle", None, "Cycles", 4500, 50000, ["star tech", "revoo", "yadea"]),
    ("trinx mtb cycle under 25000", None, "Cycles", 4500, 25000, ["star tech", "revoo"]),
    ("\u09b8\u09be\u0987\u0995\u09c7\u09b2", None, "Cycles", 4500, 50000, ["star tech", "ryans"]),  # সাইকেল

    # --- 1B. ELECTRIC BIKES & E-SCOOTERS (EV STORE PURITY) ---
    ("electric bike", None, "Cycles & EVs", 22000, 180000, ["star tech", "ryans", "duranta", "dream cycle"]),
    ("walton takyon", None, "Cycles & EVs", 22000, 180000, ["star tech", "duranta", "dream cycle"]),
    ("electric scooter", None, "Cycles & EVs", 22000, 180000, ["star tech", "duranta", "dream cycle"]),
    ("\u0987-\u09ac\u09be\u0987\u0995", None, "Cycles & EVs", 22000, 180000, ["star tech", "duranta"]),  # ই-বাইক

    # --- 2. SMARTPHONES & MOBILE GADGETS (NEW, USED, OFFICIAL, UNOFFICIAL, ACCESSORIES) ---
    ("Mobile Phone", None, "Mobiles & Gadgets", 12000, 250000, ["star tech"]),
    ("iPhone 15 Pro", None, "Mobiles & Gadgets", 20000, 250000, ["star tech"]),
    ("Samsung Galaxy S24 Ultra", None, "Mobiles & Gadgets", 20000, 250000, ["star tech"]),
    ("Redmi Note 13", None, "Mobiles & Gadgets", 10000, 80000, ["star tech"]),
    ("Samsung A55", None, "Mobiles & Gadgets", 15000, 95000, ["star tech"]),
    ("\u09ac\u09be\u099c\u09c7\u099f \u09e8\u09eb\u09e6\u09e6\u09e6 \u09ae\u09cb\u09ac\u09be\u0987\u09b2", None, "Mobiles & Gadgets", 5000, 25000, ["star tech"]),
    ("wireless earbuds", None, "Mobiles & Gadgets", 500, 50000, []),
    ("10000 mah power bank", None, "Mobiles & Gadgets", 500, 25000, []),
    ("iPhone 15 silicone case", None, "Mobiles & Gadgets", 200, 10000, []),

    # --- 3. LAPTOPS, DESKTOPS & PC COMPONENTS (BUSINESS, GAMING, NEW, USED, RECON) ---
    ("Laptop", None, "Laptops & PC", 20000, 350000, []),
    ("MacBook Air M2", None, "Laptops & PC", 35000, 300000, []),
    ("ASUS TUF Gaming F15", None, "Laptops & PC", 35000, 280000, []),
    ("HP EliteBook 840 G6", None, "Laptops & PC", 20000, 180000, []),
    ("gaming laptop under 85000", None, "Laptops & PC", 20000, 85000, []),
    ("laptop under 60000", None, "Laptops & PC", 15000, 60000, []),
    ("AMD Ryzen 5 5600G Processor", None, "Laptops & PC", 5000, 60000, []),
    ("RTX 4060 graphics card", None, "Laptops & PC", 20000, 150000, []),
    ("gaming monitor 144hz", None, "Laptops & PC", 8000, 120000, []),

    # --- 4. CAMERAS, DSLR & PHOTOGRAPHY (NEW, USED, LENSES, ACTION CAM) ---
    ("Camera", None, "Cameras & DSLR", 14000, 300000, []),
    ("DSLR Camera", None, "Cameras & DSLR", 14000, 300000, []),
    ("Sony A6400", None, "Cameras & DSLR", 25000, 250000, []),
    ("Canon EOS 200D", None, "Cameras & DSLR", 20000, 200000, []),
    ("GoPro Hero Action Camera", None, "Cameras & DSLR", 10000, 120000, []),
    ("\u09a1\u09bf\u098f\u09b8\u098f\u09b2\u0986\u09b0 \u0995\u09cd\u09af\u09be\u09ae\u09c7\u09b0\u09be", None, "Cameras & DSLR", 14000, 300000, []),

    # --- 5. HOME APPLIANCES & WHITE GOODS (NEW & RECONDITIONED) ---
    ("Refrigerator", None, "Home Appliances", 12000, 200000, []),
    ("Walton Refrigerator", None, "Home Appliances", 12000, 180000, []),
    ("inverter ac 1.5 ton", None, "Home Appliances", 18000, 180000, []),
    ("ac", None, "Home Appliances", 12000, 180000, []),
    ("smart tv 43 inch", None, "Home Appliances", 12000, 180000, []),
    ("washing machine", None, "Home Appliances", 12000, 180000, []),
    ("microwave oven", None, "Home Appliances", 5000, 80000, []),

    # --- 6. MAINSTREAM FASHION & APPAREL ---
    ("Panjabi", None, "Fashion & Apparel", 500, 25000, ["star tech", "ryans"]),
    ("panjabi 1500 taka", None, "Fashion & Apparel", 400, 1500, ["star tech"]),
    ("\u09b2\u09be\u09b2 \u09aa\u09be\u099e\u09cd\u099c\u09be\u09ac\u09bf", None, "Fashion & Apparel", 500, 25000, ["star tech"]),
    ("mens formal shirt", None, "Fashion & Apparel", 500, 15000, ["star tech"]),
    ("polo t-shirt", None, "Fashion & Apparel", 300, 10000, ["star tech"]),
    ("three piece salwar kameez", None, "Fashion & Apparel", 800, 25000, ["star tech"]),

    # --- 7. SAREE & BOUTIQUES ---
    ("Jamdani Saree", None, "Saree & Boutiques", 1500, 60000, ["star tech"]),
    ("cotton saree under 3000", None, "Saree & Boutiques", 800, 3000, ["star tech"]),
    ("katan saree", None, "Saree & Boutiques", 1500, 60000, ["star tech"]),
    ("\u099c\u09be\u09ae\u09a6\u09be\u09a8\u09bf \u09b6\u09be\u09a1\u09bc\u09bf", None, "Saree & Boutiques", 1500, 60000, ["star tech"]),

    # --- 8. FINE JEWELRY & GOLD + 9. FASHION / BUDGET JEWELRY ---
    ("gold necklace", None, "Fine Jewelry & Gold", 10000, 500000, ["star tech"]),
    ("22k gold ring", None, "Fine Jewelry & Gold", 10000, 500000, ["star tech"]),
    ("oxidized jhumka earrings", None, "Fashion & Budget Jewellery", 150, 6000, ["star tech"]),
    ("party choker necklace", None, "Fashion & Budget Jewellery", 200, 6000, ["star tech"]),

    # --- 10. SNEAKERS & FOOTWEAR + 11. WATCHES & HOROLOGY ---
    ("Sneakers", None, "Sneakers & Shoes", 800, 25000, ["star tech"]),
    ("nike running shoes", None, "Sneakers & Shoes", 1000, 30000, ["star tech"]),
    ("mens leather formal shoes", None, "Sneakers & Shoes", 1000, 25000, ["star tech"]),
    ("casio watch", None, "Watches & Horology", 1000, 120000, []),
    ("automatic mechanical watch", None, "Watches & Horology", 1200, 150000, []),

    # --- 12. BEAUTY & SKINCARE + 13. SPORTSWEAR & GYM + 14. GROCERY & SNACKS ---
    ("sunscreen", None, "Beauty & Skincare", 300, 10000, ["star tech"]),
    ("niacinamide face serum", None, "Beauty & Skincare", 300, 10000, ["star tech"]),
    ("yoga mat", None, "Sportswear & Gym", 400, 15000, ["star tech"]),
    ("argentina football jersey", None, "Sportswear & Gym", 400, 10000, ["star tech"]),
    ("ghee", None, "Grocery & Snacks", 150, 6000, ["star tech"]),
    ("\u09b8\u09b0\u09bf\u09b7\u09be\u09b0 \u09a4\u09c7\u09b2", None, "Grocery & Snacks", 60, 5000, ["star tech"]),
    ("sundarban natural honey", None, "Grocery & Snacks", 200, 6000, ["star tech"]),
]


async def run_comprehensive_audit():
    db = SessionLocal()
    passed = 0
    failed = 0
    failures = []
    t0 = time.perf_counter()

    print("=" * 95)
    print(f"JACHAI COMPREHENSIVE 14-CATEGORY MARKET COVERAGE AUDIT ({len(COMPREHENSIVE_TEST_MATRIX)} REAL-WORLD QUERIES)")
    print("=" * 95)

    for idx, (q, hint, exp_cat, min_p, max_p, forbidden_stores) in enumerate(COMPREHENSIVE_TEST_MATRIX, 1):
        q_start = time.perf_counter()
        prods = await live_meta_search_and_persist(q, hint, db)
        ms = int((time.perf_counter() - q_start) * 1000)

        errs = []
        if not prods:
            errs.append("0 products returned")
        else:
            for p in prods[:5]:
                if exp_cat.lower() not in (p.category or "").lower():
                    errs.append(f"Category mismatch: got '{p.category}', expected '{exp_cat}'")
                if not p.offers:
                    errs.append(f"Product '{p.title_en}' has 0 store offers")
                for o in p.offers:
                    if o.current_price < min_p or o.current_price > max_p:
                        errs.append(f"Price {o.current_price} out of bounds [{min_p}..{max_p}] on '{p.title_en}' ({o.store_name})")
                    if not (o.target_url or "").startswith("http"):
                        errs.append(f"Invalid target_url '{o.target_url}' on {o.store_name}")
                    s_low = (o.store_name or "").lower()
                    for bad_s in forbidden_stores:
                        if bad_s in s_low:
                            errs.append(f"Forbidden store '{o.store_name}' appeared on '{q}'")

        if errs:
            failed += 1
            first_err = errs[0]
            failures.append((q, first_err))
            print(f"[{idx:02d}/{len(COMPREHENSIVE_TEST_MATRIX)}] FAIL | {q:<34} | {ms:4d}ms | {first_err}")
        else:
            passed += 1
            sample_low = min((o.current_price for o in prods[0].offers), default=0)
            sample_stores = [o.store_name for o in prods[0].offers[:2]]
            print(f"[{idx:02d}/{len(COMPREHENSIVE_TEST_MATRIX)}] PASS | {q:<34} | {len(prods)} boxes | Low: BDT {sample_low:>7,} | {sample_stores}")

    total_s = round(time.perf_counter() - t0, 2)
    db.close()

    print("=" * 95)
    print(f"SUMMARY: {passed}/{len(COMPREHENSIVE_TEST_MATRIX)} PASSED | {failed} FAILED | Total Time: {total_s}s")
    if failures:
        print("\nFailed Queries Detail:")
        for fq, ferr in failures:
            print(f"  - {fq!r}: {ferr}")
    print("=" * 95)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(run_comprehensive_audit()))
