import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.crawlers.facebook import (
    FacebookFCommerceParser,
    parse_fcommerce_regex,
    normalize_bengali_numerals,
)
from app.matcher.engine import (
    normalize_text,
    check_hard_constraints,
    evaluate_match,
    trigram_similarity,
)
from app.models.schema import (
    Brand,
    Category,
    ClickEvent,
    PriceSnapshot,
    Product,
    ProductVariant,
    Store,
    StoreListing,
)


# ==========================================
# 1. Crawler Tests (Facebook Regex & SLM)
# ==========================================

def test_bengali_numeral_normalization():
    raw = "মূল্য: ৳ ১,৮৫০ (ঢাকার ভেতরে ডেলিভারি ৬০ টাকা)"
    normalized = normalize_bengali_numerals(raw)
    assert "1,850" in normalized
    assert "60" in normalized


def test_fcommerce_regex_extraction():
    sample_post = """
    🔥 HOT SUMMER DEAL 🔥
    Premium Old Money Textured Cuban Collar Shirt
    
    Price: ৳ 1,850 (Regular: ৳ 2,500)
    ক্যাশ অন ডেলিভারি এভেইলেবল!
    ঢাকার ভেতরে ৬০ টাকা ডেলিভারি চার্জ।
    ঢাকার বাইরে ১২০ টাকা।
    
    Inbox us to order!
    """
    offer = parse_fcommerce_regex(sample_post, post_url="https://facebook.com/posts/1", page_name="BD Fashion")
    
    assert offer.price == 1850
    assert offer.original_price == 2500
    assert offer.cod_available is True
    assert offer.delivery_charge == 60
    assert offer.in_stock is True
    assert "Premium Old Money" in offer.raw_title


@pytest.mark.anyio
async def test_facebook_slm_extraction_and_fallback():
    parser = FacebookFCommerceParser()
    sample_post = "Authentic Smart Watch. BDT 4500. Cash on delivery."

    # Test SLM Success branch
    mock_slm_response = {
        "raw_title": "Authentic Smart Watch",
        "price": 4500,
        "original_price": 5000,
        "delivery_charge": 80,
        "cod_available": True,
        "in_stock": True,
    }
    with patch("app.crawlers.facebook.extract_via_slm", new=AsyncMock(return_value=mock_slm_response)):
        offer = await parser.parse_post(sample_post, post_url="https://facebook.com/watch")
        assert offer.price == 4500
        assert offer.delivery_charge == 80
        assert offer.cod_available is True

    # Test SLM Failure branch (clean fallback to regex)
    with patch("app.crawlers.facebook.extract_via_slm", new=AsyncMock(return_value=None)):
        fallback_offer = await parser.parse_post(sample_post, post_url="https://facebook.com/watch")
        assert fallback_offer.price == 4500
        assert fallback_offer.cod_available is True


# ==========================================
# 2. Matcher Tests
# ==========================================

def test_text_normalization():
    raw = "HOT DEAL!! Samsung Galaxy S24 Ultra (12 GB RAM / 256 GB ROM) [Official BD Warranty]"
    clean = normalize_text(raw)
    assert "hot deal" not in clean
    assert "official bd" not in clean
    assert "12gb" in clean
    assert "256gb" in clean


def test_matcher_rejects_variant_mismatch():
    """Scraped title has 128GB but candidate product variant requires 256GB -> MUST REJECT."""
    scraped_title = "Samsung Galaxy S24 Ultra 8GB/128GB Titanium Gray"
    candidate_name = "Samsung Galaxy S24 Ultra"
    candidate_variants = [
        {
            "label": "12GB/256GB - Titanium Gray",
            "attributes": {"ram": "12gb", "storage": "256gb", "color": "Titanium Gray"},
        }
    ]

    result = evaluate_match(
        raw_title=scraped_title,
        candidate_name=candidate_name,
        candidate_variants=candidate_variants,
    )

    assert result.match_status == "unmatched"
    assert result.confidence == 0.0
    assert "conflict" in result.reason.lower()


def test_matcher_confirmed_on_exact_match():
    scraped_title = "Samsung Galaxy S24 Ultra (12GB/256GB) - Titanium Gray [Official BD]"
    candidate_name = "Samsung Galaxy S24 Ultra"
    candidate_variants = [
        {
            "label": "12GB/256GB - Titanium Gray",
            "attributes": {"ram": "12gb", "storage": "256gb", "color": "Titanium Gray"},
        }
    ]

    result = evaluate_match(
        raw_title=scraped_title,
        candidate_name=candidate_name,
        candidate_variants=candidate_variants,
    )

    assert result.match_status == "confirmed"
    assert result.confidence >= 0.85
    assert result.matched_variant is not None


# ==========================================
# 3. Core API Endpoints Tests
# ==========================================

# Setup an isolated test database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        store = Store(
            name="Daraz Bangladesh",
            slug="daraz-bd",
            type="marketplace",
            platform="daraz",
            base_url="https://www.daraz.com.bd",
            status="active",
        )
        cat = Category(name_en="Smartphones", slug="smartphones")
        brand = Brand(name="Samsung", slug="samsung", aliases=["Samsung Electronics"])
        db.add_all([store, cat, brand])
        db.flush()

        prod = Product(
            category_id=cat.id,
            brand_id=brand.id,
            name="Samsung Galaxy S24 Ultra",
            slug="samsung-galaxy-s24-ultra",
            model="SM-S928B",
            specs={"ram": "12GB"},
            status="active",
        )
        db.add(prod)
        db.flush()

        listing = StoreListing(
            store_id=store.id,
            product_id=prod.id,
            source_url="https://www.daraz.com.bd/products/s24u.html",
            raw_title="Samsung Galaxy S24 Ultra 5G (12GB/256GB)",
            match_status="confirmed",
            in_stock=True,
            status="active",
            last_checked_at=datetime.now(timezone.utc) - timedelta(days=2),  # Stale (> 24h)
        )
        db.add(listing)
        db.flush()

        snap = PriceSnapshot(
            listing_id=listing.id,
            price=139999,
            original_price=169999,
            delivery_charge=0,
            cod_available=True,
            in_stock=True,
            captured_at=datetime.now(timezone.utc),
        )
        db.add(snap)
        db.commit()
    finally:
        db.close()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_api_search_endpoint():
    res = client.get("/api/v1/search?q=Galaxy")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 1
    first_result = data["results"][0]
    assert first_result["slug"] == "samsung-galaxy-s24-ultra"
    assert first_result["lowest_price"] == 139999
    assert first_result["stores_count"] == 1


def test_api_offers_endpoint_with_swr():
    res = client.get("/api/v1/products/samsung-galaxy-s24-ultra/offers")
    assert res.status_code == 200
    data = res.json()
    assert data["offers_count"] == 1
    assert data["lowest_price"] == 139999

    offer = data["offers"][0]
    assert offer["current_price"] == 139999
    assert offer["is_stale"] is True  # Stale-While-Revalidate triggered
    assert offer["redirect_url"].startswith("/go/")
    assert len(offer["price_history"]) >= 1


def test_api_redirect_endpoint_and_click_tracking():
    # Retrieve listing ID from DB
    db = TestingSessionLocal()
    listing = db.query(StoreListing).first()
    listing_id = str(listing.id)
    initial_clicks = db.query(ClickEvent).count()
    db.close()

    # Call /go/{listing_id}
    res = client.get(
        f"/go/{listing_id}",
        headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)", "Referer": "https://google.com"},
        follow_redirects=False,
    )

    # Verify 302 Found redirect
    assert res.status_code == 302
    assert res.headers["location"] == "https://www.daraz.com.bd/products/s24u.html"

    # Verify ClickEvent recorded in database
    db = TestingSessionLocal()
    final_clicks = db.query(ClickEvent).count()
    assert final_clicks == initial_clicks + 1

    last_click = db.query(ClickEvent).order_by(ClickEvent.clicked_at.desc()).first()
    assert last_click.listing_id == listing.id
    assert "iPhone" in last_click.device
    assert last_click.referrer == "https://google.com"
    db.close()

