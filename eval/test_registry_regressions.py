"""Regression tests for bd_stores_registry.py. Each test is a bug that was reproduced against the
real module and real CSVs, not a hypothetical.

  REGISTRY_BACKEND_DIR=backend python -m unittest eval/test_registry_regressions.py -v
"""
import importlib, os, sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(os.environ.get("REGISTRY_BACKEND_DIR", "backend")).resolve()))
reg = importlib.import_module("bd_stores_registry")

SAREE_COMPOSED = "শাড়ি"          # শাড়ি with U+09DC
SAREE_DECOMPOSED = "শাড়ি"  # শাড়ি with U+09A1 + U+09BC


class Budget(unittest.TestCase):
    def check(self, q, cleaned, price):
        self.assertEqual(reg.extract_budget_and_clean_query(q), (cleaned, price))

    def test_basic(self):
        self.check("gaming laptop under 85000", "gaming laptop", 85000)
        self.check("panjabi 1500 taka", "panjabi", 1500)
        self.check("phone under 20k", "phone", 20000)

    def test_thousands_separator(self):  # original returned 85 (taka!) for this
        self.check("laptop under 85,000", "laptop", 85000)

    def test_bengali_digits_removed_from_query(self):  # original left the number in the query
        self.check("বাজেট ২৫০০০ মোবাইল", "মোবাইল", 25000)

    def test_bengali_word_boundary(self):  # original \b failed after a vowel sign (া, ে)
        self.check("মোবাইল ১৫০০০ টাকার নিচে", "মোবাইল", 15000)
        self.check("পাঞ্জাবি ১৫০০ টাকা", "পাঞ্জাবি", 1500)

    def test_model_numbers_and_years_are_not_budgets(self):
        self.check("iphone 15 pro max 256 gb", "iphone 15 pro max 256 gb", None)
        self.check("laptop 2024", "laptop 2024", None)
        self.check("10000 mah power bank", "10000 mah power bank", None)

    def test_brand_under_armour_untouched(self):  # original deleted the word 'under'
        self.check("under armour shoes", "under armour shoes", None)


class Normalization(unittest.TestCase):
    def test_nukta_forms_normalize_identically(self):
        a = reg.normalize_search_query(SAREE_COMPOSED)
        b = reg.normalize_search_query(SAREE_DECOMPOSED)
        self.assertEqual(a, b)

    def test_both_normalizers_agree(self):  # original: one produced U+09DC, the other U+09A1+U+09BC
        for s in (SAREE_COMPOSED, SAREE_DECOMPOSED):
            self.assertEqual(reg.normalize_search_query(s), reg.normalize_search_query_variants(s)[1])

    def test_routing_independent_of_typing_form(self):
        for s in (SAREE_COMPOSED, SAREE_DECOMPOSED, "জামদানি " + SAREE_COMPOSED, "জামদানি " + SAREE_DECOMPOSED):
            self.assertEqual(reg.resolve_category_from_query(s)[0], "saree-boutiques", repr(s))


class FacebookUrls(unittest.TestCase):
    f = staticmethod(reg._format_facebook_url)

    def test_url_and_handle(self):
        self.assertEqual(self.f("https://www.facebook.com/startech.com.bd", "x"), "https://www.facebook.com/startech.com.bd")
        self.assertEqual(self.f("@fantora.net", "x"), "https://www.facebook.com/fantora.net")

    def test_name_with_handle_in_parens(self):  # original produced facebook.com/Chumro@chumro23
        self.assertEqual(self.f("Chumro (@chumro23)", "Chumro"), "https://www.facebook.com/chumro23")

    def test_plain_names_are_not_invented_as_pages(self):  # original made facebook.com/JamdaniVille
        for name in ("Jamdani Ville", "Glitz & Glamour BD", "Time Zone"):
            u = self.f(name, name)
            self.assertIn("/search/", u, u)


class StoreMatching(unittest.TestCase):
    def url(self, name, q="iphone 15"):
        return reg.build_store_target_url(name, q)

    def test_no_wrong_merchant_from_substring_alias(self):
        self.assertNotIn("yellowclothing.net", self.url("Yellow Mart"))   # alias 'yellow'
        self.assertNotIn("dazzle.com.bd", self.url("Dazzle & Glow", "necklace"))  # alias 'dazzle'
        self.assertNotIn("waltonbd.com", self.url("Walton Computer", "laptop"))   # alias 'walton'

    def test_known_merchants_still_resolve(self):
        self.assertIn("startech.com.bd", self.url("Star Tech", "ssd"))
        self.assertIn("ryans.com", self.url("Ryans", "laptop"))
        self.assertIn("applegadgetsbd.com", self.url("Apple Gadgets", "iphone"))

    def test_meta_returns_the_store_asked_for(self):
        self.assertEqual(reg.get_store_registry_meta("Yellow Mart")["name"], "Yellow Mart")
        self.assertEqual(reg.get_store_registry_meta("Dazzle & Glow")["category"], "Budget, Casual & Imitation Jewelry Targets")


class Loader(unittest.TestCase):
    def test_csv_with_bom_loads(self):  # Excel 'CSV UTF-8' adds a BOM; original silently dropped the whole file
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "x.csv").write_bytes(
                b"\xef\xbb\xbfName,Category,Website,Facebook page,Architecture_Mode\n"
                b"Test Store,Mobile Phones & Consumer Gadgets,teststore.com.bd,https://www.facebook.com/t, Engine A (Direct SKU Match)\n")
            orig = reg._get_registries_dir
            reg._get_registries_dir = lambda: d
            try:
                reg.load_all_registries(force=True)
                self.assertEqual([s["name"] for s in reg.ALL_STORES_REGISTRY], ["Test Store"])
            finally:
                reg._get_registries_dir = orig
                reg.load_all_registries(force=True)

    def test_broken_reload_keeps_old_registry(self):  # hot-reload of a half-saved CSV must not wipe the live registry
        n = len(reg.ALL_STORES_REGISTRY)
        self.assertGreater(n, 100)
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "empty.csv").write_text("garbage header\n", encoding="utf-8")
            orig = reg._get_registries_dir
            reg._get_registries_dir = lambda: d
            try:
                reg.load_all_registries(force=True, guard=True)
                self.assertEqual(len(reg.ALL_STORES_REGISTRY), n)
            finally:
                reg._get_registries_dir = orig
                reg.load_all_registries(force=True)

    def test_new_category_csv_is_not_filed_under_mobile(self):  # README promises 'drop in a new CSV'; original lumps it into MOBILE_GADGET
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "books.csv").write_text(
                "Name,Category,Website,Facebook page,Architecture_Mode\n"
                "Book Shop,Books & Stationery,bookshop.com.bd,https://www.facebook.com/b,Engine A (Direct SKU Match)\n",
                encoding="utf-8")
            orig = reg._get_registries_dir
            reg._get_registries_dir = lambda: d
            try:
                reg.load_all_registries(force=True)
                self.assertIn("BOOKS_STATIONERY", reg.RETAIL_VERTICALS)
                self.assertNotIn("MOBILE_GADGET", reg.RETAIL_VERTICALS)
            finally:
                reg._get_registries_dir = orig
                reg.load_all_registries(force=True)

    def test_readers_never_see_empty_state_during_reload(self):  # best effort: a race test can only fail, never prove
        import threading
        old_interval = sys.getswitchinterval()
        sys.setswitchinterval(1e-6)
        stop, bad = threading.Event(), []

        def reader():
            while not stop.is_set():
                if not reg.RETAIL_VERTICALS.get("CYCLES_EV") or not reg.ALL_STORES_REGISTRY:
                    bad.append(1)
        threads = [threading.Thread(target=reader) for _ in range(4)]
        try:
            for t in threads: t.start()
            for _ in range(120): reg.load_all_registries(force=True)
        finally:
            stop.set()
            for t in threads: t.join()
            sys.setswitchinterval(old_interval)
        self.assertEqual(len(bad), 0)


class Router(unittest.TestCase):
    def test_garbage_query_has_no_category(self):  # original sends everything unmatched to mobile-gadgets
        self.assertEqual(reg.resolve_category_or_none("asdfghjk qwertyzx")[0], None)

    def test_substring_does_not_route(self):  # 'dates' inside 'updates' sent software queries to grocery
        self.assertIsNone(reg.resolve_category_or_none("software updates")[0])
        self.assertIsNone(reg.resolve_category_or_none("bangla book")[0])

    def test_spacing_tolerance_is_kept(self):
        self.assertEqual(reg.resolve_category_or_none("iphone15")[0], "mobile-gadgets")
        self.assertEqual(reg.resolve_category_or_none("e bike")[0], "cycles-evs")

    def test_KNOWN_GAP_brand_outranks_product_noun(self):
        # Score = keyword length, so long brand names beat short product nouns. Needs an intent parser,
        # not more keywords. When this starts passing, delete the decorator.
        self.assertEqual(reg.resolve_category_or_none("samsung tv")[0], "home-appliances")
        self.assertEqual(reg.resolve_category_or_none("adidas shirt")[0], "fashion-apparel")
        self.assertEqual(reg.resolve_category_or_none("simple shirt")[0], "fashion-apparel")

    def test_real_queries_still_route(self):
        self.assertEqual(reg.resolve_category_or_none("electric bike")[0], "cycles-evs")
        self.assertEqual(reg.resolve_category_or_none("iphone 15")[0], "mobile-gadgets")
        self.assertEqual(reg.resolve_category_or_none("macbook air m2")[0], "laptops-pc")
        self.assertEqual(reg.resolve_category_or_none("ac")[0], "home-appliances")


if __name__ == "__main__":
    unittest.main()

