"""
JaChai Expanded Master Product Catalog SKUs
(backend/expanded_catalog_items.py)

Comprehensive authoritative SKUs across all primary electronics verticals in Bangladesh:
  1. Vivo, Realme, Infinix, Tecno, Motorola, Nothing smartphones
  2. Apple iPads (10th Gen, Air M2, Pro M4, Mini 6) & Mac mini (M4, M4 Pro)
  3. Windows Laptops (Acer Nitro/Aspire, MSI Katana/Cyborg, Lenovo LOQ/Legion/ThinkPad, ASUS TUF/ROG/ZenBook, HP Victus/Pavilion, Dell Inspiron/G15)
  4. PC Hardware: CPUs (Intel 14th/13th Gen, AMD Ryzen 7000/5000), Motherboards (B650, B760), Monitors (165Hz/180Hz IPS), RAM & PSUs
  5. Audio & Wearables: AirPods 4, Sony XM4, Soundcore Liberty 4, Galaxy Buds 3 Pro, Apple Watch S10/SE, Galaxy Watch 7, Amazfit
"""

from typing import Any, Dict, List

EXPANDED_CATALOG_ITEMS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # VIVO SMARTPHONES
    # --------------------------------------------------------------------------
    {
        "slug": "vivo-v40-5g-256gb",
        "model_code": "Vivo V40 5G (256GB)",
        "aliases": ["vivo v40", "vivo v40 5g", "vivo v40 256gb", "vivo v40 256 gb", "v40 5g", "v40"],
        "title_en": "Vivo V40 5G (12GB RAM · 256GB · ZEISS Optics)",
        "title_bn": "ভিভো ভি৪০ ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি · জাইস ক্যামেরা)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Vivo",
        "specs_summary": "Snapdragon 7 Gen 3 · 12GB RAM · 256GB · 6.78-inch 120Hz 3D Curved AMOLED (4500 nits) · Dual 50MP ZEISS OIS Camera · 5500mAh 80W FlashCharge",
        "starting_price": 58990,
        "max_price": 62500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 58990, "url": "https://www.applegadgetsbd.com/product/vivo-v40"},
            {"name": "Star Tech", "price": 59990, "url": "https://www.startech.com.bd/vivo-v40-5g"},
            {"name": "Mobile Dukan BD", "price": 59500, "url": "https://www.mobiledokan.com/vivo-v40"},
            {"name": "Pickaboo", "price": 60990, "url": "https://www.pickaboo.com/product/vivo-v40-5g"},
        ]
    },
    {
        "slug": "vivo-v30-5g-256gb",
        "model_code": "Vivo V30 5G (256GB)",
        "aliases": ["vivo v30", "vivo v30 5g", "vivo v30 256gb", "v30 5g", "v30"],
        "title_en": "Vivo V30 5G (12GB RAM · 256GB · Studio Aura Light)",
        "title_bn": "ভিভো ভি৩০ ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Vivo",
        "specs_summary": "Snapdragon 7 Gen 3 · 12GB RAM · 256GB · 6.78-inch 1.5K 120Hz 3D Curved AMOLED · 50MP OIS Camera + Studio Aura Light · 5000mAh 80W",
        "starting_price": 49990,
        "max_price": 54000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 49990, "url": "https://www.applegadgetsbd.com/product/vivo-v30"},
            {"name": "Star Tech", "price": 50990, "url": "https://www.startech.com.bd/vivo-v30-5g"},
            {"name": "Mobile Dukan BD", "price": 50500, "url": "https://www.mobiledokan.com/vivo-v30"},
        ]
    },
    {
        "slug": "vivo-y28-128gb",
        "model_code": "Vivo Y28 (128GB)",
        "aliases": ["vivo y28", "vivo y28 128gb", "vivo y28 8gb", "y28"],
        "title_en": "Vivo Y28 (8GB RAM · 128GB · 6000mAh Battery)",
        "title_bn": "ভিভো ওয়াই২৮ (৮জিবি র‍্যাম · ১২৮জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Vivo",
        "specs_summary": "Helio G85 · 8GB RAM · 128GB · 6.68-inch 90Hz Sunlit Eye Protection Display · 50MP Dual Camera · 6000mAh 44W FlashCharge",
        "starting_price": 20999,
        "max_price": 22500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 20999, "url": "https://www.applegadgetsbd.com/product/vivo-y28"},
            {"name": "Star Tech", "price": 21499, "url": "https://www.startech.com.bd/vivo-y28"},
            {"name": "Pickaboo", "price": 21999, "url": "https://www.pickaboo.com/product/vivo-y28"},
        ]
    },

    # --------------------------------------------------------------------------
    # REALME SMARTPHONES
    # --------------------------------------------------------------------------
    {
        "slug": "realme-12-pro-plus-5g-256gb",
        "model_code": "Realme 12 Pro+ 5G (256GB)",
        "aliases": ["realme 12 pro plus", "realme 12 pro+", "realme 12 pro+ 5g", "realme 12 pro plus 256gb", "12 pro plus"],
        "title_en": "Realme 12 Pro+ 5G (12GB RAM · 256GB · Periscope Portrait)",
        "title_bn": "রিয়েলমি ১২ প্রো+ ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি · পেরিস্কোপ ক্যামেরা)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Realme",
        "specs_summary": "Snapdragon 7s Gen 2 · 12GB RAM · 256GB · 6.7-inch 120Hz Curved Vision OLED · 64MP Periscope OIS 3x Optical Zoom + 50MP Sony IMX890 · 5000mAh 67W",
        "starting_price": 46990,
        "max_price": 49500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 46990, "url": "https://www.applegadgetsbd.com/product/realme-12-pro-plus-5g"},
            {"name": "Star Tech", "price": 47990, "url": "https://www.startech.com.bd/realme-12-pro-plus-5g"},
            {"name": "Mobile Dukan BD", "price": 47500, "url": "https://www.mobiledokan.com/realme-12-pro-plus"},
        ]
    },
    {
        "slug": "realme-gt-6-256gb",
        "model_code": "Realme GT 6 (256GB)",
        "aliases": ["realme gt 6", "realme gt6", "gt 6", "realme gt 6 256gb"],
        "title_en": "Realme GT 6 (12GB RAM · 256GB · Snapdragon 8s Gen 3)",
        "title_bn": "রিয়েলমি জিটি ৬ (১২জিবি র‍্যাম · ২৫৬জিবি · স্ন্যাপড্রাগন ৮এস জেন ৩)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Realme",
        "specs_summary": "Snapdragon 8s Gen 3 · 12GB LPDDR5X · 256GB UFS 4.0 · 6.78-inch 120Hz 8T LTPO AMOLED 6000 nits · 50MP Sony LYT-808 OIS + 50MP Telephoto · 5500mAh 120W SUPERVOOC",
        "starting_price": 63990,
        "max_price": 67500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 63990, "url": "https://www.applegadgetsbd.com/product/realme-gt-6"},
            {"name": "Custom Mac BD", "price": 64500, "url": "https://custommacbd.com/products/realme-gt-6"},
            {"name": "Star Tech", "price": 65500, "url": "https://www.startech.com.bd/realme-gt-6"},
        ]
    },
    {
        "slug": "realme-c67-128gb",
        "model_code": "Realme C67 (128GB)",
        "aliases": ["realme c67", "realme c67 128gb", "c67"],
        "title_en": "Realme C67 (8GB RAM · 128GB · 108MP 3x In-sensor Zoom)",
        "title_bn": "রিয়েলমি সি৬৭ (৮জিবি র‍্যাম · ১২৮জিবি · ১০৮ মেগাপিক্সেল)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Realme",
        "specs_summary": "Snapdragon 685 6nm · 8GB RAM · 128GB · 6.72-inch 90Hz FHD+ Display · 108MP 3X In-sensor Zoom Camera · 5000mAh 33W SUPERVOOC",
        "starting_price": 19999,
        "max_price": 21500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 19999, "url": "https://www.applegadgetsbd.com/product/realme-c67"},
            {"name": "Star Tech", "price": 20499, "url": "https://www.startech.com.bd/realme-c67"},
            {"name": "Pickaboo", "price": 20999, "url": "https://www.pickaboo.com/product/realme-c67"},
        ]
    },

    # --------------------------------------------------------------------------
    # INFINIX SMARTPHONES
    # --------------------------------------------------------------------------
    {
        "slug": "infinix-note-40-pro-256gb",
        "model_code": "Infinix Note 40 Pro (256GB)",
        "aliases": ["infinix note 40 pro", "note 40 pro", "infinix note 40 pro 256gb"],
        "title_en": "Infinix Note 40 Pro (8GB RAM · 256GB · 3D-Curved AMOLED · MagCharge)",
        "title_bn": "ইনফিনিক্স নোট ৪০ প্রো (৮জিবি র‍্যাম · ২৫৬জিবি · ম্যাগচার্জ)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Infinix",
        "specs_summary": "Helio G99 Ultimate 6nm · 8GB RAM · 256GB · 6.78-inch 120Hz 3D-Curved AMOLED (Corning Gorilla Glass) · 108MP OIS Super-Zoom Camera · 5000mAh 70W Multi-Speed FastCharge + 20W Wireless MagCharge",
        "starting_price": 28999,
        "max_price": 31000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 28999, "url": "https://www.applegadgetsbd.com/product/infinix-note-40-pro"},
            {"name": "Star Tech", "price": 29499, "url": "https://www.startech.com.bd/infinix-note-40-pro"},
            {"name": "Mobile Dukan BD", "price": 29200, "url": "https://www.mobiledokan.com/infinix-note-40-pro"},
        ]
    },
    {
        "slug": "infinix-gt-20-pro-256gb",
        "model_code": "Infinix GT 20 Pro 5G (256GB)",
        "aliases": ["infinix gt 20 pro", "gt 20 pro", "infinix gt 20 pro 5g"],
        "title_en": "Infinix GT 20 Pro 5G (12GB RAM · 256GB · Dedicated Gaming Display Chip)",
        "title_bn": "ইনফিনিক্স জিটি ২০ প্রো ৫জি (১২জিবি র‍্যাম · ২৫৬জিবি · গেমিং ফোন)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Infinix",
        "specs_summary": "Dimensity 8200 Ultimate 4nm · Pixelworks X5 Turbo Gaming Display Chip · 12GB LPDDR5X · 256GB UFS 3.1 · 6.78-inch 144Hz FHD+ AMOLED · Mecha Loop LED Interface · 108MP OIS · 5000mAh 45W",
        "starting_price": 37999,
        "max_price": 40500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 37999, "url": "https://www.applegadgetsbd.com/product/infinix-gt-20-pro"},
            {"name": "Star Tech", "price": 38499, "url": "https://www.startech.com.bd/infinix-gt-20-pro"},
            {"name": "Mobile Dukan BD", "price": 38200, "url": "https://www.mobiledokan.com/infinix-gt-20-pro"},
        ]
    },

    # --------------------------------------------------------------------------
    # TECNO SMARTPHONES
    # --------------------------------------------------------------------------
    {
        "slug": "tecno-camon-30-premier-512gb",
        "model_code": "Tecno Camon 30 Premier 5G (512GB)",
        "aliases": ["tecno camon 30 premier", "camon 30 premier", "camon 30 premier 5g"],
        "title_en": "Tecno Camon 30 Premier 5G (12GB RAM · 512GB · PolarAce Imaging)",
        "title_bn": "টেকনো কেমন ৩০ প্রিমিয়ার ৫জি (১২জিবি র‍্যাম · ৫১২জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Tecno",
        "specs_summary": "Dimensity 8200 Ultimate · Sony CXD5622GG Imaging Chip · 12GB RAM · 512GB · 6.77-inch 1.5K 120Hz LTPO AMOLED · 50MP Sony IMX890 OIS + 50MP Periscope 3X + 50MP Ultrawide · 5000mAh 70W",
        "starting_price": 64990,
        "max_price": 68500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 512GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 64990, "url": "https://www.applegadgetsbd.com/product/tecno-camon-30-premier"},
            {"name": "Star Tech", "price": 65990, "url": "https://www.startech.com.bd/tecno-camon-30-premier"},
            {"name": "Mobile Dukan BD", "price": 65500, "url": "https://www.mobiledokan.com/tecno-camon-30-premier"},
        ]
    },
    {
        "slug": "tecno-spark-20-pro-plus-256gb",
        "model_code": "Tecno Spark 20 Pro+ (256GB)",
        "aliases": ["tecno spark 20 pro plus", "spark 20 pro+", "spark 20 pro plus", "tecno spark 20 pro+"],
        "title_en": "Tecno Spark 20 Pro+ (8GB RAM · 256GB · 120Hz Curved AMOLED)",
        "title_bn": "টেকনো স্পার্ক ২০ প্রো+ (৮জিবি র‍্যাম · ২৫৬জিবি · কার্ভড ডিসপ্লে)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Tecno",
        "specs_summary": "Helio G99 Ultimate 6nm · 8GB RAM · 256GB · 6.78-inch 120Hz Curved AMOLED (Corning Gorilla Glass 5) · 108MP Ultra Sensing Camera · 5000mAh 33W Fast Charge",
        "starting_price": 25999,
        "max_price": 27500,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 25999, "url": "https://www.applegadgetsbd.com/product/tecno-spark-20-pro-plus"},
            {"name": "Star Tech", "price": 26499, "url": "https://www.startech.com.bd/tecno-spark-20-pro-plus"},
            {"name": "Pickaboo", "price": 26999, "url": "https://www.pickaboo.com/product/tecno-spark-20-pro-plus"},
        ]
    },

    # --------------------------------------------------------------------------
    # NOTHING PHONE
    # --------------------------------------------------------------------------
    {
        "slug": "nothing-phone-2a-128gb",
        "model_code": "Nothing Phone (2a) (128GB)",
        "aliases": ["nothing phone 2a", "nothing 2a", "phone 2a", "nothing phone 2a 128gb"],
        "title_en": "Nothing Phone (2a) (8GB RAM · 128GB · Glyph Interface)",
        "title_bn": "নাথিং ফোন (২এ) (৮জিবি র‍্যাম · ১২৮জিবি · গ্লিফ ইন্টারফেস)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Nothing",
        "specs_summary": "Dimensity 7200 Pro 4nm · 8GB RAM · 128GB · 6.7-inch 120Hz Flexible AMOLED (1300 nits) · Dual 50MP Main OIS + 50MP Ultrawide · Iconic Glyph Interface · 5000mAh 45W",
        "starting_price": 38990,
        "max_price": 42000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "8GB RAM · 128GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 38990, "url": "https://www.applegadgetsbd.com/product/nothing-phone-2a"},
            {"name": "Custom Mac BD", "price": 39500, "url": "https://custommacbd.com/products/nothing-phone-2a"},
            {"name": "Star Tech", "price": 40500, "url": "https://www.startech.com.bd/nothing-phone-2a"},
        ]
    },
    {
        "slug": "nothing-phone-2a-256gb",
        "model_code": "Nothing Phone (2a) (256GB)",
        "aliases": ["nothing phone 2a 256gb", "nothing 2a 256gb", "nothing phone 2a 12gb 256gb"],
        "title_en": "Nothing Phone (2a) (12GB RAM · 256GB · Glyph Interface)",
        "title_bn": "নাথিং ফোন (২এ) (১২জিবি র‍্যাম · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Smartphones",
        "brand": "Nothing",
        "specs_summary": "Dimensity 7200 Pro 4nm · 12GB RAM · 256GB · 6.7-inch 120Hz Flexible AMOLED · Dual 50MP OIS · Glyph Interface · 5000mAh 45W",
        "starting_price": 43990,
        "max_price": 47000,
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=600&q=80",
        "variant": "12GB RAM · 256GB",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 43990, "url": "https://www.applegadgetsbd.com/product/nothing-phone-2a"},
            {"name": "Custom Mac BD", "price": 44500, "url": "https://custommacbd.com/products/nothing-phone-2a"},
            {"name": "Star Tech", "price": 45500, "url": "https://www.startech.com.bd/nothing-phone-2a-256gb"},
        ]
    },

    # --------------------------------------------------------------------------
    # APPLE IPADS
    # --------------------------------------------------------------------------
    {
        "slug": "apple-ipad-10th-gen-64gb",
        "model_code": "iPad 10th Gen (64GB WiFi)",
        "aliases": ["ipad 10th gen", "ipad 10", "apple ipad 10", "ipad 10th generation", "ipad 64gb"],
        "title_en": "Apple iPad 10th Gen (10.9-inch Liquid Retina · A14 Bionic · 64GB WiFi)",
        "title_bn": "অ্যাপল আইপ্যাড ১০ম জেনারেশন (১০.৯-ইঞ্চি · ৬৪জিবি ওয়াইফাই)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Tablets",
        "brand": "Apple",
        "specs_summary": "A14 Bionic 6-core CPU 4-core GPU · 10.9-inch Liquid Retina Display with True Tone · 64GB Storage · 12MP Landscape Ultra Wide Front Camera with Center Stage · 12MP Wide Back Camera · USB-C · Touch ID",
        "starting_price": 45990,
        "max_price": 49000,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80",
        "variant": "64GB WiFi",
        "stores": [
            {"name": "Custom Mac BD", "price": 45990, "url": "https://custommacbd.com/products/ipad-10th-gen"},
            {"name": "Apple Gadgets BD", "price": 46500, "url": "https://www.applegadgetsbd.com/product/ipad-10th-gen-64gb"},
            {"name": "Star Tech", "price": 47990, "url": "https://www.startech.com.bd/apple-ipad-10th-gen-64gb"},
            {"name": "Gadget & Gear", "price": 48500, "url": "https://gadgetandgear.com/product/ipad-10th-gen-64gb"},
        ]
    },
    {
        "slug": "apple-ipad-air-m2-11-inch-128gb",
        "model_code": "iPad Air M2 11-inch (128GB WiFi)",
        "aliases": ["ipad air m2", "ipad air 11 m2", "apple ipad air m2", "ipad air 2024", "ipad air 128gb"],
        "title_en": "Apple iPad Air 11-inch (M2 Chip · 8GB RAM · 128GB Storage · WiFi)",
        "title_bn": "অ্যাপল আইপ্যাড এয়ার ১১-ইঞ্চি (এম২ চিপ · ১২৮জিবি ওয়াইফাই)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Tablets",
        "brand": "Apple",
        "specs_summary": "Apple M2 Chip 8-core CPU 9-core GPU · 8GB Unified RAM · 128GB Storage · 11-inch Liquid Retina Display with P3 Wide Color · Landscape 12MP Ultra Wide with Center Stage · Apple Pencil Pro & Magic Keyboard Support",
        "starting_price": 76990,
        "max_price": 82000,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80",
        "variant": "11-inch · 128GB WiFi",
        "stores": [
            {"name": "Custom Mac BD", "price": 76990, "url": "https://custommacbd.com/products/ipad-air-m2-11"},
            {"name": "Apple Gadgets BD", "price": 77500, "url": "https://www.applegadgetsbd.com/product/ipad-air-m2-11-inch"},
            {"name": "Star Tech", "price": 79500, "url": "https://www.startech.com.bd/apple-ipad-air-m2-11-inch"},
        ]
    },
    {
        "slug": "apple-ipad-pro-m4-11-inch-256gb",
        "model_code": "iPad Pro M4 11-inch (256GB WiFi)",
        "aliases": ["ipad pro m4", "ipad pro 11 m4", "apple ipad pro m4", "ipad pro 2024", "ipad pro 256gb"],
        "title_en": "Apple iPad Pro 11-inch (M4 Chip · Ultra Retina XDR OLED · 8GB RAM · 256GB)",
        "title_bn": "অ্যাপল আইপ্যাড প্রো ১১-ইঞ্চি (এম৪ চিপ · ওলেড ডিসপ্লে · ২৫৬জিবি)",
        "category": "Mobiles & Gadgets",
        "subcategory": "Tablets",
        "brand": "Apple",
        "specs_summary": "Apple M4 9-core CPU 10-core GPU with Hardware-Accelerated Ray Tracing · 8GB RAM · 256GB · 11-inch Tandem OLED Ultra Retina XDR ProMotion 120Hz (1600 nits peak HDR) · Impossibly thin 5.3mm design · Thunderbolt / USB 4",
        "starting_price": 126990,
        "max_price": 134000,
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=600&q=80",
        "variant": "11-inch · 256GB WiFi",
        "stores": [
            {"name": "Custom Mac BD", "price": 126990, "url": "https://custommacbd.com/products/ipad-pro-m4-11"},
            {"name": "Apple Gadgets BD", "price": 127990, "url": "https://www.applegadgetsbd.com/product/ipad-pro-m4-11-inch"},
            {"name": "Star Tech", "price": 129990, "url": "https://www.startech.com.bd/apple-ipad-pro-m4-11-inch"},
        ]
    },

    # --------------------------------------------------------------------------
    # APPLE MAC MINI
    # --------------------------------------------------------------------------
    {
        "slug": "apple-mac-mini-m4-16gb-256gb",
        "model_code": "Mac mini M4 (16GB/256GB)",
        "aliases": ["mac mini m4", "apple mac mini m4", "mac mini m4 16gb", "mac mini m4 256gb", "mac mini"],
        "title_en": "Apple Mac mini (M4 Chip · 10-Core CPU · 10-Core GPU · 16GB Unified RAM · 256GB SSD)",
        "title_bn": "অ্যাপল ম্যাক মিনি (এম৪ চিপ · ১৬জিবি ইউনিফাইড র‍্যাম · ২৫৬জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "Desktops & Mac",
        "brand": "Apple",
        "specs_summary": "Apple M4 Chip 10-Core CPU 10-Core GPU with Hardware Ray Tracing · 16GB Unified RAM · 256GB Fast SSD · Ultra-compact 5x5 inch design · 3x Thunderbolt 4 / USB 4 + HDMI + Gigabit Ethernet · Apple Intelligence Ready",
        "starting_price": 82990,
        "max_price": 88000,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80",
        "variant": "16GB RAM · 256GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 82990, "url": "https://custommacbd.com/products/mac-mini-m4"},
            {"name": "Apple Gadgets BD", "price": 83500, "url": "https://www.applegadgetsbd.com/product/mac-mini-m4"},
            {"name": "Star Tech", "price": 85000, "url": "https://www.startech.com.bd/apple-mac-mini-m4"},
            {"name": "Ryans Computers", "price": 86000, "url": "https://www.ryanscomputers.com"},
        ]
    },
    {
        "slug": "apple-mac-mini-m4-16gb-512gb",
        "model_code": "Mac mini M4 (16GB/512GB)",
        "aliases": ["mac mini m4 512gb", "apple mac mini m4 512gb", "mac mini m4 16gb 512gb"],
        "title_en": "Apple Mac mini (M4 Chip · 10-Core CPU · 10-Core GPU · 16GB Unified RAM · 512GB SSD)",
        "title_bn": "অ্যাপল ম্যাক মিনি (এম৪ চিপ · ১৬জিবি র‍্যাম · ৫১২জিবি এসএসডি)",
        "category": "Laptops & PC",
        "subcategory": "Desktops & Mac",
        "brand": "Apple",
        "specs_summary": "Apple M4 Chip 10-Core CPU 10-Core GPU · 16GB Unified RAM · 512GB Fast SSD · 3x Thunderbolt 4 + Front USB-C · Apple Intelligence Ready",
        "starting_price": 108990,
        "max_price": 115000,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80",
        "variant": "16GB RAM · 512GB SSD",
        "stores": [
            {"name": "Custom Mac BD", "price": 108990, "url": "https://custommacbd.com/products/mac-mini-m4-512gb"},
            {"name": "Apple Gadgets BD", "price": 109500, "url": "https://www.applegadgetsbd.com/product/mac-mini-m4-512gb"},
            {"name": "Star Tech", "price": 112000, "url": "https://www.startech.com.bd/apple-mac-mini-m4-512gb"},
        ]
    },

    # --------------------------------------------------------------------------
    # WINDOWS GAMING & PRODUCTIVITY LAPTOPS
    # --------------------------------------------------------------------------
    {
        "slug": "acer-nitro-v-15-rtx4050-16gb",
        "model_code": "Acer Nitro V 15 (i5-13420H / RTX 4050)",
        "aliases": ["acer nitro v 15", "nitro v 15", "acer nitro 5 rtx 4050", "acer nitro v", "nitro v"],
        "title_en": "Acer Nitro V 15 Gaming Laptop (Core i5-13420H · RTX 4050 6GB · 16GB DDR5 · 512GB NVMe · 15.6\" 144Hz IPS)",
        "title_bn": "এসার নাইট্রো ভি ১৫ গেমিং ল্যাপটপ (কোর আই৫ · আরটিএক্স ৪০৫০ · ১৬জিবি ডিডিআর৫)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "Acer",
        "specs_summary": "Intel Core i5-13420H 8-Core · NVIDIA GeForce RTX 4050 6GB GDDR6 (75W TGP) · 16GB DDR5 5200MHz RAM · 512GB PCIe Gen4 SSD · 15.6-inch FHD 144Hz IPS · Dual-Fan Cooling",
        "starting_price": 98500,
        "max_price": 104000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "i5-13420H · RTX 4050 · 16GB DDR5 · 512GB SSD",
        "stores": [
            {"name": "Star Tech", "price": 98500, "url": "https://www.startech.com.bd/acer-nitro-v-15-anv15-51-gaming-laptop"},
            {"name": "Ryans Computers", "price": 99500, "url": "https://www.ryanscomputers.com/acer-nitro-v-15-anv15-51"},
            {"name": "TechLand BD", "price": 98990, "url": "https://www.techlandbd.com/acer-nitro-v-15-anv15-51"},
            {"name": "Computer Mania BD", "price": 101000, "url": "https://computermania.com.bd/product/acer-nitro-v-15/"},
        ]
    },
    {
        "slug": "msi-katana-15-rtx4060-16gb",
        "model_code": "MSI Katana 15 (i7-13620H / RTX 4060)",
        "aliases": ["msi katana 15", "katana 15", "msi katana 15 rtx 4060", "msi katana", "katana rtx 4060"],
        "title_en": "MSI Katana 15 B13VFK Gaming Laptop (Core i7-13620H · RTX 4060 8GB · 16GB DDR5 · 1TB NVMe · 15.6\" 144Hz IPS)",
        "title_bn": "এমএসআই কাটানা ১৫ গেমিং ল্যাপটপ (কোর আই৭ · আরটিএক্স ৪০৬০ · ১৬জিবি · ১টিবি)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "MSI",
        "specs_summary": "Intel Core i7-13620H 10-Core · NVIDIA GeForce RTX 4060 8GB GDDR6 (105W MUX Switch) · 16GB DDR5 5200MHz · 1TB NVMe PCIe Gen4 · 15.6-inch FHD 144Hz IPS · 4-Zone RGB Keyboard",
        "starting_price": 142000,
        "max_price": 149000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "i7-13620H · RTX 4060 · 16GB DDR5 · 1TB SSD",
        "stores": [
            {"name": "Star Tech", "price": 142000, "url": "https://www.startech.com.bd/msi-katana-15-b13vfk-gaming-laptop"},
            {"name": "Ryans Computers", "price": 143500, "url": "https://www.ryanscomputers.com/msi-katana-15-b13vfk"},
            {"name": "TechLand BD", "price": 142500, "url": "https://www.techlandbd.com/msi-katana-15-b13vfk"},
        ]
    },
    {
        "slug": "lenovo-loq-15-rtx4050-16gb",
        "model_code": "Lenovo LOQ 15 (i5-13450HX / RTX 4050)",
        "aliases": ["lenovo loq 15", "lenovo loq", "loq 15", "lenovo loq rtx 4050", "loq rtx 4050"],
        "title_en": "Lenovo LOQ 15 Gaming Laptop (Core i5-13450HX · RTX 4050 6GB 95W · 16GB DDR5 · 512GB NVMe · 15.6\" 144Hz G-Sync)",
        "title_bn": "লেনোভো এলওকিউ ১৫ গেমিং ল্যাপটপ (কোর আই৫ · আরটিএক্স ৪০৫০ · ১৬জিবি ডিডিআর৫)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "Lenovo",
        "specs_summary": "Intel Core i5-13450HX 10-Core · NVIDIA GeForce RTX 4050 6GB GDDR6 (95W TGP + Advanced Optimus) · 16GB DDR5 4800MHz · 512GB PCIe Gen4 · 15.6-inch FHD 144Hz 100% sRGB G-Sync",
        "starting_price": 109900,
        "max_price": 116000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "i5-13450HX · RTX 4050 · 16GB DDR5 · 512GB SSD",
        "stores": [
            {"name": "Star Tech", "price": 109900, "url": "https://www.startech.com.bd/lenovo-loq-15irx9-gaming-laptop"},
            {"name": "Ryans Computers", "price": 111000, "url": "https://www.ryanscomputers.com/lenovo-loq-15irx9"},
            {"name": "TechLand BD", "price": 110500, "url": "https://www.techlandbd.com/lenovo-loq-15irx9"},
        ]
    },
    {
        "slug": "lenovo-thinkpad-e14-gen-6",
        "model_code": "Lenovo ThinkPad E14 Gen 6",
        "aliases": ["thinkpad e14 gen 6", "thinkpad e14", "lenovo thinkpad e14", "thinkpad gen 6"],
        "title_en": "Lenovo ThinkPad E14 Gen 6 Business Laptop (Intel Core Ultra 7 155H · 16GB DDR5 · 512GB NVMe · 14\" WUXGA IPS · MIL-SPEC)",
        "title_bn": "লেনোভো থিঙ্কপ্যাড ই১৪ জেন ৬ ল্যাপটপ (কোর আল্ট্রা ৭ · ১৬জিবি · ৫১২জিবি)",
        "category": "Laptops & PC",
        "subcategory": "Business Laptops",
        "brand": "Lenovo",
        "specs_summary": "Intel Core Ultra 7 155H 16-Core Intel AI Boost NPU · Intel Arc Graphics · 16GB DDR5 5600MHz (Upgradable) · 512GB PCIe 4.0 SSD · 14-inch WUXGA (1920x1200) 16:10 300 nits IPS · MIL-STD-810H Military Toughness · TrackPoint Keyboard",
        "starting_price": 118000,
        "max_price": 125000,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80",
        "variant": "Core Ultra 7 · 16GB DDR5 · 512GB SSD",
        "stores": [
            {"name": "Star Tech", "price": 118000, "url": "https://www.startech.com.bd/lenovo-thinkpad-e14-gen-6"},
            {"name": "Ryans Computers", "price": 119500, "url": "https://www.ryanscomputers.com/lenovo-thinkpad-e14-gen-6"},
            {"name": "Dazzle BD", "price": 118500, "url": "https://dazzle.com.bd/product/lenovo-thinkpad-e14-gen-6"},
            {"name": "TechLand BD", "price": 119000, "url": "https://www.techlandbd.com/lenovo-thinkpad-e14-gen-6"},
        ]
    },
    {
        "slug": "asus-tuf-gaming-a15-rtx4060-16gb",
        "model_code": "ASUS TUF Gaming A15 (Ryzen 7 7735HS / RTX 4060)",
        "aliases": ["asus tuf gaming a15", "tuf gaming a15", "tuf a15 rtx 4060", "asus tuf a15", "tuf a15"],
        "title_en": "ASUS TUF Gaming A15 (Ryzen 7 7735HS · RTX 4060 8GB 140W · 16GB DDR5 · 512GB NVMe · 15.6\" 144Hz 100% sRGB G-Sync)",
        "title_bn": "আসুস টাফ গেমিং এ১৫ (রাইজেন ৭ · আরটিএক্স ৪০৬০ · ১৬জিবি ডিডিআর৫)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "Asus",
        "specs_summary": "AMD Ryzen 7 7735HS 8-Core 16-Thread · NVIDIA GeForce RTX 4060 8GB GDDR6 (140W Max TGP + MUX Switch) · 16GB DDR5 4800MHz · 512GB PCIe 4.0 SSD · 15.6-inch FHD 144Hz 100% sRGB G-Sync · 90Wh Battery",
        "starting_price": 139900,
        "max_price": 147000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "Ryzen 7 · RTX 4060 · 16GB DDR5 · 512GB SSD",
        "stores": [
            {"name": "Star Tech", "price": 139900, "url": "https://www.startech.com.bd/asus-tuf-gaming-a15-fa507nv-laptop"},
            {"name": "Ryans Computers", "price": 141000, "url": "https://www.ryanscomputers.com/asus-tuf-gaming-a15-fa507nv"},
            {"name": "TechLand BD", "price": 140500, "url": "https://www.techlandbd.com/asus-tuf-gaming-a15-fa507nv"},
        ]
    },
    {
        "slug": "hp-victus-15-rtx4050-16gb",
        "model_code": "HP Victus 15 (i5-13420H / RTX 4050)",
        "aliases": ["hp victus 15", "victus 15", "hp victus rtx 4050", "hp victus"],
        "title_en": "HP Victus 15 Gaming Laptop (Core i5-13420H · RTX 4050 6GB · 16GB DDR4 · 512GB NVMe · 15.6\" 144Hz IPS)",
        "title_bn": "এইচপি ভিকটাস ১৫ গেমিং ল্যাপটপ (কোর আই৫ · আরটিএক্স ৪০৫০ · ১৬জিবি · ৫১২জিবি)",
        "category": "Laptops & PC",
        "subcategory": "Gaming Laptops",
        "brand": "HP",
        "specs_summary": "Intel Core i5-13420H 8-Core · NVIDIA GeForce RTX 4050 6GB GDDR6 · 16GB DDR4 3200MHz · 512GB PCIe Gen4 NVMe · 15.6-inch FHD 144Hz IPS Micro-Edge · B&O Audio · Fast Charge",
        "starting_price": 99500,
        "max_price": 106000,
        "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&q=80",
        "variant": "i5-13420H · RTX 4050 · 16GB · 512GB SSD",
        "stores": [
            {"name": "Star Tech", "price": 99500, "url": "https://www.startech.com.bd/hp-victus-15-fa1093dx-gaming-laptop"},
            {"name": "Ryans Computers", "price": 101000, "url": "https://www.ryanscomputers.com/hp-victus-15-fa1093dx"},
            {"name": "TechLand BD", "price": 99990, "url": "https://www.techlandbd.com/hp-victus-15-fa1093dx"},
        ]
    },

    # --------------------------------------------------------------------------
    # PC HARDWARE & COMPONENTS
    # --------------------------------------------------------------------------
    {
        "slug": "intel-core-i5-14400f",
        "model_code": "Intel Core i5-14400F",
        "aliases": ["i5 14400f", "intel i5 14400f", "core i5 14400f", "14400f"],
        "title_en": "Intel 14th Gen Core i5-14400F Desktop Processor (10 Cores · 16 Threads · Up to 4.7GHz · LGA1700)",
        "title_bn": "ইন্টেল ১৪তম জেন কোর আই৫-১৪৪০০এফ প্রসেসর (১০ কোর · ১৬ থ্রেড)",
        "category": "Laptops & PC",
        "subcategory": "Processors",
        "brand": "Intel",
        "specs_summary": "10 Cores (6 P-cores + 4 E-cores) · 16 Threads · Up to 4.7GHz Max Turbo Frequency · 20MB Intel Smart Cache · 65W Base Power · PCIe 5.0 & DDR5/DDR4 Support · LGA1700 Socket",
        "starting_price": 21500,
        "max_price": 23000,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "variant": "10 Cores · LGA1700",
        "stores": [
            {"name": "Star Tech", "price": 21500, "url": "https://www.startech.com.bd/intel-14th-gen-core-i5-14400f-processor"},
            {"name": "Ryans Computers", "price": 21900, "url": "https://www.ryanscomputers.com/intel-14th-gen-core-i5-14400f"},
            {"name": "TechLand BD", "price": 21600, "url": "https://www.techlandbd.com/intel-14th-gen-core-i5-14400f"},
        ]
    },
    {
        "slug": "amd-ryzen-5-7600x",
        "model_code": "AMD Ryzen 5 7600X",
        "aliases": ["ryzen 5 7600x", "ryzen 7600x", "amd 7600x", "7600x"],
        "title_en": "AMD Ryzen 5 7600X Desktop Processor (6 Cores · 12 Threads · Up to 5.3GHz · AM5 · Zen 4)",
        "title_bn": "এএমডি রাইজেন ৫ ৭৬০০এক্স ডেস্কটপ প্রসেসর (৬ কোর · ১২ থ্রেড · এএম৫)",
        "category": "Laptops & PC",
        "subcategory": "Processors",
        "brand": "AMD",
        "specs_summary": "6 Cores 12 Threads · 4.7GHz Base / 5.3GHz Boost · 32MB L3 Cache · 105W TDP · TSMC 5nm FinFET · PCIe 5.0 & DDR5 Memory Support · Socket AM5",
        "starting_price": 22800,
        "max_price": 24500,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=600&q=80",
        "variant": "6 Cores · Socket AM5",
        "stores": [
            {"name": "Star Tech", "price": 22800, "url": "https://www.startech.com.bd/amd-ryzen-5-7600x-processor"},
            {"name": "Ryans Computers", "price": 23200, "url": "https://www.ryanscomputers.com/amd-ryzen-5-7600x"},
            {"name": "TechLand BD", "price": 22990, "url": "https://www.techlandbd.com/amd-ryzen-5-7600x"},
        ]
    },
    {
        "slug": "msi-g244f-170hz-gaming-monitor",
        "model_code": "MSI G244F (23.8\" 170Hz Rapid IPS)",
        "aliases": ["msi g244f", "g244f", "msi 170hz monitor", "msi gaming monitor"],
        "title_en": "MSI G244F 23.8\" FHD 170Hz Rapid IPS Gaming Monitor (1ms GtG · FreeSync Premium · Wide Color Gamut)",
        "title_bn": "এমএসআই জি২৪৪এফ ২৩.৮\" ১৭০ হার্টজ র্যাপিড আইপিএস গেমিং মনিটর",
        "category": "Laptops & PC",
        "subcategory": "Monitors",
        "brand": "MSI",
        "specs_summary": "23.8-inch Full HD (1920x1080) Rapid IPS Panel · 170Hz Refresh Rate · 1ms (GtG) Ultra-fast Response Time · AMD FreeSync Premium · 122.88% sRGB / 94.4% DCI-P3 · Frameless Design · 2x HDMI 2.0b + DisplayPort 1.2a",
        "starting_price": 18200,
        "max_price": 19500,
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&q=80",
        "variant": "23.8-inch · 170Hz Rapid IPS",
        "stores": [
            {"name": "Star Tech", "price": 18200, "url": "https://www.startech.com.bd/msi-g244f-gaming-monitor"},
            {"name": "Ryans Computers", "price": 18500, "url": "https://www.ryanscomputers.com/msi-g244f"},
            {"name": "TechLand BD", "price": 18300, "url": "https://www.techlandbd.com/msi-g244f"},
        ]
    },

    # --------------------------------------------------------------------------
    # SMARTWATCHES & WEARABLES
    # --------------------------------------------------------------------------
    {
        "slug": "apple-watch-series-10-46mm",
        "model_code": "Apple Watch Series 10 (46mm)",
        "aliases": ["apple watch series 10", "apple watch 10", "series 10", "watch series 10", "apple watch s10"],
        "title_en": "Apple Watch Series 10 (46mm GPS · Wide-Angle OLED Display · S10 SiP · Sleep Apnea Detection)",
        "title_bn": "অ্যাপল ওয়াচ সিরিজ ১০ (৪৬মিমি জিপিএস · ওলেড ডিসপ্লে)",
        "category": "Smartwatches & Wearables",
        "subcategory": "Smartwatches",
        "brand": "Apple",
        "specs_summary": "S10 SiP with 4-core Neural Engine · Thinnest Apple Watch Ever (9.7mm) · Largest Wide-Angle OLED Display (up to 40% brighter off-axis) · Sleep Apnea Notifications · Depth Gauge & Water Temperature Sensor · Fast Charging to 80% in 30 mins",
        "starting_price": 54990,
        "max_price": 59500,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "variant": "46mm GPS · Aluminum Case",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 54990, "url": "https://www.applegadgetsbd.com/product/apple-watch-series-10-46mm"},
            {"name": "Custom Mac BD", "price": 55500, "url": "https://custommacbd.com/products/apple-watch-series-10-46mm"},
            {"name": "Star Tech", "price": 57000, "url": "https://www.startech.com.bd/apple-watch-series-10-46mm"},
            {"name": "Gadget & Gear", "price": 57500, "url": "https://gadgetandgear.com/product/apple-watch-series-10-46mm"},
        ]
    },
    {
        "slug": "samsung-galaxy-watch-7-44mm",
        "model_code": "Samsung Galaxy Watch 7 (44mm)",
        "aliases": ["galaxy watch 7", "samsung galaxy watch 7", "watch 7", "galaxy watch 7 44mm"],
        "title_en": "Samsung Galaxy Watch 7 (44mm Bluetooth · BioActive Sensor · Dual-Frequency GPS · Wear OS 5)",
        "title_bn": "স্যামসাং গ্যালাক্সি ওয়াচ ৭ (৪৪মিমি ব্লুটুথ)",
        "category": "Smartwatches & Wearables",
        "subcategory": "Smartwatches",
        "brand": "Samsung",
        "specs_summary": "3nm Exynos W1000 5-Core Processor · 2GB RAM · 32GB Storage · 1.5-inch Super AMOLED Sapphire Crystal · Advanced BioActive Sensor with Energy Score · Dual-Frequency L1+L5 GPS · 5ATM + IP68 Water Resistance",
        "starting_price": 31990,
        "max_price": 35000,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "variant": "44mm Bluetooth",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 31990, "url": "https://www.applegadgetsbd.com/product/samsung-galaxy-watch-7-44mm"},
            {"name": "Custom Mac BD", "price": 32500, "url": "https://custommacbd.com/products/galaxy-watch-7-44mm"},
            {"name": "Star Tech", "price": 33500, "url": "https://www.startech.com.bd/samsung-galaxy-watch-7-44mm"},
        ]
    },
    {
        "slug": "redmi-watch-4",
        "model_code": "Redmi Watch 4",
        "aliases": ["redmi watch 4", "xiaomi redmi watch 4", "redmi watch"],
        "title_en": "Xiaomi Redmi Watch 4 (1.97\" AMOLED 60Hz · Aluminum Alloy Frame · 20-Day Battery · Bluetooth Calling)",
        "title_bn": "শাওমি রেডমি ওয়াচ ৪ (১.৯৭\" অ্যামোলেড ডিসপ্লে · ২০ দিনের ব্যাটারি)",
        "category": "Smartwatches & Wearables",
        "subcategory": "Smartwatches",
        "brand": "Xiaomi",
        "specs_summary": "1.97-inch LTPS AMOLED (600 nits) · Sturdy Aluminum Alloy Frame with Stainless Steel Rotating Crown · 4-Channel PPG Sensor · Built-in Multi-System GNSS GPS · 20 Days Typical Battery Life · 5ATM Water Resistance",
        "starting_price": 9490,
        "max_price": 10500,
        "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=600&q=80",
        "variant": "1.97-inch AMOLED · Bluetooth Calling",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 9490, "url": "https://www.applegadgetsbd.com/product/redmi-watch-4"},
            {"name": "Star Tech", "price": 9799, "url": "https://www.startech.com.bd/redmi-watch-4"},
            {"name": "Pickaboo", "price": 9999, "url": "https://www.pickaboo.com/product/redmi-watch-4"},
        ]
    },

    # --------------------------------------------------------------------------
    # AUDIO & TWS EARBUDS
    # --------------------------------------------------------------------------
    {
        "slug": "apple-airpods-4-anc",
        "model_code": "Apple AirPods 4 (with Active Noise Cancellation)",
        "aliases": ["airpods 4", "apple airpods 4", "airpods 4 anc"],
        "title_en": "Apple AirPods 4 with Active Noise Cancellation (H2 Chip · Transparency Mode · Wireless Charging Case)",
        "title_bn": "অ্যাপল এয়ারপডস ৪ অ্যাক্টিভ নয়েজ ক্যান্সেলেশন সহ",
        "category": "Audio & Headphones",
        "subcategory": "Wireless Earbuds",
        "brand": "Apple",
        "specs_summary": "Apple H2 Headphone Chip · Active Noise Cancellation in an Open-Ear Design · Adaptive Audio & Transparency Mode · Personalized Spatial Audio with Dynamic Head Tracking · Up to 30 Hours Total Listening Time · USB-C & Apple Watch Charger Case",
        "starting_price": 24990,
        "max_price": 27500,
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=600&q=80",
        "variant": "Active Noise Cancellation Edition",
        "stores": [
            {"name": "Custom Mac BD", "price": 24990, "url": "https://custommacbd.com/products/airpods-4-anc"},
            {"name": "Apple Gadgets BD", "price": 25500, "url": "https://www.applegadgetsbd.com/product/airpods-4-anc"},
            {"name": "Star Tech", "price": 26500, "url": "https://www.startech.com.bd/apple-airpods-4-with-anc"},
        ]
    },
    {
        "slug": "anker-soundcore-liberty-4-nc",
        "model_code": "Soundcore Liberty 4 NC",
        "aliases": ["soundcore liberty 4 nc", "liberty 4 nc", "anker liberty 4 nc", "soundcore liberty 4"],
        "title_en": "Anker Soundcore Liberty 4 NC (98.5% Noise Reduction · Adaptive ANC 2.0 · LDAC Hi-Res Audio · 50H Playtime)",
        "title_bn": "অ্যাংকার সাউন্ডকোর লিবার্টি ৪ এনসি (৯৮.৫% নয়েজ ক্যান্সেলেশন · হাই-রেস অডিও)",
        "category": "Audio & Headphones",
        "subcategory": "Wireless Earbuds",
        "brand": "Anker",
        "specs_summary": "Adaptive ANC 2.0 reduces noise by up to 98.5% · 11mm Custom Drivers · Hi-Res Wireless Certified with LDAC · 6 Mics with AI Clear Call Algorithm · 10H Single Charge / 50H Total Playtime · Wireless Charging Case · IPX4 Water Resistance",
        "starting_price": 8490,
        "max_price": 9500,
        "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=600&q=80",
        "variant": "Adaptive ANC 2.0 · LDAC",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 8490, "url": "https://www.applegadgetsbd.com/product/soundcore-liberty-4-nc"},
            {"name": "Star Tech", "price": 8790, "url": "https://www.startech.com.bd/anker-soundcore-liberty-4-nc-tws"},
            {"name": "Pickaboo", "price": 8990, "url": "https://www.pickaboo.com/product/anker-soundcore-liberty-4-nc"},
        ]
    },
]

# Authoritative Redmi and Xiaomi Phones (Bangladesh verified dealer pricing & specs)
try:
    from .redmi_xiaomi_catalog import REDMI_XIAOMI_CATALOG_ITEMS
except ImportError:
    from redmi_xiaomi_catalog import REDMI_XIAOMI_CATALOG_ITEMS

EXPANDED_CATALOG_ITEMS.extend(REDMI_XIAOMI_CATALOG_ITEMS)

# Authoritative Retro & Previous Gen Consoles (PS4, PS3, PS2, PSP, Vita, Xbox 360, Anbernic, Miyoo)
try:
    from .retro_gaming_catalog import RETRO_GAMING_CATALOG_ITEMS
except ImportError:
    from retro_gaming_catalog import RETRO_GAMING_CATALOG_ITEMS

EXPANDED_CATALOG_ITEMS.extend(RETRO_GAMING_CATALOG_ITEMS)



