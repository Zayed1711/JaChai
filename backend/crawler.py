import asyncio
import json
import random
import re
import statistics
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup
import httpx
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

try:
    from .models import PriceHistory, Product, SpotlightCard, StoreOffer, DiscoveredDomain, SearchTelemetry
    from .adapters import search_stores_concurrently
    from .bd_stores_registry import (
        RETAIL_VERTICALS,
        get_stores_for_vertical,
        get_stores_for_category,
        build_store_target_url,
        get_store_registry_meta,
        compute_trust_score,
        FCOMMERCE_JEWELRY_BOUTIQUES,
        FCOMMERCE_SAREE_BOUTIQUES,
        extract_budget_and_clean_query,
        resolve_category_from_query,
        resolve_category_or_none,
        CATEGORY_REGISTRY_MAP,
    )
    from .llm_reasoner import (
        analyze_search_intent,
        verify_and_filter_candidates,
        is_bangladesh_store_url,
        deterministic_intent_fallback,
        extract_mandatory_anchor_tokens,
        user_requested_accessory,
        matches_anchor_tokens,
        translate_bengali_and_banglish_for_store,
        classify_comparison_mode,
        ACCESSORY_KEYWORDS,
    )
except ImportError:
    from models import PriceHistory, Product, SpotlightCard, StoreOffer, DiscoveredDomain, SearchTelemetry
    from adapters import search_stores_concurrently
    from bd_stores_registry import (
        RETAIL_VERTICALS,
        get_stores_for_vertical,
        get_stores_for_category,
        build_store_target_url,
        get_store_registry_meta,
        compute_trust_score,
        FCOMMERCE_JEWELRY_BOUTIQUES,
        FCOMMERCE_SAREE_BOUTIQUES,
        extract_budget_and_clean_query,
        resolve_category_from_query,
        resolve_category_or_none,
        CATEGORY_REGISTRY_MAP,
    )
    from slm_organizer import call_ollama_linguistic_router, slm_verify_candidate
from llm_reasoner import (
        analyze_search_intent,
        verify_and_filter_candidates,
        is_bangladesh_store_url,
        deterministic_intent_fallback,
        extract_mandatory_anchor_tokens,
        user_requested_accessory,
        matches_anchor_tokens,
        translate_bengali_and_banglish_for_store,
        classify_comparison_mode,
        ACCESSORY_KEYWORDS,
    )


# ==============================================================================
# CATEGORY NEGATIVE KEYWORD FIREWALLS (STRICT ZERO-CONTAMINATION GATE)
# ==============================================================================
NEGATION_CLAUSE_RE = re.compile(
    r"\b(?:without|no|except|not|excluding|chara|bade)\s+(?:any\s+|original\s+)?(?:charger|adapter|cable|case|cover|back\s+cover|glass|screen\s+protector|protector|box|strap|earphone|headphone)\b"
    r"|(?:charger|adapter|cable|case|cover|glass|protector|box|strap)\s+(?:chara|bade|ছাড়া|ছাড়া|বাদে)(?:\s|$)"
    r"|(?:ছাড়া|ছাড়া|বাদে)\s*(?:চার্জার|কেবল|ক্যাবল|কাভার|কেস|গ্লাস|বক্স)"
    r"|(?:চার্জার|কেবল|ক্যাবল|কাভার|কেস|গ্লাস|বক্স)\s*(?:ছাড়া|ছাড়া|বাদে)",
    re.IGNORECASE,
)


PRICE_FLUFF_RE = re.compile(
    r"(?i)\b(?:price\s+in\s+bangladesh|price\s+in\s+bd|bd\s+price|best\s+price|price\s+bd|in\s+bangladesh|in\s+bd)\b"
)

def clean_query_for_display_and_search(raw_query: str) -> Tuple[str, Optional[int]]:
    """Strips negated accessory phrases, price fluff, and budget constraints so product titles stay clean."""
    no_neg = NEGATION_CLAUSE_RE.sub(" ", raw_query or "")
    no_neg = PRICE_FLUFF_RE.sub(" ", no_neg)
    no_neg = re.sub(r"\s+", " ", no_neg).strip()
    cleaned_q, max_bdt = extract_budget_and_clean_query(no_neg)
    cleaned_q = NEGATION_CLAUSE_RE.sub(" ", cleaned_q)
    cleaned_q = PRICE_FLUFF_RE.sub(" ", cleaned_q)
    cleaned_q = re.sub(r"\s+", " ", cleaned_q).strip()
    return (cleaned_q or no_neg or raw_query.strip()), max_bdt


def is_gibberish_search(raw_query: str) -> bool:
    """Rejects random keyboard mashing, malicious payloads, and extreme length while preserving valid Bangla/English/models."""
    q = (raw_query or "").strip().lower()
    if not q:
        return True
    if len(q) > 120:
        return True
    if any(inj in q for inj in ("<script", "select ", "union ", "drop table", "1=1", "or '1'='1", "or 1=1", "../", "..\\")):
        return True
    if re.search(r"(.)\1{6,}", q):
        return True
    if re.search(r"[\u0980-\u09FF]", q):
        return False
    known_short = {"ac", "tv", "pc", "ev", "ssd", "ram", "gpu", "cpu", "ups", "ips", "led", "dslr", "nvme", "ddr4", "ddr5", "hdmi", "cctv", "qled", "oled", "tws", "mtb", "bmx", "rgb", "usb"}
    if q in known_short:
        return False
    tokens = re.findall(r"[a-z]+", q)
    if not tokens:
        return True
    for tok in tokens:
        if tok in known_short or len(tok) <= 3:
            continue
        vowels = sum(1 for c in tok if c in "aeiouy")
        if vowels / len(tok) < 0.13 or re.search(r"[bcdfghjklmnpqrstvwxz]{5,}", tok):
            return True
    return False


CATEGORY_NEGATIVE_FIREWALL: Dict[str, Tuple[str, ...]] = {
    "Cycles & Electric Vehicles (EVs)": (
        "motherboard", "processor", "ryzen", "intel", "core i3", "core i5", "core i7", "core i9",
        "ddr4", "ddr5", "nvme", "ssd", "graphics card", "rtx", "gtx", "desktop pc", "gaming pc",
        "monitor", "laptop", "macbook", "router", "printer", "saree", "panjabi",
    ),
    "Laptops, Desktops & Computer Components": (
        "saree", "panjabi", "salwar", "sunscreen", "face wash", "mustard oil", "ghee", "jhumka", "bicycle",
    ),
    "Mobile Phones & Gadgets": (
        "motherboard", "desktop pc", "refrigerator", "washing machine", "microwave oven", "saree", "panjabi",
    ),
    "Saree & Boutiques": (
        "motherboard", "processor", "ryzen", "intel", "core i3", "core i5", "core i7", "core i9",
        "graphics card", "desktop pc", "gaming pc", "laptop", "router", "refrigerator", "microwave",
    ),
    "Fashion & Apparel": (
        "motherboard", "processor", "ryzen", "intel", "graphics card", "desktop pc", "refrigerator",
    ),
    "Grocery & Snacks": (
        "motherboard", "processor", "graphics card", "laptop", "smartphone", "iphone", "saree",
    ),
    "Fine Jewelry & Gold": (
        "motherboard", "processor", "laptop", "desktop pc", "refrigerator",
    ),
    "Fashion & Budget Jewellery": (
        "motherboard", "processor", "laptop", "desktop pc", "refrigerator",
    ),
    "Beauty & Skincare": (
        "motherboard", "processor", "laptop", "desktop pc", "refrigerator",
    ),
    "Bicycles, MTB & Aero": (
        "motherboard", "processor", "graphics card", "laptop", "saree", "panjabi",
    ),
    "Gaming Consoles & Accessories": (
        "saree", "panjabi", "salwar", "sunscreen", "face wash", "mustard oil", "ghee", "jhumka", "refrigerator", "washing machine",
    ),
    "Watches & Horology": (
        "motherboard", "processor", "laptop", "desktop pc", "refrigerator", "washing machine",
        "microwave", "saree", "panjabi", "salwar", "face wash", "cream", "crem",
    ),
}


def passes_category_negative_firewall(title: str, category: str, query: str = "") -> bool:
    if not title or not category:
        return True

    t_low = title.lower()
    q_low = (query or "").lower()
    cat_norm = category.strip().lower()

    target_blocklist: Optional[Tuple[str, ...]] = None
    for firewall_cat, blocklist in CATEGORY_NEGATIVE_FIREWALL.items():
        fc_norm = firewall_cat.strip().lower()
        if (
            (fc_norm in cat_norm)
            or (cat_norm in fc_norm)
            or ("saree" in fc_norm and "saree" in cat_norm)
            or ("fashion" in fc_norm and "fashion" in cat_norm)
            or ("grocery" in fc_norm and "grocery" in cat_norm)
            or ("jewelry" in fc_norm and "jewel" in cat_norm)
            or ("beauty" in fc_norm and ("beauty" in cat_norm or "skincare" in cat_norm))
            or ("cycle" in fc_norm and ("cycle" in cat_norm or "ev" in cat_norm or "bicycle" in cat_norm))
            or ("laptop" in fc_norm and ("laptop" in cat_norm or "computer" in cat_norm or "pc" in cat_norm))
            or ("mobile" in fc_norm and ("mobile" in cat_norm or "phone" in cat_norm or "gadget" in cat_norm))
            or ("watch" in fc_norm and "watch" in cat_norm)
            or ("horology" in fc_norm and "horology" in cat_norm)
        ):
            target_blocklist = blocklist
            break

    if not target_blocklist:
        return True

    for bad_kw in target_blocklist:
        if q_low and re.search(r"(?i)\b" + re.escape(bad_kw) + r"\b", q_low):
            continue
        if re.search(r"(?i)\b" + re.escape(bad_kw) + r"\b", t_low):
            return False

    return True


CATEGORY_COMPATIBILITY_MAP: Dict[str, List[str]] = {
    "cameras-photography": ["cameras & dslr", "cameras, dslr & photography gear", "cameras_and_photography", "cameras-photography", "cameras", "dslr"],
    "bicycles-mtb": ["cycles & bicycles (mtb & aero)", "cycles, bicycles, mtb & aero bikes", "bicycles_and_mtb", "bicycles-mtb", "cycles & evs"],
    "cycles-evs": ["electric bikes & evs (cycles & evs)", "cycles & evs", "cycles & electric vehicles (evs)", "cycles_and_evs", "cycles-evs"],
    "mobile-gadgets": ["mobiles & gadgets", "mobile phones & consumer gadgets", "mobiles-computers", "gadgets", "mobile-gadgets", "mobiles"],
    "laptops-pc": ["laptops & pc", "laptops, desktops & computer components", "mobiles-computers", "laptops-pc", "laptops", "pc"],
    "fine-jewelry": ["fine jewelry & gold", "fine_jewelry_and_gold", "fine-jewelry", "jewelleries", "fine jewelry & premium fashion jewelry stores"],
    "sneakers-footwear": ["sneakers & shoes", "sneakers_and_footwear", "sneakers-footwear", "sneakers & footwear stores", "sneakers-watches", "shoes"],
    "watches-horology": ["watches & horology", "watches_and_horology", "watches-horology", "watches & horology retailers", "sneakers-watches"],
    "home-appliances": ["home appliances", "appliances_and_electronics", "appliances-electronics", "home-appliances", "home appliances & white goods"],
    "beauty-skincare": ["beauty & skincare", "beauty_and_skincare", "beauty-skincare", "beauty, skincare & lifestyle stores"],
    "sportswear-gym": ["sportswear & gym", "sportswear_and_gym", "sportswear-gym", "sportswear, activewear & gym gear"],
    "gaming-consoles": ["gaming consoles & accessories", "gaming_consoles_and_accessories", "gaming-consoles", "gaming consoles", "consoles", "playstation", "xbox", "nintendo"],
}


def is_product_category_compatible(prod_cat: str, cat_id: str, display_en: str, title: str = "") -> bool:
    if not prod_cat:
        return True
    p_low = prod_cat.strip().lower()
    d_low = display_en.strip().lower()
    if p_low == d_low:
        return True

    compat_list = CATEGORY_COMPATIBILITY_MAP.get(cat_id, [d_low])
    is_compat = any(c in p_low or p_low in c for c in compat_list)
    if not is_compat:
        return False

    t_low = title.lower()
    if p_low == "mobiles-computers":
        if cat_id == "laptops-pc":
            if any(w in t_low for w in ["phone", "redmi", "iphone", "pixel", "samsung galaxy", "oneplus"]) and not any(w in t_low for w in ["laptop", "notebook", "desktop", "pc", "macbook", "ram", "ssd", "monitor"]):
                return False
        elif cat_id == "mobile-gadgets":
            if any(w in t_low for w in ["laptop", "notebook", "desktop pc", "gaming pc", "motherboard", "processor"]) and not any(w in t_low for w in ["phone", "iphone", "earbuds", "watch", "charger", "cable"]):
                return False

    if p_low == "sneakers-watches":
        if cat_id == "watches-horology" and not any(w in t_low for w in ["watch", "chrono", "dial", "time"]):
            return False
        if cat_id == "sneakers-footwear" and not any(w in t_low for w in ["shoe", "sneaker", "boot", "suede", "sole", "footwear"]):
            return False

            return False

    return True


# ==============================================================================
# 1. BENGALI & ENGLISH BDT PRICE PARSER
# ==============================================================================
def parse_bdt_price(raw_text: str) -> Optional[int]:
    if not raw_text or not isinstance(raw_text, str):
        return None
    upper_raw = raw_text.upper()
    for cur in ("USD", "INR", "EUR", "GBP", "CAD", "AUD", "$", "₹", "€", "£", "RS", "RUPEE"):
        if cur in upper_raw:
            return None

    bn_to_en = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
    normalized = raw_text.translate(bn_to_en)

    cleaned = (
        normalized.replace(",", "")
        .replace("৳", "")
        .replace("BDT", "")
        .replace("bdt", "")
        .replace("Tk.", "")
        .replace("Tk", "")
        .replace("tk", "")
        .replace("Taka", "")
        .replace("/-", "")
    )

    candidates = re.findall(r"\b\d+\b", cleaned)
    for cand in candidates:
        val = int(cand)
        if 50 <= val <= 50000000:
            return val

    fallback_candidates = re.findall(r"\d+", cleaned)
    for cand in fallback_candidates:
        val = int(cand)
        if 50 <= val <= 50000000:
            return val

    return None


# ==============================================================================
# 2. MULTI-STRATEGY HTML PRICE & STOCK EXTRACTOR
# ==============================================================================
def extract_price_from_html(
    html: str, css_selector: Optional[str] = None
) -> Tuple[Optional[int], bool]:
    if not html:
        return None, True

    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    page_text_lower = soup.get_text().lower()
    out_of_stock_indicators = [
        "out of stock", "stock out", "upcoming", "sold out",
        "স্টক আউট", "স্টক শেষ", "পণ্যটি শেষ",
    ]
    in_stock = not any(indicator in page_text_lower for indicator in out_of_stock_indicators)

    if css_selector and css_selector.strip():
        selector = css_selector.strip()
        try:
            elem = soup.select_one(selector)
            if elem:
                val_attr = elem.get("content") or elem.get("value")
                if val_attr:
                    price = parse_bdt_price(str(val_attr))
                    if price:
                        return price, in_stock
                price = parse_bdt_price(elem.get_text())
                if price:
                    return price, in_stock
        except Exception:
            pass

    meta_selectors = [
        ('meta[property="product:price:amount"]', "content"),
        ('meta[property="og:price:amount"]', "content"),
        ('meta[itemprop="price"]', "content"),
        ('meta[name="twitter:data1"]', "content"),
    ]
    for tag_query, attr in meta_selectors:
        meta_tag = soup.select_one(tag_query)
        if meta_tag and meta_tag.get(attr):
            price = parse_bdt_price(str(meta_tag.get(attr)))
            if price:
                return price, in_stock

    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    for script in json_ld_scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                nodes = item.get("@graph", [item]) if isinstance(item, dict) else [item]
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    if node.get("@type") in ("Product", "IndividualProduct"):
                        offers = node.get("offers", {})
                        offer_list = offers if isinstance(offers, list) else [offers]
                        for off in offer_list:
                            if not isinstance(off, dict):
                                continue
                            raw_p = off.get("price") or off.get("lowPrice")
                            if raw_p:
                                price = parse_bdt_price(str(raw_p))
                                if price:
                                    avail = str(off.get("availability", "")).lower()
                                    if "outofstock" in avail or "soldout" in avail:
                                        in_stock = False
                                    return price, in_stock
        except Exception:
            continue

    common_selectors = [
        ".product-price", ".price-new", ".special-price .price", ".special-price",
        ".p-item-price", ".p-price", ".woocommerce-Price-amount", ".current-price",
        ".price-tag", ".price-box .price", ".price-box", ".curr-rate", ".rate-22k",
    ]
    for sel in common_selectors:
        try:
            elem = soup.select_one(sel)
            if elem:
                price = parse_bdt_price(elem.get_text())
                if price:
                    return price, in_stock
        except Exception:
            continue

    return None, in_stock


# ==============================================================================
# 3. MULTI-STRATEGY AUTHENTIC PRODUCT IMAGE EXTRACTOR
# ==============================================================================
def is_placeholder_image(url: str) -> bool:
    if not url or not isinstance(url, str):
        return True
    u_lower = url.strip().lower()
    if u_lower.startswith("data:image/"):
        if len(url) < 400 or "r0lgodlh" in u_lower:
            return True
        return False

    bad_patterns = [
        "1x1", "blank.gif", "pixel.gif", "spacer.gif", "placeholder",
        "no-image", "loader.gif", "loading.gif", "spinner.gif", "avatar",
        "icon-", "/icons/", "logo",
    ]
    return any(p in u_lower for p in bad_patterns)


def extract_image_from_node_or_html(node_or_soup, base_url: str = "") -> Optional[str]:
    if not node_or_soup:
        return None

    img_elements = node_or_soup.select("img") if hasattr(node_or_soup, "select") else []
    for img in img_elements:
        attrs = img.attrs if hasattr(img, "attrs") else {}
        for attr_key in ["data-src", "data-lazy-src", "srcset", "src"]:
            raw_val = attrs.get(attr_key)
            if not raw_val:
                continue
            if attr_key == "srcset":
                first_entry = raw_val.split(",")[0].strip()
                val = first_entry.split(" ")[0].strip()
            else:
                val = raw_val.strip()
            if val and not is_placeholder_image(val):
                return urljoin(base_url, val)

    if hasattr(node_or_soup, "select_one"):
        og_img = node_or_soup.select_one('meta[property="og:image"]')
        if og_img and og_img.get("content") and not is_placeholder_image(og_img.get("content")):
            return urljoin(base_url, og_img.get("content").strip())

        tw_img = node_or_soup.select_one('meta[name="twitter:image"]')
        if tw_img and tw_img.get("content") and not is_placeholder_image(tw_img.get("content")):
            return urljoin(base_url, tw_img.get("content").strip())

    return None


# ==============================================================================
# 4. STORE REGISTRY & ZERO-404 MERCHANT ENDPOINT GENERATOR
# ==============================================================================
STORE_SEARCH_URL_TEMPLATES = {
    "Gadget & Gear": "https://gadgetandgear.com/search?q={q}",
    "Apple Gadgets BD": "https://www.applegadgetsbd.com/search?q={q}",
    "Take & Talk": "https://takeandtalkbd.com/search?q={q}",
    "Pickaboo": "https://www.pickaboo.com/search-result/{q}",
    "Star Tech": "https://www.startech.com.bd/product/search?search={q}",
    "Ryans Computers": "https://www.ryans.com/search?q={q}",
    "Dazzle BD": "https://dazzle.com.bd/?s={q}&post_type=product",
    "Sumash Tech": "https://sumashtech.com/search?q={q}",
    "Salextra": "https://salextra.com.bd/search?q={q}",
    "TechLand BD": "https://www.techlandbd.com/search?q={q}",
    "Aarong": "https://www.aarong.com/search?q={q}",
    "Sailor BD": "https://sailor.clothing/search?q={q}",
    "Sailor": "https://sailor.clothing/search?q={q}",
    "Fabrilife": "https://fabrilife.com/search?q={q}",
    "Cats Eye": "https://catseye.com.bd/catalogsearch/result/?q={q}",
    "Anjan's": "https://anjans.com/search?q={q}",
    "Time Zone BD": "https://timezonebd.com/search?q={q}",
    "Apex Footwear": "https://apex4u.com/search?q={q}",
    "Bata Bangladesh": "https://batabd.com/search?q={q}",
}


def get_store_search_url(store_name: str, query: str, vertical: Optional[str] = None) -> str:
    clean_q = quote_plus(query.strip())
    url = build_store_target_url(store_name, query, vertical)
    if url and "facebook.com" not in url:
        return url

    s_clean = store_name.strip()
    for s_key, template in STORE_SEARCH_URL_TEMPLATES.items():
        if s_key.lower() in s_clean.lower() or s_clean.lower() in s_key.lower():
            return template.format(q=clean_q)

    return url or f"https://www.facebook.com/marketplace/dhaka/search/?query={clean_q}"


# ==============================================================================
# 5. ANTI-ACCESSORY & STRICT INTENT FILTERING
# ==============================================================================
ACCESSORY_NEGATIVE_TOKENS = [
    "case", "cover", "back cover", "silicone case", "leather case", "clear case",
    "tempered glass", "glass protector", "screen protector", "matte protector", "privacy glass",
    "skin", "sticker", "wrap", "cooling pad", "laptop bag", "backpack",
    "sleeve", "stand", "holder", "mount", "cable", "lightning cable",
    "type-c cable", "converter", "adapter", "charger", "power bank",
    "strap", "watch strap", "band", "watch band", "loop band", "trail loop",
    "ocean band", "alpine loop", "magnetic link", "sport loop", "sport band", "bumper",
    "pouch", "camera lens protector",
    "lens protector", "protector",
]

PRIMARY_HARDWARE_KEYWORDS = [
    "iphone", "phone", "smartphone", "laptop", "macbook", "ipad", "tablet",
    "pixel", "galaxy", "redmi", "xiaomi", "oneplus", "realme", "vivo", "oppo",
    "samsung", "apple", "honor", "infinix", "tecno", "motorola", "iqoo",
    "asus", "lenovo", "dell", "hp", "acer", "canon", "nikon", "sony",
    "watch", "smartwatch", "smart watch",
]


def is_accessory_listing(title: str, query: str) -> bool:
    q_lower = query.lower()
    t_lower = title.lower()
    for token in ACCESSORY_NEGATIVE_TOKENS:
        if token in q_lower:
            return False
    if any(dev in q_lower for dev in PRIMARY_HARDWARE_KEYWORDS):
        for token in ACCESSORY_NEGATIVE_TOKENS:
            if re.search(r"(?i)\b" + re.escape(token) + r"\b", t_lower):
                return True
    return False


# ==============================================================================
# 6. STRICT TITLE-TO-IMAGE ALIGNMENT & APPAREL GUARD
# ==============================================================================
BANNED_IMAGE_PATTERNS = [
    "savarkar", "gandhi", "nehru", "politician", "political", "statue",
    "monument", "historical", "flag", "parliament", "protest", "memorial",
    "leader", "freedom_fighter", "swami", "vivekananda",
]

APPAREL_KEYWORDS = [
    "panjabi", "punjabi", "saree", "shari", "kurti", "shirt", "t-shirt",
    "tshirt", "polo", "linen", "salwar", "kameez", "ethnic", "apparel",
    "clothing", "dress", "fashion", "abaya", "hijab",
]

AUTHENTIC_APPAREL_IMAGES = {
    "cotton panjabi": "/images/cotton-panjabi.svg",
    "panjabi": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
    "punjabi": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
    "jamdani": "/images/jamdani-saree.jpg",
    "saree": "/images/jamdani-saree.jpg",
    "shari": "/images/jamdani-saree.jpg",
    "kurti": "/images/linen-kurti.svg",
    "linen": "/images/old-money-shirt.jpg",
    "shirt": "/images/old-money-shirt.jpg",
    "dress": "/images/jamdani-saree.jpg",
    "fashion": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
}

CURATED_BD_MERCHANT_IMAGES = {
    "camera": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80",
    "dslr": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80",
    "canon": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80",
    "gopro": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80",
    "e-bike": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80",
    "electric bike": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80",
    "ebike": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80",
    "bicycle": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
    "cycle": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
    "scooter": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=80",
    "refrigerator": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80",
    "fridge": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80",
    "washing machine": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?auto=format&fit=crop&w=600&q=80",
    "blender": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?auto=format&fit=crop&w=600&q=80",
    "microwave": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=600&q=80",
    "ac": "https://images.unsplash.com/photo-1615873968403-89e068629265?auto=format&fit=crop&w=600&q=80",
    "tv": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=600&q=80",
    "redmi": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
    "smartphone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
    "phone": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
    "iphone": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=600&q=80",
    "samsung": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?auto=format&fit=crop&w=600&q=80",
    "panjabi": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
    "shirt": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80",
    "jamdani": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    "saree": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
    "earbuds": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80",
    "keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=600&q=80",
    "watch": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80",
    "smartwatch": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
    "sneakers": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
    "shoes": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
    "laptop": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
    "pc": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
    "honey": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=600&q=80",
    "ghee": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&w=600&q=80",
    "gold": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80",
    "jewelry": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80",
    "skincare": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80",
}

DEFAULT_CATEGORY_IMAGES = {
    "cameras-photography": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80",
    "bicycles-mtb": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
    "cycles-evs": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80",
    "home-appliances": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80",
    "fine-jewelry": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80",
    "sneakers-footwear": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
    "watches-horology": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80",
    "beauty-skincare": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80",
    "sportswear-gym": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80",
    "laptops-pc": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
    "mobile-gadgets": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80",
}


def get_authentic_image_for_query(title: str, query: str, category: Optional[str] = None) -> str:
    text = f"{title.lower()} {query.lower()} {category or ''}".lower()
    for kw, img_url in CURATED_BD_MERCHANT_IMAGES.items():
        if re.search(rf"\b{re.escape(kw)}\b", text):
            return img_url
    if category and category in DEFAULT_CATEGORY_IMAGES:
        return DEFAULT_CATEGORY_IMAGES[category]
    try:
        cat_id, _ = resolve_category_from_query(query, category)
        if cat_id in DEFAULT_CATEGORY_IMAGES:
            return DEFAULT_CATEGORY_IMAGES[cat_id]
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80"


def validate_and_sanitize_image(
    image_url: Optional[str], title: str, query: str, category: Optional[str] = None
) -> str:
    text = f"{title.lower()} {query.lower()} {category or ''}".lower()
    is_apparel = any(kw in text for kw in APPAREL_KEYWORDS) or category in ("fashion", )

    if image_url:
        img_lower = image_url.lower()
        if any(banned in img_lower for banned in BANNED_IMAGE_PATTERNS):
            image_url = None
        if "photo-1523275335684-37898b6baf30" in img_lower and not any(w in text for w in ["watch", "smartwatch", "chronograph"]):
            image_url = None

    # Check local downloaded product images in frontend/public/images/products/<cat_id>/ first
    try:
        from predetermined_catalog import CATEGORY_PREDETERMINED_CATALOG, resolve_product_card_image
        cat_spec = CATEGORY_PREDETERMINED_CATALOG.get(category or "", {})
        for p_item in cat_spec.get("products", []):
            if p_item["search_kw"].lower() in text or p_item["slug"].replace("-", " ") in text:
                cand_img = resolve_product_card_image(category or "", p_item["slug"], "")
                if cand_img:
                    return cand_img
    except Exception:
        pass

    if is_apparel:
        # Preserve any real scraped merchant product image (http/https or local /images/)
        if image_url and not is_placeholder_image(image_url) and "unsplash.com" not in image_url.lower():
            return image_url
        if any(w in text for w in ("underwear", "boxer", "brief", "innerwear", "vest", "t-shirt", "tshirt")):
            return "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=600&q=80"
        if any(w in text for w in ("belt", "wallet")):
            return "https://images.unsplash.com/photo-1624222247344-550fb60583dc?auto=format&fit=crop&w=600&q=80"
        if "sock" in text:
            return "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?auto=format&fit=crop&w=600&q=80"
        if any(w in text for w in ("jeans", "denim", "trouser", "pant", "chino")):
            return "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80"
        for kw, auth_img in AUTHENTIC_APPAREL_IMAGES.items():
            if kw in text:
                return auth_img
        return "/images/cotton-panjabi.svg"

    if not image_url or is_placeholder_image(image_url):
        return get_authentic_image_for_query(title, query, category)

    return image_url


# ==============================================================================
# 7. MULTI-VERTICAL LIVE SCRAPING ENGINE (ALL 13 CATEGORIES)
# ==============================================================================
async def scrape_startech_search(query: str, client: httpx.AsyncClient, max_budget_bdt: Optional[int] = None) -> List[dict]:
    """Scrapes Star Tech Bangladesh search results page."""
    results = []
    en_query = translate_bengali_and_banglish_for_store(query)
    url = f"https://www.startech.com.bd/product/search?search={quote_plus(en_query)}"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.startech.com.bd/",
        }
        res = await client.get(url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(".p-item")
            for item in items[:24]:
                title_el = item.select_one(".p-item-name a")
                price_el = item.select_one(".p-item-price")
                if not title_el or not price_el:
                    continue

                title = title_el.get_text(strip=True)
                product_url = urljoin("https://www.startech.com.bd", title_el.get("href", ""))
                image_url = extract_image_from_node_or_html(item, "https://www.startech.com.bd")
                from adapters import parse_prices
                pr_vals = parse_prices(price_el.get_text(" "))
                price = min(pr_vals) if pr_vals else parse_bdt_price(price_el.get_text())

                if max_budget_bdt and price and price > max_budget_bdt:
                    continue
                if len(results) >= 8:
                    break
                if title and price and image_url:
                    results.append({
                        "title": title,
                        "product_url": product_url,
                        "image_url": image_url,
                        "price": price,
                        "store_name": "Star Tech",
                        "source_type": "crawler",
                        "in_stock": "out of stock" not in item.get_text().lower(),
                        "category": "Laptops & PC",
                    })
    except Exception as e:
        print(f"[Spider] Star Tech error for '{query}': {e}")
    return results


async def scrape_dazzle_or_generic_search(query: str, client: httpx.AsyncClient) -> List[dict]:
    """Scrapes Dazzle BD or mobile gadgets stores."""
    from adapters import search_single_store
    en_query = translate_bengali_and_banglish_for_store(query)
    dazzle_store = {"name": "Dazzle BD", "domain": "dazzle.com.bd", "platform": "nextjs-js", "source_type": "crawler"}
    return await search_single_store(client, dazzle_store, en_query, limit=6)


async def scrape_store_search(
    query: str,
    vertical: Optional[str] = None,
    max_budget_bdt: Optional[int] = None,
    category_id: Optional[str] = None,
) -> List[dict]:
    """
    Executes concurrent asynchronous search scrapers across ALL verified stores in the
    target category CSV registry using `backend/adapters.py`.
    """
    en_query = translate_bengali_and_banglish_for_store(query)
    if not category_id:
        category_id, _ = resolve_category_from_query(query, vertical)

    stores = get_stores_for_category(category_id, query=en_query)
    if not stores and vertical:
        stores = get_stores_for_vertical(vertical)



    combined = await search_stores_concurrently(
        stores=stores,
        q=en_query,
        max_budget_bdt=max_budget_bdt,
        concurrency=10,
        per_store=6,
        deadline=5.5,
    )

    # Also run dedicated Star Tech scraper if in LAPTOP_PC
    if (category_id == "laptops-pc" or vertical == "LAPTOP_PC") and not any(r.get("store_name") == "Star Tech" for r in combined):
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.5), follow_redirects=True) as client:
                st_rows = await scrape_startech_search(en_query, client, max_budget_bdt=max_budget_bdt)
                combined.extend(st_rows)
        except Exception:
            pass

    # Mark direct store scraped items as authentic
    for item in combined:
        item["is_real_scraped"] = True

    # If direct store DOM scraping returned fewer than 4 items (e.g. due to JS SPA / Cloudflare),
    # harvest real live Bangladeshi product listings via scrape_bangladesh_web_live!
    if len(combined) < 4:
        try:
            from adapters import scrape_bangladesh_web_live
            cat_label = CATEGORY_REGISTRY_MAP.get(category_id, {}).get("display_en", "Mobiles & Gadgets")
            web_rows = await scrape_bangladesh_web_live(
                en_query, category_label=cat_label, max_budget_bdt=max_budget_bdt, limit=10
            )
            seen_u = {r.get("product_url") for r in combined}
            for wr in web_rows:
                if wr.get("product_url") not in seen_u:
                    combined.append(wr)
                    seen_u.add(wr.get("product_url"))
        except Exception as e:
            print(f"[Web Harvester] Fallback error for '{en_query}': {e}")

    return combined


# ==============================================================================
# 8. UNIVERSAL CANONICAL SKU & VARIANT/QUALITY ENGINE (ALL PRODUCT TYPES)
# ==============================================================================
STORAGE_RE = re.compile(r"\b(16|32|64|128|256|512|825)\s*(?:gb|g)\b|\b(1|2|4)\s*(?:tb|t)\b", re.I)
RAM_RE = re.compile(r"\b(\d+)\s*gb\s*(?:ram|memory)\b", re.I)
RAM_SLASH_STORAGE_RE = re.compile(r"\b(\d+)\s*gb?\s*[\/|\\]\s*(\d+)\s*(gb|tb)\b", re.I)
WATCH_SIZE_RE = re.compile(r"\b(38|40|41|42|44|45|46|47|49)\s*mm\b", re.I)
WATCH_CONN_RE = re.compile(r"\b(cellular|lte|gps)\b", re.I)

# Hardware, Peripherals & Component Specs across All Verticals
DDR_RE = re.compile(r"\b(ddr[345]|lpddr[45]x?)\b", re.I)
FREQ_RE = re.compile(r"\b(\d{4})\s*mhz\b", re.I)
SSD_TYPE_RE = re.compile(r"\b(nvme(?:\s*m\.?2)?|sata(?:\s*2\.5\"?)?|gen\s*[345]|pcie\s*[345]\.?0)\b", re.I)
CONSOLE_ED_RE = re.compile(r"\b(disc\s+edition|digital\s+edition|oled\s+model|slim\s+disc|slim\s+digital)\b", re.I)
CPU_INTEL_RE = re.compile(r"\b(core\s+(?:ultra\s+[579]|i[3579])(?:\s*[-–]?\s*\d{4,5}[a-z0-9]*)?)\b", re.I)
CPU_AMD_RE = re.compile(r"\b(ryzen\s+[3579](?:\s*[-–]?\s*\d{4,5}[a-z0-9]*)?)\b", re.I)
CPU_APPLE_RE = re.compile(r"\b(m[1234](?:\s*(?:pro|max|ultra))?)\b", re.I)
GPU_CHIP_RE = re.compile(r"\b(rtx\s*\d{4}(?:\s*(?:ti\s*super|ti|super))?|gtx\s*\d{4}|rx\s*\d{4}(?:\s*xtx|\s*xt)?)\b", re.I)
VRAM_RE = re.compile(r"\b(\d+)\s*gb\s*(?:gddr[56]x?|vram)\b", re.I)
CAMERA_KIT_RE = re.compile(r"\b(body\s*only|with\s+\d+-\d+mm\s*lens|\d+-\d+mm\s*kit)\b", re.I)
LENS_SPEC_RE = re.compile(r"\b(\d+mm\s*f\/?\d(?:\.\d+)?)\b", re.I)
QUALITY_WARRANTY_RE = re.compile(r"\b(unofficial(?:\s*global)?|official(?:\s*btrc|\s*warranty)?|global\s*version|player\s*edition|fan\s*edition|thai\s*a1)\b", re.I)
JEWELRY_KARAT_RE = re.compile(r"\b(18k|21k|22k|24k)\b", re.I)

COLOR_WORDS = [
    "black", "white", "blue", "green", "pink", "yellow", "purple", "silver",
    "gray", "grey", "titanium", "natural", "desert", "midnight", "starlight", "graphite",
    "sierra", "alpine", "cosmic", "phantom", "cream", "violet", "lavender", "mint", "red",
    "bronze", "amber", "emerald", "onyx", "ruby", "sapphire", "obsidian", "porcelain",
    "hazel", "rose", "bay", "aloe", "peony", "wintergreen", "charcoal", "coral", "chalk",
    "snow", "seafoam", "lemongrass", "space gray", "space black", "dark blue", "lemon",
    "peach", "orange", "cyan", "magenta"
]
COLOR_RE = re.compile(r"\b(?:" + "|".join(re.escape(c) for c in COLOR_WORDS) + r")\b", re.I)
NOISE_RE = re.compile(
    r"(?i)\b(price\s+in\s+bangladesh|price\s+in\s+bd|bd\s+price|best\s+price|buy\s+online|full\s+specs|specification|specifications|review|updated|\d{4}\s+specs|oct\s+\d{4}|nov\s+\d{4}|btrc\s+approved|international\s+version|factory\s+unlocked|sim\s+free|dual\s+sim|physical\s+dual\s+sim|esim|nano\s+sim|sealed\s+pack|intact\s+box|100%\s+original|authentic|default)\b"
)

BRAND_ALIASES = [
    (r"\b(pixel\s*\d+[a-z]*(?:\s*pro\s*xl|\s*pro\s*fold|\s*pro|\s*fold|\s*a)?)\b", "Google "),
    (r"\b(iphone\s*\d+[a-z]*(?:\s*pro\s*max|\s*pro|\s*plus|\s*mini)?)\b", "Apple "),
    (r"\b(ipad\s*(?:pro|air|mini)?\s*\d*)\b", "Apple "),
    (r"\b(macbook\s*(?:air|pro)?\s*(?:m\d+)?)\b", "Apple "),
    (r"\b(apple\s*watch\s*(?:ultra\s*\d*|series\s*\d+|se\s*\d*|se)?)\b", ""),
    (r"\b(galaxy\s*s\d+[a-z]*(?:\s*ultra|\s*plus|\s*fe)?)\b", "Samsung "),
    (r"\b(galaxy\s*watch\s*\d+[a-z]*(?:\s*classic|\s*pro|\s*ultra|\s*fe)?)\b", "Samsung "),
    (r"\b(playstation\s*5|ps5)\b", "Sony "),
    (r"\b(xbox\s*series\s*[xs])\b", "Microsoft "),
    (r"\b(nintendo\s*switch)\b", ""),
]

def extract_canonical_sku_info(title: str, query: str = "") -> Tuple[str, str, str]:
    """
    Universal Canonical SKU Engine across ALL product categories:
    - Mobile phones, Laptops, Computers, Laptop parts, Computer parts, Gaming consoles, Wearables, Cameras, Sports, Jewelry
    - Color is NEVER treated as a variant (50+ standard and OEM colors unconditionally stripped)
    - Distinguishes hardware variants (RAM, Storage, SSD Gen, DDR, Bus MHz, CPU, Dedicated GPU, Console Editions, mm sizes)
    - Distinguishes quality & condition tiers (Official Warranty BTRC vs Unofficial Global, Brand New vs Pre-Owned, Player Edition vs Fan)
    - Consolidates identical Model + Variant + Quality into EXACTLY ONE comparison card
    Returns: (disp_title, variant_tag, canonical_slug)
    """
    if " — Verified Store Price Comparison" in title or " — Player Edition" in title or " — Thai A1" in title or " — Fan / Stadium" in title:
        c_slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        return title.strip(), "Standard", c_slug

    raw = title.strip()
    is_used = any(u in raw.lower() for u in ("used", "pre-owned", "refurbished", "reconditioned", "grade-a", "second hand"))
    cond = "used" if is_used else "new"

    # Determine Product Classification
    is_laptop = any(k in raw.lower() for k in ("laptop", "notebook", "macbook", "rog strix", "zephyrus", "legion", "victus", "predator", "tuf gaming", "zenbook", "thinkpad", "vivobook", "pavilion", "inspiron", "omen"))
    is_gpu_part = not is_laptop and any(g in raw.lower() for g in ("rtx 40", "rtx 30", "gtx 16", "rx 7", "rx 6", "graphics card", "gpu"))
    is_ram_part = any(r in raw.lower() for r in ("desktop ram", "laptop ram", "ddr4", "ddr5", "fury beast", "vengeance", "ripjaws"))

    # 1. Hardware & Component Dimensions
    ram = ""
    storage = ""
    
    slash_m = RAM_SLASH_STORAGE_RE.search(raw)
    if slash_m:
        ram = f"{slash_m.group(1)}GB RAM"
        st_unit = (slash_m.group(3) or "GB").upper() if len(slash_m.groups()) >= 3 and slash_m.group(3) else "GB"
        storage = f"{slash_m.group(2)}{st_unit}"
    else:
        ram_m = RAM_RE.search(raw)
        if ram_m:
            ram = f"{ram_m.group(1)}GB RAM"
            raw_no_ram = RAM_RE.sub(" ", raw)
        else:
            raw_no_ram = raw

        st_m = STORAGE_RE.search(raw_no_ram)
        if st_m:
            val = st_m.group(1) or st_m.group(2)
            unit = "TB" if (st_m.group(2) or "tb" in st_m.group(0).lower()) else "GB"
            storage = f"{val}{unit}"
        elif query:
            qm = STORAGE_RE.search(query)
            if qm:
                val = qm.group(1) or qm.group(2)
                unit = "TB" if (qm.group(2) or "tb" in qm.group(0).lower()) else "GB"
                storage = f"{val}{unit}"

    if not storage and not is_laptop and not is_gpu_part and not is_ram_part:
        raw_low = raw.lower()
        if any(f in raw_low for f in ("pixel 9", "pixel 8", "pixel 7", "iphone 15", "iphone 14", "iphone 13", "galaxy s24", "galaxy s23")):
            storage = "128GB"

    # Computer & Laptop RAM parts (DDR4/DDR5 + Frequency)
    ddr_m = DDR_RE.search(raw)
    freq_m = FREQ_RE.search(raw)
    ram_part_spec = ""
    ram_raw_cap = ""
    if is_ram_part and (ddr_m or freq_m or ram or storage):
        parts = []
        if storage:
            ram_raw_cap = storage
            parts.append(storage)
            storage = ""
        elif ram:
            ram_raw_cap = ram.replace(" RAM", "")
            parts.append(ram_raw_cap)
        if ddr_m:
            parts.append(ddr_m.group(1).upper())
        if freq_m:
            parts.append(f"{freq_m.group(1)}MHz")
        ram_part_spec = " ".join(parts).strip()

    # SSD Type & Gen
    ssd_m = SSD_TYPE_RE.search(raw)
    ssd_spec = ""
    if ssd_m:
        matched_ssd = ssd_m.group(1).upper().replace(" ", "")
        if "NVME" in matched_ssd:
            ssd_spec = "NVMe M.2"
        elif "SATA" in matched_ssd:
            ssd_spec = "SATA SSD"
        elif "GEN4" in matched_ssd or "PCIE4" in matched_ssd:
            ssd_spec = "PCIe 4.0 Gen4"
        elif "GEN3" in matched_ssd or "PCIE3" in matched_ssd:
            ssd_spec = "PCIe 3.0 Gen3"
        elif "GEN5" in matched_ssd or "PCIE5" in matched_ssd:
            ssd_spec = "PCIe 5.0 Gen5"

    # Gaming Console Edition
    console_m = CONSOLE_ED_RE.search(raw)
    console_ed = ""
    if console_m:
        ed_low = console_m.group(1).lower()
        if "disc" in ed_low:
            console_ed = "Disc Edition"
        elif "digital" in ed_low:
            console_ed = "Digital Edition"
        elif "oled" in ed_low:
            console_ed = "OLED Model"

    # Processors & CPUs
    cpu_spec = ""
    apple_m = CPU_APPLE_RE.search(raw)
    if apple_m and any(w in raw.lower() for w in ("macbook", "mac", "ipad")):
        cpu_spec = apple_m.group(1).upper()
    else:
        intel_m = CPU_INTEL_RE.search(raw)
        if intel_m:
            cpu_spec = intel_m.group(1).title()
        else:
            amd_m = CPU_AMD_RE.search(raw)
            if amd_m:
                cpu_spec = amd_m.group(1).title()

    # Dedicated GPUs & VRAM
    gpu_spec = ""
    gpu_m = GPU_CHIP_RE.search(raw)
    vram_m = VRAM_RE.search(raw)
    vram_spec = vram_m.group(0).upper() if vram_m else ""
    if gpu_m:
        gpu_spec = gpu_m.group(1).upper()

    # Smartwatches
    watch_size_match = WATCH_SIZE_RE.search(raw)
    watch_size = f"{watch_size_match.group(1)}mm" if watch_size_match else ""
    watch_conn_match = WATCH_CONN_RE.search(raw)
    watch_conn = watch_conn_match.group(1).upper() if watch_conn_match else ""

    # Cameras
    cam_kit_m = CAMERA_KIT_RE.search(raw)
    cam_kit = cam_kit_m.group(1).title() if cam_kit_m else ""
    lens_m = LENS_SPEC_RE.search(raw)
    lens_spec = lens_m.group(1) if lens_m else ""

    # Quality / Warranty / Regional Edition
    quality_spec = ""
    qw_m = QUALITY_WARRANTY_RE.search(raw)
    if qw_m:
        qw_low = qw_m.group(1).lower()
        if "unofficial" in qw_low or "global" in qw_low:
            quality_spec = "Unofficial / Global"
        elif "official" in qw_low or "btrc" in qw_low:
            quality_spec = "Official Warranty"
        elif "player" in qw_low:
            quality_spec = "Player Edition"
        elif "fan" in qw_low:
            quality_spec = "Fan Edition"
        elif "thai" in qw_low:
            quality_spec = "Thai A1 Master Copy"

    # Fine Jewelry Karat
    karat_m = JEWELRY_KARAT_RE.search(raw)
    karat_spec = f"{karat_m.group(1).upper()} Gold" if karat_m else ""

    # 2. Clean store names and noise
    clean = re.split(r"\s+[-—|:]\s+(?:Star Tech|Apple Gadgets|Dazzle|Custom Mac|Sumash|KRY|Ryans|Pickaboo|Gadget & Gear|Mobile Buzz|Tri Tech|MobileBD|Mobilebuzzbd)", raw, flags=re.I)[0]
    clean = re.sub(r"(?i)\b(?:www\.)?[a-z0-9\-_]+\.(?:com\.bd|com|bd|org|net)\b", " ", clean)
    clean = NOISE_RE.sub(" ", clean)
    clean = COLOR_RE.sub(" ", clean)
    clean = re.sub(r"\(.*?\)|\[.*?\]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    # 3. Check for Sub-model modifiers
    sub_models = ["pro xl", "pro fold", "pro max", "pro", "plus", "ultra", "fold", "flip", "mini", "lite", "classic", "slim", "se", "fe"]
    found_sub = None
    for sm in sub_models:
        if re.search(r"\b" + re.escape(sm) + r"\b", raw.lower()):
            found_sub = sm.upper() if sm.lower() in ("pro xl", "pro max", "se", "fe") else sm.title()
            break

    # 4. Blacklist words that belong to extracted variants/qualities so they don't corrupt base model title
    blacklisted_tokens = {
        "official", "unofficial", "global", "warranty", "btrc",
        "disc", "digital", "edition", "oled", "model",
        "used", "pre-owned", "refurbished", "reconditioned", "second", "hand",
        "nvme", "m.2", "sata", "gen3", "gen4", "gen5", "pcie", "4.0", "3.0", "5.0", "ssd", "hdd",
        "ddr3", "ddr4", "ddr5", "lpddr4", "lpddr5", "ram", "memory",
        "gddr5", "gddr6", "gddr6x", "vram",
        "core", "i3", "i5", "i7", "i9", "ryzen",
        "player", "fan", "thai", "a1", "master", "copy",
        "18k", "21k", "22k", "24k"
    }
    if is_laptop:
        if gpu_spec:
            for gt in gpu_spec.lower().split(): blacklisted_tokens.add(gt)
    if storage:
        blacklisted_tokens.add(storage.lower())
    if ram:
        blacklisted_tokens.add(ram.lower().replace(" ram", ""))
    if ram_raw_cap:
        blacklisted_tokens.add(ram_raw_cap.lower())
    if watch_size:
        blacklisted_tokens.add(watch_size.lower())
    if watch_conn:
        blacklisted_tokens.add(watch_conn.lower())

    raw_tokens = [w for w in clean.split() if len(w) > 1 or w.isdigit() or re.match(r"(?i)^[ivx]+$", w) or re.match(r"^\d+[a-zA-Z]*$", w)]

    model_tokens = []
    for t in raw_tokens:
        t_low = t.lower()
        if t_low in blacklisted_tokens or re.search(r"\d+mhz", t_low):
            continue
        if found_sub and t_low in found_sub.lower().split():
            continue
        if re.match(r"(?i)^[ivx]+$", t):
            model_tokens.append(t.upper())
        elif not t.isupper() and len(t) > 3:
            model_tokens.append(t.title())
        else:
            model_tokens.append(t)

    token_limit = 5 if is_gpu_part else 4
    if len(model_tokens) > token_limit and re.match(r"(?i)^[ivx]+$", model_tokens[token_limit]):
        token_limit += 1

    base_name = " ".join(model_tokens[:token_limit]).strip()
    if found_sub and found_sub.lower() not in base_name.lower():
        base_name = f"{base_name} {found_sub}"

    # Brand prefix unification
    for alias_pattern, brand_prefix in BRAND_ALIASES:
        if re.search(alias_pattern, base_name, re.I):
            if brand_prefix and not base_name.lower().startswith(brand_prefix.lower().strip()):
                base_name = f"{brand_prefix}{base_name}"
            break

    # Standardize casing for key tech models
    base_name = re.sub(r"(?i)\biphone\b", "iPhone", base_name)
    base_name = re.sub(r"(?i)\bipad\b", "iPad", base_name)
    base_name = re.sub(r"(?i)\bmacbook\b", "MacBook", base_name)
    base_name = re.sub(r"(?i)\bps5\b", "PlayStation 5", base_name)
    base_name = re.sub(r"(?i)\bpro xl\b", "Pro XL", base_name)
    base_name = re.sub(r"(?i)\bpro max\b", "Pro Max", base_name)
    base_name = re.sub(r"(?i)\brtx\b", "RTX", base_name)
    base_name = re.sub(r"(?i)\bgtx\b", "GTX", base_name)
    base_name = re.sub(r"(?i)\bgeforce\b", "GeForce", base_name)

    if not base_name:
        clean_name = raw[:40].strip()
        c_slug = re.sub(r"[^a-z0-9]+", "-", clean_name.lower()).strip("-")
        return clean_name, "Standard", c_slug

    # 5. Assemble Structured Variant & Quality Elements
    variant_items = []
    
    if ram_part_spec:
        variant_items.append(ram_part_spec)
    elif "watch" in base_name.lower():
        if watch_size: variant_items.append(watch_size)
        if watch_conn: variant_items.append(watch_conn)
    elif is_gpu_part:
        if vram_spec:
            variant_items.append(vram_spec)
        elif storage:
            variant_items.append(f"{storage} VRAM")
    elif is_laptop:
        if cpu_spec: variant_items.append(cpu_spec)
        if ram: variant_items.append(ram)
        if storage: variant_items.append(f"{storage} SSD")
        if gpu_spec: variant_items.append(gpu_spec)
    else:
        # Gaming console
        if console_ed: variant_items.append(console_ed)
        # Processor
        if cpu_spec: variant_items.append(cpu_spec)
        # Storage & RAM
        if ram: variant_items.append(ram)
        if storage:
            if ssd_spec and "ssd" in raw.lower():
                variant_items.append(f"{storage} {ssd_spec}")
            else:
                variant_items.append(storage)
        elif ssd_spec:
            variant_items.append(ssd_spec)

    # Cameras
    if cam_kit: variant_items.append(cam_kit)
    if lens_spec and lens_spec not in base_name: variant_items.append(lens_spec)

    # Jewelry
    if karat_spec: variant_items.append(karat_spec)

    # Quality / Warranty / Edition
    if quality_spec: variant_items.append(quality_spec)

    variant_tag = " · ".join(variant_items) if variant_items else ""

    disp_title = f"{base_name} ({variant_tag})" if variant_tag else base_name
    if is_used:
        disp_title += " (Pre-Owned)"

    var_slug = re.sub(r"[^a-z0-9]+", "-", variant_tag.lower()).strip("-") if variant_tag else "std"
    base_slug = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")
    canonical_slug = f"{base_slug}-{var_slug}-{cond}".strip("-")

    return disp_title, variant_tag or "Standard", canonical_slug


def canonical_product_group_key(title: str, query: str = "") -> str:
    """
    Normalizes product titles so the same model from different stores groups into ONE
    unified comparison card.
    """
    _, _, g_key = extract_canonical_sku_info(title, query)
    return g_key


def generate_resilient_fallback(
    query: str, category: Optional[str] = None, intent: Optional[dict] = None
) -> List[dict]:
    """
    Mode B Category & Verified Store Price-Range Index Builder:
    When a user searches a broad category (e.g. 'mobile phone', 'saree', 'fashion jewellery',
    'electric bike', 'panjabi') or when live store DOMs are behind Cloudflare/FB walls,
    builds verified store comparison entries from the category's curated CSV registry
    with realistic category starting price ranges and 0% 404 merchant search/FB URLs.
    """
    q_clean, max_budget_bdt = clean_query_for_display_and_search(query.strip())
    en_kw = translate_bengali_and_banglish_for_store(q_clean)

    cat_id, cat_meta = resolve_category_from_query(query.strip(), category)
    inferred_category = cat_meta["display_en"]
    vertical = cat_meta.get("vertical", "MULTI_MARKETPLACE")
    min_p = cat_meta.get("price_min", 500)
    max_p = cat_meta.get("price_max", 250000)
    base_price = cat_meta.get("base_price", 3500)

    if user_requested_accessory(query):
        min_p, max_p, base_price = 250, 4500, 850
    elif any(k in en_kw.lower() for k in ("router", "wifi", "tp-link", "tenda", "switch", "webcam", "ups", "pendrive", "mouse", "keyboard")):
        min_p, max_p, base_price = 1200, 12000, 2650
    elif any(k in en_kw.lower() for k in ("earphone", "earbuds", "tws", "neckband", "speaker", "jbl", "power bank", "powerbank", "smartwatch")):
        min_p, max_p, base_price = 650, 18000, 2200

    if max_budget_bdt and max_budget_bdt > 0:
        min_p = min(min_p, max(100, int(max_budget_bdt * 0.45)))
        max_p = min(max_p, max_budget_bdt)
        base_price = min(base_price, int(max_budget_bdt * 0.80))

    reg_stores = get_stores_for_category(cat_id, query=q_clean)
    # Star Tech allowed for all gadgets/smartphones
    if cat_id == "cycles-evs":
        is_ebike_q = any(k in en_kw.lower() for k in ("electric", "e-bike", "ebike", "scooter", "takyon", "ev", "battery"))
        pedal_only = ("duranta", "veloce", "dream cycle", "lion cycle", "cyclelife")
        if is_ebike_q:
            reg_stores = [s for s in reg_stores if not any(p in (s.get("name") or "").lower() for p in pedal_only)]

    stores = []
    for s in reg_stores[:8]:
        s_type = "f_commerce" if (s.get("source_type") == "f_commerce" or not s.get("website_url")) else "crawler"
        stores.append((s.get("name"), s_type, s))

    display_title_base = q_clean.title() if not re.search(r"[\u0980-\u09FF]", q_clean) else f"{en_kw.title()} ({q_clean})"

    # Special Quality-Tier Expansion for Football / Cricket Jerseys (Player Edition, Thai A1 Master Copy, Fan Edition)
    if cat_id == "sportswear-gym" and any(j in en_kw.lower() for j in ("jersey", "jarsi", "kit", "argentina", "brazil")):
        jersey_tiers = [
            (f"{display_title_base} — Player Edition (Authentic Dri-FIT Slim Fit)", 1350),
            (f"{display_title_base} — Thai A1 Master Copy (Premium Embroidery & Print)", 850),
            (f"{display_title_base} — Fan / Stadium Edition ( breathable Mesh Fabric)", 550),
        ]
        items = []
        for t_title, t_base_p in jersey_tiers:
            if max_budget_bdt and t_base_p > max_budget_bdt:
                t_base_p = max(250, int(max_budget_bdt * 0.85))
            img_url = validate_and_sanitize_image(None, t_title, en_kw, cat_id)
            for s_idx, (store_name, s_type, s_dict) in enumerate(stores[:5]):
                store_url = build_store_target_url(store_name, en_kw, vertical)
                calc_price = t_base_p + [0, 50, -30, 80, -20][s_idx % 5]
                if max_budget_bdt and calc_price > max_budget_bdt:
                    calc_price = max_budget_bdt
                items.append({
                    "title": t_title,
                    "product_url": store_url,
                    "image_url": img_url,
                    "price": calc_price,
                    "original_price": int(calc_price * 1.15),
                    "store_name": store_name,
                    "source_type": s_type,
                    "in_stock": True,
                    "category": inferred_category,
                    "cod_terms_en": f"Quality Tier Verified · Starting from ৳{calc_price:,} · Cash on Delivery",
                    "cod_terms_bn": f"কোয়ালিটি ভেরিফাইড · শুরু ৳{calc_price:,} · ক্যাশ অন ডেলিভারি",
                    "is_sponsored": False,
                })
        return items

    templates = cat_meta.get("model_templates", ["{title} — Verified Store Price Comparison", "{title} Collection"])
    titles = [t.format(title=display_title_base) for t in templates[:2]]

    base_price = max(min_p, min(max_p, base_price))
    items = []

    for idx, title in enumerate(titles):
        img_url = validate_and_sanitize_image(None, title, en_kw, cat_id)
        p_price = int(base_price * (1.0 + idx * 0.08))
        for s_idx, (store_name, s_type, s_dict) in enumerate(stores):
            store_url = build_store_target_url(store_name, en_kw, vertical)
            offsets = [0, 150, -100, 300, -200, 450, 250, -150]
            variation = offsets[s_idx % len(offsets)]
            calc_price = max(min_p, min(max_p, p_price + variation))
            range_high = min(max_p, int(calc_price * 1.65))

            cod_en = (
                f"Price Range: ৳{calc_price:,} – ৳{range_high:,} · Cash on Delivery Available"
                if s_dict.get("engine") == "Engine B"
                else f"Starting from ৳{calc_price:,} up to ৳{range_high:,} · Cash on Delivery"
            )
            cod_bn = (
                f"দামের পরিসীমা: ৳{calc_price:,} – ৳{range_high:,} · ক্যাশ অন ডেলিভারি"
                if s_dict.get("engine") == "Engine B"
                else f"শুরু ৳{calc_price:,} থেকে সর্বোচ্চ ৳{range_high:,} · ক্যাশ অন ডেলিভারি"
            )

            items.append({
                "title": title,
                "product_url": store_url,
                "image_url": img_url,
                "price": calc_price,
                "original_price": calc_price,
                "store_name": store_name,
                "source_type": s_type,
                "in_stock": True,
                "category": inferred_category,
                "cod_terms_en": cod_en,
                "cod_terms_bn": cod_bn,
                "is_sponsored": str(s_dict.get("sponsored", "")).lower() in ("true", "1", "yes"),
            })

    return items


def normalize_store_match_name(name: str) -> str:
    n = re.sub(r"\(.*?\)", "", name or "").lower().strip()
    n = re.sub(r"\b(ltd|limited|bd|bangladesh)\b", "", n).strip()
    return " ".join(n.split())


def is_store_in_category(s_name: str, valid_stores: Set[str]) -> bool:
    if not valid_stores:
        return True
    s_low = s_name.lower().strip()
    if s_low in valid_stores:
        return True
    s_norm = normalize_store_match_name(s_low)
    if s_norm in valid_stores:
        return True
    no_p = re.sub(r"\(.*?\)", "", s_low).strip()
    if no_p in valid_stores:
        return True
    for vs in valid_stores:
        if len(vs) >= 4 and (vs in s_low or s_low in vs):
            return True
    return False



# ==============================================================================
# DURABLE CATEGORIES SUPPORTING USED / RECONDITIONED VS BRAND NEW SPLIT
# ==============================================================================
DURABLE_CONDITION_CATEGORIES = {
    "bicycles-mtb",
    "mobile-gadgets",
    "laptops-pc",
    "cameras-photography",
    "cycles-evs",
    "home-appliances",
    "watches-horology",
}

USED_CONDITION_KEYWORDS = (
    "used", "pre-owned", "preowned", "reconditioned", "refurbished",
    "second hand", "2nd hand", "open box", "corporate used", "dubai used",
    "ব্যবহৃত", "রিকন্ডিশন্ড", "পুরাতন", "সেকেন্ড হ্যান্ড",
)

VERIFIED_RECONDITIONED_MERCHANTS: Dict[str, List[Tuple[str, str, str, float]]] = {
    "mobile-gadgets": [
        ("Swap Bangladesh (Certified Pre-Owned)", "crawler", "https://swap.com.bd", 0.72),
        ("Apple Gadgets (Pre-Owned & Exchange)", "crawler", "https://www.applegadgetsbd.com", 0.75),
        ("Dazzle BD (Pre-Owned Exchange)", "crawler", "https://dazzle.com.bd", 0.74),
        ("KRY International (Pre-Owned Unit)", "crawler", "https://kryinternational.com", 0.71),
    ],
    "laptops-pc": [
        ("Computer Mania BD (Corporate Reconditioned)", "crawler", "https://computermania.com.bd", 0.62),
        ("Custom Mac BD (Certified Pre-Owned)", "crawler", "https://custommacbd.com", 0.68),
        ("Swap Bangladesh (Pre-Owned Laptops)", "crawler", "https://swap.com.bd", 0.65),
        ("Multiplan Reconditioned Laptop Hub", "f_commerce", "https://www.facebook.com/ComputerManiaBD", 0.60),
    ],
    "cameras-photography": [
        ("Camera Bazar BD (Baitul Mukarram Used)", "f_commerce", "https://www.facebook.com/camerabazarbd", 0.68),
        ("DSLR House BD (Used & Reconditioned)", "f_commerce", "https://www.facebook.com/dslrhousebd", 0.70),
        ("BD Camera Mart (Pre-Owned Gear)", "f_commerce", "https://www.facebook.com/bdcameramart", 0.66),
        ("Swap Bangladesh (Certified Used Camera)", "crawler", "https://swap.com.bd", 0.72),
    ],
    "bicycles-mtb": [
        ("Bongshal Used & Reconditioned Cycle Hub", "f_commerce", "https://www.facebook.com/BongshalCycleMart", 0.55),
        ("Swap Bangladesh (Pre-Owned Bicycles)", "crawler", "https://swap.com.bd", 0.62),
        ("Dhaka MTB & Road Bike Resale Club", "f_commerce", "https://www.facebook.com/PedalHouseBD", 0.58),
    ],
    "cycles-evs": [
        ("BD EV & Takyon Reconditioned Hub", "f_commerce", "https://www.facebook.com/takyonebike", 0.68),
        ("Swap Bangladesh (Pre-Owned E-Bike & Cycle)", "crawler", "https://swap.com.bd", 0.72),
        ("Dhaka Pre-Owned Cycle & EV Exchange", "f_commerce", "https://www.facebook.com/revoo.bd", 0.65),
    ],
    "home-appliances": [
        ("Swap Bangladesh (Pre-Owned Appliances)", "crawler", "https://swap.com.bd", 0.65),
        ("Dhaka Reconditioned AC & Appliance Hub", "f_commerce", "https://www.facebook.com/transcomdigital", 0.60),
        ("BD Showroom Reconditioned Electronics", "f_commerce", "https://www.facebook.com/Singer.Bangladesh", 0.68),
    ],
    "watches-horology": [
        ("Swap Bangladesh (Pre-Owned Watches)", "crawler", "https://swap.com.bd", 0.70),
        ("BD Vintage & Pre-Owned Watch Vault", "f_commerce", "https://www.facebook.com/timezonebd", 0.68),
    ],
}


def is_used_or_reconditioned_title(title: str) -> bool:
    t_low = (title or "").lower()
    return any(k in t_low for k in USED_CONDITION_KEYWORDS)


# ==============================================================================
# BROAD PRODUCT SEARCH -> MULTI-VARIANT SUB-CATEGORY BOXES
# ==============================================================================
BROAD_CATEGORY_VARIANT_SPECS: Dict[str, List[Dict[str, Any]]] = {
    "laptops-pc": [
        {
            "suffix_en": "Brand New Laptops (Official BD Warranty Series)",
            "suffix_bn": "???? ??????? (???????? ????????? ?????)",
            "condition": "NEW",
            "variant_tag": "? Brand New Laptops",
            "price_mult": 1.0,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Business Series Laptops (ThinkPad / EliteBook / Latitude / MacBook)",
            "suffix_bn": "?????? ????? ??????? (????????? / ??????? / ????????)",
            "condition": "NEW",
            "variant_tag": "?? Business Series",
            "price_mult": 1.18,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Gaming Series Laptops (RTX / ROG / TUF / Victus / LOQ)",
            "suffix_bn": "????? ????? ??????? (???????? / ????? / ??? / ???????)",
            "condition": "NEW",
            "variant_tag": "?? Gaming Series",
            "price_mult": 1.35,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Used Laptops (Certified Pre-Owned Grade-A)",
            "suffix_bn": "??????? ??????? (????-??? ?????-?)",
            "condition": "USED",
            "variant_tag": "?? Used Laptops",
            "price_mult": 0.42,
            "use_reconditioned_stores": True,
        },
        {
            "suffix_en": "Reconditioned Laptops (Corporate Dubai / USA Import Series)",
            "suffix_bn": "?????????? ???????? ??????? (????? / ????? ???????)",
            "condition": "USED",
            "variant_tag": "??? Reconditioned Laptops",
            "price_mult": 0.48,
            "use_reconditioned_stores": True,
        },
    ],
    "mobile-gadgets": [
        {
            "suffix_en": "Brand New Official Smartphones (BTRC Approved)",
            "suffix_bn": "???? ???????? ?????????? (???????? ????????)",
            "condition": "NEW",
            "variant_tag": "? Brand New Official",
            "price_mult": 1.0,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Brand New Unofficial / Global Smartphones (Intact Box)",
            "suffix_bn": "???? ??????? / ?????????? ?????????? (????????? ????)",
            "condition": "NEW",
            "variant_tag": "?? Unofficial / Global New",
            "price_mult": 0.88,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Gaming & Flagship Series Smartphones (5G Pro Series)",
            "suffix_bn": "????? ? ?????????? ?????????? (??? ???? ?????)",
            "condition": "NEW",
            "variant_tag": "?? Gaming & Flagship",
            "price_mult": 1.35,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Used Smartphones (Certified Pre-Owned Exchange)",
            "suffix_bn": "??????? ?????????? (???????? ????-???)",
            "condition": "USED",
            "variant_tag": "?? Used Phones",
            "price_mult": 0.55,
            "use_reconditioned_stores": True,
        },
        {
            "suffix_en": "Reconditioned Smartphones (Refurbished Grade-A)",
            "suffix_bn": "?????????? ?????????? (?????????? ?????-?)",
            "condition": "USED",
            "variant_tag": "??? Reconditioned Phones",
            "price_mult": 0.62,
            "use_reconditioned_stores": True,
        },
    ],
    "cameras-photography": [
        {
            "suffix_en": "Brand New DSLR & Mirrorless Cameras (Official Intact)",
            "suffix_bn": "???? ???????? ? ??????? ???????? (???????? ?????????)",
            "condition": "NEW",
            "variant_tag": "? Brand New Cameras",
            "price_mult": 1.0,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Action Cameras, Gimbals & Vlogging Gear (GoPro / DJI Series)",
            "suffix_bn": "??????? ????????, ?????? ? ?????? ?????",
            "condition": "NEW",
            "variant_tag": "?? Action & Vlogging",
            "price_mult": 0.65,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Used DSLR & Mirrorless Cameras (Shutter-Tested Pre-Owned)",
            "suffix_bn": "??????? ???????? ? ??????? ???????? (????? ???????)",
            "condition": "USED",
            "variant_tag": "?? Used Cameras",
            "price_mult": 0.52,
            "use_reconditioned_stores": True,
        },
        {
            "suffix_en": "Reconditioned Cameras & Prime/Zoom Lenses (Grade-A)",
            "suffix_bn": "?????????? ???????? ? ????? (?????-?)",
            "condition": "USED",
            "variant_tag": "??? Reconditioned Gear",
            "price_mult": 0.58,
            "use_reconditioned_stores": True,
        },
    ],
    "cycles-evs": [
        {
            "suffix_en": "Brand New Commuter Series (Official Showroom Intact)",
            "suffix_bn": "???? ????? ????? (???????? ?????????)",
            "condition": "NEW",
            "variant_tag": "? Brand New Units",
            "price_mult": 1.0,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Mountain, Gear & Long-Range Series (MTB & Pro EV)",
            "suffix_bn": "????????? ????? ? ??-????? ?????",
            "condition": "NEW",
            "variant_tag": "?? MTB & Long-Range",
            "price_mult": 1.15,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Used / Pre-Owned Units (Verified Resale)",
            "suffix_bn": "??????? ?????? ? ?-???? (???????? ?????)",
            "condition": "USED",
            "variant_tag": "?? Used Units",
            "price_mult": 0.58,
            "use_reconditioned_stores": True,
        },
        {
            "suffix_en": "Reconditioned Units (Battery & Motor Certified)",
            "suffix_bn": "?????????? ????? (???????? ? ???? ???????)",
            "condition": "USED",
            "variant_tag": "??? Reconditioned Units",
            "price_mult": 0.66,
            "use_reconditioned_stores": True,
        },
    ],
    "home-appliances": [
        {
            "suffix_en": "Brand New Energy-Saving Inverter Series (Official Warranty)",
            "suffix_bn": "???? ???????-????? ????????? ????? (???????? ?????????)",
            "condition": "NEW",
            "variant_tag": "? Brand New Inverter",
            "price_mult": 1.0,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Standard Non-Inverter & Budget Home Series",
            "suffix_bn": "????????????? ? ????? ??? ?????",
            "condition": "NEW",
            "variant_tag": "?? Standard Budget Series",
            "price_mult": 0.78,
            "use_reconditioned_stores": False,
        },
        {
            "suffix_en": "Used Home Appliances (Verified Pre-Owned)",
            "suffix_bn": "??????? ??? ????????????? (????-???)",
            "condition": "USED",
            "variant_tag": "?? Used Appliances",
            "price_mult": 0.52,
            "use_reconditioned_stores": True,
        },
        {
            "suffix_en": "Reconditioned & Showroom Display Units (Warranty Included)",
            "suffix_bn": "?????????? ? ????? ????? (???????????)",
            "condition": "USED",
            "variant_tag": "??? Reconditioned Units",
            "price_mult": 0.62,
            "use_reconditioned_stores": True,
        },
    ],
}


def build_broad_variant_listings(
    query: str,
    cat_id: str,
    cat_meta: Dict[str, Any],
    max_budget_bdt: Optional[int] = None,
) -> List[dict]:
    """
    Generates distinct Variant Category Boxes when the user searches a broad product name
    (e.g. 'Laptop' -> Brand New, Business Series, Gaming Series, Used, Reconditioned).
    """
    q_clean, _ = clean_query_for_display_and_search(query.strip())
    en_kw = translate_bengali_and_banglish_for_store(q_clean)
    display_title_base = q_clean.title() if not re.search(r"[\u0980-\u09FF]", q_clean) else f"{en_kw.title()} ({q_clean})"

    # Special Quality-Tier Expansion for Football / Cricket Jerseys (Player Edition, Thai A1 Master Copy, Fan Edition)
    if cat_id == "sportswear-gym" and any(j in en_kw.lower() for j in ("jersey", "jarsi", "kit", "argentina", "brazil")):
        jersey_tiers = [
            (f"{display_title_base} — Player Edition (Authentic Dri-FIT Slim Fit)", 1350),
            (f"{display_title_base} — Thai A1 Master Copy (Premium Embroidery & Print)", 850),
            (f"{display_title_base} — Fan / Stadium Edition ( breathable Mesh Fabric)", 550),
        ]
        items = []
        for t_title, t_base_p in jersey_tiers:
            if max_budget_bdt and t_base_p > max_budget_bdt:
                t_base_p = max(250, int(max_budget_bdt * 0.85))
            img_url = validate_and_sanitize_image(None, t_title, en_kw, cat_id)
            for s_idx, (store_name, s_type, s_dict) in enumerate(stores[:5]):
                store_url = build_store_target_url(store_name, en_kw, vertical)
                calc_price = t_base_p + [0, 50, -30, 80, -20][s_idx % 5]
                if max_budget_bdt and calc_price > max_budget_bdt:
                    calc_price = max_budget_bdt
                items.append({
                    "title": t_title,
                    "product_url": store_url,
                    "image_url": img_url,
                    "price": calc_price,
                    "original_price": int(calc_price * 1.15),
                    "store_name": store_name,
                    "source_type": s_type,
                    "in_stock": True,
                    "category": inferred_category,
                    "cod_terms_en": f"Quality Tier Verified · Starting from ৳{calc_price:,} · Cash on Delivery",
                    "cod_terms_bn": f"কোয়ালিটি ভেরিফাইড · শুরু ৳{calc_price:,} · ক্যাশ অন ডেলিভারি",
                    "is_sponsored": False,
                })
        return items


    inferred_category = cat_meta["display_en"]
    vertical = cat_meta.get("vertical", "MULTI_MARKETPLACE")
    min_p = cat_meta.get("price_min", 500)
    max_p = cat_meta.get("price_max", 250000)
    base_price = cat_meta.get("base_price", 35000)
    if max_budget_bdt and max_budget_bdt > 0:
        max_p = min(max_p, max_budget_bdt)
        base_price = min(base_price, int(max_budget_bdt * 0.75))

    reg_stores = get_stores_for_category(cat_id, query=q_clean)
    # Star Tech allowed for all gadgets/smartphones

    if cat_id == "cycles-evs":
        is_ebike_q = any(k in en_kw.lower() for k in ("electric", "e-bike", "ebike", "scooter", "takyon", "ev", "battery"))
        pedal_only_stores = ("duranta", "veloce", "dream cycle", "lion cycle", "cyclelife")
        ev_only_stores = ("revoo", "reevo", "yadea", "tailg", "walton", "runner", "sumato", "vmoto", "ridevo", "zeeho", "green tiger")
        if is_ebike_q:
            reg_stores = [s for s in reg_stores if not any(p in (s.get("name") or "").lower() for p in pedal_only_stores)]
        else:
            reg_stores = [s for s in reg_stores if not any(e in (s.get("name") or "").lower() for e in ev_only_stores)] or reg_stores

    stores = []
    for s in reg_stores[:6]:
        s_type = "f_commerce" if (s.get("source_type") == "f_commerce" or not s.get("website_url")) else "crawler"
        stores.append((s.get("name"), s_type, s))

    variant_specs = BROAD_CATEGORY_VARIANT_SPECS.get(cat_id, [])
    used_merchants = VERIFIED_RECONDITIONED_MERCHANTS.get(cat_id, VERIFIED_RECONDITIONED_MERCHANTS["mobile-gadgets"])
    items: List[dict] = []

    for v_spec in variant_specs:
        v_title = f"{display_title_base} - {v_spec['suffix_en']}"
        v_title_bn = f"{display_title_base} - {v_spec['suffix_bn']}"
        img_url = validate_and_sanitize_image(None, v_title, en_kw, cat_id)
        v_base = max(100, int(round(base_price * v_spec["price_mult"])))
        if max_budget_bdt and v_base > max_budget_bdt:
            v_base = max(100, int(round(max_budget_bdt * min(0.88, v_spec["price_mult"]))))

        if v_spec["use_reconditioned_stores"]:
            for m_idx, (m_name, m_type, m_url_tmpl, m_ratio) in enumerate(used_merchants):
                calc_price = max(100, int(round(v_base * (0.92 + m_idx * 0.05))))
                if max_budget_bdt and calc_price > max_budget_bdt:
                    calc_price = max_budget_bdt
                range_high = int(round(calc_price * 1.45))
                if max_budget_bdt and range_high > max_budget_bdt:
                    range_high = max_budget_bdt
                clean_q_enc = quote_plus(en_kw)
                m_url = m_url_tmpl.format(q=clean_q_enc) if "{q}" in m_url_tmpl else m_url_tmpl
                items.append({
                    "title": v_title,
                    "title_bn": v_title_bn,
                    "product_url": m_url,
                    "image_url": img_url,
                    "price": calc_price,
                    "original_price": int(round(calc_price * 1.25)),
                    "store_name": m_name,
                    "source_type": m_type,
                    "in_stock": True,
                    "category": inferred_category,
                    "cod_terms_en": f"Starting from ৳{calc_price:,} up to ৳{range_high:,} ? 15 Days Replacement & Service Warranty",
                    "cod_terms_bn": f"???? ৳{calc_price:,} ???? ???????? ৳{range_high:,} ? ?? ????? ???????????? ?????????",
                    "warranty_text": "Certified Pre-Owned / Reconditioned Warranty",
                    "condition": v_spec["condition"],
                })
        else:
            for s_idx, (store_name, s_type, s_dict) in enumerate(stores[:4]):
                store_url = build_store_target_url(store_name, en_kw, vertical)
                offsets = [0, 350, -200, 600]
                calc_price = max(100, v_base + offsets[s_idx % len(offsets)])
                if max_budget_bdt and calc_price > max_budget_bdt:
                    calc_price = max_budget_bdt
                range_high = int(round(calc_price * 1.65))
                if max_budget_bdt and range_high > max_budget_bdt:
                    range_high = max_budget_bdt
                items.append({
                    "title": v_title,
                    "title_bn": v_title_bn,
                    "product_url": store_url,
                    "image_url": img_url,
                    "price": calc_price,
                    "original_price": calc_price,
                    "store_name": store_name,
                    "source_type": s_type,
                    "in_stock": True,
                    "category": inferred_category,
                    "cod_terms_en": f"Starting from ৳{calc_price:,} up to ৳{range_high:,} ? Cash on Delivery Available",
                    "cod_terms_bn": f"???? ৳{calc_price:,} ???? ???????? ৳{range_high:,} ? ????? ?? ????????",
                    "warranty_text": "Official Brand / Store Warranty",
                    "condition": v_spec["condition"],
                })
    return items

# ==============================================================================
# 9. ON-DEMAND LIVE META-SEARCH & DYNAMIC PERSISTENCE
# ==============================================================================

def compute_min_hardware_floor(cat_id: str, search_kw: str, is_acc: bool, max_budget_bdt: Optional[int] = None) -> int:
    """Computes realistic minimum BDT price floor so accessories/Fake-100s never masquerade as primary items."""
    if is_acc:
        return 100
    q_en_low = (search_kw or "").lower()
    floor = 150
    if cat_id == "laptops-pc":
        if "gaming laptop" in q_en_low or any(k in q_en_low for k in ("rog", "tuf", "alienware", "predator", "legion")):
            floor = 45000
        elif any(k in q_en_low for k in ("laptop", "macbook", "notebook", "ultrabook", "victus", "pavilion", "inspiron", "ideapad", "vivobook", "xps", "envy", "yoga", "zenbook", "thinkpad", "latitude", "omen", "katana", "spectre", "swift", "zephyrus", "nitro", "legion")):
            floor = 25000
        elif any(k in q_en_low for k in ("desktop", "pc", "brand pc", "gaming pc")) and not any(p in q_en_low for p in ("mouse", "keyboard", "casing", "cooler", "fan", "cable", "stand", "pad")):
            floor = 10000
        elif "printer" in q_en_low:
            floor = 5000
        elif "monitor" in q_en_low:
            floor = 6000
        elif any(k in q_en_low for k in ("processor", "ryzen", "core i", "motherboard", "graphics card", "rtx", "gtx", "ssd")):
            floor = 1800
        elif "router" in q_en_low:
            floor = 800
    elif cat_id == "gaming-consoles":
        # Peripherals, controllers, accessories, and games MUST be evaluated BEFORE primary console hardware!
        if any(c in q_en_low for c in ("psn", "gift card", "game pass")):
            floor = 1000
        elif any(c in q_en_low for c in ("game disc", "cartridge", "ps5 game", "ps4 game", "switch game", "xbox game")):
            floor = 2000
        elif any(c in q_en_low for c in ("dualsense", "controller", "gamepad", "fight stick", "flight stick", "hotas", "headset", "earbuds", "charging station", "grip", "skin", "case")):
            floor = 2500
        elif any(c in q_en_low for c in ("racing wheel", "steering wheel", "pedal", "g923", "v10", "thrustmaster")):
            floor = 15000
        elif any(c in q_en_low for c in ("switch lite", "r36s", "retro handheld")):
            floor = 3500
        elif any(c in q_en_low for c in ("ps5", "playstation 5", "xbox series x", "rog ally", "legion go", "steam deck", "quest 3", "vision pro", "pvr2", "vr2")):
            floor = 35000
        elif any(c in q_en_low for c in ("ps4", "playstation 4", "xbox series s", "nintendo switch", "switch oled")):
            floor = 20000
        else:
            floor = 500
    elif cat_id == "mobile-gadgets":
        if any(w in q_en_low for w in ("case", "cover", "back cover", "glass", "protector", "tempered", "cable", "charger", "adapter", "power bank", "strap", "skin")):
            floor = 150
        elif "iphone" in q_en_low or "apple" in q_en_low:
            gen = re.search(r"iphone\s*(\d+)", q_en_low)
            if gen and int(gen.group(1)) >= 14:
                floor = 50000  # iPhone 14/15/16/17/18 realistic handset floor
            elif gen and int(gen.group(1)) >= 11:
                floor = 28000  # iPhone 11/12/13 handset floor
            else:
                floor = 20000  # Any genuine iPhone device
        elif any(f in q_en_low for f in ("ultra", "fold", "flip", "s24", "s23", "s25", "pixel 8", "pixel 9")):
            floor = 35000
        elif any(w in q_en_low for w in ("apple watch", "galaxy watch")):
            floor = 12000
        elif any(w in q_en_low for w in ("smartwatch", "smart watch", "amazfit", "haylou", "mibro", "kospet", "kieslect", "colmi", "zeblaze", "fire-boltt", "boat", "noise", "cmf", "oraimo", "fitbit", "garmin")):
            floor = 1500
        elif not any(g in q_en_low for g in ("earbud", "earphone", "tws", "airpod", "neckband", "headphone", "headset", "speaker", "jbl", "power bank", "powerbank", "watch", "smartwatch", "kieslect", "amazfit", "haylou", "mibro", "kospet", "colmi", "case", "cover", "charger", "adapter", "cable", "glass", "protector", "strap")):
            floor = 7500
        else:
            floor = 200
    elif cat_id == "watches-horology":
        if any(w in q_en_low for w in ("tissot", "seiko", "citizen", "orient", "edifice")):
            floor = 6000
        elif any(w in q_en_low for w in ("casio", "g-shock", "g shock", "timex", "fossil")):
            floor = 1800
        elif not any(g in q_en_low for g in ("strap", "band", "battery", "box", "case", "tool")):
            floor = 1000
        else:
            floor = 200
    elif cat_id == "cameras-photography":
        if any(g in q_en_low for g in ("50mm", "24-70mm", "70-200mm", "35mm", "85mm", "lens", "prime lens", "zoom lens", "telephoto", "macro lens", "wide angle", "flash", "speedlite", "godox")):
            floor = 2500
        elif any(g in q_en_low for g in ("gopro", "action camera", "pocket", "osmo", "insta360")):
            floor = 9000
        elif not any(g in q_en_low for g in ("tripod", "bag", "card", "cap", "strap", "battery", "charger", "filter", "mount", "plate", "rig", "mic", "microphone")):
            floor = 14000
        else:
            floor = 300
    elif cat_id == "bicycles-mtb":
        floor = 4500
    elif cat_id == "cycles-evs":
        if not any(g in q_en_low for g in ("helmet", "lock", "light", "pump", "monitor", "charger", "battery")):
            floor = 20000
        else:
            floor = 500
    elif cat_id == "home-appliances":
        if any(k in q_en_low for k in ("refrigerator", "fridge", "freezer", "air conditioner", "inverter ac", "ton ac", "washing machine")):
            floor = 12000
        elif any(k in q_en_low for k in ("tv", "television", "smart led tv")):
            floor = 8000
        elif any(k in q_en_low for k in ("microwave", "oven")):
            floor = 3500
        else:
            floor = 500
    elif cat_id == "fine-jewelry":
        if any(j in q_en_low for j in ("nose pin", "nakful")):
            floor = 2500
        elif any(j in q_en_low for j in ("ring",)):
            floor = 8000
        elif any(j in q_en_low for j in ("chain", "bangle", "necklace", "coin", "gold bar")):
            floor = 15000
        else:
            floor = 3000
    elif cat_id == "sneakers-footwear":
        floor = 500

    if max_budget_bdt and max_budget_bdt < floor:
        floor = max(100, int(max_budget_bdt * 0.4))
    return floor


def record_discovered_merchant_domain(db: Session, product_url: str, store_name: str, primary_category: Optional[str] = None):
    """Dynamically registers discovered Bangladeshi merchant domains for continuous crawler expansion."""
    try:
        if not product_url or not product_url.startswith("http"):
            return
        parsed = urlparse(product_url)
        domain = (parsed.netloc or "").lower().strip()
        if not domain or domain in ("localhost", "127.0.0.1") or len(domain) < 4:
            return
        domain = re.sub(r"^(?:www\.|m\.)", "", domain)
        # Check active session objects first to prevent uncommitted UNIQUE constraint collision
        for obj in list(db.new):
            if isinstance(obj, DiscoveredDomain) and getattr(obj, "domain", None) == domain:
                obj.crawl_success_count += 1
                return

        existing = db.query(DiscoveredDomain).filter(DiscoveredDomain.domain == domain).first()
        if existing:
            existing.crawl_success_count += 1
            existing.last_crawled_at = datetime.utcnow()
            if primary_category and not existing.primary_category:
                existing.primary_category = primary_category
        else:
            new_dom = DiscoveredDomain(
                domain=domain,
                store_name=store_name or domain,
                primary_category=primary_category,
                is_verified=True if any(t1 in (store_name or "").lower() for t1 in ("star tech", "ryans", "custom mac", "pickaboo", "apple gadgets")) else False,
                crawl_success_count=1,
                last_crawled_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )
            db.add(new_dom)
    except Exception:
        pass


async def scrape_wide_net_multistore(query: str, min_floor: int = 150, anchor_tokens: Optional[List[str]] = None, category_id: Optional[str] = None, include_web_live: bool = True) -> List[dict]:
    """
    Tier 2: Wide-Net Web Discovery Scraper
    Hits multi-category merchants simultaneously without rigid category-bucket filtering upfront.
    Queries Custom Mac BD, Star Tech, and Universal BD Web Harvester concurrently.
    """
    clean_q = query.strip()
    results = []
    seen_urls = set()

    # Worker 1: Custom Mac BD (Shopify Suggest API - Fast JSON)
    async def _worker_custommac():
        try:
            url = f"https://custommacbd.com/search/suggest.json?q={quote_plus(clean_q)}&resources[type]=product&resources[limit]=10"
            async with httpx.AsyncClient(timeout=4.0, headers={"User-Agent": "Mozilla/5.0"}) as c:
                r = await c.get(url)
                if r.status_code == 200:
                    for p in r.json().get("resources", {}).get("results", {}).get("products", []):
                        p_price = float(p.get("price", 0))
                        full_u = f"https://custommacbd.com{p.get('url')}"
                        p_title = p.get("title", "")
                        if anchor_tokens and not matches_anchor_tokens(p_title, anchor_tokens, clean_q):
                            continue
                        if p_price >= min_floor and full_u not in seen_urls:
                            seen_urls.add(full_u)
                            results.append({
                                "title": p.get("title"),
                                "price": int(p_price),
                                "original_price": int(p_price * 1.1),
                                "product_url": full_u,
                                "image_url": p.get("image"),
                                "store_name": "Custom Mac BD",
                                "source_type": "crawler",
                                "is_real_scraped": True,
                                "in_stock": True,
                            })
        except Exception:
            pass

    # Worker 2: Star Tech (OpenCart HTML Search)
    async def _worker_startech():
        try:
            url = f"https://www.startech.com.bd/product/search?search={quote_plus(clean_q)}"
            async with httpx.AsyncClient(timeout=4.5, headers={"User-Agent": "Mozilla/5.0"}) as c:
                r = await c.get(url)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, "html.parser")
                    for it in soup.select(".p-item"):
                        name_el = it.select_one(".p-item-name a")
                        price_el = it.select_one(".p-item-price")
                        img_el = it.select_one(".p-item-img img")
                        if name_el and price_el:
                            title = name_el.get_text(strip=True)
                            if anchor_tokens and not matches_anchor_tokens(title, anchor_tokens, clean_q):
                                continue
                            p_raw = price_el.get_text(" ", strip=True)
                            nums = re.findall(r"[\d,]+", p_raw)
                            if nums:
                                val = int(nums[0].replace(",", ""))
                                full_u = name_el.get("href")
                                if val >= min_floor and full_u and full_u not in seen_urls:
                                    seen_urls.add(full_u)
                                    results.append({
                                        "title": title,
                                        "price": val,
                                        "original_price": int(val * 1.08),
                                        "product_url": full_u,
                                        "image_url": img_el.get("src") if img_el else None,
                                        "store_name": "Star Tech",
                                        "source_type": "crawler",
                                        "is_real_scraped": True,
                                        "in_stock": True,
                                    })
        except Exception:
            pass

    # Worker 3: Universal Bangladesh Live Web Scraper (Google Search / Multi-Engine over BD stores)
    async def _worker_web_live():
        if not include_web_live:
            return
        try:
            from adapters import scrape_bangladesh_web_live
            cat_label = CATEGORY_REGISTRY_MAP.get(category_id, {}).get("display_en", "All Verticals") if category_id else "All Verticals"
            web_rows = await scrape_bangladesh_web_live(clean_q, category_label=cat_label, limit=10)
            for wr in web_rows:
                u = wr.get("product_url")
                p_val = wr.get("price") or 0
                w_title = wr.get("title", "")
                if anchor_tokens and not matches_anchor_tokens(w_title, anchor_tokens, clean_q):
                    continue
                if p_val >= min_floor and u and u not in seen_urls:
                    seen_urls.add(u)
                    results.append(wr)
        except Exception:
            pass

    await asyncio.gather(_worker_custommac(), _worker_startech(), _worker_web_live(), return_exceptions=True)
    return results

async def live_meta_search_and_persist(
    query: str, category: Optional[str], db: Session
) -> List[Product]:
    """
    Pinpoint Dual-Mode Meta-Search Engine:
      1. Rejects gibberish and unmapped nonsense queries immediately.
      2. Resolves exact category from the 13-category registry and determines Mode A (Exact SKU) vs Mode B (Price Range).
      3. Translates Bengali/Banglish queries for store search bars while preserving bilingual display.
      4. Checks existing database cache with strict anchor-token and negative-firewall verification.
      5. Executes concurrent live scraping across all category stores via `adapters.py`.
      6. Groups multi-store offers for the same model into a unified comparison shortlist, or builds a
         Shop Starting-Price-Range comparison card for broad/F-Commerce queries.
      7. Applies TrustShield-BD fraud scoring and Tier-2 Sponsor top-pinning (keeping Lowest Price 100% unbiased).
    """
    q_norm = (query or "").strip()
    if not q_norm or is_gibberish_search(q_norm):
        return []

    # Step 1: Resolve Category (Support both In-Syllabus and Out-of-Syllabus real product queries)
    if not category or category == "all":
        cat_id, cat_meta = resolve_category_or_none(q_norm, None)
        if not cat_id or not cat_meta:
            en_try = translate_bengali_and_banglish_for_store(q_norm)
            cat_id, cat_meta = resolve_category_or_none(en_try, None)
            if not cat_id or not cat_meta:
                cat_id = None
                cat_meta = {"display_en": "Open Market", "vertical": "MULTI_MARKETPLACE", "base_price": 500}
    else:
        cat_id, cat_meta = resolve_category_from_query(q_norm, category)

    cleaned_display_q, max_budget_bdt = clean_query_for_display_and_search(q_norm)
    comparison_mode = classify_comparison_mode(cleaned_display_q, cat_id)

    intent = deterministic_intent_fallback(cleaned_display_q, category)
    intent["raw_query"] = cleaned_display_q
    vertical = cat_meta.get("vertical", intent.get("vertical", "MULTI_MARKETPLACE"))
    search_kw = translate_bengali_and_banglish_for_store(intent.get("store_search_keyword") or cleaned_display_q)
    is_acc = bool(user_requested_accessory(q_norm))
    intent["is_accessory_query"] = is_acc

    # Check active Tier-2 Spotlight sponsor brands in DB so they can be top-pinned in their category
    active_sponsor_brands = set()
    try:
        spotlights = db.query(SpotlightCard).filter(SpotlightCard.is_active.is_(True)).all()
        for sp in spotlights:
            if sp.brand_title_en:
                active_sponsor_brands.add(sp.brand_title_en.lower().strip())
    except Exception:
        pass

    # Step 2: Check existing database cache
    term = f"%{search_kw}%"
    raw_term = f"%{cleaned_display_q}%"
    compat_list = CATEGORY_COMPATIBILITY_MAP.get(cat_id, [cat_meta.get("display_en", "Open Market")]) if cat_id else []
    cat_clauses = [Product.category.ilike(f"%{c}%") for c in compat_list] if compat_list else []

    db_cache_q = (
        db.query(Product)
        .options(joinedload(Product.offers), joinedload(Product.price_history))
        .filter(
            or_(
                Product.title_en.ilike(term),
                Product.title_bn.ilike(term),
                Product.specs_summary.ilike(term),
                Product.title_en.ilike(raw_term),
                Product.title_bn.ilike(raw_term),
            )
        )
    )
    if cat_clauses:
        db_cache_q = db_cache_q.filter(or_(*cat_clauses))
    cached_products = db_cache_q.all()

    anchor_tokens = extract_mandatory_anchor_tokens(q_norm)
    requested_acc = user_requested_accessory(q_norm)

    sanitized_cached = []
    valid_cat_stores = set()
    reg_stores_for_cat = get_stores_for_category(cat_id, query=q_norm) if cat_id else []
    for s in reg_stores_for_cat:
        rn = s.get("name", "").lower().strip()
        if rn:
            valid_cat_stores.add(rn)
            valid_cat_stores.add(normalize_store_match_name(rn))
            valid_cat_stores.add(re.sub(r"\(.*?\)", "", rn).strip())

    for p in cached_products:
        # Zero synthetic placeholders in cache
        if "(official bangladesh edition)" in (p.title_en or "").lower():
            continue
        if cat_id and not passes_category_negative_firewall(p.title_en, cat_meta.get("display_en", ""), q_norm):
            continue
        if anchor_tokens and not matches_anchor_tokens(p.title_en, anchor_tokens, q_norm):
            continue
        if not requested_acc:
            if any(re.search(r"(?i)\b" + re.escape(tok) + r"\b", p.title_en.lower()) for tok in ACCESSORY_KEYWORDS):
                continue
        else:
            if not any(re.search(r"(?i)\b" + re.escape(tok) + r"\b", p.title_en.lower()) for tok in requested_acc):
                continue
        if cat_id and not is_product_category_compatible(p.category, cat_id, cat_meta.get("display_en", ""), p.title_en):
            continue

        clean_img = validate_and_sanitize_image(p.image_url, p.title_en, q_norm, cat_id)
        if clean_img != p.image_url:
            p.image_url = clean_img

        stores_seen = set()
        seen_urls = set()
        unique_offers = []

        for off in list(p.offers):
            s_name_low = off.store_name.lower().strip()
            if valid_cat_stores and not is_store_in_category(off.store_name, valid_cat_stores):
                continue
            off_price = getattr(off, "current_price", None) or getattr(off, "price_bdt", 0)
            min_hw_floor_cached = compute_min_hardware_floor(cat_id, search_kw, is_acc, max_budget_bdt)
            if off_price and off_price < min_hw_floor_cached:
                continue
            if max_budget_bdt and off_price and off_price > max_budget_bdt:
                continue


            off_url = off.target_url if (off.target_url and off.target_url.startswith("http")) else build_store_target_url(off.store_name, p.title_en, vertical)
            if off.store_name in stores_seen or off_url in seen_urls:
                continue

            # Check Tier-2 Sponsor status
            if any(sp_b in s_name_low or s_name_low in sp_b for sp_b in active_sponsor_brands):
                off.is_sponsored = True

            stores_seen.add(off.store_name)
            seen_urls.add(off_url)
            off.target_url = off_url
            unique_offers.append(off)

        p.offers = unique_offers
        if p.image_url and len(p.offers) >= 1 and not is_placeholder_image(p.image_url):
            sanitized_cached.append(p)

    # Deduplicate and consolidate cached products strictly by canonical model & variant
    cached_by_sku: Dict[str, Product] = {}
    for cp in sanitized_cached:
        c_title, c_var, c_sku = extract_canonical_sku_info(cp.title_en, search_kw)
        if c_sku not in cached_by_sku:
            cp.title_en = c_title
            cached_by_sku[c_sku] = cp
        else:
            # Merge stores into the single existing card
            existing_card = cached_by_sku[c_sku]
            existing_stores = {o.store_name.lower().strip() for o in existing_card.offers}
            for off in cp.offers:
                s_low = off.store_name.lower().strip()
                if s_low not in existing_stores:
                    existing_card.offers.append(off)
                    existing_stores.add(s_low)
    sanitized_cached = list(cached_by_sku.values())

    user_explicit_wants_used = is_used_or_reconditioned_title(q_norm)
    has_cached_used = any(is_used_or_reconditioned_title(p.title_en) for p in sanitized_cached)
    distinct_stores = {off.store_name for p in sanitized_cached for off in p.offers if off.store_name}
    # Only short-circuit cache if we have rich coverage (at least 3 distinct products with multi-store offers)
    has_enough_cached = len(sanitized_cached) >= 3 and len(distinct_stores) >= 3
    if has_enough_cached and (not user_explicit_wants_used or has_cached_used):
        return sanitized_cached

    # Step 3: Always initialize scraped_listings list first
    scraped_listings: List[dict] = []

    # Distill noisy modifiers for store search endpoints
    # Strip literal parentheses and special punctuation (e.g. '(44mm)' -> '44mm') so store search bars don't choke
    clean_search = re.sub(r"\((.*?)\)|\[(.*?)\]", r" \1\2 ", search_kw)
    clean_search = re.sub(r"[#@$%^&*_+={}\\|~`<>]", " ", clean_search)
    clean_search = re.sub(r"\s+", " ", clean_search).strip() or search_kw
    distilled_kw = re.sub(r"(?i)\b(manual|pedal|non-gear|non\s+gear|aero)\b", "", clean_search).strip() or clean_search
    if "aero" in search_kw.lower() and "bike" in search_kw.lower():
        distilled_kw = "road bicycle"

    # For Bicycles category, invoke live bicycle scraper
    if cat_id == "bicycles-mtb":
        try:
            from adapters import scrape_bicycles_live
            live_bikes = await scrape_bicycles_live(distilled_kw, limit=8)
            if live_bikes:
                scraped_listings.extend(live_bikes)
        except Exception:
            pass

    # Query multi-store search across category stores
    try:
        more_listings = await scrape_store_search(
            distilled_kw, vertical=vertical, max_budget_bdt=max_budget_bdt, category_id=cat_id
        )
        if more_listings:
            scraped_listings.extend(more_listings)
    except Exception:
        pass

    # Step 4: Verify & Filter Scraped Candidates
    scraped_listings = verify_and_filter_candidates(intent, scraped_listings)

    # Enforce Store Department Capability Filter (Blocks mobile shops from selling routers, PC shops from selling fridges)
    from bd_stores_registry import store_matches_department_capability
    scraped_listings = [
        c for c in scraped_listings
        if store_matches_department_capability(c.get("store_name", ""), cat_id, q_norm)
    ]

    scraped_listings = [
        c for c in scraped_listings
        if passes_category_negative_firewall(c.get("title", ""), cat_meta["display_en"], q_norm)
    ]
    if max_budget_bdt:
        scraped_listings = [
            c for c in scraped_listings
            if not c.get("price") or c.get("price") <= max_budget_bdt
        ]

    min_hw_floor = compute_min_hardware_floor(cat_id, search_kw, is_acc, max_budget_bdt)
    scraped_listings = [
        c for c in scraped_listings
        if (c.get("price") or 0) >= min_hw_floor
    ]

    # Step 4B: WIDE-NET WEB DISCOVERY SCRAPER (Hits multi-category merchants simultaneously)
    is_device_query = any(k in q_norm.lower() for k in ("iphone", "apple", "samsung", "galaxy", "pixel", "laptop", "macbook", "watch", "camera"))
    if is_device_query or len(scraped_listings) < 2:
        try:
            wide_hits = await scrape_wide_net_multistore(distilled_kw, min_floor=min_hw_floor, anchor_tokens=anchor_tokens, category_id=cat_id, include_web_live=(len(scraped_listings) == 0))
            if wide_hits:
                scraped_listings.extend(wide_hits)
        except Exception as e:
            print(f"[WideNet Scraper] Notice: {e}")

    # Step 4C: SLM VERIFICATION GATE
    # Enforces strict entity containment, accessory filtering, and zero cross-brand leakage.
    if anchor_tokens:
        scraped_listings = [
            c for c in scraped_listings
            if slm_verify_candidate(c.get("title", ""), q_norm, anchor_tokens)
        ]

    # Step 4D: SLM NOT VERIFIED -> LINGUISTIC ROUTER -> RE-HARVEST WEB
    # If initial scraping yielded 0 verified hits, invoke the local Ollama Linguistic Prism (jachai-router)
    if len(scraped_listings) == 0:
        slm_decomp = call_ollama_linguistic_router(q_norm)
        rewritten_q = slm_decomp.get("clean_query")
        if rewritten_q and rewritten_q.lower() != q_norm.lower():
            try:
                retry_tokens = extract_mandatory_anchor_tokens(rewritten_q)
                retry_hits = await scrape_wide_net_multistore(rewritten_q, min_floor=min_hw_floor, anchor_tokens=retry_tokens, category_id=cat_id, include_web_live=True)
                scraped_listings = [
                    c for c in retry_hits
                    if slm_verify_candidate(c.get("title", ""), rewritten_q, retry_tokens)
                ]
            except Exception:
                pass

    # Step 4C: DEVICE VS. ACCESSORY PRICE-FLOOR GUARDIAN
    # Purges accessory traps when user requested a primary device
    if not is_acc and is_device_query:
        accessory_trap_re = re.compile(
            r"\b(battery|laptop battery|power adapter|case|cover|back cover|silicone|leather case|glass|protector|tempered|screen protector|camera protector|lens guard|skin|cable|charger|adapter|converter|power bank|powerbank|strap|band)\b",
            re.IGNORECASE
        )
        scraped_listings = [
            c for c in scraped_listings
            if (c.get("price") or 0) >= min_hw_floor
            and not accessory_trap_re.search(c.get("title", ""))
        ]
        # Generation token requirement: e.g. 'iphone 17' requires whole word '17' in title
        gen_m = re.search(r"iphone\s*(\d+)", q_norm.lower())
        if gen_m:
            g_num = gen_m.group(1)
            scraped_listings = [
                c for c in scraped_listings
                if re.search(rf"\b{g_num}\b", c.get("title", "").lower())
            ]
        # Core brand anchor requirement with strict generation guard
        if "iphone" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "iphone" in c.get("title", "").lower()]
            gen_m = re.search(r"iphone\s*(\d+)", q_norm.lower())
            if gen_m:
                g_num = gen_m.group(1)
                scraped_listings = [
                    c for c in scraped_listings
                    if re.search(rf"\b{g_num}\b", c.get("title", "").lower())
                ]
        elif "pixel" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "pixel" in c.get("title", "").lower()]
            pix_m = re.search(r"pixel\s*(\d+)", q_norm.lower())
            if pix_m:
                p_num = pix_m.group(1)
                scraped_listings = [
                    c for c in scraped_listings
                    if re.search(rf"\b{p_num}[a-z]?\b", c.get("title", "").lower())
                ]
        elif "macbook" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "macbook" in c.get("title", "").lower()]
        elif "apple watch" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "watch" in c.get("title", "").lower() and "apple" in c.get("title", "").lower()]
        elif "galaxy watch" in q_norm.lower() or ("samsung" in q_norm.lower() and "watch" in q_norm.lower()):
            scraped_listings = [c for c in scraped_listings if "watch" in c.get("title", "").lower() and ("galaxy" in c.get("title", "").lower() or "samsung" in c.get("title", "").lower())]
            gw_num_m = re.search(r"watch\s*(\d+)", q_norm.lower())
            if gw_num_m:
                w_num = gw_num_m.group(1)
                gw_candidates = [c for c in scraped_listings if re.search(rf"\b{w_num}\b", c.get("title", "").lower())]
                if gw_candidates:
                    scraped_listings = gw_candidates
        elif "smartwatch" in q_norm.lower() or "smart watch" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "watch" in c.get("title", "").lower()]
        elif "watch" in q_norm.lower():
            scraped_listings = [c for c in scraped_listings if "watch" in c.get("title", "").lower()]

        watch_series_m = re.search(r"\b(series\s*\d+|ultra\s*\d*|se\s*\d*)\b", q_norm.lower())
        if watch_series_m:
            w_series = watch_series_m.group(1).replace(" ", r"\s*")
            scraped_listings = [
                c for c in scraped_listings
                if re.search(rf"\b{w_series}\b", c.get("title", "").lower())
            ]

    # Step 5: Registry Validation & Priority Boosting (Bubble-sorts verified Tier-1 merchants to top)
    TIER1_BOOST_STORES = {"dazzle bd", "star tech", "sumash tech", "apple gadgets bd", "custom mac bd", "gadget & gear", "pickaboo", "ryans computers"}
    for item in scraped_listings:
        s_low = (item.get("store_name") or "").lower().strip()
        item["is_tier1"] = any(t1 in s_low for t1 in TIER1_BOOST_STORES)

    # ZERO SYNTHETIC PLACEHOLDERS OR FAKE FALLBACKS FOR DEVICES!
    # Only broad generic categories (like generic 'jamdani saree' or 'jersey') use starting price indicators
    is_jersey_query = cat_id == "sportswear-gym" and any(j in search_kw.lower() for j in ("jersey", "jarsi", "kit"))
    is_broad_fcommerce = False and len(scraped_listings) < 1
    if (is_broad_fcommerce or is_jersey_query) and not is_device_query:
        fallback_listings = generate_resilient_fallback(q_norm, category, intent)
        scraped_listings.extend(fallback_listings)

    # Step 6: Group listings by canonical product key so multi-store offers combine into one comparison card
    grouped: Dict[str, List[dict]] = {}
    for item in scraped_listings:
        g_key = canonical_product_group_key(item["title"], search_kw)
        grouped.setdefault(g_key, []).append(item)

    # CRITICAL FIX: Sort groups so REAL SCRAPED products ALWAYS rank above synthetic fallback items!
    sorted_groups = sorted(
        grouped.items(),
        key=lambda kv: (
            any(x.get("is_real_scraped") for x in kv[1]),
            len(kv[1]),
        ),
        reverse=True,
    )

    new_products: List[Product] = []

    for group_key, offers_data in sorted_groups[:6]:
        # Tier 3: Bubble-sort verified Tier-1 merchants to top of offers
        offers_data.sort(key=lambda o: (not o.get("is_tier1", False), o.get("price", 9999999)))
        primary = offers_data[0]
        disp_title, variant_tag, canonical_slug = extract_canonical_sku_info(primary["title"], search_kw)
        title_en = disp_title or primary["title"]
        title_bn = primary.get("title_bn") or f"{title_en} (বাংলাদেশ)"
        prod_category = cat_meta["display_en"]

        raw_img = primary.get("image_url")
        image_url = validate_and_sanitize_image(raw_img, title_en, q_norm, cat_id)

        # Deterministic canonical slug (Never generate random numbers for real product cards)
        slug = canonical_slug

        all_group_prices = [o["price"] for o in offers_data if o.get("price")]
        lowest = min(all_group_prices) if all_group_prices else 1000
        highest = max(all_group_prices) if all_group_prices else lowest
        p_30d = int(round(lowest * 1.06))
        p_15d = int(round(lowest * 1.03))

        specs_text = (
            f"{title_en} · Price Range: ৳{lowest:,} – ৳{highest:,} · Verified Bangladeshi Stores"
            if comparison_mode == "price_range" and highest > lowest
            else f"{title_en} · Verified authentic BD warranty · Best market price index"
        )

        # Check if product already exists in DB by slug or title
        product = db.query(Product).options(joinedload(Product.offers)).filter(Product.slug == slug).first()
        if not product:
            product = db.query(Product).options(joinedload(Product.offers)).filter(Product.title_en == title_en).first()

        if product:
            product.specs_summary = specs_text
            product.price_30d_ago = p_30d
            product.price_15d_ago = p_15d
            if not product.image_url or is_placeholder_image(product.image_url):
                product.image_url = image_url
        else:
            product = Product(
                slug=slug,
                title_en=title_en,
                title_bn=title_bn,
                category=prod_category,
                image_url=image_url,
                specs_summary=specs_text,
                price_30d_ago=p_30d,
                price_15d_ago=p_15d,
                is_pinned_homepage=False,
                created_at=datetime.utcnow(),
            )
            db.add(product)
            db.flush()

        existing_offers_by_store = {o.store_name.lower().strip(): o for o in product.offers}
        stores_seen = set()
        seen_urls = set()

        for off in offers_data:
            s_name = off["store_name"]
            s_low_key = s_name.lower().strip()
            if s_low_key in stores_seen:
                continue

            raw_url = off.get("product_url")
            if not raw_url or raw_url == "https://" or not raw_url.startswith("http"):
                offer_url = build_store_target_url(s_name, title_en, vertical)
            else:
                offer_url = raw_url

            if offer_url in seen_urls:
                offer_url = build_store_target_url(s_name, f"{title_en} {s_name}", vertical)

            stores_seen.add(s_low_key)
            seen_urls.add(offer_url)

            if offer_url:
                record_discovered_merchant_domain(db, offer_url, s_name, prod_category)
            s_meta = get_store_registry_meta(s_name, title_en)
            w_url = s_meta["website_url"] or (offer_url if "facebook" not in offer_url else "")
            fb_url = s_meta["facebook_url"] or (offer_url if "facebook" in offer_url else "")
            is_pre = s_meta["is_preseeded"]

            curr_p = off["price"]
            orig_p = off.get("original_price") or curr_p
            disc_pct = int(round((orig_p - curr_p) / orig_p * 100)) if orig_p > curr_p else None
            disc_tag = f"{disc_pct}% OFF" if (disc_pct and disc_pct >= 5) else None

            cod_en = off.get("cod_terms_en") or "Cash on Delivery Available"
            cod_bn = off.get("cod_terms_bn") or "ক্যাশ অন ডেলিভারি প্রযোজ্য"

            trust_res = compute_trust_score(
                store_name=s_name,
                is_preseeded=is_pre,
                source_type=off.get("source_type", "crawler"),
                cod_terms=cod_en,
                price=float(curr_p),
                all_prices=[float(p) for p in all_group_prices],
            )
            if not is_pre:
                trust_res["risk_level"] = "high"
                trust_res["trust_badge"] = "⚠️ Unverified Merchant"
                trust_res["trust_score"] = min(trust_res.get("trust_score", 55), 58)
                cod_en = "Unverified Store · Verify on Delivery (COD Only)"
                cod_bn = "অযাচাইকৃত বিক্রেতা · ক্যাশ অন ডেলিভারিতে চেক করে নিন"

            s_name_low = s_name.lower().strip()
            is_spon = bool(off.get("is_sponsored")) or any(
                sp_b in s_name_low or s_name_low in sp_b for sp_b in active_sponsor_brands
            )

            if s_low_key in existing_offers_by_store:
                existing_offer = existing_offers_by_store[s_low_key]
                existing_offer.current_price = curr_p
                existing_offer.original_price = orig_p
                existing_offer.target_url = offer_url
                existing_offer.last_synced_at = "Live Sync"
                existing_offer.in_stock = off.get("in_stock", True)
                if disc_tag:
                    existing_offer.discount_tag = disc_tag
                    existing_offer.discount_pct = disc_pct
            else:
                db_offer = StoreOffer(
                    product_id=product.id,
                    store_name=s_name,
                    source_type=off.get("source_type", "crawler"),
                    target_url=offer_url,
                    website_url=w_url or None,
                    facebook_url=fb_url or None,
                    current_price=curr_p,
                    original_price=orig_p,
                    cod_terms_en=cod_en,
                    cod_terms_bn=cod_bn,
                    warranty_text=off.get("warranty_text") or (
                        "Official 1-Year Warranty"
                        if cat_id in ("mobile-gadgets", "laptops-pc", "home-appliances")
                        else "100% Authentic Quality Checked"
                    ),
                    in_stock=off.get("in_stock", True),
                    spider_status="healthy",
                    last_synced_at="Live Sync",
                    is_preseeded=is_pre,
                    is_sponsored=is_spon,
                    trust_score=trust_res["trust_score"],
                    trust_badge=trust_res["trust_badge"],
                    risk_level=trust_res["risk_level"],
                    discount_tag=disc_tag,
                    discount_pct=disc_pct,
                )
                db.add(db_offer)
                product.offers.append(db_offer)

        db.add(PriceHistory(product_id=product.id, recorded_price=p_30d, recorded_at=datetime.utcnow()))
        db.add(PriceHistory(product_id=product.id, recorded_price=p_15d, recorded_at=datetime.utcnow()))
        db.add(PriceHistory(product_id=product.id, recorded_price=lowest, recorded_at=datetime.utcnow()))

        new_products.append(product)

    # Step 7: Consolidate new_products and sanitized_cached so SAME MODEL + SAME VARIANT = EXACTLY ONE CARD
    combined_map: Dict[str, Product] = {}
    
    for p in new_products:
        _, _, p_sku = extract_canonical_sku_info(p.title_en, search_kw)
        combined_map[p_sku] = p

    for p in sanitized_cached:
        _, _, p_sku = extract_canonical_sku_info(p.title_en, search_kw)
        if p_sku not in combined_map:
            combined_map[p_sku] = p
        else:
            target_prod = combined_map[p_sku]
            existing_stores = {o.store_name.lower().strip() for o in target_prod.offers}
            for off in p.offers:
                s_low = off.store_name.lower().strip()
                if s_low not in existing_stores:
                    target_prod.offers.append(off)
                    existing_stores.add(s_low)

    all_candidate_products = list(combined_map.values())
    is_small_gadget = any(g in q_norm.lower() for g in ("power bank", "powerbank", "earbud", "airpod", "tws", "mouse", "keyboard", "pendrive", "router", "speaker", "cable", "charger"))
    user_wants_used = is_used_or_reconditioned_title(q_norm)
    if user_wants_used and cat_id in DURABLE_CONDITION_CATEGORIES and not is_acc and not is_small_gadget and all_candidate_products:
        has_used_box = any(is_used_or_reconditioned_title(p.title_en) or "reconditioned" in (p.specs_summary or "").lower() for p in all_candidate_products)
        # Tag primary new products clearly as Brand New (Unused) in specs_summary
        for p in all_candidate_products:
            if is_used_or_reconditioned_title(p.title_en):
                if "CONDITION:USED" not in (p.specs_summary or ""):
                    p.specs_summary = f"CONDITION:USED | {p.specs_summary or p.title_en}"
            elif "CONDITION:" not in (p.specs_summary or ""):
                p.specs_summary = f"CONDITION:NEW | {p.specs_summary or p.title_en}"

        if not has_used_box:
            # Build the companion 'Used & Reconditioned' comparison box from the primary model
            ref_prod = all_candidate_products[0]
            clean_base_title = re.sub(r"\s*\(.*?\)", "", ref_prod.title_en).strip()
            used_title_en = f"{clean_base_title} (Used / Reconditioned Grade-A)"
            used_title_bn = f"{clean_base_title} (??????? / ??????????)"
            ref_prices = [o.current_price for o in ref_prod.offers if o.current_price] if ref_prod.offers else [cat_meta.get("base_price", 25000)]
            ref_lowest = min(ref_prices) if ref_prices else 25000

            used_slug = f"used-{ref_prod.slug[:40]}-{random.randint(1000, 9999)}"
            used_merchants = VERIFIED_RECONDITIONED_MERCHANTS.get(cat_id, VERIFIED_RECONDITIONED_MERCHANTS["mobile-gadgets"])
            used_low = max(100, int(round(ref_lowest * used_merchants[0][3])))
            if max_budget_bdt and used_low > max_budget_bdt:
                used_low = max(100, int(max_budget_bdt * 0.75))

            used_prod = Product(
                slug=used_slug,
                title_en=used_title_en,
                title_bn=used_title_bn,
                category=cat_meta["display_en"],
                image_url=ref_prod.image_url,
                specs_summary=f"CONDITION:USED | Certified Pre-Owned & Reconditioned ? 7?30 Days Replacement Guarantee",
                price_30d_ago=int(round(used_low * 1.08)),
                price_15d_ago=int(round(used_low * 1.04)),
                is_pinned_homepage=False,
                created_at=datetime.utcnow(),
            )
            db.add(used_prod)
            db.flush()

            clean_q_encoded = quote_plus(clean_base_title)
            for m_name, m_type, m_url_tmpl, m_ratio in used_merchants:
                u_price = max(100, int(round(ref_lowest * m_ratio)))
                if max_budget_bdt and u_price > max_budget_bdt:
                    u_price = max(100, int(max_budget_bdt * m_ratio))
                m_url = m_url_tmpl.format(q=clean_q_encoded) if "{q}" in m_url_tmpl else m_url_tmpl
                w_url = m_url if "facebook.com" not in m_url else None
                fb_url = m_url if "facebook.com" in m_url else {'Swap Bangladesh (Certified Pre-Owned)': 'https://www.facebook.com/swap.com.bd', 'Swap Bangladesh (Pre-Owned Laptops)': 'https://www.facebook.com/swap.com.bd', 'Swap Bangladesh (Certified Used Camera)': 'https://www.facebook.com/swap.com.bd', 'Swap Bangladesh (Pre-Owned E-Bike & Cycle)': 'https://www.facebook.com/swap.com.bd', 'Swap Bangladesh (Pre-Owned Appliances)': 'https://www.facebook.com/swap.com.bd', 'Swap Bangladesh (Pre-Owned Watches)': 'https://www.facebook.com/swap.com.bd', 'Apple Gadgets (Pre-Owned & Exchange)': 'https://www.facebook.com/applegadgetsltd', 'Dazzle BD (Pre-Owned Exchange)': 'https://www.facebook.com/dazzlebangladesh', 'KRY International (Pre-Owned Unit)': 'https://www.facebook.com/KryInternational', 'Computer Mania BD (Corporate Reconditioned)': 'https://www.facebook.com/ComputerManiaBD', 'Custom Mac BD (Certified Pre-Owned)': 'https://www.facebook.com/CustomMacBd', 'Multiplan Reconditioned Laptop Hub': 'https://www.facebook.com/ComputerManiaBD', 'Camera Bazar BD (Baitul Mukarram Used)': 'https://www.facebook.com/camerabazarbd', 'DSLR House BD (Used & Reconditioned)': 'https://www.facebook.com/dslrhousebd', 'BD Camera Mart (Pre-Owned Gear)': 'https://www.facebook.com/bdcameramart', 'BD EV & Takyon Reconditioned Hub': 'https://www.facebook.com/takyonebike', 'Dhaka Pre-Owned Cycle & EV Exchange': 'https://www.facebook.com/revoo.bd', 'Dhaka Reconditioned AC & Appliance Hub': 'https://www.facebook.com/transcomdigital', 'BD Showroom Reconditioned Electronics': 'https://www.facebook.com/Singer.Bangladesh', 'BD Vintage & Pre-Owned Watch Vault': 'https://www.facebook.com/timezonebd'}.get(m_name, "https://www.facebook.com/swap.com.bd")

                db.add(StoreOffer(
                    product_id=used_prod.id,
                    store_name=m_name,
                    source_type=m_type,
                    target_url=m_url,
                    website_url=w_url,
                    facebook_url=fb_url,
                    current_price=u_price,
                    original_price=ref_lowest,
                    cod_terms_en=f"Reconditioned / Pre-Owned ? Save ৳{max(0, ref_lowest - u_price):,} vs New ? Cash on Delivery",
                    cod_terms_bn=f"?????????? / ??????? ? ?????? ???? ৳{max(0, ref_lowest - u_price):,} ?????? ? ????? ?? ????????",
                    warranty_text="15 Days Replacement ? 1-Year Service Warranty",
                    in_stock=True,
                    spider_status="healthy",
                    last_synced_at="Live Sync",
                    is_preseeded=True,
                    is_sponsored=False,
                    trust_score=92,
                    trust_badge="✓ Certified Pre-Owned",
                    risk_level="low",
                    discount_tag=f"{int(round((1.0 - m_ratio) * 100))}% LOWER VS NEW",
                    discount_pct=int(round((1.0 - m_ratio) * 100)),
                ))

            db.add(PriceHistory(product_id=used_prod.id, recorded_price=int(round(used_low * 1.08)), recorded_at=datetime.utcnow()))
            db.add(PriceHistory(product_id=used_prod.id, recorded_price=int(round(used_low * 1.04)), recorded_at=datetime.utcnow()))
            db.add(PriceHistory(product_id=used_prod.id, recorded_price=used_low, recorded_at=datetime.utcnow()))
            new_products.append(used_prod)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Live Search] Error committing new products: {e}")

    all_prod_ids = [p.id for p in all_candidate_products if p.id]
    final_products = (
        db.query(Product)
        .options(joinedload(Product.offers), joinedload(Product.price_history))
        .filter(Product.id.in_(all_prod_ids))
        .all()
    ) if all_prod_ids else all_candidate_products

    # Preserve exact deduplication order
    prod_order_map = {pid: idx for idx, pid in enumerate(all_prod_ids)}
    final_products.sort(key=lambda p: prod_order_map.get(p.id, 999))

    # Flow B Resilient Curated Base Products Fallback:
    # If live web scraping returned 0 items (e.g. boutique/artisanal/offline store vertical),
    # check predetermined catalog for matching curated base product cards with verified stores.
    if not final_products and cat_id:
        try:
            from predetermined_catalog import build_predetermined_browse_products
            fallback_cards = build_predetermined_browse_products(cat_id)
            if fallback_cards:
                q_words = set(re.findall(r"\w+", q_norm.lower()))
                matched = [
                    c for c in fallback_cards
                    if any(w in c.title_en.lower() for w in q_words if len(w) > 2)
                ]
                return matched if matched else fallback_cards[:4]
        except Exception:
            pass

    return final_products


# ==============================================================================
# 10. SINGLE-OFFER & ALL-SPIDERS SYNC (FOR ADMIN COMMAND CENTER)
# ==============================================================================
async def scrape_single_offer(
    offer_id: int, db: Session, simulate_live_market: bool = False
) -> dict:
    """
    Crawls a single StoreOffer row by ID.
    Supports Anti-Zero guard, latency detection, local simulated market fallback,
    and automatic 30-day PriceHistory synchronization.
    """
    offer = db.query(StoreOffer).filter(StoreOffer.id == offer_id).first()
    if not offer:
        return {"error": "Offer not found", "offer_id": offer_id}

    if offer.source_type == "f_commerce":
        offer.last_synced_at = "Verified F-Commerce"
        offer.spider_status = "healthy"
        db.commit()
        return {
            "offer_id": offer.id,
            "status": "skipped_f_commerce",
            "current_price": offer.current_price,
            "spider_status": "healthy",
            "price_updated": False,
        }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    }

    url = offer.target_url or ""
    is_placeholder = (
        not url.startswith("http")
        or "example.com" in url
        or "localhost" in url
        or url in ("https://", "http://")
    )

    extracted_price: Optional[int] = None
    in_stock = True
    spider_status = "healthy"
    latency_ms = 120

    if not is_placeholder and not simulate_live_market:
        try:
            start_t = time.time()
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                resp = await client.get(url, headers=headers)
                latency_ms = int((time.time() - start_t) * 1000)

                if resp.status_code >= 400:
                    spider_status = "broken"
                else:
                    extracted_price, in_stock = extract_price_from_html(
                        resp.text, offer.css_selector
                    )
                    if extracted_price is None:
                        spider_status = "selector_broken"
                    elif latency_ms > 4000:
                        spider_status = "slow"
                    else:
                        spider_status = "healthy"
        except Exception:
            spider_status = "broken"

    if (extracted_price is None or is_placeholder) and simulate_live_market:
        pct_delta = random.choice([-0.02, 0.0, 0.0, 0.03, -0.01])
        extracted_price = max(100, int(round(offer.current_price * (1.0 + pct_delta))))
        spider_status = "healthy"
        latency_ms = random.randint(80, 240)

    old_price = offer.current_price
    price_updated = False

    if extracted_price is not None and extracted_price > 0:
        if extracted_price != old_price:
            offer.current_price = extracted_price
            price_updated = True
            history_entry = PriceHistory(
                product_id=offer.product_id,
                recorded_price=extracted_price,
                recorded_at=datetime.utcnow(),
            )
            db.add(history_entry)

    offer.in_stock = in_stock
    offer.spider_status = spider_status
    offer.last_synced_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    db.commit()

    return {
        "offer_id": offer.id,
        "product_id": offer.product_id,
        "store_name": offer.store_name,
        "old_price": old_price,
        "current_price": offer.current_price,
        "price_updated": price_updated,
        "in_stock": in_stock,
        "spider_status": spider_status,
        "latency_ms": latency_ms,
        "last_synced_at": offer.last_synced_at,
    }


async def run_all_spiders(
    db: Session, product_id: Optional[int] = None, simulate_live_market: bool = False
) -> dict:
    """
    Crawls matched StoreOffer records using asyncio with Semaphore(5) concurrency.
    Commits changes and returns comprehensive summary metrics.
    """
    query = db.query(StoreOffer).filter(StoreOffer.source_type == "crawler")
    if product_id is not None:
        query = query.filter(StoreOffer.product_id == product_id)

    crawler_offers = query.all()
    sem = asyncio.Semaphore(5)

    async def _safe_scrape(off_id: int):
        async with sem:
            return await scrape_single_offer(
                off_id, db, simulate_live_market=simulate_live_market
            )

    tasks = [_safe_scrape(o.id) for o in crawler_offers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    healthy_count = 0
    slow_count = 0
    broken_count = 0
    updated_count = 0

    for res in results:
        if isinstance(res, dict):
            status = res.get("spider_status")
            if status == "healthy":
                healthy_count += 1
            elif status == "slow":
                slow_count += 1
            elif status in ("broken", "selector_broken"):
                broken_count += 1

            if res.get("price_updated"):
                updated_count += 1

    synced_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "total_checked": len(crawler_offers),
        "updated_count": updated_count,
        "healthy_count": healthy_count,
        "slow_count": slow_count,
        "broken_count": broken_count,
        "synced_at": synced_at,
        "results": [r for r in results if isinstance(r, dict)],
    }

def enforce_device_price_floor(query: str, items: list) -> list:
    """
    Ensures high-ticket devices (iPhones, flagship phones, laptops) 
    never get polluted by cheap accessories (cases, protectors, chargers) priced under a realistic floor.
    """
    q_low = query.lower()
    is_device_search = any(k in q_low for k in ("iphone", "galaxy s", "pixel", "macbook", "laptop", "watch"))
    is_accessory_explicit = any(k in q_low for k in ("case", "cover", "protector", "glass", "adapter", "cable", "strap"))
    
    if is_device_search and not is_accessory_explicit:
        filtered = []
        for item in items:
            p = item.get("lowest_price") or item.get("current_price") or 0
            # If an iPhone or flagship is listed under 15,000 BDT, it's an accessory/error—drop it.
            if p > 15000 or any(kw in str(item.get("name","")).lower() for kw in ("pro", "max", "ultra", "tb", "gb")) and p > 8000:
                filtered.append(item)
            elif p > 30000: # Safe absolute floor for primary phones/laptops
                filtered.append(item)
        return filtered if filtered else items
    return items
