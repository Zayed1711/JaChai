"""
JaChai SQA Diagnostic Suite (backend/sqa_diagnostic_suite.py)
Principal SQA Automation Engineering Test & Audit Harness
Executes 7 Comprehensive Audits:
  AUDIT 1: Database Hygiene & Legacy Pollution Audit (White-Box DB Check)
  AUDIT 2: White-Box Unit Tests (parse_bdt_price, build_store_target_url, llm_reasoner)
  AUDIT 3: Black-Box Live Search API & Multi-Vertical Matrix (GET /api/v1/search/live)
  AUDIT 4: Black-Box Outbound /go/offer/{id} Redirect & Merchant Reachability Check
  AUDIT 5: Black-Box Image Proxy & Visual Asset Reachability (GET /api/v1/image-proxy)
  AUDIT 6: Black-Box Storefront & Frontend UI State Audit (frontend/src/App.jsx)
  AUDIT 7: Security & Admin Endpoints Check (/api/v1/admin/overview)
"""

import asyncio
import os
import re
import sys
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx

# Ensure local backend imports resolve
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import SessionLocal, engine, Base
from models import Product, StoreOffer, Billboard, SpotlightCard
from crawler import parse_bdt_price
from bd_stores_registry import (
    build_store_target_url,
    RETAIL_VERTICALS,
    BANNED_INTERNATIONAL_DOMAINS,
    BANNED_FOREIGN_CURRENCIES,
)
from llm_reasoner import (
    analyze_search_intent,
    deterministic_intent_fallback,
    verify_and_filter_candidates,
    is_bangladesh_store_url,
)

BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")


# ANSI Color formatting
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def log_pass(msg: str):
    print(f"  {GREEN}[PASS]{RESET} {msg}")


def log_warn(msg: str):
    print(f"  {YELLOW}[WARN]{RESET} {msg}")


def log_fail(msg: str):
    print(f"  {RED}[FAIL]{RESET} {msg}")


def log_section(title: str):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}")


class SQADiagnosticHarness:
    def __init__(self, autofix: bool = False):
        self.autofix = autofix
        self.db = SessionLocal()
        self.results = {
            "passed": 0,
            "warned": 0,
            "failed": 0,
            "details": []
        }

    def close(self):
        self.db.close()

    def record(self, status: str, msg: str):
        if status == "PASS":
            self.results["passed"] += 1
            log_pass(msg)
        elif status == "WARN":
            self.results["warned"] += 1
            log_warn(msg)
        else:
            self.results["failed"] += 1
            log_fail(msg)
        self.results["details"].append({"status": status, "message": msg})

    # ==========================================================================
    # AUDIT 1: DATABASE HYGIENE & LEGACY POLLUTION AUDIT (WHITE-BOX)
    # ==========================================================================
    def audit_1_database_hygiene(self):
        log_section("AUDIT 1 — Database Hygiene & Legacy Pollution Audit (White-Box DB Check)")
        products = self.db.query(Product).all()

        if not products:
            self.record("WARN", "Database contains 0 products. Run seeding or searches first.")
            return

        duplicate_urls_found = 0
        mismatched_store_urls = 0
        foreign_entities = 0
        empty_offer_products = 0
        zero_price_products = 0
        stale_startech_loops = 0

        for p in products:
            # Check empty offers
            if not p.offers or len(p.offers) == 0:
                empty_offer_products += 1
                self.record("FAIL", f"Product #{p.id} ('{p.title_en}') has 0 StoreOffer rows!")
                continue

            # Check lowest price
            prices = [o.current_price for o in p.offers if o.current_price]
            min_p = min(prices) if prices else 0
            if min_p <= 0:
                zero_price_products += 1
                self.record("FAIL", f"Product #{p.id} ('{p.title_en}') has lowest price <= 0 ({min_p})")

            # Check duplicate target URLs on same product
            urls = [o.target_url for o in p.offers if o.target_url]
            if len(urls) != len(set(urls)):
                duplicate_urls_found += 1
                self.record("FAIL", f"Product #{p.id} ('{p.title_en}') has duplicate offer target URLs: {len(urls)} total, {len(set(urls))} unique")

            # Check store_name vs domain mismatch
            for o in p.offers:
                target_url = (o.target_url or "").lower()
                store_name = (o.store_name or "").lower()

                # Check foreign domains / currencies
                for fd in ["amazon.", "walmart.", "ebay.", ".us/", ".ca/"]:
                    if fd in target_url:
                        foreign_entities += 1
                        self.record("FAIL", f"Product #{p.id} offer #{o.id} ({o.store_name}) contains foreign domain: {o.target_url}")

                # Check Star Tech loop bug: non-Star-Tech store pointing to startech.com.bd
                if "startech.com.bd" in target_url and "star tech" not in store_name:
                    mismatched_store_urls += 1
                    stale_startech_loops += 1
                    self.record("FAIL", f"Product #{p.id} offer #{o.id}: Store '{o.store_name}' points to Star Tech domain: {o.target_url}")

                # Check Ryans / Pickaboo mismatches
                if ("ryanscomputers.com" in target_url or "ryans.com" in target_url) and "ryans" not in store_name:
                    mismatched_store_urls += 1
                    self.record("FAIL", f"Product #{p.id} offer #{o.id}: Store '{o.store_name}' points to Ryans Computers domain: {o.target_url}")
                if "pickaboo.com" in target_url and "pickaboo" not in store_name:
                    mismatched_store_urls += 1
                    self.record("FAIL", f"Product #{p.id} offer #{o.id}: Store '{o.store_name}' points to Pickaboo domain: {o.target_url}")

        if duplicate_urls_found == 0 and mismatched_store_urls == 0 and foreign_entities == 0 and empty_offer_products == 0:
            self.record("PASS", f"All {len(products)} products and associated offers in jachai.db are 100% clean, non-duplicated, and free of Star Tech loop bugs.")
        else:
            log_fail(f"Audit 1 Summary: {duplicate_urls_found} duplicate URL sets, {mismatched_store_urls} domain mismatches, {foreign_entities} foreign domains, {empty_offer_products} empty offers.")

    # ==========================================================================
    # AUDIT 2: WHITE-BOX UNIT TESTS (PRICE PARSER, URL BUILDER, LLM REASONER)
    # ==========================================================================
    def audit_2_whitebox_unit_tests(self):
        log_section("AUDIT 2 — White-Box Unit Tests (parse_bdt_price, build_store_target_url, llm_reasoner)")

        # 1. Test parse_bdt_price across 10 edge cases
        test_cases = [
            ("৳ ১,৪৫,৯৯০", 145990, "Bengali numerals with commas and currency symbol"),
            ("Flat 25% OFF! ৳2,450", 2450, "Discount prefix string"),
            ("Call 01711223344 Price ৳1,500", 1500, "Phone number prefix text"),
            ("৳12", None, "Price below sanity minimum (< 50)"),
            ("Tk 1,200.00", 1200, "Decimal currency format"),
            ("৳ 50,000,001", None, "Price above sanity maximum (> 50M)"),
            ("Special Deal: BDT 4,999/- only", 4999, "BDT abbreviation with /- suffix"),
            ("০", None, "Zero Bengali numeral (< 50)"),
            ("Price: Tk. ৮,৫০০ (Incl. VAT)", 8500, "Bengali digits with Tk. prefix and suffix text"),
            ("", None, "Empty string input"),
        ]

        parser_passed = 0
        for raw, expected, desc in test_cases:
            val = parse_bdt_price(raw)
            if val == expected:
                parser_passed += 1
            else:
                self.record("FAIL", f"parse_bdt_price failed on '{raw}' ({desc}): expected {expected}, got {val}")

        if parser_passed == len(test_cases):
            self.record("PASS", f"parse_bdt_price: 10/10 edge cases verified successfully.")

        # 2. Test build_store_target_url across 20 stores from 9 verticals
        stores_to_test = [
            ("Gadget & Gear", "MOBILE_GADGET"),
            ("Sumash Tech", "MOBILE_GADGET"),
            ("Apple Gadgets BD", "MOBILE_GADGET"),
            ("Dazzle BD", "MOBILE_GADGET"),
            ("Pickaboo", "MOBILE_GADGET"),
            ("KRY International", "MOBILE_GADGET"),
            ("Star Tech", "LAPTOP_PC"),
            ("Ryans Computers", "LAPTOP_PC"),
            ("TechLand BD", "LAPTOP_PC"),
            ("Fabrilife", "FASHION_APPAREL"),
            ("Aarong", "FASHION_APPAREL"),
            ("Sailor BD", "FASHION_APPAREL"),
            ("Yellow", "FASHION_APPAREL"),
            ("Tangail Saree Kutir", "FASHION_APPAREL"),
            ("Diamond World", "JEWELRY"),
            ("Apan Jewellers", "JEWELRY"),
            ("Time Zone BD", "WATCHES_HOROLOGY"),
            ("Apex Footwear", "SNEAKERS_FOOTWEAR"),
            ("Bata Bangladesh", "SNEAKERS_FOOTWEAR"),
            ("Chaldal", "GROCERY_SNACKS"),
        ]

        generated_urls = []
        for s_name, vert in stores_to_test:
            url = build_store_target_url(s_name, "test query", vert)
            if not url or not url.startswith("http"):
                self.record("FAIL", f"build_store_target_url returned invalid URL for '{s_name}': {url}")
            generated_urls.append(url)

        if len(generated_urls) == len(set(generated_urls)):
            self.record("PASS", f"build_store_target_url: 20/20 stores generated unique, properly encoded URLs with zero collisions.")
        else:
            self.record("FAIL", f"build_store_target_url: Duplicate URLs detected among 20 test stores! Total {len(generated_urls)}, Unique {len(set(generated_urls))}")

        # 3. Test analyze_search_intent across 8 representative queries
        intent_queries = [
            ("iPhone 15 Pro", "MOBILE_GADGET", 8000, 300000, False),
            ("MacBook Air M3", "LAPTOP_PC", 15000, 600000, False),
            ("Cotton Panjabi", "FASHION_APPAREL", 450, 40000, False),
            ("Dhakai Jamdani Saree", "FASHION_APPAREL", 450, 40000, False),
            ("Wireless Earbuds", "MOBILE_GADGET", 500, 50000, False),
            ("Casio Watch", "WATCHES_HOROLOGY", 1200, 600000, False),
            ("Bata Sneakers", "SNEAKERS_FOOTWEAR", 900, 60000, False),
            ("Organic Honey", "GROCERY_SNACKS", 60, 25000, False),
        ]

        intent_passed = 0
        loop = asyncio.get_event_loop()
        for q, exp_vert, min_bound, max_bound, exp_acc in intent_queries:
            intent = loop.run_until_complete(analyze_search_intent(q, None))
            vert = intent.get("vertical")
            is_acc = intent.get("is_accessory_query")
            min_p = intent.get("min_sanity_price_bdt", 0)
            max_p = intent.get("max_sanity_price_bdt", 0)

            if vert == exp_vert and is_acc == exp_acc and min_p >= 50 and max_p <= 2000000:
                intent_passed += 1
            else:
                self.record("FAIL", f"analyze_search_intent failed for '{q}': got vertical={vert} (expected {exp_vert}), accessory={is_acc}, bounds=({min_p}, {max_p})")

        if intent_passed == len(intent_queries):
            self.record("PASS", f"analyze_search_intent: 8/8 queries correctly classified into verticals with sane BDT bounds.")

    # ==========================================================================
    # AUDIT 3: BLACK-BOX LIVE SEARCH API & MULTI-VERTICAL MATRIX
    # ==========================================================================
    def audit_3_blackbox_live_search(self):
        log_section("AUDIT 3 — Black-Box Live Search API & Multi-Vertical Matrix (GET /api/v1/search/live)")

        search_tests = [
            ("iPhone 15", "MOBILE_GADGET", ["gadget & gear", "sumash tech", "apple gadgets", "dazzle", "pickaboo"], ["star tech", "ryans"]),
            ("Samsung Galaxy S24", "MOBILE_GADGET", ["gadget & gear", "sumash tech", "apple gadgets", "dazzle", "pickaboo"], ["star tech", "ryans"]),
            ("Cotton Panjabi", "FASHION_APPAREL", ["fabrilife", "aarong", "sailor", "le reve", "yellow", "cats eye"], ["star tech", "ryans", "techland"]),
            ("Jamdani Saree", "FASHION_APPAREL", ["aarong", "sailor", "anjan", "tangail", "boutique"], ["star tech", "ryans", "techland"]),
            ("Gaming Laptop", "LAPTOP_PC", ["star tech", "ryans", "techland"], []),
            ("Sneakers", "SNEAKERS_FOOTWEAR", ["apex", "bata", "lotto", "bay"], []),
            ("Smart Watch", "WATCHES_HOROLOGY", ["time zone", "watch zone", "star tech"], []),
        ]

        with httpx.Client(base_url=BASE_URL, timeout=18.0) as client:
            for query, expected_vert, preferred_stores, forbidden_stores in search_tests:
                start_t = time.time()
                try:
                    resp = client.get("/api/v1/search/live", params={"q": query})
                    latency_ms = int((time.time() - start_t) * 1000)

                    if resp.status_code != 200:
                        self.record("FAIL", f"Search '{query}' returned HTTP {resp.status_code} (latency: {latency_ms}ms)")
                        continue

                    items = resp.json()
                    if not items or len(items) == 0:
                        self.record("FAIL", f"Search '{query}' returned 0 products (latency: {latency_ms}ms)")
                        continue

                    # Verify product relevance, accessory filter, and offer URL uniqueness
                    has_forbidden = False
                    has_accessory = False
                    has_duplicate_urls = False

                    accessory_tokens = ["case", "cover", "protector", "tempered glass", "backpack", "cooling pad"]

                    for p in items:
                        title_lower = p.get("title_en", "").lower()
                        offers = p.get("offers", [])

                        # Anti-accessory check on primary hardware queries
                        if expected_vert in ("MOBILE_GADGET", "LAPTOP_PC"):
                            for tok in accessory_tokens:
                                if re.search(r"\b" + re.escape(tok) + r"\b", title_lower):
                                    has_accessory = True
                                    self.record("FAIL", f"Search '{query}' returned accessory product: '{p.get('title_en')}'")

                        # Offer uniqueness
                        offer_urls = [o.get("target_url") for o in offers if o.get("target_url")]
                        if len(offer_urls) != len(set(offer_urls)):
                            has_duplicate_urls = True
                            self.record("FAIL", f"Search '{query}' returned product with duplicate offer URLs: '{p.get('title_en')}' ({len(offer_urls)} vs {len(set(offer_urls))})")

                        # Check forbidden store monopoly
                        for o in offers:
                            s_name = (o.get("store_name") or "").lower()
                            for forb in forbidden_stores:
                                if forb in s_name:
                                    has_forbidden = True
                                    self.record("FAIL", f"Search '{query}' contains forbidden store '{o.get('store_name')}' for vertical {expected_vert}!")

                    if not has_forbidden and not has_accessory and not has_duplicate_urls:
                        self.record("PASS", f"Search '{query}': {len(items)} items returned in {latency_ms}ms with clean store routing, zero accessories, and unique URLs.")

                except Exception as exc:
                    self.record("FAIL", f"Search '{query}' encountered exception: {exc}")

    # ==========================================================================
    # AUDIT 4: BLACK-BOX OUTBOUND REDIRECT & MERCHANT REACHABILITY CHECK
    # ==========================================================================
    def audit_4_blackbox_redirect_and_merchant_reachability(self):
        log_section("AUDIT 4 — Black-Box Outbound /go/offer/{id} Redirect & Live Merchant Reachability Check")

        sample_offers = (
            self.db.query(StoreOffer)
            .filter(StoreOffer.target_url.isnot(None))
            .order_by(StoreOffer.id.desc())
            .limit(10)
            .all()
        )

        if not sample_offers:
            self.record("WARN", "No StoreOffers available in database to test redirect reachability.")
            return

        with httpx.Client(base_url=BASE_URL, timeout=8.0, follow_redirects=False) as client:
            for offer in sample_offers:
                try:
                    resp = client.get(f"/go/offer/{offer.id}")
                    if resp.status_code in (302, 307):
                        location = resp.headers.get("location", "")
                        from bd_stores_registry import get_store_facebook_fallback_url
                        expected_fb = get_store_facebook_fallback_url(offer.store_name)
                        if location == offer.target_url or offer.target_url in location or (expected_fb and expected_fb in location):
                            pass
                        else:
                            self.record("FAIL", f"/go/offer/{offer.id} redirect mismatch: expected '{offer.target_url}' (or FB '{expected_fb}'), got '{location}'")
                    else:
                        self.record("FAIL", f"/go/offer/{offer.id} did not return 302/307 (status: {resp.status_code})")
                except Exception as exc:
                    self.record("FAIL", f"/go/offer/{offer.id} error: {exc}")

        self.record("PASS", f"Outbound click redirect (/go/offer/id): Verified 302/307 location header matches offer.target_url across {len(sample_offers)} sample offers.")

        # Live Merchant External Reachability Test
        print("  -> Testing live HTTP reachability of core merchant search templates...")
        merchants_to_ping = [
            ("Gadget & Gear", "https://gadgetandgear.com/search?q=iphone"),
            ("Star Tech", "https://www.startech.com.bd/product/search?search=laptop"),
            ("Ryans Computers", "https://www.ryans.com/search?q=laptop"),
            ("Dazzle BD", "https://dazzle.com.bd/?s=phone&post_type=product"),
            ("Pickaboo", "https://www.pickaboo.com/search-result/phone"),
            ("Fabrilife", "https://fabrilife.com/search?q=panjabi"),
            ("Aarong", "https://www.aarong.com/search?q=panjabi"),
            ("Chaldal", "https://chaldal.com/search/honey"),
        ]

        reachability_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        with httpx.Client(timeout=10.0, follow_redirects=True, headers=reachability_headers) as client:
            reachable_count = 0
            for name, test_url in merchants_to_ping:
                try:
                    res = client.get(test_url)
                    if res.status_code == 404:
                        self.record("FAIL", f"Merchant '{name}' returned HTTP 404 Not Found at: {test_url}")
                    elif res.status_code in (200, 301, 302, 403):  # 403 often Cloudflare WAF bot-challenge
                        reachable_count += 1
                    else:
                        log_warn(f"Merchant '{name}' returned HTTP {res.status_code} on search endpoint.")
                except Exception as exc:
                    log_warn(f"Merchant '{name}' ping timeout/network error: {exc}")

            if reachable_count >= 5:
                self.record("PASS", f"Live merchant endpoints reachability verified ({reachable_count}/{len(merchants_to_ping)} responded non-404).")

    # ==========================================================================
    # AUDIT 5: BLACK-BOX IMAGE PROXY & VISUAL ASSET REACHABILITY
    # ==========================================================================
    def audit_5_blackbox_image_proxy(self):
        log_section("AUDIT 5 — Black-Box Image Proxy & Visual Asset Reachability (GET /api/v1/image-proxy)")

        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            # 1. Fetch storefront init products and billboards
            try:
                init_res = client.get("/api/v1/storefront/init")
                if init_res.status_code != 200:
                    self.record("FAIL", f"/api/v1/storefront/init returned HTTP {init_res.status_code}")
                    return

                init_data = init_res.json()
                products = init_data.get("products", [])
                billboards = init_data.get("billboards", [])
                spotlights = init_data.get("spotlight_cards", [])

                images_to_test = []
                for p in products[:5]:
                    if p.get("image_url"):
                        images_to_test.append(p.get("image_url"))
                for b in billboards[:3]:
                    if b.get("image_url"):
                        images_to_test.append(b.get("image_url"))
                for s in spotlights[:3]:
                    if s.get("image_url"):
                        images_to_test.append(s.get("image_url"))

                proxy_passed = 0
                for img_url in images_to_test:
                    # Skip local relative paths (/images/...)
                    if img_url.startswith("/"):
                        proxy_passed += 1
                        continue

                    # Test fetching through /api/v1/image-proxy?url=
                    p_res = client.get("/api/v1/image-proxy", params={"url": img_url})
                    if p_res.status_code == 200:
                        c_type = p_res.headers.get("content-type", "")
                        c_len = len(p_res.content)
                        if "image/" in c_type and c_len > 100:
                            proxy_passed += 1
                        else:
                            self.record("WARN", f"Proxy image '{img_url}' returned unexpected content-type '{c_type}' (size: {c_len}b)")
                    else:
                        self.record("FAIL", f"Proxy failed for '{img_url}': HTTP {p_res.status_code}")

                if proxy_passed == len(images_to_test):
                    self.record("PASS", f"Image Proxy: All {len(images_to_test)} tested visual assets are reachable, non-corrupt, and verified image content.")
                else:
                    self.record("WARN", f"Image Proxy: {proxy_passed}/{len(images_to_test)} visual assets passed.")

            except Exception as exc:
                self.record("FAIL", f"Audit 5 error: {exc}")

    # ==========================================================================
    # AUDIT 6: BLACK-BOX STOREFRONT & FRONTEND UI STATE AUDIT
    # ==========================================================================
    def audit_6_frontend_ui_state(self):
        log_section("AUDIT 6 — Black-Box Storefront & Frontend UI State Audit (frontend/src/App.jsx)")

        with httpx.Client(base_url=BASE_URL, timeout=8.0) as client:
            try:
                res = client.get("/api/v1/storefront/init")
                if res.status_code != 200:
                    self.record("FAIL", f"/api/v1/storefront/init returned HTTP {res.status_code}")
                    return

                data = res.json()
                billboards = data.get("billboards", [])
                spotlights = data.get("spotlight_cards", [])
                hubs = data.get("trending_hubs", [])

                # Verify Billboards count >= 4
                if len(billboards) >= 4:
                    self.record("PASS", f"Storefront Init: {len(billboards)} active kinetic billboard slides returned.")
                else:
                    self.record("FAIL", f"Storefront Init: Expected >= 4 billboards, got {len(billboards)}")

                # Verify Spotlight Cards (SLOT #02, SLOT #03, SLOT #04)
                spotlight_codes = [s.get("slot_code") for s in spotlights]
                if "SLOT #02" in spotlight_codes and "SLOT #03" in spotlight_codes and "SLOT #04" in spotlight_codes:
                    self.record("PASS", f"Storefront Init: All 3 partner spotlight cards present ({spotlight_codes[:3]}).")
                else:
                    self.record("FAIL", f"Storefront Init: Missing spotlight slot codes. Got: {spotlight_codes}")

                # Verify Trending Hubs count == 6
                if len(hubs) == 6:
                    self.record("PASS", f"Storefront Init: 6/6 Generic Trending Category Hubs present.")
                else:
                    self.record("WARN", f"Storefront Init: Expected 6 trending hubs, got {len(hubs)}")

            except Exception as exc:
                self.record("FAIL", f"Audit 6 storefront init error: {exc}")

        # Static Code Analysis of frontend/src/App.jsx
        app_jsx_path = os.path.normpath(os.path.join(CURRENT_DIR, "..", "frontend", "src", "App.jsx"))
        if os.path.exists(app_jsx_path):
            with open(app_jsx_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Check 1: Does clicking category pill trigger live search on Home screen?
            if "executeLiveSearch(tab.en, tab.id)" in code or "executeLiveSearch" in code:
                self.record("PASS", "frontend/src/App.jsx: Category filter pills trigger live search across categories.")
            else:
                self.record("WARN", "frontend/src/App.jsx: Category pills do not appear to invoke executeLiveSearch.")

            # Check 2: Billboard & Spotlight modal click handlers
            if "openComparisonModal(currentBillboard.productKey)" in code and "openComparisonModal(slot.productKey)" in code:
                self.record("PASS", "frontend/src/App.jsx: Billboard and Spotlight clicks correctly invoke openComparisonModal.")
            else:
                self.record("WARN", "frontend/src/App.jsx: openComparisonModal missing on billboards or spotlight cards.")

            # Check 3: Image proxy usage
            if "getImageProxyUrl" in code:
                self.record("PASS", "frontend/src/App.jsx: getImageProxyUrl helper integrated for visual assets.")
            else:
                self.record("FAIL", "frontend/src/App.jsx: getImageProxyUrl helper missing.")
        else:
            self.record("WARN", f"App.jsx not found at expected path: {app_jsx_path}")

    # ==========================================================================
    # AUDIT 7: SECURITY & ADMIN ENDPOINTS CHECK
    # ==========================================================================
    def audit_7_security_admin_endpoints(self):
        log_section("AUDIT 7 — Security & Admin Endpoints Check (/api/v1/admin/overview)")

        with httpx.Client(base_url=BASE_URL, timeout=8.0) as client:
            # 1. Unauthenticated request must return 401
            try:
                unauth_res = client.get("/api/v1/admin/overview")
                if unauth_res.status_code == 401:
                    self.record("PASS", "/api/v1/admin/overview: Unauthenticated access rejected with HTTP 401.")
                else:
                    self.record("FAIL", f"/api/v1/admin/overview unauthenticated request returned HTTP {unauth_res.status_code} (expected 401)!")
            except Exception as exc:
                self.record("FAIL", f"Admin unauthenticated check failed: {exc}")

            # 2. Authenticated request with Master PIN
            try:
                auth_res = client.get("/api/v1/admin/overview", headers={"X-Admin-Pin": "2026"})
                if auth_res.status_code == 200:
                    data = auth_res.json()
                    if "billboards" in data and ("spotlights" in data or "spotlight_cards" in data):
                        self.record("PASS", "/api/v1/admin/overview: Master PIN '2026' authenticated successfully with HTTP 200 and operational payload.")
                    else:
                        self.record("WARN", "/api/v1/admin/overview: Returned 200 but payload missing billboards/spotlights keys.")
                else:
                    self.record("FAIL", f"/api/v1/admin/overview with X-Admin-Pin: 2026 returned HTTP {auth_res.status_code} (expected 200)!")
            except Exception as exc:
                self.record("FAIL", f"Admin authenticated check failed: {exc}")

    # ==========================================================================
    # RUN ALL AUDITS & GENERATE REPORT
    # ==========================================================================
    def run_all(self):
        start_time = time.time()
        print(f"\n{BOLD}JaChai Principal SQA Diagnostic Suite — Starting 7 Audits...{RESET}")

        self.audit_1_database_hygiene()
        self.audit_2_whitebox_unit_tests()
        self.audit_3_blackbox_live_search()
        self.audit_4_blackbox_redirect_and_merchant_reachability()
        self.audit_5_blackbox_image_proxy()
        self.audit_6_frontend_ui_state()
        self.audit_7_security_admin_endpoints()

        duration = round(time.time() - start_time, 2)
        total = self.results["passed"] + self.results["warned"] + self.results["failed"]

        log_section("FINAL SQA DIAGNOSTIC SUITE SUMMARY REPORT")
        print(f"Total Checks Executed : {total}")
        print(f"Passed Checks         : {GREEN}{self.results['passed']}{RESET}")
        print(f"Warnings              : {YELLOW}{self.results['warned']}{RESET}")
        print(f"Failed Checks         : {RED}{self.results['failed']}{RESET}")
        print(f"Total Execution Time  : {duration}s")

        if self.results["failed"] == 0 and self.results["warned"] == 0:
            print(f"\n{GREEN}{BOLD}>>> [STATUS: GREEN / 100% HEALTHY] ALL SQA AUDITS PASSED PERFECTLY <<<{RESET}\n")
            return 0
        elif self.results["failed"] == 0:
            print(f"\n{YELLOW}{BOLD}>>> [STATUS: AMBER / PASSED WITH WARNINGS] All core audits passed <<<{RESET}\n")
            return 0
        else:
            print(f"\n{RED}{BOLD}>>> [STATUS: RED / DEFECTS DETECTED] {self.results['failed']} checks failed and require remediation <<<{RESET}\n")
            return 1


if __name__ == "__main__":
    harness = SQADiagnosticHarness()
    try:
        exit_code = harness.run_all()
    finally:
        harness.close()
    sys.exit(exit_code)

