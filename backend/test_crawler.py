import sys
import json

# Ensure Windows PowerShell console safely renders UTF-8 Bengali characters
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient

from crawler import extract_price_from_html, parse_bdt_price
from database import Base, SessionLocal, engine
from main import app
from seed import seed_database


def run_crawler_verification():
    print("==================================================")
    print("TEST 1: BILINGUAL BDT PRICE PARSER")
    print("==================================================")

    # Test 1: Bengali numerals with currency symbol and commas
    price_bn = parse_bdt_price("৳ ১,৪৬,৯৯০")
    print(f"parse_bdt_price('৳ ১,৪৬,৯৯০') -> {price_bn}")
    assert price_bn == 146990, f"Expected 146990, got {price_bn}"

    # Test 2: English formatting with Tk. and slash-hyphen
    price_en = parse_bdt_price("Tk. 85,555/-")
    print(f"parse_bdt_price('Tk. 85,555/-') -> {price_en}")
    assert price_en == 85555, f"Expected 85555, got {price_en}"

    # Test 3: Sanity bound filter (< 50 discount percentage ignored)
    price_mixed = parse_bdt_price("Flat 15% OFF! Today ৳4,890 only")
    print(f"parse_bdt_price('Flat 15% OFF! Today ৳4,890 only') -> {price_mixed}")
    assert price_mixed == 4890, f"Expected 4890, got {price_mixed}"

    # Test 4: Extreme out-of-range sanity checks
    assert parse_bdt_price("৳20") is None, "Expected None for price < 50"
    assert parse_bdt_price("৳90,000,000") is None, "Expected None for price > 50,000,000"
    print("✓ All BDT price parser tests passed!")

    print("\n==================================================")
    print("TEST 2: MULTI-STRATEGY HTML EXTRACTOR")
    print("==================================================")

    # Strategy A: Custom CSS Selector
    html_custom = """
    <html>
      <body>
        <div class="product-wrap">
          <span class="custom-startech-price">৳ ৫২,৫০০</span>
        </div>
      </body>
    </html>
    """
    price_a, in_stock_a = extract_price_from_html(html_custom, css_selector=".custom-startech-price")
    print(f"Strategy A (Custom CSS): price={price_a}, in_stock={in_stock_a}")
    assert price_a == 52500
    assert in_stock_a is True

    # Strategy B: OpenGraph / Meta Tags
    html_meta = """
    <html>
      <head>
        <meta property="product:price:amount" content="7990" />
      </head>
      <body>
        <h1>Handcrafted Jamdani Saree</h1>
      </body>
    </html>
    """
    price_b, in_stock_b = extract_price_from_html(html_meta, css_selector=None)
    print(f"Strategy B (OpenGraph Meta): price={price_b}, in_stock={in_stock_b}")
    assert price_b == 7990
    assert in_stock_b is True

    # Strategy C: JSON-LD Schema.org Product / Offers
    json_ld_data = {
        "@context": "https://schema.org/",
        "@type": "Product",
        "name": "Samsung Galaxy S24 Ultra",
        "offers": {
            "@type": "Offer",
            "priceCurrency": "BDT",
            "price": "128900",
            "availability": "https://schema.org/InStock"
        }
    }
    html_jsonld = f"""
    <html>
      <head>
        <script type="application/ld+json">
        {json.dumps(json_ld_data)}
        </script>
      </head>
      <body>
        <h1>Samsung S24 Ultra</h1>
      </body>
    </html>
    """
    price_c, in_stock_c = extract_price_from_html(html_jsonld, css_selector=None)
    print(f"Strategy C (JSON-LD): price={price_c}, in_stock={in_stock_c}")
    assert price_c == 128900
    assert in_stock_c is True

    # Stock Out Detection
    html_stock_out = """
    <html>
      <body>
        <span class="product-price">৳ 3,650</span>
        <div class="badge">Stock Out</div>
      </body>
    </html>
    """
    price_stock, in_stock_flag = extract_price_from_html(html_stock_out, css_selector=".product-price")
    print(f"Stock Detection: price={price_stock}, in_stock={in_stock_flag}")
    assert price_stock == 3650
    assert in_stock_flag is False
    print("✓ All HTML extractor tests passed!")

    print("\n==================================================")
    print("TEST 3: WEBCRAWLER REST ENDPOINTS & SPIDER HEALTH")
    print("==================================================")
    # Ensure database is prepared
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

    client = TestClient(app)

    # 1. Test POST /api/v1/admin/crawler/run (Batch Spider Run)
    res_run = client.post("/api/v1/admin/crawler/run?simulate=true")
    print(f"POST /api/v1/admin/crawler/run: status {res_run.status_code}")
    assert res_run.status_code == 200
    run_data = res_run.json()
    print(f"  - Total Checked: {run_data['total_checked']}")
    print(f"  - Updated Count: {run_data['updated_count']}")
    print(f"  - Healthy Spiders: {run_data['healthy_count']}")
    print(f"  - Slow Spiders: {run_data['slow_count']}")
    print(f"  - Synced At: {run_data['synced_at']}")
    assert run_data["total_checked"] > 0
    assert "products" in run_data and len(run_data["products"]) > 0

    # 2. Test GET /api/v1/admin/crawler/health (Spider Health Matrix)
    res_health = client.get("/api/v1/admin/crawler/health")
    print(f"GET /api/v1/admin/crawler/health: status {res_health.status_code}")
    assert res_health.status_code == 200
    health_matrix = res_health.json()
    print(f"  - Tracked Spiders in Matrix: {len(health_matrix)}")
    assert len(health_matrix) > 0
    first_spider = health_matrix[0]
    print(f"  - Sample Spider: {first_spider['store_name']} ({first_spider['domain']}) -> {first_spider['spider_status']}")
    assert "spider_status" in first_spider
    assert "domain" in first_spider

    # 3. Test POST /api/v1/admin/crawler/run/{product_id} (Per-Product Rescrape)
    prod_id = health_matrix[0]["product_id"]
    res_prod_scrape = client.post(f"/api/v1/admin/crawler/run/{prod_id}?simulate=true")
    print(f"POST /api/v1/admin/crawler/run/{prod_id}: status {res_prod_scrape.status_code}")
    assert res_prod_scrape.status_code == 200
    assert res_prod_scrape.json()["total_checked"] > 0

    # 4. Test POST /api/v1/admin/crawler/offer/{offer_id} (Per-Offer Rescrape)
    off_id = health_matrix[0]["id"]
    res_off_scrape = client.post(f"/api/v1/admin/crawler/offer/{off_id}?simulate=true")
    print(f"POST /api/v1/admin/crawler/offer/{off_id}: status {res_off_scrape.status_code}")
    assert res_off_scrape.status_code == 200
    assert res_off_scrape.json()["id"] == off_id

    print("\n==================================================")
    print("ALL CRAWLER & SPIDER HEALTH TESTS PASSED (100% OK)")
    print("==================================================")


if __name__ == "__main__":
    run_crawler_verification()
