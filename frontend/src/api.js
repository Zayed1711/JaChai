/**
 * JaChai API Client
 * Connects frontend state directly to FastAPI backend on http://localhost:8000
 */

export const API_BASE_URL =
  (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) ||
  (typeof window !== 'undefined' && window.__VITE_API_URL__) ||
  '';

export function getAdminToken() {
  if (typeof window === 'undefined') return null;
  return sessionStorage.getItem('jachai_admin_token') || localStorage.getItem('jachai_admin_token');
}

export function setAdminToken(token) {
  if (typeof window === 'undefined') return;
  if (token) {
    sessionStorage.setItem('jachai_admin_token', token);
  } else {
    sessionStorage.removeItem('jachai_admin_token');
    localStorage.removeItem('jachai_admin_token');
  }
}

export function getAuthHeaders() {
  const token = getAdminToken();
  const headers = {
    'Content-Type': 'application/json',
    'X-Admin-Pin': '42791' // dev/local fallback
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// ==============================================================================
// PUBLIC STOREFRONT API
// ==============================================================================

export async function fetchStorefrontInit(trackImpressions = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/storefront/init?track_impressions=${trackImpressions}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] fetchStorefrontInit offline fallback:', err.message);
    return null;
  }
}

export async function fetchCategories() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/categories`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data?.categories || [];
  } catch (err) {
    console.warn('[JaChai API] fetchCategories error:', err.message);
    return [];
  }
}

export async function searchProducts(query = '', category = 'all') {
  try {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category && category !== 'all') params.append('category', category);
    const res = await fetch(`${API_BASE_URL}/api/v1/products?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] searchProducts error:', err.message);
    return null;
  }
}

export async function searchLiveProducts(query = '', category = 'all', browse = false) {
  try {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category && category !== 'all') params.append('category', category);
    if (browse) params.append('browse', 'true');
    const res = await fetch(`${API_BASE_URL}/api/v1/search/live?${params.toString()}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] searchLiveProducts error:', err.message);
    return null;
  }
}

export async function fetchTrendingHubs() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/storefront/trending-hubs`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.hubs || [];
  } catch (err) {
    console.warn('[JaChai API] fetchTrendingHubs error:', err.message);
    return [];
  }
}

export function getImageProxyUrl(url) {
  if (!url) return '';
  if (url.startsWith('/images/') || url.startsWith('/icons/') || url.startsWith('/uploads/') || url.startsWith('data:')) {
    return url;
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    if (url.includes('/uploads/')) return url;
    // Avoid double proxying if already pointing to localhost:8000/api/v1/image-proxy
    if (url.includes('/api/v1/image-proxy')) return url;
    return `${API_BASE_URL}/api/v1/image-proxy?url=${encodeURIComponent(url)}`;
  }
  return url;
}

export async function fetchProductOffers(slug) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/products/${slug}/offers`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] fetchProductOffers error:', err.message);
    return null;
  }
}

export async function submitAdvertiserLead(leadData) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/leads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadData)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] submitAdvertiserLead error:', err.message);
    return null;
  }
}

// Outbound /go/ Redirect & Click Tracking
export async function trackOutboundClick(type, id) {
  try {
    const endpoint =
      type === 'offer'
        ? `${API_BASE_URL}/api/v1/track/offer/${id}`
        : type === 'billboard'
        ? `${API_BASE_URL}/api/v1/track/billboard/${id}`
        : `${API_BASE_URL}/api/v1/track/spotlight/${id}`;

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn(`[JaChai API] trackOutboundClick error for ${type} #${id}:`, err.message);
  }
  return null;
}

// ==============================================================================
// STEALTH ADMIN AUTHENTICATION
// ==============================================================================

export async function adminLogin(pin) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pin })
  });
  const data = await res.json();
  if (!res.ok) {
    const errorMsg = data?.detail || 'Authentication failed.';
    const err = new Error(errorMsg);
    err.status = res.status;
    err.detail = errorMsg;
    throw err;
  }
  if (data.access_token) {
    setAdminToken(data.access_token);
  }
  return data;
}

export async function adminLogout() {
  try {
    await fetch(`${API_BASE_URL}/api/v1/admin/logout`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
  } catch {}
  setAdminToken(null);
}

export async function checkAdminSession() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/session`, {
      headers: getAuthHeaders()
    });
    return res.ok;
  } catch {
    return false;
  }
}

// ==============================================================================
// ADMIN COMMAND CENTER LIVE CRUD
// ==============================================================================

export async function fetchAdminOverview() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/overview`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] fetchAdminOverview error:', err.message);
    return null;
  }
}

export async function fetchSponsorAnalytics() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/analytics/sponsors`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] fetchSponsorAnalytics error:', err.message);
    return null;
  }
}

export async function fetchSpiderHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/health`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] fetchSpiderHealth error:', err.message);
    return null;
  }
}

export async function triggerRunAllSpiders(simulate = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/run?simulate=${simulate}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] triggerRunAllSpiders error:', err.message);
    return null;
  }
}

export async function triggerProductScrape(productId, simulate = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/run/${productId}?simulate=${simulate}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] triggerProductScrape error:', err.message);
    return null;
  }
}

export async function triggerOfferScrape(offerId, simulate = true) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/offer/${offerId}?simulate=${simulate}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('[JaChai API] triggerOfferScrape error:', err.message);
    return null;
  }
}

// Billboard CRUD
export async function apiCreateBillboard(billboardData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/billboards`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(billboardData)
  });
  return await res.json();
}

export async function apiUpdateBillboard(id, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/billboards/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  return await res.json();
}

export async function apiDeleteBillboard(id) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/billboards/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return await res.json();
}

// Spotlight Card CRUD
export async function apiUpdateSpotlight(id, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/spotlights/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  return await res.json();
}

// Tickers CRUD
export async function apiCreateTicker(tickerData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/tickers`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(tickerData)
  });
  return await res.json();
}

export async function apiDeleteTicker(id) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/tickers/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return await res.json();
}

export async function apiUpdateTickerSpeed(glideSpeedSec) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/tickers/speed`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ glide_speed_sec: glideSpeedSec })
  });
  return await res.json();
}

// Macro Commodity Scraper (Live Gold & Oil)
export async function apiFetchMacroTicker() {
  const res = await fetch(`${API_BASE_URL}/api/v1/macro-ticker`);
  if (!res.ok) throw new Error('Failed to fetch macro ticker data');
  return await res.json();
}

export async function apiRunMacroScraper(payload = { live_scrape: true }) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/scrape-macro`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || 'Failed to run macro commodity scraper');
  }
  return await res.json();
}

export async function apiUpdateMacroTicker(updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/refresh-ticker`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  if (!res.ok) throw new Error('Failed to update macro ticker');
  return await res.json();
}

// Product Catalog CRUD
export async function apiCreateProduct(productData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/products`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(productData)
  });
  return await res.json();
}

export async function apiUpdateProduct(id, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/products/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  return await res.json();
}

export async function apiDeleteProduct(id) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/products/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return await res.json();
}

// Store Offers CRUD
export async function apiCreateOffer(offerData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/offers`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(offerData)
  });
  return await res.json();
}

export async function apiUpdateOffer(id, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/offers/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData)
  });
  return await res.json();
}

export async function apiDeleteOffer(id) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/offers/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  return await res.json();
}

// Leads Status Update
export async function apiUpdateLeadStatus(id, newStatus) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/leads/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ status: newStatus })
  });
  return await res.json();
}

// Homepage Blocks (Slots 1-6) CRUD
export async function fetchAdminHomepageBlocks() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-blocks`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiCreateHomepageBlock(blockData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-blocks`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(blockData),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiUpdateHomepageBlock(id, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-blocks/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiDeleteHomepageBlock(id) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-blocks/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// Homepage Slots (Exact 6 Slots Pinning & Ordering) API
export async function fetchAdminHomepageSlots() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-slots`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiSaveHomepageSlot(slotData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-slots`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(slotData),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiUpdateHomepageSlot(slotOrder, updateData) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-slots/${slotOrder}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(updateData),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiDeleteHomepageSlot(slotOrder) {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/homepage-slots/${slotOrder}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// Local Banner & Spotlight Poster File Upload
export async function uploadAdvertiserBanner(file) {
  const token = getAdminToken();
  const formData = new FormData();
  formData.append('file', file);
  const headers = { 'X-Admin-Pin': '2026' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/upload-banner`, {
    method: 'POST',
    headers,
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || `Upload failed with HTTP ${res.status}`);
  }
  return await res.json();
}

// ==============================================================================
// DATA MAPPERS (Backend Schema -> Frontend React State)
// ==============================================================================

export function mapStorefrontData(data) {
  if (!data) return null;

  const normalizeCategory = (cat) => {
    if (cat === 'watches' || cat === 'sneakers') return 'sneakers-watches';
    return cat || 'all';
  };

  const billboards = (data.billboards || []).map((b) => ({
    id: b.id,
    productKey: (b.target_url || '').replace(/^\/+/, '') || 's24-ultra',
    tagEn: b.category_badge ? `SPONSORED · ${b.category_badge}` : 'SPONSORED · CAMPAIGN',
    tagBn: 'স্পন্সরড · ক্যাম্পেইন',
    brandEn: b.sponsor_en,
    brandBn: b.sponsor_bn,
    headlineLightEn: b.headline_en.split('·')[0]?.trim() || b.headline_en,
    headlineBoldEn: b.headline_en.split('·')[1]?.trim() || '',
    headlineBn: b.headline_bn,
    subtextEn: `${b.headline_en} — Starting from ৳${b.starting_price.toLocaleString()}`,
    subtextBn: `${b.headline_bn} — শুরু মাত্র ৳${b.starting_price.toLocaleString()} থেকে`,
    startingPrice: b.starting_price,
    originalPrice: Math.round(b.starting_price * 1.2),
    badgeEn: b.category_badge || 'Featured',
    badgeBn: 'ফিচার্ড',
    image: b.image_url,
    targetUrl: b.target_url,
    expiryDate: b.campaign_end || '2026-12-31',
    isActive: b.is_active !== false,
    impressions: b.impressions || 0,
    clicks: b.clicks || 0
  }));

  const sidePanels = (data.spotlight_cards || []).map((s) => {
    const rawTarget = (s.target_url || '').replace(/^\/+/, '');
    const fallbackKey =
      s.slot_code === 'SLOT #02' ? 'jamdani-saree' :
      s.slot_code === 'SLOT #03' ? 'retro-keyboard' :
      'urban-sneakers';
    return {
      id: s.id,
      slotBadge: s.slot_code || 'SLOT #02',
      productKey: rawTarget || fallbackKey,
      brandEn: s.brand_title_en,
      brandBn: s.brand_title_bn,
      titleEn: s.tagline_en,
      titleBn: s.tagline_bn,
      price: s.starting_price,
      originalPrice: Math.round(s.starting_price * 1.15),
      perkEn: 'Verified Deal',
      perkBn: 'যাচাইকৃত ডিল',
      image: s.image_url,
      targetUrl: s.target_url,
      isActive: s.is_active !== false,
      impressions: s.impressions || 0,
      clicks: s.clicks || 0
    };
  });

  const tickers = (data.ticker_ads || []).map((t) => {
    let brandEn = 'LIVE INDEX';
    let textEn = t.text_en || '';
    if (textEn.includes(':')) {
      const parts = textEn.split(':');
      brandEn = parts[0].trim();
      textEn = parts.slice(1).join(':').trim();
    }
    let brandBn = brandEn;
    let textBn = t.text_bn || '';
    if (textBn.includes(':')) {
      const parts = textBn.split(':');
      brandBn = parts[0].trim();
      textBn = parts.slice(1).join(':').trim();
    }
    const tLow = (t.text_en || '').toLowerCase();
    const targetKey = (tLow.includes('oil') || tLow.includes('soybean') || tLow.includes('mustard'))
      ? 'pure-oil-index'
      : tLow.includes('gold')
      ? 'gold-jewellery'
      : (tLow.includes('saree') || tLow.includes('jamdani'))
      ? 'jamdani-saree'
      : (tLow.includes('watch') || tLow.includes('horology'))
      ? 'luxury-watch'
      : (tLow.includes('keyboard') || tLow.includes('keycraft'))
      ? 'retro-keyboard'
      : (tLow.includes('sneaker') || tLow.includes('urban sole'))
      ? 'urban-sneakers'
      : (tLow.includes('shirt') || tLow.includes('linen'))
      ? 'old-money-shirt'
      : 'gold-jewellery';

    return {
      id: t.id,
      brandEn,
      brandBn,
      textEn,
      textBn,
      targetKey,
      isActive: t.is_active !== false
    };
  });

  const products = (data.products || []).map((p) => {
    const lowest = p.lowest_price;
    const original = p.highest_original_price || Math.round(lowest * 1.15);
    const categoryKey = normalizeCategory(p.category);

    const offers = (p.offers || []).map((o) => ({
      id: o.id,
      store:
        o.source_type === 'f_commerce'
          ? 'F-COMMERCE'
          : o.source_type === 'crawler'
          ? 'WEB STORE'
          : 'VERIFIED STORE',
      subStoreEn: o.store_name,
      subStoreBn: o.store_name,
      termsEn: o.cod_terms_en || 'Cash on Delivery',
      termsBn: o.cod_terms_bn || 'ক্যাশ অন ডেলিভারি',
      price: o.current_price,
      originalPrice: o.original_price,
      warrantyEn: o.warranty_text || 'Official Warranty',
      warrantyBn: o.warranty_text || 'অফিসিয়াল ওয়ারেন্টি',
      url: o.target_url,
      isSponsored: false,
      inStock: o.in_stock,
      spiderStatus: o.spider_status,
      lastSynced: o.last_synced_at
    })).sort((a, b) => a.price - b.price);

    const pastPrices = [
      {
        labelEn: '30d Ago',
        labelBn: '৩০ দিন আগে',
        price: p.price_30d_ago || original
      },
      {
        labelEn: '15d Ago',
        labelBn: '১৫ দিন আগে',
        price: p.price_15d_ago || Math.round((lowest + original) / 2)
      },
      {
        labelEn: 'Today Lowest',
        labelBn: 'আজকে সর্বনিম্ন',
        price: lowest
      }
    ];

    return {
      id: p.id,
      key: p.slug,
      category: categoryKey,
      categoryEn:
        categoryKey === 'fashion'
          ? "Women's & Men's Fashion"
          : categoryKey === 'gadgets'
          ? 'Gadget & Electronics'
          : categoryKey === 'mobiles-computers'
          ? 'Mobile and Computers'
          : categoryKey === 'jewelleries'
          ? 'Jewelleries & Gold'
          : categoryKey === 'snacks-food'
          ? 'Snacks & Food'
          : categoryKey === 'sneakers-watches'
          ? 'Sneakers and Watches'
          : p.category,
      categoryBn:
        categoryKey === 'fashion'
          ? 'ফ্যাশন'
          : categoryKey === 'gadgets'
          ? 'গ্যাজেট ও ইলেকট্রনিক্স'
          : categoryKey === 'mobiles-computers'
          ? 'মোবাইল ও কম্পিউটার'
          : categoryKey === 'jewelleries'
          ? 'জুয়েলারি ও স্বর্ণ'
          : categoryKey === 'snacks-food'
          ? 'স্ন্যাকস ও ফুড'
          : categoryKey === 'sneakers-watches'
          ? 'স্নিকার্স ও ঘড়ি'
          : p.category,
      nameEn: p.title_en,
      nameBn: p.title_bn,
      price: lowest,
      originalPrice: original,
      storeCount: offers.length,
      badgeEn: p.discount_percent > 0 ? `Flat ${p.discount_percent}% Off` : 'Best Deal',
      badgeBn: p.discount_percent > 0 ? `${p.discount_percent}% ছাড়` : 'সেরা ডিল',
      statusEn: 'Live Rate Tracked',
      statusBn: 'লাইভ রেট ট্র্যাকড',
      image: p.image_url,
      isPinned: p.is_pinned_homepage !== false,
      pastPrices,
      offers
    };
  });

  const trendingHubs = (data.trending_hubs || []).map((h) => ({
    id: h.id,
    titleEn: h.title_en,
    titleBn: h.title_bn,
    subtitleEn: h.subtitle_en,
    subtitleBn: h.subtitle_bn,
    queryTrigger: h.query_trigger,
    badgeEn: h.badge_en,
    badgeBn: h.badge_bn,
    iconName: h.icon_name,
    startingPrice: h.starting_price_bdt,
    image: h.image_url,
  }));

  const homepageBlocks = (data.homepage_blocks || []).map((b) => ({
    id: b.id,
    slotOrder: b.slot_order,
    titleEn: b.title_en,
    titleBn: b.title_bn,
    subtitleEn: b.subtitle_en,
    subtitleBn: b.subtitle_bn,
    queryTrigger: b.search_query,
    category: b.category,
    image: b.image_url,
    badgeEn: b.badge_text || 'HOT COMPARE',
    badgeBn: b.badge_text || 'হট কম্পেয়ার',
    startingPrice: b.starting_price_bdt,
    isActive: b.is_active,
  }));

  return {
    billboards: billboards.length > 0 ? billboards : undefined,
    sidePanels: sidePanels.length > 0 ? sidePanels : undefined,
    tickers: tickers.length > 0 ? tickers : undefined,
    tickerSpeed: data.glide_speed_sec || 55,
    products: products.length > 0 ? products : undefined,
    trendingHubs: trendingHubs.length > 0 ? trendingHubs : undefined,
    homepageBlocks: homepageBlocks.length > 0 ? homepageBlocks : undefined,
  };
}

export function mapProductItem(p) {
  if (!p) return null;
  const lowest = p.lowest_price || (p.offers && p.offers.length > 0 ? Math.min(...p.offers.map(o => o.current_price)) : 0);
  const original = p.highest_original_price || Math.round(lowest * 1.15);

  const offers = (p.offers || []).map((o) => {
    const orig = o.original_price || Math.round(o.current_price * 1.15);
    const discPct = o.discount_pct || (orig > o.current_price ? Math.round(((orig - o.current_price) / orig) * 100) : null);
    const discTag = o.discount_tag || (discPct && discPct >= 5 ? `${discPct}% OFF` : null);
    const isPre = o.is_preseeded !== false;
    const web = o.website_url || (o.target_url && !o.target_url.includes('facebook.com') ? o.target_url : null);
    const fb = o.facebook_url || (o.target_url && o.target_url.includes('facebook.com') ? o.target_url : null);

    return {
      id: o.id,
      store:
        o.source_type === 'f_commerce'
          ? 'F-COMMERCE'
          : o.source_type === 'crawler'
          ? 'WEB STORE'
          : 'VERIFIED STORE',
      subStoreEn: o.store_name,
      subStoreBn: o.store_name,
      termsEn: o.cod_terms_en || 'Cash on Delivery Available',
      termsBn: o.cod_terms_bn || 'ক্যাশ অন ডেলিভারি প্রযোজ্য',
      price: o.current_price,
      originalPrice: orig,
      warrantyEn: o.warranty_text || 'Official Warranty',
      warrantyBn: o.warranty_text || 'অফিসিয়াল ওয়ারেন্টি',
      url: o.target_url || web || fb,
      websiteUrl: web,
      facebookUrl: fb,
      isPreseeded: isPre,
      trustScore: o.trust_score || (isPre ? 96 : 78),
      trustBadge: o.trust_badge || (isPre ? '✓ 98% Verified Safe' : 'Market Verified'),
      riskLevel: o.risk_level || (isPre ? 'low' : 'moderate'),
      discountTag: discTag,
      discountPct: discPct,
      isSponsored: Boolean(o.is_sponsored),
      inStock: o.in_stock !== false,
      spiderStatus: o.spider_status || 'healthy',
      lastSynced: o.last_synced_at || 'Just now',
    };
  }).sort((a, b) => {
    if (a.isSponsored !== b.isSponsored) {
      return a.isSponsored ? -1 : 1;
    }
    if (a.isPreseeded !== b.isPreseeded) {
      return a.isPreseeded ? -1 : 1;
    }
    return a.price - b.price;
  });

  const pastPrices = [
    {
      labelEn: '30d Ago',
      labelBn: '৩০ দিন আগে',
      price: p.price_30d_ago || original,
    },
    {
      labelEn: '15d Ago',
      labelBn: '১৫ দিন আগে',
      price: p.price_15d_ago || Math.round((lowest + original) / 2),
    },
    {
      labelEn: 'Today Lowest',
      labelBn: 'আজকে সর্বনিম্ন',
      price: lowest,
    },
  ];

  const isBrowse = Boolean((p.slug && p.slug.startsWith('browse-')) || (p.specs_summary && p.specs_summary.includes('Starts from')));
  const badgeEn = isBrowse ? 'Starts From' : (p.discount_percent > 0 ? `Flat ${p.discount_percent}% Off` : 'Best Deal');
  const badgeBn = isBrowse ? 'শুরু এখান থেকে' : (p.discount_percent > 0 ? `${p.discount_percent}% ছাড়` : 'সেরা ডিল');

  return {
    id: p.id,
    key: p.slug,
    category: p.category || 'all',
    categoryEn: p.category || 'Curated',
    categoryBn: p.category || 'সেরা ডিল',
    nameEn: p.title_en,
    nameBn: p.title_bn,
    price: lowest,
    originalPrice: original,
    storeCount: offers.length,
    badgeEn,
    badgeBn,
    statusEn: isBrowse ? 'Starts From Live Stores' : 'Live Rate Tracked',
    statusBn: isBrowse ? 'শুরু লাইভ স্টোর থেকে' : 'লাইভ রেট ট্র্যাকড',
    image: p.image_url,
    isPinned: p.is_pinned_homepage !== false,
    isBrowse,
    pastPrices,
    offers,
  };
}

// ==============================================================================
// DYNAMIC REGISTRY ADMIN API
// ==============================================================================

export async function fetchAdminRegistryStatus() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/registry/status`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function apiReloadAdminRegistry() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/registry/reload`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// ==============================================================================
// PRE-WARM HARVESTER ADMIN API
// ==============================================================================

export async function triggerPrewarmCrawler() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/prewarm`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function fetchPrewarmStatus() {
  const res = await fetch(`${API_BASE_URL}/api/v1/admin/crawler/prewarm-status`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// ==============================================================================
// STORE LEADERBOARD & MERCHANT TRUST INDEX API
// ==============================================================================

export async function fetchLeaderboard(category = 'all', pillar = 'price', limit = 25) {
  const params = new URLSearchParams({
    category: category || 'all',
    pillar: pillar || 'price',
    limit: String(limit || 25),
  });
  const res = await fetch(`${API_BASE_URL}/api/v1/leaderboard?${params.toString()}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}




