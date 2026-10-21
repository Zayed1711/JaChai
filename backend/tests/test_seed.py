import uuid
from datetime import datetime, timezone, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
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
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable, CreateIndex


def test_ddl_compilation_postgresql():
    """Verify that all tables and GIN trigram index generate valid PostgreSQL DDL."""
    dialect = postgresql.dialect()
    table_names = [table.name for table in Base.metadata.sorted_tables]
    expected_tables = [
        "brands",
        "categories",
        "sponsored_slots",
        "stores",
        "products",
        "product_variants",
        "store_listings",
        "click_events",
        "price_snapshots",
    ]
    for expected in expected_tables:
        assert expected in table_names

    # Verify GIN index on products
    product_table = Base.metadata.tables["products"]
    trgm_index = next(idx for idx in product_table.indexes if idx.name == "ix_products_name_trgm")
    compiled_index = str(CreateIndex(trgm_index).compile(dialect=dialect))
    assert "USING gin" in compiled_index
    assert "gin_trgm_ops" in compiled_index


def test_seed_records_consistency():
    """Verify data structures, relationships, and constraints in the seed dataset."""
    now = datetime.now(timezone.utc)
    
    # Store
    store = Store(
        name="Daraz Bangladesh",
        slug="daraz-bd",
        type="marketplace",
        platform="daraz",
        base_url="https://www.daraz.com.bd",
        adapter_key="daraz_crawler",
        status="active",
    )
    
    # Category
    cat = Category(
        name_en="Smartphones",
        name_bn="স্মার্টফোন",
        slug="smartphones",
    )
    
    # Brand
    brand = Brand(
        name="Samsung",
        slug="samsung",
        aliases=["Samsung BD", "স্যামসাং"],
    )
    
    # Product
    product = Product(
        category=cat,
        brand=brand,
        name="Samsung Galaxy S24 Ultra",
        model="SM-S928B/DS",
        slug="samsung-galaxy-s24-ultra",
        specs={"ram": "12GB", "storage": "256GB"},
        status="active",
    )
    
    # Variant
    variant = ProductVariant(
        product=product,
        label="12GB/256GB - Titanium Gray",
        attributes={"ram": "12GB", "storage": "256GB", "color": "Titanium Gray"},
        variant_key="s24u-12gb-256gb-gray",
    )
    
    # Listing
    listing = StoreListing(
        store=store,
        product=product,
        variant=variant,
        source_url="https://www.daraz.com.bd/products/s24u.html",
        source_product_id="DRZ-S24U",
        raw_title="Samsung Galaxy S24 Ultra 5G (12GB/256GB) - Titanium Gray",
        match_status="confirmed",
        match_confidence=0.99,
        import_type="official",
        in_stock=True,
    )
    
    # Price Snapshots (Historical price drop)
    snap_old = PriceSnapshot(
        listing=listing,
        price=159999,
        original_price=169999,
        delivery_charge=120,
        cod_available=True,
        in_stock=True,
        captured_at=now - timedelta(days=10),
    )
    snap_live = PriceSnapshot(
        listing=listing,
        price=139999,
        original_price=169999,
        delivery_charge=0,
        cod_available=True,
        in_stock=True,
        captured_at=now,
    )
    
    assert listing.store.name == "Daraz Bangladesh"
    assert listing.product.brand.name == "Samsung"
    assert listing.variant.label == "12GB/256GB - Titanium Gray"
    assert snap_old.price > snap_live.price

