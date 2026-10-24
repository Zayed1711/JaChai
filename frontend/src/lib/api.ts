export interface SearchProductResult {
  id: string;
  name: string;
  slug: string;
  model: string | null;
  category: string;
  brand: string | null;
  lowest_price: number | null;
  stores_count: number;
  similarity_score: number;
}

export interface SearchResponse {
  query: string;
  count: number;
  results: SearchProductResult[];
}

export interface PriceHistoryPoint {
  price: number;
  original_price: number | null;
  captured_at: string;
}

export interface StoreOfferItem {
  listing_id: string;
  store_name: string;
  store_slug: string;
  store_type: string;
  platform: string;
  raw_title: string;
  source_url: string;
  redirect_url: string;
  seller_name: string | null;
  seller_rating: number | null;
  warranty_text: string | null;
  in_stock: boolean;
  thumbnail_url: string | null;
  current_price: number;
  original_price: number | null;
  delivery_charge: number | null;
  cod_available: boolean | null;
  last_checked_at: string | null;
  is_stale: boolean;
  risk_level?: string;
  trust_badge?: string;
  price_history: PriceHistoryPoint[];
}

export interface ProductOffersResponse {
  product_id: string;
  product_name: string;
  product_slug: string;
  model: string | null;
  category: string;
  brand: string | null;
  offers_count: number;
  lowest_price: number | null;
  offers: StoreOfferItem[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

const BENGALI_DIGITS: Record<string, string> = {
  "0": "০", "1": "১", "2": "২", "3": "৩", "4": "৪",
  "5": "৫", "6": "৬", "7": "৭", "8": "৮", "9": "৯",
};

/**
 * Format numeric BDT amount into Bangladeshi Taka currency format (e.g. ৳ ১,২০,০০০ or ৳ 120,000)
 */
export function formatBDT(price: number | null | undefined, useBengaliDigits: boolean = false): string {
  if (price === null || price === undefined || isNaN(price)) {
    return "৳ --";
  }

  // Format with South Asian numbering system (en-IN gives 1,20,000 style formatting)
  const formattedEn = new Intl.NumberFormat("en-IN", {
    maximumFractionDigits: 0,
  }).format(price);

  if (!useBengaliDigits) {
    return `৳ ${formattedEn}`;
  }

  // Convert digits to Bengali
  const formattedBn = formattedEn.replace(/\d/g, (d) => BENGALI_DIGITS[d] || d);
  return `৳ ${formattedBn}`;
}

// Fallback catalog mock data in case backend is offline during build/demo
const MOCK_PRODUCTS: SearchProductResult[] = [
  {
    id: "s24u-mock-id",
    name: "Samsung Galaxy S24 Ultra",
    slug: "samsung-galaxy-s24-ultra",
    model: "SM-S928B/DS",
    category: "Smartphones",
    brand: "Samsung",
    lowest_price: 139999,
    stores_count: 2,
    similarity_score: 1.0,
  },
  {
    id: "shirt-mock-id",
    name: "Old Money Textured Cuban Collar Shirt",
    slug: "old-money-textured-cuban-collar-shirt",
    model: "OM-CC-01",
    category: "Men's Fashion",
    brand: "Artisan Heritage",
    lowest_price: 1850,
    stores_count: 1,
    similarity_score: 1.0,
  },
];

const MOCK_OFFERS: Record<string, ProductOffersResponse> = {
  "samsung-galaxy-s24-ultra": {
    product_id: "s24u-mock-id",
    product_name: "Samsung Galaxy S24 Ultra",
    product_slug: "samsung-galaxy-s24-ultra",
    model: "SM-S928B/DS",
    category: "Smartphones",
    brand: "Samsung",
    offers_count: 2,
    lowest_price: 139999,
    offers: [
      {
        listing_id: "daraz-listing-id",
        store_name: "Daraz Bangladesh",
        store_slug: "daraz-bd",
        store_type: "marketplace",
        platform: "daraz",
        raw_title: "Samsung Galaxy S24 Ultra 5G (12GB/256GB) - Titanium Gray [Official BD Warranty]",
        source_url: "https://www.daraz.com.bd",
        redirect_url: "http://localhost:8000/go/daraz-listing-id",
        seller_name: "Samsung Brand Store (DarazMall)",
        seller_rating: 4.8,
        warranty_text: "1 Year Official Samsung Bangladesh Warranty",
        in_stock: true,
        thumbnail_url: null,
        current_price: 139999,
        original_price: 169999,
        delivery_charge: 0,
        cod_available: true,
        last_checked_at: new Date().toISOString(),
        is_stale: false,
        price_history: [
          { price: 159999, original_price: 169999, captured_at: new Date(Date.now() - 10 * 86400000).toISOString() },
          { price: 149999, original_price: 169999, captured_at: new Date(Date.now() - 3 * 86400000).toISOString() },
          { price: 139999, original_price: 169999, captured_at: new Date().toISOString() },
        ],
      },
      {
        listing_id: "startech-listing-id",
        store_name: "Star Tech",
        store_slug: "star-tech",
        store_type: "web_store",
        platform: "custom",
        raw_title: "Samsung Galaxy S24 Ultra 12GB RAM 256GB ROM Titanium Gray",
        source_url: "https://www.startech.com.bd",
        redirect_url: "http://localhost:8000/go/startech-listing-id",
        seller_name: "Star Tech Engineering Ltd",
        seller_rating: 4.9,
        warranty_text: "1 Year Official Warranty",
        in_stock: true,
        thumbnail_url: null,
        current_price: 142000,
        original_price: 150000,
        delivery_charge: 60,
        cod_available: true,
        last_checked_at: new Date().toISOString(),
        is_stale: false,
        price_history: [
          { price: 144000, original_price: 150000, captured_at: new Date(Date.now() - 7 * 86400000).toISOString() },
          { price: 142000, original_price: 150000, captured_at: new Date().toISOString() },
        ],
      },
    ],
  },
  "old-money-textured-cuban-collar-shirt": {
    product_id: "shirt-mock-id",
    product_name: "Old Money Textured Cuban Collar Shirt",
    product_slug: "old-money-textured-cuban-collar-shirt",
    model: "OM-CC-01",
    category: "Men's Fashion",
    brand: "Artisan Heritage",
    offers_count: 1,
    lowest_price: 1850,
    offers: [
      {
        listing_id: "fb-listing-id",
        store_name: "BD Gadget & Apparel Hub",
        store_slug: "bd-gadget-apparel-hub",
        store_type: "facebook_page",
        platform: "facebook",
        raw_title: "Premium Old Money Textured Cuban Collar Resort Shirt - Off White",
        source_url: "https://facebook.com/bdgadgetapparelhub",
        redirect_url: "http://localhost:8000/go/fb-listing-id",
        seller_name: "BD Gadget Hub (F-Commerce)",
        seller_rating: 4.6,
        warranty_text: "3 Days Replacement Guarantee",
        in_stock: true,
        thumbnail_url: null,
        current_price: 1850,
        original_price: 2500,
        delivery_charge: 100,
        cod_available: true,
        last_checked_at: new Date().toISOString(),
        is_stale: false,
        price_history: [
          { price: 2200, original_price: 2500, captured_at: new Date(Date.now() - 5 * 86400000).toISOString() },
          { price: 1850, original_price: 2500, captured_at: new Date().toISOString() },
        ],
      },
    ],
  },
};

/**
 * Perform product search via FastAPI backend with resilient fallback.
 */
export async function searchProducts(query: string): Promise<SearchResponse> {
  const cleanQ = query.trim();
  if (!cleanQ) {
    return { query: "", count: 0, results: [] };
  }

  try {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(cleanQ)}`, {
      cache: "no-store",
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline or unreachable - use client-side fuzzy fallback
  }

  // Resilient fallback for demo / SSG
  const filtered = MOCK_PRODUCTS.filter(
    (p) =>
      p.name.toLowerCase().includes(cleanQ.toLowerCase()) ||
      p.category.toLowerCase().includes(cleanQ.toLowerCase()) ||
      (p.brand && p.brand.toLowerCase().includes(cleanQ.toLowerCase()))
  );

  return {
    query: cleanQ,
    count: filtered.length,
    results: filtered,
  };
}

/**
 * Fetch product offers and price history by slug.
 */
export async function getProductOffers(slug: string): Promise<ProductOffersResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/products/${encodeURIComponent(slug)}/offers`, {
      cache: "no-store",
    });
    if (res.ok) {
      return await res.json();
    }
  } catch {
    // Backend offline or unreachable
  }

  // Resilient fallback for demo / SSG
  return MOCK_OFFERS[slug] || null;
}

