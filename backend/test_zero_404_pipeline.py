"""
Automated Test & SQA Audit Suite for JaChai Zero-404 Scraper Architecture (backend/test_zero_404_pipeline.py)
Validates all 5 Pillars:
1. HTTP HEAD / Streaming GET Pre-Flight Check
2. Persistent Redirect Writeback (301/302)
3. Bilingual Soft-404 Classifier (English + Bengali)
4. Decoupled 3-Stage Queue Architecture
5. Sitemap Parsing & Validation
"""

import asyncio
import os
import sys
import unittest

import httpx

from url_healer import classify_soft_404, fast_preflight_check
from database import SessionLocal
from models import Product, StoreOffer
from crawler import run_all_spiders, scrape_single_offer
from sitemap_importer import is_likely_product_url


class TestZero404Pipeline(unittest.TestCase):

    def test_soft_404_classifier_english(self):
        """Pillar 3: Verifies English Soft-404 text detection."""
        test_cases = [
            ("<html><head><title>404 Not Found</title></head><body>Nothing here</body></html>", True),
            ("<html><body><h1>Page Not Found</h1><p>The product you are looking for has been removed.</p></body></html>", True),
            ("<div>Sorry, no results for your search query.</div>", True),
            ("<div>This item is no longer available in our store.</div>", True),
            ("<html><head><title>Sony PlayStation 5 Price in Bangladesh</title></head><body><h1>Sony PS5 Slim</h1><span>65,000 BDT</span></body></html>", False),
        ]
        for html, expected in test_cases:
            is_soft, reason = classify_soft_404(html)
            self.assertEqual(is_soft, expected, f"Failed on: {html[:60]} -> got {is_soft}, expected {expected} ({reason})")

    def test_soft_404_classifier_bengali(self):
        """Pillar 3: Verifies Bengali Soft-404 detection (common on Bangladeshi retail sites)."""
        test_cases = [
            ("<div>দুঃখিত, আপনার খোঁজা পণ্যটি পাওয়া যায়নি।</div>", True),
            ("<div>স্টক আউট - এই মডেলটি বর্তমানে পাওয়া যাচ্ছে না</div>", True),
            ("<html><head><title>পণ্যটি খুঁজে পাওয়া যায়নি | Star Tech</title></head><body>Empty</body></html>", True),
            ("<div>বর্তমানে পণ্যটি স্টকে নেই, অন্য মডেল দেখতে পারেন।</div>", True),
            ("<div><h1>শাওমি রেডমি নোট ১৩ প্রো</h1><p>মূল্য: ২৫,০০০ টাকা</p></div>", False),
        ]
        for html, expected in test_cases:
            is_soft, reason = classify_soft_404(html)
            self.assertEqual(is_soft, expected, f"Failed on: {html[:60]} -> got {is_soft}, expected {expected} ({reason})")

    def test_product_url_heuristic(self):
        """Pillar 5: Tests sitemap product URL filtering."""
        self.assertTrue(is_likely_product_url("https://store.com/products/apple-iphone-15-pro-max"))
        self.assertTrue(is_likely_product_url("https://store.com/product/sony-playstation-5-slim"))
        self.assertFalse(is_likely_product_url("https://store.com/pages/privacy-policy"))
        self.assertFalse(is_likely_product_url("https://store.com/cart"))
        self.assertFalse(is_likely_product_url("https://store.com/category/smartphones/"))

    def test_fast_preflight_check(self):
        """Pillars 1 & 2: Tests fast pre-flight check, HEAD rejection fallback, and redirects using MockTransport."""
        def mock_handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if "status/404" in url_str:
                return httpx.Response(404, request=request)
            if "status/405" in url_str:
                if request.method == "HEAD":
                    return httpx.Response(405, request=request)
                return httpx.Response(200, text="<html><body><h1>Valid Product</h1><p>Price: 100</p></body></html>", request=request)
            if "soft-404" in url_str:
                return httpx.Response(200, text="<html><head><title>404 Not Found</title></head><body>Empty</body></html>", request=request)
            if "redirect" in url_str:
                return httpx.Response(301, headers={"Location": "https://store.com/product/canonical"}, request=request)
            if "canonical" in url_str:
                return httpx.Response(200, text="<html><body><h1>Canonical PS5</h1></body></html>", request=request)
            return httpx.Response(200, text="<html><body><h1>Valid Product</h1></body></html>", request=request)

        transport = httpx.MockTransport(mock_handler)

        async def _run():
            async with httpx.AsyncClient(transport=transport) as client:
                # 1. Test live responsive page
                alive, status, final_url, _ = await fast_preflight_check(client, "https://store.com/item/1")
                self.assertTrue(alive)
                self.assertEqual(status, 200)

                # 2. Test 404 rejection
                alive_404, status_404, _, _ = await fast_preflight_check(client, "https://store.com/status/404")
                self.assertFalse(alive_404)
                self.assertEqual(status_404, 404)

                # 3. Test 405 Method Not Allowed on HEAD -> gracefully falls back to Streaming GET and passes!
                alive_405, status_405, final_url_405, _ = await fast_preflight_check(client, "https://store.com/status/405")
                self.assertTrue(alive_405)
                self.assertEqual(status_405, 200)

                # 4. Test Soft-404 rejection even when status is 200 OK
                alive_soft, status_soft, _, _ = await fast_preflight_check(client, "https://store.com/soft-404")
                self.assertFalse(alive_soft)

                # 5. Test redirect following to canonical destination
                alive_red, status_red, final_url_red, _ = await fast_preflight_check(client, "https://store.com/redirect")
                self.assertTrue(alive_red)
                self.assertIn("canonical", final_url_red)

        asyncio.run(_run())

    def test_decoupled_spiders_queue(self):
        """Pillar 4: Tests the 3-stage queue execution with simulated market on product 12."""
        async def _run():
            db = SessionLocal()
            try:
                # Test spiders with simulate_live_market=True on product_id=12
                res = await run_all_spiders(db, product_id=12, simulate_live_market=True)
                self.assertIsInstance(res, dict)
                self.assertIn("total_checked", res)
                self.assertIn("synced_at", res)
                self.assertIn("healthy_count", res)
                print(f"\n[Spider Queue Audit] Product 12 - Total checked: {res['total_checked']}, Healthy: {res['healthy_count']}, Updated: {res['updated_count']}")
            finally:
                db.close()

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
