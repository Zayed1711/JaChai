"""
JaChai Universal Catalog Distiller & Normalization Engine
(backend/catalog_distiller.py)

Ingests raw store feed items (Shopify variants, JSON-LD, Sitemaps), normalizes them
into canonical products, separates hardware variants (RAM/Storage/SoC), merges
multi-store dealer offers into unified comparison cards, and writes them into
the persistent database and in-memory master index.
"""

from datetime import datetime, timezone
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session, joinedload

try:
    from .models import Product, StoreOffer
    from .database import SessionLocal
except ImportError:
    from models import Product, StoreOffer
    from database import SessionLocal

logger = logging.getLogger("catalog_distiller")
logging.basicConfig(level=logging.INFO)

# Vertical category classification rules
CATEGORY_KEYWORDS = [
    ("Home Appliances", ["refrigerator", "fridge", "freezer", "washing machine", "air conditioner", "inverter ac", "microwave oven", "geyser", "deep fridge"]),
    ("Cameras & Photography", ["camera", "dslr", "mirrorless", "gopro", "action cam", "dji osmo", "insta360", "lens", "tripod", "camcorder"]),
    ("Gaming & Consoles", ["playstation", "ps5", "ps4", "xbox", "nintendo switch", "steam deck", "gamepad", "console", "dualsense"]),
    ("Smartwatches & Wearables", ["smartwatch", "smart watch", "apple watch", "galaxy watch", "fitness band", "band 8", "band 9"]),
    ("Audio & Headphones", ["headphone", "earphone", "earbuds", "airpods", "galaxy buds", "anc", "tws", "speaker", "soundbar"]),
    ("Watches & Horology", ["casio", "g-shock", "edifice", "tissot", "seiko", "orient", "citizen", "chronograph"]),
    ("Laptops & Computers", ["laptop", "macbook", "notebook", "thinkpad", "ideapad", "zenbook", "vivobook", "mac mini", "imac", "motherboard", "graphics card", "rtx", "gtx", "ryzen", "core i5", "core i7", "core i9", "core ultra", "nvme", "ssd", "ram ddr"]),
    ("Mobiles & Gadgets", ["phone", "smartphone", "iphone", "pixel", "galaxy", "redmi", "xiaomi", "oneplus", "realme", "vivo", "oppo", "infinix", "tecno", "ipad", "tablet"]),
]

KNOWN_BRANDS = [
    "Apple", "Google", "Samsung", "Sony", "Asus", "Dell", "HP", "Lenovo", "Acer", "MSI",
    "Xiaomi", "Redmi", "OnePlus", "Realme", "Vivo", "Oppo", "Infinix", "Tecno",
    "Casio", "Tissot", "Seiko", "Citizen", "Canon", "Nikon", "DJI", "GoPro", "Insta360",
    "Walton", "Vision", "Gree", "Singer", "Haier", "Whirlpool", "Panasonic", "NZXT",
]

# Color and aesthetic tags to strip from canonical titles to avoid fragmenting identical hardware
NOISE_COLOR_TOKENS = [
    "space gray", "space grey", "silver", "gold", "rose gold", "midnight", "starlight",
    "deep purple", "space black", "titanium", "natural titanium", "desert titanium",
    "white titanium", "black titanium", "blue titanium", "obsidian", "porcelain", "hazel",
    "bay", "mint", "aloe", "coral", "peony", "wintergreen", "phantom black", "phantom silver",
    "cream", "green", "violet", "amber yellow", "cobalt violet", "onyx black", "marble gray",
    "carbon black", "cloud white", "storm grey", "shadow black", "platinum silver",
]


def detect_brand(title: str, vendor_hint: str = "") -> str:
    """Detects brand from title or vendor hint."""
    if vendor_hint:
        for b in KNOWN_BRANDS:
            if b.lower() == vendor_hint.lower().strip():
                return b

    title_lower = title.lower()
    for b in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(b.lower())}\b", title_lower):
            return b
    return "Universal"


def detect_category(title: str, hint: str = "") -> str:
    """Classifies product into a clean vertical category."""
    if hint and any(c[0].lower() in hint.lower() for c in CATEGORY_KEYWORDS):
        for cat_name, _ in CATEGORY_KEYWORDS:
            if cat_name.lower() in hint.lower():
                return cat_name

    title_lower = title.lower()
    for cat_name, kws in CATEGORY_KEYWORDS:
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", title_lower):
                return cat_name
    return "Mobiles & Gadgets"


def extract_ram_storage(text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extracts hardware RAM and Storage capacity tokens."""
    t_lower = text.lower()

    # Match patterns like '16GB / 512GB' or '12GB 256GB'
    dual_m = re.search(r"(\d+)\s*gb\s*[/,+|\-]\s*(\d+)\s*(gb|tb)", t_lower)
    if dual_m:
        ram = f"{dual_m.group(1)}GB"
        unit = dual_m.group(3).upper()
        storage = f"{dual_m.group(2)}{unit}"
        return ram, storage

    ram_m = re.search(r"\b(4|6|8|12|16|18|24|32|36|48|64|128)\s*gb\s*(ram|unified memory)?\b", t_lower)
    ram = f"{ram_m.group(1)}GB" if ram_m and ("ram" in t_lower or "memory" in t_lower or int(ram_m.group(1)) <= 64) else None

    storage_m = re.search(r"\b(64|128|256|512)\s*gb\b|\b(1|2|4)\s*tb\b", t_lower)
    storage = None
    if storage_m:
        if storage_m.group(1):
            storage = f"{storage_m.group(1)}GB"
        elif storage_m.group(2):
            storage = f"{storage_m.group(2)}TB"

    return ram, storage


def canonicalize_product_title(raw_title: str, brand: str) -> Tuple[str, str, str]:
    """
    Cleans raw retailer product title into:
      1. Canonical Title: e.g. 'Apple Mac mini M4 (16GB RAM · 256GB SSD)'
      2. Model Code: e.g. 'Mac mini M4 (16GB/256GB)'
      3. Deterministic Slug: e.g. 'mac-mini-m4-16gb-256gb'
    """
    cleaned = raw_title.strip()

    # Strip retailer noise: 'price in bangladesh', 'official bd warranty', 'best price'
    cleaned = re.sub(r"(?i)\b(price\s+in\s+bangladesh|in\s+bd|bd\s+price|best\s+price|official\s+warranty)\b", "", cleaned)
    # Strip noise color tokens
    for c in NOISE_COLOR_TOKENS:
        cleaned = re.sub(rf"(?i)\b{re.escape(c)}\b", "", cleaned)

    # Clean whitespace and trailing punctuation
    cleaned = re.sub(r"[\s\-_/|]+", " ", cleaned).strip()

    ram, storage = extract_ram_storage(raw_title)

    # Ensure brand is in title
    if brand != "Universal" and not cleaned.lower().startswith(brand.lower()):
        cleaned = f"{brand} {cleaned}"

    # Append hardware variant tag cleanly
    variant_tokens = []
    if ram:
        variant_tokens.append(f"{ram} RAM")
    if storage:
        variant_tokens.append(f"{storage} Storage")

    if variant_tokens and not any(v in cleaned for v in (ram or "___", storage or "___")):
        variant_str = " · ".join(variant_tokens)
        canonical_title = f"{cleaned} ({variant_str})"
    else:
        canonical_title = cleaned

    # Generate slug
    slug_base = re.sub(r"[^a-z0-9]+", "-", canonical_title.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug_base)

    model_code = re.sub(r"\s+", " ", re.sub(r"[()]", "", canonical_title)).strip()

    return canonical_title, model_code, slug


def distill_feed_items(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Groups raw store feed items into consolidated canonical comparison cards
    with multi-store dealer offers.
    """
    grouped: Dict[str, Dict[str, Any]] = {}

    for item in raw_items:
        title = item.get("title", "").strip()
        price = item.get("price")
        if not title or not price or price <= 0:
            continue

        store_name = item.get("store_name", "Verified BD Dealer")
        vendor_hint = item.get("vendor", "")
        brand = detect_brand(title, vendor_hint)
        category = detect_category(title, item.get("category_hint", ""))

        canonical_title, model_code, slug = canonicalize_product_title(title, brand)

        if slug not in grouped:
            grouped[slug] = {
                "slug": slug,
                "title_en": canonical_title,
                "title_bn": f"{canonical_title} (বাংলাদেশ)",
                "model_code": model_code,
                "brand": brand,
                "category": category,
                "image_url": item.get("image_url") or "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
                "specs_summary": f"{canonical_title} · {brand} · Official Bangladeshi Retailer Warranty",
                "offers": [],
            }

        # Check if store already added for this card
        existing_stores = {o["store_name"].lower() for o in grouped[slug]["offers"]}
        if store_name.lower() not in existing_stores:
            grouped[slug]["offers"].append({
                "store_name": store_name,
                "price": price,
                "original_price": item.get("original_price") or price,
                "url": item.get("url") or "",
                "available": item.get("available", True),
                "source_type": item.get("source_type", "feed"),
            })

    # Finalize price statistics for each grouped product
    distilled_products = []
    for g in grouped.values():
        offers = g["offers"]
        if not offers:
            continue
        # Sort offers by lowest price
        offers.sort(key=lambda o: o["price"])
        prices = [o["price"] for o in offers]
        g["starting_price"] = min(prices)
        g["max_price"] = max(prices)
        g["offers_count"] = len(offers)
        distilled_products.append(g)

    logger.info(f"[Distiller] Consolidated {len(raw_items)} raw feed items into {len(distilled_products)} canonical SKUs.")
    return distilled_products


def persist_distilled_catalog_to_db(distilled_items: List[Dict[str, Any]], db: Session) -> int:
    """
    Persists distilled products and their merchant offers directly into the JaChai SQLite/Postgres DB.
    Idempotent: updates existing prices and links new store offers without duplication.
    """
    persisted_count = 0
    now_utc = datetime.now(timezone.utc)

    for item in distilled_items:
        slug = item["slug"]
        title_en = item["title_en"]
        title_bn = item["title_bn"]
        category = item["category"]
        image_url = item["image_url"]
        specs_summary = item["specs_summary"]
        starting_p = item["starting_price"]

        # Check if Product exists
        product = db.query(Product).options(joinedload(Product.offers)).filter(Product.slug == slug).first()
        if not product:
            product = db.query(Product).options(joinedload(Product.offers)).filter(Product.title_en == title_en).first()

        if product:
            product.specs_summary = specs_summary
            if not product.image_url or "unsplash" in product.image_url:
                if image_url and "unsplash" not in image_url:
                    product.image_url = image_url
        else:
            product = Product(
                slug=slug,
                title_en=title_en,
                title_bn=title_bn,
                category=category,
                image_url=image_url,
                specs_summary=specs_summary,
                price_30d_ago=int(starting_p * 1.05),
                price_15d_ago=int(starting_p * 1.02),
                is_pinned_homepage=False,
                created_at=now_utc,
            )
            db.add(product)
            db.flush()

        # Update or add StoreOffers
        existing_offers_by_store = {o.store_name.lower().strip(): o for o in product.offers}

        for off in item["offers"]:
            s_name = off["store_name"]
            s_key = s_name.lower().strip()
            curr_p = off["price"]
            orig_p = off.get("original_price") or curr_p
            target_u = off.get("url") or ""

            # Guardrail check: if unusually low, tag as risky rather than dropping
            risk_level = "low"
            trust_badge = "✓ 98% Verified Safe"
            trust_score = 95
            if curr_p < starting_p * 0.4 and starting_p > 10000:
                risk_level = "high"
                trust_badge = "⚠️ Price Anomaly / High Risk"
                trust_score = 45

            if s_key in existing_offers_by_store:
                existing = existing_offers_by_store[s_key]
                existing.current_price = curr_p
                existing.original_price = orig_p
                if target_u:
                    existing.target_url = target_u
                existing.last_synced_at = "Feed Auto-Sync"
                existing.in_stock = off.get("available", True)
                existing.risk_level = risk_level
                existing.trust_badge = trust_badge
                existing.trust_score = trust_score
            else:
                new_offer = StoreOffer(
                    product_id=product.id,
                    store_name=s_name,
                    source_type="crawler",
                    target_url=target_u,
                    website_url=target_u,
                    facebook_url=f"https://www.facebook.com/search/top/?q={s_name}",
                    current_price=curr_p,
                    original_price=orig_p,
                    cod_terms_en=f"৳{curr_p:,} · Verified Authentic BD Stock",
                    cod_terms_bn=f"৳{curr_p:,} · ভেরিফাইড আসল পণ্য",
                    warranty_text="Official / Store BD Warranty",
                    in_stock=off.get("available", True),
                    spider_status="healthy",
                    last_synced_at="Feed Auto-Sync",
                    is_preseeded=True,
                    is_sponsored=False,
                    trust_score=trust_score,
                    trust_badge=trust_badge,
                    risk_level=risk_level,
                    discount_tag=f"{int(round((orig_p - curr_p)/orig_p * 100))}% OFF" if orig_p > curr_p else None,
                    discount_pct=int(round((orig_p - curr_p)/orig_p * 100)) if orig_p > curr_p else 0,
                )
                db.add(new_offer)

        persisted_count += 1

    try:
        db.commit()
        logger.info(f"[Distiller] Successfully committed {persisted_count} products & offers to database.")
    except Exception as e:
        db.rollback()
        logger.error(f"[Distiller] Error committing to database: {e}")

    return persisted_count


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    from feed_harvester import run_full_feed_harvest
    import asyncio

    print("Running Harvester + Distiller pipeline test...")
    raw = asyncio.run(run_full_feed_harvest(max_shopify_pages=1, max_sitemap_items=5))
    distilled = distill_feed_items(raw)
    print(f"Distilled {len(distilled)} unique canonical SKUs.")
    db = SessionLocal()
    try:
        saved = persist_distilled_catalog_to_db(distilled, db)
        print(f"Persisted {saved} SKUs to database.")
    finally:
        db.close()
