"""
JaChai Curated Bangladeshi Retail & F-Commerce Stores Registry (backend/bd_stores_registry.py)
Dynamic Self-Updating Registry Engine

Features:
1. Category-Separated CSV Ingestion: Dynamically reads all category CSVs from `registries/*.csv`.
2. Dynamic Column Support: Automatically detects and binds any new or custom columns added manually
   to any CSV file (e.g. 'Rating', 'Phone', 'Location', 'Notes', 'Delivery_BDT').
3. Auto-Reload on File Change: Monitors file modification timestamps (mtime); whenever a CSV file
   is modified or saved manually, the in-memory registry updates automatically without requiring a server restart.
4. Guaranteed Failover & Direct SKU Matching: Supports Dual-Engine architecture (Engine A vs Engine B)
   and website-to-Facebook 2.5s smart failover.
"""

import os
import glob
import csv
import re
import time
import threading
import statistics
import unicodedata
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus


# ==============================================================================
# BANNED INTERNATIONAL ENTITIES & CURRENCIES (STRICT GEO-FENCING)
# ==============================================================================
BANNED_FOREIGN_CURRENCIES = ["USD", "INR", "EUR", "GBP", "CAD", "$", "₹", "€", "£"]

BANNED_INTERNATIONAL_DOMAINS = [
    "amazon.", "walmart.", "bestbuy.", "ebay.", "aliexpress.", "alibaba.",
    "target.", "newegg.", "flipkart.", "myntra.", "reliancedigital.", "croma.",
    ".in/", ".in?", ".co.in", ".pk/", ".in", ".us/", ".ca/", ".uk/"
]

BANNED_OPEN_MARKETPLACES_IN_TECH = (
    'daraz', 'daraz bd', 'daraz bangladesh', 'bikroy', 'ajkerdeal',
    'othoba', 'bdstall', 'priyoshop', 'clickbd', 'sindabad'
)

# Known direct merchant search URL templates (Live verified endpoints)
MERCHANT_SEARCH_TEMPLATES: Dict[str, str] = {
    'aarong.com': 'https://www.aarong.com/search?q={q}',
    'apex4u.com': 'https://apex4u.com/?s={q}',
    'applegadgetsbd.com': 'https://www.applegadgetsbd.com/?s={q}',
    'batabd.com': 'https://batabd.com/search?q={q}',
    'chaldal.com': 'https://chaldal.com/search/{q}',
    'computermania.com.bd': 'https://computermania.com.bd/search?q={q}',
    'custommacbd.com': 'https://custommacbd.com/search?q={q}',
    'daraz.com.bd': 'https://www.daraz.com.bd/catalog/?q={q}',
    'dazzle.com.bd': 'https://dazzle.com.bd/?s={q}&post_type=product',
    'diamondworldltd.com': 'https://www.diamondworldltd.com/?s={q}',
    'durantabikes.com': 'https://durantabikes.com/?s={q}',
    'fabrilife.com': 'https://fabrilife.com/search?q={q}',
    'gadgetandgear.com': 'https://gadgetandgear.com/search?q={q}',
    'goribergadget.com': 'https://goribergadget.com/search?q={q}',
    'istockbd.com': 'https://istockbd.com/search?q={q}',
    'khaasfood.com': 'https://khaasfood.com/search?q={q}',
    'kryinternational.com': 'https://kryinternational.com/?s={q}&post_type=product',
    'pcbstorebd.com': 'https://pcbstorebd.com/search?q={q}',
    'pickaboo.com': 'https://www.pickaboo.com/search-result/{q}',
    'ryans.com': 'https://www.ryans.com/search?q={q}',
    'sailor.clothing': 'https://sailor.clothing/search?q={q}',
    'shajgoj.com': 'https://shajgoj.com/?s={q}',
    'shwapno.com': 'https://shwapno.com/search?q={q}',
    'startech.com.bd': 'https://www.startech.com.bd/product/search?search={q}',
    'sumashtech.com': 'https://sumashtech.com/search?q={q}',
    'techlandbd.com': 'https://www.techlandbd.com/index.php?route=product/search&search={q}',
    'timezonebd.com': 'https://timezonebd.com/search?q={q}',
    'waltonbd.com': 'https://waltonbd.com/index.php?route=product/search&search={q}',
    'yellowclothing.net': 'https://yellowclothing.net/search?q={q}',
}

# Known merchant aliases to exact domain templates or direct URLs
MERCHANT_ALIASES: Dict[str, str] = {
    'star tech': 'startech.com.bd',
    'startech': 'startech.com.bd',
    'ryans': 'ryans.com',
    'ryans computers': 'ryans.com',
    'gadget & gear': 'gadgetandgear.com',
    'gadget and gear': 'gadgetandgear.com',
    'gadgetgear': 'gadgetandgear.com',
    'sumash': 'sumashtech.com',
    'sumash tech': 'sumashtech.com',
    'apple gadgets': 'applegadgetsbd.com',
    'apple gadgets bd': 'applegadgetsbd.com',
    'dazzle': 'dazzle.com.bd',
    'dazzle bd': 'dazzle.com.bd',
    'dazzle mobile': 'dazzle.com.bd',
    'kry': 'kryinternational.com',
    'kry international': 'kryinternational.com',
    'custom mac': 'custommacbd.com',
    'custom mac bd': 'custommacbd.com',
    'istock': 'istockbd.com',
    'istock bd': 'istockbd.com',
    'goriber gadget': 'goribergadget.com',
    'pickaboo': 'pickaboo.com',
    'techland': 'techlandbd.com',
    'tech land': 'techlandbd.com',
    'computer mania': 'computermania.com.bd',
    'computer mania bd': 'computermania.com.bd',
    'walton': 'waltonbd.com',
    'walton plaza': 'waltonbd.com',
    'duranta': 'durantabikes.com',
    'duranta bikes': 'durantabikes.com',
    'duranta bicycle': 'durantabikes.com',
    'duranta gallery': 'durantabikes.com',
    'aarong': 'aarong.com',
    'fabrilife': 'fabrilife.com',
    'chaldal': 'chaldal.com',
    'shwapno': 'shwapno.com',
    'khaas food': 'khaasfood.com',
    'khaasfood': 'khaasfood.com',
    'apex': 'apex4u.com',
    'apex footwear': 'apex4u.com',
    'bata': 'batabd.com',
    'bata bangladesh': 'batabd.com',
    'shajgoj': 'shajgoj.com',
    'diamond world': 'diamondworldltd.com',
    'timezone': 'timezonebd.com',
    'time zone': 'timezonebd.com',
    'yellow': 'yellowclothing.net',
    'sailor': 'sailor.clothing',
    'sailor bd': 'sailor.clothing',
    'daraz': 'daraz.com.bd',
    'daraz mall': 'daraz.com.bd',
}

# Category name to vertical key mapping
CATEGORY_VERTICAL_MAP: Dict[str, str] = {
    'snacks, dry foods & grocery marketplaces': 'GROCERY_SNACKS',
    'grocery': 'GROCERY_SNACKS',
    'mobile phones & consumer gadgets': 'MOBILE_GADGET',
    'mobiles': 'MOBILE_GADGET',
    'laptops, desktops & computer components': 'LAPTOP_PC',
    'laptops': 'LAPTOP_PC',
    'mainstream fashion & apparel brands': 'FASHION_APPAREL',
    'fashion': 'FASHION_APPAREL',
    'fine jewelry & premium fashion jewelry stores': 'JEWELRY',
    'budget, casual & imitation jewelry targets': 'JEWELRY',
    'jewelry': 'JEWELRY',
    'small & medium saree & boutique pages': 'SAREE_BOUTIQUE',
    'saree': 'SAREE_BOUTIQUE',
    'sneakers & footwear stores': 'SNEAKERS_FOOTWEAR',
    'sneakers': 'SNEAKERS_FOOTWEAR',
    'footwear': 'SNEAKERS_FOOTWEAR',
    'watches & horology retailers': 'WATCHES_HOROLOGY',
    'watches': 'WATCHES_HOROLOGY',
    'home appliances & white goods': 'APPLIANCES_WHITE_GOODS',
    'appliances': 'APPLIANCES_WHITE_GOODS',
    'beauty, skincare & lifestyle stores': 'BEAUTY_SKINCARE',
    'beauty skincare & lifestyle stores': 'BEAUTY_SKINCARE',
    'beauty': 'BEAUTY_SKINCARE',
    'cycles & electric vehicles (evs)': 'CYCLES_EV',
    'cycles': 'CYCLES_EV',
    'sportswear, activewear & gym gear': 'SPORTSWEAR_GYM',
    'activewear & gym gear': 'SPORTSWEAR_GYM',
    'sportswear': 'SPORTSWEAR_GYM',
    'multi-category marketplaces': 'MULTI_MARKETPLACE',
}


# ==============================================================================
# RESOLVE DIRECTORY PATHS
# ==============================================================================
BASE_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(BASE_BACKEND_DIR)

POSSIBLE_REGISTRY_DIRS = [
    os.path.join(PROJECT_ROOT_DIR, "registries"),
    os.path.join(BASE_BACKEND_DIR, "registries"),
    os.path.join(BASE_BACKEND_DIR, "data", "registries"),
    r"e:\JaChai\registries",
]

POSSIBLE_MASTER_CSVS = [
    os.path.join(PROJECT_ROOT_DIR, "JaChai_Final_Curated_Registry_v3.csv"),
    os.path.join(BASE_BACKEND_DIR, "JaChai_Final_Curated_Registry_v3.csv"),
    r"e:\JaChai\JaChai_Final_Curated_Registry_v3.csv",
]


def _get_registries_dir() -> Optional[str]:
    for p in POSSIBLE_REGISTRY_DIRS:
        if os.path.isdir(p):
            return p
    return None


def _get_master_csv_fallback() -> Optional[str]:
    for p in POSSIBLE_MASTER_CSVS:
        if os.path.isfile(p):
            return p
    return None


# ==============================================================================
# IN-MEMORY DYNAMIC REGISTRY STATE
# (Objects are mutated in-place so all external imports stay up to date)
# ==============================================================================
ALL_STORES_REGISTRY: List[Dict[str, Any]] = []
RETAIL_VERTICALS: Dict[str, List[Dict[str, Any]]] = {}
FCOMMERCE_JEWELRY_BOUTIQUES: List[Dict[str, Any]] = []
FCOMMERCE_SAREE_BOUTIQUES: List[Dict[str, Any]] = []
STORE_FACEBOOK_PAGES: Dict[str, str] = {}
DETECTED_COLUMNS: List[str] = []
REGISTRY_METADATA: Dict[str, Any] = {
    "total_stores": 0,
    "categories_count": 0,
    "csv_files": [],
    "detected_columns": [],
    "last_reloaded_at": None,
    "loaded_from": None,
}

_LAST_MTIMES: Dict[str, float] = {}
_LAST_CHECK_TIMESTAMP: float = 0.0
_LAST_MTIME_CHECK_TS: float = 0.0
_REGISTRY_RELOAD_LOCK = threading.RLock()


# ==============================================================================
# DYNAMIC ROW & STORE NORMALIZER
# ==============================================================================
def _clean_domain(domain_or_url: str) -> str:
    if not domain_or_url:
        return ""
    d = domain_or_url.strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    d = d.split("/")[0].split("?")[0].strip()
    return d


_FB_HANDLE_RE = re.compile(r"^[A-Za-z0-9._\-]{3,}$")


def _format_facebook_url(fb_name_or_url: str, store_name: str) -> str:
    """
    Accepts a full URL, an '@handle', or 'Display Name (@handle)'. A bare display name is NOT a page
    address, so it becomes a Facebook search link instead of an invented page URL.
    """
    raw = (fb_name_or_url or "").strip()
    if not raw:
        clean_name = quote_plus(store_name.strip())
        return f"https://www.facebook.com/marketplace/dhaka/search/?query={clean_name}"
    if raw.lower().startswith(("http://", "https://")):
        return raw
    m = re.search(r"\(@([A-Za-z0-9._\-]+)\)\s*$", raw)
    if m:
        return f"https://www.facebook.com/{m.group(1)}"
    if raw.startswith("@") and _FB_HANDLE_RE.match(raw[1:]):
        return f"https://www.facebook.com/{raw[1:]}"
    return f"https://www.facebook.com/search/top/?q={quote_plus(raw)}"


def _normalize_store_row(row: Dict[str, str], detected_cols: Set[str]) -> Dict[str, Any]:
    """
    Transforms any CSV row into a standardized Store dictionary while
    dynamically retaining ALL original and custom columns added manually.
    """
    store: Dict[str, Any] = {}

    # 1. Dynamically copy all columns present in the row
    for k, v in row.items():
        if k:
            k_clean = k.strip()
            v_clean = (v or "").strip()
            detected_cols.add(k_clean)
            store[k_clean] = v_clean
            # Also store normalized lowercase slug for ease of access (e.g. 'phone_number')
            slug_key = re.sub(r"[^a-zA-Z0-9]+", "_", k_clean).strip("_").lower()
            if slug_key and slug_key != k_clean:
                store[slug_key] = v_clean

    # 2. Extract standard fields with flexible header matching
    name = (
        store.get("Name") or store.get("name") or
        store.get("Store Name") or store.get("store_name") or ""
    )
    category = (
        store.get("Category") or store.get("category") or
        store.get("Retail Category") or "Uncategorized"
    )
    website_raw = (
        store.get("Website") or store.get("website") or
        store.get("Website URL") or store.get("website_url") or
        store.get("Domain") or store.get("domain") or ""
    )
    fb_raw = (
        store.get("Facebook page") or store.get("facebook_page") or
        store.get("Facebook") or store.get("facebook") or
        store.get("facebook_page_url") or store.get("fb_page") or ""
    )
    arch_mode_raw = (
        store.get("Architecture_Mode") or store.get("architecture_mode") or
        store.get("Mode") or store.get("engine") or "Engine A (Direct SKU Match)"
    )

    domain = _clean_domain(website_raw)
    engine_val = "Engine B" if "engine b" in arch_mode_raw.lower() else "Engine A"
    arch_mode = "Engine B (Starts From Benchmark)" if engine_val == "Engine B" else "Engine A (Direct SKU Match)"

    # Determine Website Search Template
    if domain in MERCHANT_SEARCH_TEMPLATES:
        website_url = MERCHANT_SEARCH_TEMPLATES[domain]
    elif domain:
        website_url = f"https://{domain}/search?q={{q}}"
    else:
        website_url = ""

    # Determine Facebook Fallback URL
    facebook_page_url = _format_facebook_url(fb_raw, name)
    source_type = "crawler" if domain else "f_commerce"

    # Search URL template
    search_url_template = website_url if website_url else facebook_page_url

    # Assign standardized keys
    store.update({
        "name": name,
        "category": category,
        "domain": domain,
        "website_url": website_url,
        "facebook_page_url": facebook_page_url,
        "architecture_mode": arch_mode,
        "engine": engine_val,
        "search_url_template": search_url_template,
        "source_type": source_type,
        "fb_page": fb_raw or name,
        "fb_verified": "/search/" not in facebook_page_url and "/marketplace/" not in facebook_page_url,
    })

    return store


# ==============================================================================
# DYNAMIC REGISTRY LOADER
# ==============================================================================
def load_all_registries(force: bool = False, guard: bool = False) -> Dict[str, Any]:
    """
    Scans the registries folder or master CSV, extracts all stores,
    preserves all dynamic columns, and populates module-level registry variables.
    """
    global _LAST_MTIMES, _LAST_CHECK_TIMESTAMP, _LAST_MTIME_CHECK_TS

    reg_dir = _get_registries_dir()
    master_csv = _get_master_csv_fallback()

    loaded_stores: List[Dict[str, Any]] = []
    detected_cols: Set[str] = set()
    current_mtimes: Dict[str, float] = {}
    csv_paths: List[str] = []
    read_errors: List[str] = []

    # Priority 1: Read all category CSV files in registries/
    if reg_dir and os.path.isdir(reg_dir):
        found_files = sorted(glob.glob(os.path.join(reg_dir, "*.csv")))
        if found_files:
            csv_paths = found_files

    # Priority 2: Fallback to master CSV
    if not csv_paths and master_csv and os.path.isfile(master_csv):
        csv_paths = [master_csv]

    if not csv_paths:
        return REGISTRY_METADATA

    # Ingest rows from discovered CSV files
    for path in csv_paths:
        try:
            norm_p = os.path.normcase(os.path.abspath(path))
            mtime = os.path.getmtime(path)
            current_mtimes[norm_p] = mtime
            with open(path, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not any(row.values()):
                        continue
                    store = _normalize_store_row(row, detected_cols)
                    if store.get("name"):
                        loaded_stores.append(store)
        except Exception as e:
            read_errors.append(path)
            print(f"[JaChai Dynamic Registry] Warning: Error reading '{path}': {e}")

    # Build grouped collections
    verticals: Dict[str, List[Dict[str, Any]]] = {}
    jewelry_boutiques: List[Dict[str, Any]] = []
    saree_boutiques: List[Dict[str, Any]] = []
    fb_pages: Dict[str, str] = {}

    for store in loaded_stores:
        name = store["name"]
        cat_lower = store["category"].lower().strip()
        v_key = (CATEGORY_VERTICAL_MAP.get(cat_lower)
                 or re.sub(r"[^A-Z0-9]+", "_", store["category"].upper()).strip("_")
                 or "UNCATEGORIZED")

        # Vertical grouping
        verticals.setdefault(v_key, []).append(store)

        # Boutique grouping
        if "jewelry" in cat_lower and ("budget" in cat_lower or "imitation" in cat_lower or store["source_type"] == "f_commerce"):
            jewelry_boutiques.append(store)
        elif "saree" in cat_lower or "boutique" in cat_lower:
            saree_boutiques.append(store)

        # Facebook lookup map
        fb_url = store["facebook_page_url"]
        if fb_url:
            fb_pages[name.lower()] = fb_url
            if store.get("domain"):
                fb_pages[store["domain"].lower()] = fb_url

    # Atomic thread-safe update of module exports
    with _REGISTRY_RELOAD_LOCK:
        # Hot-reload guard: a half-saved or broken CSV must not wipe the live registry.
        old_n = len(ALL_STORES_REGISTRY)
        if guard and old_n and (read_errors or len(loaded_stores) < 0.5 * old_n):
            print(f"[JaChai Dynamic Registry] Reload rejected: {len(loaded_stores)} stores parsed vs {old_n} live "
                  f"(read errors: {read_errors or 'none'}). Keeping the previous registry until the files change again.")
            _LAST_MTIMES = current_mtimes
            _LAST_CHECK_TIMESTAMP = _LAST_MTIME_CHECK_TS = time.time()
            return REGISTRY_METADATA

        ALL_STORES_REGISTRY[:] = loaded_stores

        # Update in place, then drop stale keys. Never clear() first: readers would see an empty dict.
        RETAIL_VERTICALS.update(verticals)
        for k in [k for k in RETAIL_VERTICALS if k not in verticals]:
            RETAIL_VERTICALS.pop(k, None)

        FCOMMERCE_JEWELRY_BOUTIQUES[:] = jewelry_boutiques
        FCOMMERCE_SAREE_BOUTIQUES[:] = saree_boutiques

        STORE_FACEBOOK_PAGES.update(fb_pages)
        for k in [k for k in STORE_FACEBOOK_PAGES if k not in fb_pages]:
            STORE_FACEBOOK_PAGES.pop(k, None)

        DETECTED_COLUMNS[:] = sorted(list(detected_cols))

        _LAST_MTIMES = current_mtimes
        _LAST_CHECK_TIMESTAMP = time.time()
        _LAST_MTIME_CHECK_TS = _LAST_CHECK_TIMESTAMP

        # Update metadata
        REGISTRY_METADATA.update({
            "total_stores": len(ALL_STORES_REGISTRY),
            "categories_count": len([k for k, v in RETAIL_VERTICALS.items() if v]),
            "csv_files": [os.path.basename(p) for p in csv_paths],
            "csv_full_paths": csv_paths,
            "detected_columns": list(DETECTED_COLUMNS),
            "last_reloaded_at": datetime.now().isoformat(),
            "loaded_from": reg_dir if (reg_dir and csv_paths != [master_csv]) else master_csv,
        })

    return REGISTRY_METADATA


def check_and_reload_if_modified(min_interval_seconds: float = 0.3, force: bool = False) -> bool:
    """
    Lightweight, thread-safe check comparing file mtimes.
    Throttled to run at most once every min_interval_seconds (default 0.3s).
    Automatically triggers atomic in-memory reload if any CSV file has been modified manually.
    """
    global _LAST_CHECK_TIMESTAMP, _LAST_MTIME_CHECK_TS

    now = time.time()
    if not force and (now - _LAST_MTIME_CHECK_TS < min_interval_seconds):
        return False

    with _REGISTRY_RELOAD_LOCK:
        # Re-check inside lock
        if not force and (now - _LAST_MTIME_CHECK_TS < min_interval_seconds):
            return False
        _LAST_MTIME_CHECK_TS = now
        _LAST_CHECK_TIMESTAMP = now

        reg_dir = _get_registries_dir()
        csv_paths = []
        if reg_dir and os.path.isdir(reg_dir):
            csv_paths = sorted(glob.glob(os.path.join(reg_dir, "*.csv")))
        if not csv_paths:
            master_csv = _get_master_csv_fallback()
            if master_csv and os.path.isfile(master_csv):
                csv_paths = [master_csv]

        if not csv_paths:
            return False

        needs_reload = False
        if len(csv_paths) != len(_LAST_MTIMES):
            needs_reload = True
        else:
            for p in csv_paths:
                try:
                    norm_p = os.path.normcase(os.path.abspath(p))
                    mtime = os.path.getmtime(p)
                    if norm_p not in _LAST_MTIMES or mtime > _LAST_MTIMES[norm_p]:
                        needs_reload = True
                        break
                except Exception:
                    continue

        if needs_reload or force:
            load_all_registries(force=True, guard=True)
            return True

    return False


# ==============================================================================
# ACCESSOR FUNCTIONS & SMART RESOLVERS
# ==============================================================================
def get_all_stores_registry() -> List[Dict[str, Any]]:
    """Returns all stores, reloading automatically if files were updated."""
    check_and_reload_if_modified()
    return ALL_STORES_REGISTRY


def get_stores_for_vertical(vertical: str) -> List[Dict[str, Any]]:
    """Returns curated stores for a vertical name or synonym with auto-freshness."""
    check_and_reload_if_modified()

    v_norm = (vertical or "").strip().upper()
    if v_norm in RETAIL_VERTICALS:
        return RETAIL_VERTICALS[v_norm]

    synonyms = {
        "MOBILES": "MOBILE_GADGET",
        "MOBILE": "MOBILE_GADGET",
        "SMARTPHONE": "MOBILE_GADGET",
        "LAPTOPS": "LAPTOP_PC",
        "LAPTOP": "LAPTOP_PC",
        "COMPUTERS": "LAPTOP_PC",
        "PC": "LAPTOP_PC",
        "FASHION": "FASHION_APPAREL",
        "APPAREL": "FASHION_APPAREL",
        "CLOTHING": "FASHION_APPAREL",
        "SAREE": "SAREE_BOUTIQUE",
        "SAREES": "SAREE_BOUTIQUE",
        "JEWELLERY": "JEWELRY",
        "SNEAKERS": "SNEAKERS_FOOTWEAR",
        "SHOES": "SNEAKERS_FOOTWEAR",
        "WATCHES": "WATCHES_HOROLOGY",
        "WATCH": "WATCHES_HOROLOGY",
        "GROCERY": "GROCERY_SNACKS",
        "SNACKS": "GROCERY_SNACKS",
        "BEAUTY": "BEAUTY_SKINCARE",
        "COSMETICS": "BEAUTY_SKINCARE",
        "APPLIANCES": "APPLIANCES_WHITE_GOODS",
        "CYCLES": "CYCLES_EV",
        "EV": "CYCLES_EV",
        "SPORTSWEAR": "SPORTSWEAR_GYM",
        "GYM": "SPORTSWEAR_GYM",
    }
    mapped = synonyms.get(v_norm, "MOBILE_GADGET")
    return RETAIL_VERTICALS.get(mapped, RETAIL_VERTICALS.get("MOBILE_GADGET", []))


def sanitize_search_query_for_store(query: str) -> str:
    """
    Sanitizes raw product titles and noisy queries into clean, concise search keywords (max 3-4 words)
    suitable for Bangladeshi eCommerce internal search bars without symbols or parentheses that cause 404s.
    """
    if not query:
        return ""
    # Strip parenthetical annotations: (Authentic BD...), (Official...), (100% Pure...), etc.
    q = re.sub(r"\(.*?\)", "", query)
    q = re.sub(r"\[.*?\]", "", q)
    # Strip symbols, quotes, commas, hashes, dots, slashes, backslashes, percent signs
    q = re.sub(r'["\'#·|:;,~`*+?<>!%^&{}\\\/]', " ", q)
    # Remove synthesized boilerplate tags
    boilerplate = [
        "authentic bd commuter edition", "authentic bd", "verified authentic", 
        "best market price index", "best market price", "with freedos", "freedos",
        "official warranty", "intact box", "global edition", "bangladesh edition",
        "official bangladesh edition", "handcrafted", "festive saree", "casual edition",
        "price in bangladesh", "bd price", "online in bd", "official outlet"
    ]
    for b in boilerplate:
        q = re.sub(r"(?i)\b" + re.escape(b) + r"\b", "", q)
    
    # Normalize whitespace
    words = [w for w in q.split() if w.strip()]
    if not words:
        return query.strip()[:30]
    
    # Return at most 3 to 4 concise keywords
    return " ".join(words[:4]).strip()


def _name_key(name: str) -> str:
    """Comparable form of a store name: drops '(@handle)', punctuation, case and spacing."""
    n = re.sub(r"\(@[^)]*\)", " ", name or "")
    n = canon_text(n.lower())
    n = re.sub(r"[^\w\s\u0980-\u09FF]", " ", n)
    return " ".join(n.split())


_MIN_ALIAS_LEN = 7  # shorter aliases ('yellow', 'walton', 'dazzle') are only accepted as an exact match


def _find_store(store_name: str) -> Optional[Dict[str, Any]]:
    """
    Resolve a store by identity, never by loose substring. Order: exact registry name, exact domain,
    exact alias, then whole-word containment (longest wins). Returns None rather than guessing.
    """
    key = _name_key(store_name)
    if not key:
        return None
    stores = list(ALL_STORES_REGISTRY)
    for s in stores:
        if _name_key(s.get("name", "")) == key:
            return s
    raw = (store_name or "").strip()
    if "." in raw and " " not in raw:
        dom = _clean_domain(raw)
        for s in stores:
            if s.get("domain") and s["domain"] == dom:
                return s

    def by_domain(domain: str, prefer: str) -> Optional[Dict[str, Any]]:
        cands = [s for s in stores if s.get("domain") == domain]
        for s in cands:
            if _name_key(s.get("name", "")).startswith(prefer):
                return s
        return cands[0] if cands else None

    alias_dom = MERCHANT_ALIASES.get(key)
    if alias_dom:
        hit = by_domain(alias_dom, key)
        if hit:
            return hit
    padded = f" {key} "
    best, best_len = None, 0
    for s in stores:
        nk = _name_key(s.get("name", ""))
        if len(nk) >= 5 and f" {nk} " in padded and len(nk) > best_len:
            best, best_len = s, len(nk)
    for alias, dom in MERCHANT_ALIASES.items():
        if (len(alias) >= _MIN_ALIAS_LEN or " " in alias) and f" {alias} " in padded and len(alias) > best_len:
            hit = by_domain(dom, alias)
            if hit:
                best, best_len = hit, len(alias)
    return best


def get_store_facebook_fallback_url(store_name: str, query: str = "") -> str:
    """
    Returns the registry's Facebook URL for a store when it is a real page address; otherwise a
    Facebook search link. Never returns &merchant= parameter which breaks Facebook Marketplace.
    """
    check_and_reload_if_modified()
    s_norm = (store_name or "").strip().lower()
    if s_norm in STORE_FACEBOOK_PAGES:
        return STORE_FACEBOOK_PAGES[s_norm]
    store = _find_store(store_name)
    if store and store.get("facebook_page_url"):
        return store["facebook_page_url"]
    return f"https://www.facebook.com/search/top/?q={quote_plus((store_name or '').strip())}"


def build_store_target_url(store_name: str, query: str, vertical: Optional[str] = None) -> str:
    """
    Merchant-specific search URL for a store. Resolves the store by identity (see _find_store) and
    falls back to a Facebook search link, never to another merchant's site.
    """
    check_and_reload_if_modified()

    clean_term = sanitize_search_query_for_store(query)
    clean_q = quote_plus(clean_term) if clean_term else quote_plus((query or "").strip())

    store = _find_store(store_name)
    if store:
        dom = store.get("domain", "")
        if dom in MERCHANT_SEARCH_TEMPLATES:
            return MERCHANT_SEARCH_TEMPLATES[dom].format(q=clean_q)
        if store.get("website_url"):
            return store["website_url"].format(q=clean_q)
        if store.get("facebook_page_url"):
            return store["facebook_page_url"]

    alias_dom = MERCHANT_ALIASES.get(_name_key(store_name))  # e.g. 'daraz' is templated but not in the CSVs
    if alias_dom in MERCHANT_SEARCH_TEMPLATES:
        return MERCHANT_SEARCH_TEMPLATES[alias_dom].format(q=clean_q)
    return get_store_facebook_fallback_url(store_name, query)


def get_registry_status() -> Dict[str, Any]:
    """Returns dynamic registry metadata and file statistics for admin dashboard."""
    check_and_reload_if_modified()
    return dict(REGISTRY_METADATA)


def get_store_registry_meta(store_name: str, query: str = "") -> Dict[str, Any]:
    """
    Looks up a store in the curated Bangladeshi registry and returns its verified
    website URL, Facebook page URL, location, and pre-seeded status.
    """
    check_and_reload_if_modified()
    clean_term = sanitize_search_query_for_store(query)
    clean_q = quote_plus(clean_term) if clean_term else (quote_plus(query.strip()) if query else "")

    store = _find_store(store_name)
    if store:
        s_dom = store.get("domain", "")
        raw_website = store.get("Website") or store.get("website") or store.get("website_url") or ""
        website = ""
        if s_dom in MERCHANT_SEARCH_TEMPLATES:
            website = MERCHANT_SEARCH_TEMPLATES[s_dom].format(q=clean_q) if clean_q else f"https://{s_dom}"
        elif raw_website:
            if clean_q and store.get("website_url"):
                website = store["website_url"].format(q=clean_q)
            elif raw_website.startswith("http"):
                website = raw_website
            else:
                website = f"https://{store.get('domain', raw_website)}"

        fb_url = (store.get("facebook_page_url")
                  or STORE_FACEBOOK_PAGES.get(store.get("name", "").lower(), "")
                  or f"https://www.facebook.com/search/top/?q={quote_plus(store.get('name', store_name))}")
        return {
            "name": store.get("name", store_name),
            "website_url": website,
            "facebook_url": fb_url,
            "fb_verified": bool(store.get("fb_verified")),
            "location": store.get("Location") or store.get("location") or "Bangladesh",
            "category": store.get("category", ""),
            "is_preseeded": True,
            "architecture_mode": store.get("architecture_mode", "Engine A (Direct SKU Match)")
        }

    # Store not in pre-seeded registry (Open Market Discovery)
    fb_top = f"https://www.facebook.com/search/top/?q={quote_plus((store_name or '').strip())}"
    return {
        "name": store_name,
        "website_url": "",
        "facebook_url": fb_top,
        "fb_verified": False,
        "location": "Bangladesh",
        "category": "",
        "is_preseeded": False,
        "architecture_mode": "Open Market Discovery"
    }


def compute_trust_score(
    store_name: str,
    is_preseeded: bool = True,
    source_type: str = "crawler",
    comments: Optional[List[str]] = None,
    cod_terms: str = "",
    price_anomaly_pct: float = 0.0,
    price: Optional[float] = None,
    all_prices: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    JaChai TrustShield-BD Algorithm:
    Evaluates store legitimacy, comment sentiment (Bengali/Banglish/English),
    payment terms, and price anomaly to protect shoppers from F-Commerce scams.
    Uses statistics.median for price baseline and penalizes offers < 0.55 * median.
    """
    # 1. Base Score from Registry Verification
    score = 96 if is_preseeded else 76

    # 2. Payment Terms Risk
    cod_lower = (cod_terms or "").lower()
    if any(k in cod_lower for k in ["cash on delivery", "ক্যাশ অন ডেলিভারি", "trial on delivery", "ডেলিভারিতে ট্রায়াল"]):
        score += 3
    elif any(k in cod_lower for k in ["100% advance", "full advance", "সম্পূর্ণ অগ্রিম", "advance required"]):
        score -= 28

    # 3. Price Anomaly (Unrealistic bait pricing penalty using median baseline)
    if all_prices and len(all_prices) >= 2 and price is not None and price > 0:
        med = statistics.median(all_prices)
        if med > 0:
            if price < 0.55 * med:
                score -= 32
                price_anomaly_pct = max(price_anomaly_pct, 1.0 - (price / med))
            elif price < 0.70 * med:
                score -= 15
                price_anomaly_pct = max(price_anomaly_pct, 1.0 - (price / med))

    if price_anomaly_pct > 0.45:
        score -= int((price_anomaly_pct - 0.45) * 50)

    # 4. Two-Tier Bengali / Banglish Comment Lexicon Classifier
    fraud_flags = []
    if comments and len(comments) > 0:
        hard_triggers = [
            "বাটপার", "প্রতারক", "ভুয়া", "চিটার", "টাকা নিয়ে ব্লক", "scam", "fraud",
            "fake", "cheat", "chiter", "advance niye block", "batpar", "protarok"
        ]
        soft_triggers = [
            "নকল", "ছবি মিল নাই", "ডেলিভারি পাইনি", "দেরি", "রিটার্ন নিচ্ছে না",
            "not original", "bad quality", "baje product", "chobi ek rokom"
        ]
        trust_anchors = [
            "অরিজিনাল", "প্রোডাক্ট পেয়েছি", "original product", "trusted page",
            "ভালো সার্ভিস", "fast delivery", "valostuff", "authentic"
        ]

        hard_hits = 0
        soft_hits = 0
        trust_hits = 0

        for comment in comments:
            c_low = comment.lower()
            for ht in hard_triggers:
                if ht in c_low:
                    hard_hits += 1
                    fraud_flags.append(f"Hard scam keyword '{ht}' detected in feedback")
            for st in soft_triggers:
                if st in c_low:
                    soft_hits += 1
            for ta in trust_anchors:
                if ta in c_low:
                    trust_hits += 1

        sentiment_penalty = (hard_hits * 18) + (soft_hits * 6) - (trust_hits * 4)
        score -= sentiment_penalty

    # Clamp score to [10, 99]
    score = max(10, min(99, score))

    if score >= 88:
        risk_level = "low"
        trust_badge = "✓ 98% Verified Safe" if is_preseeded else "✓ Market Verified"
    elif score >= 60:
        risk_level = "moderate"
        trust_badge = "Standard Merchant · COD Recommended"
    else:
        risk_level = "high"
        trust_badge = "⚠️ Caution: High Advance Risk"

    return {
        "trust_score": score,
        "trust_badge": trust_badge,
        "risk_level": risk_level,
        "fraud_flags": fraud_flags[:3]
    }


# ==============================================================================
# 5. STRICT 13-CATEGORY REGISTRY MAP & SMART QUERY ROUTER
# ==============================================================================
CATEGORY_REGISTRY_MAP: Dict[str, Dict[str, Any]] = {
    "cycles-evs": {
        "csv": "cycles_and_evs.csv",
        "csv_aliases": [
            "cycles_and_evs.csv", "cycles_and_evs", "cycles-and-evs", "cycles-evs",
            "cycles & electric vehicles (evs)", "cycles & evs"
        ],
        "csv_category": "Cycles & Electric Vehicles (EVs)",
        "display_en": "Cycles & EVs",
        "display_bn": "সাইকেল ও ই-বাইক",
        "vertical": "CYCLES_EV",
        "keywords": [
            "bicycle", "bicycles", "gear cycle", "mountain bike", "mtb", "road bike", "hybrid cycle",
            "gravel bike", "fat bike", "folding bike", "bmx", "commuter cycle", "kids cycle",
            "electric bike", "e-bike", "ebike", "ebikes", "e bikes", "battery bike", "electric bicycle",
            "electric cycle", "electric scooter", "e-scooter", "escooter", "scooty", "ev scooter",
            "battery scooty", "electric moped", "electric vehicle", "ev", "evs", "electronic vehicle",
            "electronic bike", "cycle helmet", "cycle lock", "cycle light", "ev charger", "cycle pump",
            "hub motor", "pedal assist", "lithium battery cycle",
            "cycle", "saikel", "cycal", "betari saikel", "gari", "gaddi", "skuti", "motorsaikele",
            "সাইকেল", "গিয়ার সাইকেল", "মাউন্টেইন বাইক", "রোড বাইক", "হাইব্রিড সাইকেল", "সাধারণ সাইকেল",
            "ছেলেদের সাইকেল", "মেয়েদের সাইকেল", "বাচ্চাদের সাইকেল", "দুরন্ত সাইকেল", "ফনিক্স সাইকেল",
            "ভেলেসি সাইকেল", "সাইকেলের দাম", "ই-বাইক", "ইলেকট্রিক বাইক", "ব্যাটারি বাইক", "ইলেকট্রিক সাইকেল",
            "চার্জের বাইক", "পরিবেশ বান্ধব বাইক", "ওয়ালটন ই-বাইক", "গ্রিন টাইগার বাইক", "ইলেকট্রিক স্কুটার",
            "স্কুটি", "ব্যাটারি স্কুটি", "ইলেকট্রিক স্কুটি", "মেয়েদের স্কুটি", "সাইকেল হেলমেট",
            "সাইকেল লক", "সাইকেল লাইট", "ইভি চার্জার", "সাইকেল পাম্প",
            "takyon", "walton takyon", "walton e-bikes", "lion cycle", "duranta", "duranta sports",
            "duranta bikes", "veloce", "veloce bicycles", "reevo", "runner automobiles", "runner ev",
            "yadea", "tailg", "hero electric", "green tiger", "phoenix cycle", "core cycle", "foxter",
            "ghost cycle", "trek", "giant", "upland", "trinx", "dream cycle store", "cyclelife exclusive"
        ],
        "default_query": "Electric Bike",
        "base_price": 48000,
        "price_min": 25000,
        "price_max": 180000,
        "model_templates": [
            "{title} (Authentic BD Commuter Edition)",
            "{title} Alloy Frame Edition",
            "{title} Eco Commuter Edition"
        ]
    },
    "home-appliances": {
        "csv": "appliances_and_electronics.csv",
        "csv_aliases": [
            "appliances_and_electronics.csv", "appliances_and_electronics", "appliances-and-electronics",
            "appliances-electronics", "home-appliances", "appliances"
        ],
        "csv_category": "Home Appliances & White Goods",
        "display_en": "Home Appliances",
        "display_bn": "হোম অ্যাপ্লায়েন্স",
        "vertical": "HOME_APPLIANCES",
        "keywords": [
            "inverter ac", "air conditioner 1.5 ton", "1 ton ac", "smart ac", "energy saving ac",
            "refrigerator", "double door fridge", "single door fridge", "smart fridge", "direct cool fridge",
            "deep fridge", "freezer", "smart tv", "android tv 32 inch", "43 inch smart tv", "led tv 55 inch",
            "4k ultra hd tv", "microwave oven", "electric oven", "convection oven", "grill oven",
            "automatic washing machine", "front load washer", "top load washing machine", "electric blender",
            "juicer grinder", "air fryer", "electric kettle", "rice cooker", "induction cooker", "gas stove",
            "geyser", "water heater", "water purifier", "vacuum cleaner", "ceiling fan", "voltage stabilizer",
            "ips", "fan", "ac", "tv", "fridge", "oven",
            "eshi", "aicy", "frij", "frize", "tivi", "tevi", "oben", "woven", "chula", "pani filter", "blendar",
            "এসি", "এয়ার কন্ডিশনার", "ইনভার্টার এসি", "১.৫ টন এসি", "১ টন এসি", "ফ্রিজ", "রেফ্রিজারেটর",
            "ডাবল ডোর ফ্রিজ", "ডিপ ফ্রিজ", "স্মার্ট টিভি", "টিভি", "এলইডি টিভি", "অ্যান্ড্রয়েড টিভি",
            "৪কে টিভি", "৩২ ইঞ্চি টিভি", "৪৩ ইঞ্চি টিভি", "ওভেন", "মাইক্রোওয়েভ ওভেন", "ইলেকট্রিক ওভেন",
            "ওয়াশিং মেশিন", "অটোমেটিক ওয়াশিং মেশিন", "কাপড় ধোয়ার মেশিন", "ব্লেন্ডার", "জুসার", "রাইস কুকার",
            "পানির ফিল্টার", "ফ্যান", "গিজার", "গ্যাসের চুলা",
            "Singer BD", "Walton BD", "Transcom Digital", "Rangs eMart", "Butterfly BD", "Best Electronics",
            "Electro Mart", "Vision", "Minister", "Gree", "Haier", "Panasonic", "LG", "Sony Bravia",
            "Whirlpool", "Hitachi", "Sharp", "Midea", "Philips", "Miyako", "Jaipan"
        ],
        "default_query": "Refrigerator",
        "base_price": 36000,
        "price_min": 18000,
        "price_max": 150000,
        "model_templates": [
            "{title} (Energy Saving Inverter Series)",
            "{title} Direct Cool Frost Free",
            "{title} Smart Digital Inverter"
        ]
    },
    "fashion-apparel": {
        "csv": "fashion_and_apparel.csv",
        "csv_aliases": [
            "fashion_and_apparel.csv", "fashion_and_apparel", "fashion-and-apparel", "fashion-apparel",
            "fashion", "apparel"
        ],
        "csv_category": "Mainstream Fashion & Apparel Brands",
        "display_en": "Fashion & Apparel",
        "display_bn": "ফ্যাশন ও পোশাক",
        "vertical": "FASHION_APPAREL",
        "keywords": [
            "panjabi", "mens panjabi", "cotton panjabi", "silk panjabi", "eid panjabi", "embroidered panjabi",
            "t-shirt", "mens polo t shirt", "oversized t-shirt", "drop shoulder t shirt", "cotton tee",
            "salwar kameez", "three piece", "ladies suit", "party three piece", "cotton three piece",
            "mens formal shirt", "office shirt", "casual shirt", "oxford shirt", "linen shirt",
            "denim jeans", "mens jeans pant", "gabardine pants", "cargo pants", "formal trousers", "chinos",
            "joggers", "cotton socks", "winter socks", "blazer", "suit", "jacket", "hoodie", "sweatshirt",
            "sweater", "lungi", "gamcha", "fotua", "borkha", "burqa", "abaya", "hijab", "polo", "shirt",
            "punjabi", "panzabi", "panjbi", "tshart", "genji", "thri pis", "3 piece", "3-piece", "payer moja",
            "kamiz", "jama",
            "পাঞ্জাবি", "কাটলি পাঞ্জাবি", "কটন পাঞ্জাবি", "সিল্ক পাঞ্জাবি", "বিয়ে পাঞ্জাবি", "সাদা পাঞ্জাবি",
            "কালো পাঞ্জাবি", "মেনস পাঞ্জাবি", "ঈদ কালেকশন পাঞ্জাবি", "টিশার্ট", "গেঞ্জি", "পোলো শার্ট",
            "গোল গলার গেঞ্জি", "হাফ হাতা গেঞ্জি", "ফুল হাতা টিশার্ট", "থ্রি পিস", "সালোয়ার কামিজ",
            "মহিলাদের থ্রি পিস", "সুতি থ্রি পিস", "ঈদ থ্রি পিস", "ফরমাল শার্ট", "অফিস শার্ট",
            "ক্যাজুয়াল শার্ট", "চেক শার্ট", "জিন্স প্যান্ট", "গ্যাবারডিন প্যান্ট", "কারগো প্যান্ট",
            "ফরমাল ট্রাউজার", "ছেলেদের প্যান্ট", "মোজা", "ব্লেজার", "হুডি", "লুঙ্গি",
            "Yellow", "Sailor", "Richman", "Lubnan", "Cats Eye", "Ecstasy", "Gentle Park", "Artisan",
            "Dorjibari", "Infinity Mega Mall", "Freeland", "Fabrilife", "Klotho", "Illiyeen", "Blucheez",
            "Raw Nation"
        ],
        "default_query": "Panjabi",
        "base_price": 2400,
        "price_min": 850,
        "price_max": 18000,
        "model_templates": [
            "{title} (100% Pure Organic Cotton)",
            "{title} Premium Tailored Fit",
            "{title} Classic Heritage Fit"
        ]
    },
    "saree-boutiques": {
        "csv": "saree_boutiques_fcommerce.csv",
        "csv_aliases": [
            "saree_boutiques_fcommerce.csv", "saree_boutiques_fcommerce", "saree-boutiques-fcommerce",
            "saree-boutiques", "saree", "boutiques"
        ],
        "csv_category": "Small & Medium Saree & Boutique Pages",
        "display_en": "Saree & Boutiques",
        "display_bn": "শাড়ি ও বুটিকস",
        "vertical": "SAREE_BOUTIQUE",
        "keywords": [
            "jamdani saree", "dhakai jamdani", "half silk jamdani", "muslin jamdani", "bridal jamdani",
            "katan saree", "benaroshi saree", "rajshahi silk katan", "tissue katan", "bridals benaroshi",
            "silk saree", "raw silk saree", "party wear saree", "georgette saree", "chiffon saree",
            "daily wear saree", "cotton saree", "handloom saree", "taant saree", "monipuri saree",
            "tangail saree", "khadi saree", "organza saree", "sequin saree", "lawn three piece",
            "pakistani lawn suit", "chiffon suit", "velvet three piece", "festive suit", "saree", "sari", "শাড়ি",
            "jamdhani shari", "katan shari", "benarosi", "shari", "sharee", "tater shari", "pakistani thri pis",
            "জামদানি শাড়ি", "ঢাকাই জামদানি", "হাফ সিল্ক জামদানি", "মসলিন জামদানি", "বিয়ে জামদানি",
            "লাল জামদানি", "আসল জামদানি", "হাতে বোনা জামদানি", "কাতান শাড়ি", "বেনারসি শাড়ি",
            "রাজশাহী সিল্ক কাতান", "টিস্যু কাতান", "বিয়ে বেনারসি", "ব্রাইডাল কাতান", "সিল্ক শাড়ি",
            "পার্টি শাড়ি", "জর্জেট শাড়ি", "শিফন শাড়ি", "ডিজাইনার শাড়ি", "সুতি শাড়ি", "তাঁতের শাড়ি",
            "মণিপুরী শাড়ি", "টাঙ্গাইল শাড়ি", "লন থ্রি পিস", "পাকিস্তানি থ্রি পিস", "ভেলভেট থ্রি পিস",
            "Aarong Saree", "Tangail Sharee Kutir", "Pirang", "Nodi", "Kumudini", "Taant", "Doshobhuja",
            "Maya", "Sutra", "Anjan's", "Kay Kraft", "Rong Bangladesh", "Sadakalo", "Bibiana", "Deshi Dosh"
        ],
        "default_query": "Jamdani Saree",
        "base_price": 5500,
        "price_min": 2500,
        "price_max": 45000,
        "model_templates": [
            "{title} (Authentic Handloom Weave)",
            "{title} Pure Silk Festive Edition",
            "{title} Traditional Tangail Handloom"
        ]
    },
    "fine-jewelry": {
        "csv": "fine_jewelry_and_gold.csv",
        "csv_aliases": [
            "fine_jewelry_and_gold.csv", "fine_jewelry_and_gold",
            "fine-jewelry-and-gold", "fine-jewellery", "fine-jewelry", "gold", "diamond"
        ],
        "csv_category": "Fine Jewelry & Premium Fashion Jewelry Stores",
        "display_en": "Fine Jewelry & Gold",
        "display_bn": "স্বর্ণ ও ডায়মন্ড গহনা",
        "vertical": "FINE_JEWELRY",
        "keywords": [
            "22k gold ring", "gold band", "engagement ring", "diamond ring", "mens gold ring",
            "diamond necklace", "bridal jewelry set", "gold necklace", "bridal gold set", "sitahar",
            "gold bala", "gold earrings", "gold chain", "gold pendant", "24k gold", "22k gold", "21k gold",
            "18k gold", "solid gold", "real gold", "certified diamond", "diamond solitare", "diamond nose pin",
            "gold coin", "gold bar", "gold bhori", "platinum", "white gold", "rose gold", "hallmarked gold",
            "kdm gold", "gold", "diamond",
            "shonar angti", "sona", "shona", "shorno", "heera", "hira", "bhori", "vuri", "swarna",
            "সোনার আংটি", "গোল্ড ব্যান্ড", "এনগেজমেন্ট রিং", "ডায়মন্ড আংটি", "২২ ক্যারেট সোনা", "২১ ক্যারেট আংটি",
            "খাঁটি সোনা", "সোনার গহনা", "সোনার নেকলেস", "ব্রাইডাল গোল্ড সেট", "সীতাহার", "সোনার বালা",
            "সোনার কানের দুল", "বিয়ের সোনার গহনা", "ভারী সোনার সেট", "সোনার চুড়ি", "ভরি", "হীরা",
            "ডায়মন্ড নেকলেস", "সোনার চেইন",
            "Diamond World", "Apan Jewellers", "Amin Jewellers", "Al-Amin Jewellers", "Venus Jewellers",
            "Jarwa House", "D'damas BD", "Pearl Oasis", "Royal Malabar", "Senco Gold BD"
        ],
        "default_query": "Gold Jewellery",
        "base_price": 45000,
        "price_min": 15000,
        "price_max": 450000,
        "model_templates": [
            "{title} (Hallmarked 22K Cadmium Certified)",
            "{title} Traditional Bridal Collection",
            "{title} Certified Artisan Crafted"
        ]
    },
    "fashion-jewelry": {
        "csv": "budget_jewelry_fcommerce.csv",
        "csv_aliases": [
            "budget_jewellery_fcommerce.csv", "budget_jewelry_fcommerce.csv",
            "budget_jewellery_fcommerce", "budget_jewelry_fcommerce",
            "budget-jewellery-fcommerce", "budget-jewelry-fcommerce",
            "budget-jewelry", "budget-jewellery", "budget_jewelry", "budget_jewellery",
            "fashion-jewellery", "fashion-jewelry"
        ],
        "csv_category": "Budget, Casual & Imitation Jewelry Targets",
        "display_en": "Fashion & Budget Jewellery",
        "display_bn": "ফ্যাশন ও বাজেট জুয়েলারি",
        "vertical": "FASHION_JEWELRY",
        "keywords": [
            "oxidized earrings", "jhumka", "imitation earrings", "party jhumka", "long earrings",
            "imitation necklace set", "party choker", "choker", "choker necklace", "long necklace", "rani haar",
            "artificial jewelry set", "budget jewelry", "fashion jewelry", "costume jewelry",
            "silver plated jewelry", "gold plated jewelry", "clay jewelry", "terracotta jewelry",
            "fabric jewelry", "thread jewelry", "beaded jewelry", "bangles", "churi", "reshmi churi",
            "clay churi", "bala", "bracelet", "anklet", "payel", "paiel", "nupur", "nose pin", "nath",
            "nolok", "finger ring", "angti", "tikli", "matha patti", "maang tikka", "waist chain", "bichha",
            "saree pin", "hair accessories",
            "kaner dul", "jhumko", "chudi", "dul", "har",
            "ঝুমকা", "ঝুমকো", "কানের দুল", "অক্সিডাইজড দুল", "ফ্যাশন দুল", "পার্টি ঝুমকা", "লম্বা দুল",
            "পাথরের দুল", "নেকলেস সেট", "চোকার", "রানি হার", "লং নেকলেস", "কৃত্রিম গহনা", "গলার হার",
            "স্টাইলিশ চোকার", "নূপুর", "পায়েল", "চুড়ি", "টিকলি", "নোলক", "আংটি", "বালা", "ইমিটেশন গহনা",
            "কসমেটিকস নেকলেস",
            "Shukti", "Clay Station", "Bohurupi", "Oikko", "Kantik", "Shingari", "Nokshi", "Rangon",
            "Ornamentry", "Gohona Kutir", "Shajbati", "Bohubrihi", "Dokaan Jewelry"
        ],
        "default_query": "Fashion Jewellery",
        "base_price": 950,
        "price_min": 250,
        "price_max": 4500,
        "model_templates": [
            "{title} (Handcrafted Oxidized Collection)",
            "{title} Artisan Bohemian Set",
            "{title} Ethnic Kundan Floral Set"
        ]
    },
    "sneakers-footwear": {
        "csv": "sneakers_and_footwear.csv",
        "csv_aliases": [
            "sneakers_and_footwear.csv", "sneakers_and_footwear", "sneakers-and-footwear",
            "sneakers-footwear", "sneakers", "footwear", "shoes"
        ],
        "csv_category": "Sneakers & Footwear Stores",
        "display_en": "Sneakers & Shoes",
        "display_bn": "স্নিকার্স ও জুতা",
        "vertical": "SNEAKERS_FOOTWEAR",
        "keywords": [
            "sneakers", "running shoes", "sports shoes", "gym shoes", "casual sneakers", "white sneakers",
            "mens formal shoes", "leather shoes", "oxford shoes", "derby shoes", "office shoes",
            "mens sandals", "slippers", "slides", "flip flops", "loafers", "slip on shoes",
            "womens sandals", "heel shoes", "party heels", "ballerina flats", "wedges", "boots",
            "chelsea boots", "converse", "chappal", "shoe", "shoes", "sandal",
            "snikars", "keds", "lader shoe", "sendal", "choti", "juta", "juto",
            "স্নিকার্স", "কেডস", "জুতা", "রানিং জুতা", "স্পোর্টস জুতা", "ফরমাল জুতা", "চামড়ার জুতা",
            "অফিস জুতা", "স্যান্ডেল", "চটি", "লোফার জুতা", "স্লিপার", "ঘরের চটি", "মহিলাদের জুতা",
            "হাই হিল", "ফ্ল্যাট জুতা", "পার্টি হিল", "মেয়েদের স্যান্ডেল", "ওয়েজেস",
            "Apex", "Bata", "Lotto BD", "Bay Emporium", "Step Footwear", "Zeil's", "Orion Footwear",
            "Vibram", "Nike", "Adidas", "Puma", "New Balance", "Under Armour", "Vans", "Reebok", "Skechers"
        ],
        "default_query": "Sneakers",
        "base_price": 3800,
        "price_min": 1500,
        "price_max": 18000,
        "model_templates": [
            "{title} (Genuine Leather Streetwear Edition)",
            "{title} Comfort Foam Low-Top"
        ]
    },
    "watches-horology": {
        "csv": "watches_and_horology.csv",
        "csv_aliases": [
            "watches_and_horology.csv", "watches_and_horology", "watches-and-horology",
            "watches-horology", "watches", "horology"
        ],
        "csv_category": "Watches & Horology Retailers",
        "display_en": "Watches & Horology",
        "display_bn": "ঘড়ি ও টাইমপিস",
        "vertical": "WATCHES_HOROLOGY",
        "keywords": [
            "casio watch", "casio vintage", "casio g-shock", "g-shock", "g shock", "gshock",
            "digital watch", "mens metal watch", "luxury watch", "automatic watch", "mechanical watch",
            "analog watch", "leather strap watch", "chronograph", "diver watch", "dress watch",
            "smartwatch", "bluetooth calling smartwatch", "amoled smartwatch", "fitness tracker",
            "watch strap", "leather watch belt", "metal watch band", "silicon watch strap", "watch",
            "watches", "timepiece",
            "casio ghori", "ghori", "ghari", "hater ghori", "wacth", "ghorir belt", "smart ghori",
            "ক্যাসিও ঘড়ি", "ঘড়ি", "হাতঘড়ি", "ডিজিটাল ঘড়ি", "মেটাল ঘড়ি", "ক্যাসিও ভিন্টেজ", "জি শক ঘড়ি",
            "লাক্সারি ঘড়ি", "অটোমেটিক ঘড়ি", "মেকানিক্যাল ঘড়ি", "অ্যানালগ ঘড়ি", "লেদার বেল্ট ঘড়ি",
            "স্মার্টওয়াচ", "কলিং স্মার্টওয়াচ", "ঘড়ির বেল্ট", "লেদার বেল্ট", "মেটাল বেল্ট", "সিলিকন স্ট্র্যাপ",
            "Casio", "Edifice", "Naviforce", "Curren", "Skmei", "Tissot", "Seiko", "Citizen", "Fossil",
            "Orient", "Rolex", "Omega", "Tag Heuer", "Titan", "Fastrack", "Timex", "Time Zone BD",
            "Watch Gallery"
        ],
        "default_query": "Watch",
        "base_price": 4500,
        "price_min": 1200,
        "price_max": 85000,
        "model_templates": [
            "{title} (Sapphire Glass Automatic)",
            "{title} Official Warranty Chronograph"
        ]
    },
    "beauty-skincare": {
        "csv": "beauty_and_skincare.csv",
        "csv_aliases": [
            "beauty_and_skincare.csv", "beauty_and_skincare", "beauty-and-skincare",
            "beauty-skincare", "beauty", "skincare", "cosmetics"
        ],
        "csv_category": "Beauty, Skincare & Lifestyle Stores",
        "display_en": "Beauty & Skincare",
        "display_bn": "বিউটি ও স্কিনকেয়ার",
        "vertical": "BEAUTY_SKINCARE",
        "keywords": [
            "sunscreen", "spf 50 sunblock", "mineral sunscreen", "gel sunscreen", "whitening sunscreen",
            "face wash", "cleanser", "acne face wash", "salicylic acid cleanser", "gentle cleanser",
            "moisturizer", "face cream", "hydrating lotion", "gel moisturizer", "night cream",
            "matte lipstick", "liquid lip color", "lip gloss", "lip tint", "lip balm",
            "niacinamide serum", "face serum", "vitamin c serum", "hyaluronic acid", "retinol",
            "hair oil", "onion hair oil", "anti hair fall oil", "shampoo", "conditioner", "body wash",
            "perfume", "attar", "foundation", "bb cream", "concealer", "compact powder", "kajal",
            "mascara", "skincare", "serum", "toner", "cosmetics",
            "sunscream", "sunscren", "facewash", "feswash", "mozerizer", "moshcharaijar", "lipistik",
            "lipstic", "shaban", "chuler tel",
            "সানস্ক্রিন", "সানব্লক", "এসপিএফ ৫০", "জেল সানস্ক্রিন", "ফেসওয়াশ", "ক্লিনজার",
            "ব্রণ দূর করার ফেসওয়াশ", "ময়েশ্চারাইজার", "ফেস ক্রিম", "লোশন", "নাইট ক্রিম", "লিপস্টিক",
            "লিপ গ্লস", "লিপ বাম", "ম্যাট লিপস্টিক", "লিকুইড লিপস্টিক", "সিরাম", "চুলের তেল",
            "পেঁয়াজ তেল", "সাবান", "শ্যাম্পু", "পারফিউম", "আতর", "কাজল", "মেকআপ",
            "Shajgoj", "Banglashoppers", "Beauty Booth", "The Mall BD", "Skin Cafe", "Cosmetics BD",
            "L'Oreal", "Garnier", "Nivea", "Pond's", "Dove", "Simple", "COSRX", "The Ordinary",
            "Some By Mi", "Neutrogena", "CeraVe", "Cetaphil", "Lakme", "Maybelline", "Al Haramain", "Ajmal"
        ],
        "default_query": "Skincare",
        "base_price": 1400,
        "price_min": 450,
        "price_max": 8500,
        "model_templates": [
            "{title} (Dermatologist Tested 100% Authentic)",
            "{title} Hydrating Repair Formula"
        ]
    },
    "sportswear-gym": {
        "csv": "sportswear_and_gym.csv",
        "csv_aliases": [
            "sportswear_and_gym.csv", "sportswear_and_gym", "sportswear-and-gym",
            "sportswear-gym", "sportswear", "gym"
        ],
        "csv_category": "Sportswear, Activewear & Gym Gear",
        "display_en": "Sportswear & Gym",
        "display_bn": "স্পোর্টস ও জিম গিয়ার",
        "vertical": "SPORTSWEAR_GYM",
        "keywords": [
            "football jersey", "argentina jersey 2026", "brazil jersey", "cricket jersey", "bangladesh jersey",
            "gym tracksuit", "running shorts", "compression shirt", "joggers pants", "workout hoodie",
            "activewear", "yoga mat", "resistance bands", "dumbbells set", "push up board", "skipping rope",
            "gym gloves", "weightlifting belt", "pull up bar", "treadmill", "cricket bat", "football",
            "badminton racket", "shuttlecock", "gym bag", "sports duffel bag", "shaker bottle", "water bottle gym",
            "sportswear", "gym wear", "gym", "jersey",
            "jarsi", "jerci", "traksoot", "trackshute", "khellar jarsi", "bayam",
            "জার্সি", "আর্জেন্টিনা জার্সি", "ব্রাজিল জার্সি", "ক্রিকেট জার্সি", "বাংলাদেশ জার্সি", "ফুটবল জার্সি",
            "ট্র্যাকসুট", "রানিং শর্টস", "কম্প্রেশন শার্ট", "জগার্স প্যান্ট", "জিমের কাপড়", "যোগা ম্যাট",
            "রেজিস্ট্যান্স ব্যান্ড", "ডাম্বেল সেট", "পুশ আপ বোর্ড", "স্কিপিং দড়ি", "ব্যায়ামের ম্যাট",
            "ফিটনেস সরঞ্জাম", "ক্রিকেট ব্যাট", "ফুটবল", "ব্যাডমিন্টন র‌্যাকেট", "জিম ব্যাগ", "শেইকার বোতল",
            "Decathlon BD", "Sports World", "BD Cricket Store", "Bodyline", "Vector Sports", "Yonex",
            "Li-Ning", "Mikasa", "Molten", "Nivia", "Cosco", "Kookaburra", "Gray Nicolls"
        ],
        "default_query": "Sportswear",
        "base_price": 1800,
        "price_min": 650,
        "price_max": 14000,
        "model_templates": [
            "{title} (Moisture-Wicking Dri-Fit Series)",
            "{title} Pro Athletic Training Edition"
        ]
    },
    "grocery-snacks": {
        "csv": "grocery_and_snacks.csv",
        "csv_aliases": [
            "grocery_and_snacks.csv", "grocery_and_snacks", "grocery-and-snacks",
            "grocery-snacks", "grocery", "snacks"
        ],
        "csv_category": "Snacks, Dry Foods & Grocery Marketplaces",
        "display_en": "Grocery & Snacks",
        "display_bn": "গ্রোসারি ও স্ন্যাকস",
        "vertical": "GROCERY_SNACKS",
        "keywords": [
            "mustard oil", "pure mustard oil", "pure cow ghee", "gawya ghee", "sundarban honey",
            "natural honey", "organic honey", "date palm jaggery", "chinigura rice", "aromatic rice",
            "masoor dal", "mung dal", "organic oats", "soybean oil", "sunflower oil", "olive oil",
            "pumpkin seeds", "sunflower seeds", "chia seeds", "mixed nuts", "almonds cashews", "dates",
            "dry fruits", "raisins", "turmeric powder", "spices", "tea", "coffee", "biscuits", "noodles",
            "chanachur", "pickles", "grocery", "snack", "ghee", "honey",
            "shorishar tel", "sorisar tel", "khati ghi", "modhu", "khati modhu", "chal", "daal", "tel",
            "holud", "jira", "khejur", "cha", "kopi", "achar",
            "সরিষার তেল", "ঘি", "খাঁটি ঘি", "গাওয়া ঘি", "ঘানি ভাঙা তেল", "মধু", "সুন্দরবনের মধু",
            "প্রাকৃতিক মধু", "খাঁটি মধু", "খেজুরের গুড়", "পোলাও চাল", "চিনিগুড়া চাল", "মসুর ডাল",
            "মুগ ডাল", "ওটস", "কুমড়ার বীজ", "সূর্যমুখীর বীজ", "চিয়া সিডস", "বাদাম", "কাজুবাদাম ও পেস্তা",
            "ড্রাই ফ্রুটস", "চাল", "ডাল", "তেল", "মসলা", "হলুদ", "মরিচ", "চা", "কফি", "নুডলস", "চানাচুর",
            "আচার",
            "Chaldal", "Shwapno", "Meena Bazar", "Agora", "Khaas Food", "Bongo Bajar Organic", "Prakritik",
            "Teer", "Rupchanda", "Radhuni", "Pran", "Fresh", "Aarong Dairy", "Milk Vita",
            "Kazi & Kazi Tea", "Ispahani"
        ],
        "default_query": "Organic Food",
        "base_price": 750,
        "price_min": 200,
        "price_max": 5000,
        "model_templates": [
            "{title} (100% Pure Organic & Natural)",
            "{title} Premium Export Quality"
        ]
    },
    "laptops-pc": {
        "csv": "laptops_and_computers.csv",
        "csv_aliases": [
            "laptops_and_computers.csv", "laptops_and_computers", "laptops-and-computers",
            "laptops-pc", "laptops", "pc", "computers"
        ],
        "csv_category": "Laptops, Desktops & Computer Components",
        "display_en": "Laptops & PC",
        "display_bn": "ল্যাপটপ ও কম্পিউটার",
        "vertical": "LAPTOP_PC",
        "keywords": [
            "laptop", "notebook", "ultrabook", "student laptop", "office laptop", "slim laptop",
            "touch screen laptop", "chromebook", "macbook air", "macbook pro", "apple macbook m2",
            "m3 macbook pro", "macbook air m1", "mac mini", "imac", "gaming laptop", "rtx 4060 laptop",
            "rtx 4070 laptop", "asus rog strix", "acer nitro 5", "msi cyborg", "lenovo loq", "hp victus",
            "desktop pc", "gaming pc", "core i5 desktop", "core i7 pc", "ryzen 5 pc", "office pc",
            "brand pc", "intel core i5 13th gen", "intel core i7", "amd ryzen 5 5600g", "ryzen 7 7700x",
            "lga 1700 motherboard", "am5 motherboard", "graphics card", "rtx 3070", "rtx 4060 gpu",
            "gtx 1650", "rx 6600", "gpu", "nvme ssd", "sata ssd", "m.2 ssd", "1tb hdd", "desktop ram 16gb",
            "ddr5 ram", "storage", "ips monitor", "gaming monitor 144hz", "monitor", "laptop cooling pad",
            "laptop stand", "mechanical keyboard", "gaming mouse", "processor", "motherboard", "ram", "ssd", "pc",
            "leptop", "labtop", "laptap", "macbok", "destop", "pici", "grafix card", "essdi", "hardisk",
            "moniter", "minitor", "leptop cooler",
            "ল্যাপটপ", "নোটবুক", "ম্যাকবুক", "অ্যাপল ল্যাপটপ", "গেমিং ল্যাপটপ", "হাই এন্ড ল্যাপটপ",
            "গ্রাফিক্স ল্যাপটপ", "নিট্রো ফাইভ", "আসুস আরওজি", "লেনোভো লোড", "ভিক্টাস ল্যাপটপ", "কম্পিউটার",
            "ডেস্কটপ পিসি", "গেমিং পিসি", "রাইজেন পিসি", "কোর আই ফাইভ", "অফিস কম্পিউটার", "প্রসেসর",
            "মাদারবোর্ড", "ইন্টেল কোর", "রাইজেন প্রসেসর", "গ্রাফিক্স কার্ড", "জিপিইউ", "জিটিএক্স ১৬৫০",
            "আরটিএক্স ৪০৬০", "এসএসডি", "হার্ডডিস্ক", "র্যাম", "মনিটর", "ল্যাপটপ স্ট্যান্ড",
            "Star Tech", "Ryans Computers", "TechLand BD", "Creatus Computer", "PC House", "PotakaIT",
            "Nexus Computer", "UCC", "Skyland", "Asus", "HP", "Dell", "Lenovo", "MSI", "Acer",
            "Apple MacBook", "Gigabyte", "Corsair", "Logitech", "Razer"
        ],
        "default_query": "Laptop",
        "base_price": 65000,
        "price_min": 35000,
        "price_max": 280000,
        "model_templates": [
            "{title} (Official BD Warranty Edition)",
            "{title} High Performance Series"
        ]
    },
    "mobile-gadgets": {
        "csv": "mobile_phones_and_gadgets.csv",
        "csv_aliases": [
            "mobile_phones_and_gadgets.csv", "mobile_phones_and_gadgets", "mobile-phones-and-gadgets",
            "mobile-gadgets", "mobiles-gadgets", "mobiles", "gadgets"
        ],
        "csv_category": "Mobile Phones & Consumer Gadgets",
        "display_en": "Mobiles & Gadgets",
        "display_bn": "মোবাইল ও গ্যাজেট",
        "vertical": "MOBILE_GADGET",
        "keywords": [
            "mobile phone", "smartphone", "cell phone", "touch phone", "android mobile", "ios phone",
            "5g smartphone", "4g mobile", "budget phone", "flagship smartphone", "gaming phone",
            "camera phone", "iphone 15", "iphone 15 pro", "iphone 15 pro max", "iphone 14", "iphone 14 pro",
            "iphone 13", "iphone 16", "iphone 16 pro max", "iphone 12", "iphone 11", "iphone se",
            "samsung galaxy s24", "s24 ultra", "samsung a55", "samsung a35", "samsung s23",
            "galaxy z fold", "galaxy z flip", "samsung a15", "redmi note 13", "xiaomi 14", "poco x6 pro",
            "oneplus 12", "oneplus nord", "realme gt", "realme c67", "vivo v30", "oppo reno 11",
            "infinix hot 40", "tecno spark", "wireless earbuds", "tws earbuds", "airpods", "bluetooth headset",
            "power bank", "powerbank", "portable charger", "fast charger", "smartwatch", "smart watch",
            "fitness band", "iphone 15 back cover", "silicon case", "tempered glass", "screen protector",
            "type c cable", "fast charger cord", "phone", "mobile", "gadget", "charger",
            "mobail", "smatphon", "phone", "fon", "smart phon", "iphon 15", "appel iphone", "aifon",
            "ifone", "samsang s24", "sumsung mobile", "xiomi phone", "one plus", "earbads", "aripods",
            "paoar bank", "smart ghori", "smarwatch", "iphone 15 kovar", "mobail er glass", "charjar cabel",
            "মোবাইল", "স্মার্টফোন", "ফোন", "টাচ ফোন", "অ্যান্ড্রয়েড মোবাইল", "কম দামে মোবাইল",
            "ভালো মোবাইল", "আইফোন ১৫", "আইফোন ১৪", "আইফোন ১৬", "অ্যাপল ফোন", "আইফোন প্রো ম্যাক্স",
            "স্যামসাং এস২৪", "স্যামসাং মোবাইল", "গ্যালাক্সি ফোন", "স্যামসাং এ৫৪", "স্যামসাং আল্ট্রা",
            "রিয়েলমি মোবাইল", "শাওমি ফোন", "ওয়ানপ্লাস", "ভিভো ফোন", "অপ্পো", "ইনফিনিক্স", "টেকনো মোবাইল",
            "ব্লুটুথ ইয়ারবাড", "এয়ারপড", "পাওয়ার ব্যাংক", "স্মার্ট ওয়াচ", "ফিটনেস ব্যান্ড",
            "আইফোন ১৫ ব্যাক কাভার", "গ্লাস প্রটেক্টর", "টাইপ সি ক্যাবল",
            "Gadget & Gear", "Star Tech Gadgets", "Apple", "Samsung", "Xiaomi", "Realme", "OnePlus",
            "Vivo", "Oppo", "Infinix", "Tecno", "Honor", "Motorola", "Google Pixel", "Nothing Phone",
            "Anker", "Baseus", "Ugreen", "QCY", "Haylou", "Joyroom", "Hoco", "Remax", "Oraimo"
        ],
        "default_query": "Smartphone",
        "base_price": 45000,
        "price_min": 12000,
        "price_max": 250000,
        "model_templates": [
            "{title} (Official Bangladesh Edition)",
            "{title} Global Edition (Intact Box)"
        ]
    },
}

# Aliases
CATEGORY_REGISTRY_MAP["budget-jewelry"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["budget-jewellery"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["budget_jewellery_fcommerce"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["budget_jewelry_fcommerce"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["budget-jewelry-fcommerce"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["budget-jewellery-fcommerce"] = CATEGORY_REGISTRY_MAP["fashion-jewelry"]
CATEGORY_REGISTRY_MAP["appliances-electronics"] = CATEGORY_REGISTRY_MAP["home-appliances"]
CATEGORY_REGISTRY_MAP["appliances-and-electronics"] = CATEGORY_REGISTRY_MAP["home-appliances"]
CATEGORY_REGISTRY_MAP["appliances"] = CATEGORY_REGISTRY_MAP["home-appliances"]
CATEGORY_REGISTRY_MAP["fashion"] = CATEGORY_REGISTRY_MAP["fashion-apparel"]
CATEGORY_REGISTRY_MAP["fashion-and-apparel"] = CATEGORY_REGISTRY_MAP["fashion-apparel"]
CATEGORY_REGISTRY_MAP["watches"] = CATEGORY_REGISTRY_MAP["watches-horology"]
CATEGORY_REGISTRY_MAP["watches-and-horology"] = CATEGORY_REGISTRY_MAP["watches-horology"]
CATEGORY_REGISTRY_MAP["mobiles-gadgets"] = CATEGORY_REGISTRY_MAP["mobile-gadgets"]
CATEGORY_REGISTRY_MAP["mobile-phones-and-gadgets"] = CATEGORY_REGISTRY_MAP["mobile-gadgets"]
CATEGORY_REGISTRY_MAP["mobiles"] = CATEGORY_REGISTRY_MAP["mobile-gadgets"]
CATEGORY_REGISTRY_MAP["gadgets"] = CATEGORY_REGISTRY_MAP["mobile-gadgets"]


# One canonical Unicode form for Bengali text. NFC *decomposes* ড় ঢ় য় (they are composition
# exclusions), so every query, keyword and title must go through this same function.
_BN_NUKTA_CANONICAL = {
    "\u09a1\u09bc": "\u09dc",  # ড + ় -> ড়
    "\u09a2\u09bc": "\u09dd",  # ঢ + ় -> ঢ়
    "\u09af\u09bc": "\u09df",  # য + ় -> য়
}
_HAS_BENGALI = re.compile(r"[\u0980-\u09FF]")


def canon_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    for decomposed, composed in _BN_NUKTA_CANONICAL.items():
        s = s.replace(decomposed, composed)
    return s


def _word_hit(kw_norm: str, spaced: str) -> bool:
    """Whole-word match for English keywords (optional plural s/es), so 'dates' never fires inside 'updates'."""
    return re.search(rf"(?<![a-z0-9]){re.escape(kw_norm)}(?:s|es)?(?![a-z0-9])", spaced) is not None


def normalize_search_query(q: str) -> str:
    """
    Sub-string safe and Bengali Unicode-safe query normalizer.
    Preserves Bengali characters (\u0980-\u09FF) and combining vowel signs (kar / কার),
    canonicalizes nukta forms, lowercases English, strips noisy punctuation and spacing.
    """
    if not q:
        return ""
    cleaned = re.sub(r'[^\w\s\u0980-\u09FF-]', ' ', canon_text(q).lower())
    cleaned = cleaned.replace("-", " ").replace("_", " ")
    return " ".join(cleaned.split()).strip()


_DIG = "0-9\u09e6-\u09ef"  # ASCII and Bengali digits
_BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_CURW = r"bdt|tk|taka|৳|টাকা"
_NUMW = rf"[{_DIG}][{_DIG},]*(?:\.[0-9]+)?"
# Whitespace/punctuation boundaries, not \b: \b breaks after Bengali vowel signs (া, ে ...).
_BUDGET_A = re.compile(
    rf"(?<!\S)(?P<kw>under|below|less\s+than|within|upto|up\s+to|max|budget|বাজেট)\s*(?P<c1>{_CURW})?\s*"
    rf"(?P<num>{_NUMW})\s*(?P<k>[kK])?\s*(?P<c2>{_CURW})?(?!\S)", re.I)
_BUDGET_B = re.compile(
    rf"(?<!\S)(?P<num>{_NUMW})\s*(?P<k>[kK])?\s*(?P<c2>টাকার\s+নিচে|টাকার\s+মধ্যে|{_CURW}|/-)(?!\S)", re.I)


def extract_budget_and_clean_query(raw_query: str) -> Tuple[str, Optional[int]]:
    """
    Extracts price-ceiling phrases ('under 85,000', 'below 85k', '1500 taka', 'বাজেট ৮৫০০০',
    '১৫০০ টাকার নিচে') into (cleaned_query, max_price_bdt), removing exactly the matched phrase.
    A bare number is never a budget (model numbers, years, 'max 256 gb' stay in the query), and a
    keyword-only match under 100 needs an explicit currency word.
    """
    if not raw_query:
        return "", None
    for pat in (_BUDGET_A, _BUDGET_B):
        for m in pat.finditer(raw_query):
            g = m.groupdict()
            try:
                value = float(g["num"].translate(_BN_DIGITS).replace(",", ""))
            except ValueError:
                continue
            if g.get("k"):
                value *= 1000
            has_currency = bool(g.get("c1") or g.get("c2"))
            if value < 100 and not has_currency:
                continue
            if (g.get("kw") or "").lower() == "max" and value < 1000 and not has_currency:
                continue
            cleaned = raw_query[:m.start()] + " " + raw_query[m.end():]
            return " ".join(cleaned.split()), int(value)
    return " ".join(raw_query.split()), None


def normalize_search_query_variants(text: str):
    """
    Strips case, hyphens, slashes, punctuation, and extra whitespace.
    Returns: (raw_lower, spaced_lower, collapsed_lower, tokens_set)
    """
    if not text:
        return "", "", "", set()
    raw = canon_text(text).strip().lower()
    spaced = re.sub(r'[^\w\s\u0980-\u09FF]', ' ', raw).strip()
    spaced = re.sub(r'\s+', ' ', spaced)
    collapsed = re.sub(r'[^\w\u0980-\u09FF]', '', raw)
    tokens = set(spaced.split())
    return raw, spaced, collapsed, tokens


# Pre-compiled multi-word EV Priority Regexes (Guarantees e-bike/betari saikel never bleed into computer shops)
EV_PRIORITY_COMPOUNDS = [
    "electronic bike", "electronic bikes", "electric bike", "electric bikes",
    "e-bike", "e-bikes", "ebike", "ebikes", "battery bike", "battery cycle",
    "electric bicycle", "electric cycle", "electric scooter", "e-scooter",
    "escooter", "battery scooty", "betari saikel", "battery saikel",
    "ই-বাইক", "ইলেকট্রিক বাইক", "ব্যাটারি বাইক", "ইলেকট্রিক সাইকেল",
    "ব্যাটারি সাইকেল", "ইলেকট্রিক স্কুটার", "ব্যাটারি স্কুটি"
]


def _resolve_category(query: str, category_hint: Optional[str] = None, allow_default: bool = True) -> tuple:
    """
    Deterministically resolves the category ID and display metadata from any query or hint.
    Guarantees 'e-bike' maps strictly to 'cycles-evs', 'refrigerator' maps strictly to 'home-appliances', etc.
    Zero-constraint normalization: ignores case, hyphens, slashes, spaces, and typo variants.
    Returns (category_id, meta_dict).
    """
    q_raw, q_spaced, q_collapsed, q_tokens = normalize_search_query_variants(query)

    # Priority 0: Multi-Word Priority Intent Routing for Cycles & EVs
    # Compound phrases MUST be evaluated before generic single words (e.g. 'electronic') to prevent
    # leaking into tech stores (Star Tech, Ryans, TechLand).
    for ev_phrase in EV_PRIORITY_COMPOUNDS:
        ev_norm = normalize_search_query(ev_phrase)
        if ev_norm in q_spaced or ev_phrase in q_raw or ev_phrase.replace("-", "") in q_collapsed:
            return "cycles-evs", CATEGORY_REGISTRY_MAP["cycles-evs"]

    # Priority 1: Unambiguous domain keywords in query ALWAYS override stale/contradictory category hints
    if q_collapsed:
        matches = []
        primary_categories = [
            ("cycles-evs", CATEGORY_REGISTRY_MAP["cycles-evs"]),
            ("home-appliances", CATEGORY_REGISTRY_MAP["home-appliances"]),
            ("fashion-apparel", CATEGORY_REGISTRY_MAP["fashion-apparel"]),
            ("saree-boutiques", CATEGORY_REGISTRY_MAP["saree-boutiques"]),
            ("fine-jewelry", CATEGORY_REGISTRY_MAP["fine-jewelry"]),
            ("fashion-jewelry", CATEGORY_REGISTRY_MAP["fashion-jewelry"]),
            ("sneakers-footwear", CATEGORY_REGISTRY_MAP["sneakers-footwear"]),
            ("watches-horology", CATEGORY_REGISTRY_MAP["watches-horology"]),
            ("beauty-skincare", CATEGORY_REGISTRY_MAP["beauty-skincare"]),
            ("sportswear-gym", CATEGORY_REGISTRY_MAP["sportswear-gym"]),
            ("grocery-snacks", CATEGORY_REGISTRY_MAP["grocery-snacks"]),
            ("laptops-pc", CATEGORY_REGISTRY_MAP["laptops-pc"]),
            ("mobile-gadgets", CATEGORY_REGISTRY_MAP["mobile-gadgets"]),
        ]

        # Gather all keywords sorted by length descending (longest-match-first)
        all_kw_items = []
        for cat_id, meta in primary_categories:
            for kw in meta["keywords"]:
                all_kw_items.append((len(kw.strip()), cat_id, meta, kw.strip()))

        all_kw_items.sort(key=lambda x: x[0], reverse=True)

        for kw_len, cat_id, meta, kw in all_kw_items:
            kw_raw = canon_text(kw.lower())
            kw_norm = normalize_search_query(kw_raw)
            kw_collapsed = re.sub(r'[^\w\u0980-\u09FF]', '', kw_raw)
            if not kw_collapsed:
                continue

            matched = False
            score = len(kw_raw)

            # Short terms (<= 3 chars, e.g. 'ac', 'tv', 'ev', 'pc', 'bat', 'dul') require strict whitespace boundary
            # (?<!\S)...(?!\S) so 'macbook air m2' or 'watch' NEVER triggers 'ac' -> 'air conditioner'
            if len(kw_collapsed) <= 3:
                pattern = rf'(?<!\S){re.escape(kw_norm)}(?!\S)'
                if re.search(pattern, q_spaced) or kw_norm in q_tokens:
                    matched = True
                    score = len(kw_norm) * 3
            else:
                # Bengali or multi-word boundary check
                if _HAS_BENGALI.search(kw_norm):
                    direct = kw_raw in q_raw or kw_norm in q_spaced  # Bengali suffixes (শাড়ির) need prefix matching
                else:
                    direct = _word_hit(kw_norm, q_spaced)
                if direct:
                    matched = True
                    if kw_raw == q_raw or kw_norm == q_spaced:
                        score += 60
                # Space-insensitive match ('iphone15', 'e bikes') only for multi-word or Bengali keywords;
                # single English words must match as tokens, or 'dates' fires inside 'updates'.
                elif (len(kw_collapsed) >= 4 and (' ' in kw_norm or _HAS_BENGALI.search(kw_norm))
                      and kw_collapsed in q_collapsed):
                    matched = True
                    score = len(kw_collapsed)
                elif kw_norm in q_tokens:
                    matched = True

            if matched:
                matches.append((score, cat_id, meta))

        if matches:
            matches.sort(key=lambda m: m[0], reverse=True)
            return matches[0][1], matches[0][2]

    # Priority 2: Use category hint when query is brand-only or generic
    if category_hint and category_hint != 'all':
        hint_clean = category_hint.strip().lower()
        hint_norm = hint_clean.replace("_", "-").replace(".csv", "")
        hint_uk = hint_norm.replace("jewellery", "jewelry")

        # Check direct keys and registered aliases
        if hint_clean in CATEGORY_REGISTRY_MAP:
            return hint_clean, CATEGORY_REGISTRY_MAP[hint_clean]
        if hint_norm in CATEGORY_REGISTRY_MAP:
            return hint_norm, CATEGORY_REGISTRY_MAP[hint_norm]
        if hint_uk in CATEGORY_REGISTRY_MAP:
            return hint_uk, CATEGORY_REGISTRY_MAP[hint_uk]

        for cat_id, meta in CATEGORY_REGISTRY_MAP.items():
            csv_name = meta["csv"].lower().replace(".csv", "")
            csv_norm = csv_name.replace("_", "-")
            aliases = [a.lower().replace(".csv", "").replace("_", "-") for a in meta.get("csv_aliases", [])]
            if hint_clean in (meta["display_en"].lower(), meta["vertical"].lower(), meta["csv"].lower(), meta.get("csv_category", "").lower()):
                return cat_id, meta
            if hint_norm in (cat_id, csv_norm, meta["display_en"].lower(), meta["vertical"].lower(), meta.get("csv_category", "").lower()) or hint_norm in aliases:
                return cat_id, meta
            if hint_uk in (cat_id, csv_norm) or hint_uk in aliases:
                return cat_id, meta

    # Priority 3: Default fallback
    if not allow_default:
        return None, None
    return "mobile-gadgets", CATEGORY_REGISTRY_MAP["mobile-gadgets"]


def resolve_category_from_query(query: str, category_hint: Optional[str] = None) -> tuple:
    """Legacy behaviour: anything unmatched falls back to mobile-gadgets."""
    return _resolve_category(query, category_hint, allow_default=True)


def resolve_category_or_none(query: str, category_hint: Optional[str] = None) -> tuple:
    """Returns (None, None) when nothing matches, so callers can say "no results" instead of guessing."""
    return _resolve_category(query, category_hint, allow_default=False)



def get_stores_for_category(category_id: str) -> List[Dict[str, Any]]:
    """Returns curated verified stores strictly from that category's CSV registry."""
    check_and_reload_if_modified()
    meta = CATEGORY_REGISTRY_MAP.get(category_id)
    if not meta:
        _, meta = resolve_category_from_query("", category_hint=category_id)
    if not meta:
        return []
    csv_cat = meta.get("csv_category", "").lower()
    results = []
    for store in ALL_STORES_REGISTRY:
        s_cat = (store.get("category") or store.get("Category") or "").lower()
        if s_cat == csv_cat:
            results.append(store)
    return results


# ==============================================================================
# INITIAL LOAD ON MODULE IMPORT
# ==============================================================================
load_all_registries(force=True)
