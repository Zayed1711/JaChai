import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

try:
    from .models import (
        Billboard,
        SpotlightCard,
        TickerAd,
        Product,
        StoreOffer,
        PriceHistory,
        AdLead,
        HotProduct,
    )
except ImportError:
    from models import (
        Billboard,
        SpotlightCard,
        TickerAd,
        Product,
        StoreOffer,
        PriceHistory,
        AdLead,
        HotProduct,
    )


def seed_database(db: Session) -> None:
    """
    Idempotent database seeder.
    Only seeds if products table is currently empty.
    """
    if db.query(Product).first() is not None:
        # Guarantee all 3 Spotlight Cards (SLOT #02, #03, #04) exist
        existing_slots = {s.slot_code for s in db.query(SpotlightCard).all()}
        if "SLOT #04" not in existing_slots:
            slot4 = SpotlightCard(
                slot_code="SLOT #04",
                brand_title_en="URBAN SOLE BD",
                brand_title_bn="আরবান সোল বিডি",
                tagline_en="Classic Suede & Leather Low-Top Streetwear Sneakers",
                tagline_bn="স্ট্রিটওয়্যার সুয়েড ও লেদার ক্লাসিক স্নিকার্স",
                starting_price=3650,
                image_url="/images/urban-sneakers.jpg",
                target_url="/",
                is_active=True,
                impressions=18400,
                clicks=720,
            )
            db.add(slot4)
            db.commit()
            print("[JaChai Seeder] Backfilled missing SLOT #04 SpotlightCard.")
        seed_hot_products(db)
        print("[JaChai Seeder] Database contains records. Seeding checks complete.")
        return

    print("[JaChai Seeder] Empty database detected. Seeding full curated dataset...")

    # ==========================================
    # 1. TIER 1 PRIMARY HERO BILLBOARDS
    # ==========================================
    billboards = [
        Billboard(
            sponsor_en="BILLBOARD SLOT #01",
            sponsor_bn="বিলবোর্ড স্লট #০১",
            headline_en="YOUR AD GOES HERE",
            headline_bn="আপনার বিজ্ঞাপন এখানে দিন",
            category_badge="Premier Hero Slot",
            starting_price=0,
            image_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80",
            target_url="/advertise",
            campaign_start="2026-10-01",
            campaign_end="2026-12-31",
            is_active=True,
            impressions=0,
            clicks=0,
            display_order=1
        ),
        Billboard(
            sponsor_en="BILLBOARD SLOT #02",
            sponsor_bn="বিলবোর্ড স্লট #০২",
            headline_en="YOUR AD GOES HERE",
            headline_bn="আপনার বিজ্ঞাপন এখানে দিন",
            category_badge="Premier Hero Slot",
            starting_price=0,
            image_url="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80",
            target_url="/advertise",
            campaign_start="2026-10-01",
            campaign_end="2026-12-31",
            is_active=True,
            impressions=0,
            clicks=0,
            display_order=2
        ),
        Billboard(
            sponsor_en="BILLBOARD SLOT #03",
            sponsor_bn="বিলবোর্ড স্লট #০৩",
            headline_en="YOUR AD GOES HERE",
            headline_bn="আপনার বিজ্ঞাপন এখানে দিন",
            category_badge="Premier Hero Slot",
            starting_price=0,
            image_url="https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=1200&q=80",
            target_url="/advertise",
            campaign_start="2026-10-01",
            campaign_end="2026-12-31",
            is_active=True,
            impressions=0,
            clicks=0,
            display_order=3
        ),
        Billboard(
            sponsor_en="BILLBOARD SLOT #04",
            sponsor_bn="বিলবোর্ড স্লট #০৪",
            headline_en="YOUR AD GOES HERE",
            headline_bn="আপনার বিজ্ঞাপন এখানে দিন",
            category_badge="Premier Hero Slot",
            starting_price=0,
            image_url="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
            target_url="/advertise",
            campaign_start="2026-10-01",
            campaign_end="2026-12-31",
            is_active=True,
            impressions=0,
            clicks=0,
            display_order=4
        )
    ]
    db.add_all(billboards)
    db.flush()

    # ==========================================
    # 2. TIER 2 PARTNER SPOTLIGHT CARDS
    # ==========================================
    spotlights = [
        SpotlightCard(
            slot_code="SLOT #02",
            brand_title_en="AAROHI ARTISAN WEAVES",
            brand_title_bn="আরোহী আর্টিসান উইভস",
            tagline_en="Festive Handloom Jamdani & Organza Collection",
            tagline_bn="উৎসবের আসল ঢাকাই জামদানি ও অর্গানজা কালেকশন",
            starting_price=7990,
            image_url="/images/jamdani-saree.jpg",
            target_url="/",
            is_active=True,
            impressions=31200,
            clicks=1150
        ),
        SpotlightCard(
            slot_code="SLOT #03",
            brand_title_en="KEYCRAFT LABS",
            brand_title_bn="কিক্রাফট স্টুডিও",
            tagline_en="Retro 75% Hot-Swap Tri-Mode Wireless Mech Deck",
            tagline_bn="রেট্রো ৭৫% ওয়্যারলেস হট-সোয়াপ মেকানিক্যাল কিবোর্ড",
            starting_price=4890,
            image_url="/images/retro-keyboard.jpg",
            target_url="/",
            is_active=True,
            impressions=24500,
            clicks=980
        ),
        SpotlightCard(
            slot_code="SLOT #04",
            brand_title_en="URBAN SOLE BD",
            brand_title_bn="আরবান সোল বিডি",
            tagline_en="Classic Suede & Leather Low-Top Streetwear Sneakers",
            tagline_bn="স্ট্রিটওয়্যার সুয়েড ও লেদার ক্লাসিক স্নিকার্স",
            starting_price=3650,
            image_url="/images/urban-sneakers.jpg",
            target_url="/",
            is_active=True,
            impressions=18400,
            clicks=720
        )
    ]
    db.add_all(spotlights)
    db.flush()

    # ==========================================
    # 3. TIER 3 MOVING MARQUEE TICKERS
    # ==========================================
    tickers = [
        TickerAd(
            text_en="BAJUS LIVE GOLD INDEX: 22K Hallmarked Gold: ৳1,18,450 / Bhori (11.664g) · Live Rate Tracked Across Verified Jewellers",
            text_bn="বাজুস লাইভ গোল্ড ইনডেক্স: ২২ ক্যারেট হলমার্কযুক্ত স্বর্ণের রেট: ৳১,১৮,৪৫০ / ভরি · ভেরিফাইড জুয়েলার্স লাইভ রেট ট্র্যাকড",
            is_active=True,
            glide_speed_sec=55,
            priority_order=1
        ),
        TickerAd(
            text_en="HERITAGE WEAVES: Handcrafted Dhakai Jamdani Sarees from ৳7,990 · Open Parcel Trial on Delivery",
            text_bn="হেরিটেজ উইভস: খাঁটি ঢাকাই জামদানি শাড়ি মাত্র ৳৭,৯৯০ থেকে শুরু · ডেলিভারিতে ট্রায়াল সুবিধা",
            is_active=True,
            glide_speed_sec=55,
            priority_order=2
        ),
        TickerAd(
            text_en="CHRONOS HOROLOGY: Swiss Emerald Automatic Mechanical Watches from ৳51,900 · 2-Year Official Warranty",
            text_bn="ক্রোনোস হরোলোজি: সুইস এমারেল্ড অটোমেটিক মেকানিক্যাল ঘড়ি · ২ বছরের অফিসিয়াল ওয়ারেন্টি",
            is_active=True,
            glide_speed_sec=55,
            priority_order=3
        ),
        TickerAd(
            text_en="KEYCRAFT STUDIO: Retro 75% Hot-Swap Tri-Mode Wireless Keyboards from ৳4,890 · Fast Delivery",
            text_bn="কিক্রাফট স্টুডিও: রেট্রো ৭৫% ওয়্যারলেস হট-সোয়াপ কিবোর্ড মাত্র ৳৪,৮৯০ · দ্রুত ডেলিভারি",
            is_active=True,
            glide_speed_sec=55,
            priority_order=4
        ),
        TickerAd(
            text_en="URBAN SOLE BD: Classic Suede & Leather Low-Top Streetwear Sneakers from ৳3,650 · 7-Day Free Size Exchange",
            text_bn="আরবান সোল বিডি: ক্লাসিক সুয়েড ও লেদার স্নিকার্স মাত্র ৳৩,৬৫০ · ৭ দিনের ফ্রি সাইজ এক্সচেঞ্জ",
            is_active=True,
            glide_speed_sec=55,
            priority_order=5
        ),
        TickerAd(
            text_en="ATELIER LINEN: Old Money Breathable Cuban Linen Shirts from ৳890 · Nationwide Cash on Delivery",
            text_bn="অ্যাটেলিয়ার লিনেন: ওল্ড মানি কিউবান লিনেন শার্ট মাত্র ৳৮৯০ · সারাদেশে ক্যাশ অন ডেলিভারি",
            is_active=True,
            glide_speed_sec=55,
            priority_order=6
        )
    ]
    db.add_all(tickers)
    db.flush()

    # ==========================================
    # 4. PRODUCTS & STORE OFFERS (Catalog)
    # ==========================================
    products_data = [
        {
            "product": Product(
                slug="jamdani-saree",
                title_en="Handcrafted Dhakai Jamdani & Organza Festive Saree",
                title_bn="হ্যান্ডক্রাফটেড ঢাকাই জামদানি ও অর্গানজা উৎসবের শাড়ি",
                category="fashion",
                image_url="/images/jamdani-saree.jpg",
                specs_summary="100% Hand-woven cotton silk with authentic Dhakai motif. Trial-on-delivery across Bangladesh.",
                price_30d_ago=9500,
                price_15d_ago=8800,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Aarohi Artisan Handlooms",
                    source_type="f_commerce",
                    target_url="https://facebook.com/aarohi.weaves",
                    css_selector=None,
                    current_price=7990,
                    original_price=9500,
                    cod_terms_en="Trial on Delivery · 7-Day Easy Exchange · Cash on Delivery",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ৭ দিনের সহজ এক্সচেঞ্জ · ক্যাশ অন ডেলিভারি",
                    warranty_text="100% Handloom Guarantee",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=1840
                ),
                StoreOffer(
                    store_name="Heritage Weaves Plaza",
                    source_type="crawler",
                    target_url="https://heritageweavesbd.com/jamdani",
                    css_selector=".price-tag",
                    current_price=8400,
                    original_price=9500,
                    cod_terms_en="Trial on Delivery · Free Dhaka Delivery · Cash on Delivery",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ফ্রি ঢাকা ডেলিভারি · ক্যাশ অন ডেলিভারি",
                    warranty_text="Authentic Dhakai Certificate",
                    spider_status="healthy",
                    last_synced_at="15 mins ago",
                    clicks=820
                ),
                StoreOffer(
                    store_name="Shonar Bangla Silk & Weaves",
                    source_type="crawler",
                    target_url="https://shonarbanglasilk.com/item/102",
                    css_selector=".current-price",
                    current_price=8650,
                    original_price=9500,
                    cod_terms_en="Cash on Delivery · ৳70 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৭০ ডেলিভারি",
                    warranty_text="7-Day Return Policy",
                    spider_status="healthy",
                    last_synced_at="1 hour ago",
                    clicks=410
                )
            ]
        },
        {
            "product": Product(
                slug="designer-kurti-set",
                title_en="Designer Pastel Linen 3-Piece Kurti Set",
                title_bn="ডিজাইনার প্যাস্টেল লিনেন ৩-পিস কুর্তি সেট",
                category="fashion",
                image_url="/images/jamdani-saree.jpg",
                specs_summary="Pure breathable linen with thread embroidery, organza dupatta, and matching trousers.",
                price_30d_ago=4200,
                price_15d_ago=3800,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Pastel Threads BD",
                    source_type="f_commerce",
                    target_url="https://facebook.com/pastelthreads",
                    css_selector=None,
                    current_price=3250,
                    original_price=4200,
                    cod_terms_en="Trial on Delivery · Cash on Delivery · ৳60 Inside Dhaka",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ক্যাশ অন ডেলিভারি · ৳৬০ ঢাকা",
                    warranty_text="Fabric Color Guarantee",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=320
                ),
                StoreOffer(
                    store_name="Aarong Online Store",
                    source_type="crawler",
                    target_url="https://aarong.com/women/kurti-set",
                    css_selector=".product-price",
                    current_price=3600,
                    original_price=4200,
                    cod_terms_en="Cash on Delivery · ৳80 Nationwide",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৮০ সারাদেশে",
                    warranty_text="Official Store Receipt",
                    spider_status="healthy",
                    last_synced_at="35 mins ago",
                    clicks=190
                )
            ]
        },
        {
            "product": Product(
                slug="retro-keyboard",
                title_en="Retro 75% Wireless Hot-Swap Mechanical Keyboard",
                title_bn="রেট্রো ৭৫% ওয়্যারলেস হট-সোয়াপ মেকানিক্যাল কিবোর্ড",
                category="gadgets",
                image_url="/images/retro-keyboard.jpg",
                specs_summary="Tri-mode wireless connectivity (Bluetooth 5.1/2.4G/Type-C), gasket mount, pre-lubed switches.",
                price_30d_ago=5600,
                price_15d_ago=5200,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="KeyCraft Studio BD",
                    source_type="crawler",
                    target_url="https://keycraftbd.com/keyboard-retro75",
                    css_selector=".price-box",
                    current_price=4890,
                    original_price=5600,
                    cod_terms_en="Cash on Delivery · 1-Year Replacement Warranty · ৳60 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ১ বছর রিপ্লেসমেন্ট ওয়ারেন্টি · ৳৬০ ডেলিভারি",
                    warranty_text="1-Year Full Switch Warranty",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=980
                ),
                StoreOffer(
                    store_name="DeskSetup Aesthetics BD",
                    source_type="f_commerce",
                    target_url="https://facebook.com/desksetupaesthetics",
                    css_selector=None,
                    current_price=5150,
                    original_price=5600,
                    cod_terms_en="Cash on Delivery · 6-Month Service Warranty · ৳70 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৬ মাস সার্ভিস ওয়ারেন্টি · ৳৭০ ডেলিভারি",
                    warranty_text="Free Keycap Puller Included",
                    spider_status="healthy",
                    last_synced_at="20 mins ago",
                    clicks=450
                ),
                StoreOffer(
                    store_name="Star Tech BD",
                    source_type="crawler",
                    target_url="https://startech.com.bd/retro-keyboard",
                    css_selector=".p-price",
                    current_price=5350,
                    original_price=5600,
                    cod_terms_en="Cash on Delivery · ৳60 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৬০ ডেলিভারি",
                    warranty_text="Official Brand Support",
                    spider_status="healthy",
                    last_synced_at="45 mins ago",
                    clicks=290
                )
            ]
        },
        {
            "product": Product(
                slug="sunset-lamp",
                title_en="Aura RGB Sunset Projection Lamp with App Control",
                title_bn="অরা আরজিবি সানসেট প্রজেকশন ল্যাম্প (অ্যাপ কন্ট্রোল)",
                category="gadgets",
                image_url="/images/retro-keyboard.jpg",
                specs_summary="16-color optical crystal lens, 360-degree aluminum rotation, smartphone Bluetooth control.",
                price_30d_ago=1850,
                price_15d_ago=1500,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Gadget Craze BD",
                    source_type="f_commerce",
                    target_url="https://facebook.com/gadgetcrazebd",
                    css_selector=None,
                    current_price=1250,
                    original_price=1850,
                    cod_terms_en="Cash on Delivery · ৳60 Inside Dhaka",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৬০ ঢাকা",
                    warranty_text="6-Month Adapter Replacement",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=310
                ),
                StoreOffer(
                    store_name="Daraz BD Mall",
                    source_type="crawler",
                    target_url="https://daraz.com.bd/sunset-lamp",
                    css_selector="meta[property='product:price:amount']",
                    current_price=1390,
                    original_price=1850,
                    cod_terms_en="Cash on Delivery · ৳55 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৫৫ ডেলিভারি",
                    warranty_text="7 Days Seller Return",
                    spider_status="healthy",
                    last_synced_at="1 hour ago",
                    clicks=170
                )
            ]
        },
        {
            "product": Product(
                slug="urban-sneakers",
                title_en="Urban Suede & Leather Low-Top Streetwear Sneakers",
                title_bn="আরবান সুয়েড ও লেদার লো-টপ স্ট্রিটওয়্যার স্নিকার্স",
                category="sneakers-watches",
                image_url="/images/urban-sneakers.jpg",
                specs_summary="Handcrafted premium suede leather with vulcanized gum sole and breathable mesh insole.",
                price_30d_ago=4200,
                price_15d_ago=3900,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Urban Sole Footwear BD",
                    source_type="crawler",
                    target_url="https://urbansolebd.com/sneakers",
                    css_selector=".price",
                    current_price=3650,
                    original_price=4200,
                    cod_terms_en="Trial on Delivery · 7-Day Size Replacement · Cash on Delivery",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ৭ দিনের সাইজ রিপ্লেসমেন্ট · ক্যাশ অন ডেলিভারি",
                    warranty_text="90-Day Sole Warranty",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=760
                ),
                StoreOffer(
                    store_name="Kicks & Threads Dhaka",
                    source_type="f_commerce",
                    target_url="https://facebook.com/kicksandthreads",
                    css_selector=None,
                    current_price=3800,
                    original_price=4200,
                    cod_terms_en="Trial on Delivery · Free Crew Socks · ৳70 Delivery",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ফ্রি মোজা · ৳৭০ ডেলিভারি",
                    warranty_text="7 Days Easy Exchange",
                    spider_status="healthy",
                    last_synced_at="30 mins ago",
                    clicks=420
                )
            ]
        },
        {
            "product": Product(
                slug="luxury-watch",
                title_en="Classic Emerald Dial Automatic Stainless Steel Luxury Watch",
                title_bn="সুইস অটোমেটিক এমারেল্ড ডায়াল মেকানিক্যাল লাক্সারি ঘড়ি",
                category="sneakers-watches",
                image_url="https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=900&q=80",
                specs_summary="Self-winding mechanical caliber, emerald sunburst dial, anti-reflective sapphire crystal, 100m water resistant.",
                price_30d_ago=58000,
                price_15d_ago=54500,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Chronos Swiss Horology",
                    source_type="crawler",
                    target_url="https://chronosbd.com/watches/emerald",
                    css_selector=".price-val",
                    current_price=51900,
                    original_price=58000,
                    cod_terms_en="2-Year Official Warranty · Insured Free Courier · Original Papers",
                    cod_terms_bn="২ বছর অফিসিয়াল ওয়ারেন্টি · ফ্রি ইন্সুরেন্স ডেলিভারি · আসল পেপারস",
                    warranty_text="2 Years Movement Warranty",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=1420
                ),
                StoreOffer(
                    store_name="Swiss Watch Lounge BD",
                    source_type="crawler",
                    target_url="https://swisswatchlounge.com/chrono",
                    css_selector=".amount",
                    current_price=53500,
                    original_price=58000,
                    cod_terms_en="Official Brand Warranty · Store Pickup Available",
                    cod_terms_bn="অফিসিয়াল ব্র্যান্ড ওয়ারেন্টি · শোরুম পিকআপ সুবিধা",
                    warranty_text="Lifetime Authenticity Guarantee",
                    spider_status="healthy",
                    last_synced_at="2 hours ago",
                    clicks=610
                )
            ]
        },
        {
            "product": Product(
                slug="snacks-food",
                title_en="Honey Glazed Roasted Nuts & Gourmet Dried Fruit Jar",
                title_bn="প্রিমিয়াম হানি রোস্টেড নাটস ও ড্রাই ফ্রুটস কম্বো জার",
                category="snacks-food",
                image_url="/images/snacks-food.jpg",
                specs_summary="450g airtight jar with California almonds, cashew nuts, Iranian pistachios, and Sundarbans honey.",
                price_30d_ago=1150,
                price_15d_ago=980,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="NutriBites Gourmet BD",
                    source_type="f_commerce",
                    target_url="https://facebook.com/nutribitesbd",
                    css_selector=None,
                    current_price=850,
                    original_price=1150,
                    cod_terms_en="100% Organic Sealed Jar · Cash on Delivery · ৳60 Inside Dhaka",
                    cod_terms_bn="১০০% খাঁটি সিলড জার · ক্যাশ অন ডেলিভারি · ৳৬০ ঢাকা",
                    warranty_text="Freshness Seal Guarantee",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=540
                ),
                StoreOffer(
                    store_name="Organic Delight Bangladesh",
                    source_type="crawler",
                    target_url="https://organicdelightbd.com/item/nuts",
                    css_selector=".product-price",
                    current_price=920,
                    original_price=1150,
                    cod_terms_en="Cash on Delivery · Same-Day Delivery Inside Dhaka",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ঢাকা শহরে সেম-ডে ডেলিভারি",
                    warranty_text="Food Grade Certified",
                    spider_status="healthy",
                    last_synced_at="45 mins ago",
                    clicks=280
                )
            ]
        },
        {
            "product": Product(
                slug="gold-jewellery",
                title_en="22K Hallmarked Gold Rate Index (1 Bhori / 11.664g)",
                title_bn="২২ ক্যারেট হলমার্কযুক্ত স্বর্ণের রেট (১ ভরি / ১১.৬৬৪ গ্রাম)",
                category="jewelleries",
                image_url="/images/gold-jewellery.svg",
                specs_summary="Daily revised benchmark gold price index based on Bangladesh Jewellers Association (BAJUS) standard.",
                price_30d_ago=115200,
                price_15d_ago=116800,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Bangladesh Jewellers Association (BAJUS)",
                    source_type="crawler",
                    target_url="https://bajus.org/gold-rate",
                    css_selector=".rate-22k",
                    current_price=118450,
                    original_price=121500,
                    cod_terms_en="Official Benchmark Rate (22K Cadmium Gold) · Hallmarked Standard",
                    cod_terms_bn="অফিসিয়াল বেঞ্চমার্ক রেট (২২ ক্যারেট ক্যাডমিয়াম) · হলমার্ক মানদণ্ড",
                    warranty_text="Govt & BAJUS Benchmark",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=2340
                ),
                StoreOffer(
                    store_name="Diamond World Gold Vault",
                    source_type="crawler",
                    target_url="https://diamondworldltd.com/gold",
                    css_selector=".curr-rate",
                    current_price=118450,
                    original_price=121500,
                    cod_terms_en="100% Hallmarked · Free Cleaning & Authenticity Certificate · Dhaka/Ctg",
                    cod_terms_bn="১০০% হলমার্কযুক্ত · ফ্রি পলিশ ও খাঁটি সনদপত্র · ঢাকা/চট্টগ্রাম শোরুম",
                    warranty_text="Lifetime Gold Buyback Guarantee",
                    spider_status="healthy",
                    last_synced_at="4 mins ago",
                    clicks=1120
                ),
                StoreOffer(
                    store_name="Apan Jewellers Premium",
                    source_type="crawler",
                    target_url="https://apanjewellers.com/rate",
                    css_selector=".gold-table",
                    current_price=118800,
                    original_price=121500,
                    cod_terms_en="Tested Laser Hallmarking · Certified Hallmark Card Included",
                    cod_terms_bn="লেজার হলমার্ক টেস্টেড · কার্ড ও ভাউচারসহ ডেলিভারি",
                    warranty_text="100% Purity Guarantee",
                    spider_status="healthy",
                    last_synced_at="10 mins ago",
                    clicks=590
                )
            ]
        },
        {
            "product": Product(
                slug="s24-ultra",
                title_en="Samsung Galaxy S24 Ultra (12GB / 256GB Titanium)",
                title_bn="স্যামসাং গ্যালাক্সি এস২৪ আল্ট্রা (১২জিবি / ২৫৬জিবি)",
                category="mobiles-computers",
                image_url="/images/s24-ultra.png",
                specs_summary="Snapdragon 8 Gen 3, 200MP Quad Telephoto Camera, 6.8 Dynamic AMOLED 2X, S-Pen included.",
                price_30d_ago=145000,
                price_15d_ago=135000,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Samsung Official Flagship Store",
                    source_type="crawler",
                    target_url="https://samsung.com/bd/smartphones/s24-ultra",
                    css_selector=".price-display",
                    current_price=128900,
                    original_price=145000,
                    cod_terms_en="Official Warranty · Free Insured Courier · 0% EMI Available",
                    cod_terms_bn="অফিসিয়াল ওয়ারেন্টি · ফ্রি ইনসিওরড কুরিয়ার · ০% ইএমআই সুবিধা",
                    warranty_text="1-Year Official Samsung Warranty",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=1650
                ),
                StoreOffer(
                    store_name="Gadget Vault Bangladesh",
                    source_type="f_commerce",
                    target_url="https://facebook.com/gadgetvaultbd",
                    css_selector=None,
                    current_price=131500,
                    original_price=145000,
                    cod_terms_en="Cash on Delivery · ৳60 Inside Dhaka · Sealed Pack",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৬০ ঢাকা · ইনট্যাক্ট বক্স",
                    warranty_text="1-Year Service Warranty",
                    spider_status="healthy",
                    last_synced_at="18 mins ago",
                    clicks=720
                )
            ]
        },
        {
            "product": Product(
                slug="iphone-18-pro-max",
                title_en="Apple iPhone 18 Pro Max (256GB Natural Titanium)",
                title_bn="অ্যাপল আইফোন ১৮ প্রো ম্যাক্স (২৫৬জিবি ন্যাচারাল টাইটানিয়াম)",
                category="mobiles-computers",
                image_url="/images/s24-ultra.png",
                specs_summary="A19 Pro Bionic, ProMotion 120Hz LTPO, Titanium unibody, 48MP Triple Lens with 10x Optical Zoom.",
                price_30d_ago=189000,
                price_15d_ago=182000,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Apple Authorized Store BD",
                    source_type="crawler",
                    target_url="https://applestore.com.bd/iphone18promax",
                    css_selector=".price-tag",
                    current_price=174900,
                    original_price=189000,
                    cod_terms_en="Official BTRC Approved · 1-Year Official Apple Care",
                    cod_terms_bn="অফিসিয়াল বিটিআরসি অনুমোদিত · ১ বছর অ্যাপল কেয়ার",
                    warranty_text="Official Apple Global Warranty",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=1980
                ),
                StoreOffer(
                    store_name="Star Tech BD",
                    source_type="crawler",
                    target_url="https://startech.com.bd/apple-iphone-18-pro-max",
                    css_selector=".p-price",
                    current_price=176500,
                    original_price=189000,
                    cod_terms_en="Cash on Delivery · ৳60 Nationwide",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৬০ সারাদেশে",
                    warranty_text="1-Year Replacement Warranty",
                    spider_status="healthy",
                    last_synced_at="35 mins ago",
                    clicks=880
                )
            ]
        },
        {
            "product": Product(
                slug="old-money-shirt",
                title_en="Old Money Textured Cuban Collar Linen Shirt",
                title_bn="ওল্ড মানি টেক্সচার্ড কিউবান কলার লিনেন শার্ট",
                category="fashion",
                image_url="/images/old-money-shirt.jpg",
                specs_summary="Breathable heavyweight cotton linen blend with relaxed fit & natural shell buttons.",
                price_30d_ago=1250,
                price_15d_ago=1050,
                is_pinned_homepage=True
            ),
            "offers": [
                StoreOffer(
                    store_name="Dhaka Drip Attire Studio",
                    source_type="f_commerce",
                    target_url="https://facebook.com/dhakadrip",
                    css_selector=None,
                    current_price=890,
                    original_price=1250,
                    cod_terms_en="Trial on Delivery · 7-Day Free Size Exchange · ৳60 Delivery",
                    cod_terms_bn="ডেলিভারিতে ট্রায়াল সুবিধা · ৭ দিনের ফ্রি সাইজ এক্সচেঞ্জ · ৳৬০ ডেলিভারি",
                    warranty_text="100% Breathable Weave",
                    spider_status="healthy",
                    last_synced_at="Just now",
                    clicks=650
                ),
                StoreOffer(
                    store_name="Urban Dapper Bangladesh",
                    source_type="crawler",
                    target_url="https://urbandapper.com/cuban-linen",
                    css_selector=".price",
                    current_price=980,
                    original_price=1250,
                    cod_terms_en="Cash on Delivery · ৳50 Delivery",
                    cod_terms_bn="ক্যাশ অন ডেলিভারি · ৳৫০ ডেলিভারি",
                    warranty_text="7 Days Exchange Policy",
                    spider_status="healthy",
                    last_synced_at="1 hour ago",
                    clicks=310
                )
            ]
        }
    ]

    for item in products_data:
        p = item["product"]
        db.add(p)
        db.flush()

        for offer in item["offers"]:
            offer.product_id = p.id
            db.add(offer)

        # Seed 30d, 15d, and today price trend history
        now = datetime.utcnow()
        histories = [
            PriceHistory(product_id=p.id, recorded_price=p.price_30d_ago, recorded_at=now - timedelta(days=30)),
            PriceHistory(product_id=p.id, recorded_price=p.price_15d_ago, recorded_at=now - timedelta(days=15)),
            PriceHistory(product_id=p.id, recorded_price=min(o.current_price for o in item["offers"]), recorded_at=now),
        ]
        db.add_all(histories)

    # ==========================================
    # 5. ADVERTISER LEADS INBOX
    # ==========================================
    leads = [
        AdLead(
            brand_name="Shwapno Superstores",
            contact_phone="+8801711223344",
            selected_tier="Primary Kinetic Billboard",
            budget_note="Monthly prime slot campaign for fresh groceries",
            status="Paid via bKash/Nagad",
            created_at="Today, 08:30 AM"
        ),
        AdLead(
            brand_name="Kicks BD Vault",
            contact_phone="+8801822334455",
            selected_tier="Product Spotlight Placement",
            budget_note="Festive sneaker push across Dhaka",
            status="Pending",
            created_at="Yesterday, 04:15 PM"
        )
    ]
    db.add_all(leads)

    db.commit()
    print("[JaChai Seeder] Successfully seeded all billboards, spotlights, tickers, products, offers, and leads.")
    seed_hot_products(db)


DEFAULT_HOT_PRODUCTS = [
    {
        "slug": "gold-hallmark-pricing",
        "title_en": "Gold (22K & 24K Hallmark Benchmark)",
        "title_bn": "স্বর্ণ (২২ ও ২৪ ক্যারেট হলমার্ক রেট)",
        "subtitle_en": "24K: ৳154,700/Vori • 22K: ৳141,800/Vori • 21K: ৳135,400/Vori",
        "subtitle_bn": "২৪ ক্যারেট: ৳১৫৪,৭০০/ভরি • ২২ ক্যারেট: ৳১৪১,৮০০/ভরি • ২১ ক্যারেট: ৳১৩৫,৪০০/ভরি",
        "category_id": "jewelry-watches",
        "search_query": "gold",
        "current_price": 141800,
        "previous_price": 138500,
        "unit_en": "Starts from / Vori",
        "unit_bn": "শুরু / ভরি",
        "icon_name": "Sparkles",
        "display_order": 1,
        "latest_release_name": "24K Fine Gold: ৳154,700/Vori • 22K Hallmark: ৳141,800/Vori • 21K: ৳135,400/Vori (BAJUS Official)",
        "latest_release_price": 154700,
        "latest_release_badge": "24K Benchmark",
        "latest_release_url": "https://www.bajus.org/",
        "stores": [
            {"name": "BAJUS Official Benchmark", "price": 141800, "url": "https://www.bajus.org/", "status": "National Hallmark"},
            {"name": "Diamond World BD", "price": 141800, "url": "https://diamondworldbd.com/", "status": "Certified 22K/24K"},
            {"name": "Apan Jewellers", "price": 141800, "url": "https://apanjewellers.com/", "status": "Certified 22K/24K"},
            {"name": "Al-Amin Jewellers", "price": 142000, "url": "https://alaminjewellers.com/", "status": "In Stock"}
        ]
    },
    {
        "slug": "fuel-oil-energy",
        "title_en": "Fuel (Octane, Diesel, Petrol)",
        "title_bn": "জ্বালানি তেল (অকটেন, ডিজেল, পেট্রোল)",
        "subtitle_en": "Octane: ৳125/L • Diesel: ৳105/L • Petrol: ৳120/L (BPC Regulated)",
        "subtitle_bn": "অকটেন: ৳১২৫/লিটার • ডিজেল: ৳১০৫/লিটার • পেট্রোল: ৳১২০/লিটার",
        "category_id": "groceries-daily",
        "search_query": "fuel octane diesel",
        "current_price": 105,
        "previous_price": 105,
        "unit_en": "Starts from / Litre",
        "unit_bn": "শুরু / লিটার",
        "icon_name": "Fuel",
        "display_order": 2,
        "latest_release_name": "Octane: ৳125/Litre • Diesel: ৳105/Litre • Petrol: ৳120/Litre (Government Regulated)",
        "latest_release_price": 125,
        "latest_release_badge": "Octane / Diesel",
        "latest_release_url": "https://padmaoil.gov.bd/",
        "stores": [
            {"name": "Padma Oil Company Ltd", "price": 105, "url": "https://padmaoil.gov.bd/", "status": "Regulated Retail"},
            {"name": "Meghna Petroleum Ltd", "price": 105, "url": "https://mpl.gov.bd/", "status": "Regulated Retail"},
            {"name": "Jamuna Oil Company Ltd", "price": 105, "url": "https://jamunaoil.gov.bd/", "status": "Regulated Retail"}
        ]
    },
    {
        "slug": "iphones",
        "title_en": "iPhones (Apple Flagship Series)",
        "title_bn": "আইফোন (অ্যাপল ফ্ল্যাগশিপ সিরিজ)",
        "subtitle_en": "Apple iPhone 13, 14, 15, 16 Pro & Pro Max Flagships",
        "subtitle_bn": "অ্যাপল আইফোন ১৩, ১৪, ১৫, ১৬ প্রো এবং প্রো ম্যাক্স",
        "category_id": "mobile-gadgets",
        "search_query": "iphone",
        "current_price": 68500,
        "previous_price": 72000,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "Smartphone",
        "display_order": 3,
        "latest_release_name": "Apple iPhone 16 Pro Max 256GB Desert Titanium",
        "latest_release_price": 172500,
        "latest_release_badge": "Latest Flagship",
        "latest_release_url": "https://www.applegadgetsbd.com/",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 68500, "url": "https://www.applegadgetsbd.com/", "status": "In Stock"},
            {"name": "Star Tech", "price": 69999, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Ryans Computers", "price": 70500, "url": "https://www.ryans.com/", "status": "In Stock"},
            {"name": "Dazzle BD", "price": 68900, "url": "https://dazzle.com.bd/", "status": "In Stock"},
            {"name": "Kite9 BD", "price": 69500, "url": "https://kite9.com.bd/", "status": "Limited Stock"}
        ]
    },
    {
        "slug": "samsung-galaxy-s-series",
        "title_en": "Samsung Galaxy S Series",
        "title_bn": "স্যামসাং গ্যালাক্সি এস সিরিজ",
        "subtitle_en": "Galaxy S23, S24, S24 Ultra & FE Official Flagships",
        "subtitle_bn": "স্যামসাং গ্যালাক্সি এস২৩, এস২৪ ও এস২৪ আল্ট্রা ফ্ল্যাগশিপ",
        "category_id": "mobile-gadgets",
        "search_query": "samsung galaxy s",
        "current_price": 79500,
        "previous_price": 84000,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "Smartphone",
        "display_order": 4,
        "latest_release_name": "Samsung Galaxy S24 Ultra 12GB/256GB Titanium Gray",
        "latest_release_price": 148000,
        "latest_release_badge": "Latest Flagship",
        "latest_release_url": "https://samsungplaza.com.bd/",
        "stores": [
            {"name": "Star Tech", "price": 79500, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Apple Gadgets BD", "price": 80999, "url": "https://www.applegadgetsbd.com/", "status": "In Stock"},
            {"name": "Samsung Plaza BD", "price": 82500, "url": "https://samsungplaza.com.bd/", "status": "Official BD Warranty"},
            {"name": "Pickaboo", "price": 81500, "url": "https://www.pickaboo.com/", "status": "In Stock"},
            {"name": "Daraz Mall", "price": 83000, "url": "https://www.daraz.com.bd/", "status": "In Stock"}
        ]
    },
    {
        "slug": "ram-ddr4-ddr5-modules",
        "title_en": "RAM (DDR4 / DDR5 Modules)",
        "title_bn": "র‌্যাম (ডিডিআর৪ ও ডিডিআর৫)",
        "subtitle_en": "Desktop & Laptop 8GB, 16GB, 32GB High-Speed RAM",
        "subtitle_bn": "ডেস্কটপ ও ল্যাপটপ ৮জিবি, ১৬জিবি, ৩২জিবি মেমোরি মডিউল",
        "category_id": "desktop-components",
        "search_query": "ram ddr4 ddr5",
        "current_price": 2450,
        "previous_price": 2750,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "Cpu",
        "display_order": 5,
        "latest_release_name": "Corsair Dominator Titanium RGB DDR5 32GB (2x16GB) 6000MHz CL30",
        "latest_release_price": 19800,
        "latest_release_badge": "Latest DDR5",
        "latest_release_url": "https://www.startech.com.bd/",
        "stores": [
            {"name": "Star Tech", "price": 2450, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Ryans Computers", "price": 2500, "url": "https://www.ryans.com/", "status": "In Stock"},
            {"name": "Tech Land BD", "price": 2480, "url": "https://www.techlandbd.com/", "status": "In Stock"},
            {"name": "Skyland BD", "price": 2550, "url": "https://www.skyland.com.bd/", "status": "In Stock"}
        ]
    },
    {
        "slug": "ssd-nvme-sata-storage",
        "title_en": "SSD (NVMe M.2 & SATA Drives)",
        "title_bn": "এসএসডি (এনভিএমই ও সাটা)",
        "subtitle_en": "256GB, 512GB, 1TB & 2TB PCIe Gen3/Gen4 Solid State Drives",
        "subtitle_bn": "২৫৬জিবি, ৫১২জিবি, ১টিবি ও ২টিবি হাই-স্পিড এসএসডি স্টোরেজ",
        "category_id": "desktop-components",
        "search_query": "ssd nvme m.2",
        "current_price": 2850,
        "previous_price": 3200,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "HardDrive",
        "display_order": 6,
        "latest_release_name": "Samsung 990 PRO 1TB PCIe 4.0 NVMe M.2 (7450 MB/s Read)",
        "latest_release_price": 14500,
        "latest_release_badge": "Latest Gen4",
        "latest_release_url": "https://www.startech.com.bd/",
        "stores": [
            {"name": "Star Tech", "price": 2850, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Ryans Computers", "price": 2900, "url": "https://www.ryans.com/", "status": "In Stock"},
            {"name": "Tech Land BD", "price": 2890, "url": "https://www.techlandbd.com/", "status": "In Stock"},
            {"name": "Computer Village", "price": 2950, "url": "https://www.computervillage.com.bd/", "status": "In Stock"}
        ]
    },
    {
        "slug": "gpu-rtx-radeon-graphics",
        "title_en": "GPU (Graphics Cards)",
        "title_bn": "জিপিইউ (গ্রাফিক্স কার্ড)",
        "subtitle_en": "NVIDIA GeForce RTX 3060/4060/4070 & AMD Radeon Series",
        "subtitle_bn": "গেমিং ও এআই রেন্ডারিং এনভিডিয়া আরটিএক্স ও এএমডি রেডিয়ন কার্ড",
        "category_id": "desktop-components",
        "search_query": "gpu graphics card rtx",
        "current_price": 28500,
        "previous_price": 31000,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "Zap",
        "display_order": 7,
        "latest_release_name": "Gigabyte GeForce RTX 4070 SUPER WINDFORCE OC 12GB GDDR6X",
        "latest_release_price": 79500,
        "latest_release_badge": "Latest RTX Super",
        "latest_release_url": "https://www.startech.com.bd/",
        "stores": [
            {"name": "Star Tech", "price": 28500, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Ryans Computers", "price": 29200, "url": "https://www.ryans.com/", "status": "In Stock"},
            {"name": "Tech Land BD", "price": 28990, "url": "https://www.techlandbd.com/", "status": "In Stock"},
            {"name": "Ultra Technology", "price": 29500, "url": "https://ultratech.com.bd/", "status": "In Stock"}
        ]
    },
    {
        "slug": "processors-intel-amd-cpus",
        "title_en": "Processors (Intel & AMD CPUs)",
        "title_bn": "প্রসেসর (ইন্টেল ও এএমডি সিপিইউ)",
        "subtitle_en": "Intel Core i3/i5/i7/i9 12th-14th Gen & AMD Ryzen 5000/7000/9000",
        "subtitle_bn": "ইন্টেল কোর এবং এএমডি রাইজেন লেটেস্ট জেনারেশন ডেস্কটপ প্রসেসর",
        "category_id": "desktop-components",
        "search_query": "processor intel core amd ryzen",
        "current_price": 9800,
        "previous_price": 10500,
        "unit_en": "Starts from",
        "unit_bn": "শুরু",
        "icon_name": "CircuitBoard",
        "display_order": 8,
        "latest_release_name": "AMD Ryzen 7 9800X3D Desktop Gaming Processor (8 Cores, 16 Threads, 5.2GHz)",
        "latest_release_price": 64500,
        "latest_release_badge": "Latest Zen 5 3D",
        "latest_release_url": "https://www.startech.com.bd/",
        "stores": [
            {"name": "Star Tech", "price": 9800, "url": "https://www.startech.com.bd/", "status": "In Stock"},
            {"name": "Ryans Computers", "price": 9990, "url": "https://www.ryans.com/", "status": "In Stock"},
            {"name": "Tech Land BD", "price": 9850, "url": "https://www.techlandbd.com/", "status": "In Stock"},
            {"name": "Computer Village", "price": 10200, "url": "https://www.computervillage.com.bd/", "status": "In Stock"}
        ]
    }
]

def seed_hot_products(db: Session) -> None:
    """Guarantee all 8 Hot Products benchmarks exist and are populated with verified store pricing and latest releases."""
    try:
        existing_records = {hp.slug: hp for hp in db.query(HotProduct).all()}
        added = 0
        updated = 0
        for item in DEFAULT_HOT_PRODUCTS:
            if item["slug"] not in existing_records:
                hp = HotProduct(
                    slug=item["slug"],
                    title_en=item["title_en"],
                    title_bn=item["title_bn"],
                    subtitle_en=item.get("subtitle_en", ""),
                    subtitle_bn=item.get("subtitle_bn", ""),
                    category_id=item.get("category_id", "mobile-gadgets"),
                    search_query=item.get("search_query", ""),
                    current_price=item.get("current_price", 0),
                    previous_price=item.get("previous_price", 0),
                    unit_en=item.get("unit_en", "Starts from"),
                    unit_bn=item.get("unit_bn", "শুরু"),
                    icon_name=item.get("icon_name", "Smartphone"),
                    stores_json=json.dumps(item.get("stores", []), ensure_ascii=False),
                    latest_release_name=item.get("latest_release_name"),
                    latest_release_price=item.get("latest_release_price"),
                    latest_release_badge=item.get("latest_release_badge"),
                    latest_release_url=item.get("latest_release_url"),
                    is_active=True,
                    display_order=item.get("display_order", 1),
                    last_calibrated_at=datetime.utcnow()
                )
                db.add(hp)
                added += 1
            else:
                existing_hp = existing_records[item["slug"]]
                # Ensure latest release data is synced if missing
                if item.get("latest_release_name") and not existing_hp.latest_release_name:
                    existing_hp.latest_release_name = item.get("latest_release_name")
                    existing_hp.latest_release_price = item.get("latest_release_price")
                    existing_hp.latest_release_badge = item.get("latest_release_badge")
                    existing_hp.latest_release_url = item.get("latest_release_url")
                    updated += 1
        if added > 0 or updated > 0:
            db.commit()
            print(f"[JaChai Seeder] Seeded {added} Hot Product benchmark records, updated {updated} existing.")
    except Exception as exc:
        db.rollback()
        print(f"[JaChai Seeder] Hot product seeding notice: {exc}")
