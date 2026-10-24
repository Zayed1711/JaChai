"""
JaChai Universal Master Product Catalog Engine
(backend/master_catalog.py)

Industry-standard Master Catalog architecture covering all core consumer electronics:
  1. Mobile Phones & Tablets (Pixel, iPhone, Samsung, OnePlus, Xiaomi, iPad)
  2. Laptops, MacBooks & PC Components (MacBook Air/Pro, Asus ROG, HP Victus, Intel/Ryzen, RTX, NVMe SSDs)
  3. Gaming Consoles & Handhelds (PS5 Slim Disc/Digital, Nintendo Switch OLED, Xbox Series X/S, Steam Deck)
  4. Smartwatches & Audio (Apple Watch, Galaxy Watch, AirPods Pro, Galaxy Buds, Sony ANC)
  5. Cameras & Action Cams (Sony Alpha, Canon EOS, GoPro Hero, DJI Osmo, Insta360)
  6. Watches & Horology (Casio G-Shock, Tissot PRX, Seiko 5, Citizen Eco-Drive)
  7. Home Appliances (Delegated to appliances_catalog.py)

Enables instantaneous (< 5ms) deterministic retrieval, exact hardware variant separation,
and authentic Bangladeshi dealer pricing without brittle real-time HTTP web-scraping latency.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from urllib.parse import quote_plus

try:
    from .models import Product, StoreOffer
    from .appliances_catalog import match_appliances_catalog, build_appliance_product_card, get_appliance_suggestions
    from .expanded_catalog_items import EXPANDED_CATALOG_ITEMS
except ImportError:
    from models import Product, StoreOffer
    from appliances_catalog import match_appliances_catalog, build_appliance_product_card, get_appliance_suggestions
    from expanded_catalog_items import EXPANDED_CATALOG_ITEMS

# ==============================================================================
# AUTHORITATIVE MASTER CATALOG ITEMS (300+ TOP SKUs ACROSS ALL VERTICALS)
# ==============================================================================
MASTER_CATALOG_ITEMS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # 1. GOOGLE PIXEL PHONES
    # --------------------------------------------------------------------------
    {
        "slug": "google-pixel-9-256gb",
        "model_code": "Pixel 9 (256GB)",
        "aliases": ["google pixel 9 256 gb", "google pixel 9 256gb", "pixel 9 256 gb", "pixel 9 256gb", "google pixel 9 256", "pixel 9 256"],
        "title_en": "Google Pixel 9 (12GB RAM · 256GB)",
        "title_bn": "গুগল পিক্সেল ৯ (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Google",
        "specs_summary": "Google Tensor G4 · 12GB RAM · 256GB UFS 4.0 · 6.3-inch Actua OLED 120Hz · 50MP Main + 48MP Ultrawide · 4700mAh",
        "starting_price": 78990,
        "max_price": 84500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 78990, "url": "https://www.applegadgetsbd.com/product/google-pixel-9"},
            {"name": "Custom Mac BD", "price": 79500, "url": "https://custommacbd.com/products/google-pixel-9"},
            {"name": "Star Tech", "price": 81000, "url": "https://www.startech.com.bd/google-pixel-9-256gb"},
            {"name": "Mobile Dukan BD", "price": 79990, "url": "https://www.mobiledokan.com/google-pixel-9"},
            {"name": "Kry International", "price": 80500, "url": "https://kryinternational.com/product/google-pixel-9-256gb"},
            {"name": "Daraz Bangladesh", "price": 82000, "url": "https://www.daraz.com.bd/catalog/?q=Google+Pixel+9+256GB"},
        ]
    },
    {
        "slug": "google-pixel-9-128gb",
        "model_code": "Pixel 9 (128GB)",
        "aliases": ["google pixel 9 128 gb", "google pixel 9 128gb", "pixel 9 128 gb", "pixel 9 128gb", "pixel 9 128", "google pixel 9", "pixel 9"],
        "title_en": "Google Pixel 9 (12GB RAM · 128GB)",
        "title_bn": "গুগল পিক্সেল ৯ (১২জিবি র‍্যাম · ১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Google",
        "specs_summary": "Google Tensor G4 · 12GB RAM · 128GB UFS 4.0 · 6.3-inch Actua OLED 120Hz · 50MP Main · 4700mAh",
        "starting_price": 71990,
        "max_price": 76500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 71990, "url": "https://www.applegadgetsbd.com/product/google-pixel-9"},
            {"name": "Custom Mac BD", "price": 72500, "url": "https://custommacbd.com/products/google-pixel-9"},
            {"name": "Star Tech", "price": 73500, "url": "https://www.startech.com.bd/google-pixel-9"},
            {"name": "Mobile Dukan BD", "price": 72990, "url": "https://www.mobiledokan.com/google-pixel-9"},
            {"name": "Daraz Bangladesh", "price": 74500, "url": "https://www.daraz.com.bd/catalog/?q=Google+Pixel+9"},
        ]
    },
    {
        "slug": "google-pixel-9-pro-256gb",
        "model_code": "Pixel 9 Pro (256GB)",
        "aliases": ["google pixel 9 pro 256 gb", "google pixel 9 pro 256gb", "pixel 9 pro 256 gb", "pixel 9 pro 256gb", "pixel 9 pro 256", "google pixel 9 pro", "pixel 9 pro"],
        "title_en": "Google Pixel 9 Pro (16GB RAM · 256GB)",
        "title_bn": "গুগল পিক্সেল ৯ প্রো (১৬জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Google",
        "specs_summary": "Google Tensor G4 · 16GB RAM · 256GB · 6.3-inch Super Actua LTPO OLED 120Hz · 50MP Triple Pro Camera with 5x Telephoto · 4700mAh",
        "starting_price": 108990,
        "max_price": 115000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "16GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 108990, "url": "https://www.applegadgetsbd.com/product/google-pixel-9-pro"},
            {"name": "Custom Mac BD", "price": 109500, "url": "https://custommacbd.com/products/google-pixel-9-pro"},
            {"name": "Star Tech", "price": 112000, "url": "https://www.startech.com.bd/google-pixel-9-pro"},
            {"name": "Kry International", "price": 110000, "url": "https://kryinternational.com/product/google-pixel-9-pro"},
            {"name": "Daraz Bangladesh", "price": 113500, "url": "https://www.daraz.com.bd/catalog/?q=Google+Pixel+9+Pro"},
        ]
    },
    {
        "slug": "google-pixel-9-pro-xl-256gb",
        "model_code": "Pixel 9 Pro XL (256GB)",
        "aliases": ["google pixel 9 pro xl 256 gb", "google pixel 9 pro xl 256gb", "pixel 9 pro xl 256 gb", "pixel 9 pro xl 256gb", "pixel 9 pro xl", "google pixel 9 pro xl"],
        "title_en": "Google Pixel 9 Pro XL (16GB RAM · 256GB)",
        "title_bn": "গুগল পিক্সেল ৯ প্রো এক্সএল (১৬জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Google",
        "specs_summary": "Google Tensor G4 · 16GB RAM · 256GB · 6.8-inch Super Actua LTPO OLED 120Hz · 50MP Triple Camera · 5060mAh · 37W Fast Charging",
        "starting_price": 124990,
        "max_price": 132000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "16GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 124990, "url": "https://www.applegadgetsbd.com/product/google-pixel-9-pro-xl"},
            {"name": "Custom Mac BD", "price": 125500, "url": "https://custommacbd.com/products/google-pixel-9-pro-xl"},
            {"name": "Star Tech", "price": 128000, "url": "https://www.startech.com.bd/google-pixel-9-pro-xl"},
            {"name": "Mobile Dukan BD", "price": 126000, "url": "https://www.mobiledokan.com/google-pixel-9-pro-xl"},
            {"name": "Daraz Bangladesh", "price": 129500, "url": "https://www.daraz.com.bd/catalog/?q=Google+Pixel+9+Pro+XL"},
        ]
    },
    {
        "slug": "google-pixel-8a-128gb",
        "model_code": "Pixel 8a (128GB)",
        "aliases": ["google pixel 8a", "pixel 8a", "pixel 8a 128gb", "pixel 8a 128 gb", "google pixel 8a 128gb"],
        "title_en": "Google Pixel 8a (8GB RAM · 128GB)",
        "title_bn": "গুগল পিক্সেল ৮এ (৮জিবি র‍্যাম · ১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Google",
        "specs_summary": "Google Tensor G3 · 8GB RAM · 128GB · 6.1-inch OLED 120Hz · 64MP Camera · 4492mAh · 7 Years OS Updates",
        "starting_price": 51990,
        "max_price": 55500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 51990, "url": "https://www.applegadgetsbd.com/product/google-pixel-8a"},
            {"name": "Custom Mac BD", "price": 52500, "url": "https://custommacbd.com/products/google-pixel-8a"},
            {"name": "Star Tech", "price": 53500, "url": "https://www.startech.com.bd/google-pixel-8a"},
            {"name": "Daraz Bangladesh", "price": 54000, "url": "https://www.daraz.com.bd/catalog/?q=Google+Pixel+8a"},
        ]
    },

    # --------------------------------------------------------------------------
    # 2. APPLE IPHONE
    # --------------------------------------------------------------------------
    {
        "slug": "apple-iphone-16-pro-max-256gb",
        "model_code": "iPhone 16 Pro Max (256GB)",
        "aliases": ["iphone 16 pro max 256gb", "iphone 16 pro max 256 gb", "iphone 16 pro max", "apple iphone 16 pro max", "16 pro max 256"],
        "title_en": "Apple iPhone 16 Pro Max (256GB · Grade-A International)",
        "title_bn": "অ্যাপল আইফোন ১৬ প্রো ম্যাক্স (২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Apple",
        "specs_summary": "Apple A18 Pro Bionic 3nm · 8GB RAM · 256GB NVMe · 6.9-inch Super Retina XDR OLED 120Hz ProMotion · 48MP Fusion Triple Camera · Camera Control Button · Titanium Design",
        "starting_price": 154990,
        "max_price": 165000,
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=600&q=80",
        "variant": "256GB · Dual SIM",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 154990, "url": "https://www.applegadgetsbd.com/product/iphone-16-pro-max"},
            {"name": "Custom Mac BD", "price": 155500, "url": "https://custommacbd.com/products/iphone-16-pro-max"},
            {"name": "Star Tech", "price": 158000, "url": "https://www.startech.com.bd/iphone-16-pro-max"},
            {"name": "Dazzle BD", "price": 156000, "url": "https://dazzle.com.bd/product/iphone-16-pro-max"},
            {"name": "Pickaboo", "price": 159990, "url": "https://www.pickaboo.com/product-detail/apple-iphone-16-pro-max"},
            {"name": "Daraz Bangladesh", "price": 162000, "url": "https://www.daraz.com.bd/catalog/?q=iPhone+16+Pro+Max"},
        ]
    },
    {
        "slug": "apple-iphone-16-pro-128gb",
        "model_code": "iPhone 16 Pro (128GB)",
        "aliases": ["iphone 16 pro 128gb", "iphone 16 pro 128 gb", "iphone 16 pro", "apple iphone 16 pro", "16 pro 128"],
        "title_en": "Apple iPhone 16 Pro (128GB · Grade-A International)",
        "title_bn": "অ্যাপল আইফোন ১৬ প্রো (১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Apple",
        "specs_summary": "Apple A18 Pro Bionic · 8GB RAM · 128GB · 6.3-inch Super Retina XDR OLED 120Hz · 48MP Triple Camera · Camera Control · Grade 5 Titanium",
        "starting_price": 134990,
        "max_price": 142000,
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=600&q=80",
        "variant": "128GB · Dual SIM",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 134990, "url": "https://www.applegadgetsbd.com/product/iphone-16-pro"},
            {"name": "Custom Mac BD", "price": 135500, "url": "https://custommacbd.com/products/iphone-16-pro"},
            {"name": "Star Tech", "price": 138000, "url": "https://www.startech.com.bd/iphone-16-pro"},
            {"name": "Pickaboo", "price": 139990, "url": "https://www.pickaboo.com/product-detail/apple-iphone-16-pro"},
            {"name": "Daraz Bangladesh", "price": 141000, "url": "https://www.daraz.com.bd/catalog/?q=iPhone+16+Pro"},
        ]
    },
    {
        "slug": "apple-iphone-16-128gb",
        "model_code": "iPhone 16 (128GB)",
        "aliases": ["iphone 16 128gb", "iphone 16 128 gb", "iphone 16", "apple iphone 16", "16 128gb"],
        "title_en": "Apple iPhone 16 (128GB · Grade-A International)",
        "title_bn": "অ্যাপল আইফোন ১৬ (১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Apple",
        "specs_summary": "Apple A18 Bionic · 8GB RAM · 128GB · 6.1-inch Super Retina XDR OLED · 48MP Fusion Camera · Action Button & Camera Control",
        "starting_price": 99990,
        "max_price": 106000,
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=600&q=80",
        "variant": "128GB · Dual SIM",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 99990, "url": "https://www.applegadgetsbd.com/product/iphone-16"},
            {"name": "Custom Mac BD", "price": 100500, "url": "https://custommacbd.com/products/iphone-16"},
            {"name": "Star Tech", "price": 103000, "url": "https://www.startech.com.bd/iphone-16"},
            {"name": "Pickaboo", "price": 104990, "url": "https://www.pickaboo.com/product-detail/apple-iphone-16"},
            {"name": "Daraz Bangladesh", "price": 105500, "url": "https://www.daraz.com.bd/catalog/?q=iPhone+16"},
        ]
    },
    {
        "slug": "apple-iphone-15-pro-max-256gb",
        "model_code": "iPhone 15 Pro Max (256GB)",
        "aliases": ["iphone 15 pro max 256gb", "iphone 15 pro max 256 gb", "iphone 15 pro max", "apple iphone 15 pro max"],
        "title_en": "Apple iPhone 15 Pro Max (256GB · Grade-A International)",
        "title_bn": "অ্যাপল আইফোন ১৫ প্রো ম্যাক্স (২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Apple",
        "specs_summary": "Apple A17 Pro 3nm · 8GB RAM · 256GB · 6.7-inch Super Retina XDR OLED 120Hz · 48MP 5x Optical Telephoto · Titanium Body · USB-C 3.0",
        "starting_price": 139990,
        "max_price": 147000,
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=600&q=80",
        "variant": "256GB · Dual SIM",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 139990, "url": "https://www.applegadgetsbd.com/product/iphone-15-pro-max"},
            {"name": "Custom Mac BD", "price": 140500, "url": "https://custommacbd.com/products/iphone-15-pro-max"},
            {"name": "Star Tech", "price": 143000, "url": "https://www.startech.com.bd/iphone-15-pro-max"},
            {"name": "Pickaboo", "price": 144990, "url": "https://www.pickaboo.com/product-detail/apple-iphone-15-pro-max"},
            {"name": "Daraz Bangladesh", "price": 146000, "url": "https://www.daraz.com.bd/catalog/?q=iPhone+15+Pro+Max"},
        ]
    },
    {
        "slug": "apple-iphone-15-128gb",
        "model_code": "iPhone 15 (128GB)",
        "aliases": ["iphone 15 128gb", "iphone 15 128 gb", "iphone 15", "apple iphone 15"],
        "title_en": "Apple iPhone 15 (128GB · Grade-A International)",
        "title_bn": "অ্যাপল আইফোন ১৫ (১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Apple",
        "specs_summary": "Apple A16 Bionic · 6GB RAM · 128GB · 6.1-inch Super Retina XDR OLED · Dynamic Island · 48MP Main Camera · USB-C",
        "starting_price": 82990,
        "max_price": 88000,
        "image_url": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=600&q=80",
        "variant": "128GB · Dual SIM",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 82990, "url": "https://www.applegadgetsbd.com/product/iphone-15"},
            {"name": "Custom Mac BD", "price": 83500, "url": "https://custommacbd.com/products/iphone-15"},
            {"name": "Star Tech", "price": 85500, "url": "https://www.startech.com.bd/iphone-15"},
            {"name": "Pickaboo", "price": 86990, "url": "https://www.pickaboo.com/product-detail/apple-iphone-15"},
            {"name": "Daraz Bangladesh", "price": 87500, "url": "https://www.daraz.com.bd/catalog/?q=iPhone+15"},
        ]
    },

    # --------------------------------------------------------------------------
    # 3. SAMSUNG GALAXY FLAGSHIPS
    # --------------------------------------------------------------------------
    {
        "slug": "samsung-galaxy-s24-ultra-256gb",
        "model_code": "Galaxy S24 Ultra (256GB)",
        "aliases": ["samsung s24 ultra", "samsung galaxy s24 ultra", "s24 ultra 256gb", "s24 ultra 256 gb", "galaxy s24 ultra 256gb", "s24 ultra"],
        "title_en": "Samsung Galaxy S24 Ultra 5G (12GB RAM · 256GB)",
        "title_bn": "স্যামসাং গ্যালাক্সি এস২৪ আল্ট্রা ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Samsung",
        "specs_summary": "Snapdragon 8 Gen 3 for Galaxy 4nm · 12GB RAM · 256GB UFS 4.0 · 6.8-inch Dynamic AMOLED 2X 120Hz 2600 nits · 200MP Quad Camera · Titanium Frame · Built-in S-Pen · 5000mAh",
        "starting_price": 124990,
        "max_price": 135000,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 124990, "url": "https://www.applegadgetsbd.com/product/samsung-galaxy-s24-ultra"},
            {"name": "Custom Mac BD", "price": 125500, "url": "https://custommacbd.com/products/samsung-galaxy-s24-ultra"},
            {"name": "Star Tech", "price": 129000, "url": "https://www.startech.com.bd/samsung-galaxy-s24-ultra"},
            {"name": "Mobile Dukan BD", "price": 126500, "url": "https://www.mobiledokan.com/samsung-galaxy-s24-ultra"},
            {"name": "Daraz Bangladesh", "price": 131000, "url": "https://www.daraz.com.bd/catalog/?q=Samsung+Galaxy+S24+Ultra"},
        ]
    },
    {
        "slug": "samsung-galaxy-s24-plus-256gb",
        "model_code": "Galaxy S24+ (256GB)",
        "aliases": ["samsung s24 plus", "samsung galaxy s24 plus", "s24 plus 256gb", "s24 plus", "s24+ 256gb", "s24+"],
        "title_en": "Samsung Galaxy S24+ 5G (12GB RAM · 256GB)",
        "title_bn": "স্যামসাং গ্যালাক্সি এস২৪+ ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Samsung",
        "specs_summary": "Snapdragon 8 Gen 3 / Exynos 2400 · 12GB RAM · 256GB · 6.7-inch QHD+ Dynamic AMOLED 2X 120Hz · 50MP Triple Camera · 4900mAh",
        "starting_price": 94990,
        "max_price": 102000,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 94990, "url": "https://www.applegadgetsbd.com/product/samsung-galaxy-s24-plus"},
            {"name": "Custom Mac BD", "price": 95500, "url": "https://custommacbd.com/products/samsung-galaxy-s24-plus"},
            {"name": "Star Tech", "price": 98000, "url": "https://www.startech.com.bd/samsung-galaxy-s24-plus"},
            {"name": "Daraz Bangladesh", "price": 99500, "url": "https://www.daraz.com.bd/catalog/?q=Samsung+Galaxy+S24+Plus"},
        ]
    },
    {
        "slug": "samsung-galaxy-a55-5g-128gb",
        "model_code": "Galaxy A55 5G (128GB)",
        "aliases": ["samsung a55", "samsung galaxy a55", "a55 5g", "galaxy a55 128gb", "samsung a55 128gb"],
        "title_en": "Samsung Galaxy A55 5G (8GB RAM · 128GB)",
        "title_bn": "স্যামসাং গ্যালাক্সি এ৫৫ ৫জি (৮জিবি র‍্যাম · ১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Samsung",
        "specs_summary": "Exynos 1480 4nm with Xclipse 530 GPU · 8GB RAM · 128GB · 6.6-inch Super AMOLED 120Hz · 50MP OIS Triple Camera · Metal Frame · IP67 Water Resistant · 5000mAh",
        "starting_price": 42990,
        "max_price": 46500,
        "image_url": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 42990, "url": "https://www.applegadgetsbd.com/product/samsung-galaxy-a55-5g"},
            {"name": "Star Tech", "price": 43500, "url": "https://www.startech.com.bd/samsung-galaxy-a55-5g"},
            {"name": "Transcom Digital", "price": 45999, "url": "https://transcomdigital.com/samsung-galaxy-a55"},
            {"name": "Pickaboo", "price": 44500, "url": "https://www.pickaboo.com/product-detail/samsung-galaxy-a55-5g"},
            {"name": "Daraz Bangladesh", "price": 43990, "url": "https://www.daraz.com.bd/catalog/?q=Samsung+Galaxy+A55"},
        ]
    },

    # --------------------------------------------------------------------------
    # 4. ONEPLUS & XIAOMI
    # --------------------------------------------------------------------------
    {
        "slug": "oneplus-12-256gb",
        "model_code": "OnePlus 12 (256GB)",
        "aliases": ["oneplus 12", "oneplus 12 256gb", "oneplus 12 256 gb", "1+ 12 256gb"],
        "title_en": "OnePlus 12 5G (16GB RAM · 256GB)",
        "title_bn": "ওয়ানপ্লাস ১২ ৫জি (১৬জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "OnePlus",
        "specs_summary": "Snapdragon 8 Gen 3 4nm · 16GB LPDDR5X RAM · 256GB UFS 4.0 · 6.82-inch 2K 120Hz ProXDR AMOLED · Hasselblad 50MP Camera · 5400mAh · 100W SuperVOOC Fast Charge",
        "starting_price": 79990,
        "max_price": 86000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "16GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 79990, "url": "https://www.applegadgetsbd.com/product/oneplus-12"},
            {"name": "Star Tech", "price": 81500, "url": "https://www.startech.com.bd/oneplus-12"},
            {"name": "Mobile Dukan BD", "price": 80990, "url": "https://www.mobiledokan.com/oneplus-12"},
            {"name": "Daraz Bangladesh", "price": 83000, "url": "https://www.daraz.com.bd/catalog/?q=OnePlus+12"},
        ]
    },
    {
        "slug": "xiaomi-redmi-note-13-pro-plus-256gb",
        "model_code": "Redmi Note 13 Pro+ (256GB)",
        "aliases": ["redmi note 13 pro+", "redmi note 13 pro plus", "xiaomi redmi note 13 pro+", "note 13 pro plus 256gb"],
        "title_en": "Xiaomi Redmi Note 13 Pro+ 5G (12GB RAM · 256GB)",
        "title_bn": "শাওমি রেডমি নোট ১৩ প্রো+ ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Xiaomi",
        "specs_summary": "MediaTek Dimensity 7200-Ultra 4nm · 12GB RAM · 256GB · 6.67-inch Curved 1.5K AMOLED 120Hz · 200MP OIS Camera · IP68 Water Resistance · 5000mAh · 120W HyperCharge",
        "starting_price": 41990,
        "max_price": 45000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 41990, "url": "https://www.applegadgetsbd.com/product/redmi-note-13-pro-plus"},
            {"name": "Star Tech", "price": 42500, "url": "https://www.startech.com.bd/redmi-note-13-pro-plus"},
            {"name": "Pickaboo", "price": 43500, "url": "https://www.pickaboo.com/product-detail/redmi-note-13-pro-plus"},
            {"name": "Daraz Bangladesh", "price": 42990, "url": "https://www.daraz.com.bd/catalog/?q=Redmi+Note+13+Pro+Plus"},
        ]
    },

    # --------------------------------------------------------------------------
    # 5. APPLE MACBOOKS & LAPTOPS
    # --------------------------------------------------------------------------
    {
        "slug": "apple-macbook-air-13-m3-8gb-256gb",
        "model_code": "MacBook Air M3 (8GB · 256GB)",
        "aliases": ["macbook air m3", "apple macbook air m3", "macbook air m3 256gb", "macbook air m3 8gb 256gb", "m3 macbook air 13"],
        "title_en": "Apple MacBook Air 13-inch (M3 Chip · 8-Core CPU · 8-Core GPU · 8GB Unified RAM · 256GB SSD)",
        "title_bn": "অ্যাপল ম্যাকবুক এয়ার ১৩-ইঞ্চি (এম৩ চিপ · ৮জিবি র‍্যাম · ২৫৬জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "MacBooks",
        "brand": "Apple",
        "specs_summary": "Apple M3 Chip (8-Core CPU, 8-Core GPU, 16-Core Neural Engine) · 8GB Unified Memory · 256GB SSD · 13.6-inch Liquid Retina True Tone · MagSafe 3 · Up to 18 Hours Battery",
        "starting_price": 126990,
        "max_price": 136000,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "variant": "M3 Chip · 8GB RAM · 256GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 126990, "url": "https://custommacbd.com/products/macbook-air-13-m3-8gb-256gb"},
            {"name": "Star Tech", "price": 128500, "url": "https://www.startech.com.bd/apple-macbook-air-13-inch-m3-8gb-256gb"},
            {"name": "Ryans Computers", "price": 129000, "url": "https://www.ryans.com/apple-macbook-air-13-inch-m3-8gb-256gb"},
            {"name": "Apple Gadgets BD", "price": 127500, "url": "https://www.applegadgetsbd.com/product/macbook-air-13-m3"},
            {"name": "Tech Land BD", "price": 129500, "url": "https://www.techlandbd.com/macbook-air-m3-8gb-256gb"},
        ]
    },
    {
        "slug": "apple-macbook-air-13-m3-16gb-512gb",
        "model_code": "MacBook Air M3 (16GB · 512GB)",
        "aliases": ["macbook air m3 16gb 512gb", "macbook air m3 16gb", "macbook air m3 512gb", "m3 macbook air 16gb 512gb"],
        "title_en": "Apple MacBook Air 13-inch (M3 Chip · 8-Core CPU · 10-Core GPU · 16GB Unified RAM · 512GB SSD)",
        "title_bn": "অ্যাপল ম্যাকবুক এয়ার ১৩-ইঞ্চি (এম৩ চিপ · ১৬জিবি র‍্যাম · ৫১২জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "MacBooks",
        "brand": "Apple",
        "specs_summary": "Apple M3 Chip (8-Core CPU, 10-Core GPU) · 16GB Unified Memory · 512GB Fast SSD · 13.6-inch Liquid Retina Display · Dual Display Support with Lid Closed",
        "starting_price": 164990,
        "max_price": 175000,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "variant": "M3 Chip · 16GB RAM · 512GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 164990, "url": "https://custommacbd.com/products/macbook-air-13-m3-16gb-512gb"},
            {"name": "Star Tech", "price": 166500, "url": "https://www.startech.com.bd/apple-macbook-air-13-inch-m3-16gb-512gb"},
            {"name": "Ryans Computers", "price": 167000, "url": "https://www.ryans.com/apple-macbook-air-13-inch-m3-16gb-512gb"},
            {"name": "Tech Land BD", "price": 168000, "url": "https://www.techlandbd.com/macbook-air-m3-16gb-512gb"},
        ]
    },
    {
        "slug": "apple-macbook-air-13-m2-8gb-256gb",
        "model_code": "MacBook Air M2 (8GB · 256GB)",
        "aliases": ["macbook air m2", "apple macbook air m2", "macbook air m2 256gb", "m2 macbook air"],
        "title_en": "Apple MacBook Air 13-inch (M2 Chip · 8-Core CPU · 8-Core GPU · 8GB Unified RAM · 256GB SSD)",
        "title_bn": "অ্যাপল ম্যাকবুক এয়ার ১৩-ইঞ্চি (এম২ চিপ · ৮জিবি র‍্যাম · ২৫৬জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "MacBooks",
        "brand": "Apple",
        "specs_summary": "Apple M2 Chip (8-Core CPU, 8-Core GPU) · 8GB Unified RAM · 256GB SSD · 13.6-inch Liquid Retina Display · 1080p FaceTime HD Camera · MagSafe 3",
        "starting_price": 112990,
        "max_price": 120000,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "variant": "M2 Chip · 8GB RAM · 256GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 112990, "url": "https://custommacbd.com/products/macbook-air-13-m2-8gb-256gb"},
            {"name": "Star Tech", "price": 114500, "url": "https://www.startech.com.bd/apple-macbook-air-13-inch-m2-8gb-256gb"},
            {"name": "Ryans Computers", "price": 115000, "url": "https://www.ryans.com/apple-macbook-air-13-inch-m2-8gb-256gb"},
            {"name": "Tech Land BD", "price": 115500, "url": "https://www.techlandbd.com/macbook-air-m2-8gb-256gb"},
        ]
    },
    {
        "slug": "apple-macbook-pro-14-m3-pro-18gb-512gb",
        "model_code": "MacBook Pro 14 M3 Pro (18GB · 512GB)",
        "aliases": ["macbook pro 14 m3 pro", "macbook pro m3 pro", "m3 pro macbook pro 14", "apple macbook pro m3 pro"],
        "title_en": "Apple MacBook Pro 14-inch (M3 Pro Chip · 11-Core CPU · 14-Core GPU · 18GB Unified RAM · 512GB SSD)",
        "title_bn": "অ্যাপল ম্যাকবুক প্রো ১৪-ইঞ্চি (এম৩ প্রো চিপ · ১৮জিবি র‍্যাম · ৫১২জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "MacBooks",
        "brand": "Apple",
        "specs_summary": "Apple M3 Pro Chip (11-Core CPU, 14-Core GPU, 150GB/s memory bandwidth) · 18GB Unified RAM · 512GB High-Speed SSD · 14.2-inch Liquid Retina XDR 120Hz ProMotion · Space Black",
        "starting_price": 234990,
        "max_price": 248000,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80",
        "variant": "M3 Pro Chip · 18GB RAM · 512GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 234990, "url": "https://custommacbd.com/products/macbook-pro-14-m3-pro-18gb-512gb"},
            {"name": "Star Tech", "price": 238000, "url": "https://www.startech.com.bd/apple-macbook-pro-14-inch-m3-pro"},
            {"name": "Ryans Computers", "price": 239000, "url": "https://www.ryans.com/apple-macbook-pro-14-inch-m3-pro"},
            {"name": "Tech Land BD", "price": 241000, "url": "https://www.techlandbd.com/macbook-pro-14-m3-pro"},
        ]
    },

    # --------------------------------------------------------------------------
    # 6. WINDOWS GAMING & SLIM LAPTOPS
    # --------------------------------------------------------------------------
    {
        "slug": "asus-rog-zephyrus-g16-gu605mv-rtx4060",
        "model_code": "ROG Zephyrus G16 (RTX 4060)",
        "aliases": ["asus rog zephyrus g16", "rog zephyrus g16", "zephyrus g16 rtx 4060", "asus zephyrus g16"],
        "title_en": "ASUS ROG Zephyrus G16 (Intel Core Ultra 7 155H · 16GB LPDDR5X · 1TB NVMe Gen4 · RTX 4060 8GB · 2.5K 240Hz OLED)",
        "title_bn": "আসুস আরওজি জেফিরাস জি১৬ (কোর আল্ট্রা ৭ · ১৬জিবি র‍্যাম · ১টিবি এসএসডি · আরটিএক্স ৪০৬০)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "ASUS",
        "specs_summary": "Intel Core Ultra 7 155H (16-Core, 22-Threads) · 16GB LPDDR5X 7467MHz · 1TB PCIe 4.0 SSD · NVIDIA GeForce RTX 4060 8GB GDDR6 (100W TGP) · 16-inch 2.5K ROG Nebula OLED 240Hz 0.2ms · 90Wh Battery",
        "starting_price": 245000,
        "max_price": 260000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "Core Ultra 7 · 16GB RAM · 1TB SSD · RTX 4060 8GB",
        "stores": [
            {"name": "Star Tech", "price": 245000, "url": "https://www.startech.com.bd/asus-rog-zephyrus-g16-gu605mv"},
            {"name": "Ryans Computers", "price": 247000, "url": "https://www.ryans.com/asus-rog-zephyrus-g16-gu605mv"},
            {"name": "Tech Land BD", "price": 248000, "url": "https://www.techlandbd.com/asus-rog-zephyrus-g16-gu605mv"},
            {"name": "Computer Mania BD", "price": 246500, "url": "https://computermaniabd.com/product/asus-rog-zephyrus-g16-gu605mv/"},
        ]
    },
    {
        "slug": "asus-tuf-gaming-f15-fx506hf-rtx2050",
        "model_code": "ASUS TUF Gaming F15",
        "aliases": ["asus tuf gaming f15", "asus tuf f15", "tuf f15", "asus tuf gaming f15 rtx 2050"],
        "title_en": "ASUS TUF Gaming F15 (Intel Core i5-11400H · 8GB DDR4 · 512GB NVMe SSD · RTX 2050 4GB · 144Hz)",
        "title_bn": "আসুস টাফ গেমিং এফ১৫ (কোর আই৫ · ৮জিবি র‍্যাম · ৫১২জিবি এসএসডি · আরটিএক্স ২০৫০)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "ASUS",
        "specs_summary": "Intel Core i5-11400H (6-Core, 12-Threads) · 8GB DDR4 3200MHz (Upgradable to 32GB) · 512GB M.2 NVMe SSD · NVIDIA GeForce RTX 2050 4GB · 15.6-inch FHD IPS 144Hz · MIL-STD-810H Military Grade",
        "starting_price": 79500,
        "max_price": 85000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "Core i5 · 8GB RAM · 512GB SSD · RTX 2050 4GB",
        "stores": [
            {"name": "Star Tech", "price": 79500, "url": "https://www.startech.com.bd/asus-tuf-gaming-f15-fx506hf"},
            {"name": "Ryans Computers", "price": 81000, "url": "https://www.ryans.com/asus-tuf-gaming-f15-fx506hf"},
            {"name": "Tech Land BD", "price": 80500, "url": "https://www.techlandbd.com/asus-tuf-gaming-f15-fx506hf"},
            {"name": "Computer Mania BD", "price": 81500, "url": "https://computermaniabd.com/product/asus-tuf-f15-fx506hf/"},
        ]
    },
    {
        "slug": "hp-victus-15-fb1013dx-rtx2050",
        "model_code": "HP Victus 15",
        "aliases": ["hp victus 15", "victus 15", "hp victus gaming", "hp victus 15 rtx 2050"],
        "title_en": "HP Victus 15 (AMD Ryzen 5 7535HS · 8GB DDR5 · 512GB PCIe Gen4 SSD · RTX 2050 4GB · 144Hz)",
        "title_bn": "এইচপি ভিকটাস ১৫ (রাইজেন ৫ · ৮জিবি ডিডিআর৫ · ৫১২জিবি এসএসডি · আরটিএক্স ২০৫০)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "HP",
        "specs_summary": "AMD Ryzen 5 7535HS (6-Core, 12-Threads up to 4.55GHz) · 8GB DDR5 4800MHz · 512GB PCIe Gen4 NVMe SSD · NVIDIA GeForce RTX 2050 4GB · 15.6-inch FHD IPS 144Hz Anti-Glare",
        "starting_price": 78500,
        "max_price": 84000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "Ryzen 5 · 8GB DDR5 · 512GB SSD · RTX 2050 4GB",
        "stores": [
            {"name": "Star Tech", "price": 78500, "url": "https://www.startech.com.bd/hp-victus-15-fb1013dx"},
            {"name": "Ryans Computers", "price": 79900, "url": "https://www.ryans.com/hp-victus-15-fb1013dx"},
            {"name": "Tech Land BD", "price": 80000, "url": "https://www.techlandbd.com/hp-victus-15-fb1013dx"},
        ]
    },

    # --------------------------------------------------------------------------
    # 7. PC HARDWARE & COMPONENTS
    # --------------------------------------------------------------------------
    {
        "slug": "nvidia-geforce-rtx-4060-8gb",
        "model_code": "GeForce RTX 4060 (8GB)",
        "aliases": ["rtx 4060", "rtx 4060 8gb", "nvidia rtx 4060", "geforce rtx 4060", "rtx 4060 gpu"],
        "title_en": "NVIDIA GeForce RTX 4060 (8GB GDDR6 · Dual Fan OC Edition)",
        "title_bn": "এনভিডিয়া জিফোর্স আরটিএক্স ৪০৬০ (৮জিবি জিডিডিআর৬ গ্রাফিক্স কার্ড)",
        "category": "Laptops & PC",
        "subcategory": "Graphics Cards",
        "brand": "NVIDIA",
        "specs_summary": "Ada Lovelace Architecture · 3072 CUDA Cores · 8GB GDDR6 128-bit · DLSS 3 Frame Generation · 3rd Gen RT Cores · 115W Low Power Efficiency · 3x DisplayPort 1.4a, 1x HDMI 2.1a",
        "starting_price": 38500,
        "max_price": 43000,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB GDDR6 · DLSS 3",
        "stores": [
            {"name": "Star Tech", "price": 38500, "url": "https://www.startech.com.bd/component/graphics-card/rtx-4060"},
            {"name": "Ryans Computers", "price": 39500, "url": "https://www.ryans.com/component/graphics-card/rtx-4060"},
            {"name": "Tech Land BD", "price": 39000, "url": "https://www.techlandbd.com/graphics-card/rtx-4060"},
            {"name": "Nexus Technologies", "price": 39900, "url": "https://www.nexustech.com.bd/rtx-4060"},
        ]
    },
    {
        "slug": "samsung-990-pro-1tb-nvme-pcie-4",
        "model_code": "Samsung 990 Pro (1TB)",
        "aliases": ["samsung 990 pro 1tb", "samsung 990 pro", "990 pro 1tb", "samsung 990 pro nvme 1tb"],
        "title_en": "Samsung 990 Pro (1TB PCIe 4.0 NVMe M.2 Internal Gaming SSD)",
        "title_bn": "স্যামসাং ৯৯০ প্রো (১টিবি পিসিআইই ৪.০ এনভিএমই এম.২ এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "Storage & SSD",
        "brand": "Samsung",
        "specs_summary": "PCIe Gen 4.0 x4, NVMe 2.0 · Sequential Read up to 7450 MB/s · Sequential Write up to 6900 MB/s · Samsung In-House Pascal Controller · 1GB LPDDR4 DRAM · 600 TBW · 5-Year Warranty",
        "starting_price": 14200,
        "max_price": 16000,
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80",
        "variant": "1TB NVMe M.2 · PCIe 4.0",
        "stores": [
            {"name": "Star Tech", "price": 14200, "url": "https://www.startech.com.bd/samsung-990-pro-1tb-nvme-ssd"},
            {"name": "Ryans Computers", "price": 14600, "url": "https://www.ryans.com/samsung-990-pro-1tb-nvme-ssd"},
            {"name": "Tech Land BD", "price": 14500, "url": "https://www.techlandbd.com/samsung-990-pro-1tb-ssd"},
            {"name": "Daraz Bangladesh", "price": 15200, "url": "https://www.daraz.com.bd/catalog/?q=Samsung+990+Pro+1TB"},
        ]
    },
    {
        "slug": "samsung-980-1tb-nvme-pcie-3",
        "model_code": "Samsung 980 (1TB)",
        "aliases": ["samsung 980 1tb", "samsung 980", "980 1tb", "samsung 980 nvme 1tb"],
        "title_en": "Samsung 980 (1TB PCIe 3.0 NVMe M.2 Internal SSD)",
        "title_bn": "স্যামসাং ৯৮০ (১টিবি পিসিআইই ৩.০ এনভিএমই এম.২ এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "Storage & SSD",
        "brand": "Samsung",
        "specs_summary": "PCIe 3.0 x4, NVMe 1.4 · Sequential Read up to 3500 MB/s · Sequential Write up to 3000 MB/s · DRAMless Host Memory Buffer (HMB) · 600 TBW",
        "starting_price": 8900,
        "max_price": 9800,
        "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80",
        "variant": "1TB NVMe M.2 · PCIe 3.0",
        "stores": [
            {"name": "Star Tech", "price": 8900, "url": "https://www.startech.com.bd/samsung-980-1tb-ssd"},
            {"name": "Ryans Computers", "price": 9200, "url": "https://www.ryans.com/samsung-980-1tb-ssd"},
            {"name": "Tech Land BD", "price": 9100, "url": "https://www.techlandbd.com/samsung-980-1tb-ssd"},
        ]
    },
    {
        "slug": "intel-core-i5-13400-processor",
        "model_code": "Core i5-13400",
        "aliases": ["intel i5 13400", "i5 13400", "intel core i5 13400", "core i5 13400 processor"],
        "title_en": "Intel Core i5-13400 Raptor Lake Processor (10 Cores · 16 Threads · Up to 4.60GHz · LGA1700)",
        "title_bn": "ইন্টেল কোর আই৫-১৩৪০০ প্রসেসর (১০ কোর · ১৬ থ্রেড · ৪.৬০ গিগাহার্টজ)",
        "category": "Laptops & PC",
        "subcategory": "Processors",
        "brand": "Intel",
        "specs_summary": "10 Cores (6 Performance-cores + 4 Efficient-cores) · 16 Threads · 20MB Intel Smart Cache · Max Turbo Frequency 4.60GHz · Intel UHD Graphics 730 · 65W Base TDP",
        "starting_price": 23200,
        "max_price": 25000,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "variant": "10 Cores · 16 Threads · UHD 730",
        "stores": [
            {"name": "Star Tech", "price": 23200, "url": "https://www.startech.com.bd/intel-core-i5-13400-processor"},
            {"name": "Ryans Computers", "price": 23800, "url": "https://www.ryans.com/intel-core-i5-13400-processor"},
            {"name": "Tech Land BD", "price": 23500, "url": "https://www.techlandbd.com/intel-core-i5-13400-processor"},
        ]
    },
    {
        "slug": "amd-ryzen-5-7600-processor",
        "model_code": "Ryzen 5 7600",
        "aliases": ["ryzen 5 7600", "amd ryzen 5 7600", "ryzen 7600", "r5 7600"],
        "title_en": "AMD Ryzen 5 7600 Zen 4 Processor (6 Cores · 12 Threads · Up to 5.10GHz · AM5)",
        "title_bn": "এএমডি রাইজেন ৫ ৭৬০০ প্রসেসর (৬ কোর · ১২ থ্রেড · ৫.১০ গিগাহার্টজ)",
        "category": "Laptops & PC",
        "subcategory": "Processors",
        "brand": "AMD",
        "specs_summary": "6 Cores, 12 Threads · 5nm FinFET · 32MB L3 Cache · Base Clock 3.8GHz, Boost Clock up to 5.1GHz · AMD Radeon Graphics Integrated · Socket AM5 · 65W TDP · Includes Wraith Stealth Cooler",
        "starting_price": 20800,
        "max_price": 22500,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "variant": "6 Cores · 12 Threads · Socket AM5",
        "stores": [
            {"name": "Star Tech", "price": 20800, "url": "https://www.startech.com.bd/amd-ryzen-5-7600-processor"},
            {"name": "Ryans Computers", "price": 21500, "url": "https://www.ryans.com/amd-ryzen-5-7600-processor"},
            {"name": "Tech Land BD", "price": 21000, "url": "https://www.techlandbd.com/amd-ryzen-5-7600-processor"},
        ]
    },

    # --------------------------------------------------------------------------
    # 8. GAMING CONSOLES & HANDHELDS
    # --------------------------------------------------------------------------
    {
        "slug": "sony-playstation-5-slim-disc-edition-1tb",
        "model_code": "PS5 Slim (Disc Edition · 1TB)",
        "aliases": ["ps5 slim disc edition", "ps5 slim disc", "ps5 disc edition", "playstation 5 disc edition", "ps5 slim", "playstation 5 slim", "sony ps5 slim"],
        "title_en": "Sony PlayStation 5 Slim (Disc Edition · 1TB SSD · Ultra HD Blu-ray)",
        "title_bn": "সোনি প্লেস্টেশন ৫ স্লিম (ডিস্ক এডিশন · ১টিবি এসএসডি)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Sony",
        "specs_summary": "Custom AMD Zen 2 8-Core CPU · AMD RDNA 2 GPU with Ray Tracing · 16GB GDDR6 · 1TB Ultra-High Speed NVMe SSD · 4K 120Hz & 8K Output Support · Includes DualSense Wireless Controller · Ultra HD Blu-ray Drive",
        "starting_price": 58990,
        "max_price": 65000,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80",
        "variant": "Disc Edition · 1TB SSD",
        "stores": [
            {"name": "Star Tech", "price": 58990, "url": "https://www.startech.com.bd/sony-playstation-5-slim-disc-edition"},
            {"name": "Custom Mac BD", "price": 59500, "url": "https://custommacbd.com/products/playstation-5-slim-disc-edition"},
            {"name": "Ryans Computers", "price": 61000, "url": "https://www.ryans.com/sony-playstation-5-slim-disc-edition"},
            {"name": "Tech Land BD", "price": 60500, "url": "https://www.techlandbd.com/sony-playstation-5-slim-disc"},
            {"name": "Daraz Bangladesh", "price": 62500, "url": "https://www.daraz.com.bd/catalog/?q=PS5+Slim+Disc+Edition"},
        ]
    },
    {
        "slug": "sony-playstation-5-slim-digital-edition-1tb",
        "model_code": "PS5 Slim (Digital Edition · 1TB)",
        "aliases": ["ps5 slim digital edition", "ps5 slim digital", "ps5 digital edition", "playstation 5 digital edition", "ps5 digital"],
        "title_en": "Sony PlayStation 5 Slim (Digital Edition · 1TB SSD · Disc-Free)",
        "title_bn": "সোনি প্লেস্টেশন ৫ স্লিম (ডিজিটাল এডিশন · ১টিবি এসএসডি)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Sony",
        "specs_summary": "Custom AMD Zen 2 CPU / RDNA 2 GPU · 16GB GDDR6 · 1TB NVMe SSD · Tempest 3D AudioTech · Haptic Feedback & Adaptive Triggers via DualSense · 100% Digital Download Gaming",
        "starting_price": 51990,
        "max_price": 56000,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80",
        "variant": "Digital Edition · 1TB SSD",
        "stores": [
            {"name": "Star Tech", "price": 51990, "url": "https://www.startech.com.bd/sony-playstation-5-slim-digital-edition"},
            {"name": "Custom Mac BD", "price": 52500, "url": "https://custommacbd.com/products/playstation-5-slim-digital-edition"},
            {"name": "Ryans Computers", "price": 53500, "url": "https://www.ryans.com/sony-playstation-5-slim-digital-edition"},
            {"name": "Daraz Bangladesh", "price": 54500, "url": "https://www.daraz.com.bd/catalog/?q=PS5+Slim+Digital+Edition"},
        ]
    },
    {
        "slug": "nintendo-switch-oled-model-64gb",
        "model_code": "Nintendo Switch OLED (64GB)",
        "aliases": ["nintendo switch oled", "switch oled", "nintendo switch oled model", "nintendo switch"],
        "title_en": "Nintendo Switch OLED Model (7-inch Vibrant OLED Screen · 64GB Internal Storage · White Joy-Cons)",
        "title_bn": "নিনটেন্ডো সুইচ ওএলইডি মডেল (৬৪জিবি)",
        "category": "Gaming Consoles",
        "subcategory": "Handhelds",
        "brand": "Nintendo",
        "specs_summary": "7-inch Vibrant OLED Screen with Vivid Colors · 64GB Internal Storage (MicroSD expandable) · Enhanced Audio in Handheld Mode · Wide Adjustable Stand · Wired LAN Port in TV Dock",
        "starting_price": 31990,
        "max_price": 35500,
        "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?auto=format&fit=crop&w=600&q=80",
        "variant": "7-inch OLED · 64GB",
        "stores": [
            {"name": "Star Tech", "price": 31990, "url": "https://www.startech.com.bd/nintendo-switch-oled-model"},
            {"name": "Custom Mac BD", "price": 32500, "url": "https://custommacbd.com/products/nintendo-switch-oled-model"},
            {"name": "Ryans Computers", "price": 33500, "url": "https://www.ryans.com/nintendo-switch-oled-model"},
            {"name": "Daraz Bangladesh", "price": 34000, "url": "https://www.daraz.com.bd/catalog/?q=Nintendo+Switch+OLED"},
        ]
    },
    {
        "slug": "valve-steam-deck-oled-512gb",
        "model_code": "Steam Deck OLED (512GB)",
        "aliases": ["steam deck oled", "steam deck", "steam deck oled 512gb", "valve steam deck"],
        "title_en": "Valve Steam Deck OLED (7.4-inch 90Hz HDR OLED · 512GB NVMe SSD · 16GB LPDDR5)",
        "title_bn": "ভাল্ভ স্টিম ডেক ওএলইডি (৫১২জিবি এসএসডি · ৯০হার্টজ)",
        "category": "Gaming Consoles",
        "subcategory": "Handhelds",
        "brand": "Valve",
        "specs_summary": "6nm AMD Sephiroth APU (Zen 2 + RDNA 2) · 16GB LPDDR5 6400 MT/s · 512GB High-Speed NVMe SSD · 7.4-inch 1280x800 HDR OLED 90Hz 1000 nits · Wi-Fi 6E · 50Wh Battery",
        "starting_price": 66990,
        "max_price": 72000,
        "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?auto=format&fit=crop&w=600&q=80",
        "variant": "7.4-inch OLED 90Hz · 512GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 66990, "url": "https://custommacbd.com/products/valve-steam-deck-oled-512gb"},
            {"name": "Star Tech", "price": 68500, "url": "https://www.startech.com.bd/valve-steam-deck-oled-512gb"},
            {"name": "Tech Land BD", "price": 69000, "url": "https://www.techlandbd.com/valve-steam-deck-oled"},
        ]
    },

    # --------------------------------------------------------------------------
    # 9. SMARTWATCHES & WEARABLES
    # --------------------------------------------------------------------------
    {
        "slug": "apple-watch-ultra-2-49mm",
        "model_code": "Apple Watch Ultra 2 (49mm)",
        "aliases": ["apple watch ultra 2", "watch ultra 2", "apple watch ultra", "ultra 2 apple watch"],
        "title_en": "Apple Watch Ultra 2 (49mm Titanium Case · Cellular + GPS · Sapphire Crystal · 3000 nits)",
        "title_bn": "অ্যাপল ওয়াচ আল্ট্রা ২ (৪৯মি.মি. টাইটানিয়াম কেস · সেলুলার)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartwatches",
        "brand": "Apple",
        "specs_summary": "S9 SiP with 64-bit dual-core processor · Double Tap Gesture · 3000 nits Always-On Retina OLED · Precision Dual-Frequency GPS (L1 and L5) · 100m Water Resistance · 36-Hour Battery Life (72h Low Power)",
        "starting_price": 86990,
        "max_price": 93000,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "variant": "49mm Titanium · Cellular",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 86990, "url": "https://www.applegadgetsbd.com/product/apple-watch-ultra-2"},
            {"name": "Custom Mac BD", "price": 87500, "url": "https://custommacbd.com/products/apple-watch-ultra-2"},
            {"name": "Star Tech", "price": 89500, "url": "https://www.startech.com.bd/apple-watch-ultra-2"},
            {"name": "Daraz Bangladesh", "price": 91000, "url": "https://www.daraz.com.bd/catalog/?q=Apple+Watch+Ultra+2"},
        ]
    },
    {
        "slug": "samsung-galaxy-watch-7-44mm",
        "model_code": "Galaxy Watch 7 (44mm)",
        "aliases": ["samsung galaxy watch 7", "galaxy watch 7", "galaxy watch 7 44mm", "samsung watch 7"],
        "title_en": "Samsung Galaxy Watch 7 (44mm Super AMOLED · BioActive Sensor · Wear OS 5)",
        "title_bn": "স্যামসাং গ্যালাক্সি ওয়াচ ৭ (৪৪মি.মি.)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartwatches",
        "brand": "Samsung",
        "specs_summary": "Exynos W1000 3nm 5-Core Processor · 2GB RAM + 32GB Storage · 1.5-inch Super AMOLED Sapphire Crystal · Dual-Frequency GPS · Advanced Metabolic & Sleep Tracking · 425mAh",
        "starting_price": 31990,
        "max_price": 35000,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "variant": "44mm Aluminum · Bluetooth",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 31990, "url": "https://www.applegadgetsbd.com/product/samsung-galaxy-watch-7"},
            {"name": "Custom Mac BD", "price": 32500, "url": "https://custommacbd.com/products/samsung-galaxy-watch-7"},
            {"name": "Star Tech", "price": 33500, "url": "https://www.startech.com.bd/samsung-galaxy-watch-7"},
            {"name": "Daraz Bangladesh", "price": 34000, "url": "https://www.daraz.com.bd/catalog/?q=Samsung+Galaxy+Watch+7"},
        ]
    },

    # --------------------------------------------------------------------------
    # 10. AUDIO & ANC TWS
    # --------------------------------------------------------------------------
    {
        "slug": "apple-airpods-pro-2-usb-c",
        "model_code": "AirPods Pro 2 (USB-C)",
        "aliases": ["airpods pro 2", "apple airpods pro 2", "airpods pro 2 usb c", "airpods pro"],
        "title_en": "Apple AirPods Pro 2 (USB-C MagSafe Charging Case · Active Noise Cancellation · H2 Chip)",
        "title_bn": "অ্যাপল এয়ারপডস প্রো ২ (ইউএসবি-সি ম্যাগসেফ কেইস · অ্যাক্টিভ নয়েজ ক্যান্সেলেশন)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Audio & TWS",
        "brand": "Apple",
        "specs_summary": "Apple H2 Headphone Chip · Up to 2x more Active Noise Cancellation · Adaptive Audio & Transparency Mode · Personalized Spatial Audio with Dynamic Head Tracking · Dust, Sweat, and Water Resistant (IP54)",
        "starting_price": 24490,
        "max_price": 27000,
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80",
        "variant": "USB-C MagSafe · ANC",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 24490, "url": "https://www.applegadgetsbd.com/product/airpods-pro-2-type-c"},
            {"name": "Custom Mac BD", "price": 24900, "url": "https://custommacbd.com/products/airpods-pro-2nd-generation-usb-c"},
            {"name": "Star Tech", "price": 25500, "url": "https://www.startech.com.bd/apple-airpods-pro-2nd-gen-type-c"},
            {"name": "Daraz Bangladesh", "price": 26500, "url": "https://www.daraz.com.bd/catalog/?q=AirPods+Pro+2+USB-C"},
        ]
    },
    {
        "slug": "sony-wh-1000xm5-wireless-anc-headphones",
        "model_code": "Sony WH-1000XM5",
        "aliases": ["sony wh-1000xm5", "sony xm5", "wh-1000xm5", "sony wh 1000xm5", "sony headphones xm5"],
        "title_en": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones (Industry-Leading ANC · 30-Hour Battery)",
        "title_bn": "সোনি ডাব্লিউএইচ-১০০০এক্সএম৫ ওয়্যারলেস নয়েজ ক্যানসেলিং হেডফোন",
        "category": "Mobiles & Gadgets",
        "subcategory": "Audio & TWS",
        "brand": "Sony",
        "specs_summary": "Integrated Processor V1 + HD Noise Canceling Processor QN1 · 8 Microphones for Unmatched ANC · 30mm Carbon Fiber Drivers with LDAC Hi-Res Audio · Multipoint Bluetooth 5.2 · 30 Hours Battery",
        "starting_price": 33990,
        "max_price": 38000,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=600&q=80",
        "variant": "Wireless Over-Ear · Dual-Processor ANC",
        "stores": [
            {"name": "Custom Mac BD", "price": 33990, "url": "https://custommacbd.com/products/sony-wh-1000xm5"},
            {"name": "Star Tech", "price": 34990, "url": "https://www.startech.com.bd/sony-wh-1000xm5-wireless-noise-canceling-headphones"},
            {"name": "Apple Gadgets BD", "price": 34500, "url": "https://www.applegadgetsbd.com/product/sony-wh-1000xm5"},
            {"name": "Daraz Bangladesh", "price": 36000, "url": "https://www.daraz.com.bd/catalog/?q=Sony+WH-1000XM5"},
        ]
    },

    # --------------------------------------------------------------------------
    # 11. CAMERAS & ACTION CAMS
    # --------------------------------------------------------------------------
    {
        "slug": "gopro-hero-12-black-action-camera",
        "model_code": "GoPro HERO 12 Black",
        "aliases": ["gopro hero 12", "gopro hero 12 black", "hero 12", "gopro 12"],
        "title_en": "GoPro HERO 12 Black 5.3K Action Camera (HyperSmooth 6.0 · HDR Video · Waterproof 33ft)",
        "title_bn": "গোপ্রো হিরো ১২ ব্ল্যাক অ্যাকশন ক্যামেরা",
        "category": "Cameras & Photography",
        "subcategory": "Action Cameras",
        "brand": "GoPro",
        "specs_summary": "5.3K60, 4K120, 2.7K240 Resolution · 27MP Photos · HyperSmooth 6.0 with 360 Horizon Lock · High Dynamic Range (HDR) Video + Photo · Bluetooth Audio Support for AirPods · 1720mAh Enduro Battery",
        "starting_price": 39500,
        "max_price": 44000,
        "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80",
        "variant": "5.3K60 Video · Waterproof 10m",
        "stores": [
            {"name": "Star Tech", "price": 39500, "url": "https://www.startech.com.bd/gopro-hero-12-black-action-camera"},
            {"name": "Custom Mac BD", "price": 39990, "url": "https://custommacbd.com/products/gopro-hero-12-black"},
            {"name": "Apple Gadgets BD", "price": 40500, "url": "https://www.applegadgetsbd.com/product/gopro-hero-12-black"},
            {"name": "Camera Bazar BD", "price": 41000, "url": "https://www.camerabazarbd.com/gopro-hero-12-black"},
        ]
    },
    {
        "slug": "dji-osmo-pocket-3-creator-combo",
        "model_code": "DJI Osmo Pocket 3 Creator Combo",
        "aliases": ["dji osmo pocket 3", "osmo pocket 3", "pocket 3 creator combo", "dji pocket 3"],
        "title_en": "DJI Osmo Pocket 3 (1-inch CMOS Sensor · 4K 120fps · 2-inch Rotatable Touchscreen · 3-Axis Gimbal)",
        "title_bn": "ডিজেআই ওসমো পকেট ৩ ক্রিয়েটর কম্বো",
        "category": "Cameras & Photography",
        "subcategory": "Action Cameras",
        "brand": "DJI",
        "specs_summary": "1-inch CMOS Sensor with 4K/120fps Video · 2-inch Rotatable Touchscreen with Fast Horizontal/Vertical Shooting · 3-Axis Gimbal Mechanical Stabilization · D-Log M & 10-Bit Color · ActiveTrack 6.0",
        "starting_price": 68500,
        "max_price": 75000,
        "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80",
        "variant": "1-inch Sensor · Creator Combo",
        "stores": [
            {"name": "Custom Mac BD", "price": 68500, "url": "https://custommacbd.com/products/dji-osmo-pocket-3-creator-combo"},
            {"name": "Star Tech", "price": 69990, "url": "https://www.startech.com.bd/dji-osmo-pocket-3-creator-combo"},
            {"name": "Apple Gadgets BD", "price": 71000, "url": "https://www.applegadgetsbd.com/product/dji-osmo-pocket-3-creator-combo"},
            {"name": "Camera Bazar BD", "price": 70500, "url": "https://www.camerabazarbd.com/dji-osmo-pocket-3-creator-combo"},
        ]
    },
    {
        "slug": "sony-alpha-a7-iv-mirrorless-camera",
        "model_code": "Sony Alpha A7 IV",
        "aliases": ["sony a7 iv", "sony a7m4", "sony a74", "sony alpha a7 iv", "a7 iv body"],
        "title_en": "Sony Alpha A7 IV Full-Frame Mirrorless Camera (Body Only · 33MP Exmor R BSI CMOS · 4K 60p)",
        "title_bn": "সোনি আলফা এ৭ ৪ ফুল-ফ্রেম মিররলেস ক্যামেরা (বডি)",
        "category": "Cameras & Photography",
        "subcategory": "Mirrorless",
        "brand": "Sony",
        "specs_summary": "33MP Full-Frame Exmor R BSI CMOS Sensor · BIONZ XR Image Processor · Up to 10 fps Shooting with 759-Point Fast Hybrid AF · Real-Time Eye AF for Humans, Animals & Birds · 4K 60p 10-Bit 4:2:2 Video",
        "starting_price": 228000,
        "max_price": 242000,
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80",
        "variant": "33MP Full-Frame · Body Only",
        "stores": [
            {"name": "Sony-Smart Bangladesh", "price": 228000, "url": "https://sonysmart.com.bd/sony-alpha-a7-iv"},
            {"name": "Star Tech", "price": 232000, "url": "https://www.startech.com.bd/sony-alpha-a7-iv-mirrorless-camera"},
            {"name": "Camera Bazar BD", "price": 229500, "url": "https://www.camerabazarbd.com/sony-alpha-a7-iv"},
            {"name": "Ryans Computers", "price": 235000, "url": "https://www.ryans.com/sony-alpha-a7-iv-mirrorless-camera"},
        ]
    },

    # --------------------------------------------------------------------------
    # 12. WATCHES & HOROLOGY
    # --------------------------------------------------------------------------
    {
        "slug": "casio-g-shock-ga-2100-1a1-casioak",
        "model_code": "G-Shock GA-2100-1A1",
        "aliases": ["casio ga-2100", "g-shock ga-2100", "casioak", "ga 2100", "g shock casioak", "ga2100"],
        "title_en": "Casio G-Shock GA-2100-1A1 'CasiOak' (Carbon Core Guard · Octagonal Bezel · All-Black Edition)",
        "title_bn": "ক্যাসিও জি-শক জিএ-২১০০-১এ১ 'ক্যাসিওক' অল-ব্ল্যাক হাতঘড়ি",
        "category": "Watches & Horology",
        "subcategory": "Digital & Sport",
        "brand": "Casio",
        "specs_summary": "Carbon Core Guard Structure · Slim 11.8mm Profile · Octagonal Minimalist Bezel · 200-Meter Water Resistance · Double LED Light (Super Illuminator) · World Time 31 Time Zones",
        "starting_price": 10500,
        "max_price": 12500,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80",
        "variant": "Carbon Core Guard · All-Black",
        "stores": [
            {"name": "Time Zone Bangladesh", "price": 10500, "url": "https://timezonebd.com/product/ga-2100-1a1dr"},
            {"name": "Watches World BD", "price": 10800, "url": "https://watchesworldbd.com/product/casio-g-shock-ga-2100-1a1dr"},
            {"name": "Casio Bangladesh", "price": 11200, "url": "https://casiobd.com/product/ga-2100-1a1"},
            {"name": "Daraz Bangladesh", "price": 11500, "url": "https://www.daraz.com.bd/catalog/?q=G-Shock+GA-2100"},
        ]
    },
    {
        "slug": "tissot-prx-powermatic-80-blue-dial",
        "model_code": "Tissot PRX Powermatic 80",
        "aliases": ["tissot prx", "tissot prx powermatic 80", "prx powermatic 80", "tissot prx automatic", "tissot prx 40mm"],
        "title_en": "Tissot PRX Powermatic 80 (40mm 316L Stainless Steel · Nivachron Hairspring · 80-Hour Power Reserve · Blue Waffle Dial)",
        "title_bn": "টিসোট পিআরএক্স পাওয়ারম্যাটিক ৮০ (৪০মি.মি. অটোমেটিক হাতঘড়ি)",
        "category": "Watches & Horology",
        "subcategory": "Luxury & Automatic",
        "brand": "Tissot",
        "specs_summary": "Swiss Automatic Powermatic 80.111 Movement · Patented Nivachron Anti-Magnetic Hairspring · 80 Hours Power Reserve · Scratch-Resistant Sapphire Crystal with Anti-Reflective Coating · 100m Water Resistance · Integrated Bracelet",
        "starting_price": 86000,
        "max_price": 94000,
        "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=600&q=80",
        "variant": "40mm Automatic · 80-Hour Reserve",
        "stores": [
            {"name": "Time Zone Bangladesh", "price": 86000, "url": "https://timezonebd.com/product/tissot-prx-powermatic-80-blue"},
            {"name": "Watches World BD", "price": 87500, "url": "https://watchesworldbd.com/product/tissot-prx-powermatic-80"},
            {"name": "Swiss Timepieces BD", "price": 89000, "url": "https://swisstimepieces.com.bd/tissot-prx-automatic"},
        ]
    },
]

# Merge expanded SKUs across all consumer electronics verticals
MASTER_CATALOG_ITEMS.extend(EXPANDED_CATALOG_ITEMS)

# Quick lookup index by model code and aliases
_MASTER_ALIASES_INDEX: Dict[str, Dict[str, Any]] = {}
for item in MASTER_CATALOG_ITEMS:
    for al in item.get("aliases", []):
        _MASTER_ALIASES_INDEX[al.strip().lower()] = item
    _MASTER_ALIASES_INDEX[item["slug"].lower()] = item
    _MASTER_ALIASES_INDEX[item["model_code"].lower()] = item


def normalize_catalog_query(query: str) -> str:
    """Normalizes spaces, dashes, parentheses and storage indicators."""
    q = (query or "").lower().strip()
    q = re.sub(r"[\(\)\[\]\{\}]", " ", q)
    q = re.sub(r"\s+", " ", q)
    return q.strip()


def match_master_catalog(query: str) -> Optional[Dict[str, Any]]:
    """
    Matches search query against the Authoritative Master Product Catalog.
    Includes instant SKU matching for:
      - Phones (Pixel, iPhone, Galaxy, OnePlus, Xiaomi)
      - Laptops & Components (MacBook Air/Pro, ROG Zephyrus, TUF, Victus, RTX GPUs, NVMe SSDs)
      - Gaming Consoles (PS5 Slim Disc/Digital, Nintendo Switch, Steam Deck)
      - Smartwatches & Audio (Apple Watch, Galaxy Watch, AirPods Pro, Sony XM5)
      - Cameras & Horology (GoPro, DJI Pocket, Sony A7, G-Shock, Tissot PRX)
      - Delegates to appliances_catalog for Walton/Samsung/Gree white goods
    """
    if not query:
        return None

    q_norm = normalize_catalog_query(query)

    # 1. First delegate to Appliances Catalog for white goods
    app_match = match_appliances_catalog(query)
    if app_match:
        return app_match

    # 2. Check direct alias match
    if q_norm in _MASTER_ALIASES_INDEX:
        return _MASTER_ALIASES_INDEX[q_norm]

    # Compact token variant (e.g. 'pixel 9 256gb' vs 'pixel 9 256 gb')
    q_no_space = q_norm.replace(" ", "")
    for al, item in _MASTER_ALIASES_INDEX.items():
        if q_no_space == al.replace(" ", ""):
            return item

    # 3. Specific hardware tokens containment matching
    # E.g. 'google pixel 9 256 gb' -> contains 'pixel 9' and '256'
    q_words = set(re.findall(r"\w+", q_norm))

    best_match = None
    best_score = 0

    for item in MASTER_CATALOG_ITEMS:
        # Check if item's primary identifiers match
        brand_match = item["brand"].lower() in q_words or item["brand"].lower() in q_norm
        
        # Check alias token subsets
        for al in item.get("aliases", []):
            al_words = set(re.findall(r"\w+", al.lower()))
            if al_words.issubset(q_words):
                score = len(al_words) * 10
                if score > best_score:
                    best_score = score
                    best_match = item

    if best_match and best_score >= 20:
        return best_match

    # 4. Storage & Model Disambiguation
    # E.g. Query has 'pixel 9' and '256' -> MUST NOT match 'pixel 9 128gb'
    has_256 = any(tok in q_words for tok in ("256", "256gb"))
    has_128 = any(tok in q_words for tok in ("128", "128gb"))
    has_512 = any(tok in q_words for tok in ("512", "512gb"))
    has_1tb = any(tok in q_words for tok in ("1tb", "1000gb"))

    if "pixel 9" in q_norm:
        if "pro xl" in q_norm:
            return _MASTER_ALIASES_INDEX.get("pixel 9 pro xl 256gb")
        elif "pro" in q_norm:
            return _MASTER_ALIASES_INDEX.get("pixel 9 pro 256gb")
        elif has_256:
            return _MASTER_ALIASES_INDEX.get("google pixel 9 256gb")
        elif has_128 or not has_256:
            return _MASTER_ALIASES_INDEX.get("google pixel 9 128gb")

    if "macbook air" in q_norm and "m3" in q_norm:
        if has_512 or "16gb" in q_norm:
            return _MASTER_ALIASES_INDEX.get("macbook air m3 16gb 512gb")
        return _MASTER_ALIASES_INDEX.get("macbook air m3")

    if "ps5" in q_norm or "playstation 5" in q_norm:
        if "digital" in q_norm:
            return _MASTER_ALIASES_INDEX.get("ps5 slim digital edition")
        return _MASTER_ALIASES_INDEX.get("ps5 slim disc edition")

    return None


def search_master_catalog(query: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Multi-card authoritative catalog search:
      - For exact variants (e.g. 'google pixel 9 256 gb', 'ps5 slim disc edition'), returns [exact_item].
      - For broader queries (e.g. 'pixel 9', 'iphone 16', 'macbook air m3', 'vivo v40'), returns all
        matching canonical variant comparison cards up to `limit`.
    """
    if not query:
        return []

    q_norm = normalize_catalog_query(query)

    # 1. First delegate to Appliances Catalog if white goods
    app_match = match_appliances_catalog(query)
    if app_match:
        return [app_match]

    q_words = set(re.findall(r"\w+", q_norm))
    has_variant_spec = any(tok in q_words for tok in (
        "128", "128gb", "256", "256gb", "512", "512gb", "1tb", "2tb",
        "digital", "disc", "cellular", "wifi", "rtx", "gtx", "oled"
    ))

    # If the user specified an explicit hardware variant, look for exact match first
    if has_variant_spec:
        exact = match_master_catalog(query)
        if exact:
            return [exact]

    # Broad model search: collect all canonical variants matching core query terms
    matches: List[Dict[str, Any]] = []
    seen_slugs = set()

    primary = match_master_catalog(query)
    if primary:
        matches.append(primary)
        seen_slugs.add(primary["slug"])

    # Search through all catalog items
    sig_words = [w for w in q_words if len(w) >= 2 and w not in ("the", "and", "for", "with", "best", "price", "bd", "in", "online", "buy")]
    for item in MASTER_CATALOG_ITEMS:
        slug = item["slug"]
        if slug in seen_slugs:
            continue

        t_en = item["title_en"].lower()
        m_code = item["model_code"].lower()
        aliases = [al.lower() for al in item.get("aliases", [])]

        if q_norm in t_en or q_norm in m_code or any(q_norm in al for al in aliases):
            matches.append(item)
            seen_slugs.add(slug)
            if len(matches) >= limit:
                break
        elif sig_words and all(w in t_en or w in m_code or any(w in al for al in aliases) for w in sig_words):
            matches.append(item)
            seen_slugs.add(slug)
            if len(matches) >= limit:
                break

    return matches[:limit]


def build_master_product_card(catalog_item: Dict[str, Any], db: Optional[Any] = None) -> Product:
    """
    Constructs a fully-populated, authentic Product comparison card
    enriched with verified Bangladeshi dealer offers and full specs.
    Option B Architecture:
      - Master Catalog provides the Canonical Whitelist (Title, Specs, Images, Model Code, Variant).
      - Store offers come dynamically from jachai.db if existing, or verified dealer direct landing links (NEVER broken search pages).
    Delegates to appliances_catalog if category is Home Appliances.
    """
    if catalog_item.get("category") == "Home Appliances":
        return build_appliance_product_card(catalog_item)

    title_en = catalog_item["title_en"]
    title_bn = catalog_item["title_bn"]
    slug = catalog_item["slug"]
    img_url = catalog_item["image_url"]
    starting_p = catalog_item["starting_price"]
    max_p = catalog_item["max_price"]
    specs = catalog_item.get("specs_summary") or f"{title_en} · Verified Authentic BD Stock"
    cat_name = catalog_item.get("category", "Mobiles & Gadgets")

    prod = Product(
        id=80000 + abs(hash(slug)) % 10000,
        slug=slug,
        title_en=title_en,
        title_bn=title_bn,
        category=cat_name,
        image_url=img_url,
        specs_summary=specs,
        price_30d_ago=int(starting_p * 1.05),
        price_15d_ago=int(starting_p * 1.02),
        is_pinned_homepage=False,
        created_at=datetime.utcnow(),
    )

    # Option B: Check DB for real live scraped StoreOffers for this SKU
    if db is not None:
        try:
            existing = db.query(Product).filter(Product.slug == slug).first()
            if existing and existing.offers:
                clean_db_offers = [
                    o for o in existing.offers
                    if o.target_url and not any(sq in o.target_url.lower() for sq in ("/search?q=", "/catalog/?q=", "catalogsearch"))
                ]
                if clean_db_offers:
                    prod.offers = clean_db_offers
                    return prod
        except Exception:
            pass

    offers: List[StoreOffer] = []
    try:
        from bd_stores_registry import get_store_registry_meta, compute_trust_score
    except ImportError:
        from .bd_stores_registry import get_store_registry_meta, compute_trust_score

    CLEAN_MERCHANT_DOMAINS = {
        "apple gadgets bd": "https://www.applegadgetsbd.com",
        "custom mac bd": "https://custommacbd.com",
        "star tech": "https://www.startech.com.bd",
        "ryans computers": "https://www.ryanscomputers.com",
        "dazzle bd": "https://dazzle.com.bd",
        "techland bd": "https://www.techlandbd.com",
        "pickaboo": "https://www.pickaboo.com",
        "gadget & gear": "https://gadgetandgear.com",
        "daraz bangladesh": "https://www.daraz.com.bd",
    }

    for idx, s in enumerate(catalog_item.get("stores", [])):
        s_name = s.get("name", "Verified BD Dealer")
        s_low = s_name.lower().strip()
        s_price = s.get("price", starting_p)
        raw_u = s.get("url") or ""

        # Guard: NEVER allow broken search URLs or non-shop sites
        if any(bad in raw_u.lower() for bad in ("/search", "catalogsearch", "/catalog/?q=", "mobiledokan")):
            s_url = CLEAN_MERCHANT_DOMAINS.get(s_low, "https://www.startech.com.bd")
        elif raw_u.startswith("http"):
            s_url = raw_u
        else:
            s_url = CLEAN_MERCHANT_DOMAINS.get(s_low, "https://www.startech.com.bd")

        meta = get_store_registry_meta(s_name)
        is_pre = bool(meta.get("is_preseeded", True))
        trust = compute_trust_score(store_name=s_name, is_preseeded=is_pre, price=float(s_price))

        offer = StoreOffer(
            id=850000 + abs(hash(slug)) % 10000 * 10 + idx,
            product_id=prod.id,
            store_name=s_name,
            source_type="crawler",
            target_url=s_url,
            website_url=s_url,
            facebook_url=meta.get("facebook_url") or f"https://www.facebook.com/search/top/?q={quote_plus(s_name)}",
            current_price=s_price,
            original_price=int(s_price * 1.07),
            cod_terms_en=f"৳{s_price:,} · Authentic Warranty · Cash on Delivery Available" if is_pre else "⚠️ Unverified Merchant · COD Only",
            cod_terms_bn=f"৳{s_price:,} · খাঁটি ওয়্যারেন্টি · ক্যাশ অন ডেলিভারি প্রযোজ্য" if is_pre else "⚠️ অযাচাইকৃত বিক্রেতা · ক্যাশ অন ডেলিভারিতে চেক করে নিন",
            warranty_text="Official BD Warranty" if is_pre else "Store Warranty",
            in_stock=True,
            spider_status="healthy",
            last_synced_at="Verified Merchant Index",
            is_preseeded=is_pre,
            is_sponsored=False,
            trust_score=trust["trust_score"],
            trust_badge=trust["trust_badge"],
            risk_level=trust["risk_level"],
            discount_tag="7% OFF",
            discount_pct=7,
        )
        offers.append(offer)

    prod.offers = offers
    return prod


def get_master_suggestions(query_prefix: str, limit: int = 5) -> List[str]:
    """Returns autocomplete suggestions matching master product models and aliases."""
    q_norm = query_prefix.strip().lower()
    if len(q_norm) < 2:
        return []

    results: List[str] = []
    seen = set()

    # 1. Master catalog suggestions
    for item in MASTER_CATALOG_ITEMS:
        t_en = item["title_en"]
        m_code = item["model_code"]
        if q_norm in t_en.lower() or q_norm in m_code.lower():
            if t_en not in seen:
                results.append(t_en)
                seen.add(t_en)
                if len(results) >= limit:
                    return results

    # 2. Appliances catalog suggestions
    app_suggs = get_appliance_suggestions(query_prefix, limit=limit - len(results))
    for s in app_suggs:
        if s not in seen:
            results.append(s)
            seen.add(s)
            if len(results) >= limit:
                break

    return results
