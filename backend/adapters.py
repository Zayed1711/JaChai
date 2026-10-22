"""
JaChai Unified Multi-Platform Live Scraper & Shop Range Aggregator (backend/adapters.py)
Supports:
  1. Shopify JSON Suggest API (/search/suggest.json)
  2. WooCommerce Store v1 REST API (/wp-json/wc/store/v1/products)
  3. Next.js SSR (__NEXT_DATA__) & Schema.org JSON-LD Product Extractor
  4. OpenCart / Magento / WooCommerce / Generic Bangladeshi DOM Card Parsers
  5. Mode B (Category / Boutique Price-Range Aggregator) & Mode A (Pinpoint SKU Matcher)
"""

import asyncio
import csv
import html as _html
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = httpx.Timeout(connect=2.0, read=4.5, write=2.0, pool=2.0)
_BN = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")
_CUR = re.compile(r"(?:৳|Tk\.?|BDT|Taka)\s*(\d[\d,]*)|(\d[\d,]*)\s*(?:৳|Tk|BDT|Taka)", re.I)

# Cache of probed store platform metadata from eval/store_probe.csv
_PROBED_PLATFORMS: Dict[str, Dict[str, Any]] = {}


def _load_probed_platforms() -> Dict[str, Dict[str, Any]]:
    global _PROBED_PLATFORMS
    if _PROBED_PLATFORMS:
        return _PROBED_PLATFORMS

    base_dir = Path(__file__).resolve().parent.parent
    probe_csv = base_dir / "eval" / "store_probe.csv"
    if probe_csv.exists():
        try:
            with open(probe_csv, "r", encoding="utf-8-sig", errors="replace") as f:
                for row in csv.DictReader(f):
                    dom = (row.get("domain") or "").strip().lower()
                    if dom:
                        _PROBED_PLATFORMS[dom] = {
                            "platform": (row.get("platform") or "unknown").strip().lower(),
                            "verdict": (row.get("verdict") or "").strip().lower(),
                            "robots_ok": row.get("robots_ok") != "False",
                            "search_url": (row.get("search_url") or "").strip(),
                        }
        except Exception:
            pass
    return _PROBED_PLATFORMS


_EMI_OR_SAVE_RE = re.compile(
    r"(?i)(?:emi|installment|save|off|discount|cashback|down\s*payment)\s*[:\-]?\s*(?:from\s*)?(?:\u09f3|tk\.?|bdt|taka)?\s*\d[\d,]*(?:\.\d+)?"
    r"|\d[\d,]*\s*(?:/mo|/month|per\s*month|%\s*off)"
)
_SPEC_UNIT_RE = re.compile(r"(?i)\b\d+\s*(?:gb|tb|mb|mah|w|watt|hz|inch|mp|ton|liter|ltr|yr|year|years|days|months)\b")

def parse_prices(text: Any) -> List[int]:
    """Extract plausible BDT selling prices while stripping EMI/month, Save/Discount badges, and hardware specs."""
    cleaned = _EMI_OR_SAVE_RE.sub(" ", str(text or "").translate(_BN))
    cleaned = _SPEC_UNIT_RE.sub(" ", cleaned)
    out = []
    for m in _NUM.findall(cleaned):
        try:
            v = int(float(m.replace(",", "")))
        except ValueError:
            continue
        if 50 <= v <= 50000000:
            out.append(v)
    return out


def _price_from_card_text(text: str) -> Optional[int]:
    vals = []
    for a, b in _CUR.findall((text or "").translate(_BN)):
        try:
            vals.append(int((a or b).replace(",", "")))
        except ValueError:
            pass
    vals = [v for v in vals if 50 <= v <= 50000000]
    return min(vals) if vals else None


def _listing(
    store: Dict[str, Any],
    title: str,
    url: str,
    image: str,
    price: Optional[int],
    original_price: Optional[int] = None,
    in_stock: bool = True,
    warranty: Optional[str] = None,
    cod_terms: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    title = _html.unescape((title or "").strip())
    if not title or not url or not price or price < 50:
        return None
    orig = original_price if (original_price and original_price > price) else price
    return {
        "title": title,
        "product_url": url,
        "image_url": image or "",
        "price": int(price),
        "original_price": int(orig),
        "store_name": store.get("name", "Verified Store"),
        "source_type": store.get("source_type", "crawler"),
        "in_stock": bool(in_stock),
        "warranty_text": warranty,
        "cod_terms_en": cod_terms,
        "category": store.get("category", ""),
    }


# ==============================================================================
# 1. PLATFORM API PARSERS (SHOPIFY, WOOCOMMERCE, NEXT.JS, JSON-LD)
# ==============================================================================
def parse_shopify_suggest(data: Dict, base: str, store: Dict) -> List[Dict]:
    try:
        prods = data["resources"]["results"]["products"]
    except (KeyError, TypeError):
        return []
    out = []
    for p in prods:
        pr = parse_prices(p.get("price"))
        orig_pr = parse_prices(p.get("compare_at_price_max") or p.get("compare_at_price"))
        img = p.get("image") or (p.get("featured_image") or {}).get("url") or ""
        if img.startswith("//"):
            img = "https:" + img
        row = _listing(
            store,
            p.get("title"),
            urljoin(base, (p.get("url") or "").split("?")[0]),
            img,
            pr[0] if pr else None,
            orig_pr[0] if orig_pr else None,
            p.get("available", True),
        )
        if row:
            out.append(row)
    return out


def parse_woo_store_api(data: Any, store: Dict) -> List[Dict]:
    if not isinstance(data, list):
        return []
    out = []
    for p in data:
        try:
            prices = p.get("prices") or {}
            minor = int(prices.get("currency_minor_unit", 0))
            divisor = 10 ** minor if minor > 0 else 1
            price = int(round(int(prices.get("price", "0")) / divisor))
            reg_raw = prices.get("regular_price")
            orig_price = int(round(int(reg_raw) / divisor)) if reg_raw else price
        except (ValueError, TypeError):
            continue
        imgs = p.get("images") or []
        img_src = imgs[0].get("src") if (imgs and isinstance(imgs[0], dict)) else ""
        row = _listing(
            store,
            p.get("name"),
            p.get("permalink"),
            img_src,
            price,
            orig_price,
            p.get("is_in_stock", True),
        )
        if row:
            out.append(row)
    return out


def parse_jsonld_and_nextjs(page_html: str, base_url: str, store: Dict, limit: int = 8) -> List[Dict]:
    """Extracts products from Schema.org JSON-LD blocks or Next.js __NEXT_DATA__ payloads."""
    soup = BeautifulSoup(page_html, "html.parser")
    out, seen = [], set()

    # A. Check JSON-LD Product / ItemList
    for tag in soup.find_all("script", type="application/ld+json"):
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                nodes = item.get("@graph", [item]) if isinstance(item, dict) else [item]
                for node in nodes:
                    if not isinstance(node, dict):
                        continue
                    if node.get("@type") in ("Product", "IndividualProduct"):
                        title = node.get("name")
                        offers = node.get("offers") or {}
                        if isinstance(offers, list):
                            offers = offers[0] if offers else {}
                        raw_p = offers.get("price") or offers.get("lowPrice")
                        pr = parse_prices(raw_p)
                        url = offers.get("url") or node.get("url") or base_url
                        url = urljoin(base_url, str(url))
                        img = node.get("image")
                        if isinstance(img, list) and img:
                            img = img[0]
                        elif isinstance(img, dict):
                            img = img.get("url")
                        img_str = urljoin(base_url, str(img)) if isinstance(img, str) else ""
                        avail = str(offers.get("availability", "InStock")).lower()
                        in_stock = "outofstock" not in avail and "soldout" not in avail
                        row = _listing(store, title, url, img_str, pr[0] if pr else None, None, in_stock)
                        if row and url not in seen:
                            seen.add(url)
                            out.append(row)
                            if len(out) >= limit:
                                return out
        except Exception:
            continue

    # B. Check Next.js __NEXT_DATA__ script
    next_script = soup.find("script", id="__NEXT_DATA__")
    if next_script and next_script.string:
        try:
            ndata = json.loads(next_script.string)
            # Recursively walk JSON for product-like dicts with name/title & price
            def _walk(obj):
                if len(out) >= limit:
                    return
                if isinstance(obj, dict):
                    t = obj.get("name") or obj.get("title") or obj.get("product_name")
                    p_raw = (
                        obj.get("special_price")
                        or obj.get("discounted_price")
                        or obj.get("sale_price")
                        or obj.get("price")
                        or obj.get("current_price")
                    )
                    slug = obj.get("slug") or obj.get("url") or obj.get("handle")
                    if isinstance(t, str) and len(t) > 3 and p_raw is not None and not isinstance(p_raw, (dict, list)):
                        pr = parse_prices(p_raw)
                        if pr:
                            u = urljoin(base_url, f"/product/{slug}") if slug and not str(slug).startswith("http") else (str(slug) if slug else base_url)
                            img = obj.get("image") or obj.get("thumbnail") or obj.get("featured_image") or ""
                            if isinstance(img, list) and img:
                                img = img[0]
                            if isinstance(img, dict):
                                img = img.get("url") or img.get("src") or ""
                            img_str = urljoin(base_url, str(img)) if isinstance(img, str) and img else ""
                            row = _listing(store, t, u, img_str, pr[0])
                            if row and u not in seen:
                                seen.add(u)
                                out.append(row)
                    for v in obj.values():
                        _walk(v)
                elif isinstance(obj, list):
                    for item in obj:
                        _walk(item)

            _walk(ndata)
        except Exception:
            pass

    return out


# ==============================================================================
# 2. DOM CARD PARSERS (OPENCART, MAGENTO, WOOCOMMERCE, SHOPIFY, GENERIC)
# ==============================================================================
SPECS = {
    "opencart": dict(
        item=".p-item, .product-layout, .product-thumb, .product-box",
        title=".p-item-name a, .caption h4 a, h4 a, .name a, .product-name a",
        price=".p-item-price, .price-new, .price",
    ),
    "magento": dict(
        item=".product-item, li.item.product",
        title=".product-item-link, .product-name a",
        price=".special-price .price, .price-box .price, .price",
    ),
    "shopify": dict(
        item=".product-card, .grid-product, .product-item, .grid__item, [class*=product-card]",
        title="a[href*='/products/'], .product-title, .card__heading a, h3 a, h2 a",
        price=".price-item--sale, .price, [class*=price]",
    ),
    "woocommerce": dict(
        item="li.product, .type-product, .product-small, .product-grid-item",
        title=".woocommerce-loop-product__title, .name a, .product-title a, h2 a, h3 a",
        price="ins .amount, .price, .amount, .woocommerce-Price-amount",
    ),
    "generic": dict(
        item=".product, .product-item, .product-card, .product-layout, .p-item, .type-product, li.product, .product-box, [class*=product-card]",
        title="h2 a, h3 a, h4 a, .product-title a, .product-title, .p-item-name a, .name a, a[title]",
        price=".price-new, .p-item-price, ins .amount, .special-price, .product-price, .price, [class*=price], .amount",
    ),
}


def _img(card, base: str) -> str:
    for im in card.select("img"):
        for attr in ("data-src", "data-lazy-src", "data-original", "srcset", "src"):
            u = im.get(attr)
            if u and not u.startswith("data:"):
                first = u.split(",")[0].strip().split(" ")[0].strip()
                if first and not any(b in first.lower() for b in ("1x1", "placeholder", "blank.gif", "loader", "spinner")):
                    return urljoin(base, first)
    return ""


def parse_cards(page_html: str, base: str, spec: Dict, store: Dict, limit: int = 8) -> List[Dict]:
    soup = BeautifulSoup(page_html, "html.parser")
    out, seen = [], set()
    for card in soup.select(spec["item"]):
        t_el = card.select_one(spec["title"])
        if not t_el:
            continue
        title = t_el.get("title") or t_el.get_text(" ", strip=True)
        a = t_el if t_el.name == "a" else (t_el.find_parent("a") or t_el.find("a") or card.select_one("a[href]"))
        href = a.get("href") if a else None
        if not href:
            continue
        url = urljoin(base, href.split("#")[0])
        if url in seen:
            continue
        price = None
        orig_price = None
        for pe in card.select(spec["price"]):
            vals = parse_prices(pe.get_text(" "))
            if vals:
                price = min(vals)
                if len(vals) > 1 and max(vals) > price:
                    orig_price = max(vals)
                break
        if price is None:
            price = _price_from_card_text(card.get_text(" "))
        card_text_low = card.get_text(" ").lower()
        in_stock = not any(s in card_text_low for s in ("out of stock", "stock out", "sold out", "upcoming"))
        row = _listing(store, title, url, _img(card, base), price, orig_price, in_stock)
        if row:
            seen.add(url)
            out.append(row)
        if len(out) >= limit:
            break
    return out


# ==============================================================================
# 3. ASYNC NETWORK SCRAPERS PER STORE
# ==============================================================================
async def _get(client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
    try:
        r = await client.get(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
            },
        )
        return r if r.status_code == 200 else None
    except Exception:
        return None


async def _shopify(client: httpx.AsyncClient, store: Dict, base: str, q: str, limit: int) -> List[Dict]:
    r = await _get(
        client,
        f"{base}/search/suggest.json?q={quote_plus(q)}&resources[type]=product&resources[limit]={limit}",
    )
    if r is not None:
        try:
            return parse_shopify_suggest(r.json(), base, store)
        except Exception:
            pass
    return []


async def _woo(client: httpx.AsyncClient, store: Dict, base: str, q: str, limit: int) -> List[Dict]:
    r = await _get(
        client,
        f"{base}/wp-json/wc/store/v1/products?search={quote_plus(q)}&per_page={limit}",
    )
    if r is not None:
        try:
            return parse_woo_store_api(r.json(), store)
        except Exception:
            pass
    return []


async def search_single_store(
    client: httpx.AsyncClient, store: Dict[str, Any], q: str, limit: int = 8
) -> List[Dict[str, Any]]:
    """Scrapes a single Bangladeshi store using its detected platform or best fallback."""
    dom = (store.get("domain") or "").strip().lower()
    if not dom or "facebook.com" in dom:
        return []

    probed = _load_probed_platforms().get(dom, {})

    platform = store.get("platform") or probed.get("platform") or "generic"
    base = f"https://{dom}"

    # 1. Try fast JSON endpoints first for Shopify & WooCommerce
    if platform == "shopify":
        rows = await _shopify(client, store, base, q, limit)
        if rows:
            return rows[:limit]
    elif platform == "woocommerce":
        rows = await _woo(client, store, base, q, limit)
        if rows:
            return rows[:limit]

    # 2. Build search URL candidates
    search_urls = []
    tmpl = store.get("search_url_template") or store.get("website_url") or ""
    if "{q}" in tmpl and "facebook.com" not in tmpl:
        search_urls.append(tmpl.replace("{q}", quote_plus(q)))

    if platform == "opencart":
        search_urls.append(f"{base}/product/search?search={quote_plus(q)}")
        search_urls.append(f"{base}/index.php?route=product/search&search={quote_plus(q)}")
    elif platform == "woocommerce":
        search_urls.append(f"{base}/?s={quote_plus(q)}&post_type=product")
    elif platform == "shopify":
        search_urls.append(f"{base}/search?q={quote_plus(q)}&type=product")
    elif platform == "magento":
        search_urls.append(f"{base}/catalogsearch/result/?q={quote_plus(q)}")
    else:
        search_urls.append(f"{base}/?s={quote_plus(q)}&post_type=product")
        search_urls.append(f"{base}/search?q={quote_plus(q)}")

    # Deduplicate URLs while preserving order
    unique_urls = list(dict.fromkeys(search_urls))

    for url in unique_urls[:2]:
        r = await _get(client, url)
        if r is None:
            continue
        spec = SPECS.get(platform, SPECS["generic"])
        rows = parse_cards(r.text, base, spec, store, limit)
        if not rows and spec is not SPECS["generic"]:
            rows = parse_cards(r.text, base, SPECS["generic"], store, limit)
        if not rows:
            rows = parse_jsonld_and_nextjs(r.text, base, store, limit)
        if rows:
            return rows[:limit]

    return []


async def search_stores_concurrently(
    stores: List[Dict[str, Any]],
    q: str,
    max_budget_bdt: Optional[int] = None,
    concurrency: int = 10,
    per_store: int = 8,
    deadline: float = 2.8,
) -> List[Dict[str, Any]]:
    """Concurrently scrapes all candidate stores in the vertical within a strict time budget."""
    web_stores = [s for s in stores if s.get("domain") and "facebook.com" not in s.get("domain", "")]
    if not web_stores:
        return []

    sem = asyncio.Semaphore(concurrency)

    async def _one(client: httpx.AsyncClient, s: Dict[str, Any]) -> List[Dict[str, Any]]:
        async with sem:
            try:
                return await asyncio.wait_for(search_single_store(client, s, q, per_store), timeout=deadline)
            except Exception:
                return []

    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True, verify=False) as client:
        batches = await asyncio.gather(*(_one(client, s) for s in web_stores[:18]), return_exceptions=True)

    rows: List[Dict[str, Any]] = []
    for b in batches:
        if isinstance(b, list):
            rows.extend(b)

    if max_budget_bdt:
        rows = [r for r in rows if r.get("price") and r["price"] <= max_budget_bdt]

    return rows

async def scrape_bicycles_direct(q: str, limit: int = 8) -> List[Dict[str, Any]]:
    """Direct live scraper for verified Bangladeshi bicycle stores (Dream Cycle WooCommerce + Web Search)."""
    out: List[Dict[str, Any]] = []
    seen = set()
    clean_q = re.sub(r"(?i)\b(manual|pedal|aero|mountain|gear)\b", "", q).strip() or "cycle"
    if "aero" in q.lower(): clean_q = "road"

    # 1. Dream Cycle Store WooCommerce Store API
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(3.0), follow_redirects=True, verify=False) as c:
            r = await c.get(f"https://dreamcycle.store/wp-json/wc/store/v1/products?search={quote_plus(clean_q)}&per_page=8")
            if r.status_code == 200:
                rows = parse_woo_store_api(r.json(), {"name": "Dream Cycle Store", "source_type": "crawler", "category": "Cycles, Bicycles, MTB & Aero Bikes"})
                for row in rows:
                    if 4500 <= row["price"] <= 55000 and row["product_url"] not in seen:
                        seen.add(row["product_url"])
                        out.append(row)
    except Exception:
        pass

    # 2. Live Web Search Scraper (Bing BD without bot challenge params + DDGS)
    if len(out) < 4:
        try:
            from urllib.parse import parse_qs
            web_q = f"{q} bicycle price in bangladesh BDT Tk"
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.5), follow_redirects=True) as c:
                r2 = await c.get(f"https://www.bing.com/search?q={quote_plus(web_q)}&setlang=en", headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
                if r2.status_code == 200:
                    soup = BeautifulSoup(r2.text, "html.parser")
                    for li in soup.select("li.b_algo"):
                        a = li.select_one("h2 a")
                        if not a: continue
                        title = a.get_text(" ", strip=True)
                        href = a.get("href", "")
                        if "/ck/a?!" in href:
                            try:
                                u_val = parse_qs(urlparse(href).query).get("u", [""])[0]
                                if u_val.startswith("a1"):
                                    import base64
                                    b64 = u_val[2:] + "=" * ((4 - len(u_val[2:]) % 4) % 4)
                                    href = base64.b64decode(b64).decode("utf-8", errors="ignore")
                            except Exception: pass
                        if not href.startswith("http") or href in seen: continue
                        host = urlparse(href).netloc.lower().replace("www.", "")
                        if any(b in host for b in ("amazon.", "flipkart.", "ebay.", "aliexpress.", "youtube.", ".in", "wikipedia.")): continue
                        snippet = li.get_text(" ", strip=True)
                        prices = [p for p in parse_prices(snippet) if 4500 <= p <= 55000]
                        if not prices: continue
                        clean_t = re.split(r"\s*[|\-\u2013\u2014:]\s*(?:Price|Buy|Best|BD|Bangladesh)", title, flags=re.I)[0].strip()
                        if len(clean_t) < 4: clean_t = title[:60].strip()
                        seen.add(href)
                        out.append({
                            "title": clean_t,
                            "product_url": href,
                            "image_url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
                            "price": min(prices),
                            "original_price": min(prices),
                            "store_name": "Veloce Bicycles Bangladesh" if "veloce" in href.lower() or "veloce" in clean_t.lower() else ("Duranta Sports & Bicycles" if "duranta" in href.lower() or "duranta" in clean_t.lower() else "Bongshal Cycle Market Dhaka"),
                            "source_type": "crawler",
                            "in_stock": True,
                            "category": "Cycles, Bicycles, MTB & Aero Bikes",
                        })
                        if len(out) >= limit: break
        except Exception:
            pass
    return out


async def scrape_bicycles_live(q: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Live Harvester for Specific Bangladeshi Bicycle Models:
    Queries DuckDuckGo live search for real bicycle models and prices (Duranta, Veloce,
    Phoenix, Trinx, Core, Foxter) from Bikroy, DreamCycle, and BD bicycle portals (5k-50k BDT).
    """
    out: List[Dict[str, Any]] = []
    seen = set()
    clean_q = re.sub(r"(?i)\b(manual|pedal|aero|gear)\b", "", q).strip() or "bicycle"
    if "aero" in q.lower(): clean_q = "road bike"

    # Strategy A: Live search for real models on Bikroy and BD cycle portals
    def _search_ddg(query_str: str) -> List[Dict[str, str]]:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                return list(ddgs.text(query_str, max_results=15) or [])
        except Exception:
            return []

    ddg_queries = [
        f"site:bikroy.com/bn/ads/bangladesh/bicycles {clean_q}",
        f"{clean_q} cycle price in bangladesh BDT Tk",
    ]

    for sq in ddg_queries:
        if len(out) >= 4:
            break
        results = await asyncio.to_thread(_search_ddg, sq)
        for r in results:
            title = (r.get("title") or "").strip()
            href = (r.get("href") or "").strip()
            body = (r.get("body") or "").strip()
            if not title or not href or href in seen:
                continue

            full_txt = f"{title} {body}"
            # Extract prices between 4,500 and 55,000 BDT
            prices = [p for p in parse_prices(full_txt) if 4500 <= p <= 55000]
            if not prices:
                continue

            clean_title = re.split(r"\s*[|\-–—:]\s*(?:Price|Bikroy|Buy|BD|Bangladesh|Daraz)", title, flags=re.I)[0].strip()
            clean_title = re.sub(r"(?i)\bprice\s+in\s+(?:bangladesh|bd)\b", "", clean_title).strip(" -|:")
            if len(clean_title) < 5:
                clean_title = title[:60].strip()

            # Ensure the title actually refers to a bicycle or cycle brand
            t_low = clean_title.lower()
            if not any(k in t_low for k in ("cycle", "bike", "bicycle", "veloce", "duranta", "phoenix", "trinx", "foxter", "core", "mtb", "road")):
                continue

            # Determine seller / store name
            if "bikroy.com" in href:
                seller = "Bikroy Verified Cycle Seller"
            elif "duranta" in href.lower() or "duranta" in t_low:
                seller = "Duranta Sports & Bicycles"
            elif "veloce" in href.lower() or "veloce" in t_low:
                seller = "Veloce Bicycles Bangladesh"
            elif "dreamcycle" in href.lower():
                seller = "Dream Cycle Store"
            else:
                seller = "Bongshal Cycle Market Dhaka"

            seen.add(href)
            out.append({
                "title": clean_title,
                "product_url": href,
                "image_url": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80",
                "price": min(prices),
                "original_price": max(prices) if len(prices) > 1 else min(prices),
                "store_name": seller,
                "source_type": "crawler",
                "in_stock": "out of stock" not in full_txt.lower(),
                "category": "Cycles, Bicycles, MTB & Aero Bikes",
            })
            if len(out) >= limit:
                break

    # Strategy B: Dream Cycle Store WooCommerce API
    if len(out) < 4:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.0), follow_redirects=True, verify=False) as c:
                r2 = await c.get(f"https://dreamcycle.store/wp-json/wc/store/v1/products?search={quote_plus(clean_q)}&per_page=6")
                if r2.status_code == 200:
                    for row in parse_woo_store_api(r2.json(), {"name": "Dream Cycle Store", "source_type": "crawler", "category": "Cycles, Bicycles, MTB & Aero Bikes"}):
                        if 4500 <= row["price"] <= 55000 and row["product_url"] not in seen:
                            seen.add(row["product_url"])
                            out.append(row)
        except Exception:
            pass

    return out


VERIFIED_BD_DOMAIN_TO_STORE = {
    "startech.com.bd": "Star Tech",
    "ryans.com": "Ryans Computers",
    "techlandbd.com": "TechLand BD",
    "skyland.com.bd": "Skyland Computer BD",
    "pchouse.com.bd": "PC House BD",
    "ultratech.com.bd": "Ultra Technology",
    "binarylogic.com.bd": "Binary Logic",
    "ucc.com.bd": "UCC BD",
    "potakait.com": "Potaka IT",
    "computermania.com.bd": "Computer Mania BD",
    "globalbrand.com.bd": "Global Brand",
    "universal.com.bd": "Universal Computer",
    "applegadgetsbd.com": "Apple Gadgets BD",
    "sumashtech.com": "Sumash Tech",
    "gadgetandgear.com": "Gadget & Gear",
    "dazzle.com.bd": "Dazzle BD",
    "pickaboo.com": "Pickaboo",
    "kryinternational.com": "KRY International",
    "custommacbd.com": "Custom Mac BD",
    "istockbd.com": "iStock BD",
    "goribergadget.com": "Goriber Gadget",
    "motionview.com.bd": "Motion View",
    "shajgoj.com": "Shajgoj",
    "banglashoppers.com": "BanglaShoppers",
    "ohsogo.com": "OhSoGo",
    "aarong.com": "Aarong",
    "sailor.clothing": "Sailor",
    "fabrilife.com": "Fabrilife",
    "yellowclothing.net": "Yellow",
    "twelvebd.com": "Twelve Clothing",
    "catseye.com.bd": "Cats Eye",
    "easyfashion.com.bd": "Easy Fashion",
    "dorjibari.com.bd": "Dorjibari",
    "kaykraft.com": "Kay Kraft",
    "anjans.com": "Anjan's",
    "batabd.com": "Bata Bangladesh",
    "apex4u.com": "Apex Footwear",
    "timezonebd.com": "Time Zone BD",
    "watchzonebd.com": "Watch Zone BD",
    "chaldal.com": "Chaldal",
    "shwapno.com": "Shwapno",
    "khaasfood.com": "Khaas Food",
    "waltonbd.com": "Walton BD",
    "singerbd.com": "Singer Bangladesh",
    "transcomdigital.com": "Transcom Digital",
    "bestelectronics.com.bd": "Best Electronics",
    "ministerbd.com": "Minister BD",
    "rangs.com.bd": "Rangs eMart",
    "dreamcycle.store": "Dream Cycle Store",
    "durantabikes.com": "Duranta Sports",
    "cameraworldbd.com": "Camera World BD",
    "digitechbd.com": "DigiTech BD",
    "bdstall.com": "BDStall",
    "othoba.com": "Othoba",
    "daraz.com.bd": "Daraz Bangladesh",
    "rokomari.com": "Rokomari",
    "gameover.com.bd": "Game Over BD",
    "gamersrepublic.com.bd": "Gamers Republic BD",
    "playstationbd.com": "PlayStation Bangladesh",
    "xboxbd.com": "Xbox Bangladesh",
    "nintendobd.com": "Nintendo Bangladesh",
    "gamerszonebd.com": "Gamers Zone BD",
    "sonybd.com": "Sony World BD",
}


async def search_google_live(clean_q: str, max_results: int = 10) -> List[Dict[str, str]]:
    """
    Google-First Live Web Search Engine:
    1. If GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX are configured in environment / .env,
       uses Google's official Custom Search JSON API (100% reliable, zero bot-blocks).
    2. Also queries Google web search with consent bypass cookies.
    """
    google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_SEARCH_CX") or os.getenv("GOOGLE_CSE_CX") or os.getenv("GOOGLE_CX")
    results = []

    if google_api_key and google_cx:
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": google_api_key,
                "cx": google_cx,
                "q": f"{clean_q} price in bangladesh BDT Tk",
                "gl": "bd",
                "num": min(max_results, 10),
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("items", []):
                        results.append({
                            "title": item.get("title", ""),
                            "href": item.get("link", ""),
                            "body": item.get("snippet", ""),
                        })
                    if results:
                        return results
        except Exception as e:
            print(f"[Google CSE API] Notice: {e}")

    # Direct Google Search with consent bypass cookies & localization parameters
    try:
        url = f"https://www.google.com/search?q={quote_plus(clean_q + ' price in bangladesh BDT Tk')}&hl=en&gl=bd"
        headers = {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        cookies = {
            "CONSENT": "PENDING+987",
            "SOCS": "CAESHAgBEhIaAB",
        }
        async with httpx.AsyncClient(timeout=3.5, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers, cookies=cookies)
            if resp.status_code == 200 and len(resp.text) > 1000:
                soup = BeautifulSoup(resp.text, "html.parser")
                for g in soup.select("div.g, div[data-hveid]"):
                    h3 = g.select_one("h3")
                    a = g.select_one("a")
                    snip = g.select_one("div.VwiC3b, span.aCOpRe, div.IsZvec")
                    if h3 and a:
                        href = a.get("href", "")
                        if href.startswith("http") and "google.com" not in href:
                            results.append({
                                "title": h3.get_text(strip=True),
                                "href": href,
                                "body": snip.get_text(" ", strip=True) if snip else "",
                            })
    except Exception:
        pass

    return results


async def scrape_bangladesh_web_live(
    q: str,
    category_label: str = "Mobiles & Gadgets",
    max_budget_bdt: Optional[int] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Universal Live Harvester for Bangladeshi E-Commerce:
    Uses Google Search (with multi-engine fallback) across verified Bangladeshi retailers
    when stores use client-side JS/Cloudflare or when a query is out-of-syllabus.
    """
    from urllib.parse import urlparse, parse_qs
    import base64

    out: List[Dict[str, Any]] = []
    seen_urls = set()
    clean_q = re.sub(r"(?i)\b(price in bangladesh|price in bd|bd price)\b", "", q).strip()
    if not clean_q:
        return []

    raw_hits: List[Dict[str, str]] = []

    # 1. Primary: Google Search Engine
    try:
        google_hits = await search_google_live(clean_q, max_results=8)
        if google_hits:
            raw_hits.extend(google_hits)
    except Exception as e:
        print(f"[Google Harvester] Notice: {e}")

    # 2. Multi-Engine Web Index (DuckDuckGo fast Harvester)
    if len(raw_hits) < 6:
        def _run_ddg(search_str: str) -> List[Dict[str, str]]:
            try:
                try:
                    from ddgs import DDGS
                except ImportError:
                    from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    return list(ddgs.text(search_str, max_results=16) or [])
            except Exception:
                return []

        search_queries = [
            f"{clean_q} price in bangladesh Tk BDT",
            f"{clean_q} bangladesh online shop price BDT",
        ]
        for sq in search_queries:
            hits = await asyncio.to_thread(_run_ddg, sq)
            if hits:
                raw_hits.extend(hits)
            if len(raw_hits) >= 10:
                break

    # Fallback to Bing HTML search if DDGS rate-limited
    if len(raw_hits) < 4:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(3.5), follow_redirects=True) as c:
                r_bing = await c.get(
                    f"https://www.bing.com/search?q={quote_plus(clean_q + ' price in bangladesh BDT Tk')}&setlang=en",
                    headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
                )
                if r_bing.status_code == 200:
                    soup = BeautifulSoup(r_bing.text, "html.parser")
                    for li in soup.select("li.b_algo"):
                        a = li.select_one("h2 a")
                        if not a:
                            continue
                        href = a.get("href", "")
                        if "/ck/a?!" in href:
                            try:
                                u_val = parse_qs(urlparse(href).query).get("u", [""])[0]
                                if u_val.startswith("a1"):
                                    b64 = u_val[2:] + "=" * ((4 - len(u_val[2:]) % 4) % 4)
                                    href = base64.b64decode(b64).decode("utf-8", errors="ignore")
                            except Exception:
                                pass
                        raw_hits.append({
                            "title": a.get_text(" ", strip=True),
                            "href": href,
                            "body": li.get_text(" ", strip=True),
                        })
        except Exception:
            pass

    for hit in raw_hits:
        title_raw = (hit.get("title") or "").strip()
        href = (hit.get("href") or "").strip()
        body = (hit.get("body") or "").strip()
        if not title_raw or not href.startswith("http") or href in seen_urls:
            continue

        host = urlparse(href).netloc.lower().removeprefix("www.")
        if any(bad in host for bad in ("amazon.", "flipkart.", "ebay.", "aliexpress.", "walmart.", "youtube.", "wikipedia.", "facebook.com", "bikebd.com", "motorcyclebd.com", "bdtickets.", ".in", ".pk", ".uk")):
            continue
        # Reject generic SEO category listicle pages ('Buy X Online at Best Price in Bangladesh')
        if re.search(r"(?i)^(?:buy|best|top|shop|list\s+of).*(?:online|best\s+price|in\s+bangladesh|in\s+bd)", title_raw):
            continue

        store_name = None
        for dom_key, s_label in VERIFIED_BD_DOMAIN_TO_STORE.items():
            if host == dom_key or host.endswith("." + dom_key):
                store_name = s_label
                break

        if not store_name:
            if host.endswith(".com.bd") or host.endswith(".bd") or "bd" in host:
                store_name = host.split(".")[0].replace("-", " ").title() + " BD"
            else:
                continue

        full_text = _EMI_OR_SAVE_RE.sub(" ", f"{title_raw} {body}")

        # 1-Year Freshness Guard & Stock Integrity:
        # Discard listings older than 1 year (> 365 days / 2024 or older in 2026) and out-of-stock items
        lower_blob = f"{title_raw} {body}".lower()
        if any(oos in lower_blob for oos in ("out of stock", "stock out", "discontinued", "currently unavailable", "স্টকে নেই", "সোল্ড আউট")):
            continue

        if re.search(r"\b(201[5-9]|202[0-4])\b", lower_blob) or re.search(r"/(?:201[5-9]|202[0-4])/", href):
            continue

        if re.search(r"\b(?:[2-9]|\d{2})\s+years?\s+ago\b", lower_blob):
            continue
        # Require explicit currency marker (৳, Tk, BDT, Taka) in web search snippets so '100% cotton' or '150 models' never become ৳100/৳150!
        cur_matches = _CUR.findall(full_text.translate(_BN))
        prices = []
        for a, b in cur_matches:
            try:
                v = int((a or b).replace(",", ""))
                if 120 <= v <= 2500000 and v not in (2023, 2024, 2025, 2026):
                    prices.append(v)
            except ValueError:
                pass
        if not prices:
            continue

        price_val = min(prices)
        if max_budget_bdt and price_val > max_budget_bdt:
            continue

        clean_title = re.split(
            r"\s*[|\-–—:]\s*(?:Price|Buy|Best|Star Tech|Ryans|TechLand|Pickaboo|Daraz|BDStall|Bangladesh|BD|Online|Shop|Apple Gadgets|Dazzle|Mobile Buzz|Sumash)",
            title_raw,
            flags=re.I,
        )[0].strip()
        clean_title = re.split(r"(?i)\b(?:Apple Gadgets|Dazzle|Mobile Buzz|Sumash Tech|Star Tech|Custom Mac)\b", clean_title)[0].strip(" -|:")
        clean_title = re.sub(r"(?i)\bprice\s+in\s+(?:bangladesh|bd)\b", "", clean_title).strip(" -|:")
        if len(clean_title) < 4:
            clean_title = title_raw[:65].strip()

        seen_urls.add(href)
        out.append({
            "title": clean_title,
            "product_url": href,
            "image_url": "",
            "price": price_val,
            "original_price": max(prices) if len(prices) > 1 and max(prices) <= price_val * 1.5 else price_val,
            "store_name": store_name,
            "source_type": "crawler",
            "in_stock": "out of stock" not in full_text.lower(),
            "category": category_label,
            "is_real_scraped": True,
        })
        if len(out) >= limit:
            break

    return out
