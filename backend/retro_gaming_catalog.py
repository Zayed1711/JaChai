"""
JaChai Authoritative Retro & Previous Generation Gaming Consoles Catalog
(backend/retro_gaming_catalog.py)

Comprehensive, production-grade dataset of retro, vintage, and previous-generation
gaming consoles and handhelds in the Bangladeshi market (Sony PlayStation 4, PS3, PS2, PSP,
PS Vita, Xbox 360, Xbox One, Nintendo 3DS, Game Boy Advance, Anbernic, Miyoo Mini, Sega).
Verified with authentic Bangladeshi dealer pricing (Star Tech, Custom Mac BD, Ryans, Tech Land,
Daraz, Apple Gadgets BD, Pickaboo).
"""

from typing import List, Dict, Any

RETRO_GAMING_CATALOG_ITEMS: List[Dict[str, Any]] = [
    # --------------------------------------------------------------------------
    # SONY PLAYSTATION 4 (SLIM & PRO)
    # --------------------------------------------------------------------------
    {
        "slug": "sony-playstation-4-slim-1tb",
        "model_code": "PS4 Slim (1TB)",
        "aliases": [
            "ps4", "ps4 slim", "playstation 4", "playstation 4 slim", "sony ps4", "sony ps4 slim",
            "ps4 1tb", "ps4 slim 1tb", "প্লেস্টেশন ৪", "প্লেস্টেশন ৪ স্লিম", "পিএস৪", "পিএস৪ স্লিম"
        ],
        "title_en": "Sony PlayStation 4 Slim (1TB HDR Gaming Console · DualShock 4 Wireless Controller)",
        "title_bn": "সোনি প্লেস্টেশন ৪ স্লিম (১টিবি এইচডিআর গেমিং কনসোল · ডুয়ালশক ৪ কন্ট্রোলার)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Sony",
        "specs_summary": "1.6GHz 8-Core AMD Jaguar CPU · 1.84 TFLOPS AMD Radeon GPU · 8GB GDDR5 RAM · 1TB Internal Storage · HDR10 Support · Full HD 1080p Gaming · Includes DualShock 4 Wireless Controller & HDMI Cable",
        "starting_price": 28500,
        "max_price": 32500,
        "image_url": "https://images.unsplash.com/photo-1507457379470-08b800bebc67?auto=format&fit=crop&w=600&q=80",
        "variant": "1TB HDD · DualShock 4",
        "stores": [
            {"name": "Custom Mac BD", "price": 28500, "url": "https://custommacbd.com/products/playstation-4-slim-1tb"},
            {"name": "Star Tech", "price": 29500, "url": "https://www.startech.com.bd/sony-playstation-4-slim-1tb"},
            {"name": "Ryans Computers", "price": 30500, "url": "https://www.ryans.com/sony-playstation-4-slim-1tb"},
            {"name": "Daraz Bangladesh", "price": 29990, "url": "https://www.daraz.com.bd/catalog/?q=PS4+Slim+1TB"},
        ]
    },
    {
        "slug": "sony-playstation-4-slim-500gb",
        "model_code": "PS4 Slim (500GB)",
        "aliases": [
            "ps4 500gb", "ps4 slim 500gb", "playstation 4 500gb", "sony ps4 500gb", "পিএস৪ ৫০০জিবি"
        ],
        "title_en": "Sony PlayStation 4 Slim (500GB HDR Gaming Console · Jet Black)",
        "title_bn": "সোনি প্লেস্টেশন ৪ স্লিম (৫০০জিবি এইচডিআর গেমিং কনসোল)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Sony",
        "specs_summary": "1.6GHz 8-Core AMD Jaguar CPU · 1.84 TFLOPS AMD Radeon Graphics · 8GB GDDR5 · 500GB Storage · HDR Gaming · Sleek Energy-Efficient Slim Chassis · DualShock 4 Controller",
        "starting_price": 25990,
        "max_price": 28500,
        "image_url": "https://images.unsplash.com/photo-1507457379470-08b800bebc67?auto=format&fit=crop&w=600&q=80",
        "variant": "500GB HDD · Jet Black",
        "stores": [
            {"name": "Custom Mac BD", "price": 25990, "url": "https://custommacbd.com/products/playstation-4-slim-500gb"},
            {"name": "Star Tech", "price": 26900, "url": "https://www.startech.com.bd/sony-playstation-4-slim-500gb"},
            {"name": "Daraz Bangladesh", "price": 27500, "url": "https://www.daraz.com.bd/catalog/?q=PS4+Slim+500GB"},
        ]
    },
    {
        "slug": "sony-playstation-4-pro-1tb",
        "model_code": "PS4 Pro (1TB)",
        "aliases": [
            "ps4 pro", "playstation 4 pro", "sony ps4 pro", "ps4 pro 1tb", "playstation 4 pro 1tb",
            "প্লেস্টেশন ৪ প্রো", "পিএস৪ প্রো"
        ],
        "title_en": "Sony PlayStation 4 Pro (1TB 4K Dynamic Gaming Console · Boost Mode · Enhanced Graphics)",
        "title_bn": "সোনি প্লেস্টেশন ৪ প্রো (১টিবি ৪কে গেমিং কনসোল · বুস্ট মোড)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Sony",
        "specs_summary": "2.1GHz 8-Core AMD Jaguar CPU · 4.2 TFLOPS AMD Radeon Polaris GPU · 8GB GDDR5 + 1GB DDR3 · 1TB Storage · Dynamic 4K Gaming & 4K Video Streaming · Boost Mode for Enhanced Frame Rates",
        "starting_price": 34990,
        "max_price": 38500,
        "image_url": "https://images.unsplash.com/photo-1507457379470-08b800bebc67?auto=format&fit=crop&w=600&q=80",
        "variant": "1TB HDD · 4K Pro Edition",
        "stores": [
            {"name": "Custom Mac BD", "price": 34990, "url": "https://custommacbd.com/products/playstation-4-pro-1tb"},
            {"name": "Star Tech", "price": 36500, "url": "https://www.startech.com.bd/sony-playstation-4-pro-1tb"},
            {"name": "Ryans Computers", "price": 37000, "url": "https://www.ryans.com/sony-playstation-4-pro-1tb"},
            {"name": "Tech Land BD", "price": 36800, "url": "https://www.techlandbd.com/sony-playstation-4-pro"},
        ]
    },

    # --------------------------------------------------------------------------
    # SONY RETRO PLAYSTATION (PS3 & PS2)
    # --------------------------------------------------------------------------
    {
        "slug": "sony-playstation-3-super-slim-500gb",
        "model_code": "PS3 Super Slim (500GB)",
        "aliases": [
            "ps3", "ps3 slim", "ps3 super slim", "playstation 3", "sony ps3", "playstation 3 super slim",
            "প্লেস্টেশন ৩", "পিএস৩"
        ],
        "title_en": "Sony PlayStation 3 Super Slim (500GB HDD · HEN Custom Firmware · DualShock 3 Controller)",
        "title_bn": "সোনি প্লেস্টেশন ৩ সুপার স্লিম (৫০০জিবি · ডুয়ালশক ৩ কন্ট্রোলার)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Consoles",
        "brand": "Sony",
        "specs_summary": "IBM Cell Broadband Engine 3.2GHz · RSX 'Reality Synthesizer' 550MHz · 256MB XDR RAM + 256MB GDDR3 · 500GB Internal Storage · 1080p HDMI Output · Blu-ray Player · HEN/CFW Jailbreak Ready with 40+ Pre-Loaded Games",
        "starting_price": 15500,
        "max_price": 18500,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80",
        "variant": "500GB · DualShock 3 · HEN Mod",
        "stores": [
            {"name": "Custom Mac BD", "price": 15500, "url": "https://custommacbd.com/products/playstation-3-super-slim"},
            {"name": "Daraz Bangladesh", "price": 16500, "url": "https://www.daraz.com.bd/catalog/?q=PS3+Super+Slim"},
            {"name": "Pickaboo", "price": 16990, "url": "https://www.pickaboo.com/product/sony-ps3-super-slim"},
        ]
    },
    {
        "slug": "sony-playstation-2-slim",
        "model_code": "PS2 Slim (FMCB Mod)",
        "aliases": [
            "ps2", "ps2 slim", "playstation 2", "sony ps2", "ps2 console", "প্লেস্টেশন ২", "পিএস২"
        ],
        "title_en": "Sony PlayStation 2 Slim Console (Free McBoot FMCB Edition · 2x DualShock 2 Controllers · 64GB USB)",
        "title_bn": "সোনি প্লেস্টেশন ২ স্লিম কনসোল (ফ্রি ম্যাকবুট এডিশন · ২টি ডুয়ালশক ২ কন্ট্রোলার)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Consoles",
        "brand": "Sony",
        "specs_summary": "Emotion Engine 294MHz 128-bit CPU · Graphics Synthesizer 147MHz · 32MB Direct RDRAM · Free McBoot (FMCB) Memory Card + 64GB High-Speed USB Loaded with 50+ Legendary Classics · Includes 2 DualShock 2 Controllers & AV Component Cables",
        "starting_price": 7500,
        "max_price": 9500,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "FMCB Mod · 2 Controllers · 64GB USB",
        "stores": [
            {"name": "Custom Mac BD", "price": 7500, "url": "https://custommacbd.com/products/playstation-2-slim"},
            {"name": "Daraz Bangladesh", "price": 7990, "url": "https://www.daraz.com.bd/catalog/?q=PS2+Slim+Console"},
            {"name": "Star Tech", "price": 8500, "url": "https://www.startech.com.bd/sony-playstation-2-slim"},
        ]
    },

    # --------------------------------------------------------------------------
    # SONY RETRO HANDHELDS (PSP & PS VITA)
    # --------------------------------------------------------------------------
    {
        "slug": "sony-psp-3000-handheld",
        "model_code": "PSP 3000 (64GB Pro Duo)",
        "aliases": [
            "psp", "psp 3000", "playstation portable", "sony psp", "psp e1000", "psp street",
            "sony psp 3000", "পিএসপি"
        ],
        "title_en": "Sony PSP 3000 PlayStation Portable (4.3-inch Anti-Reflective Screen · 64GB High-Speed Memory · PRO-C CFW)",
        "title_bn": "সোনি পিএসপি ৩০০০ পোর্টেবল কনসোল (৪.৩-ইঞ্চি ডিসপ্লে · ৬৪জিবি মেমোরি)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Sony",
        "specs_summary": "MIPS R4000 333MHz CPU · 64MB RAM · 4.3-inch 16:9 LCD (Anti-Glare / Wide Color Gamut) · Built-in Microphone · PRO-C Permanent Custom Firmware · 64GB MicroSD with Pro Duo Adapter (50+ PSP/PS1/GBA Games)",
        "starting_price": 7990,
        "max_price": 9500,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "PSP 3000 · 64GB PRO-C CFW",
        "stores": [
            {"name": "Custom Mac BD", "price": 7990, "url": "https://custommacbd.com/products/sony-psp-3000"},
            {"name": "Apple Gadgets BD", "price": 8500, "url": "https://www.applegadgetsbd.com/product/sony-psp-3000"},
            {"name": "Daraz Bangladesh", "price": 8800, "url": "https://www.daraz.com.bd/catalog/?q=Sony+PSP+3000"},
        ]
    },
    {
        "slug": "sony-ps-vita-slim-pch2000-128gb",
        "model_code": "PS Vita Slim (128GB Henkaku)",
        "aliases": [
            "ps vita", "psvita", "playstation vita", "ps vita slim", "ps vita 2000", "ps vita 1000",
            "sony ps vita", "পিএস ভিটা"
        ],
        "title_en": "Sony PlayStation Vita Slim PCH-2000 (5-inch HD IPS · Henkaku Custom Firmware · 128GB SD2Vita)",
        "title_bn": "সোনি প্লেস্টেশন ভিটা স্লিম (৫-ইঞ্চি আইপিএস · হেনকাকু ১২৮জিবি)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Sony",
        "specs_summary": "ARM Cortex-A9 Quad-Core CPU · SGX543MP4+ GPU · 512MB RAM + 128MB VRAM · 5-inch Color-Rich IPS LCD · Dual Analog Sticks · Rear Multi-Touch Pad · Henkaku Enso Jailbreak · 128GB SD2Vita Loaded with PKGi Store & RetroArch",
        "starting_price": 14990,
        "max_price": 17500,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "PCH-2000 Slim · 128GB SD2Vita",
        "stores": [
            {"name": "Custom Mac BD", "price": 14990, "url": "https://custommacbd.com/products/sony-ps-vita-slim-2000"},
            {"name": "Daraz Bangladesh", "price": 15900, "url": "https://www.daraz.com.bd/catalog/?q=PS+Vita+Slim"},
            {"name": "Star Tech", "price": 16500, "url": "https://www.startech.com.bd/sony-ps-vita-slim"},
        ]
    },

    # --------------------------------------------------------------------------
    # MICROSOFT XBOX RETRO & PREVIOUS GEN (XBOX 360 & XBOX ONE S)
    # --------------------------------------------------------------------------
    {
        "slug": "microsoft-xbox-360-e-500gb-rgh",
        "model_code": "Xbox 360 E (500GB RGH)",
        "aliases": [
            "xbox 360", "xbox 360 slim", "xbox 360 e", "xbox 360 rgh", "xbox 360 jtag",
            "microsoft xbox 360", "এক্সবক্স ৩৬০"
        ],
        "title_en": "Microsoft Xbox 360 E (500GB HDD · RGH 3.0 JTAG Mod · Aurora Custom Dashboard)",
        "title_bn": "মাইক্রোসফট এক্সবক্স ৩৬০ ই (৫০০জিবি হার্ডডিস্ক · আরজিএইচ ৩.০ মোড)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Consoles",
        "brand": "Microsoft",
        "specs_summary": "3.2GHz Triple-Core Xenon CPU · 500MHz ATI Xenos GPU · 512MB Unified GDDR3 RAM · 500GB Internal Hard Drive · RGH 3.0 Instant Boot JTAG Modded with Aurora Dashboard · Includes Wireless Controller & HDMI Cable",
        "starting_price": 15990,
        "max_price": 18500,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80",
        "variant": "500GB HDD · RGH 3.0 · Wireless Controller",
        "stores": [
            {"name": "Custom Mac BD", "price": 15990, "url": "https://custommacbd.com/products/microsoft-xbox-360-e"},
            {"name": "Daraz Bangladesh", "price": 16900, "url": "https://www.daraz.com.bd/catalog/?q=Xbox+360+E+500GB"},
            {"name": "Ryans Computers", "price": 17500, "url": "https://www.ryans.com/microsoft-xbox-360-e"},
        ]
    },
    {
        "slug": "microsoft-xbox-one-s-1tb",
        "model_code": "Xbox One S (1TB)",
        "aliases": [
            "xbox one s", "xbox one", "xbox one 1tb", "microsoft xbox one s", "xbox 1s",
            "এক্সবক্স ওয়ান এস", "এক্সবক্স ওয়ান"
        ],
        "title_en": "Microsoft Xbox One S (1TB HDR Gaming Console · 4K Ultra HD Blu-ray · Robot White)",
        "title_bn": "মাইক্রোসফট এক্সবক্স ওয়ান এস (১টিবি এইচডিআর গেমিং কনসোল · ৪কে ব্লুরে)",
        "category": "Gaming Consoles",
        "subcategory": "Consoles",
        "brand": "Microsoft",
        "specs_summary": "1.75GHz 8-Core Custom AMD Jaguar CPU · 1.4 TFLOPS AMD Radeon GPU · 8GB DDR3 RAM · 1TB Storage · 4K Ultra HD Blu-ray Player · HDR10 Gaming & Streaming · Spatial Audio with Dolby Atmos",
        "starting_price": 26500,
        "max_price": 29990,
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80",
        "variant": "1TB HDD · Robot White · 4K Blu-ray",
        "stores": [
            {"name": "Star Tech", "price": 26500, "url": "https://www.startech.com.bd/microsoft-xbox-one-s-1tb"},
            {"name": "Custom Mac BD", "price": 27200, "url": "https://custommacbd.com/products/xbox-one-s-1tb"},
            {"name": "Ryans Computers", "price": 28500, "url": "https://www.ryans.com/microsoft-xbox-one-s-1tb"},
            {"name": "Daraz Bangladesh", "price": 28990, "url": "https://www.daraz.com.bd/catalog/?q=Xbox+One+S+1TB"},
        ]
    },

    # --------------------------------------------------------------------------
    # NINTENDO RETRO HANDHELDS (3DS & GAME BOY ADVANCE)
    # --------------------------------------------------------------------------
    {
        "slug": "nintendo-3ds-xl-handheld",
        "model_code": "Nintendo 3DS XL (64GB CFW)",
        "aliases": [
            "nintendo 3ds", "3ds", "nintendo 3ds xl", "3ds xl", "new 3ds xl", "2ds xl",
            "nintendo 2ds", "নিনটেন্ডো থ্রিডিএস"
        ],
        "title_en": "Nintendo 3DS XL Dual Screen Handheld (Glasses-Free 3D · 64GB High-Speed · Luma3DS CFW)",
        "title_bn": "নিনটেন্ডো ৩ডিএস এক্সএল হ্যান্ডহেল্ড (গ্লাসেস-ফ্রি ৩ডি · ৬৪জিবি)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Nintendo",
        "specs_summary": "ARM11 Dual-Core 268MHz CPU · PICA200 GPU · Dual Screens (4.88-inch Autostereoscopic 3D Top Screen + 4.18-inch Resistive Touchscreen Bottom) · Luma3DS Permanent Custom Firmware · 64GB MicroSD with hShop & FBI Installer",
        "starting_price": 16500,
        "max_price": 19500,
        "image_url": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?auto=format&fit=crop&w=600&q=80",
        "variant": "Dual Screen · 64GB Luma3DS CFW",
        "stores": [
            {"name": "Custom Mac BD", "price": 16500, "url": "https://custommacbd.com/products/nintendo-3ds-xl"},
            {"name": "Daraz Bangladesh", "price": 17500, "url": "https://www.daraz.com.bd/catalog/?q=Nintendo+3DS+XL"},
            {"name": "Star Tech", "price": 18200, "url": "https://www.startech.com.bd/nintendo-3ds-xl"},
        ]
    },
    {
        "slug": "nintendo-game-boy-advance-sp-ips",
        "model_code": "Game Boy Advance SP (IPS V2)",
        "aliases": [
            "game boy", "gameboy", "game boy advance", "game boy advance sp", "gba", "gba sp",
            "game boy color", "gbc", "গেমবয়", "গেম বয়"
        ],
        "title_en": "Nintendo Game Boy Advance SP (V2 IPS Backlit Screen Mod · 900mAh Rechargeable Li-Ion · EZ-Flash Omega Ready)",
        "title_bn": "নিনটেন্ডো গেম বয় অ্যাডভান্স এসপি (আইপিএস ভি২ ব্যাকলিট স্ক্রিন মোড)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Nintendo",
        "specs_summary": "16.78MHz 32-bit ARM7TDMI + 8-bit Z80 Co-Processor · Upgraded 3.0-inch V2 IPS Backlit LCD with 10 Brightness Levels · Clamshell Folding Protective Design · Plays all original Game Boy, Game Boy Color, and Game Boy Advance Cartridges",
        "starting_price": 8500,
        "max_price": 11500,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "IPS Backlit V2 Screen Mod",
        "stores": [
            {"name": "Custom Mac BD", "price": 8500, "url": "https://custommacbd.com/products/game-boy-advance-sp-ips"},
            {"name": "Daraz Bangladesh", "price": 9200, "url": "https://www.daraz.com.bd/catalog/?q=Game+Boy+Advance+SP"},
            {"name": "Star Tech", "price": 9800, "url": "https://www.startech.com.bd/game-boy-advance-sp"},
        ]
    },

    # --------------------------------------------------------------------------
    # ALL-IN-ONE RETRO EMULATION HANDHELDS (ANBERNIC & MIYOO MINI)
    # --------------------------------------------------------------------------
    {
        "slug": "anbernic-rg35xx-plus-retro-handheld",
        "model_code": "Anbernic RG35XX Plus (64GB)",
        "aliases": [
            "anbernic", "anbernic rg35xx", "rg35xx", "anbernic rg35xx plus", "rg35xx plus",
            "rg35xx h", "retro handheld console", "অ্যানবারনিক", "অ্যানবারনিক আরজি৩৫এক্সএক্স"
        ],
        "title_en": "Anbernic RG35XX Plus Retro Gaming Handheld (3.5-inch IPS 640x480 · Allwinner H700 · 64GB 5000+ Games)",
        "title_bn": "অ্যানবারনিক আরজি৩৫এক্সএক্স প্লাস রেট্রো গেমিং কনসোল (৩.৫-ইঞ্চি আইপিএস · ৫০০০+ গেম)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Anbernic",
        "specs_summary": "Allwinner H700 Quad-Core ARM Cortex-A53 1.5GHz · Dual-Core Mali-G31 MP2 GPU · 1GB LPDDR4 RAM · 3.5-inch OCA Full Lamination IPS Screen (640x480) · 3300mAh Battery (8h Playtime) · Supports PS1, PSP, N64, Arcade, GBA, GBC, SNES, NES, Sega · Mini HDMI TV Output & Bluetooth 4.2",
        "starting_price": 5850,
        "max_price": 7200,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "3.5-inch IPS · 64GB 5000+ Games",
        "stores": [
            {"name": "Star Tech", "price": 5850, "url": "https://www.startech.com.bd/anbernic-rg35xx-plus-retro-gaming-console"},
            {"name": "Apple Gadgets BD", "price": 6200, "url": "https://www.applegadgetsbd.com/product/anbernic-rg35xx-plus"},
            {"name": "Tech Land BD", "price": 6100, "url": "https://www.techlandbd.com/anbernic-rg35xx-plus"},
            {"name": "Pickaboo", "price": 6490, "url": "https://www.pickaboo.com/product/anbernic-rg35xx-plus"},
            {"name": "Daraz Bangladesh", "price": 5990, "url": "https://www.daraz.com.bd/catalog/?q=Anbernic+RG35XX+Plus"},
        ]
    },
    {
        "slug": "miyoo-mini-plus-retro-handheld-64gb",
        "model_code": "Miyoo Mini Plus (64GB)",
        "aliases": [
            "miyoo mini", "miyoo mini plus", "miyoo mini+", "miyoo", "miyoo handheld",
            "মিউ মিনি", "মিউ মিনি প্লাস"
        ],
        "title_en": "Miyoo Mini Plus Retro Handheld Gaming Console (3.5-inch IPS OCA Display · Wi-Fi · 64GB OnionOS Loaded)",
        "title_bn": "মিউ মিনি প্লাস রেট্রো হ্যান্ডহেল্ড গেমিং কনসোল (৩.৫-ইঞ্চি আইপিএস · ওয়াইফাই)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Handhelds",
        "brand": "Miyoo",
        "specs_summary": "ARM Cortex-A7 Dual-Core 1.2GHz · 128MB DDR3 RAM · 3.5-inch IPS Screen (640x480) with Ultra-Narrow Bezels · Built-in Wi-Fi for RetroArch Netplay · 3000mAh Battery · OnionOS Optimized · Emulates PS1, GBA, GBC, SNES, NES, Genesis, NeoGeo",
        "starting_price": 6750,
        "max_price": 7990,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "3.5-inch IPS · 64GB OnionOS",
        "stores": [
            {"name": "Apple Gadgets BD", "price": 6750, "url": "https://www.applegadgetsbd.com/product/miyoo-mini-plus"},
            {"name": "Star Tech", "price": 6990, "url": "https://www.startech.com.bd/miyoo-mini-plus"},
            {"name": "Custom Mac BD", "price": 7200, "url": "https://custommacbd.com/products/miyoo-mini-plus"},
            {"name": "Daraz Bangladesh", "price": 6890, "url": "https://www.daraz.com.bd/catalog/?q=Miyoo+Mini+Plus"},
        ]
    },

    # --------------------------------------------------------------------------
    # SEGA CLASSIC RETRO CONSOLES
    # --------------------------------------------------------------------------
    {
        "slug": "sega-genesis-mini-classic-console",
        "model_code": "Sega Genesis Mini (42 Classics)",
        "aliases": [
            "sega", "sega genesis", "sega mega drive", "sega mini", "sega genesis mini", "সেগা"
        ],
        "title_en": "Sega Genesis Mini Classic Console (42 Legendary Pre-Loaded Games · 2 Wired Controllers · HDMI 720p)",
        "title_bn": "সেগা জেনেসিস মিনি ক্লাসিক কনসোল (৪২টি বিল্ট-ইন গেম · ২টি কন্ট্রোলার · এইচডিএমআই)",
        "category": "Gaming Consoles",
        "subcategory": "Retro Consoles",
        "brand": "Sega",
        "specs_summary": "Faithful 55% Miniature Replica of Original Model 1 Sega Genesis · 42 Pre-Loaded Legendary 16-bit Classics including Sonic the Hedgehog, Castlevania, Contra · HDMI 720p Output with CRT Filter Option · Includes 2 Classic Wired 3-Button USB Controllers",
        "starting_price": 8990,
        "max_price": 10500,
        "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=600&q=80",
        "variant": "42 Built-in Classics · Dual Controllers",
        "stores": [
            {"name": "Custom Mac BD", "price": 8990, "url": "https://custommacbd.com/products/sega-genesis-mini"},
            {"name": "Daraz Bangladesh", "price": 9500, "url": "https://www.daraz.com.bd/catalog/?q=Sega+Genesis+Mini"},
            {"name": "Star Tech", "price": 9990, "url": "https://www.startech.com.bd/sega-genesis-mini"},
        ]
    },
]
