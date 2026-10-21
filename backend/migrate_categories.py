import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Product

def migrate():
    db = SessionLocal()
    prods = db.query(Product).all()
    updated = 0
    for p in prods:
        c = (p.category or "").strip()
        t = (p.title_en or "").lower()
        new_cat = c

        if c == "mobiles-computers":
            if any(w in t for w in ["laptop", "notebook", "desktop", "pc", "macbook", "ideapad", "ssd", "monitor"]):
                new_cat = "Laptops & PC"
            else:
                new_cat = "Mobiles & Gadgets"
        elif c == "fashion":
            if any(w in t for w in ["saree", "shari", "jamdani", "tangail"]):
                new_cat = "Saree & Boutiques"
            else:
                new_cat = "Fashion & Apparel"
        elif c == "sneakers-watches":
            if any(w in t for w in ["watch", "chrono", "chronometer"]):
                new_cat = "Watches & Horology"
            else:
                new_cat = "Sneakers & Shoes"
        elif c == "gadgets":
            new_cat = "Mobiles & Gadgets"
        elif c == "jewelleries":
            new_cat = "Fine Jewelry & Gold"
        elif c == "snacks-food":
            new_cat = "Grocery & Snacks"

        if new_cat != c:
            p.category = new_cat
            updated += 1

    db.commit()
    print(f"Migrated {updated} products to canonical categories.")
    
    # Print distinct categories
    cats = {p.category for p in db.query(Product).all()}
    print("Categories in DB now:", sorted(list(cats)))
    db.close()

if __name__ == "__main__":
    migrate()

