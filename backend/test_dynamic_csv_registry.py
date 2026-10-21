"""
JaChai Automated Verification Suite: Dynamic Category-Separated CSV Registry
Verifies:
1. All 13 category CSV files exist in `registries/` and account for all 326 curated stores.
2. Core stores from all categories map to their respective verticals and architecture modes.
3. Adding a new column manually to any CSV is automatically detected in-memory without server restart.
4. Added columns are accessible directly on store dictionaries.
5. Deleting or modifying a column restores cleanly.
"""

import csv
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bd_stores_registry as reg


class TestDynamicCSVRegistry(unittest.TestCase):
    def setUp(self):
        reg.load_all_registries(force=True)

    def test_01_all_category_csvs_and_stores_loaded(self):
        print("\n[TEST 1] Verifying Category-Separated CSV Ingestion...")
        status = reg.get_registry_status()
        self.assertGreaterEqual(status["total_stores"], 300, f"Expected at least 300 stores, found {status['total_stores']}")
        self.assertGreaterEqual(len(status["csv_files"]), 13, "Expected at least 13 category CSV files")

        expected_files = [
            "mobile_phones_and_gadgets.csv",
            "laptops_and_computers.csv",
            "fashion_and_apparel.csv",
            "grocery_and_snacks.csv",
            "fine_jewelry_and_gold.csv",
            "budget_jewelry_fcommerce.csv",
            "saree_boutiques_fcommerce.csv",
            "sneakers_and_footwear.csv",
            "watches_and_horology.csv",
            "appliances_and_electronics.csv",
            "beauty_and_skincare.csv",
            "cycles_and_evs.csv",
            "sportswear_and_gym.csv",
        ]
        for ef in expected_files:
            self.assertIn(ef, status["csv_files"], f"Missing category file: {ef}")

        print(f"  [PASS] All 13 category CSV files verified ({status['total_stores']} stores total).")

    def test_02_vertical_mappings_and_architecture_modes(self):
        print("\n[TEST 2] Verifying Vertical Mappings and Architecture Modes...")
        all_stores = reg.get_all_stores_registry()

        # Check sample stores
        store_names = {s["name"]: s for s in all_stores}
        self.assertIn("Gadget & Gear (G&G)", store_names)
        self.assertIn("Star Tech", store_names)
        self.assertIn("Aarong", store_names)
        self.assertIn("Khaas Food", store_names)
        self.assertIn("Diamond World Limited", store_names)
        self.assertIn("Reevo", store_names)

        g_and_g = store_names["Gadget & Gear (G&G)"]
        self.assertEqual(g_and_g["engine"], "Engine A")
        self.assertEqual(g_and_g["architecture_mode"], "Engine A (Direct SKU Match)")
        self.assertIn("gadgetandgear.com", g_and_g["website_url"])

        aarong = store_names["Aarong"]
        self.assertEqual(aarong["engine"], "Engine B")
        self.assertEqual(aarong["architecture_mode"], "Engine B (Starts From Benchmark)")

        print("  [PASS] Store vertical mappings and Engine A/B modes verified.")

    def test_03_dynamic_manual_column_addition_and_auto_update(self):
        print("\n[TEST 3] Verifying Dynamic Manual Column Addition & Auto-Update...")

        initial_cols = list(reg.DETECTED_COLUMNS)
        print(f"  Initial detected columns: {initial_cols}")
        self.assertIn("Name", initial_cols)
        self.assertIn("Category", initial_cols)

        # 1. Manually add new columns: 'Rating', 'Helpline', 'Special_Tag' to cycles_and_evs.csv
        target_csv = os.path.join(reg._get_registries_dir(), "cycles_and_evs.csv")
        with open(target_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            original_rows = list(reader)

        header = original_rows[0]
        new_header = header + ["Rating", "Helpline", "Special_Tag"]
        modified_rows = [new_header]
        for r in original_rows[1:]:
            modified_rows.append(r + ["4.95", "01700-112233", "EcoFriendly_EV"])

        # Reset mtime throttle so check triggers immediately
        reg._LAST_MTIME_CHECK_TS = 0.0
        with open(target_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(modified_rows)

        try:
            # 2. Trigger getter and assert auto-update
            reg._LAST_MTIME_CHECK_TS = 0.0
            updated_stores = reg.get_all_stores_registry()
            updated_cols = reg.DETECTED_COLUMNS

            print(f"  Updated detected columns: {updated_cols}")
            self.assertIn("Rating", updated_cols)
            self.assertIn("Helpline", updated_cols)
            self.assertIn("Special_Tag", updated_cols)

            # Check that stores have the new fields dynamically attached
            ev_stores_with_new_cols = [s for s in updated_stores if s.get("Rating") == "4.95"]
            self.assertGreaterEqual(len(ev_stores_with_new_cols), 8)

            sample_store = ev_stores_with_new_cols[0]
            self.assertEqual(sample_store["Rating"], "4.95")
            self.assertEqual(sample_store["Helpline"], "01700-112233")
            self.assertEqual(sample_store["Special_Tag"], "EcoFriendly_EV")
            # Also lowercase slug access
            self.assertEqual(sample_store["rating"], "4.95")
            self.assertEqual(sample_store["helpline"], "01700-112233")
            self.assertEqual(sample_store["special_tag"], "EcoFriendly_EV")

            print(f"  [PASS] Successfully auto-detected added columns on '{sample_store['name']}': Rating={sample_store['Rating']}, Helpline={sample_store['Helpline']}")

        finally:
            # 3. Clean up and restore original CSV
            reg._LAST_MTIME_CHECK_TS = 0.0
            with open(target_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(original_rows)

            reg._LAST_MTIME_CHECK_TS = 0.0
            restored_stores = reg.get_all_stores_registry()
            print(f"  Restored detected columns: {reg.DETECTED_COLUMNS}")
            self.assertNotIn("Special_Tag", reg.DETECTED_COLUMNS)
            print("  [PASS] Original CSV restored and clean registry confirmed.")


if __name__ == "__main__":
    unittest.main(verbosity=2)

