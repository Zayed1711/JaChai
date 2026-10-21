"""
JaChai Shop Link Discovery Script (Web Search + SLM)
=====================================================
Reads all categorical CSV registries in registries/, extracting shop NAMES ONLY
(completely ignores existing URL columns in source CSVs).

Discovers:
  1. Official Website URL
  2. Facebook Page URL

Pipeline:
  Step 1: Web Scrape Search (Bing search scrape + direct base64 target URL decode)
  Step 2: Embedded Handle Extraction for F-commerce (@handle pattern)
  Step 3: Local SLM (Ollama qwen2.5:1.5b) inference fallback if still missing
  Step 4: Live HTTP validation (HEAD / GET status check < 400)

Outputs:
  - registries/verified_shops_registry.csv (Name, Category, Location, Website, Facebook Page)
  - registries/shops_errors.csv            (Name, Category, Location, Error)

Options:
  --resume    Skip shops that already exist in verified or error registries
"""

import base64
import csv
import json
import logging
import os
import re
import sys
import time
import urllib.parse
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

REGISTRIES_DIR = Path(__file__).resolve().parent
OUT_VERIFIED   = REGISTRIES_DIR / "verified_shops_registry.csv"
OUT_ERRORS     = REGISTRIES_DIR / "shops_errors.csv"

OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL   = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
OLLAMA_TIMEOUT = httpx.Timeout(connect=2.0, read=20.0, write=5.0, pool=2.0)

SEARCH_SLEEP     = 1.5   # Seconds between search queries
SHOP_SLEEP       = 1.0   # Seconds between shops
VALIDATE_TIMEOUT = 10.0  # HTTP status validation timeout

SKIP_DOMAINS = {
    "google.", "bing.", "yahoo.", "duckduckgo.", "wikipedia.", "wikimedia.",
    "youtube.", "twitter.", "x.com", "instagram.", "tiktok.", "linkedin.",
    "amazon.", "daraz.", "shajgoj.", "bikroy.", "prothomalo.", "bdnews24.",
    "daily-sun.", "thedailystar.", "sokalerkantho.", "jugantor.", "ittefaq.",
    "facebook.", "fb.com",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("discover_shops")
logging.getLogger("httpx").setLevel(logging.WARNING)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_http = httpx.Client(
    headers=HEADERS,
    follow_redirects=True,
    timeout=VALIDATE_TIMEOUT,
    verify=False,
)

def normalise_url(url: str) -> str:
    url = url.strip().rstrip("/")
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def is_facebook_url(url: str) -> bool:
    u = url.lower()
    return "facebook.com" in u or "fb.com" in u

def is_skip_domain(url: str) -> bool:
    u = url.lower()
    return any(d in u for d in SKIP_DOMAINS)

def clean_name(name: str) -> str:
    return re.sub(r"\s*\(@[^)]*\)", "", name).strip()

def extract_fb_handle(name: str) -> Optional[str]:
    m = re.search(r"\(@([^)]+)\)", name)
    if m:
        h = m.group(1).lstrip("@")
        return re.split(r"\.", h)[0]
    return None

def decode_bing_redirect_url(bing_url: str) -> Optional[str]:
    try:
        parsed = urllib.parse.urlparse(bing_url)
        qs = urllib.parse.parse_qs(parsed.query)
        u_val = qs.get("u", [""])[0]
        if u_val.startswith("a1"):
            b64 = u_val[2:]
            b64 += "=" * ((4 - len(b64) % 4) % 4)
            return base64.b64decode(b64).decode("utf-8", errors="ignore")
    except Exception:
        pass
    return None

def search_bing(query: str, max_results: int = 5) -> List[str]:
    url = "https://www.bing.com/search"
    params = {"q": query, "setlang": "en"}
    try:
        r = _http.get(url, params=params, timeout=15)
        time.sleep(SEARCH_SLEEP)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "lxml")
            decoded_urls = []
            for a in soup.select("li.b_algo h2 a"):
                href = a.get("href", "")
                if "/ck/a?!" in href:
                    decoded = decode_bing_redirect_url(href)
                    if decoded and decoded.startswith("http"):
                        decoded_urls.append(decoded)
                elif href.startswith("http"):
                    decoded_urls.append(href)
            return decoded_urls[:max_results]
    except Exception as exc:
        log.warning("Search failed for %r: %s", query, exc)
    return []

def validate_url(url: str) -> Tuple[bool, str]:
    url = normalise_url(url)
    if not url:
        return False, "empty URL"
    try:
        r = _http.head(url, timeout=VALIDATE_TIMEOUT)
        if r.status_code < 400:
            return True, ""
        r2 = _http.get(url, timeout=VALIDATE_TIMEOUT)
        if r2.status_code < 400:
            return True, ""
        return False, f"HTTP {r2.status_code}"
    except httpx.TimeoutException:
        return False, "timeout"
    except httpx.TooManyRedirects:
        return False, "too many redirects"
    except Exception as exc:
        return False, str(exc)[:80]

def find_website(name: str, category: str) -> Optional[str]:
    cn = clean_name(name)
    queries = [
        f'"{cn}" Bangladesh official website',
        f'"{cn}" site:*.com.bd OR site:*.store OR site:*.shop',
        f'{cn} Bangladesh online shopping store',
    ]
    for q in queries:
        for url in search_bing(q, max_results=5):
            if not is_facebook_url(url) and not is_skip_domain(url):
                return url
    return None

def find_facebook(name: str, category: str) -> Optional[str]:
    cn = clean_name(name)
    handle = extract_fb_handle(name)
    if handle:
        guessed = f"https://www.facebook.com/{handle}"
        ok, _ = validate_url(guessed)
        if ok:
            return guessed

    queries = [
        f'site:facebook.com "{cn}" Bangladesh',
        f'"{cn}" Bangladesh official facebook page',
    ]
    for q in queries:
        for url in search_bing(q, max_results=5):
            if is_facebook_url(url):
                parsed = urllib.parse.urlparse(url)
                parts = [p for p in parsed.path.strip("/").split("/") if p]
                if parts:
                    handle_part = parts[0]
                    if handle_part.lower() not in ("login", "search", "pages", "groups", "watch", "events"):
                        return f"https://www.facebook.com/{handle_part}"
    return None

def check_ollama_status() -> bool:
    try:
        r = httpx.get("http://localhost:11434/api/tags", timeout=2.0, verify=False)
        return r.status_code == 200
    except Exception:
        return False

def slm_infer_links(name: str, category: str) -> Tuple[Optional[str], Optional[str]]:
    cn = clean_name(name)
    prompt = (
        f'Shop: "{cn}", Category: "{category}" in Bangladesh. '
        f'Provide its official website URL and Facebook page URL in JSON: '
        f'{{"website": "https://...", "facebook": "https://www.facebook.com/..."}} '
        f'Use null if unknown.'
    )
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 120},
    }
    try:
        with httpx.Client(timeout=OLLAMA_TIMEOUT, verify=False) as client:
            r = client.post(OLLAMA_API_URL, json=payload)
        raw = r.json().get("response", "")
        m = re.search(r"\{.*?\}", raw, re.DOTALL)
        if not m:
            return None, None
        data = json.loads(m.group())
        site = data.get("website") or None
        fb = data.get("facebook") or None
        if site and (len(site) < 10 or "example" in site): site = None
        if fb and (len(fb) < 20 or "example" in fb): fb = None
        return site, fb
    except Exception as exc:
        log.debug("SLM inference error: %s", exc)
        return None, None

def read_csv_shops(path: Path) -> List[dict]:
    shops = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return shops
        for row in reader:
            raw = {k.strip(): (v or "").strip() for k, v in row.items() if k}
            name = raw.get("Name", "").strip()
            cat = raw.get("Category", "").strip()
            loc = raw.get("Location", "Bangladesh").strip() or "Bangladesh"
            if name:
                shops.append({"name": name, "category": cat, "location": loc, "_source": path.name})
    return shops

def load_all_shops() -> List[dict]:
    all_shops = []
    for p in sorted(REGISTRIES_DIR.glob("*.csv")):
        if p.stem in ("verified_shops_registry", "shops_errors"):
            continue
        s = read_csv_shops(p)
        log.info("  %-40s → %3d shops", p.name, len(s))
        all_shops.extend(s)
    return all_shops

def load_processed_names() -> set:
    done = set()
    for path in (OUT_VERIFIED, OUT_ERRORS):
        if path.exists():
            with open(path, newline="", encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    name = r.get("Name", "").strip()
                    if name:
                        done.add(name)
    return done

def append_verified(row: dict) -> None:
    write_hdr = not OUT_VERIFIED.exists()
    with open(OUT_VERIFIED, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Name", "Category", "Location", "Website", "Facebook Page"])
        if write_hdr:
            w.writeheader()
        w.writerow({
            "Name": row["name"],
            "Category": row["category"],
            "Location": row["location"],
            "Website": row["website"],
            "Facebook Page": row["facebook"],
        })

def append_error(row: dict) -> None:
    write_hdr = not OUT_ERRORS.exists()
    with open(OUT_ERRORS, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["Name", "Category", "Location", "Error"])
        if write_hdr:
            w.writeheader()
        w.writerow({
            "Name": row["name"],
            "Category": row["category"],
            "Location": row["location"],
            "Error": row["error"],
        })

def discover_shop(shop: dict, use_slm: bool) -> dict:
    name = shop["name"]
    cat = shop["category"]
    loc = shop["location"]

    website = find_website(name, cat)
    facebook = find_facebook(name, cat)

    if use_slm and (not website or not facebook):
        slm_site, slm_fb = slm_infer_links(name, cat)
        if not website and slm_site: website = slm_site
        if not facebook and slm_fb: facebook = slm_fb

    website = normalise_url(website) if website else ""
    facebook = normalise_url(facebook) if facebook else ""

    errors = []
    if website:
        ok, err = validate_url(website)
        if ok:
            log.info("  ✓ web: %s", website)
        else:
            log.warning("  ✗ web: %s [%s]", website, err)
            errors.append(f"website invalid ({err}): {website}")
            website = ""
    else:
        errors.append("website not found")

    if facebook:
        ok, err = validate_url(facebook)
        if ok:
            log.info("  ✓ fb : %s", facebook)
        else:
            log.warning("  ✗ fb : %s [%s]", facebook, err)
            errors.append(f"facebook invalid ({err}): {facebook}")
            facebook = ""
    else:
        errors.append("facebook not found")

    return {
        "name": name,
        "category": cat,
        "location": loc,
        "website": website,
        "facebook": facebook,
        "error": "; ".join(errors),
    }

def main():
    resume = "--resume" in sys.argv
    log.info("=" * 60)
    log.info("JaChai Shop Link Discovery (Bing Scrape + SLM)")
    log.info("=" * 60)

    use_slm = check_ollama_status()
    log.info("Ollama SLM: %s", "ONLINE (%s)" % OLLAMA_MODEL if use_slm else "OFFLINE (Search Scrape Only)")

    if resume:
        done = load_processed_names()
        log.info("Resume mode active: %d shops previously recorded", len(done))
    else:
        done = set()
        OUT_VERIFIED.unlink(missing_ok=True)
        OUT_ERRORS.unlink(missing_ok=True)

    shops = load_all_shops()
    total_raw = len(shops)
    if resume and done:
        shops = [s for s in shops if s["name"] not in done]

    total = len(shops)
    log.info("Total shops to process: %d (Skipped %d)", total, total_raw - total)
    log.info("-" * 60)

    verified_count = 0
    error_count = 0

    for i, shop in enumerate(shops, 1):
        log.info("[%d/%d] %s", i, total, shop["name"])
        res = discover_shop(shop, use_slm)

        if res["website"] or res["facebook"]:
            append_verified(res)
            verified_count += 1
        if res["error"]:
            append_error(res)
            error_count += 1

        if i < total:
            time.sleep(SHOP_SLEEP)

    log.info("-" * 60)
    log.info("Completed discovery run.")
    log.info("  Verified registry: %s (%d records)", OUT_VERIFIED, verified_count)
    log.info("  Error report     : %s (%d records)", OUT_ERRORS, error_count)
    log.info("=" * 60)

if __name__ == "__main__":
    main()
