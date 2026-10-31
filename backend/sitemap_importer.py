"""
JaChai Store Sitemap & robots.txt Ingestion Engine (backend/sitemap_importer.py)
Implements Pillar 5 of the Search Engine Architecture:
Directly discovers canonical product URLs from store XML sitemaps (Shopify, WooCommerce, OpenCart, etc.)
with zero guesswork and zero broken links.
"""

import argparse
import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import httpx

try:
    from database import SessionLocal
    from models import Product, StoreOffer
    from url_healer import fast_preflight_check, classify_soft_404
except ImportError:
    from .database import SessionLocal
    from .models import Product, StoreOffer
    from .url_healer import fast_preflight_check, classify_soft_404

logger = logging.getLogger("sitemap_importer")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Common sitemap paths by e-commerce platform
COMMON_SITEMAP_CANDIDATES = [
    "/sitemap_products_1.xml",   # Shopify standard
    "/product-sitemap.xml",      # Yoast SEO / WooCommerce
    "/product-sitemap1.xml",     # RankMath / WooCommerce
    "/sitemap.xml",              # Generic / Star Tech / Ryans
    "/sitemap/products.xml",     # Magento / Custom
]

# Registered stores with known product sitemaps
KNOWN_STORE_SITEMAPS: Dict[str, str] = {
    "custommacbd.com": "https://custommacbd.com/sitemap_products_1.xml",
    "kryinternational.com": "https://kryinternational.com/product-sitemap.xml",
    "dreamcycle.store": "https://dreamcycle.store/product-sitemap.xml",
    "motionview.com.bd": "https://motionview.com.bd/product-sitemap.xml",
    "dazzle.com.bd": "https://dazzle.com.bd/sitemap.xml",
    "sumashtech.com": "https://sumashtech.com/sitemap.xml",
}

# Negative path filters to ignore non-product URLs inside general sitemaps
NON_PRODUCT_SUBSTRINGS = (
    "/page/",
    "/blog/",
    "/category/",
    "/categories/",
    "/product-category/",
    "/cart",
    "/checkout",
    "/account",
    "/privacy-policy",
    "/terms",
    "/contact",
    "/about",
    "/faq",
    "/career",
    "/warranty",
    "/refund",
)


def is_likely_product_url(url: str) -> bool:
    """Heuristic filter to check if a URL inside a sitemap points to a single product."""
    path = (urlparse(url).path or "").lower()
    if any(bad in path for bad in NON_PRODUCT_SUBSTRINGS):
        return False
    if any(good in path for good in ("/product/", "/products/", "/item/", ".html", "-bd")):
        return True
    # If path has multiple segments and ends with a slug
    segments = [s for s in path.strip("/").split("/") if s]
    return len(segments) >= 1 and not path.endswith("/")


async def fetch_sitemap_urls(
    client: httpx.AsyncClient,
    sitemap_url: str,
    max_urls: int = 200,
) -> List[str]:
    """
    Downloads and parses an XML sitemap (or sitemap index).
    Returns list of discovered canonical product URLs.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36 (JaChai Spider/2.0)"
        ),
        "Accept": "application/xml,text/xml,*/*",
    }
    try:
        resp = await client.get(sitemap_url, headers=headers, timeout=10.0, follow_redirects=True)
        if resp.status_code != 200 or not resp.text:
            logger.warning(f"Failed to fetch sitemap: {sitemap_url} (HTTP {resp.status_code})")
            return []

        # Strip XML namespaces for simplified element matching
        xml_clean = re.sub(r' xmlns="[^"]+"', "", resp.text, count=1)
        root = ET.fromstring(xml_clean)

        discovered = []

        # 1. If this is a sitemap index (<sitemapindex><sitemap><loc>...), recurse into product sub-sitemaps
        if root.tag.endswith("sitemapindex"):
            for sitemap_node in root.findall("sitemap"):
                loc_node = sitemap_node.find("loc")
                if loc_node is not None and loc_node.text:
                    sub_url = loc_node.text.strip()
                    if "product" in sub_url.lower():
                        logger.info(f"Traversing sub-sitemap: {sub_url}")
                        sub_urls = await fetch_sitemap_urls(client, sub_url, max_urls=max_urls - len(discovered))
                        discovered.extend(sub_urls)
                        if len(discovered) >= max_urls:
                            break

        # 2. Standard urlset (<urlset><url><loc>...)
        for url_node in root.findall("url"):
            loc_node = url_node.find("loc")
            if loc_node is not None and loc_node.text:
                url = loc_node.text.strip()
                if is_likely_product_url(url):
                    discovered.append(url)
                    if len(discovered) >= max_urls:
                        break

        return discovered[:max_urls]
    except Exception as e:
        logger.error(f"Error parsing XML sitemap {sitemap_url}: {e}")
        return []


async def scan_and_validate_store_sitemap(
    store_name: str,
    sitemap_url: str,
    limit: int = 50,
    concurrency: int = 4,
) -> Dict[str, any]:
    """
    Extracts URLs from sitemap, then runs the fast pre-flight check on each candidate.
    Returns audit statistics: total parsed, alive, soft_404, dead.
    """
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, verify=False) as client:
        logger.info(f"Fetching sitemap for {store_name}: {sitemap_url}")
        urls = await fetch_sitemap_urls(client, sitemap_url, max_urls=limit)
        logger.info(f"Discovered {len(urls)} product candidate URLs from sitemap.")

        if not urls:
            return {"store": store_name, "total_found": 0, "alive": 0, "dead": 0, "soft_404": 0, "urls": []}

        sem = asyncio.Semaphore(concurrency)
        verified_results = []

        async def _check_url(u: str):
            async with sem:
                is_alive, status, final_url, snippet = await fast_preflight_check(client, u, timeout=4.0)
                is_soft = False
                if is_alive and snippet:
                    is_soft, _ = classify_soft_404(snippet)
                return {
                    "original_url": u,
                    "final_url": final_url,
                    "status_code": status,
                    "is_alive": is_alive and not is_soft,
                    "is_soft_404": is_soft,
                }

        tasks = [_check_url(u) for u in urls]
        checked = await asyncio.gather(*tasks)

        alive_count = sum(1 for c in checked if c["is_alive"])
        soft_count = sum(1 for c in checked if c["is_soft_404"])
        dead_count = sum(1 for c in checked if not c["is_alive"] and not c["is_soft_404"])

        return {
            "store": store_name,
            "total_found": len(urls),
            "alive": alive_count,
            "dead": dead_count,
            "soft_404": soft_count,
            "sample_verified": [c for c in checked if c["is_alive"]][:10],
        }


def main():
    parser = argparse.ArgumentParser(description="JaChai Store Sitemap Ingestion Tool")
    parser.add_argument("--store", type=str, default="all", help="Specific store domain or 'all'")
    parser.add_argument("--limit", type=int, default=20, help="Max URLs to validate per store")
    args = parser.parse_args()

    stores_to_scan = KNOWN_STORE_SITEMAPS
    if args.store != "all":
        match = {k: v for k, v in KNOWN_STORE_SITEMAPS.items() if args.store in k}
        if match:
            stores_to_scan = match
        else:
            stores_to_scan = {args.store: f"https://{args.store}/sitemap.xml"}

    async def _run():
        for s_name, s_url in stores_to_scan.items():
            print(f"\n==================================================")
            print(f"Scanning Sitemap: {s_name} -> {s_url}")
            print(f"==================================================")
            res = await scan_and_validate_store_sitemap(s_name, s_url, limit=args.limit)
            print(f"Total Found : {res['total_found']}")
            print(f"Alive & OK  : {res['alive']}")
            print(f"Soft-404    : {res['soft_404']}")
            print(f"Dead (404)  : {res['dead']}")
            if res["sample_verified"]:
                print("\nSample Verified Canonical URLs:")
                for s in res["sample_verified"][:5]:
                    print(f"  [HTTP {s['status_code']}] {s['final_url']}")

    asyncio.run(_run())


if __name__ == "__main__":
    main()
