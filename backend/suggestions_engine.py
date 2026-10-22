import re
import sqlite3
import os
from typing import List, Dict, Any

# Standardized, high-ticket spec products in Bangladesh (Laptops, Phones, Smartwatches, Horology, Consoles, Cameras)
CLEAN_PRODUCT_CATALOG: List[str] = [
    # Smartwatches
    "Samsung Galaxy Watch 6 44mm",
    "Samsung Galaxy Watch 6 Classic 47mm",
    "Samsung Galaxy Watch 6 40mm",
    "Samsung Galaxy Watch Ultra 47mm",
    "Samsung Galaxy Watch FE",
    "Samsung Galaxy Watch 5 Pro",
    "Apple Watch Series 9 45mm GPS",
    "Apple Watch Series 9 41mm GPS",
    "Apple Watch Ultra 2 49mm Cellular",
    "Apple Watch SE 44mm 2nd Gen",
    "Apple Watch SE 40mm 2nd Gen",
    "Amazfit Balance Smartwatch",
    "Amazfit GTR 4 Smart Watch",
    "Amazfit Active Smart Watch",
    "Haylou Solar Plus RT3 Smart Watch",
    "Kieslect Calling Watch Kr Pro",

    # Traditional Horology
    "Casio Edifice Chronograph EFR-539D",
    "Casio Edifice Slim Sapphire EFR-S108D",
    "Casio G-Shock GA-2100 CasiOak",
    "Casio Vintage Digital A168WA",
    "Casio Enticer Men's Analog Watch",
    "Tissot PRX Powermatic 80 Automatic",
    "Seiko 5 Sports Automatic SRPD",

    # Laptops & Computing
    "Asus Vivobook 15 X1504VA Core i5",
    "Asus Vivobook 16X OLED Creator Edition",
    "Asus Vivobook Go 14 Ryzen 5",
    "Asus Vivobook S 14 OLED Intel Evo",
    "Asus Zenbook 14 OLED Ultra 7",
    "Apple MacBook Air M3 13-inch 256GB",
    "Apple MacBook Air M2 13-inch 256GB",
    "Apple MacBook Pro M3 Pro 14-inch 512GB",
    "Lenovo IdeaPad Slim 3 Core i3",
    "Dell Inspiron 15 Core i5",
    "HP Pavilion 15 Core i5",

    # Smartphones & Tablets
    "Samsung Galaxy S24 Ultra 256GB",
    "Samsung Galaxy S24 Plus 256GB",
    "Samsung Galaxy S23 Ultra",
    "Samsung Galaxy A55 5G",
    "Apple iPhone 15 Pro Max 256GB",
    "Apple iPhone 15 Pro 128GB",
    "Apple iPhone 15 128GB",
    "Apple iPhone 16 Pro Max",
    "Apple iPad Air M2 11-inch",
    "Apple iPad 10th Gen 64GB",
    "Google Pixel 8 Pro 128GB",
    "Google Pixel 8a 128GB",
    "Xiaomi Redmi Note 13 Pro 4G",
    "OnePlus 12 5G 256GB",

    # Gaming Consoles & Handhelds
    "Sony PlayStation 5 Slim Disc Edition",
    "Sony PlayStation 5 Digital Edition",
    "Sony PlayStation 4 Pro 1TB",
    "Nintendo Switch OLED Model",
    "Nintendo Switch Lite",
    "Xbox Series X 1TB",
    "Xbox Series S 512GB",
    "Asus ROG Ally Z1 Extreme",
    "Steam Deck OLED 512GB",

    # Cameras & Photography
    "Sony Alpha A7 IV Mirrorless Camera",
    "Sony Alpha A6700 Mirrorless Camera",
    "Canon EOS R6 Mark II Mirrorless Camera",
    "Canon EOS R50 Mirrorless Camera",
    "DJI Mini 4 Pro Drone",
    "DJI Osmo Pocket 3 Creator Combo",
    "GoPro HERO 12 Black",

    # Home Appliances
    "Gree 1.5 Ton Inverter AC",
    "General 1.5 Ton Inverter AC",
    "Samsung 43-inch 4K Smart LED TV",
    "Sony Bravia 55-inch 4K Google TV",
    "Samsung 300L Inverter Refrigerator",

    # Cycles & EVs
    "Veloce Outrage 601 Mountain Bike MTB",
    "Firefox Target 29 D Mountain Cycle",
    "Walton Takyon Electric Bike",

    # Beauty & Skincare
    "Dr. Althea 345 Relief Cream 50ml",
    "Dr. Althea Vitamin C Boosting Serum",
    "Beauty of Joseon Relief Sun Rice Probiotics SPF50",
    "COSRX Advanced Snail 96 Mucin Power Essence",
    "Skin1004 Madagascar Centella Ampoule",
    "Round Lab Birch Juice Moisturizing Sunscreen",
    "CeraVe Daily Moisturizing Lotion",
    "Cetaphil Gentle Skin Cleanser",
    "The Ordinary Niacinamide 10% + Zinc 1%",
]

_PRODUCTS_INDEX: List[str] = []

def initialize_products_index():
    global _PRODUCTS_INDEX
    if _PRODUCTS_INDEX:
        return

    items = list(CLEAN_PRODUCT_CATALOG)
    seen = {p.lower().strip() for p in items}

    # Ingest clean titles from SQLite if available (filtering out non-fungible categories)
    db_path = os.path.join(os.path.dirname(__file__), "jachai.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT title_en FROM products
                WHERE title_en IS NOT NULL
                  AND category NOT IN ('Fashion & Apparel', 'Saree & Boutiques', 'Fashion & Budget Jewellery', 'Grocery & Snacks')
                LIMIT 300
            """)
            for row in cur.fetchall():
                t = (row[0] or "").strip()
                t_clean = re.sub(r"\(official.*?\)|\[.*?\]", "", t, flags=re.I).strip()
                t_clean = re.sub(r"\s+", " ", t_clean)
                if len(t_clean) >= 6 and t_clean.lower() not in seen and not any(b in t_clean.lower() for b in ["synthetic", "dummy", "test"]):
                    items.append(t_clean)
                    seen.add(t_clean.lower())
            conn.close()
        except Exception:
            pass

    _PRODUCTS_INDEX = items

initialize_products_index()

def get_search_suggestions(raw_prefix: str, limit: int = 6) -> Dict[str, Any]:
    """
    Returns clean, pure product suggestions without category clutter.
    """
    q = (raw_prefix or "").strip().lower()
    if len(q) < 2:
        return {"query": raw_prefix, "suggestions": []}

    # Strip parentheses and normalize
    q_clean = re.sub(r"\(.*?\)|\[.*?\]", " ", q)
    q_clean = re.sub(r"[^\w\s-]", " ", q_clean)
    q_norm = re.sub(r"\s+", " ", q_clean).strip()

    tokens = q_norm.split()
    matched: List[Dict[str, str]] = []
    seen = set()

    # Priority 1: Prefix match
    for prod in _PRODUCTS_INDEX:
        p_low = prod.lower()
        if p_low.startswith(q_norm) or p_low.startswith(q):
            if prod not in seen:
                matched.append({"title": prod})
                seen.add(prod)
                if len(matched) >= limit:
                    break

    # Priority 2: All tokens match
    if len(matched) < limit:
        for prod in _PRODUCTS_INDEX:
            p_low = prod.lower()
            if all(tok in p_low for tok in tokens):
                if prod not in seen:
                    matched.append({"title": prod})
                    seen.add(prod)
                    if len(matched) >= limit:
                        break

    return {
        "query": raw_prefix,
        "suggestions": matched[:limit],
    }
