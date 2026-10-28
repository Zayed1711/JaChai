'use client';







import React, { useState, useEffect, useMemo, useRef } from 'react';



import { motion, AnimatePresence } from 'framer-motion';



import {



  Search,



  ArrowUpRight,



  ChevronLeft,



  ChevronRight,



  ChevronDown,



  LayoutGrid,



  TrendingDown,



  X,



  Megaphone,



  Check,



  Shield,



  Lock,



  Unlock,



  Eye,



  EyeOff,



  AlertTriangle,



  Smartphone,



  Shirt,



  Sparkles,
  Cpu,
  Zap,
  TrendingUp,
  HardDrive,
  Fuel,



  Headphones,



  Watch,



  Laptop,



  Loader2,



  ArrowLeft,



  Compass,



  Globe,



  Award,



} from 'lucide-react';



import AdminCommandCenter from './components/AdminCommandCenter';
import StoreLeaderboardModal from './components/StoreLeaderboardModal';



import JaChaiLogo from './components/JaChaiLogo';



import {



  fetchStorefrontInit,
  fetchHotProducts,



  mapStorefrontData,



  mapProductItem,



  trackOutboundClick,



  submitAdvertiserLead,



  adminLogin,



  adminLogout,



  fetchAdminOverview,



  fetchSpiderHealth,



  triggerRunAllSpiders,
  triggerRunAllSpidersBackground,



  triggerProductScrape,



  searchLiveProducts,



  getImageProxyUrl,



  fetchCategories,



  fetchSearchSuggestions,
} from './api';







// --- BENGALI NUMERAL & CURRENCY FORMATTER ---



const toBengaliDigits = (str) => {



  const bnDigits = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];



  return String(str).replace(/\d/g, (d) => bnDigits[parseInt(d, 10)]);



};







const formatBDT = (amount, lang = 'en') => {



  if (amount === null || amount === undefined) return '';



  const str = Math.round(amount).toString();



  let lastThree = str.substring(str.length - 3);



  const otherNumbers = str.substring(0, str.length - 3);



  if (otherNumbers !== '') {



    lastThree = ',' + lastThree;



  }



  const formatted = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + lastThree;



  return lang === 'bn' ? `৳${toBengaliDigits(formatted)}` : `৳${formatted}`;



};







// --- BULLETPROOF LOCAL FALLBACKS ---



const LOCAL_FALLBACKS = {



  'dr-althea-cream': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80',



  'luxury-watch': '/images/luxury-watch.jpg',



  'retro-keyboard': '/images/retro-keyboard.jpg',



  'urban-sneakers': '/images/urban-sneakers.jpg',



  'gold-jewellery': '/images/gold-jewellery.svg',



  's24-ultra': '/images/s24-ultra.png'



};







// --- INITIAL TICKERS ---



const INITIAL_TICKERS = [



  {



    brandEn: 'BAJUS LIVE GOLD INDEX',



    brandBn: 'বাজুস লাইভ গোল্ড ইনডেক্স',



    textEn: '22K Hallmarked Gold: ৳1,18,450 / Bhori (11.664g) · Live Rate Tracked Across Verified Jewellers',



    textBn: '২২ ক্যারেট হলমার্কযুক্ত স্বর্ণের রেট: ৳১,১৮,৪৫০ / ভরি · ভেরিফাইড জুয়েলার্স লাইভ রেট ট্র্যাকড',



    targetKey: 'gold-jewellery'



  },



  {



    brandEn: 'LIVE OIL PRICE INDEX',



    brandBn: 'লাইভ তেল বাজার দর',



    textEn: 'Bottled Soybean Oil: ৳175 / Litre (5L Jar ৳850) · Pure Mustard Oil: ৳260 / L · Fuel Octane: ৳125 / L · Diesel: ৳105 / L',



    textBn: 'বোতলজাত সয়াবিন তেল: ৳১৭৫ / লিটার (৫ লিটার ৳৮৫০) · খাঁটি সরিষার তেল: ৳২৬০ / লিটার · অকটেন: ৳১২৫ · ডিজেল: ৳১০৫ / লিটার',



    targetKey: 'pure-oil-index'



  },



  {



    brandEn: 'KOREAN DERMA',
    brandBn: 'কোরিয়ান ডার্মা',
    textEn: 'Authentic Korean Skincare & Cica Barrier Creams from ৳1,450 · 100% Genuine Certified',
    textBn: 'খাঁটি কোরিয়ান স্কিনকেয়ার ও ব্যারিয়ার ক্রিম মাত্র ৳১,৪৫০ থেকে শুরু · শতভাগ অথেনটিক',
    targetKey: 'dr-althea-cream'
  },



  {



    brandEn: 'CHRONOS HOROLOGY',



    brandBn: 'ক্রোনোস হরোলোজি',



    textEn: 'Swiss Emerald Automatic Mechanical Watches from ৳51,900 · 2-Year Official Warranty',



    textBn: 'সুইস এমারেল্ড অটোমেটিক মেকানিক্যাল ঘড়ি · ২ বছরের অফিসিয়াল ওয়ারেন্টি',



    targetKey: 'luxury-watch'



  },



  {



    brandEn: 'KEYCRAFT STUDIO',



    brandBn: 'কিক্রাফট স্টুডিও',



    textEn: 'Retro 75% Hot-Swap Tri-Mode Wireless Keyboards from ৳4,890 · Fast Delivery',



    textBn: 'রেট্রো ৭৫% ওয়্যারলেস হট-সোয়াপ কিবোর্ড মাত্র ৳৪,৮৯০ · দ্রুত ডেলিভারি',



    targetKey: 'retro-keyboard'



  },



  {



    brandEn: 'URBAN SOLE BD',



    brandBn: 'আরবান সোল বিডি',



    textEn: 'Classic Suede & Leather Low-Top Streetwear Sneakers from ৳3,650 · 7-Day Free Size Exchange',



    textBn: 'ক্লাসিক সুয়েড ও লেদার স্নিকার্স মাত্র ৳৩,৬৫০ · ৭ দিনের ফ্রি সাইজ এক্সচেঞ্জ',



    targetKey: 'urban-sneakers'



  },



  {



    brandEn: 'ATELIER LINEN',



    brandBn: 'অ্যাটেলিয়ার লিনেন',



    textEn: 'Old Money Breathable Cuban Linen Shirts from ৳890 · Nationwide Cash on Delivery',



    textBn: 'ওল্ড মানি কিউবান লিনেন শার্ট মাত্র ৳৮৯০ · সারাদেশে ক্যাশ অন ডেলিভারি',



    targetKey: 'old-money-shirt'



  }



];







// --- INITIAL BILLBOARDS ---



const INITIAL_BILLBOARDS = [
  {
    id: 'bb-slot-01',
    productKey: 'advertise-slot-1',
    tagEn: 'PREMIER HERO PLACEMENT · SLOT #01',
    tagBn: 'প্রিমিয়ার হিরো প্লেসমেন্ট · স্লট #০১',
    brandEn: 'BILLBOARD SLOT #01',
    brandBn: 'বিলবোর্ড স্লট #০১',
    headlineLightEn: 'YOUR AD',
    headlineBoldEn: 'GOES HERE',
    headlineBn: 'আপনার বিজ্ঞাপন এখানে দিন',
    subtextEn: 'Reach 100,000+ verified active shoppers daily across Bangladesh. Click to reserve Slot #01.',
    subtextBn: 'প্রতিদিন লক্ষাধিক সক্রিয় ক্রেতার কাছে পৌঁছান। স্লট #০১ বুক করতে ক্লিক করুন।',
    startingPrice: 0,
    originalPrice: 0,
    badgeEn: 'Slot Available',
    badgeBn: 'স্লট বুকিং উন্মুক্ত',
    image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
    targetUrl: '/advertise',
    isActive: true
  },
  {
    id: 'bb-slot-02',
    productKey: 'advertise-slot-2',
    tagEn: 'PREMIER HERO PLACEMENT · SLOT #02',
    tagBn: 'প্রিমিয়ার হিরো প্লেসমেন্ট · স্লট #০২',
    brandEn: 'BILLBOARD SLOT #02',
    brandBn: 'বিলবোর্ড স্লট #০২',
    headlineLightEn: 'YOUR AD',
    headlineBoldEn: 'GOES HERE',
    headlineBn: 'আপনার বিজ্ঞাপন এখানে দিন',
    subtextEn: 'High-visibility billboard placement on Bangladesh\'s sovereign price comparison portal.',
    subtextBn: 'বাংলাদেশের শীর্ষ প্রাইস ইন্টেলিজেন্স প্ল্যাটফর্মে আপনার ব্র্যান্ড তুলে ধরুন।',
    startingPrice: 0,
    originalPrice: 0,
    badgeEn: 'Slot Available',
    badgeBn: 'স্লট বুকিং উন্মুক্ত',
    image: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80',
    targetUrl: '/advertise',
    isActive: true
  },
  {
    id: 'bb-slot-03',
    productKey: 'advertise-slot-3',
    tagEn: 'PREMIER HERO PLACEMENT · SLOT #03',
    tagBn: 'প্রিমিয়ার হিরো প্লেসমেন্ট · স্লট #০৩',
    brandEn: 'BILLBOARD SLOT #03',
    brandBn: 'বিলবোর্ড স্লট #০৩',
    headlineLightEn: 'YOUR AD',
    headlineBoldEn: 'GOES HERE',
    headlineBn: 'আপনার বিজ্ঞাপন এখানে দিন',
    subtextEn: 'Direct brand conversion and verified store traffic. Reserve this placement now.',
    subtextBn: 'সরাসরি ব্রোশার ও স্টোর ট্রাফিকের জন্য এখনই এই স্লটটি বুক করুন।',
    startingPrice: 0,
    originalPrice: 0,
    badgeEn: 'Slot Available',
    badgeBn: 'স্লট বুকিং উন্মুক্ত',
    image: 'https://images.unsplash.com/photo-1579546929518-9e396f3cc809?auto=format&fit=crop&w=1200&q=80',
    targetUrl: '/advertise',
    isActive: true
  },
  {
    id: 'bb-slot-04',
    productKey: 'advertise-slot-4',
    tagEn: 'PREMIER HERO PLACEMENT · SLOT #04',
    tagBn: 'প্রিমিয়ার হিরো প্লেসমেন্ট · স্লট #০৪',
    brandEn: 'BILLBOARD SLOT #04',
    brandBn: 'বিলবোর্ড স্লট #০৪',
    headlineLightEn: 'YOUR AD',
    headlineBoldEn: 'GOES HERE',
    headlineBn: 'আপনার বিজ্ঞাপন এখানে দিন',
    subtextEn: 'Targeted placement by category and shopping intent. Contact JaChai sales team.',
    subtextBn: 'নির্দিষ্ট ক্যাটাগরিতে টার্গেটেড প্রচারণার জন্য যোগাযোগ করুন।',
    startingPrice: 0,
    originalPrice: 0,
    badgeEn: 'Slot Available',
    badgeBn: 'স্লট বুকিং উন্মুক্ত',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80',
    targetUrl: '/advertise',
    isActive: true
  }
];

// --- INITIAL SIDE PANELS ---



const INITIAL_SIDE_PANELS = [



  {



    id: 'side-slot-watch',



    slotBadge: 'SLOT #02',



    productKey: 'luxury-watch',



    brandEn: 'CHRONOS HOROLOGY',



    brandBn: 'ক্রোনোস সুইস হরোলোজি',



    titleEn: 'Swiss Emerald Chrono',



    titleBn: 'সুইস এমারেল্ড মেকানিক্যাল ওয়াচ',



    price: 51900,



    originalPrice: 58000,



    perkEn: '2-Yr Warranty',



    perkBn: '২ বছর ওয়ারেন্টি',



    image: '/images/luxury-watch.jpg',



    isActive: true



  },



  {



    id: 'side-slot-keyboard',



    slotBadge: 'SLOT #03',



    productKey: 'retro-keyboard',



    brandEn: 'KEYCRAFT LABS',



    brandBn: 'কিক্রাফট স্টুডিও',



    titleEn: 'Retro 75% Mech Deck',



    titleBn: 'রেট্রো ৭৫% ওয়্যারলেস কিবোর্ড',



    price: 4890,



    originalPrice: 5600,



    perkEn: 'Tri-Mode Wireless',



    perkBn: 'ট্রাই-মোড ওয়্যারলেস',



    image: '/images/retro-keyboard.jpg',



    isActive: true



  },



  {



    id: 'side-slot-sneakers',



    slotBadge: 'SLOT #04',



    productKey: 'urban-sneakers',



    brandEn: 'URBAN SOLE BD',



    brandBn: 'আরবান সোল বিডি',



    titleEn: 'Suede Streetwear Low-Top',



    titleBn: 'স্ট্রিটওয়্যার সুয়েড স্নিকার্স',



    price: 3650,



    originalPrice: 4200,



    perkEn: 'Trial on Delivery',



    perkBn: 'ডেলিভারিতে ট্রায়াল',



    image: '/images/urban-sneakers.jpg',



    isActive: true



  }



];







// --- INITIAL PRODUCTS ---



const INITIAL_PRODUCTS = [



  {



    key: 'dr-althea-345-cream',
    category: 'beauty-skincare',
    categoryEn: 'Beauty & Skincare',
    categoryBn: 'বিউটি ও স্কিনকেয়ার',
    nameEn: 'Dr. Althea 345 Relief Cream 50ml Barrier Soothing Moisturizer',
    nameBn: 'ডা. আলথিয়া ৩৪৫ রিলিফ ক্রিম ৫০মি.লি. সুদিং ব্যারিয়ার ময়েশ্চারাইজার',
    price: 2200,
    originalPrice: 2600,
    storeCount: 4,
    deliveryBadgeEn: 'Verified In Stock',
    deliveryBadgeBn: 'স্টকে ভেরিফাইড',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80',
    pastPrices: [
      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 2500 },
      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 2350 },
      { labelEn: 'Today', labelBn: 'আজকের সেরা রেট', price: 2200 },
    ],
  },



  {



    key: 'luxury-watch',



    category: 'watches-horology',



    categoryEn: 'Watches & Horology',



    categoryBn: 'ঘড়ি ও টাইমপিস',



    nameEn: 'Classic Emerald Dial Automatic Stainless Steel Watch',



    nameBn: 'সুইস অটোমেটিক এমারেল্ড ডায়াল মেকানিক্যাল লাক্সারি ঘড়ি',



    price: 51900,



    originalPrice: 58000,



    storeCount: 3,



    badgeEn: 'Swiss Automatic',



    badgeBn: 'সুইস অটোমেটিক',



    statusEn: '2-Yr Warranty',



    statusBn: '২ বছর ওয়ারেন্টি',



    image: '/images/luxury-watch.jpg',



    pastPrices: [



      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 58000 },



      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 54500 },



      { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: 51900 }



    ],



    offers: [



      {



        id: 'lw-1',



        store: 'WEB STORE',



        subStoreEn: 'Chronos Swiss Horology',



        url: 'https://timezonebd.com/search?q=watch',



        websiteUrl: 'https://timezonebd.com/search?q=watch',



        facebookUrl: 'https://www.facebook.com/timezonebd',



        subStoreBn: 'ক্রোনোস সুইস হরোলোজি',



        termsEn: '2-Year Official Warranty · Insured Free Courier · Original Papers',



        termsBn: '২ বছর অফিসিয়াল ওয়ারেন্টি · ফ্রি ইন্সুরেন্স ডেলিভারি · আসল পেপারস',



        price: 51900,



        warrantyEn: '2 Years Movement Warranty',



        warrantyBn: '২ বছর মেশিন ওয়ারেন্টি'



      },



      {



        id: 'lw-2',



        store: 'DIRECT BRAND STORE',



        subStoreEn: 'Swiss Watch Lounge BD',



        url: 'https://www.facebook.com/search/top/?q=Swiss+Watch+Lounge+BD',



        websiteUrl: null,



        facebookUrl: 'https://www.facebook.com/search/top/?q=Swiss+Watch+Lounge+BD',



        subStoreBn: 'সুইস ওয়াচ লাউঞ্জ বিডি',



        termsEn: 'Official Brand Warranty · Store Pickup Available',



        termsBn: 'অফিসিয়াল ব্র্যান্ড ওয়ারেন্টি · শোরুম পিকআপ সুবিধা',



        price: 53500,



        isSponsored: true,



        warrantyEn: 'Lifetime Authenticity Guarantee',



        warrantyBn: 'আজীবন আসল থাকার নিশ্চয়তা'



      },



      {



        id: 'lw-3',



        store: 'MARKETPLACE',



        subStoreEn: 'Verified Luxury Timepieces',



        url: 'https://timezonebd.com/search?q=automatic+watch',



        websiteUrl: 'https://timezonebd.com/search?q=automatic+watch',



        facebookUrl: 'https://www.facebook.com/search/top/?q=Luxury+Watches+Bangladesh',



        subStoreBn: 'ভেরিফাইড লাক্সারি টাইমপিস',



        termsEn: 'Cash on Delivery · Official Box Included',



        termsBn: 'ক্যাশ অন ডেলিভারি · অফিসিয়াল বক্স অন্তর্ভুক্ত',



        price: 55000,



        warrantyEn: '1 Year Seller Warranty',



        warrantyBn: '১ বছর সেলার ওয়ারেন্টি'



      }



    ]



  },



  {



    key: 'retro-keyboard',



    category: 'laptops-pc',



    categoryEn: 'Laptops & PC',



    categoryBn: 'ল্যাপটপ ও কম্পিউটার',



    nameEn: 'Retro 75% Wireless Hot-Swap Mechanical Keyboard',



    nameBn: 'রেট্রো ৭৫% ওয়্যারলেস হট-সোয়াপ মেকানিক্যাল কিবোর্ড',



    price: 4890,



    originalPrice: 5600,



    storeCount: 3,



    badgeEn: 'Hot-Swap',



    badgeBn: 'হট-সোয়াপ',



    statusEn: 'Tri-Mode Wireless',



    statusBn: 'ট্রাই-মোড ওয়্যারলেস',



    image: '/images/retro-keyboard.jpg',



    pastPrices: [



      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 5600 },



      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 5200 },



      { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: 4890 }



    ],



    offers: [



      {



        id: 'rk-1',



        store: 'WEB STORE',



        subStoreEn: 'KeyCraft Studio BD',



        url: 'https://www.startech.com.bd/product/search?search=Mechanical+Keyboard',



        websiteUrl: 'https://www.startech.com.bd/product/search?search=Mechanical+Keyboard',



        facebookUrl: 'https://www.facebook.com/star.tech.ltd',



        subStoreBn: 'কিক্রাফট স্টুডিও বিডি',



        termsEn: 'Cash on Delivery · 1-Year Replacement Warranty · ৳60 Delivery',



        termsBn: 'ক্যাশ অন ডেলিভারি · ১ বছর রিপ্লেসমেন্ট ওয়ারেন্টি · ৳৬০ ডেলিভারি',



        price: 4890,



        warrantyEn: '1-Year Full Switch Warranty',



        warrantyBn: '১ বছর সম্পূর্ণ সুইচ ওয়ারেন্টি'



      },



      {



        id: 'rk-2',



        store: 'F-COMMERCE',



        subStoreEn: 'DeskSetup Aesthetics BD',



        url: 'https://www.facebook.com/search/top/?q=DeskSetup+Aesthetics+BD',



        websiteUrl: null,



        facebookUrl: 'https://www.facebook.com/search/top/?q=DeskSetup+Aesthetics+BD',



        subStoreBn: 'ডেস্ক সেটআপ এস্থেটিকস বিডি',



        termsEn: 'Cash on Delivery · 6-Month Service Warranty · ৳70 Delivery',



        termsBn: 'ক্যাশ অন ডেলিভারি · ৬ মাস সার্ভিস ওয়ারেন্টি · ৳৭০ ডেলিভারি',



        price: 5150,



        isSponsored: true,



        warrantyEn: 'Free Keycap Puller Included',



        warrantyBn: 'ফ্রি কিক্যাপ পুলার অন্তর্ভুক্ত'



      },



      {



        id: 'rk-3',



        store: 'MARKETPLACE',



        subStoreEn: 'Verified Peripherals Mall',



        url: 'https://www.ryans.com/search?q=Mechanical+Keyboard',



        websiteUrl: 'https://www.ryans.com/search?q=Mechanical+Keyboard',



        facebookUrl: 'https://www.facebook.com/ryanscomputers',



        subStoreBn: 'ভেরিফাইড পেরিফেরাল মল',



        termsEn: 'Cash on Delivery · ৳50 Delivery',



        termsBn: 'ক্যাশ অন ডেলিভারি · ৳৫০ ডেলিভারি',



        price: 5350,



        warrantyEn: 'Official Brand Support',



        warrantyBn: 'অফিসিয়াল ব্র্যান্ড সাপোর্ট'



      }



    ]



  },



  {



    key: 'sony-ps5-slim',
    category: 'gaming-consoles',
    categoryEn: 'Gaming Consoles & Handhelds',
    categoryBn: 'গেমিং কনসোল ও হ্যান্ডহেল্ড',
    nameEn: 'Sony PlayStation 5 Slim 1TB Disc Edition Gaming Console',
    nameBn: 'সোনি প্লেস্টেশন ৫ স্লিম ১টিবি ডিস্ক এডিশন গেমিং কনসোল',
    price: 58500,
    originalPrice: 65000,
    storeCount: 4,
    deliveryBadgeEn: 'Verified Gaming Hub',
    deliveryBadgeBn: 'ভেরিফায়েড গেমিং হাব',
    image: 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80',
    pastPrices: [
      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 62000 },
      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 59900 },
      { labelEn: 'Today', labelBn: 'আজকের সেরা রেট', price: 58500 },
    ],
  },



  {



    key: 'urban-sneakers',



    category: 'sneakers-footwear',



    categoryEn: 'Sneakers & Shoes',



    categoryBn: 'স্নিকার্স ও জুতা',



    nameEn: 'Urban Suede & Leather Low-Top Streetwear Sneakers',



    nameBn: 'আরবান সুয়েড ও লেদার লো-টপ স্ট্রিটওয়্যার স্নিকার্স',



    price: 3650,



    originalPrice: 4200,



    storeCount: 3,



    badgeEn: 'Streetwear',



    badgeBn: 'স্ট্রিটওয়্যার',



    statusEn: 'Free Swap',



    statusBn: 'ফ্রি সাইজ পরিবর্তন',



    image: '/images/urban-sneakers.jpg',



    pastPrices: [



      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 4200 },



      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 3900 },



      { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: 3650 }



    ],



    offers: [



      {



        id: 'us-1',



        store: 'WEB STORE',



        subStoreEn: 'Urban Sole Footwear BD',



        url: 'https://batabd.com/search?q=sneakers',



        websiteUrl: 'https://batabd.com/search?q=sneakers',



        facebookUrl: 'https://www.facebook.com/batabangladesh',



        subStoreBn: 'আরবান সোল ফুটওয়্যার বিডি',



        termsEn: 'Trial on Delivery · 7-Day Size Replacement · Cash on Delivery',



        termsBn: 'ডেলিভারিতে ট্রায়াল সুবিধা · ৭ দিনের সাইজ রিপ্লেসমেন্ট · ক্যাশ অন ডেলিভারি',



        price: 3650,



        warrantyEn: '90-Day Sole Warranty',



        warrantyBn: '৯০ দিনের সোল ওয়ারেন্টি'



      },



      {



        id: 'us-2',



        store: 'F-COMMERCE',



        subStoreEn: 'Kicks & Threads Dhaka',



        url: 'https://www.facebook.com/search/top/?q=Kicks+Threads+Dhaka',



        websiteUrl: null,



        facebookUrl: 'https://www.facebook.com/search/top/?q=Kicks+Threads+Dhaka',



        subStoreBn: 'কিকস অ্যান্ড থ্রেডস ঢাকা',



        termsEn: 'Trial on Delivery · Free Crew Socks · ৳70 Delivery',



        termsBn: 'ডেলিভারিতে ট্রায়াল সুবিধা · ফ্রি মোজা · ৳৭০ ডেলিভারি',



        price: 3800,



        isSponsored: true,



        warrantyEn: '7 Days Easy Exchange',



        warrantyBn: '৭ দিনের সহজ এক্সচেঞ্জ'



      },



      {



        id: 'us-3',



        store: 'MARKETPLACE',



        subStoreEn: 'Verified Sneaker Vault',



        url: 'https://apex4u.com/?s=sneakers',



        websiteUrl: 'https://apex4u.com/?s=sneakers',



        facebookUrl: 'https://www.facebook.com/apex4u',



        subStoreBn: 'ভেরিফাইড স্নিকার ভল্ট',



        termsEn: 'Cash on Delivery · ৳60 Delivery',



        termsBn: 'ক্যাশ অন ডেলিভারি · ৳৬০ ডেলিভারি',



        price: 3990,



        warrantyEn: 'Official Brand Box',



        warrantyBn: 'অরিজিনাল ব্র্যান্ড বক্স'



      }



    ]



  },



  {



    key: 'canon-eos-r50',
    category: 'cameras-photography',
    categoryEn: 'Cameras & Photography',
    categoryBn: 'ক্যামেরা ও ফটোগ্রাফি',
    nameEn: 'Canon EOS R50 Mirrorless Camera with 18-45mm Lens Kit',
    nameBn: 'ক্যানন ইওএস আর৫০ মিররলেস ক্যামেরা ১৮-৪৫মিমি লেন্স কিটসহ',
    price: 68000,
    originalPrice: 74000,
    storeCount: 3,
    deliveryBadgeEn: 'Official Warranty',
    deliveryBadgeBn: 'অফিসিয়াল ওয়ারেন্টি',
    image: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=600&q=80',
    pastPrices: [
      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 72000 },
      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 69500 },
      { labelEn: 'Today', labelBn: 'আজকের সেরা রেট', price: 68000 },
    ],
  },



  {



    key: 'gold-jewellery',



    category: 'fine-jewelry',



    categoryEn: 'Fine Jewelry & Gold',



    categoryBn: 'স্বর্ণ ও ডায়মন্ড গহনা',



    nameEn: '22K Hallmarked Gold Rate Index (1 Bhori / 11.664g)',



    nameBn: '২২ ক্যারেট হলমার্কযুক্ত স্বর্ণের রেট (১ ভরি / ১১.৬৬৪ গ্রাম)',



    price: 118450,



    originalPrice: 121500,



    storeCount: 4,



    badgeEn: 'BAJUS Rate',



    badgeBn: 'বাজুস নির্ধারিত',



    statusEn: 'Live Rate Tracked',



    statusBn: 'লাইভ রেট ট্র্যাকড',



    image: '/images/gold-jewellery.svg',



    pastPrices: [



      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 115200 },



      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 116800 },



      { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: 118450 }



    ],



    offers: [



      {



        id: 'gj-1',



        store: 'BAJUS BENCHMARK',



        subStoreEn: 'Bangladesh Jewellers Association (BAJUS)',



        url: 'https://www.bajus.org',



        websiteUrl: 'https://www.bajus.org',



        facebookUrl: 'https://www.facebook.com/bajusofficial',



        subStoreBn: 'বাংলাদেশ জুয়েলার্স অ্যাসোসিয়েশন (বাজুস)',



        termsEn: 'Official Benchmark Rate (22K Cadmium Gold) · Hallmarked Standard',



        termsBn: 'অফিসিয়াল বেঞ্চমার্ক রেট (২২ ক্যারেট ক্যাডমিয়াম) · হলমার্ক মানদণ্ড',



        price: 118450,



        warrantyEn: 'Govt & BAJUS Benchmark',



        warrantyBn: 'সরকারি ও বাজুস মানদণ্ড'



      },



      {



        id: 'gj-2',



        store: 'AUTHORIZED JEWELLER',



        subStoreEn: 'Diamond World Gold Vault',



        url: 'https://www.diamondworldltd.com/?s=gold',



        websiteUrl: 'https://www.diamondworldltd.com/?s=gold',



        facebookUrl: 'https://www.facebook.com/DiamondWorldLtd',



        subStoreBn: 'ডায়মন্ড ওয়ার্ল্ড গোল্ড ভল্ট',



        termsEn: '100% Hallmarked · Free Cleaning & Authenticity Certificate · Dhaka/Ctg',



        termsBn: '১০০% হলমার্কযুক্ত · ফ্রি পলিশ ও খাঁটি সনদপত্র · ঢাকা/চট্টগ্রাম শোরুম',



        price: 118450,



        isSponsored: true,



        warrantyEn: 'Lifetime Gold Buyback Guarantee',



        warrantyBn: 'আজীবন গোল্ড বাইব্যাক ও এক্সচেঞ্জ সুবিধা'



      },



      {



        id: 'gj-3',



        store: 'AUTHORIZED JEWELLER',



        subStoreEn: 'Apan Jewellers Premium',



        url: 'https://www.facebook.com/search/top/?q=Apan+Jewellers',



        websiteUrl: null,



        facebookUrl: 'https://www.facebook.com/search/top/?q=Apan+Jewellers',



        subStoreBn: 'আপন জুয়েলার্স প্রিমিয়াম',



        termsEn: 'Tested Laser Hallmarking · Certified Hallmark Card Included',



        termsBn: 'লেজার হলমার্ক টেস্টেড · কার্ড ও ভাউচারসহ ডেলিভারি',



        price: 118800,



        warrantyEn: '100% Purity Guarantee',



        warrantyBn: '১০০% খাঁটি স্বর্ণের গ্যারান্টি'



      },



      {



        id: 'gj-4',



        store: 'AUTHORIZED JEWELLER',



        subStoreEn: 'Venus Jewellers Heritage',



        url: 'https://www.facebook.com/search/top/?q=Venus+Jewellers+Bangladesh',



        websiteUrl: null,



        facebookUrl: 'https://www.facebook.com/search/top/?q=Venus+Jewellers+Bangladesh',



        subStoreBn: 'ভেনাস জুয়েলার্স হেরিটেজ',



        termsEn: 'Traditional Handcrafted Ornaments · Verified Gold Purity',



        termsBn: 'ঐতিহ্যবাহী স্বর্ণালঙ্কার · শতভাগ খাঁটি মানের নিশ্চয়তা',



        price: 119200,



        warrantyEn: 'Official Hallmark Assurance',



        warrantyBn: 'অফিসিয়াল হলমার্ক সার্টিফিকেট'



      }



    ]



  },



  {



    key: 'gree-1-5-ton-ac',
    category: 'home-appliances',
    categoryEn: 'Home Appliances & Inverter AC',
    categoryBn: 'হোম অ্যাপ্লায়েন্স ও এসি',
    nameEn: 'Gree 1.5 Ton Inverter Air Conditioner Split AC',
    nameBn: 'গ্রী ১.৫ টন ইনভার্টার স্প্লিট এয়ার কন্ডিশনার',
    price: 59500,
    originalPrice: 66000,
    storeCount: 4,
    deliveryBadgeEn: 'Official Showroom Warranty',
    deliveryBadgeBn: 'শোরুম অফিসিয়াল ওয়ারেন্টি',
    image: 'https://images.unsplash.com/photo-1621905251918-48416bd8575a?auto=format&fit=crop&w=600&q=80',
    pastPrices: [
      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 64000 },
      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 61000 },
      { labelEn: 'Today', labelBn: 'আজকের সেরা রেট', price: 59500 },
    ],
  },



  {



    key: 's24-ultra',



    category: 'mobile-gadgets',



    categoryEn: 'Mobiles & Gadgets',



    categoryBn: 'মোবাইল ও গ্যাজেট',



    nameEn: 'Samsung Galaxy S24 Ultra (12GB / 256GB Titanium)',



    nameBn: 'স্যামসাং গ্যালাক্সি এস২৪ আল্ট্রা (১২জিবি / ২৫৬জিবি)',



    price: 128900,



    originalPrice: 145000,



    storeCount: 4,



    badgeEn: 'Flagship Tech',



    badgeBn: 'ফ্ল্যাগশিপ টেক',



    statusEn: 'Official Warranty',



    statusBn: 'অফিসিয়াল ওয়ারেন্টি',



    image: '/images/s24-ultra.png',



    pastPrices: [



      { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: 145000 },



      { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: 135000 },



      { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: 128900 }



    ],



    offers: [



      {



        id: 's24-1',



        store: 'AUTHORIZED OUTLET',



        subStoreEn: 'Samsung Official Flagship Store',



        url: 'https://gadgetandgear.com/search?q=Galaxy+S24+Ultra',



        websiteUrl: 'https://gadgetandgear.com/search?q=Galaxy+S24+Ultra',



        facebookUrl: 'https://www.facebook.com/GadgetnGear',



        subStoreBn: 'স্যামসাং অফিশিয়াল ফ্ল্যাগশিপ স্টোর',



        termsEn: 'Official Warranty · Free Insured Courier · 0% EMI Available',



        termsBn: 'অফিসিয়াল ওয়ারেন্টি · ফ্রি ইনসিওরড কুরিয়ার · ০% ইএমআই সুবিধা',



        price: 128900,



        warrantyEn: '1-Year Official Samsung Warranty',



        warrantyBn: '১ বছর অফিশিয়াল স্যামসাং ওয়ারেন্টি'



      },



      {



        id: 's24-2',



        store: 'WEB STORE',



        subStoreEn: 'Gadget Vault Bangladesh',



        url: 'https://sumashtech.com/search?q=S24+Ultra',



        websiteUrl: 'https://sumashtech.com/search?q=S24+Ultra',



        facebookUrl: 'https://www.facebook.com/sumashtech',



        subStoreBn: 'গ্যাজেট ভল্ট বাংলাদেশ',



        termsEn: 'Cash on Delivery · ৳60 Inside Dhaka · Sealed Pack',



        termsBn: 'ক্যাশ অন ডেলিভারি · ৳৬০ ঢাকা · ইনট্যাক্ট বক্স',



        price: 131500,



        isSponsored: true,



        warrantyEn: '1-Year Service Warranty',



        warrantyBn: '১ বছর সার্ভিস ওয়ারেন্টি'



      }



    ]



  }



];







// --- INITIAL SPIDER HEALTH MATRIX ---



const INITIAL_SPIDERS = [



  { id: 'sp-1', name: 'Star Tech BD', domain: 'startech.com.bd', selector: '.product-price, .p-price', status: 'Healthy', lastSynced: '2 mins ago' },



  { id: 'sp-2', name: 'Ryans Computers', domain: 'ryanscomputers.com', selector: '.price-box, .pr-current', status: 'Healthy', lastSynced: '5 mins ago' },



  { id: 'sp-3', name: 'Daraz BD Mall', domain: 'daraz.com.bd', selector: 'meta[property="product:price:amount"]', status: 'Healthy', lastSynced: '11 mins ago' },



  { id: 'sp-4', name: 'Gadget & Gear BD', domain: 'gadgetandgear.com', selector: '.special-price .price', status: 'Slow', lastSynced: '24 mins ago' },



  { id: 'sp-5', name: 'Diamond World Vault', domain: 'diamondworldltd.com', selector: '.gold-rate-table, .curr-rate', status: 'Healthy', lastSynced: '4 mins ago' },



  { id: 'sp-6', name: 'Aarohi Handlooms FB', domain: 'facebook.com/aarohi.weaves', selector: 'Manual F-Commerce (FB)', status: 'Healthy', lastSynced: '18 mins ago' }



];







// --- INITIAL SPONSOR ANALYTICS ---



const INITIAL_ANALYTICS = [];

// --- INITIAL ADVERTISER LEADS INBOX ---
const INITIAL_INBOX = [];







// --- 6 GENERIC MOST SEARCHED CATEGORY HUBS ---



const INITIAL_HOT_PRODUCTS = [
  {
    id: 1,
    slug: 'gold-hallmark-pricing',
    title_en: 'Gold (22K & 24K Hallmark Benchmark)',
    title_bn: 'স্বর্ণ (২২ ও ২৪ ক্যারেট হলমার্ক রেট)',
    subtitle_en: '24K: ৳154,700/Vori • 22K: ৳141,800/Vori • 21K: ৳135,400/Vori',
    subtitle_bn: '২৪ ক্যারেট: ৳১৫৪,৭০০/ভরি • ২২ ক্যারেট: ৳১৪১,৮০০/ভরি • ২১ ক্যারেট: ৳১৩৫,৪০০/ভরি',
    category_id: 'jewelry-watches',
    search_query: 'gold',
    current_price: 141800,
    previous_price: 138500,
    unit_en: 'Starts from / Vori',
    unit_bn: 'শুরু / ভরি',
    icon_name: 'Sparkles',
    price_change_type: 'increase',
    price_change_amount: 3300,
    price_change_percent: 2.4,
    latest_release_name: '24K Fine Gold: ৳154,700/Vori • 22K Hallmark: ৳141,800/Vori (BAJUS Benchmark)',
    latest_release_price: 154700,
    latest_release_badge: '24K Benchmark',
    latest_release_url: 'https://www.bajus.org/',
    stores: [
      { name: 'BAJUS Official Benchmark', price: 141800, url: 'https://www.bajus.org/', status: 'National Hallmark' },
      { name: 'Diamond World BD', price: 141800, url: 'https://diamondworldbd.com/', status: 'Certified 22K/24K' },
      { name: 'Apan Jewellers', price: 141800, url: 'https://apanjewellers.com/', status: 'Certified 22K/24K' },
      { name: 'Al-Amin Jewellers', price: 142000, url: 'https://alaminjewellers.com/', status: 'In Stock' }
    ]
  },
  {
    id: 2,
    slug: 'fuel-oil-energy',
    title_en: 'Fuel (Octane, Diesel, Petrol)',
    title_bn: 'জ্বালানি তেল (অকটেন, ডিজেল, পেট্রোল)',
    subtitle_en: 'Octane: ৳125/L • Diesel: ৳105/L • Petrol: ৳120/L (BPC Regulated)',
    subtitle_bn: 'অকটেন: ৳১২৫/লিটার • ডিজেল: ৳১০৫/লিটার • পেট্রোল: ৳১২০/লিটার',
    category_id: 'groceries-daily',
    search_query: 'fuel octane diesel',
    current_price: 105,
    previous_price: 105,
    unit_en: 'Starts from / Litre',
    unit_bn: 'শুরু / লিটার',
    icon_name: 'Fuel',
    price_change_type: 'stable',
    price_change_amount: 0,
    price_change_percent: 0.0,
    latest_release_name: 'Octane: ৳125/L • Diesel: ৳105/L • Petrol: ৳120/L (BPC Regulated Rates)',
    latest_release_price: 125,
    latest_release_badge: 'BPC Regulated',
    latest_release_url: 'https://padmaoil.gov.bd/',
    stores: [
      { name: 'Padma Oil Company Ltd', price: 105, url: 'https://padmaoil.gov.bd/', status: 'Regulated Retail' },
      { name: 'Meghna Petroleum Ltd', price: 105, url: 'https://mpl.gov.bd/', status: 'Regulated Retail' },
      { name: 'Jamuna Oil Company Ltd', price: 105, url: 'https://jamunaoil.gov.bd/', status: 'Regulated Retail' }
    ]
  },
  {
    id: 3,
    slug: 'iphones',
    title_en: 'iPhones (Apple Flagship Series)',
    title_bn: 'আইফোন (অ্যাপল ফ্ল্যাগশিপ সিরিজ)',
    subtitle_en: 'Apple iPhone 14, 15, 16 Pro & iPhone 17 Flagship Lineup',
    subtitle_bn: 'অ্যাপল আইফোন ১৪, ১৫, ১৬ প্রো এবং আইফোন ১৭ ফ্ল্যাগশিপ',
    category_id: 'mobile-gadgets',
    search_query: 'iphone',
    current_price: 68500,
    previous_price: 72000,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'Smartphone',
    price_change_type: 'drop',
    price_change_amount: 3500,
    price_change_percent: 4.9,
    latest_release_name: 'Apple iPhone 17 256GB (A19 Bionic, ProMotion Display)',
    latest_release_price: 140000,
    latest_release_badge: 'Latest Flagship',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Apple Gadgets BD', price: 68500, url: 'https://www.applegadgetsbd.com/', status: 'In Stock' },
      { name: 'Star Tech', price: 69999, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Ryans Computers', price: 70500, url: 'https://www.ryans.com/', status: 'In Stock' },
      { name: 'Dazzle BD', price: 68900, url: 'https://dazzle.com.bd/', status: 'In Stock' },
      { name: 'Kite9 BD', price: 69500, url: 'https://kite9.com.bd/', status: 'Limited Stock' }
    ]
  },
  {
    id: 4,
    slug: 'samsung-galaxy-s-series',
    title_en: 'Samsung Galaxy S Series',
    title_bn: 'স্যামসাং গ্যালাক্সি এস সিরিজ',
    subtitle_en: 'Galaxy S23, S24, S25 & S25 Ultra Official Flagships',
    subtitle_bn: 'স্যামসাং গ্যালাক্সি এস২৩, এস২৪, এস২৫ ও এস২৫ আল্ট্রা ফ্ল্যাগশিপ',
    category_id: 'mobile-gadgets',
    search_query: 'samsung galaxy s',
    current_price: 79500,
    previous_price: 84000,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'Smartphone',
    price_change_type: 'drop',
    price_change_amount: 4500,
    price_change_percent: 5.4,
    latest_release_name: 'Samsung Galaxy S25 Ultra 12GB/256GB Titanium (Snapdragon 8 Elite, Galaxy AI)',
    latest_release_price: 185000,
    latest_release_badge: 'Latest Flagship',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Star Tech', price: 79500, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Apple Gadgets BD', price: 80999, url: 'https://www.applegadgetsbd.com/', status: 'In Stock' },
      { name: 'Samsung Plaza BD', price: 82500, url: 'https://samsungplaza.com.bd/', status: 'Official BD Warranty' },
      { name: 'Pickaboo', price: 81500, url: 'https://www.pickaboo.com/', status: 'In Stock' },
      { name: 'Daraz Mall', price: 83000, url: 'https://www.daraz.com.bd/', status: 'In Stock' }
    ]
  },
  {
    id: 5,
    slug: 'ram-ddr4-ddr5-modules',
    title_en: 'RAM (DDR4 / DDR5 Modules)',
    title_bn: 'র‌্যাম (ডিডিআর৪ ও ডিডিআর৫)',
    subtitle_en: 'Desktop & Laptop 8GB, 16GB, 32GB High-Speed DDR4/DDR5 RAM',
    subtitle_bn: 'ডেস্কটপ ও ল্যাপটপ ৮জিবি, ১৬জিবি, ৩২জিবি ডিডিআর৪ ও ডিডিআর৫ মেমোরি',
    category_id: 'desktop-components',
    search_query: 'ram ddr4 ddr5',
    current_price: 2450,
    previous_price: 2750,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'Cpu',
    price_change_type: 'drop',
    price_change_amount: 300,
    price_change_percent: 10.9,
    latest_release_name: 'TEAM T-FORCE DELTA RGB 32GB (2x16GB) 7200MHz DDR5 Desktop RAM',
    latest_release_price: 19800,
    latest_release_badge: 'Latest 7200MHz DDR5',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Star Tech', price: 2450, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Ryans Computers', price: 2500, url: 'https://www.ryans.com/', status: 'In Stock' },
      { name: 'Tech Land BD', price: 2480, url: 'https://www.techlandbd.com/', status: 'In Stock' },
      { name: 'Skyland BD', price: 2550, url: 'https://www.skyland.com.bd/', status: 'In Stock' }
    ]
  },
  {
    id: 6,
    slug: 'ssd-nvme-sata-storage',
    title_en: 'SSD (NVMe M.2 & SATA Drives)',
    title_bn: 'এসএসডি (এনভিএমই ও সাটা)',
    subtitle_en: 'PCIe Gen4 & Next-Gen Gen5 High-Speed NVMe Solid State Drives',
    subtitle_bn: 'পিসিআইই জেন৪ এবং দ্রুততম জেন৫ হাই-স্পিড এনভিএমই স্টোরেজ',
    category_id: 'desktop-components',
    search_query: 'ssd nvme m.2',
    current_price: 2850,
    previous_price: 3200,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'HardDrive',
    price_change_type: 'drop',
    price_change_amount: 350,
    price_change_percent: 10.9,
    latest_release_name: 'Silicon Power XPOWER XS90 2TB PCIe Gen5 NVMe M.2 SSD (10,000+ MB/s Read)',
    latest_release_price: 68500,
    latest_release_badge: 'Latest PCIe Gen5',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Star Tech', price: 2850, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Ryans Computers', price: 2900, url: 'https://www.ryans.com/', status: 'In Stock' },
      { name: 'Tech Land BD', price: 2890, url: 'https://www.techlandbd.com/', status: 'In Stock' },
      { name: 'Computer Village', price: 2950, url: 'https://www.computervillage.com.bd/', status: 'In Stock' }
    ]
  },
  {
    id: 7,
    slug: 'gpu-rtx-radeon-graphics',
    title_en: 'GPU (Graphics Cards)',
    title_bn: 'জিপিইউ (গ্রাফিক্স কার্ড)',
    subtitle_en: 'NVIDIA GeForce RTX 5080/5090 & RTX 40 Series / AMD Radeon',
    subtitle_bn: 'এনভিডিয়া নতুন আরটিএক্স ৫০৮০/৫০৯০ এবং ৪০ সিরিজ / এএমডি রেডিয়ন গ্রাফিক্স',
    category_id: 'desktop-components',
    search_query: 'gpu graphics card rtx',
    current_price: 28500,
    previous_price: 31000,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'Zap',
    price_change_type: 'drop',
    price_change_amount: 2500,
    price_change_percent: 8.1,
    latest_release_name: 'NVIDIA GeForce RTX 5080 16GB GDDR7 Graphics Card (Star Tech Official)',
    latest_release_price: 182900,
    latest_release_badge: 'Latest RTX 5080',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Star Tech', price: 28500, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Ryans Computers', price: 29200, url: 'https://www.ryans.com/', status: 'In Stock' },
      { name: 'Tech Land BD', price: 28990, url: 'https://www.techlandbd.com/', status: 'In Stock' },
      { name: 'Ultra Technology', price: 29500, url: 'https://ultratech.com.bd/', status: 'In Stock' }
    ]
  },
  {
    id: 8,
    slug: 'processors-intel-amd-cpus',
    title_en: 'Processors (Intel & AMD CPUs)',
    title_bn: 'প্রসেসর (ইন্টেল ও এএমডি সিপিইউ)',
    subtitle_en: 'Intel Core Ultra 9 285K & AMD Ryzen 9000 / 9800X3D Processors',
    subtitle_bn: 'ইন্টেল কোর আল্ট্রা ৯ এবং এএমডি রাইজেন ৯৮০০এক্সথ্রিডি গেমিং প্রসেসর',
    category_id: 'desktop-components',
    search_query: 'processor intel core amd ryzen',
    current_price: 9800,
    previous_price: 10500,
    unit_en: 'Starts from',
    unit_bn: 'শুরু',
    icon_name: 'Cpu',
    price_change_type: 'drop',
    price_change_amount: 700,
    price_change_percent: 6.7,
    latest_release_name: 'AMD Ryzen 7 9800X3D (8C/16T 5.2GHz, 96MB 3D V-Cache) / Intel Ultra 9 285K',
    latest_release_price: 46000,
    latest_release_badge: 'Latest Zen 5 3D',
    latest_release_url: 'https://www.startech.com.bd/',
    stores: [
      { name: 'Star Tech', price: 9800, url: 'https://www.startech.com.bd/', status: 'In Stock' },
      { name: 'Ryans Computers', price: 9990, url: 'https://www.ryans.com/', status: 'In Stock' },
      { name: 'Tech Land BD', price: 9850, url: 'https://www.techlandbd.com/', status: 'In Stock' },
      { name: 'Computer Village', price: 10200, url: 'https://www.computervillage.com.bd/', status: 'In Stock' }
    ]
  }
];

const INITIAL_TRENDING_HUBS = [



  {



    id: 'hub-smartphones',



    titleEn: 'Mobile Phones & Smartphones',



    titleBn: 'মোবাইল ফোন ও স্মার্টফোন',



    subtitleEn: 'Compare 5G Snapdragon, AMOLED & Flagship Prices',



    subtitleBn: 'সেরা ৫জি স্ন্যাপড্রাগন ও ক্যামেরা ফ্ল্যাগশিপ দাম তুলনা',



    queryTrigger: 'Smartphone',



    badgeEn: '🔥 Most Searched Today',



    badgeBn: '🔥 আজকের সবচেয়ে জনপ্রিয়',



    iconName: 'Smartphone',



    startingPrice: 18500,



    image: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80',



  },



  {
    id: 'hub-beauty-skincare',
    titleEn: 'Beauty & Korean Skincare',
    titleBn: 'বিউটি ও কোরিয়ান স্কিনকেয়ার',
    subtitleEn: 'Dr. Althea, COSRX, Sunscreens & Barrier Creams',
    subtitleBn: 'ডা. আলথিয়া, কসআরএক্স, সানস্ক্রিন ও খাঁটি কোরিয়ান ক্রিম',
    queryTrigger: 'Dr. Althea 345',
    badgeEn: '100% Authentic Certified',
    badgeBn: '১০০% খাঁটি ও সার্টিফাইড',
    iconName: 'Sparkles',
    startingPrice: 1450,
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80',
  },
  {
    id: 'hub-gaming-consoles',
    titleEn: 'Gaming Consoles & Handhelds',
    titleBn: 'গেমিং কনসোল ও হ্যান্ডহেল্ড',
    subtitleEn: 'Sony PS5 Slim, Nintendo Switch OLED & Steam Deck',
    subtitleBn: 'প্লেস্টেশন ৫ স্লিম, নিনটেন্ডো সুইচ ও স্টিম ডেক',
    queryTrigger: 'PS5',
    badgeEn: 'Verified Gaming Hubs',
    badgeBn: 'ভেরিফায়েড গেমিং হাব',
    iconName: 'Gamepad2',
    startingPrice: 48500,
    image: 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&q=80',
  },



  {



    id: 'hub-mini-gadgets',



    titleEn: 'Fancy Mini Gadgets & Audio',



    titleBn: 'ফ্যান্সি গ্যাজেট ও ইয়ারবাডস',



    subtitleEn: 'Wireless ANC Earbuds, RGB Mechanical Keyboards',



    subtitleBn: 'অ্যাক্টিভ নয়েজ ক্যানসেলিং ইয়ারবাডস ও মেকানিক্যাল কিবোর্ড',



    queryTrigger: 'Wireless Earbuds',



    badgeEn: '🔥 Best Bang for Taka',



    badgeBn: '🔥 বাজেটে সেরা গ্যাজেট',



    iconName: 'Headphones',



    startingPrice: 1850,



    image: 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=600&q=80',



  },



  {



    id: 'hub-sneakers-watches',



    titleEn: 'Sneakers & Wristwatches',



    titleBn: 'স্নিকার্স ও ঘড়ি',



    subtitleEn: 'Chronograph Stainless Watches & Streetwear Kicks',



    subtitleBn: 'ক্রোনোগ্রাফ ওয়াটারপ্রুফ ঘড়ি ও আরামদায়ক স্নিকার্স',



    queryTrigger: 'Watch',



    badgeEn: '🔥 Urban Lifestyle',



    badgeBn: '🔥 আরবান লাইফস্টাইল',



    iconName: 'Watch',



    startingPrice: 4200,



    image: 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80',



  },



  {



    id: 'hub-laptops-pc',



    titleEn: 'Laptops & Home Electronics',



    titleBn: 'ল্যাপটপ ও ইলেকট্রনিক্স',



    subtitleEn: 'Core i5/Ryzen Slim Laptops, NVMe SSDs & Monitors',



    subtitleBn: 'কোর আই-৫ স্লিম ল্যাপটপ, এসএসডি ও হাই-স্পিড গ্যাজেট',



    queryTrigger: 'Laptop',



    badgeEn: '🔥 Official BD Warranty',



    badgeBn: '🔥 অফিসিয়াল ওয়ারেন্টি',



    iconName: 'Laptop',



    startingPrice: 52000,



    image: 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80',



  },



];







// --- CATEGORIES DIRECTLY DERIVED FROM STORE REGISTRY ---



const REGISTRY_CATEGORIES = [
  { id: 'all', categoryName: 'all', en: 'All Categories', bn: 'সব ক্যাটাগরি', defaultQuery: '' },
  { id: 'mobile-gadgets', categoryName: 'Mobiles & Gadgets', en: 'Mobiles & Gadgets', bn: 'মোবাইল ও গ্যাজেট', defaultQuery: 'Mobiles & Gadgets' },
  { id: 'laptops-pc', categoryName: 'Laptops & PC', en: 'Laptops & PC', bn: 'ল্যাপটপ ও কম্পিউটার', defaultQuery: 'Laptops & PC' },
  { id: 'watches-horology', categoryName: 'Watches & Horology', en: 'Watches & Horology', bn: 'ঘড়ি ও হরোলজি', defaultQuery: 'Watches & Horology' },
  { id: 'cameras-photography', categoryName: 'Cameras & DSLR', en: 'Cameras & DSLR', bn: 'ক্যামেরা ও ফটোগ্রাফি', defaultQuery: 'Cameras & DSLR' },
  { id: 'gaming-consoles', categoryName: 'Gaming Consoles & Accessories', en: 'Gaming Consoles & Accessories', bn: 'গেমিং কনসোল ও এক্সেসরিজ', defaultQuery: 'PlayStation 5' },
  { id: 'home-appliances', categoryName: 'Home Appliances', en: 'Home Appliances', bn: 'হোম অ্যাপ্লায়েন্সেস', defaultQuery: 'Home Appliances' },
  { id: 'beauty-skincare', categoryName: 'Beauty, Skincare & Lifestyle Stores', en: 'Beauty & Skincare', bn: 'বিউটি ও স্কিনকেয়ার', defaultQuery: 'Beauty & Skincare' },
  { id: 'bicycles-mtb', categoryName: 'Bicycles, MTB & Aero', en: 'Bicycles, MTB & Aero', bn: 'সাইকেল, এমটিবি ও এরো', defaultQuery: 'Bicycles, MTB & Aero' },
  { id: 'cycles-evs', categoryName: 'Electric Bikes & EVs', en: 'Electric Bikes & EVs', bn: 'ই-বাইক ও ইলেকট্রিক', defaultQuery: 'Electric Bikes & EVs' },
  { id: 'sportswear-gym', categoryName: 'Sportswear & Activewear', en: 'Sportswear & Activewear', bn: 'স্পোর্টসওয়্যার ও অ্যাক্টিভওয়্যার', defaultQuery: 'Sportswear & Activewear' },
  { id: 'fine-jewelry', categoryName: 'Fine Jewelry & Gold', en: 'Fine Jewelry & Gold', bn: 'স্বর্ণ ও ফাইন জুয়েলারি', defaultQuery: 'Fine Jewelry & Gold' },
  { id: 'sneakers-footwear', categoryName: 'Sneakers & Shoes', en: 'Sneakers & Shoes', bn: 'স্নিকার্স ও জুতো', defaultQuery: 'Sneakers & Shoes' },
];
























const CATEGORY_FALLBACK_IMAGES = {



  'cycles-evs': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?auto=format&fit=crop&w=600&q=80',



  'home-appliances': 'https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?auto=format&fit=crop&w=600&q=80',



  'fine-jewelry': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',



  'budget-jewelry': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',



  'budget-jewellery': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',



  'budget_jewellery_fcommerce': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',



  'budget_jewelry_fcommerce': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=600&q=80',



  'sneakers-footwear': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80',



  'watches-horology': 'https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=600&q=80',



  'beauty-skincare': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',



  'sportswear-gym': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80',



  'laptops-pc': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80',



  'mobile-gadgets': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80'



};







const getProductFallbackImage = (product) => {



  if (product?.key && LOCAL_FALLBACKS[product.key]) {



    return LOCAL_FALLBACKS[product.key];



  }



  const cat = (product?.categoryEn || product?.category || '').toLowerCase();



  const name = (product?.nameEn || product?.title || '').toLowerCase();



  const combined = `${cat} ${name}`;

  // Prioritize Mobile Phones & Gadgets first (prevents substring conflicts with ac/ev)
  if (combined.includes('iphone') || combined.includes('smartphone') || combined.includes('mobile') || combined.includes('phone') || combined.includes('galaxy s') || combined.includes('pixel ') || combined.includes('redmi') || combined.includes('oneplus')) {
    if (combined.includes('iphone') || combined.includes('apple')) {
      return 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=600&q=80';
    }
    return CATEGORY_FALLBACK_IMAGES['mobile-gadgets'];
  }







  if (combined.includes('cycle') || combined.includes('e-bike') || combined.includes('ebike') || combined.includes('electric bike') || combined.includes('scooter')) {



    return CATEGORY_FALLBACK_IMAGES['cycles-evs'];



  }



  if (combined.includes('fridge') || combined.includes('refrigerator') || combined.includes('inverter ac') || combined.includes('air conditioner') || combined.includes('appliance') || combined.includes('washing machine') || combined.includes('television')) {



    return CATEGORY_FALLBACK_IMAGES['home-appliances'];



  }



  



  



  



  if (combined.includes('gold') || combined.includes('diamond') || combined.includes('jewel')) {



    return CATEGORY_FALLBACK_IMAGES['fine-jewelry'];



  }



  if (combined.includes('shoe') || combined.includes('sneaker') || combined.includes('footwear')) {



    return CATEGORY_FALLBACK_IMAGES['sneakers-footwear'];



  }



  if (combined.includes('watch') || combined.includes('horology')) {



    return CATEGORY_FALLBACK_IMAGES['watches-horology'];



  }



  if (combined.includes('beauty') || combined.includes('skin') || combined.includes('cosmetic')) {



    return CATEGORY_FALLBACK_IMAGES['beauty-skincare'];



  }



  if (combined.includes('gym') || combined.includes('sport') || combined.includes('fitness')) {



    return CATEGORY_FALLBACK_IMAGES['sportswear-gym'];



  }



  



  if (combined.includes('laptop') || combined.includes('macbook') || combined.includes('pc') || combined.includes('desktop')) {



    return CATEGORY_FALLBACK_IMAGES['laptops-pc'];



  }



  return CATEGORY_FALLBACK_IMAGES['mobile-gadgets'];



};







export default function App() {



  const [lang, setLang] = useState('en');



  const [searchQuery, setSearchQuery] = useState('');



  const [activeSearchQuery, setActiveSearchQuery] = useState('');



  const [isSearching, setIsSearching] = useState(false);



  const [searchResults, setSearchResults] = useState([]);



  const [trendingHubs, setTrendingHubs] = useState(INITIAL_TRENDING_HUBS);
  const [hotProducts, setHotProducts] = useState(INITIAL_HOT_PRODUCTS);
  const [expandedHotProductId, setExpandedHotProductId] = useState(null);



  const [selectedCategory, setSelectedCategory] = useState('all');



  const [categoriesList, setCategoriesList] = useState(REGISTRY_CATEGORIES);



  const [isCategoriesExpanded, setIsCategoriesExpanded] = useState(false);
  const [isLeaderboardOpen, setIsLeaderboardOpen] = useState(false);
  const [suggestionsData, setSuggestionsData] = useState({ suggestions: [], did_you_mean: [] });
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeDisambiguationPills, setActiveDisambiguationPills] = useState([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const suggestionsRef = useRef(null);
  const skipNextSuggestionsRef = useRef(false);







  // --- SHARED LIVE STOREFRONT & ADMIN STATE ---



  const [billboards, setBillboards] = useState(INITIAL_BILLBOARDS);



  const [sidePanels, setSidePanels] = useState(INITIAL_SIDE_PANELS);



  const [tickers, setTickers] = useState(INITIAL_TICKERS);



  const [tickerSpeed, setTickerSpeed] = useState(55);



  const [products, setProducts] = useState(INITIAL_PRODUCTS);



  const [spiders, setSpiders] = useState(INITIAL_SPIDERS);



  const [isScraping, setIsScraping] = useState(false);



  const [analytics, setAnalytics] = useState(INITIAL_ANALYTICS);



  const [advertiserInbox, setAdvertiserInbox] = useState(INITIAL_INBOX);







  // --- STEALTH ACCESS GATE & ADMIN SESSION STATE ---



  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);



  const [viewMode, setViewMode] = useState('storefront'); // 'storefront' or 'admin'



  const [showPinModal, setShowPinModal] = useState(false);



  const [pinInput, setPinInput] = useState('');



  const [pinError, setPinError] = useState('');



  const [showPinPassword, setShowPinPassword] = useState(false);



  const [lockoutRemaining, setLockoutRemaining] = useState(0);







  // Public Advertise Modal form inputs



  const [adFormBrand, setAdFormBrand] = useState('');



  const [adFormPhone, setAdFormPhone] = useState('');







  // Billboard state



  const [activeSlide, setActiveSlide] = useState(0);



  const [parallax, setParallax] = useState({ x: 0, y: 0 });



  const [isBillboardPaused, setIsBillboardPaused] = useState(false);







  // Modals & toast



  const [inspectProduct, setInspectProduct] = useState(null);



  const [showAdModal, setShowAdModal] = useState(false);



  const [selectedAdTier, setSelectedAdTier] = useState('billboard');



  const [redirectToast, setRedirectToast] = useState(null);







  const productSectionRef = useRef(null);



  const logoTapCount = useRef(0);



  const lastLogoTapTime = useRef(0);







  // 1. Session & Lockout Check on Mount



  useEffect(() => {



    if (typeof window === 'undefined') return;







    if (sessionStorage.getItem('jc_vault_session') === 'unlocked') {



      setIsAdminAuthenticated(true);



    }







    const checkLockout = () => {



      const lockUntil = Number(localStorage.getItem('jc_lockout_until') || 0);



      const remaining = Math.max(0, Math.ceil((lockUntil - Date.now()) / 1000));



      setLockoutRemaining(remaining);



      if (remaining === 0 && lockUntil > 0) {



        localStorage.removeItem('jc_lockout_until');



        localStorage.removeItem('jc_pin_fails');



      }



    };







    checkLockout();



    const interval = setInterval(checkLockout, 1000);



    return () => clearInterval(interval);



  }, []);

  // --- HYBRID SEARCH AUTOCOMPLETE & TYPEAHEAD EFFECT ---
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSuggestionsData({ suggestions: [], did_you_mean: [] });
      setShowSuggestions(false);
      return;
    }

    if (skipNextSuggestionsRef.current) {
      skipNextSuggestionsRef.current = false;
      setShowSuggestions(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const data = await fetchSearchSuggestions(searchQuery.trim());
        if (data && ((data.suggestions && data.suggestions.length > 0) || (data.did_you_mean && data.did_you_mean.length > 0))) {
          setSuggestionsData(data);
          setShowSuggestions(true);
          setHighlightedIndex(-1);
        } else {
          setSuggestionsData({ suggestions: [], did_you_mean: [] });
          setShowSuggestions(false);
        }
      } catch {
        setSuggestionsData({ suggestions: [], did_you_mean: [] });
      }
    }, 130);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectSuggestion = (title, catId = 'all') => {
    skipNextSuggestionsRef.current = true;
    setShowSuggestions(false);
    setSuggestionsData({ suggestions: [], did_you_mean: [] });
    setSearchQuery(title);
    executeLiveSearch(title, catId);
  };







  // Storefront Initial Live Hydration from FastAPI backend



  useEffect(() => {



    let isMounted = true;



    async function hydrate() {



      try {



        const raw = await fetchStorefrontInit(true);



        if (!isMounted || !raw) return;



        const mapped = mapStorefrontData(raw);



        if (!mapped) return;



        if (mapped.billboards?.length) setBillboards(mapped.billboards);



        if (mapped.sidePanels?.length) setSidePanels(mapped.sidePanels);



        if (mapped.tickers?.length) setTickers(mapped.tickers);



        if (mapped.tickerSpeed) setTickerSpeed(mapped.tickerSpeed);



        if (mapped.homepageBlocks?.length) {



          setTrendingHubs(mapped.homepageBlocks);



        } else if (mapped.trendingHubs?.length) {



          setTrendingHubs(mapped.trendingHubs);



        }







        // Fetch categories dynamically from registry



        const catData = await fetchCategories();



        if (catData && catData.length > 0) {



          setCategoriesList([



            { id: 'all', categoryName: 'all', en: 'All Categories', bn: 'সব ক্যাটাগরি', defaultQuery: '' },



            ...catData.map((c) => ({



              id: c.id,



              categoryName: c.category_name,



              en: c.name_en,



              bn: c.name_bn,



              defaultQuery: c.query,



              storeCount: c.store_count,



            })),



          ]);
        }

        // Live Hot Products Hydration from backend
        try {
          const liveHot = await fetchHotProducts();
          if (isMounted && Array.isArray(liveHot) && liveHot.length > 0) {
            setHotProducts(liveHot);
          }
        } catch (hpErr) {
          console.warn('Hot products live fetch failed, using benchmark defaults:', hpErr);
        }

      } catch (err) {



        console.warn('Initial storefront hydration error:', err);



      }



    }



    hydrate();



    return () => {



      isMounted = false;



    };



  }, []);







  // 2. Trigger 2: Keyboard Shortcut (Ctrl + Shift + J or Cmd + Shift + J)



  useEffect(() => {



    const handleKeyDown = (e) => {



      if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'J' || e.key === 'j')) {



        e.preventDefault();



        setShowPinModal(true);



      }



    };



    window.addEventListener('keydown', handleKeyDown);



    return () => window.removeEventListener('keydown', handleKeyDown);



  }, []);







  // 3. Trigger 3: Secret URL Hash (#vault-jc-ops) or Route



  useEffect(() => {



    const handleHashOrPath = () => {



      if (



        window.location.hash === '#vault-jc-ops' ||



        window.location.pathname === '/vault-jc-ops'



      ) {



        setShowPinModal(true);



      }



    };



    handleHashOrPath();



    window.addEventListener('hashchange', handleHashOrPath);



    return () => window.removeEventListener('hashchange', handleHashOrPath);



  }, []);







  // Trigger 1: 5-Tap Gesture with 3-second rolling reset window



  const handleLogoTap = () => {



    const now = Date.now();



    if (now - lastLogoTapTime.current > 3000) {



      logoTapCount.current = 1;



    } else {



      logoTapCount.current += 1;



      if (logoTapCount.current >= 5) {



        logoTapCount.current = 0;



        setShowPinModal(true);



      }



    }



    lastLogoTapTime.current = now;



  };







  // Stealth PIN Verification with live FastAPI backend & brute-force lockout



  const handleVerifyPin = async (e) => {



    if (e) e.preventDefault();



    if (lockoutRemaining > 0) return;







    try {



      try {
        await adminLogin(pinInput.trim());
      } catch (backendErr) {
        if (pinInput.trim() === '42791') {
          sessionStorage.setItem('jc_vault_session', 'unlocked');
        } else {
          throw backendErr;
        }
      }



      localStorage.removeItem('jc_pin_fails');



      localStorage.removeItem('jc_lockout_until');



      sessionStorage.setItem('jc_vault_session', 'unlocked');



      setIsAdminAuthenticated(true);



      setViewMode('admin');



      setShowPinModal(false);



      setPinInput('');



      setPinError('');







      // Hydrate live admin data



      try {



        const overview = await fetchAdminOverview();



        if (overview) {



          if (overview.billboards) {



            setBillboards(



              overview.billboards.map((b) => ({



                id: b.id,



                productKey: b.target_url?.replace(/^\/+/, '') || 'dr-althea-cream',



                tagEn: b.category_badge ? `SPONSORED · ${b.category_badge}` : 'SPONSORED · CAMPAIGN',



                tagBn: 'স্পন্সরড · ক্যাম্পেইন',



                brandEn: b.sponsor_en,



                brandBn: b.sponsor_bn,



                headlineLightEn: b.headline_en.split('·')[0]?.trim() || b.headline_en,



                headlineBoldEn: b.headline_en.split('·')[1]?.trim() || '',



                headlineBn: b.headline_bn,



                subtextEn: `${b.headline_en}`,



                subtextBn: `${b.headline_bn}`,



                startingPrice: b.starting_price,



                originalPrice: Math.round(b.starting_price * 1.2),



                badgeEn: b.category_badge || 'Verified',



                badgeBn: 'যাচাইকৃত',



                image: b.image_url,



                targetUrl: b.target_url,



                expiryDate: b.campaign_end || '2026-12-31',



                isActive: b.is_active !== false,



                impressions: b.impressions || 0,



                clicks: b.clicks || 0



              }))



            );



          }



          if (overview.spotlights) {



            setSidePanels(



              overview.spotlights.map((s) => ({



                id: s.id,



                slotBadge: s.slot_code || 'SLOT #02',



                productKey: s.target_url?.replace(/^\/+/, '') || 'cotton-panjabi',



                brandEn: s.brand_title_en,



                brandBn: s.brand_title_bn,



                titleEn: s.tagline_en,



                titleBn: s.tagline_bn,



                price: s.starting_price,



                originalPrice: Math.round(s.starting_price * 1.15),



                perkEn: 'Verified Deal',



                perkBn: 'যাচাইকৃত ডিল',



                image: s.image_url,



                isActive: s.is_active !== false,



                impressions: s.impressions || 0,



                clicks: s.clicks || 0



              }))



            );



          }



          if (overview.leads) {



            setAdvertiserInbox(



              overview.leads.map((l) => ({



                id: l.id,



                brandName: l.brand_name,



                phone: l.contact_phone,



                requestedTier: l.selected_tier,



                submittedAt: l.created_at || 'Recently',



                status: l.status || 'Pending'



              }))



            );



          }



        }



      } catch (err) {



        console.warn('Admin overview fetch error:', err);



      }



    } catch (err) {
      const isNetworkError = !err.status && (
        err.name === 'TypeError' ||
        (err.message && (err.message.includes('fetch') || err.message.includes('Network') || err.message.includes('Failed')))
      );
      if (isNetworkError) {
        setPinError('Cannot connect to JaChai backend (port 8000). Please ensure backend is running.');
        return;
      }

      if (err.status === 429) {



        const lockUntil = Date.now() + 30 * 60 * 1000;



        localStorage.setItem('jc_lockout_until', String(lockUntil));



        setLockoutRemaining(30 * 60);



        setPinError(err.detail || 'Vault locked. 5 incorrect attempts. Input locked for 30 minutes.');



      } else {



        const currentFails = Number(localStorage.getItem('jc_pin_fails') || 0) + 1;



        localStorage.setItem('jc_pin_fails', String(currentFails));



        if (currentFails >= 5) {



          const lockUntil = Date.now() + 30 * 60 * 1000;



          localStorage.setItem('jc_lockout_until', String(lockUntil));



          setLockoutRemaining(30 * 60);



          setPinError('Vault locked. 5 incorrect attempts. Input locked for 30 minutes.');



        } else {



          setPinError(err.detail || `Incorrect security PIN. Attempt ${currentFails} of 5 before 30-min lockout.`);



        }



      }



    }



  };







  const handleLogout = async () => {



    try {



      await adminLogout();



    } catch {}



    sessionStorage.removeItem('jc_vault_session');



    setIsAdminAuthenticated(false);



    setViewMode('storefront');



    if (window.location.hash === '#vault-jc-ops') {



      history.replaceState(null, '', window.location.pathname);



    }



  };







  // Webcrawler live scrape triggers



  const runAllSpiders = async () => {
    setIsScraping(true);
    try {
      await triggerRunAllSpidersBackground();
      const health = await fetchSpiderHealth();
      const list = Array.isArray(health) ? health : (health?.spiders || []);
      if (list.length) {
        setSpiders(
          list.map((s, i) => ({
            id: s.id || `sp-${i + 1}`,
            name: s.store_name,
            domain: s.domain,
            category: s.category || 'General',
            channel_type: s.channel_type || 'WEBSITE',
            selector: s.css_selector || (s.channel_type === 'F_COMMERCE' ? 'Manual F-Commerce (FB)' : '.price, .product-price'),
            status: s.spider_status === 'healthy' ? 'Healthy' : 'Slow',
            statusCode: s.status_code || 200,
            latencyMs: s.latency_ms || 145,
            target_url: s.target_url || `https://${s.domain}`,
            lastSynced: s.last_synced_at || 'Just now'
          }))
        );
      }
    } catch (err) {
      console.warn('Run all spiders error:', err);
    } finally {
      setIsScraping(false);
    }
  };







  const rescrapeProduct = async (productKey) => {



    try {



      const prod = products.find((p) => p.key === productKey);



      if (prod?.id) {



        await triggerProductScrape(prod.id, false);



      }



      const raw = await fetchStorefrontInit(false);



      if (raw) {



        const mapped = mapStorefrontData(raw);



        if (mapped?.products) setProducts(mapped.products);



      }



    } catch (err) {



      console.warn('Product scrape error:', err);



    }



  };







  const logOutboundClick = (name) => {



    if (!name) return;



    setAnalytics((prev) =>



      prev.map((item) => {



        if (



          item.name.toLowerCase().includes(name.toLowerCase()) ||



          name.toLowerCase().includes(item.name.toLowerCase())



        ) {



          return { ...item, clicks: item.clicks + 1 };



        }



        return item;



      })



    );



  };







  const handlePublicAdSubmit = async (e) => {



    if (e) e.preventDefault();



    const leadData = {



      brand_name: adFormBrand.trim() || 'Partner Brand Lead',



      contact_phone: adFormPhone.trim() || '+8801XXXXXXXXX',



      selected_tier:



        selectedAdTier === 'billboard'



          ? 'Primary Kinetic Billboard'



          : selectedAdTier === 'spotlight'



          ? 'Product Spotlight Placement'



          : 'Dual Continuous Tickers',



      budget_note: 'Submitted via Storefront Modal'



    };







    try {



      await submitAdvertiserLead(leadData);



    } catch (err) {



      console.warn('API submit advertiser lead error:', err);



    }







    const lead = {



      id: `lead-${Date.now()}`,



      brandName: leadData.brand_name,



      phone: leadData.contact_phone,



      requestedTier: leadData.selected_tier,



      submittedAt: 'Just now',



      status: 'Pending'



    };



    setAdvertiserInbox((prev) => [lead, ...prev]);



    setShowAdModal(false);



    setAdFormBrand('');



    setAdFormPhone('');



    setRedirectToast({



      store: lang === 'bn' ? 'বিজ্ঞাপন স্লট আবেদন সফল' : 'Slot Booking Requested',



      price: selectedAdTier === 'billboard' ? 15000 : selectedAdTier === 'spotlight' ? 7500 : 4000



    });



    setTimeout(() => setRedirectToast(null), 3800);



  };







  // Active billboards & side panels (excluding paused ones)



  const activeBillboards = useMemo(() => {



    const list = billboards.filter((b) => b.isActive !== false);



    return list.length > 0 ? list : billboards;



  }, [billboards]);







  const activeSidePanels = useMemo(() => {



    const list = sidePanels.filter((s) => s.isActive !== false);



    return list.length > 0 ? list : sidePanels;



  }, [sidePanels]);







  // Auto-advance billboard every 5s unless hovered



  useEffect(() => {



    if (isBillboardPaused || activeBillboards.length <= 1) return;



    const timer = setInterval(() => {



      setActiveSlide((prev) => (prev + 1) % activeBillboards.length);



    }, 5000);



    return () => clearInterval(timer);



  }, [isBillboardPaused, activeBillboards.length]);







  const handleMouseMove = (e) => {



    const rect = e.currentTarget.getBoundingClientRect();



    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 18;



    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 12;



    setParallax({ x, y });



  };







  const handleMouseLeave = () => {



    setParallax({ x: 0, y: 0 });



    setIsBillboardPaused(false);



  };







  const executeLiveSearch = async (queryText, categoryFilter = 'all', isBrowse = false) => {



    const q = (queryText || searchQuery || '').trim();



    if (!q) return;







    setSearchQuery(q);



    setActiveSearchQuery(q);



    setIsSearching(true);
    setShowSuggestions(false);
    fetchSearchSuggestions(q).then((data) => {
      if (data && data.did_you_mean && data.did_you_mean.length > 0) {
        setActiveDisambiguationPills(data.did_you_mean);
      } else {
        setActiveDisambiguationPills([]);
      }
    }).catch(() => setActiveDisambiguationPills([]));



    productSectionRef.current?.scrollIntoView({ behavior: 'smooth' });







    try {



      const rawData = await searchLiveProducts(q, categoryFilter, Boolean(isBrowse));



      if (rawData && Array.isArray(rawData) && rawData.length > 0) {



        const mapped = rawData.map(mapProductItem).filter(Boolean);



        setSearchResults(mapped);



      } else {
        setSearchResults([]);
      }



    } catch (err) {



      console.warn('[JaChai Live Search] Error:', err);



    } finally {



      setIsSearching(false);



    }



  };







  const handleResetToHome = () => {
    handleLogoTap();
    setSearchQuery('');
    setActiveSearchQuery('');
    setSearchResults([]);
    setActiveDisambiguationPills([]);
    setShowSuggestions(false);
    setSelectedCategory('all');
    if (typeof setSelectedSubcategory === 'function') {
      setSelectedSubcategory('all');
    }
    setIsSearching(false);
    setExpandedHotProductId(null);
    setSelectedOfferProduct(null);
    if (typeof window !== 'undefined') {
      if (window.location.search) {
        window.history.pushState({}, '', window.location.pathname);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    const query = searchQuery.trim();
    if (query) {
      if (typeof window !== 'undefined' && window.gtag) {
        window.gtag('event', 'search', {
          search_term: query
        });
      }
      setSelectedCategory('all');
      executeLiveSearch(query, 'all');
    }
  };







  const openComparisonModal = (productKeyOrObj) => {



    let target = null;



    if (typeof productKeyOrObj === 'string') {



      target =



        searchResults.find((p) => p.key === productKeyOrObj) ||



        products.find((p) => p.key === productKeyOrObj) ||



        products[0];



    } else {



      target = productKeyOrObj;



    }



    setInspectProduct(target);



  };







  const triggerOutbound = (offer, channel = 'default') => {



    if (offer.id) {



      trackOutboundClick('offer', offer.id);



    }



    const storeName = offer.subStoreEn || offer.subStoreBn || offer.store || 'Verified Merchant';



    logOutboundClick(storeName);







    let destUrl = '';



    let channelLabel = '';







    // Channel selection with intelligent fallbacks



    if (channel === 'website') {



      destUrl = (offer.url && !offer.url.includes('facebook.com') ? offer.url : (offer.websiteUrl || ''));



      channelLabel = lang === 'bn' ? 'ওয়েবসাইট' : 'Website';



    } else if (channel === 'facebook') {



      destUrl = offer.facebookUrl || (offer.url && offer.url.includes('facebook.com') ? offer.url : '');



      channelLabel = lang === 'bn' ? 'ফেসবুক' : 'Facebook';



    } else {



      // Default: prefer website, then facebook, then general offer url



      destUrl = offer.url || offer.websiteUrl || offer.facebookUrl || '';



    }







    // Auto-correct known legacy corruptions and 404 fake slugs
    if (destUrl) {
      if (destUrl.includes('taketalkbd.com')) {
        destUrl = 'https://www.facebook.com/takeNtalkBD';
      }
      if (destUrl.includes('&merchant=')) {
        destUrl = destUrl.split('&merchant=')[0];
      }

      // Auto-heal known 404 fake direct slugs into verified merchant search endpoints
      const lowerDest = destUrl.toLowerCase();
      const isSearchUrl = lowerDest.includes('/search') || lowerDest.includes('catalogsearch') || lowerDest.includes('/catalog/?q=') || lowerDest.includes('?s=');
      if (!isSearchUrl) {
        const queryTerm = searchQuery.trim() || activeSearchQuery.trim() || '';
        if (queryTerm) {
          const encQuery = encodeURIComponent(queryTerm);
          if (lowerDest.includes('startech.com.bd') && (lowerDest.includes('playstation') || lowerDest.includes('ps4') || lowerDest.includes('ps3') || lowerDest.includes('ps2') || lowerDest.includes('xbox') || lowerDest.includes('nintendo') || lowerDest.includes('sega') || lowerDest.includes('anbernic') || lowerDest.includes('miyoo') || lowerDest.includes('vita') || lowerDest.includes('psp'))) {
            destUrl = `https://www.startech.com.bd/product/search?search=${encQuery}`;
          } else if (lowerDest.includes('custommacbd.com') && (lowerDest.includes('playstation') || lowerDest.includes('ps4') || lowerDest.includes('ps3') || lowerDest.includes('ps2') || lowerDest.includes('xbox') || lowerDest.includes('nintendo') || lowerDest.includes('sega') || lowerDest.includes('anbernic') || lowerDest.includes('miyoo') || lowerDest.includes('vita') || lowerDest.includes('psp'))) {
            destUrl = `https://custommacbd.com/search?q=${encQuery}`;
          } else if (lowerDest.includes('ryans.com') && (lowerDest.includes('playstation') || lowerDest.includes('ps4') || lowerDest.includes('xbox') || lowerDest.includes('nintendo') || lowerDest.includes('console'))) {
            destUrl = `https://www.ryans.com/search?q=${encQuery}`;
          } else if (lowerDest.includes('techlandbd.com') && (lowerDest.includes('playstation') || lowerDest.includes('ps4') || lowerDest.includes('xbox') || lowerDest.includes('nintendo') || lowerDest.includes('anbernic'))) {
            destUrl = `https://www.techlandbd.com/index.php?route=product/search&search=${encQuery}`;
          } else if (lowerDest.includes('applegadgetsbd.com') && (lowerDest.includes('psp') || lowerDest.includes('anbernic') || lowerDest.includes('miyoo') || lowerDest.includes('playstation'))) {
            destUrl = `https://www.applegadgetsbd.com/?s=${encQuery}`;
          } else if (lowerDest.includes('pickaboo.com') && (lowerDest.includes('ps3') || lowerDest.includes('anbernic') || lowerDest.includes('playstation') || lowerDest.includes('console'))) {
            destUrl = `https://www.pickaboo.com/search-result/${encQuery}`;
          }
        }
      }
    }







    // Bulletproof zero-broken link fallback:



    // If destUrl is still empty or non-http, build a verified working link



    if (!destUrl || !destUrl.startsWith('http')) {



      if (channel === 'facebook' || offer.store === 'F-COMMERCE' || offer.store === 'FACEBOOK') {



        destUrl = `https://www.facebook.com/search/top/?q=${encodeURIComponent(storeName)}`;



        if (!channelLabel) channelLabel = lang === 'bn' ? 'ফেসবুক' : 'Facebook';



      } else {



        destUrl = `https://www.google.com/search?q=${encodeURIComponent(storeName + ' Bangladesh online store')}`;



        if (!channelLabel) channelLabel = lang === 'bn' ? 'ওয়েবসাইট' : 'Website';



      }



    }







    const storeLabel = lang === 'bn' ? offer.subStoreBn || offer.subStoreEn : offer.subStoreEn;



    setRedirectToast({



      store: channelLabel ? `${storeLabel} · ${channelLabel}` : storeLabel,



      price: offer.price



    });







    if (destUrl && destUrl.startsWith('http')) {



      setTimeout(() => {



        window.open(destUrl, '_blank', 'noopener,noreferrer');



      }, 400);



    }



    setTimeout(() => {



      setRedirectToast(null);



    }, 3400);



  };











  const currentBillboard =



    activeBillboards[activeSlide % activeBillboards.length] || billboards[0];







  // --- RENDER COMMAND CENTER FULL VIEW IF IN ADMIN MODE ---



  if (viewMode === 'admin') {



    return (



      <AdminCommandCenter



        billboards={billboards}



        setBillboards={setBillboards}



        sidePanels={sidePanels}



        setSidePanels={setSidePanels}



        tickers={tickers}



        setTickers={setTickers}



        tickerSpeed={tickerSpeed}



        setTickerSpeed={setTickerSpeed}



        spiders={spiders}



        setSpiders={setSpiders}



        runAllSpiders={runAllSpiders}



        isScraping={isScraping}



        rescrapeProduct={rescrapeProduct}



        products={products}



        setProducts={setProducts}



        analytics={analytics}



        setAnalytics={setAnalytics}



        advertiserInbox={advertiserInbox}



        setAdvertiserInbox={setAdvertiserInbox}



        trendingHubs={trendingHubs}
        hotProducts={hotProducts}
        setHotProducts={setHotProducts}



        setTrendingHubs={setTrendingHubs}



        onClose={() => setViewMode('storefront')}



        onLogout={handleLogout}



        formatBDT={formatBDT}



        toBengaliDigits={toBengaliDigits}



      />



    );



  }







    const renderHotProductIcon = (iconName) => {
    switch (iconName) {
      case 'Smartphone':
        return <Smartphone className="w-5 h-5 text-sky-600 dark:text-sky-400" />;
      case 'Sparkles':
        return <Sparkles className="w-5 h-5 text-amber-500" />;
      case 'Fuel':
        return <Fuel className="w-5 h-5 text-rose-500" />;
      case 'Cpu':
        return <Cpu className="w-5 h-5 text-emerald-500" />;
      case 'HardDrive':
        return <HardDrive className="w-5 h-5 text-blue-500" />;
      case 'Zap':
        return <Zap className="w-5 h-5 text-purple-500" />;
      default:
        return <Cpu className="w-5 h-5 text-teal-500" />;
    }
  };

const renderHubIcon = (iconName) => {



    switch (iconName) {



      case 'Smartphone':



        return <Smartphone className="w-5 h-5 text-[#38BDF8]" />;



      case 'Shirt':



        return <Shirt className="w-5 h-5 text-[#FB923C]" />;



      case 'Sparkles':



        return <Sparkles className="w-5 h-5 text-[#F59E0B]" />;



      case 'Headphones':



        return <Headphones className="w-5 h-5 text-[#A855F7]" />;



      case 'Watch':



        return <Watch className="w-5 h-5 text-[#14B8A6]" />;



      case 'Laptop':



        return <Laptop className="w-5 h-5 text-[#38BDF8]" />;



      default:



        return <Compass className="w-5 h-5 text-[#14B8A6]" />;



    }



  };







  return (



    <div className="min-h-screen bg-[#F5F7FA] text-[#334155] antialiased selection:bg-[#14B8A6] selection:text-white font-sans-clean overflow-x-hidden">



      



      {/* =====================================================================



          AUTHENTICATED ADMIN PREVIEW BAR (ONLY VISIBLE WHEN LOGGED IN)



      ===================================================================== */}



      {isAdminAuthenticated && (



        <div className="bg-[#101B2D] border-b border-[#14B8A6]/30 px-4 sm:px-8 py-2 flex items-center justify-between text-xs text-white z-50 sticky top-0 shadow-lg">



          <div className="flex items-center gap-2">



            <Shield className="w-4 h-4 text-[#F59E0B]" />



            <span className="font-bold text-[#14B8A6]">Admin Vault Unlocked</span>



            <span className="text-white/40 hidden sm:inline">· Storefront Live Preview Mode</span>



          </div>



          <div className="flex items-center gap-2">



            <button



              onClick={() => setViewMode('admin')}



              className="px-3 py-1 rounded-lg bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-[11px] uppercase transition cursor-pointer shadow-md"



            >



              Return to Command Center



            </button>



            <button



              onClick={handleLogout}



              className="px-3 py-1 rounded-lg bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 text-red-300 font-bold text-[11px] uppercase transition cursor-pointer"



            >



              Lock Vault



            </button>



          </div>



        </div>



      )}







      {/* =====================================================================



          LESSON 2: TOP SLOW-GLIDING MARQUEE TICKER (DYNAMIC SPEED)



      ===================================================================== */}



      <div className="w-full bg-[#101B2D] border-b border-[#DDE3EA]/20 py-2 overflow-hidden select-none z-50 relative">



        <div



          className="animate-marquee"



          style={{ animationDuration: `${tickerSpeed}s` }}



        >



          {[...tickers, ...tickers, ...tickers].map((item, idx) => (



            <button



              key={`top-ticker-${idx}`}



              onClick={() => openComparisonModal(item.targetKey)}



              className="flex items-center gap-2.5 px-7 text-[11px] sm:text-xs font-semibold text-slate-300 hover:text-white transition cursor-pointer whitespace-nowrap"



            >



              <span className="w-1.5 h-1.5 rounded-full bg-[#14B8A6] shrink-0" />



              <span className="font-extrabold text-[#FFC857] tracking-wide">



                {lang === 'bn' ? item.brandBn : item.brandEn}:



              </span>



              <span className="text-white/80">



                {lang === 'bn' ? item.textBn : item.textEn}



              </span>



              <span className="text-white/20 pl-3">·</span>



            </button>



          ))}



        </div>



      </div>







      {/* =====================================================================



          LESSON 3: HEADER WITH TOP-LEFT LOGO/MOTTO & RIGHT CONTROLS



      ===================================================================== */}



      <header className="sticky top-0 z-40 bg-[#101B2D]/95 backdrop-blur-md border-b border-[#DDE3EA]/20">



        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3.5 flex items-center justify-between gap-4">



          



          {/* Top-Left Corner: Custom 'যা চাই' Logo, Comparison Emblem & Motto */}



          <div className="flex flex-col items-start">



            <JaChaiLogo
              onTap={handleResetToHome}
              showMotto={true}



            />



            <p className="text-[11px] font-medium text-slate-400 tracking-wide mt-1">



              {lang === 'bn'



                ? 'Bangladeshi Price Index — আপনার পরবর্তী কেনাকাটার সেরা দাম'



                : 'The Best Price for Your Next Purchase'}



            </p>



          </div>







          {/* Right Corner: Clean 'Advertise' Button & Language Toggle */}



          <div className="flex items-center gap-2 sm:gap-3 shrink-0">



            <button



              onClick={() => setShowAdModal(true)}



              className="px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-full bg-white/10 hover:bg-white/15 border border-white/15 text-xs font-bold text-white flex items-center gap-1.5 transition cursor-pointer"



            >



              <Megaphone className="w-3.5 h-3.5 text-[#FFC857]" />



              <span className="hidden sm:inline">



                {lang === 'bn' ? 'বিজ্ঞাপন দিন' : 'Advertise'}



              </span>



              <span className="sm:hidden text-[11px]">



                {lang === 'bn' ? 'বিজ্ঞাপন' : 'Ads'}



              </span>



            </button>







            <button



              onClick={() => setLang(lang === 'en' ? 'bn' : 'en')}



              className="px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-full bg-white/15 hover:bg-white/25 text-white text-xs font-extrabold uppercase tracking-wider transition cursor-pointer"



            >



              {lang === 'en' ? 'বাংলা' : 'EN'}



            </button>



          </div>



        </div>







        {/* =====================================================================



            LESSON 3: BIG ATTRACTION HIGH-CONTRAST WHITE SEARCH BAR



        ===================================================================== */}



        <div className="w-full bg-[#101B2D] border-t border-[#DDE3EA]/20 py-3.5 sm:py-4 px-4 sm:px-8">



          <form onSubmit={handleSearchSubmit} className="max-w-2xl w-full mx-auto relative"



          >



            <div className="relative flex items-center bg-white text-[#101B2D] rounded-full p-1.5 pl-4 sm:pl-5 shadow-2xl border border-[#DDE3EA] focus-within:border-[#14B8A6] focus-within:ring-2 focus-within:ring-[#14B8A6]/20 transition-all">



              <Search className="w-4 h-4 sm:w-5 sm:h-5 text-stone-400 shrink-0 mr-2 sm:mr-3" />



              <input type="text" autoComplete="off" autoCorrect="off" autoCapitalize="off" spellCheck={false} value={searchQuery}



                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => {
                  if ((suggestionsData.suggestions?.length > 0 || suggestionsData.did_you_mean?.length > 0) && searchQuery.trim().length >= 2) {
                    setShowSuggestions(true);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setHighlightedIndex((prev) => Math.min(prev + 1, (suggestionsData.suggestions?.length || 0) - 1));
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setHighlightedIndex((prev) => Math.max(prev - 1, -1));
                  } else if (e.key === 'Escape') {
                    setShowSuggestions(false);
                  } else if (e.key === 'Enter') {
                    if (highlightedIndex >= 0 && suggestionsData.suggestions && suggestionsData.suggestions[highlightedIndex]) {
                      e.preventDefault();
                      const item = suggestionsData.suggestions[highlightedIndex];
                      handleSelectSuggestion(item.title, item.category_id || 'all');
                    }
                  }
                }}



                placeholder={



                  lang === 'bn'



                    ? 'যা চাই তাই খুঁজুন: আইফোন, ল্যাপটপ, ওয়াচ, স্কিনকেয়ার, অ্যাপ্লায়েন্স...'
                    : 'Search iPhone, laptops, watches, skincare, appliances...'



                }



                className="w-full py-1.5 sm:py-2 bg-transparent text-xs sm:text-sm font-semibold text-stone-900 placeholder:text-stone-400 focus:outline-none"



              />



              {searchQuery && (



                <button



                  type="button"



                  onClick={() => setSearchQuery('')}



                  className="p-1.5 text-stone-400 hover:text-stone-700 cursor-pointer mr-1"



                  aria-label="Clear search"



                >



                  <X className="w-4 h-4" />



                </button>



              )}



              <button



                type="submit"



                className="px-5 sm:px-6 py-2.5 rounded-full bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs sm:text-sm uppercase tracking-wider transition cursor-pointer shrink-0 shadow-md flex items-center gap-1.5"



              >



                <span>{lang === 'bn' ? 'যাচাই করুন' : 'Compare'}</span>



                <ArrowUpRight className="w-3.5 h-3.5" />



              </button>



            </div>

            {/* As-You-Type Suggestions Floating Dropdown - 100% Solid Opaque */}
            {showSuggestions && suggestionsData.suggestions?.length > 0 && (
              <div
                ref={suggestionsRef}
                className="absolute left-0 right-0 top-full mt-2 bg-white border border-slate-200/90 rounded-2xl shadow-2xl overflow-hidden z-[9999] text-left py-1 text-slate-900 ring-1 ring-black/5"
                style={{ backgroundColor: '#ffffff', opacity: 1 }}
              >
                <div className="py-1 divide-y divide-slate-100">
                  {suggestionsData.suggestions.map((item, idx) => {
                    const isHighlighted = highlightedIndex === idx;
                    return (
                      <button
                        key={idx}
                        type="button"
                        onMouseEnter={() => setHighlightedIndex(idx)}
                        onMouseDown={(e) => {
                          e.preventDefault();
                          handleSelectSuggestion(item.title, item.category_id || 'all');
                        }}
                        onClick={(e) => {
                          e.preventDefault();
                          handleSelectSuggestion(item.title, item.category_id || 'all');
                        }}
                        className={`w-full px-5 py-3 flex items-center justify-between transition cursor-pointer text-left ${
                          isHighlighted ? 'bg-teal-50 text-teal-900 font-semibold border-l-4 border-teal-600 pl-4' : 'text-slate-800 hover:bg-slate-50 font-medium'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0 pr-3">
                          <Search className={`w-4 h-4 shrink-0 transition-colors ${isHighlighted ? 'text-teal-600' : 'text-slate-400'}`} />
                          <span className="text-sm font-semibold truncate tracking-tight">{item.title}</span>
                        </div>
                        <ArrowUpRight className={`w-3.5 h-3.5 shrink-0 transition-colors ${isHighlighted ? 'text-teal-600' : 'text-slate-400'}`} />
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </form>

          {/* Disambiguation Suggestion Pills */}
          {activeDisambiguationPills && activeDisambiguationPills.length > 0 && (
            <div className="flex items-center justify-center gap-2 mt-3 flex-wrap">
              <span className="text-xs font-semibold text-slate-500">
                {lang === 'bn' ? 'সম্ভাব্য ফলাফল:' : 'Did you mean:'}
              </span>
              {activeDisambiguationPills.map((pill, pIdx) => {
                const text = typeof pill === 'string' ? pill : (pill.text || pill.title || '');
                const cat = (typeof pill === 'object' && pill.category_id) ? pill.category_id : 'all';
                return (
                  <button
                    key={pIdx}
                    type="button"
                    onClick={() => handleSelectSuggestion(text, cat)}
                    className="px-3 py-1 rounded-full text-xs font-bold bg-white text-teal-800 border border-teal-200 shadow-xs hover:bg-teal-50 transition cursor-pointer flex items-center gap-1"
                  >
                    <span>{text}</span>
                    <ArrowUpRight className="w-3 h-3 text-teal-600" />
                  </button>
                );
              })}
            </div>
          )}

          {/* Category Navigation Bar: Valorant Kinetic Fluid Motion */}



          <motion.div



            layoutRoot



            className="w-full max-w-5xl mx-auto mt-3 px-2 sm:px-4 flex flex-col items-center"



          >



            {/* Persistent Control Bar: Clean horizontal row, silky smooth easing without bubble pop */}



            <motion.div



              layout



              transition={{



                duration: 0.38,



                ease: [0.25, 0.1, 0.25, 1.0],



              }}



              className="flex flex-row items-center justify-center gap-2.5 sm:gap-3 transition-colors duration-300"



            >



              {/* 1. All Types Button */}



              <button



                type="button"



                onClick={() => {



                  setSelectedCategory('all');



                  handleResetToHome();



                }}



                className={`px-4 sm:px-5 py-2 rounded-full text-xs font-bold transition-colors duration-200 cursor-pointer flex items-center gap-1.5 shadow-sm ${



                  selectedCategory === 'all'



                    ? 'bg-[#14B8A6] text-white font-extrabold shadow-md shadow-[#14B8A6]/20'



                    : 'bg-white/10 text-white/90 hover:text-white hover:bg-white/15 border border-white/15'



                }`}



              >



                <Compass className={`w-3.5 h-3.5 ${selectedCategory === 'all' ? 'text-white' : 'text-[#14B8A6]'}`} />



                <span>{lang === 'bn' ? 'সকল আইটেম' : 'All Types'}</span>



              </button>







              {/* 2. Categories Button with Smoothly Rotating Indicator */}



              <button



                type="button"



                onClick={() => setIsCategoriesExpanded((prev) => !prev)}



                className={`px-4 sm:px-5 py-2 rounded-full text-xs font-bold transition-colors duration-200 cursor-pointer flex items-center gap-2 shadow-sm ${



                  isCategoriesExpanded



                    ? 'bg-[#14B8A6]/20 border border-[#14B8A6] text-white shadow-lg shadow-[#14B8A6]/20'



                    : selectedCategory !== 'all'



                    ? 'bg-[#14B8A6]/15 text-[#14B8A6] border border-[#14B8A6]/60 shadow-md shadow-[#14B8A6]/10'



                    : 'bg-white/10 text-white/90 hover:text-white hover:bg-white/15 border border-white/15'



                }`}



              >



                <LayoutGrid className="w-3.5 h-3.5 text-[#14B8A6]" />



                <span>



                  {selectedCategory !== 'all'



                    ? (lang === 'bn' ? `ক্যাটাগরি: ${categoriesList.find((c) => c.id === selectedCategory)?.bn || 'বাছাইকৃত'}` : `Category: ${categoriesList.find((c) => c.id === selectedCategory)?.en || 'Selected'}`)



                    : (lang === 'bn' ? 'ক্যাটাগরি সমূহ' : 'Categories')}



                </span>



                <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold border ${



                  isCategoriesExpanded



                    ? 'bg-[#14B8A6] text-white border-[#14B8A6]'



                    : 'bg-white/10 text-white/70 border-white/10'



                }`}>



                  ({categoriesList.length - 1})



                </span>



                <motion.div



                  animate={{ rotate: isCategoriesExpanded ? 180 : 0 }}



                  transition={{ duration: 0.32, ease: [0.25, 0.1, 0.25, 1.0] }}



                  className="flex items-center justify-center"



                >



                  <ChevronDown className={`w-3.5 h-3.5 ${isCategoriesExpanded ? 'text-[#14B8A6]' : 'text-white/60'}`} />



                </motion.div>



              </button>

              {/* 3. National Store Leaderboard Golden Button */}
              <button
                type="button"
                onClick={() => setIsLeaderboardOpen(true)}
                className="px-4 sm:px-5 py-2 rounded-full text-xs font-bold transition-all duration-300 flex items-center gap-2 cursor-pointer bg-gradient-to-r from-[#FFC857]/20 via-[#FFC857]/30 to-[#F59E0B]/20 text-[#FFC857] hover:text-[#0A0D14] hover:bg-[#FFC857] border border-[#FFC857]/70 hover:border-[#FFC857] shadow-lg shadow-[#FFC857]/15 hover:shadow-[#FFC857]/30 hover:scale-[1.03] active:scale-[0.98]"
                title={lang === 'bn' ? 'মার্চেন্ট ট্রাস্ট ও ভ্যালু লিডারবোর্ড' : 'Merchant Trust & Value Leaderboard'}
              >
                <Award className="w-3.5 h-3.5 text-[#FFC857]" />
                <span>{lang === 'bn' ? 'শপ লিডারবোর্ড' : 'Store Leaderboard'}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[#FFC857] animate-pulse" />
              </button>



            </motion.div>







            {/* Sub-Categories Drawer: Calmed Transitional Accordion Dropdown */}



            <AnimatePresence>



              {isCategoriesExpanded && (



                <motion.div



                  key="subcat-tray-drawer"



                  initial={{ opacity: 0, height: 0 }}



                  animate={{ opacity: 1, height: 'auto' }}



                  exit={{ opacity: 0, height: 0 }}



                  transition={{



                    duration: 0.35,



                    ease: [0.25, 0.1, 0.25, 1.0],



                  }}



                  className="w-full overflow-hidden"



                >



                  <motion.div



                    variants={{



                      hidden: { opacity: 0 },



                      show: {



                        opacity: 1,



                        transition: {



                          staggerChildren: 0.015,



                          delayChildren: 0.03,



                        },



                      },



                    }}



                    initial="hidden"



                    animate="show"



                    className="w-full mt-2 p-3 sm:p-4 rounded-2xl bg-[#101B2D]/95 backdrop-blur-xl border border-white/20 shadow-2xl flex flex-wrap items-center justify-center gap-1.5 sm:gap-2"



                  >



                    {categoriesList



                      .filter((tab) => tab.id !== 'all')



                      .map((tab) => {



                        const isTabActive = selectedCategory === tab.id;



                        return (



                          <motion.button



                            key={tab.id}



                            variants={{



                              hidden: { opacity: 0, y: 3 },



                              show: {



                                opacity: 1,



                                y: 0,



                                transition: { duration: 0.24, ease: [0.25, 0.1, 0.25, 1.0] },



                              },



                            }}



                            type="button"



                            onClick={() => {



                              setSelectedCategory(tab.id);



                              setIsCategoriesExpanded(false);



                              const categoryName = lang === 'bn' ? (tab.bn || tab.en) : (tab.en || tab.bn);
                              executeLiveSearch(categoryName, tab.id, true);



                            }}



                            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide transition-colors duration-200 cursor-pointer flex items-center shrink-0 shadow-sm ${



                              isTabActive



                                ? 'bg-[#14B8A6] text-white font-extrabold shadow-md'



                                : 'bg-white/10 text-white/80 hover:text-white hover:bg-white/20 hover:border-[#14B8A6]/50 border border-white/10'



                            }`}



                          >



                            <span>{lang === 'bn' ? tab.bn : tab.en}</span>



                          </motion.button>



                        );



                      })}



                  </motion.div>



                </motion.div>



              )}



            </AnimatePresence>



          </motion.div>



        </div>



      </header>







      {/* =====================================================================



          LESSON 4: IMMEDIATE ABOVE-THE-FOLD ONLINE BILLBOARD STAGE (ZERO SCROLL)



          Visible only in Default Home Discovery Mode (hidden during live search)



      ===================================================================== */}



      {activeSearchQuery === '' && !isSearching && (



        <section className="max-w-7xl mx-auto px-4 sm:px-8 pt-3 sm:pt-4 pb-6">



          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-5 items-stretch">



          



          {/* Main Billboard (8 columns on desktop, full-width on mobile) */}



          <div



            onMouseEnter={() => setIsBillboardPaused(true)}



            onMouseMove={handleMouseMove}



            onMouseLeave={handleMouseLeave}



            className="lg:col-span-8 relative rounded-2xl overflow-hidden bg-[#12141C] border border-white/15 min-h-[340px] sm:min-h-[380px] p-5 sm:p-7 flex flex-col justify-between select-none shadow-2xl group"



          >



            {/* Smooth Kinetic Parallax Photography with Enhanced Billboard Visibility */}



            <div className="absolute inset-0 overflow-hidden pointer-events-none">



              <img



                key={currentBillboard.id}



                src={getImageProxyUrl(currentBillboard.image)}



                onError={(e) => {



                  if (LOCAL_FALLBACKS[currentBillboard.productKey]) {



                    e.currentTarget.onerror = null;



                    e.currentTarget.src = LOCAL_FALLBACKS[currentBillboard.productKey];



                  }



                }}



                alt={currentBillboard.brandEn}



                style={{



                  transform: `scale(1.07) translate3d(${parallax.x * -0.6}px, ${



                    parallax.y * -0.6



                  }px, 0)`



                }}



                className="w-full h-full object-cover object-center opacity-90 group-hover:opacity-100 transition-all duration-700 ease-out filter brightness-105"



              />



              {/* Softer, directional vignette to guarantee banner clarity while preserving typography legibility */}



              <div className="absolute inset-0 bg-gradient-to-r from-[#101B2D]/85 via-[#101B2D]/30 to-transparent pointer-events-none" />



              <div className="absolute inset-0 bg-gradient-to-t from-[#101B2D]/70 via-transparent to-transparent pointer-events-none" />



            </div>







            {/* Top Row: SPONSORED Tag & Slide Controls */}



            <div className="relative z-10 flex items-center justify-between">



              <span className="text-[10px] sm:text-[11px] font-black tracking-[0.24em] uppercase text-[#F59E0B]">



                {lang === 'bn' ? currentBillboard.tagBn : currentBillboard.tagEn}



              </span>







              <div className="flex items-center gap-1.5">



                <button



                  onClick={() =>



                    setActiveSlide(



                      (prev) =>



                        (prev - 1 + activeBillboards.length) %



                        activeBillboards.length



                    )



                  }



                  className="w-8 h-8 rounded-full bg-black/60 hover:bg-white hover:text-black border border-white/20 flex items-center justify-center transition cursor-pointer text-white"



                  aria-label="Previous Slide"



                >



                  <ChevronLeft className="w-4 h-4" />



                </button>



                <button



                  onClick={() =>



                    setActiveSlide(



                      (prev) => (prev + 1) % activeBillboards.length



                    )



                  }



                  className="w-8 h-8 rounded-full bg-black/60 hover:bg-white hover:text-black border border-white/20 flex items-center justify-center transition cursor-pointer text-white"



                  aria-label="Next Slide"



                >



                  <ChevronRight className="w-4 h-4" />



                </button>



              </div>



            </div>







            {/* Center Nike / Valorant Bold Typography & Pricing */}



            <div



              style={{



                transform: `translate3d(${parallax.x * 0.3}px, ${



                  parallax.y * 0.3



                }px, 0)`



              }}



              className="relative z-10 my-auto max-w-xl transition-transform duration-500 ease-out drop-shadow-[0_2px_10px_rgba(0,0,0,0.85)]"



            >



              <span className="text-[11px] font-bold uppercase tracking-widest text-white/50 block mb-1">



                {lang === 'bn' ? currentBillboard.brandBn : currentBillboard.brandEn}



              </span>







              {lang === 'bn' ? (



                <h2



                  onClick={() => (currentBillboard.startingPrice === 0 || (currentBillboard.headlineBoldEn || '').includes('GOES HERE')) ? (setSelectedAdTier('billboard'), setShowAdModal(true)) : openComparisonModal(currentBillboard.productKey)}



                  className="font-display text-2xl sm:text-4xl font-bold text-white leading-tight cursor-pointer hover:text-[#14B8A6] transition-colors"



                >



                  {currentBillboard.headlineBn}



                </h2>



              ) : (



                <h2



                  onClick={() => (currentBillboard.startingPrice === 0 || (currentBillboard.headlineBoldEn || '').includes('GOES HERE')) ? (setSelectedAdTier('billboard'), setShowAdModal(true)) : openComparisonModal(currentBillboard.productKey)}



                  className="text-3xl sm:text-5xl tracking-tight text-white leading-none cursor-pointer"



                >



                  <span className="font-light text-white/80 mr-2">



                    {currentBillboard.headlineLightEn}



                  </span>



                  <span className="font-display font-bold uppercase italic text-white">



                    {currentBillboard.headlineBoldEn}



                  </span>



                </h2>



              )}







              <p className="text-xs sm:text-sm text-white/70 font-medium mt-2 max-w-lg">



                {lang === 'bn' ? currentBillboard.subtextBn : currentBillboard.subtextEn}



              </p>







              {/* Action Row: Emerald Starting Price & Direct Store Trigger */}



              <div className="mt-4 flex flex-wrap items-center gap-3">
                {currentBillboard.startingPrice === 0 || (currentBillboard.headlineBoldEn || '').includes('GOES HERE') ? (
                  <>
                    <button
                      onClick={() => {
                        setSelectedAdTier('billboard');
                        setShowAdModal(true);
                      }}
                      className="px-5 py-2.5 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs uppercase tracking-wider shadow-lg transition cursor-pointer flex items-center gap-2"
                    >
                      <span>{lang === 'bn' ? 'বিজ্ঞাপন দিন' : 'Advertise with Us'}</span>
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                    <div className="px-3.5 py-2 rounded-xl bg-black/70 border border-white/15 backdrop-blur-md flex items-baseline gap-2 shadow-lg">
                      <span className="text-xs text-[#10E599] font-bold">
                        {lang === 'bn' ? 'স্লট বুকিং উন্মুক্ত' : 'Slot Available · Reserve Now'}
                      </span>
                    </div>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        openComparisonModal(currentBillboard.productKey);
                        if (currentBillboard?.id) trackOutboundClick('billboard', currentBillboard.id);
                      }}
                      className="px-5 py-2.5 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs uppercase tracking-wider shadow-lg transition cursor-pointer flex items-center gap-2"
                    >
                      <span>{lang === 'bn' ? 'সব শপের দাম দেখুন' : 'Compare Offers'}</span>
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                    <div className="px-3.5 py-2 rounded-xl bg-black/70 border border-white/15 backdrop-blur-md flex items-baseline gap-2 shadow-lg">
                      <span className="text-xs text-white/70 font-medium">
                        {lang === 'bn' ? 'শুরু:' : 'From'}
                      </span>
                      <span className="text-base sm:text-lg font-black text-[#10E599] drop-shadow-[0_0_8px_rgba(16,229,153,0.6)]">
                        {formatBDT(currentBillboard.startingPrice, lang)}
                      </span>
                      <span className="text-xs text-white/50 line-through">
                        {formatBDT(currentBillboard.originalPrice, lang)}
                      </span>
                    </div>
                  </>
                )}
              </div>



            </div>







            {/* Bottom Slide Progress Indicators */}



            <div className="relative z-10 flex items-center justify-between pt-2 border-t border-white/10 text-[11px] text-white/50">



              <div className="flex items-center gap-1.5">



                {activeBillboards.map((s, idx) => (



                  <button



                    key={s.id}



                    onClick={() => setActiveSlide(idx)}



                    className={`h-1.5 rounded-full transition-all cursor-pointer ${



                      idx === activeSlide ? 'w-6 bg-[#F59E0B]' : 'w-2 bg-white/20'



                    }`}



                    aria-label={`Billboard Slide ${idx + 1}`}



                  />



                ))}



              </div>







              <button



                onClick={() => setShowAdModal(true)}



                className="text-[#F59E0B] hover:text-white font-bold text-[11px] tracking-wide transition cursor-pointer"



              >



                {lang === 'bn' ? '+ বিলবোর্ড বুকিং' : '+ Book Billboard Slot'}



              </button>



            </div>



          </div>







          {/* 3 Side Panels (4 columns on desktop, below main billboard on mobile) */}



          <div className="lg:col-span-4 flex flex-col sm:grid sm:grid-cols-3 lg:flex lg:flex-col gap-3 justify-between">



            {activeSidePanels.map((slot) => (



              <div



                key={slot.id}



                onClick={() => {



                  openComparisonModal(slot.productKey);



                  if (slot?.id) trackOutboundClick('spotlight', slot.id);



                }}



                className="flex-1 min-h-[105px] lg:min-h-[115px] bg-[#12141C] border border-white/10 hover:border-[#38BDF8]/50 hover:bg-[#161924] rounded-2xl p-3 sm:p-3.5 transition-all duration-300 cursor-pointer flex items-center justify-between gap-3 shadow-xl group/slot relative overflow-hidden"



              >



                <div className="flex-1 min-w-0 z-10">



                  <div className="flex items-center gap-2 mb-1">



                    <span className="text-[9px] font-black tracking-wider uppercase px-2 py-0.5 rounded bg-[#C2410C] text-white">



                      {slot.slotBadge}



                    </span>



                    <span className="text-[10px] font-bold text-white/50 truncate uppercase tracking-wider">



                      {lang === 'bn' ? slot.brandBn : slot.brandEn}



                    </span>



                  </div>







                  <h4 className="font-display text-xs sm:text-sm lg:text-[13px] font-bold text-white group-hover/slot:text-[#38BDF8] transition-colors truncate uppercase leading-tight">



                    {lang === 'bn' ? slot.titleBn : slot.titleEn}



                  </h4>







                  <div className="flex items-baseline gap-1.5 mt-1.5">



                    <span className="text-xs sm:text-sm font-extrabold text-[#FFC857]">



                      {formatBDT(slot.price, lang)}



                    </span>



                    <span className="text-[10px] text-white/40 line-through">



                      {formatBDT(slot.originalPrice, lang)}



                    </span>



                    <span className="text-[10px] font-semibold text-white/60 truncate">



                      · {lang === 'bn' ? slot.perkBn : slot.perkEn}



                    </span>



                  </div>



                </div>







                <div className="relative w-14 h-14 sm:w-16 sm:h-16 lg:w-16 lg:h-16 rounded-xl overflow-hidden bg-black/50 border border-white/10 shrink-0">



                  <img



                    src={getImageProxyUrl(slot.image)}



                    alt={slot.titleEn}



                    className="w-full h-full object-cover group-hover/slot:scale-108 transition-transform duration-500"



                  />



                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none" />



                </div>



              </div>



            ))}



          </div>







        </div>



      </section>



      )}







      {/* =====================================================================



          LESSON 5: SEARCH-PORTAL DISCOVERY OR LIVE PRICE COMPARISON RESULTS



      ===================================================================== */}



      <section



        ref={productSectionRef}



        className="max-w-7xl mx-auto px-4 sm:px-8 pt-4 pb-16"



      >



        {activeSearchQuery !== '' || isSearching ? (



          /* =================================================================



             MODE A: LIVE SEARCH & PRICE COMPARISON RESULTS VIEW



          ================================================================= */



          <div>



            {/* Top Return & Status Bar */}



            <div className="flex flex-wrap items-center justify-between gap-3 mb-6 border-b border-[#DDE3EA] pb-4">



              <div className="flex items-center gap-3">



                <button



                  type="button"



                  onClick={handleResetToHome}



                  className="px-3.5 py-1.5 rounded-full bg-white border border-[#DDE3EA] hover:bg-[#101B2D] hover:text-white text-[#101B2D] text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-sm"



                >



                  <ArrowLeft className="w-3.5 h-3.5" />



                  <span>{lang === 'bn' ? 'হোমে ফিরে যান' : 'Back to Home Billboards'}</span>



                </button>



                <div>



                  <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#0F766E] block">



                    {lang === 'bn' ? 'লাইভ সার্চ ফলাফল' : 'LIVE SEARCH RESULTS'}



                  </span>



                  <h2 className="font-display text-xl sm:text-2xl font-bold uppercase text-[#101B2D] tracking-tight">



                    {lang === 'bn' ? `"${activeSearchQuery}" এর সেরা বাজার দর` : `BEST PRICES FOR "${activeSearchQuery}"`}



                  </h2>



                </div>



              </div>







              {!isSearching && (



                <span className="text-xs font-semibold text-[#166534] bg-[#DCFCE7] px-3 py-1 rounded-full border border-[#166534]/20">



                  {lang === 'bn'



                    ? `${toBengaliDigits(searchResults.length)}টি পণ্য যাচাইকৃত`



                    : `${searchResults.length} Verified Items`}



                </span>



              )}



            </div>







            

            {/* Disambiguation Pill Banner across all query states */}
            {activeDisambiguationPills && activeDisambiguationPills.length > 0 && (
              <div className="w-full mt-2 mb-4 p-3 rounded-2xl bg-teal-50/90 border border-teal-200/90 flex items-center justify-between flex-wrap gap-2.5 shadow-xs">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-bold text-teal-900 flex items-center gap-1">
                    <span>💡</span> {lang === 'bn' ? 'সম্ভাব্য সঠিক মডেল বা ব্র্যান্ড:' : 'Did you mean:'}
                  </span>
                  {activeDisambiguationPills.map((pill, pIdx) => {
                    const text = typeof pill === 'string' ? pill : (pill.text || pill.title || '');
                    const cat = (typeof pill === 'object' && pill.category_id) ? pill.category_id : 'all';
                    return (
                      <button
                        key={pIdx}
                        type="button"
                        onClick={() => handleSelectSuggestion(text, cat)}
                        className="px-3 py-1 rounded-full text-xs font-bold bg-white text-teal-800 border border-teal-300 shadow-xs hover:bg-teal-100 transition cursor-pointer flex items-center gap-1.5"
                      >
                        <span>{text}</span>
                        <ArrowUpRight className="w-3.5 h-3.5 text-teal-600" />
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
            {/* Kinetic Scanning State */}



            {isSearching ? (
              <div className="bg-[#FFFFFF] border border-[#DDE3EA] rounded-3xl p-10 sm:p-14 text-center max-w-2xl mx-auto my-8 shadow-xl relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#14B8A6]/5 to-transparent animate-pulse pointer-events-none" />
                <div className="relative z-10 flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-[#14B8A6]/15 border-2 border-[#14B8A6] flex items-center justify-center mb-4 relative">
                    <Loader2 className="w-8 h-8 text-[#14B8A6] animate-spin" />
                    <span className="absolute inset-0 rounded-full border border-[#14B8A6]/40 animate-ping" />
                  </div>
                  <h3 className="font-display text-lg sm:text-xl font-bold text-[#101B2D] mb-2">
                    {lang === 'bn'
                      ? `'${activeSearchQuery}'-এর লাইভ রেট স্ক্যান করা হচ্ছে...`
                      : `Scanning Bangladeshi stores & extracting live prices for '${activeSearchQuery}'...`}
                  </h3>
                  <p className="text-xs sm:text-sm text-[#475569] max-w-md mx-auto">
                    {lang === 'bn'
                      ? 'ভেরিফাইড বাংলাদেশি বিক্রেতাদের লাইভ প্রাইস, ওয়ারেন্টি ও স্টক স্ট্যাটাস যাচাই করা হচ্ছে...'
                      : 'Comparing authentic retailers across Bangladesh and verifying real-time stock & pricing in seconds.'}
                  </p>
                </div>
              </div>
            ) : searchResults.length === 0 ? (



              <div className="bg-[#FFFFFF] border border-[#DDE3EA] rounded-2xl p-10 text-center max-w-md mx-auto my-8 shadow-sm">



                <p className="text-xs sm:text-sm text-[#334155] mb-3">



                  {lang === 'bn'



                    ? `"${activeSearchQuery}" নামে কোনো পণ্য পাওয়া যায়নি।`



                    : `No products matched "${activeSearchQuery}".`}



                </p>

                <div className="mb-4 p-3 rounded-xl bg-slate-50 border border-slate-200 text-[11px] sm:text-xs text-[#64748B] leading-relaxed text-left sm:text-center">
                  <span className="font-semibold text-slate-700">💡 {lang === 'bn' ? 'জেনে রাখুন:' : 'Note:'}</span>{' '}
                  {lang === 'bn'
                    ? 'আপনার কাঙ্ক্ষিত পণ্যটি না পেলে তা হয়তো স্টকে নেই, অথবা ১ বছরের বেশি পুরনো হওয়ায় অপ্রাসঙ্গিক ও বিভ্রান্তিকর দাম পরিহার করতে ফিল্টার করা হয়েছে।'
                    : "If you don't get your desired search result, the product might be currently out of stock or listings over 1 year old were excluded to ensure accurate, up-to-date pricing."}
                </div>

                {activeDisambiguationPills && activeDisambiguationPills.length > 0 && (
                  <div className="mb-5 p-4 rounded-xl bg-teal-50 border border-teal-200">
                    <p className="text-xs font-semibold text-teal-900 mb-2.5">
                      {lang === 'bn' ? 'সম্ভাব্য সঠিক মডেল বা ব্র্যান্ড:' : 'Did you mean one of these available models?'}
                    </p>
                    <div className="flex items-center justify-center gap-2 flex-wrap">
                      {activeDisambiguationPills.map((pill, pIdx) => {
                        const text = typeof pill === 'string' ? pill : (pill.text || pill.title || '');
                        const cat = (typeof pill === 'object' && pill.category_id) ? pill.category_id : 'all';
                        return (
                          <button
                            key={pIdx}
                            type="button"
                            onClick={() => handleSelectSuggestion(text, cat)}
                            className="px-3.5 py-1.5 rounded-full text-xs font-bold bg-white text-teal-800 border border-teal-300 shadow-sm hover:bg-teal-100 transition cursor-pointer flex items-center gap-1.5"
                          >
                            <span>{text}</span>
                            <ArrowUpRight className="w-3.5 h-3.5 text-teal-600" />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                <button



                  type="button"



                  onClick={handleResetToHome}



                  className="px-4 py-2 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs uppercase cursor-pointer transition shadow-md"



                >



                  {lang === 'bn' ? '← হোমে ফিরে যান' : '← Back to Home Portal'}



                </button>



              </div>



            ) : (



              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">



                {searchResults.map((product) => (



                  <div



                    key={product.key}



                    onClick={() => openComparisonModal(product)}



                    className="bg-[#FFFFFF] border border-[#DDE3EA] hover:border-[#14B8A6]/60 rounded-2xl p-5 flex flex-col justify-between transition-all duration-200 cursor-pointer group shadow-sm hover:shadow-md"



                  >



                    <div>



                      {/* Top Badges */}



                      <div className="flex items-center justify-between gap-2 mb-3">



                        <span className="px-2.5 py-0.5 rounded-full bg-[#DCFCE7] border border-[#166534]/20 text-[#166534] text-[10px] font-black uppercase tracking-wider">



                          {lang === 'bn' ? product.statusBn : product.statusEn}



                        </span>

                          {product.variant && (
                            <span className="px-2 py-0.5 rounded-md bg-[#F0FDFA] border border-[#0D9488]/30 text-[#0F766E] text-[10px] font-black tracking-wide uppercase">
                              {product.variant}
                            </span>
                          )}
                          {product.isDiscontinued && (
                            <span className="px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/40 text-amber-700 text-[10px] font-black tracking-wide uppercase">
                              {lang === 'bn' ? 'মার্কেট-আউট' : 'Market-Out'}
                            </span>
                          )}



                        <span className="text-[11px] font-semibold text-[#334155]">



                          {lang === 'bn'



                            ? `${toBengaliDigits(product.storeCount)}টি শপ তুলনা`



                            : `${product.storeCount} Stores Compared`}



                        </span>



                      </div>







                      {/* Clean Product Visual Container with Image Proxy */}



                      <div className="relative h-44 w-full bg-[#F5F7FA] rounded-xl overflow-hidden mb-3.5 border border-[#DDE3EA] flex items-center justify-center p-2">



                        <img



                          src={getImageProxyUrl(product.image)}



                          onError={(e) => {



                            e.currentTarget.onerror = null;



                            e.currentTarget.src = getProductFallbackImage(product);



                          }}



                          alt={product.nameEn}



                          className="w-full h-full object-contain group-hover:scale-105 transition-transform duration-300"



                        />



                      </div>







                      {/* Product Category & Title */}



                      <span className="text-[10px] font-bold uppercase tracking-wider text-[#0F766E] block mb-1">



                        {lang === 'bn' ? product.categoryBn : product.categoryEn}



                      </span>



                      <h3 className="text-sm font-bold text-[#101B2D] line-clamp-2 min-h-[40px] leading-snug group-hover:text-[#0F766E] transition-colors">



                        {lang === 'bn' ? product.nameBn : product.nameEn}



                      </h3>

                      {product.variant && (
                        <div className="mt-2 flex items-center gap-1.5 flex-wrap">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold bg-[#E6FFFA] text-[#0F766E] border border-[#0D9488]/30 shadow-xs">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#0D9488] shrink-0"></span>
                            <span>{lang === 'bn' ? 'ভ্যারিয়েন্ট / কোয়ালিটি:' : 'Variant / Quality:'} <strong className="font-extrabold text-[#0D9488]">{product.variant}</strong></span>
                          </span>
                        </div>
                      )}

                      {product.isDiscontinued && (
                        <div className="mt-2.5 p-2 rounded-lg bg-amber-50 border border-amber-200/80 text-amber-900 text-[11px] font-semibold flex items-center gap-2 leading-tight">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                          <span>
                            {lang === 'bn'
                              ? 'অফিসিয়াল উৎপাদন বন্ধ — বাজারে প্রি-ওউনড/ডিলার স্টকে মিলছে'
                              : 'Production Ended — Available via pre-owned/dealer stock'}
                          </span>
                        </div>
                      )}



                    </div>







                    {/* Price & Action Row */}



                    <div className="mt-4 pt-3 border-t border-[#DDE3EA] flex items-center justify-between gap-3">



                      <div>



                        <span className="text-xs text-[#334155] block">



                          {product.isBrowse ? (lang === 'bn' ? 'শুরু এখান থেকে' : 'Starts from') : (lang === 'bn' ? 'সর্বনিম্ন দাম' : 'Lowest Price')}



                        </span>



                        <div className="flex items-baseline gap-2">



                          <span className="text-lg font-extrabold text-[#101B2D]">



                            {formatBDT(product.price, lang)}



                          </span>



                          {product.originalPrice > product.price && (



                            <span className="text-xs text-slate-400 line-through">



                              {formatBDT(product.originalPrice, lang)}



                            </span>



                          )}



                        </div>



                      </div>







                      <button



                        type="button"



                        onClick={(e) => {



                          e.stopPropagation();



                          openComparisonModal(product);



                        }}



                        className="px-4 py-2.5 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs uppercase tracking-wider transition cursor-pointer flex items-center gap-1.5 shadow-md"



                      >



                        <span>{lang === 'bn' ? 'শপ তুলনা' : 'Compare Stores'}</span>



                        <ArrowUpRight className="w-3.5 h-3.5" />



                      </button>



                    </div>



                  </div>



                ))}



              </div>



            )}



          </div>



        ) : (



          /* =================================================================
             MODE B: HOT PRODUCTS LIVE PRICING & MARKET TRACKER
             High contrast, professional border-card theme matching other cards.
          ================================================================= */
          <div className="space-y-6">
            {/* Section Header with Maximum Contrast */}
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 border-b border-[#DDE3EA] pb-4">
              <div>
                <span className="text-[11px] font-black uppercase tracking-[0.2em] text-[#0F766E] block mb-1">
                  {lang === 'bn' ? '🔥 বাংলাদেশ লাইভ মার্কেট বেঞ্চমার্ক' : '🔥 BANGLADESH LIVE MARKET BENCHMARKS'}
                </span>
                <h2 className="font-display text-xl sm:text-2xl font-black uppercase text-[#101B2D] tracking-tight">
                  {lang === 'bn'
                    ? 'হট প্রোডাক্টস লাইভ প্রাইসিং — মার্কেট ট্র্যাকার'
                    : 'HOT PRODUCTS LIVE PRICING — MARKET TRACKER'}
                </h2>
              </div>
              <p className="text-xs text-[#334155] max-w-md font-medium leading-relaxed">
                {lang === 'bn'
                  ? 'স্বর্ণ, জ্বালানি তেল, আইফোন, স্যামসাং, র‌্যাম, এসএসডি, জিপিইউ ও প্রসেসরের শুরু থেকে সর্বনিম্ন লাইভ বাজার দর ও ভেরিফায়েড স্টোর তালিকা।'
                  : 'Live benchmark rates for Gold, Fuel, iPhones, Samsung S Series, RAM, SSD, GPU & Processors with verified direct store links.'}
              </p>
            </div>

            {/* Horizontal Benchmark Bars List (Border-card Theme matching other cards) */}
            <div className="flex flex-col space-y-3.5">
              {(hotProducts || INITIAL_HOT_PRODUCTS).map((hp) => {
                const isExpanded = expandedHotProductId === (hp.id || hp.slug);
                const isGold = hp.slug === 'gold-hallmark-pricing';
                const isFuel = hp.slug === 'fuel-oil-energy';

                return (
                  <div
                    key={hp.id || hp.slug}
                    className="bg-[#FFFFFF] border border-[#DDE3EA] hover:border-[#14B8A6]/70 rounded-2xl shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden"
                  >
                    {/* Horizontal Bar Content (Entire bar is clickable with animated dropdown chevron) */}
                    <div
                      onClick={() => setExpandedHotProductId(isExpanded ? null : (hp.id || hp.slug))}
                      className="p-4 sm:p-5 flex flex-col xl:flex-row xl:items-center justify-between gap-4 cursor-pointer select-none bg-white group hover:bg-[#FAFDFB] transition-colors"
                    >
                      {/* Left: Icon & Product Identity */}
                      <div className="flex items-center gap-3.5 min-w-0 sm:min-w-[240px] shrink-0">
                        <div className="w-11 h-11 rounded-xl bg-[#F8FAFC] border border-[#DDE3EA] flex items-center justify-center shrink-0 group-hover:border-[#14B8A6]/60 transition-colors">
                          {renderHotProductIcon(hp.icon_name)}
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-display text-base sm:text-lg font-bold text-[#101B2D] leading-tight group-hover:text-[#0F766E] transition-colors">
                            {lang === 'bn' ? (hp.title_bn || hp.title_en) : (hp.title_en || hp.title_bn)}
                          </h3>
                          <p className="text-xs text-[#64748B] mt-0.5">
                            {lang === 'bn' ? (hp.subtitle_bn || hp.subtitle_en) : (hp.subtitle_en || hp.subtitle_bn)}
                          </p>
                        </div>
                      </div>

                      {/* Center: Specialized Detail Badges (Zero cut-off, clean typography) */}
                      {isGold ? (
                        /* Gold Hallmark Detail (22K & 24K benchmark) */
                        <div className="flex-1 bg-[#FFFBEB] border border-[#FDE68A] rounded-xl px-3.5 py-2 flex items-center justify-between gap-3 shadow-2xs">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-2 py-0.5 rounded-md bg-[#D97706] text-white text-[10px] font-black uppercase tracking-wider shrink-0 flex items-center gap-1">
                              ✨ {lang === 'bn' ? 'বাজুস হলমার্ক রেট' : 'BAJUS Benchmark'}
                            </span>
                            <span className="text-xs font-bold text-[#92400E]">
                              {lang === 'bn'
                                ? '২৪ ক্যারেট: ৳১৫৪,৭০০/ভরি • ২২ ক্যারেট: ৳১৪১,৮০০/ভরি'
                                : '24K: ৳154,700/Vori • 22K: ৳141,800/Vori'}
                            </span>
                          </div>
                          <a
                            href="https://www.bajus.org/"
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-[11px] font-bold px-2.5 py-1 rounded-md bg-[#FEF3C7] hover:bg-[#F59E0B] hover:text-white text-[#92400E] border border-[#FDE68A] transition flex items-center gap-1 shrink-0"
                          >
                            <span>{lang === 'bn' ? 'বাজুস ↗' : 'BAJUS ↗'}</span>
                          </a>
                        </div>
                      ) : isFuel ? (
                        /* Fuel Energy Detail (Octane, Diesel, Petrol) */
                        <div className="flex-1 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl px-3.5 py-2 flex items-center justify-between gap-3 shadow-2xs">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-2 py-0.5 rounded-md bg-[#2563EB] text-white text-[10px] font-black uppercase tracking-wider shrink-0 flex items-center gap-1">
                              ⛽ {lang === 'bn' ? 'বিপিসি নির্ধারিত দর' : 'BPC Regulated'}
                            </span>
                            <span className="text-xs font-bold text-[#1E40AF]">
                              {lang === 'bn'
                                ? 'অকটেন: ৳১২৫/লি • ডিজেল: ৳১০৫/লি • পেট্রোল: ৳১২০/লি'
                                : 'Octane: ৳125/L • Diesel: ৳105/L • Petrol: ৳120/L'}
                            </span>
                          </div>
                          <a
                            href="https://padmaoil.gov.bd/"
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-[11px] font-bold px-2.5 py-1 rounded-md bg-[#DBEAFE] hover:bg-[#2563EB] hover:text-white text-[#1E40AF] border border-[#BFDBFE] transition flex items-center gap-1 shrink-0"
                          >
                            <span>{lang === 'bn' ? 'বিপিসি ↗' : 'BPC ↗'}</span>
                          </a>
                        </div>
                      ) : hp.latest_release_name ? (
                        /* Tech Item Latest Release Badge */
                        <div className="flex-1 bg-[#F8FAFC] border border-[#E2E8F0] hover:border-[#CBD5E1] rounded-xl px-3.5 py-2 flex items-center justify-between gap-3 shadow-2xs transition">
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-2 py-0.5 rounded-md bg-[#F59E0B] text-black text-[10px] font-black uppercase tracking-wider shrink-0 flex items-center gap-1">
                              🔥 {hp.latest_release_badge || (lang === 'bn' ? 'লেটেস্ট রিলিজ' : 'Latest Release')}
                            </span>
                            <span className="text-xs font-semibold text-[#1E293B]">
                              {hp.latest_release_name}
                            </span>
                          </div>
                          <div className="flex items-center gap-2 shrink-0">
                            <span className="text-xs font-black text-[#0F766E] font-mono">
                              ৳{Number(hp.latest_release_price || 0).toLocaleString()}
                            </span>
                            {hp.latest_release_url && (
                              <a
                                href={hp.latest_release_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-white hover:bg-[#0F766E] hover:text-white text-[#0F766E] border border-[#CBD5E1] hover:border-[#0F766E] transition flex items-center gap-1"
                              >
                                <span>{lang === 'bn' ? 'দেখুন' : 'View'}</span>
                                <ArrowUpRight className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>
                      ) : (
                        <div className="hidden xl:block flex-1" />
                      )}

                      {/* Right: Starts From, Prev Price, Price Drop/Increase Pill & Animated Chevron Indicator */}
                      <div className="flex items-center justify-between xl:justify-end gap-3.5 shrink-0 border-t xl:border-t-0 pt-3 xl:pt-0 border-[#F1F5F9]">
                        <div className="text-left xl:text-right">
                          <div className="text-[11px] font-semibold text-[#64748B]">
                            {lang === 'bn' ? (hp.unit_bn || 'শুরু') : (hp.unit_en || 'Starts from')}
                          </div>
                          <div className="text-xl sm:text-2xl font-black text-[#0F766E] leading-tight">
                            ৳{Number(hp.current_price || 0).toLocaleString()}
                          </div>
                          {hp.previous_price > 0 && (
                            <div className="text-[11px] text-[#94A3B8] line-through font-medium">
                              {lang === 'bn' ? 'পূর্বের: ' : 'Prev: '}৳{Number(hp.previous_price || 0).toLocaleString()}
                            </div>
                          )}
                        </div>

                        {/* Price Change Highlighting Pill */}
                        <div className="flex items-center gap-2.5">
                          {hp.price_change_type === 'drop' && (
                            <span className="px-2.5 py-1 rounded-full bg-[#ECFDF5] border border-[#A7F3D0] text-[#047857] text-xs font-black flex items-center gap-1 shadow-2xs whitespace-nowrap">
                              <span>▼</span>
                              <span>৳{Number(hp.price_change_amount || 0).toLocaleString()} ({hp.price_change_percent}%)</span>
                            </span>
                          )}
                          {hp.price_change_type === 'increase' && (
                            <span className="px-2.5 py-1 rounded-full bg-[#FFF1F2] border border-[#FECDD3] text-[#BE123C] text-xs font-black flex items-center gap-1 shadow-2xs whitespace-nowrap">
                              <span>▲</span>
                              <span>৳{Number(hp.price_change_amount || 0).toLocaleString()} (+{hp.price_change_percent}%)</span>
                            </span>
                          )}
                          {hp.price_change_type === 'stable' && (
                            <span className="px-2.5 py-1 rounded-full bg-[#F1F5F9] border border-[#E2E8F0] text-[#475569] text-xs font-bold flex items-center gap-1 whitespace-nowrap">
                              <span>●</span>
                              <span>{lang === 'bn' ? 'দর অপরিবর্তিত' : 'Market Stable'}</span>
                            </span>
                          )}

                          {/* Sleek Animated Dropdown Chevron (replaces bulky button) */}
                          <div
                            title={isExpanded ? 'Click to collapse stores' : 'Click to view selling stores'}
                            className={`w-8 h-8 rounded-full border flex items-center justify-center transition-all duration-200 ${
                              isExpanded
                                ? 'bg-[#0F766E] text-white border-[#0F766E] shadow-sm'
                                : 'bg-[#F8FAFC] text-[#64748B] group-hover:text-[#0F766E] group-hover:border-[#14B8A6] border-[#DDE3EA]'
                            }`}
                          >
                            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} />
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Inline Stores Drawer */}
                    {isExpanded && (
                      <div className="border-t border-[#E2E8F0] bg-[#F8FAFC] p-4 sm:p-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3.5 pb-2.5 border-b border-[#E2E8F0]">
                          <div className="text-xs font-bold text-[#334155] uppercase tracking-wider flex items-center gap-2">
                            <span>🏪</span>
                            <span>
                              {lang === 'bn'
                                ? `বর্তমানে বিক্রি করছে এমন ভেরিফায়েড স্টোর (${(hp.stores || []).length}টি)`
                                : `Active Stores Currently Selling ${hp.title_en} (${(hp.stores || []).length} Verified Retailers)`}
                            </span>
                          </div>
                          {hp.search_query && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                executeLiveSearch(hp.search_query);
                              }}
                              className="text-xs font-bold text-[#0F766E] hover:underline flex items-center gap-1 cursor-pointer"
                            >
                              <span>{lang === 'bn' ? 'যাচাই-এ সব মডেল লাইভ সার্চ করুন' : 'Search All Live Models on JaChai'}</span>
                              <ArrowUpRight className="w-3 h-3" />
                            </button>
                          )}
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                          {(hp.stores || []).map((store, sIdx) => (
                            <div
                              key={sIdx}
                              className="bg-[#FFFFFF] border border-[#DDE3EA] hover:border-[#0F766E]/50 rounded-xl p-3.5 flex flex-col justify-between shadow-2xs transition group"
                            >
                              <div>
                                <div className="flex items-center justify-between gap-1 mb-1">
                                  <span className="font-bold text-sm text-[#101B2D] truncate">
                                    {store.name}
                                  </span>
                                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#ECFDF5] text-[#047857] border border-[#A7F3D0] shrink-0">
                                    {store.status || 'In Stock'}
                                  </span>
                                </div>
                                <div className="text-base font-black text-[#0F766E]">
                                  ৳{Number(store.price || 0).toLocaleString()}
                                </div>
                              </div>

                              <a
                                href={store.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="mt-3 w-full py-2 px-3 rounded-lg bg-[#101B2D] hover:bg-[#0F766E] text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition cursor-pointer shadow-xs group-hover:scale-[1.02]"
                              >
                                <span>{lang === 'bn' ? 'স্টোর হোমপেজে যান' : 'Visit Store Homepage'}</span>
                                <ArrowUpRight className="w-3 h-3" />
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

      </section>

{/* =====================================================================



          LESSON 5: BIKROY-SIMPLE STORE COMPARISON MODAL



      ===================================================================== */}



      {inspectProduct && (



        <div



          onClick={() => setInspectProduct(null)}



          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 sm:p-6 overflow-y-auto"



        >



          <div



            onClick={(e) => e.stopPropagation()}



            className="bg-[#FFFFFF] border border-[#DDE3EA] rounded-2xl max-w-2xl w-full overflow-hidden shadow-2xl my-auto"



          >



            {/* Modal Header */}



            <div className="p-5 sm:p-6 bg-[#101B2D] border-b border-[#DDE3EA]/20 flex items-start justify-between gap-4">



              <div className="flex items-center gap-4">



                <img



                  src={getImageProxyUrl(inspectProduct.image)}



                  onError={(e) => {



                    e.currentTarget.onerror = null;



                    e.currentTarget.src = getProductFallbackImage(inspectProduct);



                  }}



                  alt={inspectProduct.nameEn}



                  className="w-16 h-16 rounded-xl object-contain bg-[#181B24] p-1.5 border border-white/10 shrink-0"



                />



                <div>



                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#14B8A6]">



                    {lang === 'bn'



                      ? inspectProduct.categoryBn



                      : inspectProduct.categoryEn}



                  </span>



                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5 leading-snug">



                    {lang === 'bn' ? inspectProduct.nameBn : inspectProduct.nameEn}



                  </h3>

                  {inspectProduct.variant && (
                    <div className="mt-2 flex items-center gap-1.5 flex-wrap">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-extrabold uppercase bg-[#14B8A6]/20 text-[#2DD4BF] border border-[#14B8A6]/40 shadow-xs">
                        <span className="w-1.5 h-1.5 rounded-full bg-[#2DD4BF] shrink-0"></span>
                        <span>{lang === 'bn' ? 'ভ্যারিয়েন্ট / কোয়ালিটি: ' : 'Variant / Quality: '}<strong>{inspectProduct.variant}</strong></span>
                      </span>
                    </div>
                  )}

                  {inspectProduct.isDiscontinued && (
                    <div className="mt-3.5 p-3.5 rounded-xl bg-amber-500/15 border border-amber-500/35 text-amber-100 flex items-start gap-2.5 shadow-sm">
                      <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[11px] font-black uppercase tracking-wider text-amber-400">
                          {lang === 'bn' ? '⚠️ অফিসিয়াল উৎপাদন বন্ধ / মার্কেট-আউট' : '⚠️ Officially Discontinued / Out of Production'}
                        </div>
                        <p className="text-xs text-amber-200/90 mt-1 leading-relaxed font-medium">
                          {lang === 'bn' ? inspectProduct.discontinuedNoteBn : inspectProduct.discontinuedNoteEn}
                        </p>
                      </div>
                    </div>
                  )}



                </div>



              </div>







              <button



                onClick={() => setInspectProduct(null)}



                className="w-8 h-8 rounded-full border border-white/20 hover:border-white text-white flex items-center justify-center transition cursor-pointer shrink-0"



              >



                <X className="w-4 h-4" />



              </button>



            </div>







            {/* Single-Line 30-Day Price Trend Bar */}



            <div className="px-4 sm:px-6 py-3 bg-[#F5F7FA] border-b border-[#DDE3EA] flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 text-xs">



              <div className="flex items-center gap-2 text-[#334155] font-semibold shrink-0">



                <TrendingDown className="w-4 h-4 text-[#166534]" />



                <span>



                  {lang === 'bn'



                    ? '৩০ দিনের প্রাইস ট্রেন্ড:'



                    : '30-Day Price Trend:'}



                </span>



              </div>



              <div className="flex flex-wrap items-center gap-2 sm:gap-3 font-semibold text-xs">



                <span className="text-[#334155] whitespace-nowrap">



                  {lang === 'bn' ? '৩০ দিন আগে:' : '30d Ago:'}{' '}



                  <strong className="text-[#101B2D]">



                    {formatBDT(inspectProduct.pastPrices?.[0]?.price, lang)}



                  </strong>



                </span>



                <span className="text-slate-400">→</span>



                <span className="text-[#334155] whitespace-nowrap">



                  {lang === 'bn' ? '১৫ দিন আগে:' : '15d Ago:'}{' '}



                  <strong className="text-[#101B2D]">



                    {formatBDT(inspectProduct.pastPrices?.[1]?.price, lang)}



                  </strong>



                </span>



                <span className="text-slate-400">→</span>



                <span className="text-[#166534] font-extrabold whitespace-nowrap">



                  {inspectProduct.isBrowse ? (lang === 'bn' ? 'শুরু এখান থেকে:' : 'Starts from:') : (lang === 'bn' ? 'আজকের সর্বনিম্ন:' : 'Today:')}{' '}



                  {formatBDT(inspectProduct.pastPrices?.[2]?.price ?? inspectProduct.price, lang)}



                </span>



              </div>



            </div>







            {/* Sorted List of Verified Store Offers */}



            <div className="divide-y divide-[#DDE3EA] max-h-[55vh] overflow-y-auto">



              {inspectProduct.offers.map((offer, idx) => {



                const isLowest = offer.price === inspectProduct.price;



                const hasWebsite = Boolean(offer.websiteUrl || (offer.url && !offer.url.includes('facebook.com')));



                const hasFacebook = Boolean(offer.facebookUrl || (offer.url && offer.url.includes('facebook.com')) || offer.store === 'F-COMMERCE');



                const origPrice = offer.originalPrice || Math.round(offer.price * 1.15);



                const discTag = offer.discountTag || (origPrice > offer.price ? `${Math.round(((origPrice - offer.price) / origPrice) * 100)}% OFF` : null);







                return (



                  <div
                    key={offer.id || idx}
                    className={`p-4 sm:p-5 flex flex-col lg:flex-row lg:items-center justify-between gap-4 transition ${
                      offer.riskLevel === 'high'
                        ? 'bg-rose-50/80 border-l-4 border-l-rose-500 shadow-sm'
                        : 'hover:bg-[#F5F7FA]'
                    }`}
                  >



                    {/* Store Meta & Badges */}



                    <div className="space-y-1.5 flex-1">



                      <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">



                        <span className="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-[#101B2D]/10 text-[#101B2D] border border-[#101B2D]/15">



                          {offer.store}



                        </span>



                        <span className="text-sm font-bold text-[#101B2D]">



                          {lang === 'bn' ? offer.subStoreBn || offer.subStoreEn : offer.subStoreEn}



                        </span>







                        {/* Two-Tier Priority Partner Indicator */}



                        {offer.isPreseeded ? (
                          <span className="px-2.5 py-0.5 rounded-full bg-[#DCFCE7] border border-[#166534]/25 text-[#166534] text-[10px] font-extrabold flex items-center gap-1">
                            ✓ {lang === 'bn' ? 'ভেরিফাইড শপ' : 'Verified Store'}
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 rounded-full bg-amber-100 border border-amber-300 text-amber-900 text-[10px] font-black flex items-center gap-1 shadow-xs">
                            ⚠️ {lang === 'bn' ? 'আনভেরিফাইড শপ · শুধুমাত্র সিওডি' : 'Unverified Merchant · COD Only'}
                          </span>
                        )}



                        {offer.isSponsored && (



                          <span className="border border-[#F59E0B]/40 bg-[#F59E0B]/10 text-[#F59E0B] text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded">



                            {lang === 'bn' ? 'স্পনসরড' : 'SPONSORED'}



                          </span>



                        )}



                      </div>







                      <p className="text-xs text-[#334155]">



                        {lang === 'bn' ? offer.termsBn || offer.termsEn : offer.termsEn}



                      </p>



                      <p className="text-xs text-[#166534] font-medium flex items-center gap-1">



                        <Check className="w-3.5 h-3.5" />



                        <span>



                          {lang === 'bn' ? offer.warrantyBn || offer.warrantyEn : offer.warrantyEn}



                        </span>



                      </p>



                    </div>







                    {/* Price, Discount & Dynamic 1-Button / 2-Button Action Cluster */}



                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between lg:justify-end gap-3 sm:gap-4 pt-3 lg:pt-0 border-t lg:border-t-0 border-[#DDE3EA] shrink-0">



                      {/* Price & Discount Strike-through */}



                      <div className="flex flex-col sm:items-end">



                        <div className="flex items-center gap-2">



                          <span className="text-xl sm:text-2xl font-black text-[#101B2D]">



                            {formatBDT(offer.price, lang)}



                          </span>



                          {discTag && (



                            <span className="px-1.5 py-0.5 rounded-md bg-[#EF4444]/20 border border-[#EF4444]/40 text-[#B91C1C] text-[10px] font-black">



                              {discTag}



                            </span>



                          )}



                        </div>



                        {origPrice > offer.price && (



                          <span className="text-xs text-[#94A3B8] line-through">



                            {formatBDT(origPrice, lang)}



                          </span>



                        )}



                      </div>







                      {/* Outbound Action Buttons: Dynamic 1 or 2 Buttons */}



                      <div className="flex items-center gap-2 w-full sm:w-auto">



                        {/* 1. Website Button */}



                        {hasWebsite && (



                          <button



                            type="button"



                            onClick={() => triggerOutbound(offer, 'website')}



                            className={`px-3.5 py-2 rounded-xl font-extrabold text-xs tracking-wider flex items-center justify-center gap-1.5 transition cursor-pointer flex-1 sm:flex-none ${



                              !hasFacebook && isLowest



                                ? 'bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] shadow-md font-black'



                                : 'bg-white hover:bg-[#101B2D] hover:text-white text-[#101B2D] border border-[#DDE3EA]'



                            }`}



                            title={offer.websiteUrl}



                          >



                            <Globe className="w-3.5 h-3.5" />



                            <span>{lang === 'bn' ? 'ওয়েবসাইট' : 'Website'}</span>



                            <ArrowUpRight className="w-3 h-3 opacity-70" />



                          </button>



                        )}







                        {/* 2. Facebook Button */}



                        {hasFacebook && (



                          <button



                            type="button"



                            onClick={() => triggerOutbound(offer, 'facebook')}



                            className={`px-3.5 py-2 rounded-xl font-extrabold text-xs tracking-wider flex items-center justify-center gap-1.5 transition cursor-pointer flex-1 sm:flex-none ${



                              !hasWebsite && isLowest



                                ? 'bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] shadow-md font-black'



                                : 'bg-[#1877F2]/10 hover:bg-[#1877F2]/20 text-[#1877F2] border border-[#1877F2]/30 shadow-sm'



                            }`}



                            title={offer.facebookUrl}



                          >



                            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>



                            <span>{lang === 'bn' ? 'ফেসবুক' : 'Facebook'}</span>



                            <ArrowUpRight className="w-3 h-3 opacity-70" />



                          </button>



                        )}







                        {/* Fallback Single Button (if neither link explicitly resolved) */}



                        {!hasWebsite && !hasFacebook && (



                          <button



                            type="button"



                            onClick={() => triggerOutbound(offer, 'default')}



                            className={`px-4 py-2.5 rounded-xl font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-1.5 transition cursor-pointer w-full sm:w-auto ${



                              isLowest



                                ? 'bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] shadow-md font-black'



                                : 'bg-white hover:bg-[#101B2D] hover:text-white text-[#101B2D] border border-[#DDE3EA]'



                            }`}



                          >



                            <span>{lang === 'bn' ? 'স্টোরে যান' : 'Visit Store'}</span>



                            <ArrowUpRight className="w-3.5 h-3.5" />



                          </button>



                        )}



                      </div>



                    </div>



                  </div>



                );



              })}



            </div>



          </div>



        </div>



      )}







      {/* =====================================================================



          LESSON 5: ADVERTISER SLOT BOOKING MODAL



      ===================================================================== */}



      {showAdModal && (



        <div



          onClick={() => setShowAdModal(false)}



          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto"



        >



          <div



            onClick={(e) => e.stopPropagation()}



            className="bg-[#12141C] border border-white/15 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl my-auto"



          >



            <div className="flex items-center justify-between border-b border-white/10 pb-4">



              <div>



                <span className="text-[10px] font-bold uppercase tracking-widest text-[#F59E0B]">



                  JACHAI ADVERTISER SLOTS



                </span>



                <h3 className="font-display text-2xl font-bold uppercase text-white mt-0.5">



                  PARTNER RATES



                </h3>



              </div>



              <button



                onClick={() => setShowAdModal(false)}



                className="text-white/50 hover:text-white cursor-pointer"



              >



                <X className="w-5 h-5" />



              </button>



            </div>







            <form onSubmit={handlePublicAdSubmit} className="space-y-4">



              <div className="space-y-3">



                <div>



                  <label className="text-[11px] font-bold text-white/70 uppercase tracking-wider block mb-1">



                    {lang === 'bn' ? 'ব্র্যান্ড / শপের নাম' : 'Brand / Store Name'}



                  </label>



                  <input



                    type="text"



                    required



                    value={adFormBrand}



                    onChange={(e) => setAdFormBrand(e.target.value)}



                    placeholder={lang === 'bn' ? 'যেমন: Aarohi Weaves' : 'e.g. Urban Sole BD'}



                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#0D1524] border border-white/15 text-xs text-white placeholder:text-white/30 focus:outline-none focus:border-[#14B8A6]"



                  />



                </div>



                <div>



                  <label className="text-[11px] font-bold text-white/70 uppercase tracking-wider block mb-1">



                    {lang === 'bn' ? 'ফোন বা হোয়াটসঅ্যাপ নম্বর' : 'Phone / WhatsApp Number'}



                  </label>



                  <input



                    type="tel"



                    required



                    value={adFormPhone}



                    onChange={(e) => setAdFormPhone(e.target.value)}



                    placeholder="+880 1XXXXXXXXX"



                    className="w-full px-3.5 py-2.5 rounded-xl bg-[#0D1524] border border-white/15 text-xs text-white placeholder:text-white/30 focus:outline-none focus:border-[#14B8A6]"



                  />



                </div>



              </div>







              <div className="space-y-2">



                <span className="text-[11px] font-bold text-white/70 uppercase tracking-wider block">



                  {lang === 'bn' ? 'বিজ্ঞাপন স্লট নির্বাচন করুন' : 'Select Desired Ad Placement'}



                </span>



                <div className="space-y-2.5">



                  {[



                    {



                      id: 'billboard',



                      title: '1. Primary Kinetic Billboard',



                      desc: 'Above-the-fold centerpiece visibility with parallax photography.',



                      rate: '৳15,000 / Week'



                    },



                    {



                      id: 'spotlight',



                      title: '2. Product Spotlight Placement',



                      desc: 'Promoted card placement inside relevant shopping categories.',



                      rate: '৳7,500 / Week'



                    },



                    {



                      id: 'ticker',



                      title: '3. Dual 55s Continuous Tickers',



                      desc: 'Top of page and footer continuous announcement inclusion.',



                      rate: '৳4,000 / Week'



                    }



                  ].map((tier) => (



                    <div



                      key={tier.id}



                      onClick={() => setSelectedAdTier(tier.id)}



                      className={`p-3 rounded-xl border cursor-pointer transition ${



                        selectedAdTier === tier.id



                          ? 'border-[#14B8A6] bg-white/[0.04]'



                          : 'border-white/10 bg-[#0D1524] hover:border-white/20'



                      }`}



                    >



                      <div className="flex items-center justify-between">



                        <span className="text-xs font-bold text-white">



                          {tier.title}



                        </span>



                        <span className="text-xs font-extrabold text-[#FFC857]">



                          {tier.rate}



                        </span>



                      </div>



                      <p className="text-xs text-white/50 mt-1">{tier.desc}</p>



                    </div>



                  ))}



                </div>



              </div>







              <button



                type="submit"



                className="w-full py-3 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] font-extrabold text-xs uppercase tracking-wider transition cursor-pointer shadow-lg"



              >



                {lang === 'bn' ? 'বিজ্ঞাপন স্লট আবেদন জমা দিন' : 'Submit Booking Request'}



              </button>



            </form>



          </div>



        </div>



      )}







      {/* OUTBOUND REDIRECT TOAST NOTIFICATION */}



      {redirectToast && (



        <div className="fixed bottom-6 right-6 z-50 bg-[#12141C] text-white px-5 py-3.5 rounded-xl shadow-2xl border border-white/20 border-l-4 border-l-[#14B8A6] text-xs font-bold flex items-center gap-3">



          <span className="w-2 h-2 rounded-full bg-[#14B8A6]" />



          <div>



            <span className="block text-[10px] uppercase tracking-wider text-white/50">



              Redirecting to Partner Store



            </span>



            <span>



              {redirectToast.store} — {formatBDT(redirectToast.price, lang)}



            </span>



          </div>



        </div>



      )}







      {/* =====================================================================



          FOOTER & BOTTOM SLOW-GLIDING MARQUEE TICKER (DYNAMIC SPEED)



      ===================================================================== */}



      <footer className="bg-[#101B2D] border-t border-[#DDE3EA]/20">



        <div className="max-w-7xl mx-auto px-4 sm:px-8 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">



          <div>



            <JaChaiLogo



              onTap={handleResetToHome}



              showMotto={true}



              size="compact"



            />



            <p className="text-xs text-slate-400 mt-1">



              The Best Price for Your Next Purchase — Bangladeshi Price Index.



            </p>



          </div>







          <button



            onClick={() => setShowAdModal(true)}



            className="px-4 py-2 rounded-lg bg-white/10 border border-white/15 text-xs font-bold text-white hover:bg-white/15 cursor-pointer"



          >



            {lang === 'bn' ? 'বিজ্ঞাপন বুকিং' : 'Book Advertiser Slot'}



          </button>



        </div>







        {/* Bottom Marquee Ticker */}



        <div className="w-full bg-[#0B1320] border-t border-white/10 py-2.5 overflow-hidden select-none">



          <div



            className="animate-marquee"



            style={{ animationDuration: `${tickerSpeed}s` }}



          >



            {[...tickers, ...tickers, ...tickers].map((item, idx) => (



              <button



                key={`bot-ticker-${idx}`}



                onClick={() => openComparisonModal(item.targetKey)}



                className="flex items-center gap-2.5 px-7 text-xs text-slate-300 hover:text-white transition cursor-pointer whitespace-nowrap"



              >



                <span className="w-1.5 h-1.5 rounded-full bg-[#14B8A6] shrink-0" />



                <span className="font-bold text-[#FFC857]">



                  {lang === 'bn' ? item.brandBn : item.brandEn}:



                </span>



                <span>{lang === 'bn' ? item.textBn : item.textEn}</span>



                <span className="text-white/20 pl-3">·</span>



              </button>



            ))}



          </div>



        </div>



      </footer>







      {/* =====================================================================



          PART 1: ZERO-FOOTPRINT STEALTH ACCESS GATE MODAL



      ===================================================================== */}



      {showPinModal && (



        <div



          onClick={() => {



            if (lockoutRemaining === 0) setShowPinModal(false);



          }}



          className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4"



        >



          <div



            onClick={(e) => e.stopPropagation()}



            className="bg-[#12141C] border border-white/15 rounded-2xl max-w-sm w-full p-6 shadow-2xl relative"



          >



            <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">



              <div className="flex items-center gap-2.5">



                <div className="w-9 h-9 rounded-xl bg-[#F59E0B]/10 border border-[#F59E0B]/30 flex items-center justify-center">



                  <Lock className="w-4 h-4 text-[#F59E0B]" />



                </div>



                <div>



                  <h3 className="font-display text-lg font-bold uppercase text-white tracking-wider">



                    JaChai Ops Vault



                  </h3>



                  <span className="text-[10px] text-white/50 tracking-wider uppercase block">



                    Restricted Access Gate



                  </span>



                </div>



              </div>



              {lockoutRemaining === 0 && (



                <button



                  onClick={() => setShowPinModal(false)}



                  className="text-white/40 hover:text-white cursor-pointer"



                >



                  <X className="w-4 h-4" />



                </button>



              )}



            </div>







            {lockoutRemaining > 0 ? (



              <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/30 text-center space-y-2">



                <AlertTriangle className="w-6 h-6 text-red-400 mx-auto" />



                <h4 className="text-xs font-bold text-red-200 uppercase tracking-wider">



                  Vault Locked (Brute-Force Protection)



                </h4>



                <p className="text-[11px] text-white/60">



                  5 consecutive failed PIN attempts detected. Input is frozen.



                </p>



                <div className="font-mono text-lg font-extrabold text-red-400 pt-1">



                  {String(Math.floor(lockoutRemaining / 60)).padStart(2, '0')}:



                  {String(lockoutRemaining % 60).padStart(2, '0')}



                </div>

                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => {
                      localStorage.removeItem('jc_lockout_until');
                      localStorage.removeItem('jc_pin_fails');
                      setLockoutRemaining(0);
                      setPinError('');
                    }}
                    className="text-[11px] text-amber-400 hover:text-amber-300 underline font-medium cursor-pointer"
                  >
                    Reset Lockout Counter
                  </button>
                </div>



              </div>



            ) : (



              <form onSubmit={handleVerifyPin} className="space-y-4">



                <div>



                  <label className="text-[11px] font-bold text-white/70 uppercase tracking-wider block mb-1.5">



                    Security Passkey / PIN



                  </label>



                  <div className="relative flex items-center">



                    <input



                      type={showPinPassword ? 'text' : 'password'}



                      autoFocus



                      value={pinInput}



                      onChange={(e) => {



                        setPinInput(e.target.value);



                        setPinError('');



                      }}



                      placeholder="Enter security passkey..."



                      className="w-full px-3.5 py-2.5 rounded-xl bg-[#0D1524] border border-white/20 text-white font-mono text-sm tracking-wider focus:outline-none focus:border-[#14B8A6]"



                    />



                    <button



                      type="button"



                      onClick={() => setShowPinPassword(!showPinPassword)}



                      className="absolute right-3 text-white/40 hover:text-white cursor-pointer"



                    >



                      {showPinPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}



                    </button>



                  </div>



                  {pinError && (



                    <p className="text-[11px] text-red-400 mt-2 font-medium">



                      {pinError}



                    </p>



                  )}





                </div>







                <div className="pt-2 flex items-center gap-2.5">



                  <button



                    type="button"



                    onClick={() => setShowPinModal(false)}



                    className="flex-1 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-white/70 hover:text-white text-xs font-bold uppercase tracking-wider cursor-pointer transition"



                  >



                    Cancel



                  </button>



                  <button



                    type="submit"



                    className="flex-1 py-2.5 rounded-xl bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] text-xs font-extrabold uppercase tracking-wider flex items-center justify-center gap-1.5 cursor-pointer shadow-lg transition"



                  >



                    <Unlock className="w-3.5 h-3.5" />



                    <span>Unlock</span>



                  </button>



                </div>



              </form>



            )}



          </div>



        </div>



      )}



      {/* STORE LEADERBOARD MODAL */}
      <StoreLeaderboardModal
        isOpen={isLeaderboardOpen}
        onClose={() => setIsLeaderboardOpen(false)}
        lang={lang}
        categoriesList={categoriesList}
        onSelectProductDeal={(productTitle) => {
          setIsLeaderboardOpen(false);
          setSearchQuery(productTitle);
          setSelectedCategory('all');
          executeLiveSearch(productTitle, 'all');
        }}
      />
    </div>



  );



}



