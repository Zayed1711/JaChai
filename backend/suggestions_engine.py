import re
import sqlite3
import os
from typing import List, Dict, Any, Optional

try:
    from bd_stores_registry import CATEGORY_REGISTRY_MAP, resolve_category_from_query
    from predetermined_catalog import CATEGORY_PREDETERMINED_CATALOG
except ImportError:
    from .bd_stores_registry import CATEGORY_REGISTRY_MAP, resolve_category_from_query
    from .predetermined_catalog import CATEGORY_PREDETERMINED_CATALOG

# Popular, verified models and canonical search SKUs in Bangladesh
POPULAR_SEEDED_MODELS: List[Dict[str, str]] = [
    # Smartwatches
    {"title": "Apple Watch Series 9 GPS (45mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Apple Watch Series 9 GPS (41mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Apple Watch Ultra 2 (49mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Apple Watch SE 2nd Gen (44mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Apple Watch Trail Loop / Ocean Band", "category_id": "mobile-gadgets", "category_name": "Watch Accessories"},
    {"title": "Samsung Galaxy Watch 6 (44mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Samsung Galaxy Watch 6 Classic (47mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Samsung Galaxy Watch Ultra (47mm)", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Samsung Galaxy Watch FE", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Galaxy Watch Magnetic Silicone Strap", "category_id": "mobile-gadgets", "category_name": "Watch Accessories"},
    {"title": "Amazfit Balance Smartwatch", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Amazfit GTR 4 Smart Watch", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Haylou Solar Plus RT3 Smart Watch", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},
    {"title": "Kieslect Calling Watch Kr Pro", "category_id": "mobile-gadgets", "category_name": "Smartwatches"},

    # Traditional Horology
    {"title": "Casio Edifice Chronograph EFR-539D", "category_id": "watches-horology", "category_name": "Watches & Horology"},
    {"title": "Casio G-Shock GA-2100 'CasiOak'", "category_id": "watches-horology", "category_name": "Watches & Horology"},
    {"title": "Casio Vintage Digital A168WA", "category_id": "watches-horology", "category_name": "Watches & Horology"},
    {"title": "Casio Enticer Men's Analog Watch", "category_id": "watches-horology", "category_name": "Watches & Horology"},
    {"title": "Tissot PRX Powermatic 80 Automatic", "category_id": "watches-horology", "category_name": "Watches & Horology"},
    {"title": "Seiko 5 Sports Automatic SRPD", "category_id": "watches-horology", "category_name": "Watches & Horology"},

    # Laptops & Computing
    {"title": "Asus Vivobook 15 X1504VA Core i5 13th Gen", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Asus Vivobook 16X OLED Creator Edition", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Asus Vivobook Go 14 Ryzen 5", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Asus Vivobook S 14 OLED Intel Evo", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Asus Zenbook 14 OLED Ultra 7", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Apple MacBook Air M3 13-inch (8-core GPU, 256GB)", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Apple MacBook Pro M3 Pro 14-inch (512GB)", "category_id": "laptops-pc", "category_name": "Laptops & PC"},
    {"title": "Lenovo IdeaPad Slim 3 Core i3 13th Gen", "category_id": "laptops-pc", "category_name": "Laptops & PC"},

    # Beauty & Skincare
    {"title": "Dr. Althea 345 Relief Cream (50ml)", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "Dr. Althea Vitamin C Boosting Serum", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "Beauty of Joseon Relief Sun Rice + Probiotics SPF50+", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "COSRX Advanced Snail 96 Mucin Power Essence", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "Skin1004 Madagascar Centella Ampoule", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "Round Lab Birch Juice Moisturizing Sunscreen", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},
    {"title": "CeraVe Daily Moisturizing Lotion (Normal to Dry Skin)", "category_id": "beauty-skincare", "category_name": "Beauty & Skincare"},

    # Mobile Phones
    {"title": "Samsung Galaxy S24 Ultra (12GB/256GB)", "category_id": "mobile-gadgets", "category_name": "Smartphones"},
    {"title": "Apple iPhone 15 Pro Max (256GB)", "category_id": "mobile-gadgets", "category_name": "Smartphones"},
    {"title": "Apple iPhone 15 (128GB)", "category_id": "mobile-gadgets", "category_name": "Smartphones"},
    {"title": "Apple iPhone 16 Pro Max", "category_id": "mobile-gadgets", "category_name": "Smartphones"},
    {"title": "Google Pixel 8 Pro (128GB)", "category_id": "mobile-gadgets", "category_name": "Smartphones"},
    {"title": "Xiaomi Redmi Note 13 Pro 4G", "category_id": "mobile-gadgets", "category_name": "Smartphones"},

    # Fashion & Panjabi / Saree
    {"title": "Cotton Panjabi (Semi-Fitted Traditional)", "category_id": "fashion-apparel", "category_name": "Fashion & Apparel"},
    {"title": "Kabli Panjabi Suit for Men", "category_id": "fashion-apparel", "category_name": "Fashion & Apparel"},
    {"title": "Old Money Textured Linen Shirt", "category_id": "fashion-apparel", "category_name": "Fashion & Apparel"},
    {"title": "Dhakai Jamdani Saree Handwoven Cotton", "category_id": "saree-boutiques", "category_name": "Saree & Boutiques"},
    {"title": "Katan Silk Bridal Saree", "category_id": "saree-boutiques", "category_name": "Saree & Boutiques"},

    # Cycles & Bicycles
    {"title": "Veloce Outrage 601 Mountain Bike MTB", "category_id": "bicycles-mtb", "category_name": "Cycles & Bicycles"},
    {"title": "Firefox Target 29 D Mountain Cycle", "category_id": "bicycles-mtb", "category_name": "Cycles & Bicycles"},
    {"title": "Walton Takyon Electric Bike Commuter", "category_id": "cycles-evs", "category_name": "Electric Bikes & EVs"},
]

# Query disambiguation rules when user query has intersection or ambiguity
DISAMBIGUATION_MAP = {
    "watch": [
        {"label": "Smartwatches (Apple, Galaxy, Amazfit)", "query": "smart watch", "category": "mobile-gadgets"},
        {"label": "Analog / Quartz (Casio, Tissot, Seiko)", "query": "casio watch", "category": "watches-horology"},
        {"label": "Watch Straps & Accessories", "query": "smartwatch strap", "category": "mobile-gadgets"},
    ],
    "watches": [
        {"label": "Smartwatches", "query": "smart watch", "category": "mobile-gadgets"},
        {"label": "Horology / Analog Watches", "query": "casio watch", "category": "watches-horology"},
    ],
    "smartwatch": [
        {"label": "Apple Watch Series & Ultra", "query": "apple watch", "category": "mobile-gadgets"},
        {"label": "Samsung Galaxy Watch", "query": "samsung galaxy watch", "category": "mobile-gadgets"},
        {"label": "Smartwatch Straps & Bands", "query": "smartwatch strap", "category": "mobile-gadgets"},
    ],
    "galaxy watch": [
        {"label": "Samsung Galaxy Smartwatches", "query": "samsung galaxy watch", "category": "mobile-gadgets"},
        {"label": "Galaxy Watch Bands & Straps", "query": "galaxy watch strap", "category": "mobile-gadgets"},
    ],
    "apple watch": [
        {"label": "Apple Watch (Series 9 / Ultra 2)", "query": "apple watch", "category": "mobile-gadgets"},
        {"label": "Apple Watch Straps & Bands", "query": "apple watch strap", "category": "mobile-gadgets"},
    ],
    "cream": [
        {"label": "Barrier & Relief Creams (Dr. Althea, Cica)", "query": "dr althea 345 relief cream", "category": "beauty-skincare"},
        {"label": "Moisturizers & Night Creams", "query": "face cream moisturizer", "category": "beauty-skincare"},
        {"label": "Sunscreen Creams SPF 50", "query": "spf 50 sunscreen", "category": "beauty-skincare"},
    ],
    "crem": [
        {"label": "Dr. Althea 345 Relief Cream", "query": "dr althea 345 relief cream", "category": "beauty-skincare"},
        {"label": "Beauty & Skincare Creams", "query": "face cream moisturizer", "category": "beauty-skincare"},
    ],
    "asus": [
        {"label": "Asus Vivobook Laptops", "query": "asus vivobook", "category": "laptops-pc"},
        {"label": "Asus Zenbook OLED Laptops", "query": "asus zenbook", "category": "laptops-pc"},
        {"label": "Asus ROG / TUF Gaming Laptops", "query": "asus rog laptop", "category": "laptops-pc"},
    ],
    "vivobook": [
        {"label": "Asus Vivobook 15 Core i5", "query": "asus vivobook 15", "category": "laptops-pc"},
        {"label": "Asus Vivobook Go Ryzen", "query": "asus vivobook go", "category": "laptops-pc"},
        {"label": "Asus Vivobook OLED Series", "query": "asus vivobook oled", "category": "laptops-pc"},
    ],
    "laptop": [
        {"label": "Asus Vivobook & Zenbook", "query": "asus vivobook", "category": "laptops-pc"},
        {"label": "Apple MacBook (M2 / M3)", "query": "macbook air", "category": "laptops-pc"},
        {"label": "Budget Laptops Under 50K", "query": "core i3 laptop", "category": "laptops-pc"},
    ],
    "bike": [
        {"label": "Bicycles & MTB (Gear Cycles)", "query": "mtb bicycle", "category": "bicycles-mtb"},
        {"label": "Electric Bikes & Scooters (Walton)", "query": "electric bike", "category": "cycles-evs"},
    ],
    "cycle": [
        {"label": "Pedal Bicycles & MTB", "query": "bicycle", "category": "bicycles-mtb"},
        {"label": "Electric Vehicles (EV)", "query": "electric bike", "category": "cycles-evs"},
    ],
    "tv": [
        {"label": "Smart 4K Android LED TVs", "query": "smart led tv 43", "category": "home-appliances"},
        {"label": "Sony Bravia & Samsung TVs", "query": "samsung 4k tv", "category": "home-appliances"},
    ]
}

# Global catalog index for ultra-fast autocomplete
_AUTOCOMPLETE_INDEX: List[Dict[str, str]] = []

def initialize_autocomplete_index():
    global _AUTOCOMPLETE_INDEX
    if _AUTOCOMPLETE_INDEX:
        return

    items: List[Dict[str, str]] = list(POPULAR_SEEDED_MODELS)
    seen = {m["title"].lower().strip() for m in items}

    # Ingest from predetermined catalog
    try:
        for cat_id, cat_data in CATEGORY_PREDETERMINED_CATALOG.items():
            meta = CATEGORY_REGISTRY_MAP.get(cat_id, {})
            c_name = meta.get("display_en", cat_id.replace("-", " ").title())
            for prod in cat_data.get("products", []):
                t = prod.get("title_en") or prod.get("title_bn")
                if t and t.lower().strip() not in seen:
                    items.append({
                        "title": t,
                        "category_id": cat_id,
                        "category_name": c_name,
                    })
                    seen.add(t.lower().strip())
    except Exception as e:
        print(f"[Autocomplete] Notice ingesting predetermined catalog: {e}")

    # Ingest distinct items from SQLite database if available
    db_path = os.path.join(os.path.dirname(__file__), "jachai.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT title_en, category FROM products WHERE title_en IS NOT NULL LIMIT 400")
            for row in cur.fetchall():
                t = (row[0] or "").strip()
                t_clean = re.sub(r"\(official.*?\)|\[.*?\]", "", t, flags=re.I).strip()
                if len(t_clean) >= 4 and t_clean.lower() not in seen and not any(b in t_clean.lower() for b in ["synthetic", "dummy", "test"]):
                    cat_display = row[1] or "General"
                    # Simple category mapping
                    cat_id = "mobile-gadgets"
                    for cid, cm in CATEGORY_REGISTRY_MAP.items():
                        if cm.get("display_en", "").lower() == cat_display.lower():
                            cat_id = cid
                            break
                    items.append({
                        "title": t_clean,
                        "category_id": cat_id,
                        "category_name": cat_display,
                    })
                    seen.add(t_clean.lower())
            conn.close()
        except Exception as e:
            print(f"[Autocomplete] Notice ingesting sqlite: {e}")

    _AUTOCOMPLETE_INDEX = items
    print(f"[Autocomplete] Indexed {len(_AUTOCOMPLETE_INDEX)} items for instant search suggestions.")

# Auto-initialize on module load
initialize_autocomplete_index()

def get_search_suggestions(raw_prefix: str, limit: int = 5) -> Dict[str, Any]:
    """
    Returns instant (< 5ms) typeahead suggestions and disambiguation pills.
    """
    q = (raw_prefix or "").strip().lower()
    if len(q) < 2:
        return {"query": raw_prefix, "suggestions": [], "did_you_mean": []}

    # Common Banglish and phonetic typo corrections
    q_norm = q
    q_norm = re.sub(r"\bathlea\b", "althea", q_norm)
    q_norm = re.sub(r"\bcrem\b", "cream", q_norm)
    q_norm = re.sub(r"\bsunscren\b", "sunscreen", q_norm)
    q_norm = re.sub(r"\bfasewash\b", "facewash", q_norm)
    q_norm = re.sub(r"\bmobail\b", "mobile", q_norm)

    tokens = q_norm.split()
    matched: List[Dict[str, str]] = []
    seen_titles = set()

    # Priority 1: Exact prefix start match
    for item in _AUTOCOMPLETE_INDEX:
        t_low = item["title"].lower()
        if t_low.startswith(q_norm) or t_low.startswith(q):
            if item["title"] not in seen_titles:
                matched.append(item)
                seen_titles.add(item["title"])
                if len(matched) >= limit:
                    break

    # Priority 2: All query tokens present in title
    if len(matched) < limit:
        for item in _AUTOCOMPLETE_INDEX:
            t_low = item["title"].lower()
            if all(tok in t_low for tok in tokens):
                if item["title"] not in seen_titles:
                    matched.append(item)
                    seen_titles.add(item["title"])
                    if len(matched) >= limit:
                        break

    # Extract Disambiguation Pills
    did_you_mean: List[Dict[str, str]] = []
    for d_key, pills in DISAMBIGUATION_MAP.items():
        if q == d_key or q_norm == d_key or (len(q) >= 3 and d_key.startswith(q)):
            did_you_mean = pills
            break

    if not did_you_mean:
        for d_key, pills in DISAMBIGUATION_MAP.items():
            if d_key in q_norm:
                did_you_mean = pills[:2]
                break

    return {
        "query": raw_prefix,
        "normalized_query": q_norm if q_norm != q else None,
        "suggestions": matched[:limit],
        "did_you_mean": did_you_mean,
    }
