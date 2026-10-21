import sys
from fastapi.testclient import TestClient
from database import Base, SessionLocal, engine
from models import Product, Billboard, SpotlightCard, TickerAd, StoreOffer, AdLead
from seed import seed_database
from main import app

def run_tests():
    print("==================================================")
    print("STEP 1: CREATING DATABASE TABLES...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    print("\nSTEP 2: RUNNING INITIAL SEEDER...")
    db = SessionLocal()
    seed_database(db)
    
    # Verify seeded counts
    billboard_count = db.query(Billboard).count()
    spotlight_count = db.query(SpotlightCard).count()
    ticker_count = db.query(TickerAd).count()
    product_count = db.query(Product).count()
    offer_count = db.query(StoreOffer).count()
    lead_count = db.query(AdLead).count()
    db.close()

    print(f"Billboards: {billboard_count}")
    print(f"Spotlights: {spotlight_count}")
    print(f"Tickers: {ticker_count}")
    print(f"Products: {product_count}")
    print(f"Store Offers: {offer_count}")
    print(f"Ad Leads: {lead_count}")

    assert billboard_count >= 4, f"Expected at least 4 billboards, got {billboard_count}"
    assert spotlight_count >= 2, f"Expected at least 2 spotlights, got {spotlight_count}"
    assert ticker_count >= 6, f"Expected at least 6 tickers, got {ticker_count}"
    assert product_count >= 10, f"Expected at least 10 products, got {product_count}"
    assert offer_count >= 20, f"Expected at least 20 offers, got {offer_count}"
    assert lead_count >= 2, f"Expected at least 2 leads, got {lead_count}"

    print("\nSTEP 3: TESTING REST ENDPOINTS WITH TESTCLIENT...")
    client = TestClient(app)

    # 1. Test Storefront Init
    res_init = client.get("/api/v1/storefront/init")
    print(f"GET /api/v1/storefront/init: status {res_init.status_code}")
    assert res_init.status_code == 200, f"Init failed: {res_init.text}"
    init_data = res_init.json()
    assert len(init_data["billboards"]) >= 4
    assert len(init_data["spotlight_cards"]) >= 2
    assert len(init_data["ticker_ads"]) >= 6
    assert init_data["glide_speed_sec"] == 55
    assert len(init_data["products"]) >= 10

    # Verify computed fields on products
    first_product = init_data["products"][0]
    print(f"Sample Product: {first_product['title_en']}")
    print(f"  - Lowest Price: {first_product['lowest_price']}")
    print(f"  - Highest Original Price: {first_product['highest_original_price']}")
    print(f"  - Discount: -{first_product['discount_percent']}%")
    print(f"  - Store Count: {first_product['store_count']}")
    assert first_product["lowest_price"] > 0
    assert first_product["store_count"] > 0
    # Verify offers are sorted ascending
    prices = [o["current_price"] for o in first_product["offers"]]
    assert prices == sorted(prices), f"Offers not sorted ascending: {prices}"

    # 2. Test Product Search and Category Filter
    res_search = client.get("/api/v1/products?q=jamdani")
    print(f"GET /api/v1/products?q=jamdani: status {res_search.status_code}, found {len(res_search.json())}")
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1

    res_cat = client.get("/api/v1/products?category=fashion")
    print(f"GET /api/v1/products?category=fashion: status {res_cat.status_code}, found {len(res_cat.json())}")
    assert res_cat.status_code == 200
    assert len(res_cat.json()) >= 2

    # 3. Test Product Detail & Offers
    res_offers = client.get("/api/v1/products/jamdani-saree/offers")
    print(f"GET /api/v1/products/jamdani-saree/offers: status {res_offers.status_code}")
    assert res_offers.status_code == 200
    offers_data = res_offers.json()
    assert "price_history" in offers_data
    assert len(offers_data["price_history"]) >= 3

    # 4. Test Public Ad Lead submission
    new_lead_payload = {
        "brand_name": "Apex Footwear Bangladesh",
        "contact_phone": "+8801912345678",
        "selected_tier": "Partner Spotlight Slot #02",
        "budget_note": "Quarterly placement request"
    }
    res_lead = client.post("/api/v1/leads", json=new_lead_payload)
    print(f"POST /api/v1/leads: status {res_lead.status_code}")
    assert res_lead.status_code == 201
    lead_resp = res_lead.json()
    assert lead_resp["brand_name"] == "Apex Footwear Bangladesh"
    assert lead_resp["status"] == "Pending"

    # 5. Test Admin Overview
    res_admin = client.get("/api/v1/admin/overview")
    print(f"GET /api/v1/admin/overview: status {res_admin.status_code}")
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert len(admin_data["billboards"]) >= 4
    assert len(admin_data["products"]) >= 10
    assert len(admin_data["ad_leads"]) >= 3

    # 6. Test Admin Lead Status Update
    lead_id = lead_resp["id"]
    res_lead_update = client.put(f"/api/v1/admin/leads/{lead_id}", json={"status": "Paid via bKash/Nagad"})
    print(f"PUT /api/v1/admin/leads/{lead_id}: status {res_lead_update.status_code}")
    assert res_lead_update.status_code == 200
    assert res_lead_update.json()["status"] == "Paid via bKash/Nagad"

    # 7. Test Admin Ticker Speed Update
    res_speed = client.put("/api/v1/admin/tickers/speed", json={"glide_speed_sec": 45})
    print(f"PUT /api/v1/admin/tickers/speed: status {res_speed.status_code}")
    assert res_speed.status_code == 200
    assert res_speed.json()["glide_speed_sec"] == 45

    # 8. Test Admin Offer Creation & Re-sorting / Trend update
    prod_id = first_product["id"]
    new_offer_payload = {
        "product_id": prod_id,
        "store_name": "Test F-Commerce Boutique",
        "source_type": "f_commerce",
        "target_url": "https://facebook.com/testboutique",
        "current_price": 7500,
        "original_price": 9500,
        "cod_terms_en": "Cash on Delivery",
        "cod_terms_bn": "ক্যাশ অন ডেলিভারি",
        "warranty_text": "Authentic Fabric",
        "in_stock": True,
        "spider_status": "healthy"
    }
    res_new_offer = client.post("/api/v1/admin/offers", json=new_offer_payload)
    print(f"POST /api/v1/admin/offers: status {res_new_offer.status_code}")
    assert res_new_offer.status_code == 201

    # Verify that the new lowest price is reflected on the product
    res_check_prod = client.get("/api/v1/products/jamdani-saree/offers")
    updated_prod = res_check_prod.json()
    assert updated_prod["lowest_price"] == 7500
    print(f"New Lowest Price verified: {updated_prod['lowest_price']}")

    print("\n==================================================")
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("==================================================")

if __name__ == "__main__":
    run_tests()

