import uuid
from datetime import datetime, timezone
import pytest
from app.models.schema import (
    Brand,
    Category,
    ClickEvent,
    PriceSnapshot,
    Product,
    ProductVariant,
    SponsoredSlot,
    Store,
    StoreListing,
)


def test_model_instantiation():
    """Verify that all core models instantiate with expected attributes and default UUIDs."""
    # Store
    store = Store(
        name="Daraz BD",
        slug="daraz-bd",
        type="marketplace",
        platform="daraz",
        base_url="https://www.daraz.com.bd",
        status="active",
    )
    assert store.name == "Daraz BD"
    assert store.slug == "daraz-bd"

    # Category
    cat = Category(
        name_en="Smartphones",
        name_bn="স্মার্টফোন",
        slug="smartphones",
    )
    assert cat.name_en == "Smartphones"

    # Brand
    brand = Brand(
        name="Samsung",
        slug="samsung",
        aliases=["Samsung BD", "স্যামসাং"],
    )
    assert brand.name == "Samsung"
    assert "স্যামসাং" in brand.aliases

    # Product
    prod = Product(
        category_id=uuid.uuid4(),
        brand_id=uuid.uuid4(),
        name="Samsung Galaxy S24 Ultra",
        model="SM-S928B/DS",
        slug="samsung-galaxy-s24-ultra",
        specs={"ram": "12GB"},
        status="active",
    )
    assert prod.name == "Samsung Galaxy S24 Ultra"

    # ProductVariant
    variant = ProductVariant(
        product_id=uuid.uuid4(),
        label="12GB/256GB - Titanium Gray",
        attributes={"storage": "256GB"},
        variant_key="s24u-12-256",
    )
    assert variant.label == "12GB/256GB - Titanium Gray"

    # StoreListing
    listing = StoreListing(
        store_id=uuid.uuid4(),
        product_id=prod.id,
        variant_id=variant.id,
        source_url="https://daraz.com.bd/s24u",
        raw_title="Samsung Galaxy S24 Ultra",
        match_status="confirmed",
        match_confidence=0.98,
        import_type="official",
        in_stock=True,
    )
    assert listing.match_status == "confirmed"

    # PriceSnapshot
    snap = PriceSnapshot(
        listing_id=listing.id,
        price=139999,
        original_price=169999,
        delivery_charge=0,
        cod_available=True,
        in_stock=True,
    )
    assert snap.price == 139999
    assert snap.delivery_charge == 0

    # ClickEvent
    click = ClickEvent(
        listing_id=listing.id,
        session_id="sess-12345",
        device="Mobile",
        referrer="https://facebook.com",
    )
    assert click.session_id == "sess-12345"

    # SponsoredSlot
    now = datetime.now(timezone.utc)
    slot = SponsoredSlot(
        sponsor_name="Mega Sale",
        placement="tornado_hero",
        target_url="https://daraz.com.bd/sale",
        image_url="https://daraz.com.bd/banner.jpg",
        starts_at=now,
        ends_at=now,
        is_active=True,
    )
    assert slot.sponsor_name == "Mega Sale"
    assert slot.is_active is True

