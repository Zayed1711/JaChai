import sys
import os

# Set stdout encoding for Windows console
sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from database import SessionLocal, engine
from models import Product, StoreOffer, SpotlightCard
from main import app

client = TestClient(app)

def run_verification():
    print("=" * 70)
    print("=== JACHAI MILESTONE 5.1: OPEN-MARKET SCRAPING & INTEGRITY TESTS ===")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # 1. VERIFY 6 GENERIC TRENDING CATEGORY SEARCH HUBS
    # -------------------------------------------------------------------------
    print("\n--- 1. Testing Generic Trending Search Hubs Endpoint ---")
    resp_hubs = client.get("/api/v1/storefront/trending-hubs")
    assert resp_hubs.status_code == 200, f"Expected 200, got {resp_hubs.status_code}"
    hubs_data = resp_hubs.json()
    assert "hubs" in hubs_data, "Response missing 'hubs' key"
    hubs = hubs_data["hubs"]
    assert len(hubs) == 6, f"Expected 6 trending hubs, got {len(hubs)}"

    print(f"[OK] GET /api/v1/storefront/trending-hubs returned {len(hubs)} hubs:")
    for h in hubs:
        assert "S24" not in h["title_en"] and "iPhone" not in h["title_en"], "Hub titles must be generic categories"
        print(f"     * [{h['id']}] {h['title_en']} | Trigger: '{h['query_trigger']}' | From: BDT {h['starting_price_bdt']:,}")

    # -------------------------------------------------------------------------
    # 2. VERIFY STOREFRONT INIT INCLUDES ALL 3 SPOTLIGHT CARDS (FIX 1)
    # -------------------------------------------------------------------------
    print("\n--- 2. Testing Storefront Init for 3 Spotlight Cards (FIX 1) ---")
    resp_init = client.get("/api/v1/storefront/init?track_impressions=false")
    assert resp_init.status_code == 200, f"Expected 200, got {resp_init.status_code}"
    init_data = resp_init.json()
    assert "spotlight_cards" in init_data, "Init missing spotlight_cards"
    spotlights = init_data["spotlight_cards"]
    assert len(spotlights) == 3, f"Expected 3 spotlight cards (SLOT #02, #03, #04), got {len(spotlights)}"
    slot_codes = [s["slot_code"] for s in spotlights]
    assert "SLOT #02" in slot_codes and "SLOT #03" in slot_codes and "SLOT #04" in slot_codes, f"Missing slots: {slot_codes}"
    print(f"[OK] Storefront Init returned {len(spotlights)} spotlight cards: {slot_codes}")
    for s in spotlights:
        print(f"     * [{s['slot_code']}] {s['brand_title_en']} - {s['tagline_en']} (৳{s['starting_price']:,})")

    # -------------------------------------------------------------------------
    # 3. VERIFY ON-DEMAND TECH SEARCH & ANTI-ACCESSORY FILTER (FIX 2, 4, 5)
    # -------------------------------------------------------------------------
    print("\n--- 3. Testing Open-Market Tech Search & Anti-Accessory Filter (q=iPhone+15) ---")
    resp_search = client.get("/api/v1/search/live?q=iPhone+15")
    assert resp_search.status_code == 200, f"Expected 200, got {resp_search.status_code}"
    iphone_prods = resp_search.json()
    assert len(iphone_prods) >= 1, "Expected at least 1 product result for 'iPhone 15'"

    print(f"[OK] Live Meta-Search returned {len(iphone_prods)} products for 'iPhone 15':")
    for p in iphone_prods[:2]:
        title = p["title_en"]
        t_lower = title.lower()
        # Verify Anti-Accessory Filter: No cases, covers, or screen protectors
        for acc in ["case", "cover", "tempered glass", "screen protector", "skin"]:
            assert acc not in t_lower, f"Accessory item '{acc}' leaked into primary phone search: {title}"

        offers = p["offers"]
        assert len(offers) >= 2, f"Product '{title}' must have multiple store offers for comparison"

        # Verify Open-Market store names and distinct target URLs (Breaking the Star Tech loop)
        offer_urls = [o["target_url"] for o in offers]
        store_names = [o["store_name"] for o in offers]
        assert len(offer_urls) == len(set(offer_urls)), f"Duplicate target URLs found (Star Tech Loop detected!): {offer_urls}"

        print(f"     * Title: {title}")
        print(f"       Lowest: ৳{p['lowest_price']:,} | Stores: {p['store_count']}")
        for o in offers:
            assert o["target_url"].startswith("http"), f"Invalid offer target URL: {o['target_url']}"
            print(f"         - {o['store_name']}: ৳{o['current_price']:,} -> {o['target_url'][:65]}...")

    # -------------------------------------------------------------------------
    # 4. VERIFY RESILIENT ETHNIC SEARCH & APPAREL IMAGE GUARD (FIX 3, 4)
    # -------------------------------------------------------------------------
    print("\n--- 4. Testing Resilient Ethnic Search & Apparel Image Guard (q=Premium+Cotton+Panjabi) ---")
    resp_panjabi = client.get("/api/v1/search/live?q=Premium+Cotton+Panjabi")
    assert resp_panjabi.status_code == 200, f"Expected 200, got {resp_panjabi.status_code}"
    panjabi_prods = resp_panjabi.json()
    assert len(panjabi_prods) >= 1, "Expected at least 1 product result for Panjabi"
    first_p = panjabi_prods[0]

    assert "panjabi" in first_p["title_en"].lower(), "Title must match searched query"
    assert first_p["category"] == "fashion", f"Category must be 'fashion', got '{first_p['category']}'"
    img_url = first_p["image_url"].lower()

    # Image Integrity Guard: Must NOT contain any banned political/historical entities (Savarkar, etc.)
    banned_words = ["savarkar", "gandhi", "nehru", "politician", "statue", "monument"]
    for bw in banned_words:
        assert bw not in img_url, f"Banned political entity '{bw}' found in apparel image: {first_p['image_url']}"

    # Verify Fashion retail landscape
    fashion_stores = [o["store_name"] for o in first_p["offers"]]
    assert any(fs in fashion_stores for fs in ["Aarong", "Sailor BD", "Fabrilife", "Cats Eye", "Daraz Fashion"]), f"Fashion outlets missing: {fashion_stores}"
    print(f"[OK] Ethnic Panjabi query returned '{first_p['title_en']}' with {len(first_p['offers'])} authentic fashion offers:")
    print(f"     * Image: {first_p['image_url']}")
    for o in first_p["offers"]:
        print(f"         - {o['store_name']}: ৳{o['current_price']:,} -> {o['target_url'][:65]}...")

    # -------------------------------------------------------------------------
    # 5. VERIFY OUTBOUND /go/ REDIRECT INTEGRITY (FIX 2)
    # -------------------------------------------------------------------------
    print("\n--- 5. Testing Outbound /go/ Redirect Integrity ---")
    first_offer = first_p["offers"][0]
    offer_id = first_offer["id"]
    expected_destination = first_offer["target_url"]

    # Test JSON mode
    resp_track_json = client.post(f"/api/v1/track/offer/{offer_id}?format=json")
    assert resp_track_json.status_code == 200, f"Expected 200, got {resp_track_json.status_code}"
    track_data = resp_track_json.json()
    assert track_data["redirect_url"] == expected_destination, f"Redirect URL mismatch: {track_data['redirect_url']} != {expected_destination}"
    assert track_data["clicks"] >= 1, "Clicks count must be >= 1"

    # Test HTTP 302 redirect mode
    resp_redirect = client.get(f"/go/offer/{offer_id}", follow_redirects=False)
    assert resp_redirect.status_code == 302, f"Expected 302 Found, got {resp_redirect.status_code}"
    redirect_location = resp_redirect.headers.get("location")
    assert redirect_location == expected_destination, f"Location header mismatch: {redirect_location} != {expected_destination}"
    print(f"[OK] /go/offer/{offer_id} correctly issued HTTP 302 redirect directly to:")
    print(f"     {redirect_location}")

    # -------------------------------------------------------------------------
    # 6. VERIFY HOTLINK-SAFE IMAGE PROXY
    # -------------------------------------------------------------------------
    print("\n--- 6. Testing Hotlink-Safe Image Proxy Endpoint ---")
    sample_img = first_p["image_url"]
    if sample_img.startswith("http"):
        proxy_url = f"/api/v1/image-proxy?url={sample_img}"
        resp_proxy = client.get(proxy_url)
        assert resp_proxy.status_code in (200, 307, 302), f"Expected 200 or redirect, got {resp_proxy.status_code}"
        print(f"[OK] Proxy responded with status {resp_proxy.status_code} for image.")

    # -------------------------------------------------------------------------
    # 7. VERIFY DATABASE PERSISTENCE & HOMEPAGE ISOLATION
    # -------------------------------------------------------------------------
    print("\n--- 7. Verifying Database Schema & Non-Pinned Isolation ---")
    db = SessionLocal()
    try:
        pinned_count = db.query(Product).filter(Product.is_pinned_homepage.is_(True)).count()
        unpinned_count = db.query(Product).filter(Product.is_pinned_homepage.is_(False)).count()
        print(f"[OK] SQLite jachai.db verified:")
        print(f"     - Pinned Homepage Seed Products: {pinned_count}")
        print(f"     - Dynamically Scraped Live Search Products: {unpinned_count}")
        assert unpinned_count >= 1, "Dynamic searches must persist as unpinned records"
    finally:
        db.close()

    print("\n" + "=" * 70)
    print("ALL MILESTONE 5.1 VERIFICATION SUITES PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_verification()
