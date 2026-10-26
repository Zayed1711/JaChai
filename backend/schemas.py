from urllib.parse import urlparse
from datetime import datetime
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator


# ==========================================
# 1. BILLBOARD SCHEMAS (Tier 1 Hero)
# ==========================================
class BillboardBase(BaseModel):
    sponsor_en: str
    sponsor_bn: str
    headline_en: str
    headline_bn: str
    category_badge: str
    starting_price: int
    image_url: str
    target_url: str = "/"
    campaign_start: Optional[str] = None
    campaign_end: Optional[str] = None
    is_active: bool = True
    display_order: int = 0


class BillboardCreate(BillboardBase):
    pass


class BillboardUpdate(BaseModel):
    sponsor_en: Optional[str] = None
    sponsor_bn: Optional[str] = None
    headline_en: Optional[str] = None
    headline_bn: Optional[str] = None
    category_badge: Optional[str] = None
    starting_price: Optional[int] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    campaign_start: Optional[str] = None
    campaign_end: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None


class BillboardResponse(BillboardBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0


# ==========================================
# 2. SPOTLIGHT CARD SCHEMAS (Tier 2 Slots)
# ==========================================
class SpotlightCardBase(BaseModel):
    slot_code: str
    brand_title_en: str
    brand_title_bn: str
    tagline_en: str
    tagline_bn: str
    starting_price: int
    image_url: str
    target_url: str = "/"
    is_active: bool = True


class SpotlightCardCreate(SpotlightCardBase):
    pass


class SpotlightCardUpdate(BaseModel):
    slot_code: Optional[str] = None
    brand_title_en: Optional[str] = None
    brand_title_bn: Optional[str] = None
    tagline_en: Optional[str] = None
    tagline_bn: Optional[str] = None
    starting_price: Optional[int] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    is_active: Optional[bool] = None


class SpotlightCardResponse(SpotlightCardBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0


# ==========================================
# 3. TICKER AD SCHEMAS (Tier 3 Marquee)
# ==========================================
class TickerAdBase(BaseModel):
    text_en: str
    text_bn: str
    is_active: bool = True
    glide_speed_sec: int = 55
    priority_order: int = 0


class TickerAdCreate(TickerAdBase):
    pass


class TickerAdUpdate(BaseModel):
    text_en: Optional[str] = None
    text_bn: Optional[str] = None
    is_active: Optional[bool] = None
    glide_speed_sec: Optional[int] = None
    priority_order: Optional[int] = None


class TickerSpeedUpdate(BaseModel):
    glide_speed_sec: int


class TickerAdResponse(TickerAdBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ==========================================
# 4. STORE OFFER SCHEMAS (Hybrid Crawler/F-Commerce)
# ==========================================
class StoreOfferBase(BaseModel):
    product_id: int
    store_name: str
    source_type: str = "crawler"  # 'crawler' or 'f_commerce'
    target_url: str = "https://"
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    css_selector: Optional[str] = None
    current_price: int
    original_price: int
    cod_terms_en: str = "Cash on Delivery"
    cod_terms_bn: str = "ক্যাশ অন ডেলিভারি"
    warranty_text: str = "Official Warranty"
    in_stock: Optional[bool] = True
    spider_status: str = "healthy"
    last_synced_at: str = "Just now"
    is_preseeded: Optional[bool] = None
    trust_score: Optional[int] = None
    trust_badge: Optional[str] = None
    risk_level: Optional[str] = None  # 'low', 'moderate', 'high'
    discount_tag: Optional[str] = None
    discount_pct: Optional[int] = None
    is_sponsored: Optional[bool] = False
    

class StoreOfferCreate(StoreOfferBase):
    pass


class StoreOfferUpdate(BaseModel):
    store_name: Optional[str] = None
    source_type: Optional[str] = None
    target_url: Optional[str] = None
    website_url: Optional[str] = None
    facebook_url: Optional[str] = None
    css_selector: Optional[str] = None
    current_price: Optional[int] = None
    original_price: Optional[int] = None
    cod_terms_en: Optional[str] = None
    cod_terms_bn: Optional[str] = None
    warranty_text: Optional[str] = None
    in_stock: Optional[bool] = None
    spider_status: Optional[str] = None
    last_synced_at: Optional[str] = None
    is_preseeded: Optional[bool] = None
    trust_score: Optional[int] = None
    trust_badge: Optional[str] = None
    risk_level: Optional[str] = None
    discount_tag: Optional[str] = None
    discount_pct: Optional[int] = None
    is_sponsored: Optional[bool] = None
    


class StoreOfferResponse(StoreOfferBase):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = 0
    clicks: Optional[int] = 0

    @model_validator(mode="after")
    def populate_links_and_trust(self) -> "StoreOfferResponse":
        if not self.id:
            self.id = abs(hash(f"{self.product_id}_{self.store_name}_{self.current_price}")) % 9000000 + 100000
        if self.is_sponsored is None:
            self.is_sponsored = False
        if self.in_stock is None:
            self.in_stock = True
        try:
            from bd_stores_registry import get_store_registry_meta, compute_trust_score
            meta = get_store_registry_meta(self.store_name)
            if not self.website_url and meta.get("website_url"):
                self.website_url = meta["website_url"]

            # Universal Deep Link Guard: NEVER allow broken /search?q= or /catalog/?q= URLs to escape to clients
            if self.target_url and ('{q}' in self.target_url or any(bad in self.target_url.lower() for bad in ("/search", "catalogsearch", "/catalog/?q=", "?s="))):
                parsed_t = urlparse(self.target_url)
                if parsed_t.netloc:
                    self.target_url = f"{parsed_t.scheme or 'https'}://{parsed_t.netloc}"
            if self.website_url and ('{q}' in self.website_url or any(bad in self.website_url.lower() for bad in ("/search", "catalogsearch", "/catalog/?q=", "?s="))):
                parsed_w = urlparse(self.website_url)
                if parsed_w.netloc:
                    self.website_url = f"{parsed_w.scheme or 'https'}://{parsed_w.netloc}" 
            if not self.facebook_url and meta.get("facebook_url"):
                self.facebook_url = meta["facebook_url"]

            # Strictly determine whether this merchant is preseeded in the curated registry
            if meta.get("is_preseeded") is True:
                self.is_preseeded = True
            elif self.is_preseeded is not True:
                self.is_preseeded = False

            if not self.discount_pct and self.original_price and self.current_price and self.original_price > self.current_price:
                self.discount_pct = int(round((self.original_price - self.current_price) / self.original_price * 100))
                if self.discount_pct >= 5 and not self.discount_tag:
                    self.discount_tag = f"{self.discount_pct}% OFF"

            trust_info = compute_trust_score(
                self.store_name,
                is_preseeded=bool(self.is_preseeded),
                cod_terms=self.cod_terms_en or "",
                price=float(self.current_price) if self.current_price else None,
            )
            if not self.trust_score:
                self.trust_score = trust_info["trust_score"]

            if self.is_preseeded:
                if not self.trust_badge:
                    self.trust_badge = trust_info["trust_badge"]
                if not self.risk_level:
                    self.risk_level = trust_info["risk_level"]
            else:
                # Unverified merchant: clearly mark as unverified
                if not self.risk_level or self.risk_level == "low":
                    self.risk_level = "moderate"
                self.trust_badge = "⚠️ Unverified Merchant · COD Only"
                self.trust_score = min(self.trust_score or 65, 65)

            # High risk or price anomaly overrides
            if self.risk_level == "high" or (self.trust_badge and "Risk" in self.trust_badge):
                self.risk_level = "high"
                self.trust_badge = "⚠️ Price Anomaly / High Risk"
        except Exception:
            pass
        return self


# ==========================================
# 5. PRICE HISTORY SCHEMAS
# ==========================================
class PriceHistoryBase(BaseModel):
    product_id: int
    recorded_price: int


class PriceHistoryCreate(PriceHistoryBase):
    pass


class PriceHistoryResponse(PriceHistoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recorded_at: datetime


# ==========================================
# 6. PRODUCT SCHEMAS (Catalog)
# ==========================================
class ProductBase(BaseModel):
    slug: str
    title_en: str
    title_bn: str
    category: str
    image_url: str
    specs_summary: Optional[str] = None
    price_30d_ago: Optional[int] = 0
    price_15d_ago: Optional[int] = 0
    variant: Optional[str] = None
    is_pinned_homepage: Optional[bool] = True
    homepage_slot_order: Optional[int] = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    slug: Optional[str] = None
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    specs_summary: Optional[str] = None
    price_30d_ago: Optional[int] = None
    price_15d_ago: Optional[int] = None
    variant: Optional[str] = None
    is_pinned_homepage: Optional[bool] = None
    homepage_slot_order: Optional[int] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    offers: List[StoreOfferResponse] = []

    @field_validator("offers", mode="after")
    @classmethod
    def sort_offers(cls, v: List[StoreOfferResponse]) -> List[StoreOfferResponse]:
      # Tier-2 Category Sponsors appear at top, followed by Verified Pre-seeded Partners,
      # sorted by lowest price within each group.
      return sorted(
          v,
          key=lambda x: (
              not getattr(x, "is_sponsored", False),
              not getattr(x, "is_preseeded", True),
              x.current_price,
          ),
      )
    
    @computed_field
    @property
    def lowest_price(self) -> int:
        active = [o for o in self.offers if o.in_stock]
        pool = active if active else self.offers
        return min((o.current_price for o in pool), default=0)

    @computed_field
    @property
    def highest_original_price(self) -> int:
        if not self.offers:
            return 0
        return max((o.original_price for o in self.offers), default=self.lowest_price)

    @computed_field
    @property
    def discount_percent(self) -> int:
        high = self.highest_original_price
        low = self.lowest_price
        if high > low and high > 0:
            return round(((high - low) / high) * 100)
        return 0

    @computed_field
    @property
    def store_count(self) -> int:
        return len(self.offers)


class ProductDetailResponse(ProductResponse):
    price_history: List[PriceHistoryResponse] = []


# ==========================================
# 7. AD LEAD SCHEMAS (Booking Inbox)
# ==========================================
class AdLeadBase(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=150)
    contact_phone: str = Field(..., min_length=3, max_length=50)
    selected_tier: str = Field(..., min_length=1, max_length=100)
    budget_note: Optional[str] = Field(None, max_length=500)


class AdLeadCreate(AdLeadBase):
    pass


class AdLeadUpdate(BaseModel):
    status: str  # 'Pending', 'Paid via bKash/Nagad', 'Live'


class AdLeadResponse(AdLeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = "Pending"
    created_at: str


# ==========================================
# 8. TRENDING CATEGORY SEARCH HUBS SCHEMAS
# ==========================================
class TrendingHubItem(BaseModel):
    id: str
    title_en: str
    title_bn: str
    subtitle_en: str
    subtitle_bn: str
    query_trigger: str
    badge_en: str = "🔥 Most Searched Today"
    badge_bn: str = "🔥 আজকের সবচেয়ে জনপ্রিয়"
    icon_name: str
    starting_price_bdt: int
    image_url: str


class TrendingHubsResponse(BaseModel):
    hubs: List[TrendingHubItem]


class HomepageBlockBase(BaseModel):
    slot_order: int = 1
    title_en: str
    title_bn: str
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    search_query: str
    category: str = "All"
    image_url: str
    badge_text: Optional[str] = "HOT COMPARE"
    starting_price_bdt: int = 0
    is_active: bool = True


class HomepageBlockCreate(HomepageBlockBase):
    pass


class HomepageBlockUpdate(BaseModel):
    slot_order: Optional[int] = None
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    search_query: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    badge_text: Optional[str] = None
    starting_price_bdt: Optional[int] = None
    is_active: Optional[bool] = None


class HomepageBlockResponse(HomepageBlockBase):
    id: int

    class Config:
        from_attributes = True


class HomepageSlotItem(BaseModel):
    slot_order: int  # 1 to 6
    product_id: Optional[int] = None
    product_slug: Optional[str] = None
    title_en: str
    title_bn: str
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    search_query: str
    category: str = "All"
    image_url: str
    badge_text: Optional[str] = "🔥 HOT COMPARE"
    starting_price_bdt: int = 0
    is_active: bool = True


class HomepageSlotsResponse(BaseModel):
    slots: List[HomepageSlotItem]
    available_products: List[dict] = []



# ==========================================
# COMPOSITE STOREFRONT & ADMIN SCHEMAS
# ==========================================
class StorefrontInitResponse(BaseModel):
    billboards: List[BillboardResponse]
    spotlight_cards: List[SpotlightCardResponse]
    ticker_ads: List[TickerAdResponse]
    glide_speed_sec: int
    products: List[ProductResponse]
    trending_hubs: Optional[List[TrendingHubItem]] = None
    homepage_blocks: Optional[List[HomepageBlockResponse]] = None


class AdminOverviewResponse(BaseModel):
    billboards: List[BillboardResponse]
    spotlight_cards: List[SpotlightCardResponse]
    spotlights: Optional[List[SpotlightCardResponse]] = None
    ticker_ads: List[TickerAdResponse]
    products: List[ProductResponse]
    store_offers: List[StoreOfferResponse]
    ad_leads: List[AdLeadResponse]
    homepage_blocks: Optional[List[HomepageBlockResponse]] = None


# ==========================================
# CRAWLER & SPIDER HEALTH SCHEMAS
# ==========================================
class SpiderHealthItem(BaseModel):
    id: Union[int, str]
    product_id: Optional[int] = 0
    store_name: str
    category: Optional[str] = "General"
    channel: Optional[str] = "WEBSITE"
    domain: str
    target_url: str
    css_selector: Optional[str] = None
    spider_status: str  # 'healthy', 'slow', 'broken'
    current_price: Optional[int] = 0
    latency_ms: Optional[int] = 120
    last_synced_at: str


class SpiderHealthMatrixResponse(BaseModel):
    total_spiders: int
    healthy_count: int
    slow_count: int
    broken_count: int
    spiders: List[SpiderHealthItem]


class SpiderPingRequest(BaseModel):
    store_name: Optional[str] = None
    domain: Optional[str] = None
    target_url: Optional[str] = None


class SpiderPingResponse(BaseModel):
    store_name: str
    domain: str
    status: str
    spider_status: str
    latency_ms: int
    last_synced: str
    selector: str


class SpiderRunStatusResponse(BaseModel):
    is_running: bool
    progress: int
    current_store: Optional[str] = None
    total_checked: int = 0
    total_stores: int = 361
    completed_stores: int = 0
    healthy_count: int = 0
    slow_count: int = 0
    broken_count: int = 0
    completed_at: Optional[str] = None
    started_at: Optional[float] = None
    error: Optional[str] = None


class CrawlerSummaryResponse(BaseModel):
    total_checked: int
    updated_count: int
    healthy_count: int
    slow_count: int
    broken_count: int
    synced_at: str
    results: List[dict] = []
    products: Optional[List[ProductResponse]] = None


# ==========================================
# CLICK LOG & OUTBOUND REDIRECT SCHEMAS
# ==========================================
class ClickLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    target_type: str
    target_id: int
    brand_or_store_name: str
    device_type: str
    destination_url: str
    clicked_at: datetime


# ==========================================
# AUTHENTICATION SCHEMAS
# ==========================================
class AdminLoginRequest(BaseModel):
    pin: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 43200


# ==========================================
# SPONSOR ROI & ANALYTICS SCHEMAS
# ==========================================
class SponsorCampaignAnalytics(BaseModel):
    id: int
    tier: str  # 'Tier 1 Billboard' or 'Tier 2 Spotlight'
    brand_name: str
    impressions: int
    clicks: int
    ctr_percent: float
    status: str  # 'Active' or 'Paused'
    whatsapp_report_text: str


class SponsorAnalyticsResponse(BaseModel):
    campaigns: List[SponsorCampaignAnalytics]
    top_stores: List[StoreOfferResponse]
    recent_clicks: List[ClickLogResponse]

# ==========================================
# HOT PRODUCTS PRICING SCHEMAS
# ==========================================
class HotProductStoreOffer(BaseModel):
    name: str
    price: int
    url: str
    status: str = "In Stock"


class HotProductResponse(BaseModel):
    id: int
    slug: str
    title_en: str
    title_bn: str
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    category_id: str
    search_query: str
    current_price: int
    previous_price: int
    unit_en: str
    unit_bn: str
    icon_name: str
    price_change_type: str  # "drop", "increase", "stable"
    price_change_amount: int
    price_change_percent: float
    stores: List[HotProductStoreOffer] = []
    latest_release_name: Optional[str] = None
    latest_release_price: Optional[int] = None
    latest_release_badge: Optional[str] = None
    latest_release_url: Optional[str] = None
    is_active: bool
    display_order: int
    last_calibrated_at: Optional[str] = None


class HotProductUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    current_price: Optional[int] = None
    previous_price: Optional[int] = None
    unit_en: Optional[str] = None
    unit_bn: Optional[str] = None
    icon_name: Optional[str] = None
    search_query: Optional[str] = None
    category_id: Optional[str] = None
    stores: Optional[List[HotProductStoreOffer]] = None
    latest_release_name: Optional[str] = None
    latest_release_price: Optional[int] = None
    latest_release_badge: Optional[str] = None
    latest_release_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

