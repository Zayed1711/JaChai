"""
Database Legacy Pollution Cleanup Script (backend/clean_legacy_db.py)
Removes legacy polluted product rows (IDs 12 to 53) created during early Milestone 5.0 tests,
and sanitizes all remaining offer URLs using current bd_stores_registry templates.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from database import SessionLocal
from models import Product, StoreOffer
from bd_stores_registry import build_store_target_url

def clean_database():
    db = SessionLocal()
    try:
        # 1. Delete legacy test products 12 to 53
        legacy_products = db.query(Product).filter(Product.id.between(12, 53)).all()
        print(f"Found {len(legacy_products)} legacy products in range 12..53 to remove.")
        for p in legacy_products:
            db.delete(p)
        db.commit()
        print("Legacy products 12..53 removed.")

        # 2. Inspect and sanitize remaining products
        remaining_products = db.query(Product).all()
        print(f"Sanitizing remaining {len(remaining_products)} products...")

        updated_offers = 0
        deleted_offers = 0

        for p in remaining_products:
            # Check offers
            seen_urls = set()
            for o in list(p.offers):
                target_url = o.target_url or ""
                store_name = o.store_name or ""

                # Fix old Pickaboo URLs
                if "pickaboo.com/search/result/?q=" in target_url:
                    q = target_url.split("pickaboo.com/search/result/?q=")[-1]
                    o.target_url = f"https://www.pickaboo.com/search-result/{q}"
                    updated_offers += 1

                # Fix old Ryans URLs
                if "ryanscomputers.com" in target_url:
                    o.target_url = target_url.replace("ryanscomputers.com", "ryans.com")
                    updated_offers += 1

                # Fix Star Tech loops if any remain
                if "startech.com.bd" in (o.target_url or "").lower() and "star tech" not in (o.store_name or "").lower():
                    # Rebuild target URL cleanly
                    new_url = build_store_target_url(o.store_name, p.title_en, p.category)
                    o.target_url = new_url
                    updated_offers += 1

                # Deduplicate identical URLs within same product
                if o.target_url in seen_urls:
                    print(f"Removing duplicate offer #{o.id} ({o.store_name}) for product #{p.id}")
                    db.delete(o)
                    deleted_offers += 1
                else:
                    seen_urls.add(o.target_url)

        db.commit()
        print(f"Sanitization complete: {updated_offers} offers updated, {deleted_offers} duplicate offers deleted.")

    except Exception as exc:
        db.rollback()
        print(f"Error during database cleanup: {exc}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()

