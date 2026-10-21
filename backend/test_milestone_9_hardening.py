"""
Milestone 9: Production Hardening, Strict Category Isolation & Adversarial SQA Suite
(backend/test_milestone_9_hardening.py)

Tests:
1. test_01_electric_bike_never_returns_computer_stores_or_pc_parts
2. test_02_sqa01_negation_aware_accessory_guard
3. test_03_sqa02_budget_number_stripped_from_anchors
4. test_04_sqa03_no_substring_collision_and_bengali_unicode_safety
5. test_05_sqa04_multi_accessory_or_logic
6. test_06_sqa05_waf_403_does_not_false_trigger_fb_failover
7. test_07_sqa06_concurrent_hot_reload_thread_safety_and_ssrf_guard
"""

import glob
import os
import sys
import threading
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add current backend folder to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bd_stores_registry import (
    ALL_STORES_REGISTRY,
    CATEGORY_REGISTRY_MAP,
    extract_budget_and_clean_query,
    get_all_stores_registry,
    get_stores_for_category,
    normalize_search_query,
    resolve_category_from_query,
)
from crawler import (
    CATEGORY_NEGATIVE_FIREWALL,
    passes_category_negative_firewall,
)
from llm_reasoner import (
    extract_mandatory_anchor_tokens,
    matches_anchor_tokens,
    user_requested_accessory,
)
from main import (
    check_merchant_url_liveness,
    is_safe_external_url,
    track_offer_click,
)
from models import Product, StoreOffer


class TestMilestone9Hardening(unittest.TestCase):

    def test_01_electric_bike_never_returns_computer_stores_or_pc_parts(self):
        """
        Verify:
        - Query 'electronic bikes', 'electric bike', and 'betari saikel' maps to 'Cycles & Electric Vehicles (EVs)'.
        - Assert 0 stores from laptops_and_computers.csv (Star Tech, Ryans, TechLand) are included in the pool.
        - Verify passes_category_negative_firewall('MSI B550 Gaming Motherboard', 'Cycles & Electric Vehicles (EVs)') is False.
        """
        print("\n[SQA TEST 1] Verifying Strict Category Isolation for Cycles & EVs...")
        test_queries = ["electronic bikes", "electric bike", "betari saikel"]

        for q in test_queries:
            cat_id, meta = resolve_category_from_query(q)
            self.assertEqual(
                cat_id,
                "cycles-evs",
                f"Query '{q}' must map to 'cycles-evs' but got '{cat_id}'",
            )
            self.assertEqual(
                meta["csv"],
                "cycles_and_evs.csv",
                f"Query '{q}' must resolve to cycles_and_evs.csv",
            )
            self.assertEqual(
                meta["csv_category"],
                "Cycles & Electric Vehicles (EVs)",
            )

            # Assert candidate store pool from this category contains ZERO computer stores
            candidate_stores = get_stores_for_category(cat_id)
            self.assertGreater(
                len(candidate_stores),
                0,
                f"Candidate stores for '{cat_id}' should not be empty",
            )

            banned_computer_stores = ["star tech", "ryans", "techland", "computer mania"]
            for s in candidate_stores:
                s_name = s.get("name", "").lower()
                for bcs in banned_computer_stores:
                    self.assertNotIn(
                        bcs,
                        s_name,
                        f"Computer store '{bcs}' leaked into '{cat_id}' candidate pool: '{s_name}'",
                    )

        # Assert negative keyword firewall rejects PC components on cycles
        firewall_result = passes_category_negative_firewall(
            "MSI B550 Gaming Motherboard",
            "Cycles & Electric Vehicles (EVs)",
        )
        self.assertFalse(
            firewall_result,
            "passes_category_negative_firewall must reject 'MSI B550 Gaming Motherboard' on Cycles vertical",
        )
        print("  [PASS] 0 computer stores in Cycles & EVs; PC parts strictly blocked by negative firewall.")

    def test_02_sqa01_negation_aware_accessory_guard(self):
        """
        Verify SQA-01:
        - Query 'iphone 15 without charger' and 'samsung s24 chara charger'.
        - Assert user_requested_accessory is False.
        - Assert 'charger' is NOT in anchor_tokens.
        """
        print("\n[SQA TEST 2] Verifying SQA-01: Negation-Aware Accessory Guard...")
        queries = [
            ("iphone 15 without charger", "charger"),
            ("samsung s24 chara charger", "charger"),
        ]

        for q, negated_token in queries:
            is_acc = user_requested_accessory(q)
            self.assertFalse(
                is_acc,
                f"Query '{q}' should have user_requested_accessory=False due to negation",
            )

            anchors = extract_mandatory_anchor_tokens(q)
            self.assertNotIn(
                negated_token,
                anchors,
                f"Negated token '{negated_token}' should NOT be in anchor_tokens for '{q}'",
            )

        print("  [PASS] Negation-aware accessory guard correctly stripped negated accessories.")

    def test_03_sqa02_budget_number_stripped_from_anchors(self):
        """
        Verify SQA-02:
        - Query 'gaming laptop under 85000' and 'panjabi 1500 taka'.
        - Assert max_price_bdt is 85000 and 1500.
        - Assert '85000' and '1500' are NOT in anchor_tokens.
        - Assert matches_anchor_tokens('ASUS TUF Gaming Laptop RTX 4060', anchor_tokens) returns True.
        """
        print("\n[SQA TEST 3] Verifying SQA-02: Budget-Number Pre-Extraction from Anchors...")
        cleaned_1, max_p1 = extract_budget_and_clean_query("gaming laptop under 85000")
        self.assertEqual(max_p1, 85000, "Expected max_price_bdt=85000 for 'gaming laptop under 85000'")
        anchors_1 = extract_mandatory_anchor_tokens("gaming laptop under 85000")
        self.assertNotIn("85000", anchors_1, "'85000' must NOT be in anchor_tokens")
        self.assertIn("gaming", anchors_1)
        self.assertIn("laptop", anchors_1)

        # Candidate laptop matching
        self.assertTrue(
            matches_anchor_tokens("ASUS TUF Gaming Laptop RTX 4060", anchors_1),
            "ASUS TUF Gaming Laptop RTX 4060 must match ['gaming', 'laptop']",
        )

        cleaned_2, max_p2 = extract_budget_and_clean_query("panjabi 1500 taka")
        self.assertEqual(max_p2, 1500, "Expected max_price_bdt=1500 for 'panjabi 1500 taka'")
        anchors_2 = extract_mandatory_anchor_tokens("panjabi 1500 taka")
        self.assertNotIn("1500", anchors_2, "'1500' must NOT be in anchor_tokens")
        self.assertIn("panjabi", anchors_2)

        print("  [PASS] Budget numbers successfully extracted and purged from mandatory anchor tokens.")

    def test_04_sqa03_no_substring_collision_and_bengali_unicode_safety(self):
        """
        Verify SQA-03:
        - Query 'macbook air m2' maps to laptops_and_computers.csv and NEVER expands 'ac' into 'air conditioner'.
        - Query 'জামদানি শাড়ি' and 'সরিষার তেল' normalize cleanly to exact canonical targets without diacritic corruption.
        """
        print("\n[SQA TEST 4] Verifying SQA-03: No Substring Collision & Bengali Unicode Safety...")
        cat_id, meta = resolve_category_from_query("macbook air m2")
        self.assertEqual(
            meta["csv"],
            "laptops_and_computers.csv",
            f"Query 'macbook air m2' must map to laptops_and_computers.csv, not '{meta['csv']}'",
        )
        self.assertNotEqual(
            cat_id,
            "home-appliances",
            "'macbook air m2' must never trigger 'ac' -> home-appliances",
        )

        # Bengali Unicode combining mark normalization
        jamdani_q = "জামদানি শাড়ি"
        norm_jamdani = normalize_search_query(jamdani_q)
        self.assertEqual(
            norm_jamdani,
            "জামদানি শাড়ি",
            f"Bengali text '{jamdani_q}' should preserve unicode combining vowel marks",
        )
        cat_j, meta_j = resolve_category_from_query(jamdani_q)
        self.assertEqual(
            meta_j["csv"],
            "saree_boutiques_fcommerce.csv",
            f"'{jamdani_q}' must resolve to saree_boutiques_fcommerce.csv",
        )

        mustard_oil_q = "সরিষার তেল"
        norm_oil = normalize_search_query(mustard_oil_q)
        self.assertEqual(
            norm_oil,
            "সরিষার তেল",
            f"Bengali text '{mustard_oil_q}' should preserve unicode combining vowel marks",
        )
        cat_o, meta_o = resolve_category_from_query(mustard_oil_q)
        self.assertEqual(
            meta_o["csv"],
            "grocery_and_snacks.csv",
            f"'{mustard_oil_q}' must resolve to grocery_and_snacks.csv",
        )

        print("  [PASS] Zero substring collisions; Bengali Unicode combining marks perfectly preserved.")

    def test_05_sqa04_multi_accessory_or_logic(self):
        """
        Verify SQA-04:
        - Query 's24 ultra case and screen protector'.
        - Assert user_requested_accessory is True.
        - Assert matches_anchor_tokens returns True for both 'Samsung S24 Ultra Spigen Armor Case'
          and 'Samsung S24 Ultra Tempered Glass Screen Protector'.
        """
        print("\n[SQA TEST 5] Verifying SQA-04: Multi-Accessory OR Logic...")
        q = "s24 ultra case and screen protector"
        is_acc = user_requested_accessory(q)
        self.assertTrue(
            bool(is_acc),
            f"Query '{q}' has explicit accessory tokens, user_requested_accessory must be True",
        )

        anchors = extract_mandatory_anchor_tokens(q)

        case_candidate = "Samsung S24 Ultra Spigen Armor Case"
        protector_candidate = "Samsung S24 Ultra Tempered Glass Screen Protector"

        self.assertTrue(
            matches_anchor_tokens(case_candidate, anchors),
            f"'{case_candidate}' must match anchor tokens for '{q}'",
        )
        self.assertTrue(
            matches_anchor_tokens(protector_candidate, anchors),
            f"'{protector_candidate}' must match anchor tokens for '{q}'",
        )

        print("  [PASS] Multi-accessory OR logic correctly accepted both individual cases and individual protectors.")

    def test_06_sqa05_waf_403_does_not_false_trigger_fb_failover(self):
        """
        Verify SQA-05:
        - Mock an outbound merchant check returning HTTP 403 (Cloudflare WAF) vs HTTP 502 / timeout.
        - Assert HTTP 403 redirects to the merchant's primary website_url.
        - Assert HTTP 502 / timeout triggers fb_fallback to facebook_page_url.
        """
        print("\n[SQA TEST 6] Verifying SQA-05: WAF-Resilient Failover (403 Alive vs 502 Dead)...")
        # Direct classifier check
        self.assertTrue(
            check_merchant_url_liveness(status_code=403),
            "HTTP 403 (WAF block) must be treated as Website Alive",
        )
        self.assertTrue(
            check_merchant_url_liveness(status_code=200),
            "HTTP 200 must be treated as Website Alive",
        )
        self.assertFalse(
            check_merchant_url_liveness(status_code=502),
            "HTTP 502 (Bad Gateway) must be treated as dead site",
        )
        self.assertFalse(
            check_merchant_url_liveness(status_code=404),
            "HTTP 404 must be treated as dead site",
        )
        self.assertFalse(
            check_merchant_url_liveness(exc=Exception("Connection Timeout")),
            "Timeout exception must be treated as dead site",
        )

        # Mock track_offer_click behavior with mock DB and mock HTTP client
        mock_offer = MagicMock(spec=StoreOffer)
        mock_offer.id = 999
        mock_offer.store_name = "Star Tech"
        mock_offer.target_url = "https://www.startech.com.bd/product/test"
        mock_offer.clicks = 0
        mock_offer.spider_status = "live"
        mock_offer.product = MagicMock(spec=Product)
        mock_offer.product.title_en = "AMD Ryzen 5 5600G Processor"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_offer
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

        # Scenario A: Cloudflare WAF returns 403 -> Website alive, redirect to primary website
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 403
            mock_client.head.return_value = mock_resp
            mock_client.get.return_value = mock_resp
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            import asyncio
            res_403 = asyncio.run(track_offer_click(offer_id=999, request=mock_request, db=mock_db))
            # Offer target_url should NOT have changed to Facebook
            self.assertIn(
                "startech.com.bd",
                mock_offer.target_url,
                "HTTP 403 must NOT trigger failover to Facebook",
            )
            self.assertNotEqual(mock_offer.spider_status, "fb_fallback")

        # Scenario B: Server error 502 -> Dead site, trigger fb_fallback
        mock_offer.target_url = "https://www.startech.com.bd/product/test"
        mock_offer.spider_status = "live"
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.status_code = 502
            mock_client.head.return_value = mock_resp
            mock_client.get.return_value = mock_resp
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            import asyncio
            res_502 = asyncio.run(track_offer_click(offer_id=999, request=mock_request, db=mock_db))
            self.assertIn(
                "facebook.com",
                mock_offer.target_url,
                "HTTP 502 MUST trigger fb_fallback to Facebook",
            )
            self.assertEqual(mock_offer.spider_status, "fb_fallback")

        print("  [PASS] WAF 403 correctly preserved website URL; 502 correctly triggered Facebook failover.")

    def test_07_sqa06_concurrent_hot_reload_thread_safety_and_ssrf_guard(self):
        """
        Verify SQA-06:
        - Spawn 20 concurrent threads calling store lookups while touching CSV timestamps.
        - Assert 0 exceptions and 0 empty store lists.
        - Assert is_safe_external_url('http://127.0.0.1:8000/api/v1/admin') and
          is_safe_external_url('http://169.254.169.254/latest/meta-data') return False.
        """
        print("\n[SQA TEST 7] Verifying SQA-06: Thread-Safe Hot-Reload & SSRF Guard...")
        # 1. SSRF Guard
        self.assertFalse(
            is_safe_external_url("http://127.0.0.1:8000/api/v1/admin"),
            "127.0.0.1 loopback must be blocked by SSRF guard",
        )
        self.assertFalse(
            is_safe_external_url("http://localhost:8000/secret"),
            "localhost must be blocked by SSRF guard",
        )
        self.assertFalse(
            is_safe_external_url("http://169.254.169.254/latest/meta-data"),
            "Cloud metadata link-local IP must be blocked by SSRF guard",
        )
        self.assertFalse(
            is_safe_external_url("http://10.0.0.1/private"),
            "Private RFC-1918 IP must be blocked by SSRF guard",
        )
        self.assertTrue(
            is_safe_external_url("https://www.startech.com.bd"),
            "Public store URL must be accepted by SSRF guard",
        )

        # 2. Concurrent Hot-Reload Thread Safety
        reg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "registries")
        csv_files = glob.glob(os.path.join(reg_dir, "*.csv"))

        thread_errors = []
        store_counts = []

        def lookup_worker():
            try:
                for _ in range(10):
                    stores = get_all_stores_registry()
                    store_counts.append(len(stores))
                    time.sleep(0.005)
            except Exception as e:
                thread_errors.append(e)

        def touch_worker():
            try:
                if csv_files:
                    for _ in range(5):
                        target_csv = csv_files[0]
                        os.utime(target_csv, None)
                        time.sleep(0.01)
            except Exception as e:
                thread_errors.append(e)

        threads = []
        for _ in range(20):
            t = threading.Thread(target=lookup_worker)
            threads.append(t)
            t.start()

        touch_t = threading.Thread(target=touch_worker)
        threads.append(touch_t)
        touch_t.start()

        for t in threads:
            t.join()

        self.assertEqual(
            len(thread_errors),
            0,
            f"Encountered thread errors during concurrent reload: {thread_errors}",
        )
        self.assertTrue(
            all(count > 0 for count in store_counts),
            "Store counts read during concurrent hot-reload must NEVER be 0",
        )
        print("  [PASS] 20 concurrent threads survived hot-reload with 0 errors; SSRF guard 100% active.")


if __name__ == "__main__":
    unittest.main()

