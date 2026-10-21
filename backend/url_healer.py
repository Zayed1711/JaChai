"""
JaChai 4-Stage Iterative URL Self-Healing & Category Page Fallback Engine (backend/url_healer.py)

Cascade when a product URL is broken, 404, or Soft-404 ("Product not found" / "0 results"):
  Iteration 1: Exact Product URL (verifies HTTP 200 and no Soft-404 message)
  Iteration 2: Store's Verified Search URL for the model (verifies product results exist)
  Iteration 3: Store's Respective Category Page (Curated Map + Live Homepage Navbar Auto-Discovery!)
  Iteration 4: Store's Official Homepage or Verified Official Facebook Page
"""

import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin, urlparse

from bs4 import BeautifulSoup
import httpx

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Soft-404 phrases commonly shown on Bangladeshi e-commerce sites when a product/search is empty
SOFT_404_PATTERNS = (
    "page not found",
    "404 not found",
    "error 404",
    "product not found",
    "no products were found",
    "no product found",
    "there is no product that matches",
    "your search returned no results",
    "0 results for",
    "nothing found",
    "oops! that page can",
    "sorry, no results",
    "we couldn't find any",
)

# Curated Category Landing Pages for major Bangladeshi retailers
STORE_CATEGORY_PAGES: Dict[str, Dict[str, str]] = {
    "startech.com.bd": {
        "mobile-gadgets": "https://www.startech.com.bd/mobile-phone",
        "laptops-pc": "https://www.startech.com.bd/laptop-notebook",
        "cameras-photography": "https://www.startech.com.bd/camera",
        "watches-horology": "https://www.startech.com.bd/smart-watch",
        "home-appliances": "https://www.startech.com.bd/appliance",
    },
    "ryans.com": {
        "laptops-pc": "https://www.ryans.com/category/laptop-all-laptop",
        "mobile-gadgets": "https://www.ryans.com/category/all-mobile-phone",
        "cameras-photography": "https://www.ryans.com/category/camera-all-camera",
        "watches-horology": "https://www.ryans.com/category/smart-watch",
    },
    "techlandbd.com": {
        "laptops-pc": "https://www.techlandbd.com/shop-laptop-computer",
        "mobile-gadgets": "https://www.techlandbd.com/smartphones-and-tablets",
        "cameras-photography": "https://www.techlandbd.com/camera-and-accessories",
        "watches-horology": "https://www.techlandbd.com/smart-watch",
    },
    "gadgetandgear.com": {
        "mobile-gadgets": "https://gadgetandgear.com/category/phone",
        "laptops-pc": "https://gadgetandgear.com/category/macbook",
        "watches-horology": "https://gadgetandgear.com/category/watch",
        "cameras-photography": "https://gadgetandgear.com/category/action-camera",
    },
    "sumashtech.com": {
        "mobile-gadgets": "https://sumashtech.com/category/phone-and-tablet",
        "laptops-pc": "https://sumashtech.com/category/macbook-and-laptop",
        "watches-horology": "https://sumashtech.com/category/smart-watch",
    },
    "applegadgetsbd.com": {
        "mobile-gadgets": "https://www.applegadgetsbd.com/category/phones-tablets",
        "laptops-pc": "https://www.applegadgetsbd.com/category/mac-laptop",
        "watches-horology": "https://www.applegadgetsbd.com/category/smart-watches",
    },
    "pickaboo.com": {
        "mobile-gadgets": "https://www.pickaboo.com/product/smartphone",
        "laptops-pc": "https://www.pickaboo.com/product/computer-pc",
        "home-appliances": "https://www.pickaboo.com/product/home-appliances",
        "watches-horology": "https://www.pickaboo.com/product/smart-watch",
    },
    "dazzle.com.bd": {
        "mobile-gadgets": "https://dazzle.com.bd/categories/phones",
        "laptops-pc": "https://dazzle.com.bd/categories/laptop",
        "watches-horology": "https://dazzle.com.bd/categories/smart-watch",
    },
    "kryinternational.com": {
        "mobile-gadgets": "https://kryinternational.com/product-category/smartphones",
        "watches-horology": "https://kryinternational.com/product-category/smart-watch",
    },
    "motionview.com.bd": {
        "mobile-gadgets": "https://motionview.com.bd/category/smart-phone",
        "watches-horology": "https://motionview.com.bd/category/smart-watch",
        "cameras-photography": "https://motionview.com.bd/category/action-camera",
    },
    "custommacbd.com": {
        "laptops-pc": "https://custommacbd.com/collections/macbook",
        "mobile-gadgets": "https://custommacbd.com/collections/iphone",
    },
    "computermania.com.bd": {
        "laptops-pc": "https://computermania.com.bd/product-category/laptop",
    },
    "pchouse.com.bd": {
        "laptops-pc": "https://www.pchouse.com.bd/laptop",
    },
    "ultratech.com.bd": {
        "laptops-pc": "https://www.ultratech.com.bd/laptop",
    },
    "skyland.com.bd": {
        "laptops-pc": "https://www.skyland.com.bd/laptop-notebook",
    },
    "globalbrand.com.bd": {
        "laptops-pc": "https://www.globalbrand.com.bd/laptop",
    },
    "universal.com.bd": {
        "laptops-pc": "https://www.universal.com.bd/laptop",
    },
    "potakait.com": {
        "laptops-pc": "https://www.potakait.com/laptop-notebook",
    },
    "transcomdigital.com": {
        "home-appliances": "https://transcomdigital.com/home-appliances",
        "mobile-gadgets": "https://transcomdigital.com/smartphones",
    },
    "rangsemart.com.bd": {
        "home-appliances": "https://rangsemart.com.bd/product-category/home-appliances",
    },
    "ministerbd.com": {
        "home-appliances": "https://ministerbd.com/refrigerator.html",
    },
    "vision.com.bd": {
        "home-appliances": "https://vision.com.bd/category/home-appliance",
    },
    "waltonbd.com": {
        "home-appliances": "https://waltonbd.com/refrigerator-freezer",
        "cycles-evs": "https://waltonbd.com/e-bike",
        "mobile-gadgets": "https://waltonbd.com/smart-phone",
        "laptops-pc": "https://waltonbd.com/laptop",
    },
    "durantabikes.com": {
        "cycles-evs": "https://durantabikes.com/bicycles",
    },
    "dreamcycle.store": {
        "cycles-evs": "https://dreamcycle.store/product-category/bicycles",
    },
    "aarong.com": {
        "fashion-apparel": "https://www.aarong.com/men/panjabi",
        "saree-boutiques": "https://www.aarong.com/women/saree",
        "fine-jewelry": "https://www.aarong.com/jewellery",
    },
    "yellowclothing.net": {
        "fashion-apparel": "https://www.yellowclothing.net/collections/men",
        "saree-boutiques": "https://www.yellowclothing.net/collections/women",
    },
    "sailor.clothing": {
        "fashion-apparel": "https://sailor.clothing/men",
        "saree-boutiques": "https://sailor.clothing/women",
    },
    "fabrilife.com": {
        "fashion-apparel": "https://fabrilife.com/shop",
        "sportswear-gym": "https://fabrilife.com/shop?category=sports",
    },
    "twelvebd.com": {
        "fashion-apparel": "https://twelvebd.com/collections/mens",
    },
    "dorjibari.com.bd": {
        "fashion-apparel": "https://dorjibari.com.bd/collections/panjabi",
    },
    "batabd.com": {
        "sneakers-footwear": "https://www.batabd.com/collections/men",
    },
    "apex4u.com": {
        "sneakers-footwear": "https://apex4u.com/category/men",
    },
    "timezonebd.com": {
        "watches-horology": "https://timezonebd.com/watches",
    },
    "watchzonebd.com": {
        "watches-horology": "https://watchzonebd.com/shop",
    },
    "shajgoj.com": {
        "beauty-skincare": "https://shop.shajgoj.com/product-category/skin",
    },
    "banglashoppers.com": {
        "beauty-skincare": "https://www.banglashoppers.com/skin-care.html",
    },
    "khaasfood.com": {
        "grocery-snacks": "https://www.khaasfood.com/shop",
    },
    "shwapno.com": {
        "grocery-snacks": "https://www.shwapno.com",
    },
    "swap.com.bd": {
        "mobile-gadgets": "https://swap.com.bd/buy/phone",
        "laptops-pc": "https://swap.com.bd/buy/laptop",
        "cameras-photography": "https://swap.com.bd",
    },
    "cameraworldbd.com": {
        "cameras-photography": "https://cameraworldbd.com/product-category/dslr-camera",
    },
    "digitechbd.com": {
        "cameras-photography": "https://www.digitechbd.com/camera",
    },
}

# Category keywords used by the Live Navbar Auto-Discovery Spider when scanning a store's homepage
CATEGORY_NAV_KEYWORDS: Dict[str, List[str]] = {
    "mobile-gadgets": ["smartphone", "mobile-phone", "mobile", "phones", "phone", "iphone"],
    "laptops-pc": ["laptop-notebook", "all-laptop", "laptops", "laptop", "notebook", "macbook", "computer"],
    "cameras-photography": ["dslr", "mirrorless", "camera", "photography", "action-camera", "lens"],
    "cycles-evs": ["e-bike", "ebike", "electric-bike", "bicycle", "bicycles", "cycle", "scooter", "ev"],
    "home-appliances": ["refrigerator", "fridge", "air-conditioner", "ac", "television", "tv", "washing-machine", "appliance", "home-appliance"],
    "fashion-apparel": ["panjabi", "shirt", "t-shirt", "men", "mens", "apparel", "clothing", "fashion"],
    "saree-boutiques": ["saree", "jamdani", "katan", "women", "womens", "ethnic"],
    "fine-jewelry": ["gold", "diamond", "ring", "necklace", "jewellery", "jewelry"],
    "fashion-jewelry": ["earring", "jhumka", "necklace", "bangles", "jewellery", "jewelry"],
    "sneakers-footwear": ["sneaker", "sneakers", "shoe", "shoes", "footwear", "men"],
    "watches-horology": ["smart-watch", "smartwatch", "watches", "watch", "men-watches"],
    "beauty-skincare": ["skin-care", "skincare", "skin", "face", "cosmetics", "beauty"],
    "sportswear-gym": ["jersey", "sports", "activewear", "gym", "fitness"],
    "grocery-snacks": ["grocery", "organic", "honey", "ghee", "oil", "food", "shop"],
}

# In-memory cache of auto-discovered category URLs per (domain, category_id)
_DISCOVERED_CATEGORY_CACHE: Dict[Tuple[str, str], str] = {}


def _clean_domain(url_or_domain: str) -> str:
    d = (url_or_domain or "").strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    return d.split("/")[0].split("?")[0].strip()


def is_page_alive_and_has_products(
    resp: httpx.Response,
    is_search_or_product: bool = True,
    query: str = "",
) -> bool:
    """
    Strict Product-Presence Validator for Tier 1 (Product URL) & Tier 2 (Search URL):
      - Must return HTTP 200 OK (if a deep link returns 403/404/500, we heal to the Category Page!).
      - Must NOT contain any Soft-404 text.
      - Must contain actual BDT product prices AND at least 1 product card or JSON-LD Product matching the query!
    """
    if resp.status_code != 200 or not resp.text:
        return False

    text_low = resp.text[:50000].lower()
    for bad in SOFT_404_PATTERNS:
        if bad in text_low:
            return False

    if is_search_or_product:
        from adapters import parse_prices, parse_cards, SPECS
        prices = parse_prices(resp.text)
        if not prices:
            return False
        cards = parse_cards(resp.text, str(resp.url), SPECS["generic"], {"name": "check"}, limit=5)
        has_jsonld_prod = '"@type":"product"' in text_low.replace(" ", "")
        if not cards and not has_jsonld_prod:
            return False
        if query and cards:
            q_words = [w.lower() for w in re.findall(r"[a-zA-Z0-9]{2,}", query) if len(w) >= 2]
            if q_words:
                card_titles = " ".join(c.get("title", "").lower() for c in cards)
                if not any(w in card_titles for w in q_words[:2]):
                    return False

    return True


async def discover_category_url_from_homepage(
    client: httpx.AsyncClient, domain: str, category_id: str, query: str = ""
) -> Optional[str]:
    """
    Iteration 3B: Live Self-Healing Category Discovery!
    Fetches the store's homepage, scans all navigation <a href="..."> links, and finds the
    best matching category page for the product's category (e.g. /mobile-phone, /laptop, /camera).
    """
    cache_key = (domain, category_id)
    if cache_key in _DISCOVERED_CATEGORY_CACHE:
        return _DISCOVERED_CATEGORY_CACHE[cache_key]

    # 1. Check Curated Directory first
    if domain in STORE_CATEGORY_PAGES and category_id in STORE_CATEGORY_PAGES[domain]:
        curated = STORE_CATEGORY_PAGES[domain][category_id]
        _DISCOVERED_CATEGORY_CACHE[cache_key] = curated
        return curated

    # 2. Scrape Homepage Navbar Links Live
    base_url = f"https://{domain}"
    try:
        resp = await client.get(base_url)
        if resp.status_code != 200 or not resp.text:
            return base_url

        soup = BeautifulSoup(resp.text, "html.parser")
        nav_keywords = list(CATEGORY_NAV_KEYWORDS.get(category_id, []))
        q_words = [w.lower() for w in re.findall(r"[a-zA-Z]{3,}", query or "")]
        search_terms = q_words + nav_keywords

        best_url = None
        best_score = 0

        for a in soup.find_all("a", href=True):
            href = (a.get("href") or "").strip()
            if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            if domain not in (parsed.netloc or "").lower():
                continue
            path_low = (parsed.path or "").lower()
            if path_low in ("", "/") or any(x in path_low for x in ("login", "cart", "checkout", "account", "register", "wishlist", "policy", "contact", "about", "blog")):
                continue

            link_text = a.get_text(" ", strip=True).lower()
            score = 0
            for idx, kw in enumerate(search_terms):
                weight = 30 if idx < len(q_words) else 20
                if re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?:s|es)?(?![a-z0-9])", link_text):
                    score += weight + 10
                if kw in path_low:
                    score += weight
                if any(cat_prefix in path_low for cat_prefix in ("/category/", "/product-category/", "/collections/", "/shop/", "/product/")):
                    score += 8

            if score > best_score:
                best_score = score
                best_url = full_url

        if best_url and best_score >= 20:
            _DISCOVERED_CATEGORY_CACHE[cache_key] = best_url
            return best_url
    except Exception:
        pass

    return base_url


async def resolve_and_heal_offer_url(
    store_name: str,
    current_url: str,
    website_url: Optional[str],
    facebook_url: Optional[str],
    product_title: str,
    product_category: str,
    channel: str = "default",
) -> Tuple[str, str]:
    """
    Executes the 4-Stage Iterative URL Healing Cascade:
      Returns (healed_destination_url, resolution_stage)
    """
    from bd_stores_registry import (
        resolve_category_from_query,
        get_store_registry_meta,
        build_store_target_url,
        get_store_facebook_fallback_url,
    )
    from llm_reasoner import translate_bengali_and_banglish_for_store

    cat_id, cat_meta = resolve_category_from_query(product_title, product_category)
    vertical = cat_meta.get("vertical", "MOBILE_GADGET")
    en_title = translate_bengali_and_banglish_for_store(product_title)
    s_meta = get_store_registry_meta(store_name, en_title)

    official_fb = (
        facebook_url
        or s_meta.get("facebook_url")
        or get_store_facebook_fallback_url(store_name, en_title)
    )
    if "/search/" in (official_fb or "") or "/marketplace/" in (official_fb or ""):
        slug = re.sub(r"[^a-zA-Z0-9]+", "", re.sub(r"\(.*?\)", "", store_name))
        if len(slug) >= 3:
            official_fb = f"https://www.facebook.com/{slug}"

    # If user explicitly clicked the Facebook button or store is F-Commerce only
    if channel == "facebook" or (not website_url and "facebook.com" in (current_url or "").lower()):
        return official_fb, "facebook_official"

    primary_web = website_url if (website_url and "facebook.com" not in website_url) else (
        current_url if (current_url and "facebook.com" not in current_url) else s_meta.get("website_url", "")
    )
    domain = _clean_domain(primary_web)
    if not domain or "facebook.com" in domain:
        return official_fb, "facebook_fallback"

    headers = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(2.5), follow_redirects=True, headers=headers, verify=False) as client:
        # ------------------------------------------------------------------
        # ITERATION 1: Check Exact Product / Current URL
        # ------------------------------------------------------------------
        if primary_web and primary_web.startswith("http"):
            # If primary_web is already a known curated category page, check it directly
            try:
                resp1 = await client.get(primary_web)
                is_root = urlparse(primary_web).path.strip("/") == ""
                if not is_root and is_page_alive_and_has_products(resp1, is_search_or_product=True, query=en_title):
                    return str(resp1.url), "tier1_exact_url"
            except Exception:
                pass

        # ------------------------------------------------------------------
        # ITERATION 2: Try Store's Verified Search URL for Core Model Words
        # ------------------------------------------------------------------
        core_words = " ".join(en_title.split()[:3])
        search_candidate = build_store_target_url(store_name, core_words, vertical)
        if (
            search_candidate
            and "facebook.com" not in search_candidate
            and search_candidate != primary_web
            and urlparse(search_candidate).path.strip("/") != ""
        ):
            try:
                resp2 = await client.get(search_candidate)
                if is_page_alive_and_has_products(resp2, is_search_or_product=True, query=core_words):
                    return str(resp2.url), "tier2_store_search"
            except Exception:
                pass

        # ------------------------------------------------------------------
        # ITERATION 3: Resolve Store's Respective Category Page!
        # (Curated Category Directory + Live Homepage Navbar Auto-Discovery)
        # ------------------------------------------------------------------
        cat_page_url = await discover_category_url_from_homepage(client, domain, cat_id, core_words)
        if cat_page_url and cat_page_url.startswith("http"):
            try:
                resp3 = await client.get(cat_page_url)
                if resp3.status_code < 400 or resp3.status_code in (401, 403, 429):
                    return cat_page_url, "tier3_category_page"
            except Exception:
                pass

        # ------------------------------------------------------------------
        # ITERATION 4: Store Root Homepage -> Official Facebook Page
        # ------------------------------------------------------------------
        root_url = f"https://{domain}"
        try:
            resp4 = await client.get(root_url)
            if resp4.status_code < 400 or resp4.status_code in (401, 403, 429):
                return root_url, "tier4_store_homepage"
        except Exception:
            pass

    return official_fb, "fb_fallback"
