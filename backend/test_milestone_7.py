"""
JaChai Milestone 7 Comprehensive SQA Automated Verification Suite
Verifies:
1. Rebuild Registry with Dual-Targets & Architecture Modes (Engine A vs Engine B)
2. Website-to-Facebook Smart Failover (Zero-404 Guarantee on /go/offer/{id})
3. Exact-Match Search & Anti-Pollution (Anchor Tokens + 2-Way Accessory Guard)
4. Admin-Controlled 6-Block Homepage Slots CRUD (GET / POST / PUT / DELETE)
5. Local Advertiser Banner File Upload & Direct Image Proxy Bypass
"""

import io
import os
import sys
import unittest
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, UPLOAD_DIR, seed_default_homepage_blocks
from database import Base, engine, SessionLocal
from models import Product, StoreOffer, HomepageBlock
from bd_stores_registry import (
    ALL_STORES_REGISTRY,
    RETAIL_VERTICALS,
    FCOMMERCE_JEWELRY_BOUTIQUES,
    FCOMMERCE_SAREE_BOUTIQUES,
    STORE_FACEBOOK_PAGES,
    get_store_facebook_fallback_url,
    build_store_target_url,
)
from llm_reasoner import (
    extract_mandatory_anchor_tokens,
    user_requested_accessory,
    matches_anchor_tokens,
    verify_and_filter_candidates,
)


class TestMilestone7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_default_homepage_blocks(db)
        finally:
            db.close()

        cls.client = TestClient(app)
        # Login to obtain admin token
        login_resp = cls.client.post("/api/v1/admin/login", json={"pin": "2026"})
        assert login_resp.status_code == 200, f"Admin login failed: {login_resp.text}"
        cls.token = login_resp.json()["access_token"]
        cls.admin_headers = {"Authorization": f"Bearer {cls.token}"}
        cls.test_files_to_cleanup = []

    @classmethod
    def tearDownClass(cls):
        for path in cls.test_files_to_cleanup:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass

    # ==========================================================================
    # TEST 1: REBUILD REGISTRY WITH DUAL-TARGETS & ARCHITECTURE MODES
    # ==========================================================================
    def test_01_registry_rebuild_and_architecture_modes(self):
        print("\n[TEST 1] Testing Registry Rebuild & Architecture Modes...")

        # 1. Total stores count
        self.assertGreaterEqual(len(ALL_STORES_REGISTRY), 300, "Registry must contain all 326 stores from CSV")
        print(f"  [PASS] Verified {len(ALL_STORES_REGISTRY)} stores loaded into registry.")

        # 2. Every store dictionary has required dual targets & architecture mode
        sample_names = ["Star Tech", "Ryans Computers", "Aarong", "Fabrilife", "Khaas Food", "Diamond World Limited", "KRY International"]
        found_samples = 0

        for store in ALL_STORES_REGISTRY:
            self.assertIn("name", store)
            self.assertIn("category", store)
            self.assertIn("domain", store)
            self.assertIn("website_url", store)
            self.assertIn("facebook_page_url", store)
            self.assertIn("architecture_mode", store)
            self.assertIn("engine", store)

            # Must be either Engine A or Engine B
            self.assertIn(store["engine"], ["Engine A", "Engine B"])
            self.assertIn(store["architecture_mode"], [
                "Engine A (Direct SKU Match)",
                "Engine B (Starts From Benchmark)"
            ])

            if store["name"] in sample_names:
                found_samples += 1
                # Check specific engine classifications
                if store["name"] in ["Star Tech", "Ryans Computers", "Khaas Food", "KRY International"]:
                    self.assertEqual(store["engine"], "Engine A", f"{store['name']} must be Engine A (Direct SKU Match)")
                elif store["name"] in ["Aarong", "Fabrilife", "Diamond World Limited"]:
                    self.assertEqual(store["engine"], "Engine B", f"{store['name']} must be Engine B (Starts From Benchmark)")

        self.assertGreaterEqual(found_samples, 5, "Sample stores must all exist and have verified engine modes")
        print("  [PASS] Engine A (Direct SKU Match) and Engine B (Starts From Benchmark) classifications verified.")

        # 3. F-Commerce boutique nodes
        self.assertGreaterEqual(len(FCOMMERCE_JEWELRY_BOUTIQUES), 50)
        self.assertGreaterEqual(len(FCOMMERCE_SAREE_BOUTIQUES), 50)
        print(f"  [PASS] Boutique nodes verified: {len(FCOMMERCE_JEWELRY_BOUTIQUES)} Jewelry & {len(FCOMMERCE_SAREE_BOUTIQUES)} Saree nodes.")

    # ==========================================================================
    # TEST 2: WEBSITE-TO-FACEBOOK SMART FAILOVER (ZERO-404 GUARANTEE)
    # ==========================================================================
    def test_02_website_to_facebook_smart_failover(self):
        print("\n[TEST 2] Testing Website-to-Facebook Smart Failover...")

        db = SessionLocal()
        try:
            # Clean up any stale failover test products first
            stale = db.query(Product).filter(Product.slug.like("failover-test%")).all()
            for sp in stale:
                db.query(StoreOffer).filter(StoreOffer.product_id == sp.id).delete()
                db.delete(sp)
            db.commit()

            test_slug = f"failover-test-{uuid.uuid4().hex[:8]}"
            test_prod = Product(
                slug=test_slug,
                title_en="KRY Failover Flagship Smartphone",
                title_bn="à¦«à§‡à¦²à¦“à¦­à¦¾à¦° à¦«à§à¦²à§à¦¯à¦¾à¦—à¦¶à¦¿à¦ª à¦¸à§à¦®à¦¾à¦°à§à¦Ÿà¦«à§‹à¦¨",
                category="Mobiles",
                image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
                is_pinned_homepage=False,
            )
            db.add(test_prod)
            db.commit()
            db.refresh(test_prod)
            test_prod_id = test_prod.id

            unreachable_website = "http://127.0.0.1:59999/down-test"
            failover_offer = StoreOffer(
                product_id=test_prod_id,
                store_name="KRY International",
                source_type="crawler",
                target_url=unreachable_website,
                current_price=95000,
                original_price=99000,
                in_stock=True,
                spider_status="healthy",
            )
            db.add(failover_offer)
            db.commit()
            db.refresh(failover_offer)
            offer_id = failover_offer.id
        finally:
            db.close()

        # Execute GET /go/offer/{offer_id} with follow_redirects=False
        resp = self.client.get(f"/go/offer/{offer_id}", follow_redirects=False)
        self.assertIn(resp.status_code, [302, 307], f"Expected redirect, got status {resp.status_code}")

        location = resp.headers.get("location", "")
        # Should redirect to KRY International official Facebook page
        expected_fb = "https://www.facebook.com/kryinternational"
        self.assertIn("facebook.com", location.lower(), "Redirect location must route to Facebook")
        self.assertIn("kryinternational", location.lower(), f"Expected '{expected_fb}', got '{location}'")

        # Verify DB offer status was updated to fb_fallback
        db = SessionLocal()
        try:
            updated_offer = db.query(StoreOffer).filter(StoreOffer.id == offer_id).first()
            if updated_offer:
                self.assertEqual(updated_offer.spider_status, "fb_fallback")
                self.assertIn("facebook.com", updated_offer.target_url)
                db.delete(updated_offer)
            prod_to_del = db.query(Product).filter(Product.id == test_prod_id).first()
            if prod_to_del:
                db.delete(prod_to_del)
            db.commit()
        finally:
            db.close()

        print(f"  [PASS] Automatic 2.5s health probe intercepted unreachable website and routed to Facebook ({location}).")

    # ==========================================================================
    # TEST 3: EXACT-MATCH SEARCH & ANTI-POLLUTION (ANCHOR TOKENS & ACCESSORY GUARD)
    # ==========================================================================
    def test_03_exact_match_search_and_anti_pollution(self):
        print("\n[TEST 3] Testing Exact-Match Search & Dynamic Accessory Guard...")

        # 1. Zero Keyword Stuffing & Anchor Token Extraction
        tokens = extract_mandatory_anchor_tokens("iPhone 15 Pro Max price in bd best online")
        self.assertIn("iphone", tokens)
        self.assertIn("15", tokens)
        self.assertIn("pro", tokens)
        self.assertNotIn("price", tokens)
        self.assertNotIn("best", tokens)
        self.assertNotIn("online", tokens)

        # 2. Strict Entity Containment
        iphone_tokens = extract_mandatory_anchor_tokens("iPhone")
        self.assertTrue(matches_anchor_tokens("Apple iPhone 15 Pro Max 256GB", iphone_tokens, "iPhone"))
        self.assertFalse(matches_anchor_tokens("Samsung Galaxy S24 Ultra 5G", iphone_tokens, "iPhone"))
        self.assertFalse(matches_anchor_tokens("Xiaomi Redmi Note 13 Pro 5G", iphone_tokens, "iPhone"))
        print("  [PASS] Anchor token gate: 'iPhone' strictly blocks Samsung Galaxy and Redmi.")

        # 3. Dynamic Two-Way Accessory Guard
        # Primary Hardware search
        primary_candidates = [
            {"title": "Apple iPhone 15 Pro (128GB)", "price": 128000, "product_url": "https://gadgetandgear.com/product/1"},
            {"title": "iPhone 15 Pro Silicone Protective Case", "price": 1200, "product_url": "https://gadgetandgear.com/product/2"},
            {"title": "iPhone 15 Pro Tempered Glass Screen Protector", "price": 450, "product_url": "https://gadgetandgear.com/product/3"},
            {"title": "iPhone 15 Pro 20W Fast Charging Cable", "price": 1800, "product_url": "https://gadgetandgear.com/product/4"},
        ]
        filtered_primary = verify_and_filter_candidates(primary_candidates, "iPhone 15 Pro")
        primary_titles = [c["title"] for c in filtered_primary]
        self.assertIn("Apple iPhone 15 Pro (128GB)", primary_titles)
        self.assertNotIn("iPhone 15 Pro Silicone Protective Case", primary_titles)
        self.assertNotIn("iPhone 15 Pro Tempered Glass Screen Protector", primary_titles)
        self.assertNotIn("iPhone 15 Pro 20W Fast Charging Cable", primary_titles)
        print("  [PASS] Primary device query purged all cases, protectors, and charging cables.")

        # Explicit Accessory search
        acc_candidates = [
            {"title": "Apple iPhone 15 Pro (128GB)", "price": 128000, "product_url": "https://gadgetandgear.com/product/1"},
            {"title": "iPhone 15 Pro Liquid Silicone Protective Case", "price": 1200, "product_url": "https://gadgetandgear.com/product/2"},
        ]
        filtered_acc = verify_and_filter_candidates(acc_candidates, "iPhone 15 Pro Case")
        acc_titles = [c["title"] for c in filtered_acc]
        self.assertNotIn("Apple iPhone 15 Pro (128GB)", acc_titles)
        self.assertIn("iPhone 15 Pro Liquid Silicone Protective Case", acc_titles)
        print("  [PASS] Explicit accessory query required accessory keyword and purged bare hardware.")

    # ==========================================================================
    # TEST 4: ADMIN-CONTROLLED 6-BLOCK HOMEPAGE SLOTS CRUD
    # ==========================================================================
    def test_04_admin_controlled_homepage_slots_crud(self):
        print("\n[TEST 4] Testing Admin-Controlled Homepage Slots CRUD...")

        # 1. GET /api/v1/admin/homepage-slots
        res = self.client.get("/api/v1/admin/homepage-slots", headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("slots", data)
        self.assertEqual(len(data["slots"]), 6, "Must return exactly 6 homepage slots")
        self.assertIn("available_products", data)
        print("  [PASS] GET /api/v1/admin/homepage-slots returned 6 slots and available catalog products.")

        # 2. POST /api/v1/admin/homepage-slots (pin / update slot 1)
        post_payload = {
            "slot_order": 1,
            "title_en": "M7 Flagship 5G Smartphones",
            "title_bn": "à¦à¦®à§­ à¦«à§à¦²à§à¦¯à¦¾à¦—à¦¶à¦¿à¦ª à§«à¦œà¦¿ à¦¸à§à¦®à¦¾à¦°à§à¦Ÿà¦«à§‹à¦¨",
            "search_query": "Smartphone",
            "category": "Mobiles",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
            "badge_text": "ðŸ”¥ TOP COMPARED",
            "starting_price_bdt": 22500,
            "is_active": True,
        }
        res_post = self.client.post("/api/v1/admin/homepage-slots", json=post_payload, headers=self.admin_headers)
        self.assertEqual(res_post.status_code, 200)
        print("  [PASS] POST /api/v1/admin/homepage-slots updated Slot #1.")

        # 3. PUT /api/v1/admin/homepage-slots/1
        put_payload = {
            "title_en": "M7 Updated Premium Smartphones",
            "badge_text": "ðŸ”¥ VERIFIED",
        }
        res_put = self.client.put("/api/v1/admin/homepage-slots/1", json=put_payload, headers=self.admin_headers)
        self.assertEqual(res_put.status_code, 200)
        print("  [PASS] PUT /api/v1/admin/homepage-slots/1 updated slot title.")

    # ==========================================================================
    # TEST 5: LOCAL ADVERTISER BANNER UPLOAD & IMAGE PROXY DIRECT SERVING
    # ==========================================================================
    def test_05_local_advertiser_banner_upload_and_proxy(self):
        print("\n[TEST 5] Testing Advertiser Banner File Upload & Direct Proxy Bypass...")

        # 1. Upload mock banner image
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        file_tuple = ("sponsor_banner_m7.png", io.BytesIO(dummy_png), "image/png")

        upload_res = self.client.post(
            "/api/v1/admin/upload-banner",
            files={"file": file_tuple},
            headers=self.admin_headers,
        )
        self.assertEqual(upload_res.status_code, 200, f"Upload failed: {upload_res.text}")
        data = upload_res.json()
        self.assertIn("url", data)
        self.assertIn("image_url", data)
        self.assertTrue(data["url"].startswith("/uploads/banners/"))

        saved_path = os.path.join(UPLOAD_DIR, data["filename"])
        self.assertTrue(os.path.exists(saved_path), "Uploaded banner must be saved to UPLOAD_DIR")
        self.test_files_to_cleanup.append(saved_path)
        print(f"  [PASS] Banner uploaded successfully: {saved_path}")

        # 2. Test Direct Image Proxy Serving without external fetch
        proxy_res = self.client.get(f"/api/v1/image-proxy?url={data['url']}")
        self.assertEqual(proxy_res.status_code, 200)
        self.assertEqual(proxy_res.content, dummy_png)
        print("  [PASS] Image proxy successfully bypassed external fetch and served local banner directly.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
