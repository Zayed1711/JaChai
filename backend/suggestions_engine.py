import re
import sqlite3
import os
from typing import List, Dict, Any

# Standardized, high-ticket spec products in Bangladesh (Laptops, Phones, Smartwatches, Horology, Consoles, Cameras, Skincare, Appliances)
CLEAN_PRODUCT_CATALOG: List[str] = [
    # Smartphones & Tablets
    "Apple iPhone 17 Pro Max",
    "Apple iPhone 17 Pro",
    "Apple iPhone 17 Plus",
    "Apple iPhone 17",
    "Apple iPhone 16 Pro Max",
    "Apple iPhone 16 Pro",
    "Apple iPhone 16 Plus",
    "Apple iPhone 16",
    "Apple iPhone 15 Pro Max 256GB",
    "Apple iPhone 15 Pro 128GB",
    "Apple iPhone 15 128GB",
    "Apple iPhone 14 Pro Max",
    "Apple iPhone 13 128GB",
    "Samsung Galaxy S25 Ultra",
    "Samsung Galaxy S25 Plus",
    "Samsung Galaxy S25",
    "Samsung Galaxy S24 Ultra 256GB",
    "Samsung Galaxy S24 Plus 256GB",
    "Samsung Galaxy S24 128GB",
    "Samsung Galaxy S23 Ultra",
    "Samsung Galaxy Z Fold 6",
    "Samsung Galaxy Z Flip 6",
    "Samsung Galaxy A55 5G",
    "Samsung Galaxy A35 5G",
    "Google Pixel 9 Pro XL",
    "Google Pixel 9 Pro",
    "Google Pixel 9",
    "Google Pixel 8 Pro 128GB",
    "Google Pixel 8a 128GB",
    "OnePlus 13 5G",
    "OnePlus 12 5G 256GB",
    "OnePlus 12R",
    "OnePlus Nord 4",
    "Xiaomi 14 Ultra",
    "Xiaomi 14",
    "Xiaomi Redmi Note 13 Pro+ 5G",
    "Xiaomi Redmi Note 13 Pro 4G",
    "Apple iPad Pro M4 11-inch",
    "Apple iPad Air M2 11-inch",
    "Apple iPad 10th Gen 64GB",

    # Smartwatches & Wearables
    "Samsung Galaxy Watch 7 44mm",
    "Samsung Galaxy Watch 7 40mm",
    "Samsung Galaxy Watch Ultra 47mm",
    "Samsung Galaxy Watch 6 44mm",
    "Samsung Galaxy Watch 6 Classic 47mm",
    "Samsung Galaxy Watch 6 40mm",
    "Samsung Galaxy Watch FE",
    "Samsung Galaxy Watch 5 Pro",
    "Apple Watch Ultra 2 49mm Cellular",
    "Apple Watch Series 10 46mm GPS",
    "Apple Watch Series 10 42mm GPS",
    "Apple Watch Series 9 45mm GPS",
    "Apple Watch Series 9 41mm GPS",
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
    "Tissot Gentleman Powermatic 80 Silicium",
    "Seiko 5 Sports Automatic SRPD",
    "Seiko Prospex Speedtimer Solar Chronograph",

    # Laptops & Computing
    "Apple MacBook Pro M4 14-inch",
    "Apple MacBook Pro M3 Pro 14-inch 512GB",
    "Apple MacBook Air M3 13-inch 256GB",
    "Apple MacBook Air M2 13-inch 256GB",
    "Asus ROG Zephyrus G14",
    "Asus Vivobook 15 X1504VA Core i5",
    "Asus Vivobook 16X OLED Creator Edition",
    "Asus Vivobook Go 14 Ryzen 5",
    "Asus Vivobook S 14 OLED Intel Evo",
    "Asus Zenbook 14 OLED Ultra 7",
    "Lenovo Legion Pro 5 Gen 9",
    "Lenovo LOQ 15 Gaming Laptop",
    "Lenovo IdeaPad Slim 3 Core i3",
    "Dell Inspiron 15 Core i5",
    "HP Pavilion 15 Core i5",
    "HP Victus 15 Gaming Laptop",

    # Gaming Consoles & Handhelds
    "Sony PlayStation 5 Pro",
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
    "Sony Alpha A7C II Mirrorless Camera",
    "Sony Alpha A6700 Mirrorless Camera",
    "Canon EOS R6 Mark II Mirrorless Camera",
    "Canon EOS R50 Mirrorless Camera",
    "DJI Mini 4 Pro Drone",
    "DJI Osmo Pocket 3 Creator Combo",
    "GoPro HERO 12 Black",

    # Home Appliances
    "Gree 1.5 Ton Inverter AC",
    "General 1.5 Ton Inverter AC",
    "Haier 1.5 Ton Inverter AC",
    "Samsung 43-inch 4K Smart LED TV",
    "Sony Bravia 55-inch 4K Google TV",
    "Samsung 300L Inverter Refrigerator",
    "Walton 250L Direct Cool Refrigerator",

    # Cycles & EVs
    "Veloce Outrage 601 Mountain Bike MTB",
    "Veloce Legion 40 MTB Bicycle",
    "Firefox Target 29 D Mountain Cycle",
    "Duranta Alloy MTB 26 Bicycle",
    "Walton Takyon Electric Bike",

    # Beauty & Skincare
    "Dr. Althea 345 Relief Cream 50ml",
    "Dr. Althea 147 Barrier Cream 50ml",
    "Dr. Althea Vitamin C Boosting Serum 30ml",
    "Dr. Althea 345 Relief Cream Mist 60ml",
    "Beauty of Joseon Relief Sun Rice Probiotics SPF50+",
    "Beauty of Joseon Dynasty Cream",
    "Beauty of Joseon Glow Serum Propolis Niacinamide",
    "COSRX Advanced Snail 96 Mucin Power Essence",
    "COSRX Low pH Good Morning Gel Cleanser",
    "COSRX Oil-Free Ultra-Moisturizing Lotion",
    "Skin1004 Madagascar Centella Ampoule",
    "Skin1004 Madagascar Centella Hyalu-Cica Water-Fit Sun Serum SPF50+",
    "Anua Heartleaf 77% Soothing Toner",
    "Anua Heartleaf Pore Control Cleansing Oil",
    "Round Lab Birch Juice Moisturizing Sunscreen SPF50+",
    "Torriden DIVE-IN Low Molecular Hyaluronic Acid Serum",
    "CeraVe Daily Moisturizing Lotion",
    "CeraVe Foaming Facial Cleanser",
    "CeraVe SA Smoothing Cleanser",
    "Cetaphil Gentle Skin Cleanser",
    "The Ordinary Niacinamide 10% + Zinc 1%",
    "The Ordinary Hyaluronic Acid 2% + B5",
    "The Ordinary Glycolic Acid 7% Toning Solution",
    "Some By Mi AHA BHA PHA 30 Days Miracle Toner",
    "Axis-Y Dark Spot Correcting Glow Serum",
    "Laneige Lip Sleeping Mask Berry",
    "Innisfree Green Tea Seed Hyaluronic Serum",
]

_PRODUCTS_INDEX: List[str] = []

def clean_db_title(raw_title: str) -> str:
    """Strips dirty SEO noise, dates, full specs tokens from SQLite titles."""
    if not raw_title:
        return ""
    t = re.sub(r"\(.*?\)|\[.*?\]", " ", raw_title)
    t = re.sub(
        r"(?i)\b(updated|oct|nov|dec|jan|feb|mar|apr|may|jun|jul|aug|sep|202[0-9]|full specs|specification|specifications|price in bd|price in bangladesh|bd price|buy online|official warranty|official bangladesh edition|official|commuter edition)\b",
        " ",
        t,
    )
    t = re.split(r"[|:;–—]", t)[0]
    t = re.sub(r"\s+", " ", t).strip(" -,")
    return t

def initialize_products_index():
    global _PRODUCTS_INDEX
    if _PRODUCTS_INDEX:
        return

    items = list(CLEAN_PRODUCT_CATALOG)
    seen = {p.lower().strip() for p in items}

    # Ingest clean titles from SQLite if available (filtering out non-fungible categories and noisy titles)
    db_path = os.path.join(os.path.dirname(__file__), "jachai.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT title_en FROM products
                WHERE title_en IS NOT NULL
                  AND category NOT IN ('Fashion & Apparel', 'Saree & Boutiques', 'Fashion & Budget Jewellery', 'Grocery & Snacks')
                LIMIT 400
            """)
            for row in cur.fetchall():
                t = (row[0] or "").strip()
                t_clean = clean_db_title(t)
                if (
                    len(t_clean) >= 6
                    and len(t_clean) <= 60
                    and t_clean.lower() not in seen
                    and not any(b in t_clean.lower() for b in ["synthetic", "dummy", "test", "spec", "oct", "nov", "update"])
                ):
                    items.append(t_clean)
                    seen.add(t_clean.lower())
            conn.close()
        except Exception:
            pass

    _PRODUCTS_INDEX = items

initialize_products_index()

def synthesize_dynamic_suggestions(query_norm: str) -> List[str]:
    """
    Synthesizes clean, high-precision product suggestions for emerging / popular models
    when the user types terms not yet indexed in the static catalog.
    """
    q = query_norm.lower().strip()
    syn: List[str] = []

    # iPhone series
    if "iphone" in q:
        num_m = re.search(r"\b(1[1-8])\b", q)
        num = num_m.group(1) if num_m else "17"
        if "pro max" in q or "promax" in q:
            syn.append(f"Apple iPhone {num} Pro Max")
            syn.append(f"Apple iPhone {num} Pro")
        elif "pro" in q:
            syn.append(f"Apple iPhone {num} Pro")
            syn.append(f"Apple iPhone {num} Pro Max")
            syn.append(f"Apple iPhone {num}")
        elif "plus" in q:
            syn.append(f"Apple iPhone {num} Plus")
            syn.append(f"Apple iPhone {num}")
        else:
            syn.append(f"Apple iPhone {num} Pro Max")
            syn.append(f"Apple iPhone {num} Pro")
            syn.append(f"Apple iPhone {num}")

    # Samsung Galaxy series
    elif "s25" in q or "s24" in q or "s23" in q or "galaxy s" in q:
        s_num = "S25" if "s25" in q else ("S24" if "s24" in q else ("S23" if "s23" in q else "S25"))
        if "ultra" in q:
            syn.append(f"Samsung Galaxy {s_num} Ultra")
            syn.append(f"Samsung Galaxy {s_num} Plus")
        else:
            syn.append(f"Samsung Galaxy {s_num} Ultra")
            syn.append(f"Samsung Galaxy {s_num} Plus")
            syn.append(f"Samsung Galaxy {s_num}")

    # Pixel series
    elif "pixel" in q:
        p_num = "9" if "9" in q else ("8" if "8" in q else "9")
        syn.append(f"Google Pixel {p_num} Pro XL")
        syn.append(f"Google Pixel {p_num} Pro")
        syn.append(f"Google Pixel {p_num}")

    # Samsung Watch
    elif ("watch" in q and ("galaxy" in q or "samsung" in q)) or "galaxy watch" in q:
        w_num = "7" if "7" in q else ("6" if "6" in q else ("ultra" if "ultra" in q else "7"))
        if w_num == "ultra":
            syn.append("Samsung Galaxy Watch Ultra 47mm")
        else:
            syn.append(f"Samsung Galaxy Watch {w_num} 44mm")
            syn.append(f"Samsung Galaxy Watch {w_num} 40mm")
            syn.append(f"Samsung Galaxy Watch {w_num} Classic")

    # Dr. Althea Skincare
    elif "althea" in q:
        syn.append("Dr. Althea 345 Relief Cream 50ml")
        syn.append("Dr. Althea 147 Barrier Cream 50ml")
        syn.append("Dr. Althea Vitamin C Boosting Serum 30ml")

    # Generic brand + model title-casing
    elif len(q) >= 4:
        clean_phrase = re.sub(r"[^\w\s-]", "", q).strip().title()
        if len(clean_phrase) >= 4:
            syn.append(clean_phrase)

    return syn

def get_search_suggestions(raw_prefix: str, limit: int = 6) -> Dict[str, Any]:
    """
    Returns clean, pure product suggestions without category clutter.
    """
    q = (raw_prefix or "").strip().lower()
    if len(q) < 2:
        return {"query": raw_prefix, "suggestions": []}

    # Strip parentheses and special characters
    q_clean = re.sub(r"\(.*?\)|\[.*?\]", " ", q)
    q_clean = re.sub(r"[^\w\s-]", " ", q_clean)
    q_norm = re.sub(r"\s+", " ", q_clean).strip()

    tokens = [tok for tok in q_norm.split() if len(tok) >= 2 or tok.isdigit()]
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

    # Priority 3: Dynamic high-precision synthesis fallback if matched has fewer items
    if len(matched) < limit:
        synthesized = synthesize_dynamic_suggestions(q_norm)
        for s_title in synthesized:
            if s_title not in seen:
                matched.append({"title": s_title})
                seen.add(s_title)
                if len(matched) >= limit:
                    break

    return {
        "query": raw_prefix,
        "suggestions": matched[:limit],
    }
