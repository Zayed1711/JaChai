"""
JaChai Milestone 6 Comprehensive Automated SQA Test Suite
Verifies:
1. Search Isolation & Zero Keyword Bleed (Anchor Tokens + 2-Way Accessory Guard)
2. Anti-Scam Vertical Guardrails (Zero Multi-Vendor Marketplaces in PC/Phone + New Stores)
3. Dual-Target Registry & Website-to-Facebook Automatic Failover
4. Admin-Controlled Homepage Blocks (Slots 1-6) CRUD & Storefront Init
5. Local Advertiser Banner File Uploads & Local Image Proxy Direct File Serving
"""

import io
import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, UPLOAD_DIR, seed_default_homepage_blocks
from database import Base, engine, SessionLocal
from models import Product, StoreOffer, HomepageBlock
from bd_stores_registry import (
    RETAIL_VERTICALS,
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


class TestMilestone6(unittest.TestCase):
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

    # ==========================================================================
    # TEST 1: PINPOINT SEARCH PRECISION & ZERO KEYWORD BLEED
    # ==========================================================================
    def test_01_anchor_token_extraction_and_matching(self):
        print("\n[TEST 1A] Testing Anchor Token Extraction...")
        # 1. Strip stop words, retain core entity
        tokens = extract_mandatory_anchor_tokens("iPhone 15 Pro Max best price in bd")
        self.assertIn("iphone", tokens)
        self.assertNotIn("price", tokens)
        self.assertNotIn("bd", tokens)
        self.assertNotIn("best", tokens)

        tokens_socks = extract_mandatory_anchor_tokens("cotton socks buy online")
        self.assertIn("socks", tokens_socks)
        self.assertNotIn("buy", tokens_socks)
        self.assertNotIn("online", tokens_socks)

        # 2. Strict Title Containment Gate (iPhone query MUST reject Androids)
        iphone_tokens = extract_mandatory_anchor_tokens("iPhone")
        self.assertTrue(matches_anchor_tokens("Apple iPhone 15 Pro Max 256GB", iphone_tokens, "iPhone"))
        self.assertFalse(matches_anchor_tokens("Samsung Galaxy S24 Ultra 5G", iphone_tokens, "iPhone"))
        self.assertFalse(matches_anchor_tokens("Xiaomi Redmi Note 13 Pro", iphone_tokens, "iPhone"))
        print("  [PASS] iPhone strictly rejected Samsung Galaxy and Xiaomi Redmi.")

    def test_01_two_way_accessory_guard(self):
        print("\n[TEST 1B] Testing Two-Way Context-Aware Accessory Guard...")
        # Rule A: Core device search rejects accessories
        req_acc = user_requested_accessory("iPhone 15 Pro")
        self.assertEqual(len(req_acc), 0, "Query 'iPhone 15 Pro' is not an accessory query")

        candidates = [
            {"title": "Apple iPhone 15 Pro (128GB)", "price": 128000},
            {"title": "iPhone 15 Pro Max Liquid Silicone Shockproof Case", "price": 1250},
            {"title": "iPhone 15 Pro Tempered Glass Screen Protector", "price": 450},
            {"title": "iPhone 15 Pro 20W Fast Charging Cable Type-C", "price": 1800},
        ]
        filtered = verify_and_filter_candidates(candidates, "iPhone 15 Pro")
        titles = [c["title"] for c in filtered]
        self.assertIn("Apple iPhone 15 Pro (128GB)", titles)
        self.assertNotIn("iPhone 15 Pro Max Liquid Silicone Shockproof Case", titles)
        self.assertNotIn("iPhone 15 Pro Tempered Glass Screen Protector", titles)
        self.assertNotIn("iPhone 15 Pro 20W Fast Charging Cable Type-C", titles)
        print("  [PASS] Rule A verified: Core device query purged cases, glass protectors, and cables.")

        # Rule B: Explicit accessory query requires accessory token in title
        acc_candidates = [
            {"title": "Apple iPhone 15 Pro (128GB)", "price": 128000},
            {"title": "iPhone 15 Pro Ultra-Slim Matte Silicone Case", "price": 850},
            {"title": "iPhone 15 Pro Leather Back Cover", "price": 1400},
        ]
        filtered_acc = verify_and_filter_candidates(acc_candidates, "iPhone 15 Pro Case")
        acc_titles = [c["title"] for c in filtered_acc]
        self.assertNotIn("Apple iPhone 15 Pro (128GB)", acc_titles)
        self.assertIn("iPhone 15 Pro Ultra-Slim Matte Silicone Case", acc_titles)
        print("  [PASS] Rule B verified: Explicit accessory query rejected primary device listing.")

    # ==========================================================================
    # TEST 2: ANTI-SCAM VERTICAL GUARDRAILS
    # ==========================================================================
    def test_02_anti_scam_vertical_whitelists(self):
        print("\n[TEST 2] Testing Anti-Scam Vertical Whitelists...")
        banned_marketplaces = {"Daraz", "Bikroy", "AjkerDeal", "Othoba", "Bdstall", "PriyoShop", "ClickBD", "Sindabad"}

        laptop_stores = {s["name"] for s in RETAIL_VERTICALS.get("LAPTOP_PC", [])}
        mobile_stores = {s["name"] for s in RETAIL_VERTICALS.get("MOBILE_GADGET", [])}

        for banned in banned_marketplaces:
            self.assertNotIn(banned, laptop_stores, f"Security Violation: {banned} found in LAPTOP_PC")
            self.assertNotIn(banned, mobile_stores, f"Security Violation: {banned} found in MOBILE_GADGET")

        print("  [PASS] Zero multi-vendor marketplaces present in LAPTOP_PC or MOBILE_GADGET.")

        # Verify added specialists
        self.assertIn("PCB Store Bangladesh", laptop_stores, "PCB Store Bangladesh missing from LAPTOP_PC")
        self.assertIn("Raduga", mobile_stores, "Raduga missing from MOBILE_GADGET")
        self.assertIn("Goriber Gadget", mobile_stores, "Goriber Gadget missing from MOBILE_GADGET")
        print("  [PASS] Verified PCB Store Bangladesh, Raduga, and Goriber Gadget registered.")

    # ==========================================================================
    # TEST 3: DUAL-TARGET REGISTRY & FAILOVER TO FACEBOOK
    # ==========================================================================
    def test_03_dual_target_registry_and_failover(self):
        print("\n[TEST 3] Testing Dual-Target Registry & Automatic Facebook Failover...")
        fb_startech = get_store_facebook_fallback_url("Star Tech", "Ryzen 5 5600")
        self.assertTrue("facebook.com" in fb_startech and "startech" in fb_startech, f"Unexpected FB url: {fb_startech}")

        fb_raduga = get_store_facebook_fallback_url("Raduga", "Pixel 8")
        self.assertTrue(fb_raduga.startswith("https://www.facebook.com/radugabd"), f"Unexpected FB url: {fb_raduga}")

        # Test reachability failover on dead/unreachable URL
        db = SessionLocal()
        try:
            prod = db.query(Product).first()
            if not prod:
                prod = Product(
                    slug="test-failover-item",
                    title_en="Failover Test Item",
                    title_bn="ফেলওভার টেস্ট আইটেম",
                    category="gadgets",
                    image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
                    specs_summary="Test specs",
                    lowest_price=1000,
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)

            # Insert an offer with an unreachable target URL (non-routable IP to trigger timeout)
            test_offer = StoreOffer(
                product_id=prod.id,
                store_name="Star Tech",
                source_type="crawler",
                target_url="http://10.255.255.1:9999/non-existent-product",
                current_price=2500,
                original_price=3000,
                spider_status="healthy",
            )
            db.add(test_offer)
            db.commit()
            db.refresh(test_offer)

            # Execute /go/offer/{id} with format=json
            resp = self.client.get(f"/go/offer/{test_offer.id}?format=json")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertIn("facebook.com", data["redirect_url"])
            self.assertEqual(data["spider_status"], "fb_fallback")

            # Check database row was updated
            db.refresh(test_offer)
            self.assertEqual(test_offer.spider_status, "fb_fallback")
            self.assertIn("facebook.com", test_offer.target_url)
            print("  [PASS] Automatic 2.5s reachability check triggered failover to Star Tech Facebook page.")

            # Clean up test offer
            db.delete(test_offer)
            db.commit()
        finally:
            db.close()

    # ==========================================================================
    # TEST 4: ADMIN-CONTROLLED HOMEPAGE BLOCKS (SLOTS 1-6)
    # ==========================================================================
    def test_04_homepage_blocks_crud_and_storefront(self):
        print("\n[TEST 4] Testing Admin-Controlled Homepage Blocks CRUD...")
        # 1. Public storefront init contains homepage_blocks
        init_resp = self.client.get("/api/v1/storefront/init")
        self.assertEqual(init_resp.status_code, 200)
        init_data = init_resp.json()
        self.assertIn("homepage_blocks", init_data)
        blocks = init_data["homepage_blocks"]
        self.assertGreaterEqual(len(blocks), 4, "Storefront should contain at least 4-6 blocks")
        print(f"  [PASS] Storefront init returned {len(blocks)} active homepage blocks.")

        # 2. Admin GET blocks
        admin_blocks_resp = self.client.get("/api/v1/admin/homepage-blocks", headers=self.admin_headers)
        self.assertEqual(admin_blocks_resp.status_code, 200)

        # 3. Admin CREATE block
        new_block_data = {
            "slot_order": 7,
            "title_en": "Gaming Consoles & VR",
            "title_bn": "গেমিং কনসোল ও ভিআর",
            "subtitle_en": "PlayStation 5, Xbox Series X & Meta Quest",
            "subtitle_bn": "প্লেস্টেশন ৫ ও মেটা কোয়েস্ট সেরা দাম",
            "search_query": "PlayStation 5",
            "category": "Gaming",
            "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db",
            "badge_text": "GAMING DEALS",
            "starting_price_bdt": 62000,
            "is_active": True,
        }
        create_resp = self.client.post("/api/v1/admin/homepage-blocks", json=new_block_data, headers=self.admin_headers)
        self.assertEqual(create_resp.status_code, 201)
        created = create_resp.json()
        block_id = created["id"]
        self.assertEqual(created["search_query"], "PlayStation 5")

        # 4. Admin UPDATE block
        update_resp = self.client.put(
            f"/api/v1/admin/homepage-blocks/{block_id}",
            json={"starting_price_bdt": 59900, "badge_text": "PRICE DROP"},
            headers=self.admin_headers,
        )
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["starting_price_bdt"], 59900)

        # 5. Admin DELETE block
        del_resp = self.client.delete(f"/api/v1/admin/homepage-blocks/{block_id}", headers=self.admin_headers)
        self.assertEqual(del_resp.status_code, 200)
        print("  [PASS] Homepage block CRUD verified: Create, Read, Update, Delete.")

    # ==========================================================================
    # TEST 5: LOCAL ADVERTISER BANNER FILE UPLOAD & IMAGE PROXY BYPASS
    # ==========================================================================
    def test_05_local_advertiser_banner_upload_and_proxy(self):
        print("\n[TEST 5] Testing Advertiser Banner File Upload & Proxy Bypass...")
        # 1. Create a dummy test image byte stream
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

        files = {"file": ("sponsor_banner_test.png", io.BytesIO(dummy_png), "image/png")}
        upload_resp = self.client.post("/api/v1/admin/upload-banner", files=files, headers=self.admin_headers)
        self.assertEqual(upload_resp.status_code, 200)
        upload_data = upload_resp.json()
        self.assertIn("url", upload_data)
        uploaded_url = upload_data["url"]
        self.assertTrue(uploaded_url.startswith("/uploads/banners/"))

        # Verify file is saved in UPLOAD_DIR
        filename = upload_data["filename"]
        file_path = os.path.join(UPLOAD_DIR, filename)
        self.assertTrue(os.path.exists(file_path), f"Uploaded file not found on disk: {file_path}")
        print(f"  [PASS] Banner uploaded successfully to {file_path}.")

        # 2. Test Image Proxy bypass for local /uploads/ URL
        proxy_resp = self.client.get(f"/api/v1/image-proxy?url={uploaded_url}")
        self.assertEqual(proxy_resp.status_code, 200)
        self.assertEqual(proxy_resp.content, dummy_png)
        print("  [PASS] Image proxy successfully bypassed external fetch and served local banner directly.")

        # Clean up test banner
        try:
            os.remove(file_path)
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
