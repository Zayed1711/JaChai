from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
     inspect,
    text,
)
from sqlalchemy.orm import relationship
try:
    from .database import Base, engine
except ImportError:
    from database import Base, engine


class Billboard(Base):
    __tablename__ = "billboards"

    id = Column(Integer, primary_key=True, index=True)
    sponsor_en = Column(String(255), nullable=False)
    sponsor_bn = Column(String(255), nullable=False)
    headline_en = Column(String(255), nullable=False)
    headline_bn = Column(String(255), nullable=False)
    category_badge = Column(String(100), nullable=False)
    starting_price = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500), nullable=False)
    target_url = Column(String(500), default="/", nullable=False)
    campaign_start = Column(String(100), nullable=True)
    campaign_end = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)


class SpotlightCard(Base):
    __tablename__ = "spotlight_cards"

    id = Column(Integer, primary_key=True, index=True)
    slot_code = Column(String(50), nullable=False)
    brand_title_en = Column(String(255), nullable=False)
    brand_title_bn = Column(String(255), nullable=False)
    tagline_en = Column(String(255), nullable=False)
    tagline_bn = Column(String(255), nullable=False)
    starting_price = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500), nullable=False)
    target_url = Column(String(500), default="/", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)


class TickerAd(Base):
    __tablename__ = "ticker_ads"

    id = Column(Integer, primary_key=True, index=True)
    text_en = Column(String(500), nullable=False)
    text_bn = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    glide_speed_sec = Column(Integer, default=55, nullable=False)
    priority_order = Column(Integer, default=0, nullable=False)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    title_en = Column(String(255), index=True, nullable=False)
    title_bn = Column(String(255), nullable=False)
    category = Column(String(100), index=True, nullable=False)
    image_url = Column(String(500), nullable=False)
    specs_summary = Column(Text, nullable=True)
    price_30d_ago = Column(Integer, default=0, nullable=False)
    price_15d_ago = Column(Integer, default=0, nullable=False)
    is_pinned_homepage = Column(Boolean, default=True, nullable=False)
    homepage_slot_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    offers = relationship(
        "StoreOffer",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="StoreOffer.current_price.asc()"
    )
    price_history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="PriceHistory.recorded_at.asc()"
    )


class StoreOffer(Base):
    __tablename__ = "store_offers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    store_name = Column(String(255), index=True, nullable=False)
    source_type = Column(String(50), default="crawler", nullable=False)
    target_url = Column(String(500), default="https://", nullable=False)
    website_url = Column(String(500), nullable=True)
    facebook_url = Column(String(500), nullable=True)
    css_selector = Column(String(255), nullable=True)
    current_price = Column(Integer, nullable=False, default=0)
    original_price = Column(Integer, nullable=False, default=0)
    cod_terms_en = Column(String(255), default="Cash on Delivery", nullable=False)
    cod_terms_bn = Column(String(255), default="ক্যাশ অন ডেলিভারি", nullable=False)
    warranty_text = Column(String(255), default="Official Warranty", nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    spider_status = Column(String(50), default="healthy", nullable=False)
    last_synced_at = Column(String(100), default="Just now", nullable=False)
    is_preseeded = Column(Boolean, default=True, nullable=False)
    is_sponsored = Column(Boolean, default=False, nullable=False)
    trust_score = Column(Integer, default=95, nullable=False)
    trust_badge = Column(String(100), default="Verified Safe", nullable=False)
    risk_level = Column(String(50), default="low", nullable=False)
    discount_tag = Column(String(100), nullable=True)
    discount_pct = Column(Integer, nullable=True)
    clicks = Column(Integer, default=0, nullable=False)

    product = relationship("Product", back_populates="offers")

    @property
    def price_bdt(self) -> int:
        return self.current_price or 0


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    recorded_price = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="price_history")


class AdLead(Base):
    __tablename__ = "ad_leads"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    selected_tier = Column(String(100), nullable=False)
    budget_note = Column(Text, nullable=True)
    status = Column(String(50), default="Pending", nullable=False)
    created_at = Column(String(100), default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M"), nullable=False)


class ClickLog(Base):
    __tablename__ = "click_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(50), index=True, nullable=False)
    target_id = Column(Integer, index=True, nullable=False)
    brand_or_store_name = Column(String(255), nullable=False)
    device_type = Column(String(50), default="desktop", nullable=False)
    destination_url = Column(String(500), nullable=False)
    clicked_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class HomepageBlock(Base):
    __tablename__ = "homepage_blocks"

    id = Column(Integer, primary_key=True, index=True)
    slot_order = Column(Integer, default=1, nullable=False)
    title_en = Column(String(255), nullable=False)
    title_bn = Column(String(255), nullable=False)
    subtitle_en = Column(String(255), nullable=True)
    subtitle_bn = Column(String(255), nullable=True)
    search_query = Column(String(255), nullable=False)
    category = Column(String(100), default="All", nullable=False)
    image_url = Column(String(500), nullable=False)
    badge_text = Column(String(100), default="HOT COMPARE", nullable=True)
    starting_price_bdt = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


def ensure_schema_migrations():
    """Auto-adds missing columns and performance indexes to existing SQLite DBs without losing data."""
    try:
        insp = inspect(engine)
        if "store_offers" in insp.get_table_names():
            cols = {c["name"] for c in insp.get_columns("store_offers")}
            if "is_sponsored" not in cols:
                with engine.begin() as conn:
                    conn.execute(text("ALTER TABLE store_offers ADD COLUMN is_sponsored BOOLEAN NOT NULL DEFAULT 0"))
        with engine.begin() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_products_title_en ON products(title_en)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_store_offers_store_name ON store_offers(store_name)"))
    except Exception:
        pass


ensure_schema_migrations()