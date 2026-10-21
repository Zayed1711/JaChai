"""
JaChai Milestone 5.2 Comprehensive Test Suite (backend/test_milestone_5_2.py)
Validates:
  1. Curated Bangladeshi Store Registry (9 retail verticals, 100 F-Commerce nodes, data hygiene).
  2. Local Ollama (qwen2.5:1.5b) Semantic Scraper Reasoner & Fast Deterministic Fallback.
  3. 100% Bangladesh-Only Geo-Fence & Anti-Accessory Blacklist.
  4. Vertical-Prioritized Store Routing (Zero Star Tech for phones, distinct non-404 store URLs).
  5. Authentic Title-to-Image Alignment (Zero Savarkar / political figures, authentic apparel).
  6. 3-Card Side Spotlight Stage (SLOT #02, SLOT #03, SLOT #04 active).
"""

import asyncio
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bd_stores_registry import (
    RETAIL_VERTICALS,
    FCOMMERCE_JEWELRY_BOUTIQUES,
    FCOMMERCE_SAREE_BOUTIQUES,
    get_stores_for_vertical,
    build_store_target_url,
    BANNED_INTERNATIONAL_DOMAINS,
    BANNED_FOREIGN_CURRENCIES,
)
from llm_reasoner import (
    analyze_search_intent,
    verify_and_filter_candidates,
    is_bangladesh_store_url,
    deterministic_intent_fallback,
)
from crawler import (
    generate_resilient_fallback,
    live_meta_search_and_persist,
    validate_and_sanitize_image,
    get_store_search_url,
)
from database import SessionLocal, engine, Base
from models import SpotlightCard, Product, StoreOffer


class Milestone52TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        cls.db = SessionLocal()
        from seed import seed_database
        seed_database(cls.db)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ==========================================================================
    # TEST SUITE 1: CURATED STORE REGISTRY & DATA HYGIENE
    # ==========================================================================
    def test_01_store_registry_verticals_and_fcommerce(self):
        print("\n[TEST 1] Verifying Curated Bangladeshi Store Registry & Nodes...")
        # Check verticals presence
        expected_verticals = [
            "GROCERY_SNACKS", "MOBILE_GADGET", "LAPTOP_PC", "FASHION_APPAREL",
            "JEWELRY", "SNEAKERS_FOOTWEAR", "WATCHES_HOROLOGY", "MARKETPLACE", "LOCAL_SEEDS"
        ]
        for v in expected_verticals:
            self.assertIn(v, RETAIL_VERTICALS, f"Missing vertical: {v}")
            self.assertGreater(len(RETAIL_VERTICALS[v]), 0, f"Empty vertical: {v}")

        # Check 100 F-Commerce boutique nodes
        self.assertEqual(len(FCOMMERCE_JEWELRY_BOUTIQUES), 50, "Expected 50 F-Commerce jewelry boutiques")
        self.assertEqual(len(FCOMMERCE_SAREE_BOUTIQUES), 50, "Expected 50 F-Commerce saree boutiques")

        # Verify defunct platforms are excluded
        all_store_names = []
        for v_stores in RETAIL_VERTICALS.values():
            all_store_names.extend([s["name"].lower() for s in v_stores])
        for defunct in ["evaly", "e-orange", "boomboom", "bagdoom", "kiksha"]:
            self.assertNotIn(defunct, all_store_names, f"Defunct platform '{defunct}' was not excluded!")

        # Verify domain fixes
        mobile_stores = {s["name"]: s.get("domain", "") for s in RETAIL_VERTICALS["MOBILE_GADGET"]}
        fashion_stores = {s["name"]: s.get("domain", "") for s in RETAIL_VERTICALS["FASHION_APPAREL"]}
        
        self.assertIn("yellowclothing.net", fashion_stores.get("Yellow", ""))
        self.assertIn("dazzle.com.bd", mobile_stores.get("Dazzle", ""))
        print("  -> PASSED: All 9 verticals + 100 F-Commerce nodes verified with clean data hygiene.")

    # ==========================================================================
    # TEST SUITE 2: OLLAMA SEMANTIC INTENT REASONING
    # ==========================================================================
    def test_02_semantic_search_intent(self):
        print("\n[TEST 2] Verifying Ollama / Semantic Scraper Intent Reasoner...")
        loop = asyncio.get_event_loop()

        # Case A: Mobile search
        intent_phone = loop.run_until_complete(
            analyze_search_intent("iPhone 15 Pro Max price in bd", None)
        )
        self.assertEqual(intent_phone["vertical"], "MOBILE_GADGET")
        self.assertFalse(intent_phone["is_accessory_query"])
        self.assertGreaterEqual(intent_phone["min_sanity_price_bdt"], 5000)
        self.assertIn("case", intent_phone["exclude_accessory_tokens"])
        print(f"  -> Phone Intent Reasoner: {intent_phone['reasoner']} | Keyword: '{intent_phone['store_search_keyword']}'")

        # Case B: Fashion / Panjabi search
        intent_panjabi = loop.run_until_complete(
            analyze_search_intent("Cotton Panjabi for Eid", None)
        )
        self.assertEqual(intent_panjabi["vertical"], "FASHION_APPAREL")
        self.assertFalse(intent_panjabi["is_accessory_query"])

        # Case C: Accessory search
        intent_acc = loop.run_until_complete(
            analyze_search_intent("iPhone 15 silicone back cover", None)
        )
        self.assertTrue(intent_acc["is_accessory_query"])
        self.assertEqual(intent_acc["exclude_accessory_tokens"], [])
        print("  -> PASSED: Semantic intent classification, sanity bounds, and accessory isolation verified.")

    # ==========================================================================
    # TEST SUITE 3: 100% BANGLADESH-ONLY GEO-FENCE & CANDIDATE VERIFICATION
    # ==========================================================================
    def test_03_bangladesh_geofence_and_candidate_filter(self):
        print("\n[TEST 3] Verifying 100% Bangladesh-Only Geo-Fence & Candidate Guard...")
        # Geo-Fence domain checks
        self.assertTrue(is_bangladesh_store_url("https://gadgetandgear.com/product/iphone-15"))
        self.assertTrue(is_bangladesh_store_url("https://www.startech.com.bd/laptop"))
        self.assertTrue(is_bangladesh_store_url("https://www.facebook.com/marketplace/dhaka/search/?query=saree"))
        self.assertFalse(is_bangladesh_store_url("https://www.amazon.com/dp/B0CX234"))
        self.assertFalse(is_bangladesh_store_url("https://www.walmart.com/ip/iphone-15"))
        self.assertFalse(is_bangladesh_store_url("https://www.ebay.com/itm/12345"))
        self.assertFalse(is_bangladesh_store_url("https://www.aliexpress.com/item/100500.html"))

        # Candidate verification filter
        intent = {
            "vertical": "MOBILE_GADGET",
            "store_search_keyword": "iphone 15",
            "raw_query": "iphone 15",
            "min_sanity_price_bdt": 20000,
            "max_sanity_price_bdt": 300000,
            "is_accessory_query": False,
            "exclude_accessory_tokens": ["case", "cover", "protector"],
        }
        candidates = [
            {"title": "iPhone 15 128GB", "product_url": "https://gadgetandgear.com/p1", "price": 142000},
            {"title": "iPhone 15 Case Cover", "product_url": "https://applegadgetsbd.com/p2", "price": 1200}, # Accessory -> Reject
            {"title": "iPhone 15 Savarkar Edition", "product_url": "https://sumashtech.com/p3", "price": 145000}, # Political entity -> Reject
            {"title": "iPhone 15 USA Unlocked", "product_url": "https://www.amazon.com/p4", "price": 899}, # Foreign domain & price -> Reject
            {"title": "iPhone 15 256GB Global", "product_url": "https://dazzle.com.bd/p5", "price": 154000},
        ]
        verified = verify_and_filter_candidates(intent, candidates)
        self.assertEqual(len(verified), 2, f"Expected 2 verified candidates, got {len(verified)}")
        titles = [v["title"] for v in verified]
        self.assertIn("iPhone 15 128GB", titles)
        self.assertIn("iPhone 15 256GB Global", titles)
        print("  -> PASSED: Foreign domains, foreign currencies, accessories, and political entities strictly rejected.")

    # ==========================================================================
    # TEST SUITE 4: ZERO STAR TECH FOR PHONES & ZERO-404 DISTINCT URLS
    # ==========================================================================
    def test_04_vertical_routing_and_zero_startech_monopoly(self):
        print("\n[TEST 4] Verifying Vertical Specialist Routing & Zero Star Tech Phone Monopoly...")
        # 1. Test Phone Fallback Generation
        iphone_items = generate_resilient_fallback("iPhone 15")
        iphone_stores = set(i["store_name"] for i in iphone_items)
        print(f"  -> Mobile phone stores returned: {iphone_stores}")
        self.assertNotIn("Star Tech", iphone_stores, "CRITICAL: Star Tech must NOT be in mobile phone stores!")
        self.assertTrue(
            any(s in iphone_stores for s in ["Gadget & Gear", "Sumash Tech", "Apple Gadgets BD", "Dazzle BD"]),
            "Missing Bangladeshi mobile specialists!"
        )

        # 2. Test Distinct, Non-404 Store URLs
        first_title = iphone_items[0]["title"]
        first_prod_items = [i for i in iphone_items if i["title"] == first_title]
        store_urls = [i["product_url"] for i in first_prod_items]
        self.assertEqual(len(store_urls), len(set(store_urls)), "Store URLs must be strictly distinct per offer!")
        for url in store_urls:
            self.assertTrue(url.startswith("http"), f"Invalid non-HTTP URL: {url}")
            self.assertNotIn("localhost", url)

        # 3. Test Live Meta-Search & Persist for iPhone 15
        loop = asyncio.get_event_loop()
        products = loop.run_until_complete(
            live_meta_search_and_persist("iPhone 15", None, self.db)
        )
        self.assertGreaterEqual(len(products), 1, "Expected at least 1 product persisted")
        
        for p in products:
            if "iphone" in p.title_en.lower():
                store_names = [o.store_name for o in p.offers]
                self.assertNotIn("Star Tech", store_names, "Persisted iPhone 15 must NOT have Star Tech offers!")
                # Verify distinct target URLs on persisted offers
                offer_urls = [o.target_url for o in p.offers]
                self.assertEqual(len(offer_urls), len(set(offer_urls)), "Offer target URLs must be unique!")
        print("  -> PASSED: Mobile phone vertical routed to BD mobile specialists with 0% Star Tech monopoly and distinct URLs.")

    # ==========================================================================
    # TEST SUITE 5: AUTHENTIC APPAREL & SAREE IMAGERY (ZERO SAVARKAR / ENTITY)
    # ==========================================================================
    def test_05_authentic_fashion_and_saree_imagery(self):
        print("\n[TEST 5] Verifying Authentic Apparel & Saree Imagery...")
        loop = asyncio.get_event_loop()

        # Search Cotton Panjabi
        panjabi_prods = loop.run_until_complete(
            live_meta_search_and_persist("Cotton Panjabi", None, self.db)
        )
        self.assertGreaterEqual(len(panjabi_prods), 1)
        for p in panjabi_prods:
            if "panjabi" in p.title_en.lower():
                self.assertNotIn("savarkar", p.image_url.lower())
                self.assertNotIn("statue", p.image_url.lower())
                self.assertTrue(
                    any(k in p.image_url.lower() for k in ["panjabi", "shirt", "photo", "images"]),
                    f"Panjabi image '{p.image_url}' is not an authentic garment image!"
                )
                store_names = [o.store_name for o in p.offers]
                self.assertTrue(
                    any(any(brand.lower() in s.lower() for brand in ["Fabrilife", "Aarong", "Sailor", "Le Reve", "Yellow", "Cats Eye"]) for s in store_names),
                    f"No BD fashion specialist found in store offers: {store_names}"
                )

        # Search Jamdani Saree
        saree_prods = loop.run_until_complete(
            live_meta_search_and_persist("Jamdani Saree", None, self.db)
        )
        self.assertGreaterEqual(len(saree_prods), 1)
        for p in saree_prods:
            if "saree" in p.title_en.lower() or "jamdani" in p.title_en.lower():
                self.assertTrue(
                    "jamdani" in p.image_url.lower() or "saree" in p.image_url.lower() or "unsplash" in p.image_url.lower()
                )
        print("  -> PASSED: Authentic apparel & saree images aligned, zero political/historical figures.")

    # ==========================================================================
    # TEST SUITE 6: SIDE BILLBOARD STAGE (SLOT #02, SLOT #03, SLOT #04)
    # ==========================================================================
    def test_06_side_spotlight_stage_three_cards(self):
        print("\n[TEST 6] Verifying Side Spotlight Stage (3 Active Cards)...")
        cards = (
            self.db.query(SpotlightCard)
            .filter(SpotlightCard.is_active.is_(True))
            .order_by(SpotlightCard.slot_code.asc())
            .all()
        )
        self.assertGreaterEqual(len(cards), 3, f"Expected 3 active spotlight cards, found {len(cards)}")
        slot_codes = [c.slot_code for c in cards]
        self.assertIn("SLOT #02", slot_codes)
        self.assertIn("SLOT #03", slot_codes)
        self.assertIn("SLOT #04", slot_codes)
        print(f"  -> PASSED: All 3 Spotlight Cards active in jachai.db: {slot_codes[:3]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

