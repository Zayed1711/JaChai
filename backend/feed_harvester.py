"""
JaChai Automated Merchant Feed Harvester Engine
(backend/feed_harvester.py)

Ingests live structured product catalogues directly from verified Bangladeshi retailers:
  1. Shopify Public Product Feeds (/products.json) - High-throughput, multi-variant, exact prices
  2. Structured Schema.org/Product JSON-LD from Merchant Sitemaps (Apple Gadgets, Star Tech, etc.)
  3. RSS / XML Merchant Product Feeds

Provides normalized feed items for the Catalog Distiller to merge into the
Universal Master Product Catalog and Database Cache.
"""

import asyncio
from datetime import datetime
import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

logger = logging.getLogger("feed_harvester")
logging.basicConfig(level=logging.INFO)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, application/xml",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
}

# Verified Bangladeshi store endpoints
KNOWN_SHOPIFY_FEEDS = [
    {
        "store_name": "Custom Mac BD",
        "base_url": "https://custommacbd.com",
        "category_hint": "Laptops & Gadgets",
    },
]

KNOWN_SITEMAP_FEEDS = [
    {
        "store_name": "Apple Gadgets BD",
        "sitemap_url": "https://www.applegadgetsbd.com/product/sitemap.xml",
        "category_hint": "Mobiles & Gadgets",
        "max_sample": 60,
    },
    {
        "store_name": "Dazzle BD",
        "sitemap_url": "https://dazzle.com.bd/products/sitemap.xml",
        "category_hint": "Mobiles & Gadgets",
        "max_sample": 40,
    },
]


def clean_price_string(price_raw: Any) -> Optional[int]:
    """Extracts integer BDT amount from various price formats (float, str, etc.)."""
    if price_raw is None:
        return None
    try:
        if isinstance(price_raw, (int, float)):
            val = int(round(float(price_raw)))
            return val if val > 0 else None
        s = str(price_raw).replace(",", "").replace("৳", "").replace("BDT", "").strip()
        m = re.search(r"(\d+(?:\.\d+)?)", s)
        if m:
            val = int(round(float(m.group(1))))
            return val if val > 0 else None
    except Exception:
        pass
    return None


async def fetch_shopify_products(
    base_url: str,
    store_name: str,
    max_pages: int = 2,
    limit: int = 100,
    timeout: float = 12.0,
) -> List[Dict[str, Any]]:
    """
    Harvests products from a Shopify store's public /products.json feed.
    Extracts individual variant combinations (e.g. RAM, Storage, Color) with respective prices.
    """
    harvested = []
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            feed_url = f"{base_url.rstrip('/')}/products.json?limit={limit}&page={page}"
            try:
                resp = await client.get(feed_url)
                if resp.status_code != 200:
                    break
                data = resp.json()
                products = data.get("products", [])
                if not products:
                    break

                for p in products:
                    base_title = p.get("title", "").strip()
                    handle = p.get("handle", "")
                    vendor = p.get("vendor", "").strip()
                    product_type = p.get("product_type", "").strip()
                    p_url = f"{base_url.rstrip('/')}/products/{handle}" if handle else base_url

                    images = p.get("images", [])
                    img_src = images[0].get("src") if images else None

                    variants = p.get("variants", [])
                    if not variants:
                        continue

                    for v in variants:
                        v_title = v.get("title", "")
                        price = clean_price_string(v.get("price"))
                        if not price or price <= 0:
                            continue

                        # Combine base title with variant title if informative (e.g. not 'Default Title')
                        if v_title and v_title.lower() != "default title":
                            full_title = f"{base_title} ({v_title})"
                        else:
                            full_title = base_title

                        harvested.append({
                            "store_name": store_name,
                            "title": full_title,
                            "base_title": base_title,
                            "variant_title": v_title if v_title.lower() != "default title" else "",
                            "price": price,
                            "original_price": clean_price_string(v.get("compare_at_price")) or price,
                            "url": p_url,
                            "image_url": img_src,
                            "vendor": vendor,
                            "sku": v.get("sku") or "",
                            "available": bool(v.get("available", True)),
                            "source_type": "shopify_feed",
                            "harvested_at": datetime.utcnow().isoformat(),
                        })

                if len(products) < limit:
                    break
            except Exception as e:
                logger.warning(f"Error fetching Shopify feed from {feed_url}: {e}")
                break

    return harvested


async def fetch_sitemap_urls(
    sitemap_url: str,
    max_urls: int = 50,
    timeout: float = 12.0,
) -> List[str]:
    """Fetches and parses a sitemap XML to extract individual product URLs."""
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True) as client:
        try:
            resp = await client.get(sitemap_url)
            if resp.status_code != 200:
                return []
            raw_xml = resp.text
            locs = re.findall(r"<loc>(https?://[^<]+)</loc>", raw_xml)
            # Filter to likely product URLs
            filtered = [
                u for u in locs
                if any(x in u for x in ("/product/", "/products/", "/item/"))
                and not any(x in u for x in ("sitemap", "category", "brand", "tag", "blog"))
            ]
            return filtered[:max_urls]
        except Exception as e:
            logger.warning(f"Error fetching sitemap {sitemap_url}: {e}")
            return []


async def parse_jsonld_from_url(
    url: str,
    store_name: str,
    client: httpx.AsyncClient,
) -> Optional[Dict[str, Any]]:
    """Fetches a product page and extracts Schema.org/Product JSON-LD metadata."""
    try:
        resp = await client.get(url, timeout=8.0)
        if resp.status_code != 200:
            return None

        json_ld_matches = re.findall(r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>', resp.text, re.DOTALL)
        for block in json_ld_matches:
            try:
                data = json.loads(block.strip())
                # Handle @graph or direct object
                items = data.get("@graph", [data]) if isinstance(data, dict) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    if item.get("@type") == "Product":
                        name = item.get("name")
                        if not name:
                            continue
                        offers = item.get("offers", {})
                        if isinstance(offers, list) and offers:
                            offers = offers[0]
                        price = clean_price_string(offers.get("price") if isinstance(offers, dict) else item.get("price"))
                        if not price or price <= 0:
                            continue

                        img = item.get("image")
                        if isinstance(img, list) and img:
                            img = img[0]
                        elif not isinstance(img, str):
                            img = None

                        brand = item.get("brand")
                        vendor = brand.get("name") if isinstance(brand, dict) else (brand or "")

                        return {
                            "store_name": store_name,
                            "title": name.strip(),
                            "base_title": name.strip(),
                            "variant_title": "",
                            "price": price,
                            "original_price": price,
                            "url": url,
                            "image_url": img,
                            "vendor": vendor,
                            "sku": item.get("sku") or "",
                            "available": "InStock" in str(offers.get("availability", "")),
                            "source_type": "jsonld_feed",
                            "harvested_at": datetime.utcnow().isoformat(),
                        }
            except Exception:
                continue
    except Exception as e:
        logger.debug(f"JSON-LD extraction failed for {url}: {e}")
    return None


async def harvest_sitemap_store(
    sitemap_url: str,
    store_name: str,
    max_products: int = 40,
    concurrency: int = 5,
) -> List[Dict[str, Any]]:
    """Harvests products by discovering URLs from sitemap and parsing JSON-LD in parallel."""
    urls = await fetch_sitemap_urls(sitemap_url, max_urls=max_products)
    if not urls:
        return []

    harvested = []
    sem = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, timeout=10.0, follow_redirects=True) as client:
        async def worker(u: str):
            async with sem:
                item = await parse_jsonld_from_url(u, store_name, client)
                if item:
                    harvested.append(item)

        await asyncio.gather(*[worker(u) for u in urls], return_exceptions=True)

    return harvested


async def run_full_feed_harvest(
    max_shopify_pages: int = 2,
    max_sitemap_items: int = 35,
) -> List[Dict[str, Any]]:
    """
    Executes a complete feed harvesting cycle across all configured retailers.
    Returns all collected, structured product offers.
    """
    all_items: List[Dict[str, Any]] = []

    # 1. Harvest Shopify feeds
    for sf in KNOWN_SHOPIFY_FEEDS:
        try:
            items = await fetch_shopify_products(
                base_url=sf["base_url"],
                store_name=sf["store_name"],
                max_pages=max_shopify_pages,
            )
            all_items.extend(items)
            logger.info(f"[Harvester] Ingested {len(items)} items from {sf['store_name']}")
        except Exception as e:
            logger.warning(f"[Harvester] Failed to harvest {sf['store_name']}: {e}")

    # 2. Harvest Sitemap JSON-LD feeds
    for sm in KNOWN_SITEMAP_FEEDS:
        try:
            items = await harvest_sitemap_store(
                sitemap_url=sm["sitemap_url"],
                store_name=sm["store_name"],
                max_products=max_sitemap_items,
            )
            all_items.extend(items)
            logger.info(f"[Harvester] Ingested {len(items)} JSON-LD items from {sm['store_name']}")
        except Exception as e:
            logger.warning(f"[Harvester] Failed to harvest {sm['store_name']}: {e}")

    logger.info(f"[Harvester] Total feed harvest completed: {len(all_items)} live retailer items.")
    return all_items


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("Testing Feed Harvester...")
    results = asyncio.run(run_full_feed_harvest(max_shopify_pages=1, max_sitemap_items=5))
    print(f"Successfully harvested {len(results)} items.")
    for r in results[:5]:
        print(f" - [{r['store_name']}] {r['title']} -> ৳{r['price']:,} ({r['url']})")
