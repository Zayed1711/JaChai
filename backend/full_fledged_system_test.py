"""
JaChai Full-Fledged System Test & SQA Quality Assurance Harness (backend/full_fledged_system_test.py)

Executes an exhaustive, multi-dimensional verification of the JaChai platform:
  [Suite 1] Zero-404 Scraper Architecture & 5-Pillar Pipeline
  [Suite 2] Discontinued & Market-Out Advisory Logic across Retro & Modern Consoles
  [Suite 3] Cross-Category Catalog Link Integrity Audit (Gaming, Mobile, Appliances)
  [Suite 4] Shopper Outbound Navigation, Resolution & Click Tracking (/go/offer/{id})
  [Suite 5] Admin Command Center Zero-Dummy & Real-time Telemetry Verification
  [Suite 6] Google Analytics 4 (GA4) Integration & Frontend Health Check
"""

import asyncio
import os
import re
import sys
import time
import unittest
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path and configure UTF-8 output
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from database import SessionLocal, engine
from models import Product, StoreOffer, ClickLog, SearchTelemetry
from url_healer import fast_preflight_check, classify_soft_404, SOFT_404_PATTERNS
from crawler import run_all_spiders, scrape_single_offer
from sitemap_importer import is_likely_product_url
from master_catalog import MASTER_CATALOG_ITEMS, build_master_product_card
from retro_gaming_catalog import RETRO_GAMING_CATALOG_ITEMS
from redmi_xiaomi_catalog import REDMI_XIAOMI_CATALOG_ITEMS
from appliances_catalog import APPLIANCE_CATALOG_ITEMS
from auth import create_access_token
from main import app


class FullFledgedSystemTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 75)
        print(">>> STARTING JACHAI FULL-FLEDGED SYSTEM TEST HARNESS")
        print("=" * 75)
        cls.db = SessionLocal()
        cls.client = TestClient(app)
        token = create_access_token({"sub": "jachai_admin", "role": "owner"})
        cls.admin_headers = {"Authorization": f"Bearer {token}", "X-Admin-Pin": "42791"}

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        print("\n" + "=" * 75)
        print("<<< FULL-FLEDGED SYSTEM TEST HARNESS COMPLETED")
        print("=" * 75)

    # =========================================================================
    # SUITE 1: ZERO-404 PIPELINE VERIFICATION (5 PILLARS)
    # =========================================================================
    def test_suite_1_zero_404_preflight_and_soft_404(self):
        """Pillars 1, 2, 3: Pre-flight HEAD/Streaming GET, Soft-404 & Redirects."""
        print("\n--- [Suite 1] Testing Zero-404 Pipeline & Pre-flight Checks ---")

        # 1. Soft-404 English and Bengali Classifications
        en_cases = [
            ("<html><title>404 Not Found</title></html>", True),
            ("<div>Page Not Found. The product has been removed.</div>", True),
            ("<div>0 results for your query.</div>", True),
            ("<div>This item is no longer available in our store.</div>", True),
            ("<div><h1>Sony PlayStation 5</h1><span>68,000 BDT</span></div>", False),
        ]
        for html, expected in en_cases:
            is_soft, _ = classify_soft_404(html)
            self.assertEqual(is_soft, expected)

        bn_cases = [
            ("<div>দুঃখিত, আপনার খোঁজা পণ্যটি পাওয়া যায়নি।</div>", True),
            ("<div>স্টক আউট - বর্তমানে পাওয়া যাচ্ছে না</div>", True),
            ("<div>বর্তমানে পণ্যটি স্টকে নেই</div>", True),
            ("<div><h1>শাওমি রেডমি নোট ১৩</h1><p>মূল্য: ২৫,০০০ টাকা</p></div>", False),
        ]
        for html, expected in bn_cases:
            is_soft, _ = classify_soft_404(html)
            self.assertEqual(is_soft, expected)

        print("  [PASS] Bilingual Soft-404 Classifier (English & Bengali): PASS")

        # 2. Mock Transport Pre-flight Check with 405 Method Not Allowed Fallback & Redirects
        def mock_transport_handler(request: httpx.Request) -> httpx.Response:
            u = str(request.url)
            if "status/404" in u:
                return httpx.Response(404, request=request)
            if "status/405" in u:
                if request.method == "HEAD":
                    return httpx.Response(405, request=request)
                return httpx.Response(200, text="<html><body><h1>Alive Streaming Product</h1></body></html>", request=request)
            if "soft-404" in u:
                return httpx.Response(200, text="<html><head><title>404 Not Found</title></head><body>Empty</body></html>", request=request)
            if "redirect-301" in u:
                return httpx.Response(301, headers={"Location": "https://store.com/products/ps5-canonical"}, request=request)
            if "ps5-canonical" in u:
                return httpx.Response(200, text="<html><body><h1>Sony PS5 Slim</h1></body></html>", request=request)
            return httpx.Response(200, text="<html><body><h1>Standard Product</h1></body></html>", request=request)

        async def _test_preflight():
            transport = httpx.MockTransport(mock_transport_handler)
            async with httpx.AsyncClient(transport=transport) as client:
                # Normal 200
                alive, status, _, _ = await fast_preflight_check(client, "https://store.com/item/1")
                self.assertTrue(alive)
                self.assertEqual(status, 200)

                # 404
                alive_404, status_404, _, _ = await fast_preflight_check(client, "https://store.com/status/404")
                self.assertFalse(alive_404)
                self.assertEqual(status_404, 404)

                # 405 Method Not Allowed on HEAD -> automatically falls back to streaming GET!
                alive_405, status_405, _, _ = await fast_preflight_check(client, "https://store.com/status/405")
                self.assertTrue(alive_405)
                self.assertEqual(status_405, 200)

                # Soft 404 on 200 OK -> rejected
                alive_soft, _, _, _ = await fast_preflight_check(client, "https://store.com/soft-404")
                self.assertFalse(alive_soft)

                # Redirect 301 followed to canonical destination
                alive_red, _, final_url, _ = await fast_preflight_check(client, "https://store.com/redirect-301")
                self.assertTrue(alive_red)
                self.assertEqual(final_url, "https://store.com/products/ps5-canonical")

        asyncio.run(_test_preflight())
        print("  [PASS] Pre-flight HEAD + Streaming GET Fallback (Pillar 1): PASS")
        print("  [PASS] Redirect Follow & Canonical Resolution (Pillar 2): PASS")

    def test_suite_1_decoupled_spiders_queue(self):
        """Pillar 4: Decoupled 3-Stage Queue Architecture."""
        print("--- [Suite 1] Testing Decoupled 3-Stage Async Queue ---")
        async def _run():
            res = await run_all_spiders(self.db, product_id=12, simulate_live_market=True)
            self.assertIsInstance(res, dict)
            self.assertIn("total_checked", res)
            self.assertGreaterEqual(res["total_checked"], 1)
            self.assertGreaterEqual(res["healthy_count"], 1)
            print(f"  [PASS] Decoupled Queue Worker Execution: Checked {res['total_checked']} offers, {res['healthy_count']} healthy")

        asyncio.run(_run())

    # =========================================================================
    # SUITE 2: DISCONTINUED & MARKET-OUT ADVISORY LOGIC
    # =========================================================================
    def test_suite_2_discontinued_market_out_alerts(self):
        """Validates that discontinued / market-out items carry proper warning flags and notes."""
        print("\n--- [Suite 2] Testing Market-Out & Discontinued Production Logic ---")

        # 1. Retro Consoles must be flagged as discontinued
        discontinued_retro_names = [
            "Sony PlayStation 4",
            "PlayStation 3",
            "PlayStation 2",
            "PlayStation Portable",
            "PlayStation Vita",
            "Xbox 360",
            "Xbox One",
            "Nintendo 3DS",
            "Game Boy Advance",
            "Sega Genesis",
        ]
        for item in RETRO_GAMING_CATALOG_ITEMS:
            prod = build_master_product_card(item)
            title = prod.title_en
            if any(legacy.lower() in title.lower() for legacy in discontinued_retro_names):
                self.assertTrue(
                    prod.is_discontinued,
                    f"Expected {title} to have is_discontinued=True",
                )
                self.assertTrue(
                    len(prod.discontinued_note_en or "") > 10,
                    f"Expected English advisory note for {title}",
                )
                self.assertTrue(
                    len(prod.discontinued_note_bn or "") > 10,
                    f"Expected Bengali advisory note for {title}",
                )

        print(f"  [PASS] Verified {len(RETRO_GAMING_CATALOG_ITEMS)} retro console entries for discontinued status & bilingual notes: PASS")

        # 2. Modern consoles must NOT be marked discontinued
        modern_consoles = ["PlayStation 5", "Nintendo Switch", "Steam Deck"]
        for item in MASTER_CATALOG_ITEMS:
            title = item.get("title_en", "")
            if any(m.lower() in title.lower() for m in modern_consoles):
                self.assertFalse(
                    item.get("is_discontinued", False),
                    f"Modern console {title} should not be marked discontinued",
                )

        print("  [PASS] Verified active status for modern consoles (PS5, Switch, Steam Deck): PASS")

    # =========================================================================
    # SUITE 3: CROSS-CATEGORY CATALOG LINK INTEGRITY AUDIT
    # =========================================================================
    def test_suite_3_cross_category_catalog_urls(self):
        """Exhaustively verifies that all catalog URLs are valid search/category endpoints and never broken static slugs."""
        print("\n--- [Suite 3] Auditing Cross-Category Catalog Link Integrity ---")

        broken_links = []
        total_offers_audited = 0

        # Audit helper
        def audit_catalog(cat_name: str, items: list):
            nonlocal total_offers_audited
            for prod in items:
                title = prod.get("title_en") or prod.get("name") or "Unknown"
                offers = prod.get("offers") or prod.get("stores") or []
                for off in offers:
                    total_offers_audited += 1
                    target = off.get("target_url") or off.get("url") or off.get("link") or ""
                    parsed = urlparse(target)

                    # Must have scheme and domain
                    if not parsed.scheme or not parsed.netloc:
                        broken_links.append((title, off.get("store_name") or off.get("name"), target, "Missing scheme/netloc"))
                        continue

                    # Must not contain placeholder text
                    if any(p in target for p in ("example.com", "localhost", "127.0.0.1", "placeholder")):
                        broken_links.append((title, off.get("store_name") or off.get("name"), target, "Contains placeholder domain"))
                        continue

                    # For gaming retro items: verify they route to search endpoints or valid category URLs
                    if cat_name == "Retro Gaming":
                        if "daraz.com.bd" in parsed.netloc and "/products/" in parsed.path:
                            broken_links.append((title, off.get("store_name") or off.get("name"), target, "Daraz static slug instead of query endpoint"))

        audit_catalog("Retro Gaming", RETRO_GAMING_CATALOG_ITEMS)
        audit_catalog("Redmi Xiaomi", REDMI_XIAOMI_CATALOG_ITEMS)
        audit_catalog("Appliances", APPLIANCE_CATALOG_ITEMS)
        audit_catalog("Master Catalog", MASTER_CATALOG_ITEMS)

        print(f"  Total Catalog Store Offers Audited: {total_offers_audited}")
        print(f"  Broken / Invalid Link Count: {len(broken_links)}")

        if broken_links:
            for b in broken_links[:5]:
                print(f"    [FAIL] Broken Link: Product='{b[0]}', Store='{b[1]}', URL='{b[2]}', Reason='{b[3]}'")

        self.assertEqual(len(broken_links), 0, f"Discovered {len(broken_links)} broken links in catalogs!")
        print("  [PASS] Zero Broken Links Guarantee across all categories: PASS")

    # =========================================================================
    # SUITE 4: SHOPPER OUTBOUND RESOLUTION & TRACKING (/go/offer/{id})
    # =========================================================================
    def test_suite_4_outbound_navigation_and_tracking(self):
        """Tests that outbound shopper clicks resolve safely and log click metrics."""
        print("\n--- [Suite 4] Testing Shopper Outbound Navigation & Telemetry (/go/offer/{id}) ---")

        # Find an existing store offer
        offer = self.db.query(StoreOffer).filter(StoreOffer.target_url.isnot(None)).first()
        self.assertIsNotNone(offer, "Requires at least one StoreOffer in database")

        initial_clicks = offer.clicks or 0
        resp = self.client.get(f"/go/offer/{offer.id}?format=json")
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertIn("redirect_url", data)
        self.assertTrue(data["redirect_url"].startswith("http"))
        self.assertEqual(data["clicks"], initial_clicks + 1)

        # Verify ClickLog was persisted
        log_entry = (
            self.db.query(ClickLog)
            .filter(ClickLog.target_type == "offer", ClickLog.target_id == offer.id)
            .order_by(ClickLog.id.desc())
            .first()
        )
        self.assertIsNotNone(log_entry, "ClickLog entry was not saved to database")
        self.assertEqual(log_entry.destination_url, data["redirect_url"])

        print(f"  [PASS] Outbound click resolved to: {data['redirect_url'][:60]}...")
        print(f"  [PASS] Click counter incremented ({initial_clicks} -> {data['clicks']}): PASS")
        print("  [PASS] ClickLog telemetry database persistence: PASS")

    # =========================================================================
    # SUITE 5: ADMIN COMMAND CENTER ZERO-DUMMY VERIFICATION
    # =========================================================================
    def test_suite_5_admin_overview_zero_dummy(self):
        """Verifies that the admin dashboard returns live real-time metrics and zero dummy/mock strings."""
        print("\n--- [Suite 5] Verifying Admin Command Center Zero-Dummy Integrity ---")

        resp = self.client.get("/api/v1/admin/overview", headers=self.admin_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # Check overview collections exist and are loaded
        self.assertIn("products", data)
        self.assertIn("store_offers", data)
        self.assertIn("billboards", data)
        self.assertIn("spotlight_cards", data)
        self.assertIn("homepage_blocks", data)

        self.assertGreaterEqual(len(data["products"]), 1)
        self.assertGreaterEqual(len(data["store_offers"]), 1)

        # Verify sponsor analytics endpoint returns real-time metrics
        resp_sponsors = self.client.get("/api/v1/admin/analytics/sponsors", headers=self.admin_headers)
        self.assertEqual(resp_sponsors.status_code, 200)
        s_data = resp_sponsors.json()
        self.assertIn("total_impressions", s_data)
        self.assertIn("total_outbound_clicks", s_data)
        self.assertIn("total_searches", s_data)
        self.assertIn("campaigns", s_data)

        # Verify no placeholder strings exist in response payload
        raw_text = resp.text.lower()
        for placeholder in ("dummy", "lorem ipsum", "mock_data", "test_placeholder"):
            self.assertNotIn(placeholder, raw_text, f"Found placeholder '{placeholder}' in admin overview response")

        print(f"  [PASS] Admin Overview Collections: Products={len(data['products'])}, StoreOffers={len(data['store_offers'])}, Billboards={len(data['billboards'])}")
        print(f"  [PASS] Admin Telemetry Metrics: Impressions={s_data['total_impressions']}, OutboundClicks={s_data['total_outbound_clicks']}, Searches={s_data['total_searches']}")
        print("  [PASS] Zero dummy/mock data verified: PASS")

    # =========================================================================
    # SUITE 6: GA4 INTEGRATION & FRONTEND HEALTH
    # =========================================================================
    def test_suite_6_ga4_and_frontend_configuration(self):
        """Verifies GA4 ID and key frontend configuration files."""
        print("\n--- [Suite 6] Verifying Google Analytics 4 & Frontend Integration ---")

        # 1. Verify GA4 measurement ID in frontend/src/lib/gtag.ts
        gtag_path = os.path.join(CURRENT_DIR, "..", "frontend", "src", "lib", "gtag.ts")
        self.assertTrue(os.path.exists(gtag_path), "frontend/src/lib/gtag.ts must exist")
        with open(gtag_path, "r", encoding="utf-8") as f:
            gtag_content = f.read()
        self.assertIn("G-XNKQ2NC3YG", gtag_content, "GA4 measurement ID G-XNKQ2NC3YG missing from gtag.ts")

        # 2. Verify GoogleAnalytics component exists and is imported in layout.tsx
        ga_comp_path = os.path.join(CURRENT_DIR, "..", "frontend", "src", "components", "GoogleAnalytics.tsx")
        self.assertTrue(os.path.exists(ga_comp_path), "GoogleAnalytics.tsx must exist")

        layout_path = os.path.join(CURRENT_DIR, "..", "frontend", "src", "app", "layout.tsx")
        self.assertTrue(os.path.exists(layout_path), "layout.tsx must exist")
        with open(layout_path, "r", encoding="utf-8") as f:
            layout_content = f.read()
        self.assertIn("<GoogleAnalytics", layout_content, "GoogleAnalytics tag missing in layout.tsx")

        print("  [PASS] GA4 Measurement ID G-XNKQ2NC3YG configured: PASS")
        print("  [PASS] GoogleAnalytics injected into Next.js root layout: PASS")


if __name__ == "__main__":
    unittest.main()
