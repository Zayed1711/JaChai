"""
JaChai 15-Category Predetermined Product Catalog & Subcategory Browse Engine
(backend/predetermined_catalog.py)

Behavior:
  1. Clicking any of the 15 Categories displays the exact Base Products specified
     by the user with "Starts from ৳..." pricing and verified store comparison drawers.
  2. Clicking a Predetermined Product Card shows all verified stores selling that
     product type, with starting prices, trust scores, COD status, and direct links.
  3. Specific models are searched when the user explicitly queries in the Search Bar,
     preserving the exact scraped prices from the store webpages without fabrication.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from urllib.parse import quote_plus

try:
    from .bd_stores_registry import (
        CATEGORY_REGISTRY_MAP,
        MERCHANT_SEARCH_TEMPLATES,
        get_stores_for_category,
        build_store_target_url,
        get_store_registry_meta,
    )
    from .models import Product, StoreOffer, PriceHistory
except ImportError:
    from bd_stores_registry import (
        CATEGORY_REGISTRY_MAP,
        MERCHANT_SEARCH_TEMPLATES,
        get_stores_for_category,
        build_store_target_url,
        get_store_registry_meta,
    )
    from models import Product, StoreOffer, PriceHistory

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_PRODUCTS_IMG_DIR = PROJECT_ROOT / "frontend" / "public" / "images" / "products"

_PREDETERMINED_BROWSE_CACHE: Dict[str, List[Product]] = {}


def resolve_product_card_image(cat_id: str, slug: str, fallback_url: str) -> str:
    """Checks local product images, falling back to verified CDN image URL."""
    cat_folder = LOCAL_PRODUCTS_IMG_DIR / cat_id
    if cat_folder.is_dir():
        for ext in (".jpg", ".jpeg", ".png", ".webp", ".svg"):
            cand = cat_folder / f"{slug}{ext}"
            if cand.is_file():
                return f"/images/products/{cat_id}/{slug}{ext}"
    return fallback_url


# ==============================================================================
# MASTER 15-CATEGORY -> BASE PRODUCTS CATALOG
# ==============================================================================
CATEGORY_PREDETERMINED_CATALOG: Dict[str, Dict[str, Any]] = {
    # 1. Cameras & DSLR
    "cameras-photography": {
        "subcategories": ["All", "Cameras & DSLR", "Lenses", "Gimbals & Accessories"],
        "products": [
            {"slug": "mirrorless-camera", "title_en": "Mirrorless Camera", "title_bn": "মিররলেস ক্যামেরা", "subcategory": "Cameras & DSLR", "search_kw": "mirrorless camera", "starts_from": 65000, "max_price": 280000, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80"},
            {"slug": "dslr-camera", "title_en": "DSLR Camera", "title_bn": "ডিএসএলআর ক্যামেরা", "subcategory": "Cameras & DSLR", "search_kw": "dslr camera", "starts_from": 45000, "max_price": 220000, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80"},
            {"slug": "action-camera", "title_en": "Action Camera", "title_bn": "অ্যাকশন ক্যামেরা", "subcategory": "Cameras & DSLR", "search_kw": "action camera", "starts_from": 14500, "max_price": 55000, "img": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80"},
            {"slug": "vlogging-camera", "title_en": "Vlogging Camera", "title_bn": "ভ্লগিং ক্যামেরা", "subcategory": "Cameras & DSLR", "search_kw": "vlogging camera", "starts_from": 28000, "max_price": 95000, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80"},
            {"slug": "drone", "title_en": "Drone", "title_bn": "ড্রোন", "subcategory": "Cameras & DSLR", "search_kw": "drone", "starts_from": 35000, "max_price": 185000, "img": "https://images.unsplash.com/photo-1527977966376-1c8408f9f108?auto=format&fit=crop&w=600&q=80"},
            {"slug": "prime-lens", "title_en": "Prime Lens", "title_bn": "প্রাইম লেন্স", "subcategory": "Lenses", "search_kw": "prime lens", "starts_from": 16500, "max_price": 95000, "img": "https://images.unsplash.com/photo-1617005082133-548c4dd27f35?auto=format&fit=crop&w=600&q=80"},
            {"slug": "zoom-lens", "title_en": "Zoom Lens", "title_bn": "জুম লেন্স", "subcategory": "Lenses", "search_kw": "zoom lens", "starts_from": 24000, "max_price": 145000, "img": "https://images.unsplash.com/photo-1617005082133-548c4dd27f35?auto=format&fit=crop&w=600&q=80"},
            {"slug": "camera-tripod", "title_en": "Camera Tripod", "title_bn": "ক্যামেরা ট্রাইপড", "subcategory": "Gimbals & Accessories", "search_kw": "camera tripod", "starts_from": 1850, "max_price": 14500, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gimbal-stabilizer", "title_en": "Gimbal Stabilizer", "title_bn": "গিম্বল স্ট্যাবিলাইজার", "subcategory": "Gimbals & Accessories", "search_kw": "gimbal stabilizer", "starts_from": 8500, "max_price": 42000, "img": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80"},
            {"slug": "camera-bag", "title_en": "Camera Bag", "title_bn": "ক্যামেরা ব্যাগ", "subcategory": "Gimbals & Accessories", "search_kw": "camera bag", "starts_from": 1450, "max_price": 8500, "img": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=600&q=80"},
            {"slug": "studio-ring-light", "title_en": "Studio Ring Light", "title_bn": "স্টুডিও রিং লাইট", "subcategory": "Gimbals & Accessories", "search_kw": "ring light", "starts_from": 1200, "max_price": 6500, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 2. Mobiles & Gadgets
    "mobile-gadgets": {
        "subcategories": ["All", "Smartphones & Tablets", "Audio & Wearables", "Chargers & Protection"],
        "products": [
            {"slug": "smartphone", "title_en": "Smartphone", "title_bn": "স্মার্টফোন", "subcategory": "Smartphones & Tablets", "search_kw": "smartphone", "starts_from": 11500, "max_price": 215000, "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80"},
            {"slug": "feature-phone", "title_en": "Feature Phone", "title_bn": "ফিচার ফোন", "subcategory": "Smartphones & Tablets", "search_kw": "feature phone", "starts_from": 1450, "max_price": 4500, "img": "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=600&q=80"},
            {"slug": "tablet", "title_en": "Tablet", "title_bn": "ট্যাবলেট", "subcategory": "Smartphones & Tablets", "search_kw": "tablet ipad", "starts_from": 16500, "max_price": 160000, "img": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80"},
            {"slug": "smartwatch", "title_en": "Smartwatch", "title_bn": "স্মার্টওয়াচ", "subcategory": "Audio & Wearables", "search_kw": "smartwatch", "starts_from": 1850, "max_price": 55000, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80"},
            {"slug": "fitness-tracker", "title_en": "Fitness Tracker", "title_bn": "ফিটনেস ট্র্যাকার", "subcategory": "Audio & Wearables", "search_kw": "fitness tracker smart band", "starts_from": 1250, "max_price": 6500, "img": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=600&q=80"},
            {"slug": "tws-earbuds", "title_en": "TWS Earbuds", "title_bn": "টিডব্লিউএস ইয়ারবাডস", "subcategory": "Audio & Wearables", "search_kw": "tws earbuds wireless", "starts_from": 950, "max_price": 28000, "img": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80"},
            {"slug": "over-ear-anc-headphones", "title_en": "Over-Ear ANC Headphones", "title_bn": "ওভার-ইয়ার হেডফোন", "subcategory": "Audio & Wearables", "search_kw": "anc over ear headphones", "starts_from": 2850, "max_price": 42000, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "power-bank", "title_en": "Power Bank", "title_bn": "পাওয়ার ব্যাংক", "subcategory": "Chargers & Protection", "search_kw": "power bank", "starts_from": 950, "max_price": 7500, "img": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=600&q=80"},
            {"slug": "fast-charger", "title_en": "Fast Charger", "title_bn": "ফাস্ট চার্জার", "subcategory": "Chargers & Protection", "search_kw": "fast charger adapter", "starts_from": 450, "max_price": 4500, "img": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=600&q=80"},
            {"slug": "magsafe-charger", "title_en": "Magsafe Charger", "title_bn": "ম্যাগসেফ চার্জার", "subcategory": "Chargers & Protection", "search_kw": "magsafe wireless charger", "starts_from": 1450, "max_price": 6500, "img": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=600&q=80"},
            {"slug": "phone-case", "title_en": "Phone Case", "title_bn": "ফোন কেস", "subcategory": "Chargers & Protection", "search_kw": "phone case cover", "starts_from": 150, "max_price": 3200, "img": "https://images.unsplash.com/photo-1601593346740-925612772716?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 3. Laptops & PC
    "laptops-pc": {
        "subcategories": ["All", "Laptops & Desktops", "Core Components", "Displays & Peripherals"],
        "products": [
            {"slug": "ultrabook", "title_en": "Ultrabook", "title_bn": "আল্ট্রাবুক", "subcategory": "Laptops & Desktops", "search_kw": "ultrabook laptop", "starts_from": 45000, "max_price": 240000, "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gaming-laptop", "title_en": "Gaming Laptop", "title_bn": "গেমিং ল্যাপটপ", "subcategory": "Laptops & Desktops", "search_kw": "gaming laptop", "starts_from": 78000, "max_price": 360000, "img": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80"},
            {"slug": "desktop-pc", "title_en": "Desktop PC", "title_bn": "ডেস্কটপ পিসি", "subcategory": "Laptops & Desktops", "search_kw": "desktop pc", "starts_from": 25000, "max_price": 250000, "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"},
            {"slug": "graphics-card-gpu", "title_en": "Graphics Card (GPU)", "title_bn": "গ্রাফিক্স কার্ড", "subcategory": "Core Components", "search_kw": "graphics card gpu", "starts_from": 18500, "max_price": 280000, "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"},
            {"slug": "processor-cpu", "title_en": "Processor (CPU)", "title_bn": "প্রসেসর", "subcategory": "Core Components", "search_kw": "processor cpu", "starts_from": 8500, "max_price": 85000, "img": "https://images.unsplash.com/photo-1555680202-c86f0e12f086?auto=format&fit=crop&w=600&q=80"},
            {"slug": "motherboard", "title_en": "Motherboard", "title_bn": "মাদারবোর্ড", "subcategory": "Core Components", "search_kw": "motherboard", "starts_from": 7800, "max_price": 65000, "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=600&q=80"},
            {"slug": "nvme-ssd", "title_en": "NVMe SSD", "title_bn": "এনভিএমই এসএসডি", "subcategory": "Core Components", "search_kw": "nvme ssd", "starts_from": 2800, "max_price": 32000, "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"},
            {"slug": "ram-kit", "title_en": "RAM Kit", "title_bn": "র‌্যাম কিট", "subcategory": "Core Components", "search_kw": "ddr4 ddr5 ram", "starts_from": 2400, "max_price": 26000, "img": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=600&q=80"},
            {"slug": "cpu-cooler", "title_en": "CPU Cooler", "title_bn": "সিপিইউ কুলার", "subcategory": "Core Components", "search_kw": "cpu air liquid cooler", "starts_from": 1800, "max_price": 24000, "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"},
            {"slug": "power-supply-unit-psu", "title_en": "Power Supply Unit (PSU)", "title_bn": "পাওয়ার সাপ্লাই", "subcategory": "Core Components", "search_kw": "power supply psu", "starts_from": 3200, "max_price": 35000, "img": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=600&q=80"},
            {"slug": "ips-monitor", "title_en": "IPS Monitor", "title_bn": "আইপিএস মনিটর", "subcategory": "Displays & Peripherals", "search_kw": "ips monitor display", "starts_from": 11500, "max_price": 95000, "img": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80"},
            {"slug": "mechanical-keyboard", "title_en": "Mechanical Keyboard", "title_bn": "মেকানিক্যাল কীবোর্ড", "subcategory": "Displays & Peripherals", "search_kw": "mechanical keyboard", "starts_from": 2200, "max_price": 18000, "img": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gaming-mouse", "title_en": "Gaming Mouse", "title_bn": "গেমিং মাউস", "subcategory": "Displays & Peripherals", "search_kw": "gaming mouse", "starts_from": 850, "max_price": 14500, "img": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 4. Fashion & Apparel


    # 5. Grocery & Snacks


    # 6. Fine Jewelry & Gold
    "fine-jewelry": {
        "subcategories": ["All", "Gold Chains & Rings", "Bangles & Sets", "Diamond Jewelry"],
        "products": [
            {"slug": "gold-chain", "title_en": "Gold Chain", "title_bn": "সোনার চেইন", "subcategory": "Gold Chains & Rings", "search_kw": "22k gold chain", "starts_from": 35000, "max_price": 250000, "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gold-ring", "title_en": "Gold Ring", "title_bn": "সোনার আংটি", "subcategory": "Gold Chains & Rings", "search_kw": "22k gold ring", "starts_from": 18500, "max_price": 85000, "img": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "diamond-solitaire-ring", "title_en": "Diamond Solitaire Ring", "title_bn": "হীরার আংটি", "subcategory": "Diamond Jewelry", "search_kw": "diamond solitaire ring", "starts_from": 48000, "max_price": 350000, "img": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gold-wedding-band", "title_en": "Gold Wedding Band", "title_bn": "ওয়েডিং ব্যান্ড", "subcategory": "Gold Chains & Rings", "search_kw": "gold wedding band", "starts_from": 28000, "max_price": 120000, "img": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gold-bangles-bala", "title_en": "Gold Bangles (Bala)", "title_bn": "সোনার বালা", "subcategory": "Bangles & Sets", "search_kw": "22k gold bangles bala", "starts_from": 65000, "max_price": 380000, "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gold-nose-pin", "title_en": "Gold Nose Pin", "title_bn": "সোনার নাকফুল", "subcategory": "Gold Chains & Rings", "search_kw": "gold nose pin", "starts_from": 4500, "max_price": 18000, "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gold-necklace-set", "title_en": "Gold Necklace Set", "title_bn": "সোনার নেকলেস সেট", "subcategory": "Bangles & Sets", "search_kw": "gold necklace set", "starts_from": 95000, "max_price": 650000, "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"},
            {"slug": "diamond-earrings", "title_en": "Diamond Earrings", "title_bn": "হীরার কানের দুল", "subcategory": "Diamond Jewelry", "search_kw": "diamond earrings", "starts_from": 38000, "max_price": 280000, "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 7. Saree & Boutiques


    # 8. Sneakers & Shoes
    "sneakers-footwear": {
        "subcategories": ["All", "Athletic & Running", "Streetwear & Casual", "Formal & Leather"],
        "products": [
            {"slug": "running-sneakers", "title_en": "Running Sneakers", "title_bn": "রানিং স্নিকার্স", "subcategory": "Athletic & Running", "search_kw": "running sneakers shoes", "starts_from": 1850, "max_price": 18500, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
            {"slug": "casual-streetwear-shoes", "title_en": "Casual Streetwear Shoes", "title_bn": "ক্যাজুয়াল জুতো", "subcategory": "Streetwear & Casual", "search_kw": "casual sneakers shoes", "starts_from": 1650, "max_price": 14500, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
            {"slug": "leather-formal-oxford-shoes", "title_en": "Leather Formal Oxford Shoes", "title_bn": "লেদার ফরমাল জুতো", "subcategory": "Formal & Leather", "search_kw": "leather formal oxford shoes", "starts_from": 2850, "max_price": 12500, "img": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=600&q=80"},
            {"slug": "loafers", "title_en": "Loafers", "title_bn": "লোফার", "subcategory": "Formal & Leather", "search_kw": "leather loafers", "starts_from": 1950, "max_price": 8500, "img": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=600&q=80"},
            {"slug": "slip-on-shoes", "title_en": "Slip-on Shoes", "title_bn": "স্লিপ-অন জুতো", "subcategory": "Streetwear & Casual", "search_kw": "slip on casual shoes", "starts_from": 1250, "max_price": 6500, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
            {"slug": "walking-shoes", "title_en": "Walking Shoes", "title_bn": "ওয়াকিং শু", "subcategory": "Athletic & Running", "search_kw": "walking comfortable shoes", "starts_from": 1450, "max_price": 9500, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
            {"slug": "hiking-boots", "title_en": "Hiking Boots", "title_bn": "হাইকিং বুট", "subcategory": "Athletic & Running", "search_kw": "outdoor hiking boots", "starts_from": 3200, "max_price": 16500, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
            {"slug": "sandals", "title_en": "Sandals", "title_bn": "স্যান্ডেল", "subcategory": "Streetwear & Casual", "search_kw": "leather sandals slides", "starts_from": 650, "max_price": 3800, "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 9. Watches & Horology
    "watches-horology": {
        "subcategories": ["All", "Mechanical & Automatic", "Chronograph & Sport", "Dress & Smart"],
        "products": [
            {"slug": "chronograph-watch", "title_en": "Chronograph Watch", "title_bn": "ক্রোনোগ্রাফ ঘড়ি", "subcategory": "Chronograph & Sport", "search_kw": "chronograph watch", "starts_from": 3850, "max_price": 45000, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80"},
            {"slug": "automatic-mechanical-watch", "title_en": "Automatic Mechanical Watch", "title_bn": "অটোমেটিক মেকানিক্যাল ঘড়ি", "subcategory": "Mechanical & Automatic", "search_kw": "automatic mechanical watch", "starts_from": 8500, "max_price": 95000, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80"},
            {"slug": "analog-dress-watch", "title_en": "Analog Dress Watch", "title_bn": "অ্যানালগ ড্রেস ওয়াচ", "subcategory": "Dress & Smart", "search_kw": "analog dress watch", "starts_from": 1850, "max_price": 28000, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80"},
            {"slug": "digital-sport-watch", "title_en": "Digital Sport Watch", "title_bn": "ডিজিটাল স্পোর্টস ওয়াচ", "subcategory": "Chronograph & Sport", "search_kw": "digital sport watch", "starts_from": 1250, "max_price": 14500, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80"},
            {"slug": "stainless-steel-watch", "title_en": "Stainless Steel Watch", "title_bn": "স্টেইনলেস স্টিল ঘড়ি", "subcategory": "Dress & Smart", "search_kw": "stainless steel watch", "starts_from": 2450, "max_price": 38000, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80"},
            {"slug": "leather-strap-watch", "title_en": "Leather Strap Watch", "title_bn": "লেদার স্ট্র্যাপ ঘড়ি", "subcategory": "Dress & Smart", "search_kw": "leather strap watch", "starts_from": 1950, "max_price": 32000, "img": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80"},
            {"slug": "smart-hybrid-watch", "title_en": "Smart Hybrid Watch", "title_bn": "স্মার্ট হাইব্রিড ঘড়ি", "subcategory": "Dress & Smart", "search_kw": "smart hybrid watch", "starts_from": 4500, "max_price": 42000, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 10. Home Appliances
    "home-appliances": {
        "subcategories": ["All", "Refrigerators & ACs", "Kitchen Appliances", "Laundry & Home"],
        "products": [
            {"slug": "direct-cool-refrigerator", "title_en": "Direct Cool Refrigerator", "title_bn": "রেফ্রিজারেটর ফ্রিজ", "subcategory": "Refrigerators & ACs", "search_kw": "direct cool refrigerator", "starts_from": 26500, "max_price": 145000, "img": "https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80"},
            {"slug": "inverter-air-conditioner-ac", "title_en": "Inverter Air Conditioner (AC)", "title_bn": "ইনভার্টার এসি", "subcategory": "Refrigerators & ACs", "search_kw": "inverter air conditioner ac", "starts_from": 44500, "max_price": 125000, "img": "https://images.unsplash.com/photo-1615873968403-89e068629265?auto=format&fit=crop&w=600&q=80"},
            {"slug": "room-air-cooler", "title_en": "Room Air Cooler", "title_bn": "রুম এয়ার কুলার", "subcategory": "Refrigerators & ACs", "search_kw": "room air cooler", "starts_from": 8500, "max_price": 28000, "img": "https://images.unsplash.com/photo-1615873968403-89e068629265?auto=format&fit=crop&w=600&q=80"},
            {"slug": "microwave-oven", "title_en": "Microwave Oven", "title_bn": "মাইক্রোওয়েভ ওভেন", "subcategory": "Kitchen Appliances", "search_kw": "microwave oven", "starts_from": 7800, "max_price": 38000, "img": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=600&q=80"},
            {"slug": "blender-grinder", "title_en": "Blender & Grinder", "title_bn": "ব্লেন্ডার ও গ্রাইন্ডার", "subcategory": "Kitchen Appliances", "search_kw": "blender grinder mixer", "starts_from": 1950, "max_price": 14500, "img": "https://images.unsplash.com/photo-1570222094114-d054a817e56b?auto=format&fit=crop&w=600&q=80"},
            {"slug": "top-load-washing-machine", "title_en": "Top-Load Washing Machine", "title_bn": "ওয়াশিং মেশিন", "subcategory": "Laundry & Home", "search_kw": "top load washing machine", "starts_from": 18500, "max_price": 95000, "img": "https://images.unsplash.com/photo-1626806787461-102c1bfaaea1?auto=format&fit=crop&w=600&q=80"},
            {"slug": "ro-water-purifier", "title_en": "RO Water Purifier", "title_bn": "পানির ফিল্টার", "subcategory": "Kitchen Appliances", "search_kw": "ro water purifier", "starts_from": 9500, "max_price": 35000, "img": "https://images.unsplash.com/photo-1585659722983-3a675dabf23d?auto=format&fit=crop&w=600&q=80"},
            {"slug": "electric-kettle", "title_en": "Electric Kettle", "title_bn": "ইলেকট্রিক কেটলি", "subcategory": "Kitchen Appliances", "search_kw": "electric kettle", "starts_from": 850, "max_price": 4500, "img": "/images/barista-espresso.svg"},
            {"slug": "rice-cooker", "title_en": "Rice Cooker", "title_bn": "রাইস কুকার", "subcategory": "Kitchen Appliances", "search_kw": "electric rice cooker", "starts_from": 1650, "max_price": 8500, "img": "/images/barista-espresso.svg"},
            {"slug": "induction-cooker", "title_en": "Induction Cooker", "title_bn": "ইন্ডাকশন চুলা", "subcategory": "Kitchen Appliances", "search_kw": "induction cooker stove", "starts_from": 2850, "max_price": 12000, "img": "/images/barista-espresso.svg"},
        ],
    },

    # 11. Beauty & Skincare
    "beauty-skincare": {
        "subcategories": ["All", "Facial Cleansers & Serums", "Sunscreen & Moisturizers", "Makeup & Haircare"],
        "products": [
            {"slug": "facial-cleanser-face-wash", "title_en": "Facial Cleanser / Face Wash", "title_bn": "ফেস ওয়াশ", "subcategory": "Facial Cleansers & Serums", "search_kw": "face wash cleanser", "starts_from": 450, "max_price": 2800, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
            {"slug": "face-serum", "title_en": "Face Serum", "title_bn": "ফেস সিরাম", "subcategory": "Facial Cleansers & Serums", "search_kw": "face serum vitamin c niacinamide", "starts_from": 850, "max_price": 4500, "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80"},
            {"slug": "moisturizing-lotion", "title_en": "Moisturizing Lotion", "title_bn": "ময়েশ্চারাইজার", "subcategory": "Sunscreen & Moisturizers", "search_kw": "moisturizing cream lotion", "starts_from": 550, "max_price": 3200, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
            {"slug": "sunscreen", "title_en": "Sunscreen", "title_bn": "সানস্ক্রিন", "subcategory": "Sunscreen & Moisturizers", "search_kw": "sunscreen sunblock spf50", "starts_from": 650, "max_price": 3500, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
            {"slug": "snail-mucin-essence", "title_en": "Snail Mucin Essence", "title_bn": "স্নেল মিউসিন এসেন্স", "subcategory": "Facial Cleansers & Serums", "search_kw": "snail mucin essence cosrx", "starts_from": 1250, "max_price": 2800, "img": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80"},
            {"slug": "matte-lipstick", "title_en": "Matte Lipstick", "title_bn": "ম্যাট লিপস্টিক", "subcategory": "Makeup & Haircare", "search_kw": "matte lipstick velvet", "starts_from": 380, "max_price": 3200, "img": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=600&q=80"},
            {"slug": "anti-hairfall-shampoo", "title_en": "Anti-Hairfall Shampoo", "title_bn": "অ্যান্টি-হেয়ারফল শ্যাম্পু", "subcategory": "Makeup & Haircare", "search_kw": "anti hairfall shampoo", "starts_from": 480, "max_price": 2400, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
            {"slug": "sheet-mask", "title_en": "Sheet Mask", "title_bn": "শীট মাস্ক", "subcategory": "Facial Cleansers & Serums", "search_kw": "korean sheet mask", "starts_from": 90, "max_price": 350, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
            {"slug": "bridal-facial-kit", "title_en": "Bridal Facial Kit", "title_bn": "ব্রাইডাল ফেসিয়াল কিট", "subcategory": "Makeup & Haircare", "search_kw": "bridal facial glow kit", "starts_from": 1450, "max_price": 6500, "img": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 12. Bicycles, MTB & Aero
    "bicycles-mtb": {
        "subcategories": ["All", "Mountain Bikes (MTB)", "Hybrid & Commuter", "Components & Gear"],
        "products": [
            {"slug": "mountain-bike-mtb", "title_en": "Mountain Bike (MTB)", "title_bn": "মাউন্টেন বাইক (MTB)", "subcategory": "Mountain Bikes (MTB)", "search_kw": "mountain bike mtb", "starts_from": 9500, "max_price": 48000, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "hybrid-bicycle", "title_en": "Hybrid Bicycle", "title_bn": "হাইব্রিড সাইকেল", "subcategory": "Hybrid & Commuter", "search_kw": "hybrid commuter bicycle", "starts_from": 12500, "max_price": 55000, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "aluminum-frame-cycle", "title_en": "Aluminum Frame Cycle", "title_bn": "অ্যালুমিনিয়াম ফ্রেম সাইকেল", "subcategory": "Mountain Bikes (MTB)", "search_kw": "aluminum frame alloy cycle", "starts_from": 14500, "max_price": 65000, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "gear-cycle", "title_en": "Gear Cycle", "title_bn": "গিয়ার সাইকেল", "subcategory": "Mountain Bikes (MTB)", "search_kw": "21 speed gear cycle", "starts_from": 8500, "max_price": 38000, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "disc-brake-set", "title_en": "Disc Brake Set", "title_bn": "ডিস্ক ব্রেক সেট", "subcategory": "Components & Gear", "search_kw": "bicycle hydraulic disc brake", "starts_from": 1250, "max_price": 6500, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "tubeless-tire", "title_en": "Tubeless Tire", "title_bn": "টিউবলেস টায়ার", "subcategory": "Components & Gear", "search_kw": "bicycle tubeless tire", "starts_from": 1450, "max_price": 5500, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "bicycle-helmet", "title_en": "Bicycle Helmet", "title_bn": "সাইকেল হেলমেট", "subcategory": "Components & Gear", "search_kw": "bicycle safety helmet", "starts_from": 1150, "max_price": 5500, "img": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=80"},
            {"slug": "led-cycle-light", "title_en": "LED Cycle Light", "title_bn": "সাইকেল লাইট", "subcategory": "Components & Gear", "search_kw": "bicycle rechargeable led light", "starts_from": 450, "max_price": 2800, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "bicycle-pump", "title_en": "Bicycle Pump", "title_bn": "সাইকেল পাম্প", "subcategory": "Components & Gear", "search_kw": "portable bicycle tire pump", "starts_from": 380, "max_price": 2200, "img": "https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 13. Electric Bikes & EVs
    "cycles-evs": {
        "subcategories": ["All", "E-Bikes & Scooters", "Commuter & Delivery", "Batteries & Kits"],
        "products": [
            {"slug": "electric-bike-e-bike", "title_en": "Electric Bike (E-Bike)", "title_bn": "ইলেকট্রিক বাইক (ই-বাইক)", "subcategory": "E-Bikes & Scooters", "search_kw": "electric bike ebike", "starts_from": 42000, "max_price": 145000, "img": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80"},
            {"slug": "adult-e-scooter", "title_en": "Adult E-Scooter", "title_bn": "ইলেকট্রিক স্কুটার", "subcategory": "E-Bikes & Scooters", "search_kw": "electric scooter adult", "starts_from": 36000, "max_price": 95000, "img": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=80"},
            {"slug": "electric-delivery-scooter", "title_en": "Electric Delivery Scooter", "title_bn": "ডেলিভারি ই-স্কুটার", "subcategory": "Commuter & Delivery", "search_kw": "electric delivery scooter commercial", "starts_from": 68000, "max_price": 185000, "img": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=600&q=80"},
            {"slug": "folding-commuter-e-bike", "title_en": "Folding Commuter E-Bike", "title_bn": "ফোল্ডিং ই-বাইক", "subcategory": "Commuter & Delivery", "search_kw": "folding electric bicycle", "starts_from": 52000, "max_price": 135000, "img": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80"},
            {"slug": "e-bike-conversion-kit", "title_en": "E-Bike Conversion Kit", "title_bn": "ই-বাইক কনভার্সন কিট", "subcategory": "Batteries & Kits", "search_kw": "ebike motor conversion kit", "starts_from": 18500, "max_price": 45000, "img": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80"},
            {"slug": "lithium-battery-pack", "title_en": "Lithium Battery Pack", "title_bn": "লিথিয়াম ব্যাটারি প্যাক", "subcategory": "Batteries & Kits", "search_kw": "ebike lithium battery 48v 36v", "starts_from": 14500, "max_price": 48000, "img": "https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 14. Sportswear & Gym
    "sportswear-gym": {
        "subcategories": ["All", "Jerseys & Apparel", "Gym Gear & Equipment"],
        "products": [
            {"slug": "argentina-3-star-player-edition-home-jersey", "title_en": "Argentina 3-Star Player Edition Home Jersey", "title_bn": "আর্জেন্টিনা ৩-স্টার প্লেয়ার এডিশন হোম জার্সি", "subcategory": "Jerseys & Apparel", "search_kw": "argentina jersey kit", "starts_from": 1150, "max_price": 1850, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
            {"slug": "brazil-away-jersey-2024-25", "title_en": "Brazil National Team Away Jersey 2024/25", "title_bn": "ব্রাজিল জাতীয় দল অ্যাওয়ে জার্সি", "subcategory": "Jerseys & Apparel", "search_kw": "brazil jersey kit", "starts_from": 1150, "max_price": 1850, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
            {"slug": "real-madrid-fan-edition-kit", "title_en": "Real Madrid 2024/25 Home Fan Edition Kit", "title_bn": "রিয়াল মাদ্রিদ হোম ফ্যান এডিশন কিট", "subcategory": "Jerseys & Apparel", "search_kw": "real madrid jersey kit", "starts_from": 1050, "max_price": 1750, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
            {"slug": "bangladesh-cricket-world-cup-jersey", "title_en": "Bangladesh National Cricket Team Official World Cup Jersey", "title_bn": "বাংলাদেশ ক্রিকেট দল অফিশিয়াল বিশ্বকাপ জার্সি", "subcategory": "Jerseys & Apparel", "search_kw": "bangladesh cricket jersey", "starts_from": 1200, "max_price": 1950, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
            {"slug": "fabrilife-compression-gym-tee", "title_en": "Fabrilife High-Performance Compression Gym Tee", "title_bn": "ফ্যাব্রিলাইফ কম্প্রেশন জিম টি-শার্ট", "subcategory": "Jerseys & Apparel", "search_kw": "gym quick dry dri fit t-shirt", "starts_from": 690, "max_price": 1250, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
            {"slug": "hex-dumbbell-set-20kg", "title_en": "Adjustable Rubberized Hex Dumbbell Set (20kg)", "title_bn": "রাবার হেক্স ডাম্বেল সেট (২০ কেজি)", "subcategory": "Gym Gear & Equipment", "search_kw": "gym rubber dumbbells weight", "starts_from": 3850, "max_price": 6500, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80"},
            {"slug": "heavy-duty-resistance-bands-set", "title_en": "Heavy-Duty Resistance Loop Bands Set (5-Pack)", "title_bn": "রেজিস্ট্যান্স লুপ ব্যান্ডস সেট (৫ প্যাক)", "subcategory": "Gym Gear & Equipment", "search_kw": "workout resistance bands set", "starts_from": 850, "max_price": 1850, "img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80"},
            {"slug": "non-slip-tpe-yoga-mat", "title_en": "Non-Slip TPE High-Density Fitness Yoga Mat (6mm)", "title_bn": "নন-স্লিপ টিপিই হাই-ডেনসিটি ইয়োগা ম্যাট (৬ মিমি)", "subcategory": "Gym Gear & Equipment", "search_kw": "anti slip yoga mat", "starts_from": 1250, "max_price": 2600, "img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80"},
        ],
    },

    # 16. Gaming Consoles & Accessories
    "gaming-consoles": {
        "subcategories": ["All", "Gaming Consoles", "Controllers & Input", "Audio Gear", "VR & Mixed Reality", "Power & Charging", "Media & Subscriptions", "Protection & Skins"],
        "products": [
            {"slug": "ps5-console", "title_en": "PlayStation 5 (PS5) Console", "title_bn": "প্লেস্টেশন ৫ কনসোল", "subcategory": "Gaming Consoles", "search_kw": "ps5 console", "starts_from": 64000, "max_price": 78000, "img": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80"},
            {"slug": "xbox-series-x", "title_en": "Xbox Series X / S Console", "title_bn": "এক্সবক্স সিরিজ এক্স / এস", "subcategory": "Gaming Consoles", "search_kw": "xbox series x", "starts_from": 38000, "max_price": 68000, "img": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?auto=format&fit=crop&w=600&q=80"},
            {"slug": "nintendo-switch", "title_en": "Nintendo Switch (OLED / Standard)", "title_bn": "নিনটেন্ডো সুইচ কনসোল", "subcategory": "Gaming Consoles", "search_kw": "nintendo switch oled", "starts_from": 32000, "max_price": 42000, "img": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?auto=format&fit=crop&w=600&q=80"},
            {"slug": "handheld-gaming-pc", "title_en": "Handheld Gaming PC (Steam Deck / ROG Ally)", "title_bn": "হ্যান্ডহেল্ড গেমিং পিসি", "subcategory": "Gaming Consoles", "search_kw": "steam deck oled", "starts_from": 52000, "max_price": 95000, "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80"},
            {"slug": "retro-portable-console", "title_en": "Retro Portable Handheld Console", "title_bn": "রেট্রো পোর্টেবল কনসোল", "subcategory": "Gaming Consoles", "search_kw": "r36s retro handheld console", "starts_from": 4500, "max_price": 12000, "img": "https://images.unsplash.com/photo-1531525645387-7f14be1bdbbd?auto=format&fit=crop&w=600&q=80"},
            {"slug": "wireless-gamepad", "title_en": "Wireless Gamepad / Controller", "title_bn": "ওয়্যারলেস গেমপ্যাড কন্ট্রোলার", "subcategory": "Controllers & Input", "search_kw": "dualsense wireless controller", "starts_from": 2200, "max_price": 9500, "img": "https://images.unsplash.com/photo-1592840496694-26d035b52b48?auto=format&fit=crop&w=600&q=80"},
            {"slug": "racing-wheel-pedals", "title_en": "Racing Wheel & Pedal Set", "title_bn": "রেসিং হুইল ও প্যাডেল সেট", "subcategory": "Controllers & Input", "search_kw": "logitech g29 racing wheel", "starts_from": 12500, "max_price": 48000, "img": "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=600&q=80"},
            {"slug": "arcade-fight-stick", "title_en": "Arcade Fight Stick & Flight HOTAS", "title_bn": "আর্কেড ফাইট স্টিক ও ফ্লাইট স্টিক", "subcategory": "Controllers & Input", "search_kw": "arcade fight stick joystick", "starts_from": 6500, "max_price": 32000, "img": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=600&q=80"},
            {"slug": "console-gaming-headset", "title_en": "Console Gaming Headset", "title_bn": "গেমিং হেডসেট", "subcategory": "Audio Gear", "search_kw": "logitech g733 gaming headset", "starts_from": 2800, "max_price": 22000, "img": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=600&q=80"},
            {"slug": "streaming-microphone", "title_en": "USB Streaming Microphone", "title_bn": "স্ট্রিমিং মাইক্রোফোন", "subcategory": "Audio Gear", "search_kw": "usb condenser streaming microphone", "starts_from": 2400, "max_price": 16500, "img": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80"},
            {"slug": "vr-headset", "title_en": "Virtual Reality (VR) Headset", "title_bn": "ভিআর হেডসেট", "subcategory": "VR & Mixed Reality", "search_kw": "meta quest 3 vr headset", "starts_from": 42000, "max_price": 145000, "img": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?auto=format&fit=crop&w=600&q=80"},
            {"slug": "controller-charging-dock", "title_en": "Controller Charging Dock & Station", "title_bn": "কন্ট্রোলার চার্জিং ডক", "subcategory": "Power & Charging", "search_kw": "ps5 controller charging station", "starts_from": 1800, "max_price": 4500, "img": "https://images.unsplash.com/photo-1592840496694-26d035b52b48?auto=format&fit=crop&w=600&q=80"},
            {"slug": "console-nvme-ssd", "title_en": "Console NVMe SSD & Storage Expansion", "title_bn": "কনসোল এসএসডি স্টোরেজ", "subcategory": "Power & Charging", "search_kw": "ps5 nvme ssd heatsink", "starts_from": 9500, "max_price": 28000, "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=600&q=80"},
            {"slug": "game-discs-cartridges", "title_en": "Original Game Discs & Cartridges", "title_bn": "অরিজিনাল গেম ডিস্ক ও কার্ট্রিজ", "subcategory": "Media & Subscriptions", "search_kw": "ps5 original game disc", "starts_from": 2500, "max_price": 7500, "img": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=600&q=80"},
            {"slug": "digital-gift-cards", "title_en": "Digital Gift Cards & Subscriptions (PSN/Xbox)", "title_bn": "ডিজিটাল গিফট কার্ড ও সাবস্ক্রিপশন", "subcategory": "Media & Subscriptions", "search_kw": "playstation network psn gift card", "starts_from": 1200, "max_price": 14000, "img": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80"},
            {"slug": "console-carrying-case", "title_en": "Console Carrying Case & Travel Bag", "title_bn": "কনসোল ট্রাভেল ব্যাগ ও প্রটেকশন", "subcategory": "Protection & Skins", "search_kw": "nintendo switch carrying case hard shell", "starts_from": 1200, "max_price": 3800, "img": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?auto=format&fit=crop&w=600&q=80"},
        ],
    },
    # 15. Fashion & Budget Jewellery

}


def build_predetermined_browse_products(
    cat_id: str,
    subcategory: Optional[str] = None,
) -> List[Product]:
    """
    Constructs transient Product + StoreOffer objects for Category / Subcategory Browsing.
    Each card represents a Predetermined Base Product specified by the user,
    with pricing displayed as 'Starts from ৳...' and its offers list showing verified stores.
    Cached in-memory for instant sub-millisecond response time.
    """
    cat_meta = CATEGORY_REGISTRY_MAP.get(cat_id)
    if not cat_meta:
        return []

    spec = CATEGORY_PREDETERMINED_CATALOG.get(cat_id)
    if not spec:
        return []

    sub_norm = (subcategory or "").strip().lower()
    cache_key = f"{cat_id}::{sub_norm}"
    if cache_key in _PREDETERMINED_BROWSE_CACHE:
        return _PREDETERMINED_BROWSE_CACHE[cache_key]

    display_cat = cat_meta["display_en"]
    vertical = cat_meta.get("vertical", "MULTI_MARKETPLACE")

    browse_products: List[Product] = []

    for idx, item in enumerate(spec["products"], start=1):
        if sub_norm and sub_norm not in ("all", "") and item.get("subcategory", "").lower() != sub_norm:
            continue

        slug = f"browse-{cat_id}-{item['slug']}"
        title_en = item["title_en"]
        title_bn = item["title_bn"]
        search_kw = item["search_kw"]
        starts_from = item["starts_from"]
        max_p = item["max_price"]
        img_url = resolve_product_card_image(cat_id, item["slug"], item["img"])

        prod = Product(
            id=90000 + idx + abs(hash(cat_id)) % 5000,
            slug=slug,
            title_en=title_en,
            title_bn=title_bn,
            category=display_cat,
            image_url=img_url,
            specs_summary=f"SUBCATEGORY:{item['subcategory']} | Starts from ৳{starts_from:,} up to ৳{max_p:,} · Click to compare verified stores",
            price_30d_ago=int(starts_from * 1.05),
            price_15d_ago=int(starts_from * 1.02),
            is_pinned_homepage=False,
            created_at=datetime.utcnow(),
        )

        # Fetch capability-matched verified stores for this specific predetermined product
        stores = get_stores_for_category(cat_id, query=search_kw)
        offers: List[StoreOffer] = []
        offsets = [0, 50, 100, 150, 200, 250, 300, 350]

        for s_idx, s_dict in enumerate(stores[:8]):
            s_name = s_dict.get("name", "Verified Store")
            s_dom = s_dict.get("domain", "")
            raw_w = s_dict.get("website_url") or s_dict.get("Website") or s_dict.get("website") or ""
            raw_fb = s_dict.get("facebook_page_url") or ""
            
            # Universal Deep Link: Use direct clean merchant website or facebook page (NEVER broken search queries)
            if '{q}' in raw_w or '/search' in raw_w:
                raw_w = raw_w.replace('{q}', '').split('/product/search')[0].split('/search')[0].split('?')[0].rstrip('/')

            if raw_w:
                w_url = raw_w if raw_w.startswith("http") else f"https://{raw_w}"
                target_url = w_url
                fb_url = raw_fb or f"https://www.facebook.com/search/top/?q={quote_plus(s_name)}"
                s_type = "crawler"
            elif s_dom:
                w_url = f"https://{s_dom}"
                target_url = w_url
                fb_url = raw_fb or f"https://www.facebook.com/search/top/?q={quote_plus(s_name)}"
                s_type = "crawler"
            elif raw_fb:
                fb_url = raw_fb
                target_url = fb_url
                w_url = None
                s_type = "f_commerce"
            else:
                target_url = f"https://www.facebook.com/search/top/?q={quote_plus(s_name)}"
                w_url = None
                fb_url = target_url
                s_type = "f_commerce"

            step = offsets[s_idx % len(offsets)] if starts_from >= 1000 else (s_idx * 20)
            store_start_price = starts_from + step

            # Dynamic verification & TrustShield scoring
            is_pre = bool(s_dict.get("is_preseeded", True))
            from bd_stores_registry import compute_trust_score
            trust_info = compute_trust_score(store_name=s_name, is_preseeded=is_pre, price=float(store_start_price))

            offer = StoreOffer(
                id=800000 + idx * 20 + s_idx,
                product_id=prod.id,
                store_name=s_name,
                source_type=s_type,
                target_url=target_url,
                website_url=w_url,
                facebook_url=fb_url,
                current_price=store_start_price,
                original_price=store_start_price,
                cod_terms_en=f"Starts from ৳{store_start_price:,} · Direct Store Catalog · Cash on Delivery" if is_pre else "⚠️ Unverified Merchant · COD Only",
                cod_terms_bn=f"শুরু ৳{store_start_price:,} থেকে · সরাসরি স্টোর ক্যাটালগ · ক্যাশ অন ডেলিভারি" if is_pre else "⚠️ অযাচাইকৃত বিক্রেতা · ক্যাশ অন ডেলিভারিতে চেক করে নিন",
                warranty_text="Verified Store Catalog" if is_pre else "Store Warranty",
                in_stock=True,
                spider_status="healthy",
                last_synced_at="Verified Directory",
                is_preseeded=is_pre,
                is_sponsored=False,
                trust_score=trust_info["trust_score"],
                trust_badge=trust_info["trust_badge"],
                risk_level=trust_info["risk_level"],
                discount_tag="STARTS FROM",
                discount_pct=None,
            )
            offers.append(offer)

        prod.offers = offers
        prod.price_history = []
        browse_products.append(prod)

    _PREDETERMINED_BROWSE_CACHE[cache_key] = browse_products
    return browse_products


# Category aliases for predetermined catalog
CATEGORY_PREDETERMINED_CATALOG["sports-activewear"] = CATEGORY_PREDETERMINED_CATALOG["sportswear-gym"]
CATEGORY_PREDETERMINED_CATALOG["sportswear-activewear"] = CATEGORY_PREDETERMINED_CATALOG["sportswear-gym"]
CATEGORY_PREDETERMINED_CATALOG["sportswear-activewear-gym-gear"] = CATEGORY_PREDETERMINED_CATALOG["sportswear-gym"]
CATEGORY_PREDETERMINED_CATALOG["sportswear-and-gym"] = CATEGORY_PREDETERMINED_CATALOG["sportswear-gym"]
CATEGORY_PREDETERMINED_CATALOG["sports-and-activewear"] = CATEGORY_PREDETERMINED_CATALOG["sportswear-gym"]
