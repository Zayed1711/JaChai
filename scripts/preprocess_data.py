#!/usr/bin/env python3
"""
JaChai E-Commerce Linguistic Router - Phase 1: Data Ingestion, Exploration, and Cleaning
----------------------------------------------------------------------------------------
Scans:
  1. e:/JaChai/Training
     - Bangla and Banglish E-Commerce Reviews Dataset (.zip)
     - pricerunner_aggregate.csv (.zip)
     - products-1000000.csv
  2. e:/JaChai/registries/*.csv (15 Bangladeshi Retail Category Registries)
  3. backend/bd_stores_registry.py (Domain vocabularies & keyword mappings)

Cleans, deduplicates, and standardizes data elements into JaChai's
15 Core E-Commerce Categories:
  1. mobile-gadgets
  2. laptops-pc
  3. fashion-apparel
  4. saree-boutiques
  5. grocery-snacks
  6. sportswear-gym
  7. cameras-photography
  8. bicycles-mtb
  9. cycles-evs
  10. home-appliances
  11. fine-jewelry
  12. fashion-jewelry
  13. sneakers-footwear
  14. watches-horology
  15. beauty-skincare

Outputs:
  - data/cleaned_catalog_corpus.json
  - data/cleaned_bangla_reviews.json
  - data/cleaned_category_vocab.json
"""

import os
import sys
import io
import re
import csv
import json
import zipfile
from typing import Dict, List, Any, Optional

sys.stdout.reconfigure(encoding="utf-8")

# Platform Base Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRAINING_DIR = os.path.join(BASE_DIR, "Training")
REGISTRIES_DIR = os.path.join(BASE_DIR, "registries")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 15 Core JaChai Platform Categories
CORE_CATEGORIES = [
    "mobile-gadgets",
    "laptops-pc",
    "fashion-apparel",
    "saree-boutiques",
    "grocery-snacks",
    "sportswear-gym",
    "cameras-photography",
    "bicycles-mtb",
    "cycles-evs",
    "home-appliances",
    "fine-jewelry",
    "fashion-jewelry",
    "sneakers-footwear",
    "watches-horology",
    "beauty-skincare",
]

RAW_CATEGORY_MAP = {
    "mobile phones": "mobile-gadgets",
    "digital cameras": "cameras-photography",
    "cpus": "laptops-pc",
    "tvs": "home-appliances",
    "fridge freezers": "home-appliances",
    "dishwashers": "home-appliances",
    "washing machines": "home-appliances",
    "freezers": "home-appliances",
    "fridges": "home-appliances",
    "microwaves": "home-appliances",
    "makeup": "beauty-skincare",
    "skincare": "beauty-skincare",
    "haircare": "beauty-skincare",
    "grooming tools": "beauty-skincare",
    "cameras & accessories": "cameras-photography",
    "smartwatches": "watches-horology",
    "cycling": "bicycles-mtb",
    "men's clothing": "fashion-apparel",
    "clothing & apparel": "fashion-apparel",
    "women's clothing": "fashion-apparel",
    "kids' clothing": "fashion-apparel",
    "fitness equipment": "sportswear-gym",
    "headphones & earbuds": "mobile-gadgets",
    "kitchen appliances": "home-appliances",
    "small appliances": "home-appliances",
    "shoes": "sneakers-footwear",
    "sneakers": "sneakers-footwear",
    "jewelry": "fashion-jewelry",
    "fine jewelry": "fine-jewelry",
    "watches": "watches-horology",
    "groceries": "grocery-snacks",
    "snacks": "grocery-snacks",
    "food & beverages": "grocery-snacks",
    "laptops": "laptops-pc",
    "computers": "laptops-pc",
    "computer accessories": "laptops-pc",
    "monitors": "laptops-pc",
    "smartphones": "mobile-gadgets",
    "tablets": "mobile-gadgets",
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    t = text.strip()
    t = re.sub(r"[\r\n\t]+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()

def map_to_core_category(raw_cat: str, title: str = "") -> Optional[str]:
    rc = (raw_cat or "").strip().lower()
    if rc in RAW_CATEGORY_MAP:
        return RAW_CATEGORY_MAP[rc]

    combined = f"{rc} {title}".lower()

    if any(k in combined for k in ["saree", "jamdani", "katan", "boutique", "shari", "georgette saree", "silk saree"]):
        return "saree-boutiques"
    if any(k in combined for k in ["gold chain", "22k", "24k gold", "diamond ring", "gold nose pin", "fine jewelry", "gold necklace"]):
        return "fine-jewelry"
    if any(k in combined for k in ["earring", "bracelet", "necklace", "choker", "jewelry", "anklet", "jhumka", "oxidised jewelry"]):
        return "fashion-jewelry"
    if any(k in combined for k in ["shoe", "sneaker", "boot", "sandal", "loafer", "apex", "bata", "slides", "footwear", "oxford shoe"]):
        return "sneakers-footwear"
    if any(k in combined for k in ["watch", "casio", "rolex", "smartwatch", "tissot", "curren", "horology", "chronograph", "seiko"]):
        return "watches-horology"
    if any(k in combined for k in ["ghee", "khati", "honey", "modhu", "oil", "tel", "rice", "dal", "masala", "snack", "nuts", "badam", "shorisha"]):
        return "grocery-snacks"
    if any(k in combined for k in ["jersey", "barca", "madrid", "gym", "sportswear", "dumbbell", "football kit", "activewear", "yoga mat", "home kit", "away kit"]):
        return "sportswear-gym"
    if any(k in combined for k in ["camera", "dslr", "canon 200d", "nikon", "sony alpha", "lens", "tripod", "gopro", "kit lens"]):
        return "cameras-photography"
    if any(k in combined for k in ["e-bike", "ebike", "electric scooter", "scooty", "ev", "takyon", "yadea"]):
        return "cycles-evs"
    if any(k in combined for k in ["bicycle", "mountain bike", "mtb", "cycle", "duranta", "veloce", "phoenix", "gear cycle"]):
        return "bicycles-mtb"
    if any(k in combined for k in ["ac", "air conditioner", "refrigerator", "fridge", "oven", "microwave", "washing machine", "blender", "iron", "wfc-3f5", "geyser", "kettle"]):
        return "home-appliances"
    if any(k in combined for k in ["ssd", "ram", "rtx", "gtx", "ryzen", "intel core", "laptop", "pc", "desktop", "macbook", "980 pro", "nvme"]):
        return "laptops-pc"
    if any(k in combined for k in ["iphone", "samsung galaxy", "redmi", "realme", "earbuds", "headphone", "charger", "power bank", "smart gadget", "gadgets"]):
        return "mobile-gadgets"
    if any(k in combined for k in ["panjabi", "shirt", "t-shirt", "polo", "jeans", "pant", "hoodie", "boxer", "underwear", "jacket", "curtis"]):
        return "fashion-apparel"
    if any(k in combined for k in ["cream", "lotion", "serum", "sunscreen", "shampoo", "facewash", "skincare", "cosmetics", "lipstick"]):
        return "beauty-skincare"

    return None

def process_bangla_reviews(zip_path: str) -> List[Dict[str, Any]]:
    records = []
    if not os.path.exists(zip_path):
        return records

    print(f"[*] Processing Bengali & Banglish Reviews from: {os.path.basename(zip_path)}")
    try:
        with zipfile.ZipFile(zip_path, "r") as outer:
            inner_name = "Bangla and Banglish E-Commerce Reviews Dataset for/BanglaBanglish_ABSA_Dataset.zip"
            if inner_name in outer.namelist():
                inner_bytes = outer.read(inner_name)
                with zipfile.ZipFile(io.BytesIO(inner_bytes), "r") as inner:
                    csv_name = "BanglaBanglish_ABSA_Dataset/2_preprocessed_data/preprocessed_dataset.csv"
                    content = inner.read(csv_name).decode("utf-8", errors="ignore")
                    reader = csv.DictReader(io.StringIO(content))
                    for row in reader:
                        orig = clean_text(row.get("original_text", ""))
                        cleaned = clean_text(row.get("cleaned_text", ""))
                        lang = row.get("language", "unknown").strip().lower()
                        if orig and len(orig) >= 5:
                            records.append({
                                "id": row.get("id"),
                                "original_text": orig,
                                "cleaned_text": cleaned,
                                "language": lang
                            })
    except Exception as e:
        print(f"[!] Error processing reviews: {e}")

    print(f"    Loaded {len(records)} cleaned Bengali/Banglish review instances.")
    return records

def process_pricerunner(zip_path: str) -> List[Dict[str, Any]]:
    records = []
    if not os.path.exists(zip_path):
        return records

    print(f"[*] Processing PriceRunner Aggregates from: {os.path.basename(zip_path)}")
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            content = z.read("pricerunner_aggregate.csv").decode("utf-8", errors="ignore")
            reader = csv.reader(io.StringIO(content))
            for row in reader:
                if len(row) >= 7:
                    variant_title = clean_text(row[1])
                    canonical_title = clean_text(row[4])
                    raw_cat = clean_text(row[6])
                    cat_hint = map_to_core_category(raw_cat, canonical_title)
                    if cat_hint:
                        records.append({
                            "variant_title": variant_title,
                            "canonical_title": canonical_title,
                            "raw_category": raw_cat,
                            "category_hint": cat_hint
                        })
    except Exception as e:
        print(f"[!] Error processing PriceRunner: {e}")

    print(f"    Loaded {len(records)} PriceRunner product queries.")
    return records

def process_products_csv(csv_path: str, max_rows: int = 150000) -> List[Dict[str, Any]]:
    records = []
    if not os.path.exists(csv_path):
        return records

    print(f"[*] Processing Catalog Products from: {os.path.basename(csv_path)} (Sampling up to {max_rows} rows)")
    try:
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                name = clean_text(row.get("Name", ""))
                brand = clean_text(row.get("Brand", ""))
                raw_cat = clean_text(row.get("Category", ""))
                desc = clean_text(row.get("Description", ""))
                cat_hint = map_to_core_category(raw_cat, name)
                if cat_hint and name:
                    records.append({
                        "name": name,
                        "brand": brand,
                        "raw_category": raw_cat,
                        "category_hint": cat_hint,
                        "description": desc[:150]
                    })
    except Exception as e:
        print(f"[!] Error processing products CSV: {e}")

    print(f"    Extracted {len(records)} catalog records mapped to core categories.")
    return records

def process_registries() -> Dict[str, List[Dict[str, Any]]]:
    """Extracts curated store names, categories, and specialty keywords from registries."""
    registry_data = {c: [] for c in CORE_CATEGORIES}
    csv_to_cat = {
        "appliances_and_electronics.csv": "home-appliances",
        "beauty_and_skincare.csv": "beauty-skincare",
        "bicycles_and_mtb.csv": "bicycles-mtb",
        "budget_jewelry_fcommerce.csv": "fashion-jewelry",
        "cameras_and_photography.csv": "cameras-photography",
        "cycles_and_evs.csv": "cycles-evs",
        "fashion_and_apparel.csv": "fashion-apparel",
        "fine_jewelry_and_gold.csv": "fine-jewelry",
        "grocery_and_snacks.csv": "grocery-snacks",
        "laptops_and_computers.csv": "laptops-pc",
        "mobile_phones_and_gadgets.csv": "mobile-gadgets",
        "saree_boutiques_fcommerce.csv": "saree-boutiques",
        "sneakers_and_footwear.csv": "sneakers-footwear",
        "sportswear_and_gym.csv": "sportswear-gym",
        "watches_and_horology.csv": "watches-horology"
    }

    if not os.path.exists(REGISTRIES_DIR):
        return registry_data

    print(f"[*] Processing Bangladeshi Category Registries from: {REGISTRIES_DIR}")
    for fname, cat in csv_to_cat.items():
        fpath = os.path.join(REGISTRIES_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = clean_text(row.get("Name") or row.get("Store Name") or row.get("name") or "")
                        if name:
                            registry_data[cat].append({
                                "store_name": name,
                                "category_hint": cat,
                                "location": clean_text(row.get("Location") or row.get("location") or "Bangladesh"),
                                "website": clean_text(row.get("Website") or row.get("website") or ""),
                                "facebook_page": clean_text(row.get("Facebook page") or row.get("facebook_page") or "")
                            })
            except Exception as e:
                print(f"[!] Error reading {fname}: {e}")

    total_stores = sum(len(v) for v in registry_data.values())
    print(f"    Loaded {total_stores} merchant stores across all 15 core categories.")
    return registry_data

def extract_vocab_from_backend() -> Dict[str, Dict[str, Any]]:
    """Imports rich domain keywords, Bangla terms, and templates from backend registry."""
    vocab = {}
    try:
        sys.path.insert(0, os.path.join(BASE_DIR, "backend"))
        from bd_stores_registry import CATEGORY_REGISTRY_MAP
        for cat_id, meta in CATEGORY_REGISTRY_MAP.items():
            if cat_id in CORE_CATEGORIES:
                vocab[cat_id] = {
                    "display_en": meta.get("display_en"),
                    "display_bn": meta.get("display_bn"),
                    "keywords": meta.get("keywords", []),
                    "default_query": meta.get("default_query"),
                    "model_templates": meta.get("model_templates", [])
                }
        print(f"[*] Extracted domain vocabularies for {len(vocab)} categories from backend registry.")
    except Exception as e:
        print(f"[!] Warning: Could not import bd_stores_registry: {e}")
    return vocab

def main():
    print("=" * 70)
    print("JaChai E-Commerce Linguistic Router: Phase 1 Preprocessing")
    print("=" * 70)

    # 1. Process Bangla/Banglish reviews
    reviews_zip = os.path.join(TRAINING_DIR, "Bangla and Banglish E-Commerce Reviews Dataset for.zip")
    reviews = process_bangla_reviews(reviews_zip)

    # 2. Process PriceRunner
    pricerunner_zip = os.path.join(TRAINING_DIR, "pricerunner_aggregate.csv.zip")
    pricerunner_items = process_pricerunner(pricerunner_zip)

    # 3. Process products-1000000.csv
    products_csv = os.path.join(TRAINING_DIR, "products-1000000.csv")
    products = process_products_csv(products_csv, max_rows=150000)

    # 4. Process Bangladeshi Merchant Registries (15 CSVs)
    registry_stores = process_registries()

    # 5. Extract category vocabularies from backend
    vocab = extract_vocab_from_backend()

    # Save outputs
    out_reviews_path = os.path.join(DATA_DIR, "cleaned_bangla_reviews.json")
    with open(out_reviews_path, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

    out_catalog_path = os.path.join(DATA_DIR, "cleaned_catalog_corpus.json")
    catalog_corpus = {
        "pricerunner": pricerunner_items,
        "products": products[:40000],
        "registries": registry_stores
    }
    with open(out_catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog_corpus, f, ensure_ascii=False, indent=2)

    out_vocab_path = os.path.join(DATA_DIR, "cleaned_category_vocab.json")
    with open(out_vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)

    print("\n--- Phase 1 Dataset Summary ---")
    print(f"Cleaned Reviews: {out_reviews_path} ({len(reviews):,} items)")
    print(f"Cleaned Catalog: {out_catalog_path} ({len(pricerunner_items) + len(catalog_corpus['products']):,} items)")
    print(f"Category Vocab:  {out_vocab_path} ({len(vocab)} categories)")
    print("=" * 70)

if __name__ == "__main__":
    main()
