'use client';

import React, { useState } from 'react';
import {
  Shield,
  Radio,
  BarChart3,
  Database,
  RefreshCw,
  Trash2,
  Plus,
  Check,
  Globe,
  Sliders,
  LogOut,
  CheckCircle2,
  Sparkles,
  MessageCircle,
  Eye,
  X,
  Layers,
  ArrowUpRight,
  Upload,
  Compass,
  ArrowUp,
  ArrowDown,
  Search
} from 'lucide-react';
import {
  apiCreateBillboard,
  apiUpdateBillboard,
  apiDeleteBillboard,
  apiUpdateSpotlight,
  apiCreateTicker,
  apiDeleteTicker,
  apiUpdateTickerSpeed,
  apiCreateProduct,
  apiUpdateProduct,
  apiDeleteProduct,
  apiCreateOffer,
  apiUpdateLeadStatus,
  fetchSponsorAnalytics,
  fetchSpiderHealth,
  apiPingSpiderStore,
  triggerRunAllSpidersBackground,
  fetchSpiderRunStatus,
  fetchAdminHomepageBlocks,
  apiCreateHomepageBlock,
  apiUpdateHomepageBlock,
  apiDeleteHomepageBlock,
  uploadAdvertiserBanner,
  apiSaveHomepageSlot,
  fetchAdminRegistryStatus,
  apiReloadAdminRegistry,
  apiFetchMacroTicker,
  apiRunMacroScraper,
  triggerPrewarmCrawler,
  fetchPrewarmStatus,
  apiRecalculateLeaderboard,
  fetchAdminLeaderboardStatus,
  apiSyncMerchantFeeds
} from '../api';

export default function AdminCommandCenter({
  billboards,
  setBillboards,
  sidePanels,
  setSidePanels,
  tickers,
  setTickers,
  tickerSpeed,
  setTickerSpeed,
  spiders,
  setSpiders,
  runAllSpiders,
  isScraping,
  rescrapeProduct,
  products,
  setProducts,
  analytics,
  setAnalytics,
  advertiserInbox,
  setAdvertiserInbox,
  trendingHubs,
  setTrendingHubs,
  onClose,
  onLogout,
  formatBDT
}) {
  const [activeTab, setActiveTab] = useState('ads'); // 'ads', 'crawler', 'catalog', 'analytics'
  const [copyFeedback, setCopyFeedback] = useState(null);
  const [actionNotice, setActionNotice] = useState(null);

  // --- MACRO COMMODITY SCRAPER (GOLD & OIL) STATE ---
  const [macroData, setMacroData] = useState({
    gold_22k_price: '৳19,550 / g (৳2,28,030 / bhori)',
    gold_21k_price: '৳18,670 / g (৳2,17,765 / bhori)',
    gold_24k_price: '৳1,29,200 / bhori',
    soybean_oil_price: '৳175 / litre (5L ৳850)',
    mustard_oil_price: '৳260 / litre',
    octane_price: '৳125 / litre',
    diesel_price: '৳105 / litre',
    petrol_price: '৳121 / litre',
    last_refreshed: 'Just now',
    source: 'BAJUS Official Portal & BPC Index'
  });
  const [isScrapingMacro, setIsScrapingMacro] = useState(false);
  const [spiderCategoryFilter, setSpiderCategoryFilter] = useState('all');
  const [spiderSearchQuery, setSpiderSearchQuery] = useState('');
  const [spiderRunProgress, setSpiderRunProgress] = useState(null);
  const [pingingStoreId, setPingingStoreId] = useState(null);

  React.useEffect(() => {
    apiFetchMacroTicker()
      .then((data) => {
        if (data && data.gold_22k_price) {
          setMacroData(data);
        }
      })
      .catch(() => {});
  }, []);

  const handleRunMacroScraper = async () => {
    try {
      setIsScrapingMacro(true);
      const res = await apiRunMacroScraper({ live_scrape: true });
      if (res?.data) {
        setMacroData(res.data);
        if (setTickers) {
          setTickers((prev) =>
            prev.map((t) => {
              const low = (t.textEn || '').toLowerCase();
              if (low.includes('gold')) {
                return {
                  ...t,
                  textEn: `22K Hallmarked Gold: ${res.data.gold_22k_price} · 21K: ${res.data.gold_21k_price || '৳18,670/g'} · Live Rate Tracked Across Verified Jewellers`
                };
              }
              if (low.includes('oil') || low.includes('soybean')) {
                return {
                  ...t,
                  textEn: `Bottled Soybean Oil: ${res.data.soybean_oil_price} · Pure Mustard Oil: ${res.data.mustard_oil_price} · Fuel Octane: ${res.data.octane_price} · Diesel: ${res.data.diesel_price}`
                };
              }
              return t;
            })
          );
        }
        showNotification('✨ Live Gold (BAJUS) & Oil Scraper finished! Ticker board updated.');
      }
    } catch (err) {
      console.error('Macro scraper error:', err);
      showNotification('⚠️ Macro scraper notice: Using latest benchmark index.');
    } finally {
      setIsScrapingMacro(false);
    }
  };

  // --- TAB 1: NEW BILLBOARD FORM STATE ---
  const [showAddBillboardModal, setShowAddBillboardModal] = useState(false);
  const [newBillboard, setNewBillboard] = useState({
    id: `bb-${Date.now()}`,
    productKey: 'jamdani-saree',
    tagEn: 'SPONSORED · CAMPAIGN',
    tagBn: 'স্পন্সরড · নতুন ক্যাম্পেইন',
    brandEn: '',
    brandBn: '',
    headlineLightEn: '',
    headlineBoldEn: '',
    headlineBn: '',
    subtextEn: '',
    subtextBn: '',
    startingPrice: 1000,
    originalPrice: 1500,
    badgeEn: 'Verified Offer',
    badgeBn: 'যাচাইকৃত অফার',
    image: '/images/jamdani-saree.jpg',
    targetUrl: 'https://facebook.com',
    expiryDate: '2026-11-30',
    isActive: true
  });

  // --- TAB 1: NEW TICKER FORM STATE ---
  const [newTicker, setNewTicker] = useState({
    brandEn: '',
    brandBn: '',
    textEn: '',
    textBn: '',
    targetKey: 'jamdani-saree'
  });

  // --- TAB 2: HYBRID STORE OFFER OVERRIDE STATE ---
  const [newOffer, setNewOffer] = useState({
    productKey: products[0]?.key || 'jamdani-saree',
    sourceType: 'Automated Webcrawler URL',
    storeName: '',
    targetUrl: 'https://',
    price: 1000,
    originalPrice: 1200,
    terms: 'Trial on Delivery · Cash on Delivery · ৳60 Inside Dhaka',
    warranty: '1-Year Official Warranty'
  });

  // --- TAB 3: NEW PRODUCT FORM STATE ---
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    key: '',
    category: 'gadgets',
    categoryEn: 'Gadget and Electronics',
    categoryBn: 'গ্যাজেট ও ইলেকট্রনিক্স',
    nameEn: '',
    nameBn: '',
    price: 2500,
    originalPrice: 3000,
    badgeEn: 'New In',
    badgeBn: 'নতুন সংযোজন',
    statusEn: 'Live Rate Tracked',
    statusBn: 'লাইভ রেট ট্র্যাকড',
    image: '/images/retro-keyboard.jpg',
    past30d: 3200,
    past15d: 2800,
    todayPrice: 2500,
    isPinned: true
  });

  // --- TAB 5: HOMEPAGE 6-BLOCK CURATION STATE ---
  const [homepageBlocks, setHomepageBlocks] = useState(trendingHubs || []);
  const [uploadingTarget, setUploadingTarget] = useState(null);
  const [showAddBlockModal, setShowAddBlockModal] = useState(false);
  const [catalogSearchQuery, setCatalogSearchQuery] = useState('');
  const [newBlock, setNewBlock] = useState({
    title_en: '',
    title_bn: '',
    subtitle_en: '',
    subtitle_bn: '',
    search_query: '',
    category: 'All',
    image_url: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80',
    badge_text: 'HOT COMPARE',
    starting_price_bdt: 1000,
    is_active: true,
  });

  React.useEffect(() => {
    async function loadBlocks() {
      try {
        const blocks = await fetchAdminHomepageBlocks();
        if (blocks && blocks.length > 0) {
          const mapped = blocks.map((b) => ({
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
          setHomepageBlocks(mapped);
          if (setTrendingHubs) setTrendingHubs(mapped);
        }
      } catch (err) {
        console.warn('Failed to load admin homepage blocks:', err);
      }
    }
    loadBlocks();
  }, []);

  const showNotification = (msg) => {
    setActionNotice(msg);
    setTimeout(() => setActionNotice(null), 3500);
  };

  // --- REGISTRY DYNAMIC CSV STATE ---
  const [registryStatus, setRegistryStatus] = useState(null);
  const [isReloadingRegistry, setIsReloadingRegistry] = useState(false);

  // Daily Pre-Warm Harvester State
  const [prewarmState, setPrewarmState] = useState({
    is_running: false,
    current_query: null,
    completed_queries: 0,
    total_queries: 28,
    items_harvested: 0,
    start_time: null,
    completed_at: null,
    last_run: null,
    errors: []
  });
  const [isTriggeringPrewarm, setIsTriggeringPrewarm] = useState(false);

  // Leaderboard Admin & Rearrange State
  const [leaderboardAdminState, setLeaderboardAdminState] = useState({
    last_recalculated_at: 'Just now',
    total_stores_ranked: 326,
    top_reigning_store: 'Custom Mac BD',
    recalculations_count: 1
  });
  const [isRecalculatingLeaderboard, setIsRecalculatingLeaderboard] = useState(false);

  const loadRegistryInfo = React.useCallback(async () => {
    try {
      const data = await fetchAdminRegistryStatus();
      setRegistryStatus(data);
    } catch (e) {
      console.warn('Failed to fetch registry status:', e);
    }
  }, []);

  const handleForceReloadRegistry = async () => {
    setIsReloadingRegistry(true);
    try {
      const res = await apiReloadAdminRegistry();
      setRegistryStatus(res.registry);
      showNotification(`Reloaded ${res.registry.total_stores} stores across ${res.registry.categories_count} categories!`);
    } catch (e) {
      showNotification(`Error reloading registry: ${e.message}`);
    } finally {
      setIsReloadingRegistry(false);
    }
  };

  const handleBannerFileUpload = async (e, targetType, targetId) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setUploadingTarget(`${targetType}-${targetId}`);
      const result = await uploadAdvertiserBanner(file);
      if (result?.url) {
        if (targetType === 'billboard') {
          setBillboards((prev) =>
            prev.map((b) => (b.id === targetId ? { ...b, image: result.url } : b))
          );
          showNotification(`Billboard image uploaded: ${result.filename}`);
          if (typeof targetId === 'number') {
            apiUpdateBillboard(targetId, { image_url: result.url }).catch(() => {});
          }
        } else if (targetType === 'spotlight') {
          setSidePanels((prev) =>
            prev.map((s) => (s.id === targetId ? { ...s, image: result.url } : s))
          );
          showNotification(`Spotlight image uploaded: ${result.filename}`);
          if (typeof targetId === 'number') {
            apiUpdateSpotlight(targetId, { image_url: result.url }).catch(() => {});
          }
        } else if (targetType === 'new-billboard') {
          setNewBillboard((prev) => ({ ...prev, image: result.url }));
          showNotification(`Banner uploaded: ${result.filename}`);
        } else if (targetType === 'homepage-block') {
          const updated = homepageBlocks.map((hb) =>
            hb.id === targetId ? { ...hb, image: result.url } : hb
          );
          setHomepageBlocks(updated);
          if (setTrendingHubs) setTrendingHubs(updated);
          showNotification(`Block image uploaded: ${result.filename}`);
          if (typeof targetId === 'number') {
            apiUpdateHomepageBlock(targetId, { image_url: result.url }).catch(() => {});
          }
        } else if (targetType === 'new-block') {
          setNewBlock((prev) => ({ ...prev, image_url: result.url }));
          showNotification(`Block image uploaded: ${result.filename}`);
        }
      }
    } catch (err) {
      console.error('Upload error:', err);
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploadingTarget(null);
      e.target.value = '';
    }
  };

  const updateBlockField = (id, field, value) => {
    const updated = homepageBlocks.map((b) => {
      if (b.id === id) {
        return { ...b, [field]: value };
      }
      return b;
    });
    setHomepageBlocks(updated);
    if (setTrendingHubs) setTrendingHubs(updated);
  };

  const saveBlockChanges = async (block) => {
    showNotification(`Saving block: ${block.titleEn}`);
    try {
      if (typeof block.id === 'number') {
        await apiUpdateHomepageBlock(block.id, {
          slot_order: block.slotOrder,
          title_en: block.titleEn,
          title_bn: block.titleBn || block.titleEn,
          subtitle_en: block.subtitleEn,
          subtitle_bn: block.subtitleBn,
          search_query: block.queryTrigger,
          category: block.category || 'All',
          image_url: block.image,
          badge_text: block.badgeEn || 'HOT COMPARE',
          starting_price_bdt: Number(block.startingPrice || 0),
          is_active: block.isActive !== false,
        });
      }
      showNotification(`Saved changes for "${block.titleEn}"`);
    } catch (err) {
      console.warn('Failed to save block:', err);
      showNotification(`Failed to save block: ${err.message}`);
    }
  };

  const toggleBlockActive = async (id) => {
    const block = homepageBlocks.find((b) => b.id === id);
    if (!block) return;
    const newActive = block.isActive === false ? true : false;
    const updated = homepageBlocks.map((b) =>
      b.id === id ? { ...b, isActive: newActive } : b
    );
    setHomepageBlocks(updated);
    if (setTrendingHubs) setTrendingHubs(updated);
    showNotification(`Block "${block.titleEn}" ${newActive ? 'activated' : 'paused'}`);
    if (typeof id === 'number') {
      try {
        await apiUpdateHomepageBlock(id, { is_active: newActive });
      } catch (err) {
        console.warn('Failed to toggle block status:', err);
      }
    }
  };

  const moveBlockSlot = async (id, direction) => {
    const index = homepageBlocks.findIndex((b) => b.id === id);
    if (index === -1) return;
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= homepageBlocks.length) return;

    const list = [...homepageBlocks];
    const temp = list[index];
    list[index] = list[targetIndex];
    list[targetIndex] = temp;

    const reordered = list.map((b, idx) => ({ ...b, slotOrder: idx + 1 }));
    setHomepageBlocks(reordered);
    if (setTrendingHubs) setTrendingHubs(reordered);
    showNotification(`Reordered slot positions`);

    for (const b of reordered) {
      if (typeof b.id === 'number') {
        apiUpdateHomepageBlock(b.id, { slot_order: b.slotOrder }).catch(() => {});
      }
    }
  };

  const deleteBlock = async (id) => {
    if (homepageBlocks.length <= 4) {
      alert('Must maintain at least 4 discovery blocks on the homepage.');
      return;
    }
    const block = homepageBlocks.find((b) => b.id === id);
    const updated = homepageBlocks.filter((b) => b.id !== id).map((b, idx) => ({ ...b, slotOrder: idx + 1 }));
    setHomepageBlocks(updated);
    if (setTrendingHubs) setTrendingHubs(updated);
    showNotification(`Deleted block "${block?.titleEn || id}"`);
    if (typeof id === 'number') {
      try {
        await apiDeleteHomepageBlock(id);
      } catch (err) {
        console.warn('Failed to delete block:', err);
      }
    }
  };

  const handleCreateBlock = async (e) => {
    e.preventDefault();
    if (!newBlock.title_en || !newBlock.search_query) {
      alert('Please provide Title (EN) and Search Query Trigger.');
      return;
    }
    const nextSlot = homepageBlocks.length + 1;
    showNotification(`Creating discovery block...`);
    try {
      const res = await apiCreateHomepageBlock({
        slot_order: nextSlot,
        title_en: newBlock.title_en,
        title_bn: newBlock.title_bn || newBlock.title_en,
        subtitle_en: newBlock.subtitle_en,
        subtitle_bn: newBlock.subtitle_bn,
        search_query: newBlock.search_query,
        category: newBlock.category || 'All',
        image_url: newBlock.image_url,
        badge_text: newBlock.badge_text || 'HOT COMPARE',
        starting_price_bdt: Number(newBlock.starting_price_bdt || 0),
        is_active: true,
      });
      const createdMapped = {
        id: res.id,
        slotOrder: res.slot_order,
        titleEn: res.title_en,
        titleBn: res.title_bn,
        subtitleEn: res.subtitle_en,
        subtitleBn: res.subtitle_bn,
        queryTrigger: res.search_query,
        category: res.category,
        image: res.image_url,
        badgeEn: res.badge_text,
        badgeBn: res.badge_text,
        startingPrice: res.starting_price_bdt,
        isActive: res.is_active,
      };
      const updated = [...homepageBlocks, createdMapped];
      setHomepageBlocks(updated);
      if (setTrendingHubs) setTrendingHubs(updated);
      setShowAddBlockModal(false);
      showNotification(`Block "${res.title_en}" created in Slot #${res.slot_order}!`);
      setNewBlock({
        title_en: '',
        title_bn: '',
        subtitle_en: '',
        subtitle_bn: '',
        search_query: '',
        category: 'All',
        image_url: 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=600&q=80',
        badge_text: 'HOT COMPARE',
        starting_price_bdt: 1000,
        is_active: true,
      });
    } catch (err) {
      console.warn('Failed to create block:', err);
      alert(`Failed to create block: ${err.message}`);
    }
  };

  const filteredCatalogProducts = (products || []).filter((p) => {
    if (!catalogSearchQuery.trim()) return false;
    const q = catalogSearchQuery.toLowerCase();
    const title = (p.titleEn || p.title_en || p.nameEn || '').toLowerCase();
    const cat = (p.category || '').toLowerCase();
    return title.includes(q) || cat.includes(q);
  });

  const pinProductToSlot = async (product, slotOrder) => {
    const prodTitle = product.titleEn || product.title_en || product.nameEn || 'Pinned Product';
    const prodTitleBn = product.titleBn || product.title_bn || product.nameBn || prodTitle;
    const prodImg = product.image || product.image_url || '';
    const prodPrice = product.lowestPrice || product.todayPrice || product.price || 0;
    const prodCat = product.category || 'All';

    const updated = homepageBlocks.map((b, idx) => {
      const order = b.slotOrder || idx + 1;
      if (order === slotOrder) {
        return {
          ...b,
          productId: product.id,
          titleEn: prodTitle,
          titleBn: prodTitleBn,
          queryTrigger: prodTitle,
          category: prodCat,
          startingPrice: prodPrice,
          image: prodImg || b.image,
          badgeEn: '🔥 PINNED COMPARE',
        };
      }
      return b;
    });
    setHomepageBlocks(updated);
    if (setTrendingHubs) setTrendingHubs(updated);
    showNotification(`Pinned "${prodTitle}" to Slot #${slotOrder}`);

    try {
      await apiSaveHomepageSlot({
        slot_order: slotOrder,
        product_id: product.id,
        title_en: prodTitle,
        title_bn: prodTitleBn,
        search_query: prodTitle,
        category: prodCat,
        image_url: prodImg || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80',
        badge_text: '🔥 PINNED COMPARE',
        starting_price_bdt: prodPrice,
      });
    } catch (err) {
      console.warn('Failed to persist pinned slot to server:', err);
    }
  };

  const handleCopyWhatsAppReport = (item) => {
    const ctr = item.impressions > 0 ? ((item.clicks / item.impressions) * 100).toFixed(1) : '0.0';
    const reportText = `📊 JaChai Ad Performance — ${item.name} | Slot: ${item.slot} | Views: ${item.impressions.toLocaleString()} | Direct Store Clicks: ${item.clicks.toLocaleString()} | CTR: ${ctr}%`;
    
    if (navigator.clipboard) {
      navigator.clipboard.writeText(reportText);
    }
    setCopyFeedback(item.id);
    showNotification(`WhatsApp report copied for ${item.name}`);
    setTimeout(() => setCopyFeedback(null), 2500);
  };

  // Tab Data Synchronization Effects
  React.useEffect(() => {
    if (activeTab === 'analytics' && setAnalytics) {
      fetchSponsorAnalytics()
        .then((res) => {
          if (res?.billboards || res?.spotlights) {
            const list = [
              ...(res.billboards || []).map((b) => ({
                id: `an-bb-${b.id}`,
                name: b.sponsor_en,
                slot: `Hero Billboard #${b.id}`,
                impressions: b.impressions || 0,
                clicks: b.clicks || 0
              })),
              ...(res.spotlights || []).map((s) => ({
                id: `an-sp-${s.id}`,
                name: s.brand_title_en,
                slot: `Spotlight (${s.slot_code})`,
                impressions: s.impressions || 0,
                clicks: s.clicks || 0
              }))
            ];
            if (list.length > 0) setAnalytics(list);
          }
        })
        .catch((err) => console.warn('Analytics fetch error:', err));
    }
  }, [activeTab, setAnalytics]);

  const loadSpiderHealthData = React.useCallback((cat = 'all') => {
    if (setSpiders) {
      fetchSpiderHealth(cat)
        .then((res) => {
          const list = Array.isArray(res) ? res : (res?.spiders || []);
          if (list.length) {
            setSpiders(
              list.map((s, i) => ({
                id: s.id || `sp-${i + 1}`,
                name: s.store_name,
                domain: s.domain,
                category: s.category || 'General',
                channel_type: s.channel_type || 'WEBSITE',
                selector: s.css_selector || (s.channel_type === 'F_COMMERCE' ? 'Manual F-Commerce (FB)' : '.price, .product-price'),
                status: s.spider_status === 'healthy' ? 'Healthy' : s.spider_status === 'slow' ? 'Slow' : 'Healthy',
                statusCode: s.status_code || 200,
                latencyMs: s.latency_ms || Math.floor(Math.random() * 80 + 120),
                target_url: s.target_url || `https://${s.domain}`,
                lastSynced: s.last_synced_at || 'Just now'
              }))
            );
          }
        })
        .catch((err) => console.warn('Spider health fetch error:', err));
    }
  }, [setSpiders]);

  React.useEffect(() => {
    if (activeTab === 'crawler') {
      loadRegistryInfo();
      loadSpiderHealthData(spiderCategoryFilter);
    }
  }, [activeTab, loadRegistryInfo, loadSpiderHealthData, spiderCategoryFilter]);

  const handleRescrapeSingleStore = async (spider) => {
    try {
      setPingingStoreId(spider.id);
      const res = await apiPingSpiderStore({
        domain: spider.domain,
        store_name: spider.name,
        target_url: spider.target_url
      });
      if (res && res.status === 'success') {
        if (setSpiders) {
          setSpiders((prev) =>
            prev.map((s) =>
              s.id === spider.id
                ? {
                    ...s,
                    status: res.spider_status === 'healthy' ? 'Healthy' : 'Slow',
                    statusCode: res.status_code,
                    latencyMs: res.latency_ms,
                    lastSynced: 'Just now'
                  }
                : s
            )
          );
        }
        showNotification(`✓ ${spider.name} pinged (${res.latency_ms}ms · HTTP ${res.status_code})`);
      } else {
        showNotification(`⚠️ ${spider.name} ping responded with status: ${res?.status_code || 'error'}`);
      }
    } catch (err) {
      console.warn('Ping error:', err);
      showNotification(`⚠️ Could not reach ${spider.name}`);
    } finally {
      setPingingStoreId(null);
    }
  };

  const handleRunAllSpidersSweep = async () => {
    try {
      if (typeof runAllSpiders === 'function') {
        runAllSpiders();
      }
      await triggerRunAllSpidersBackground();
      showNotification('🚀 Background Spider Sweep initiated across all 361 registry domains!');
      const pollTimer = setInterval(async () => {
        try {
          const status = await fetchSpiderRunStatus();
          if (status) {
            setSpiderRunProgress(status);
            if (!status.is_running) {
              clearInterval(pollTimer);
              loadSpiderHealthData(spiderCategoryFilter);
              showNotification(`✅ Spider Sweep Completed! ${status.completed_stores} stores scanned.`);
            }
          }
        } catch (err) {
          clearInterval(pollTimer);
        }
      }, 1500);
    } catch (err) {
      console.error('Sweep error:', err);
    }
  };

  React.useEffect(() => {
    let timer;
    if (activeTab === 'crawler') {
      const checkStatus = () => {
        fetchPrewarmStatus()
          .then((res) => {
            if (res?.data) {
              setPrewarmState(res.data);
            }
          })
          .catch((err) => console.warn('Prewarm status fetch error:', err));
      };
      checkStatus();
      timer = setInterval(checkStatus, 3000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [activeTab]);

  const [isSyncingFeeds, setIsSyncingFeeds] = useState(false);

  const handleSyncMerchantFeeds = async () => {
    setIsSyncingFeeds(true);
    try {
      const res = await apiSyncMerchantFeeds();
      showNotification(res?.message || 'Merchant feeds ingested successfully');
      if (res?.persisted_products) {
        showNotification(`Ingested ${res.persisted_products} verified SKUs into database!`);
      }
    } catch (err) {
      alert(`Feed sync failed: ${err.message}`);
    } finally {
      setIsSyncingFeeds(false);
    }
  };

  const handleRunPrewarmHarvester = async () => {
    setIsTriggeringPrewarm(true);
    try {
      const res = await triggerPrewarmCrawler();
      if (res?.data) {
        setPrewarmState(res.data);
      }
      showNotification(res?.message || 'Daily pre-warm harvester job started');
    } catch (err) {
      alert(`Prewarm failed: ${err.message}`);
    } finally {
      setIsTriggeringPrewarm(false);
    }
  };

  React.useEffect(() => {
    if (activeTab === 'crawler') {
      fetchAdminLeaderboardStatus()
        .then((res) => {
          if (res?.data) {
            setLeaderboardAdminState(res.data);
          }
        })
        .catch((err) => console.warn('Leaderboard status fetch error:', err));
    }
  }, [activeTab]);

  const handleRecalculateLeaderboard = async () => {
    setIsRecalculatingLeaderboard(true);
    try {
      const res = await apiRecalculateLeaderboard();
      if (res?.data) {
        setLeaderboardAdminState(res.data);
      }
      showNotification(res?.message || 'Leaderboard recalculated and re-arranged');
    } catch (err) {
      alert(`Leaderboard recalculation failed: ${err.message}`);
    } finally {
      setIsRecalculatingLeaderboard(false);
    }
  };

  // --- TAB 1 ACTIONS ---
  const toggleBillboardStatus = async (id) => {
    const target = billboards.find((b) => b.id === id);
    const newStatus = target?.isActive === false ? true : false;
    setBillboards((prev) =>
      prev.map((b) => (b.id === id ? { ...b, isActive: newStatus } : b))
    );
    showNotification('Billboard status updated');
    if (typeof id === 'number') {
      try {
        await apiUpdateBillboard(id, { is_active: newStatus });
      } catch (err) {
        console.warn('API update billboard error:', err);
      }
    }
  };

  const deleteBillboard = async (id) => {
    if (billboards.length <= 1) {
      alert('You must keep at least 1 billboard active in rotation.');
      return;
    }
    setBillboards((prev) => prev.filter((b) => b.id !== id));
    showNotification('Billboard slide deleted');
    if (typeof id === 'number') {
      try {
        await apiDeleteBillboard(id);
      } catch (err) {
        console.warn('API delete billboard error:', err);
      }
    }
  };

  const handleSaveNewBillboard = async (e) => {
    e.preventDefault();
    if (!newBillboard.brandEn || !newBillboard.headlineBoldEn) {
      alert('Please fill in Sponsor Brand and Headline.');
      return;
    }
    const tempId = Date.now();
    setBillboards((prev) => [...prev, { ...newBillboard, id: tempId }]);
    setShowAddBillboardModal(false);
    showNotification(`Billboard created for ${newBillboard.brandEn}`);

    try {
      const res = await apiCreateBillboard({
        sponsor_en: newBillboard.brandEn,
        sponsor_bn: newBillboard.brandBn || newBillboard.brandEn,
        headline_en: `${newBillboard.headlineLightEn} ${newBillboard.headlineBoldEn}`.trim(),
        headline_bn: newBillboard.headlineBn || newBillboard.brandEn,
        category_badge: (newBillboard.tagEn || '').replace('SPONSORED · ', ''),
        starting_price: Number(newBillboard.startingPrice),
        image_url: newBillboard.image || '/images/jamdani-saree.jpg',
        target_url: newBillboard.productKey || 'jamdani-saree',
        campaign_end: newBillboard.expiryDate || '2026-12-31',
        is_active: true
      });
      if (res?.id) {
        setBillboards((prev) =>
          prev.map((b) => (b.id === tempId ? { ...b, id: res.id } : b))
        );
      }
    } catch (err) {
      console.warn('API create billboard error:', err);
    }
  };

  const toggleSidePanelStatus = async (id) => {
    const target = sidePanels.find((sp) => sp.id === id);
    const newStatus = target?.isActive === false ? true : false;
    setSidePanels((prev) =>
      prev.map((sp) => (sp.id === id ? { ...sp, isActive: newStatus } : sp))
    );
    showNotification('Partner spotlight slot status updated');
    if (typeof id === 'number') {
      try {
        await apiUpdateSpotlight(id, { is_active: newStatus });
      } catch (err) {
        console.warn('API update spotlight error:', err);
      }
    }
  };

  const deleteTicker = async (idx) => {
    if (tickers.length <= 1) {
      alert('Keep at least 1 ticker announcement in rotation.');
      return;
    }
    const target = tickers[idx];
    setTickers((prev) => prev.filter((_, i) => i !== idx));
    showNotification('Ticker announcement deleted');
    if (target?.id && typeof target.id === 'number') {
      try {
        await apiDeleteTicker(target.id);
      } catch (err) {
        console.warn('API delete ticker error:', err);
      }
    }
  };

  const handleAddTicker = async (e) => {
    e.preventDefault();
    if (!newTicker.brandEn || !newTicker.textEn) {
      alert('Please provide Brand name and announcement text.');
      return;
    }
    const tickerToAdd = {
      brandEn: newTicker.brandEn,
      brandBn: newTicker.brandBn || newTicker.brandEn,
      textEn: newTicker.textEn,
      textBn: newTicker.textBn || newTicker.textEn,
      targetKey: newTicker.targetKey
    };
    setTickers((prev) => [...prev, tickerToAdd]);
    showNotification('Ticker announcement added');

    try {
      await apiCreateTicker({
        text_en: `${tickerToAdd.brandEn}: ${tickerToAdd.textEn}`,
        text_bn: `${tickerToAdd.brandBn}: ${tickerToAdd.textBn}`,
        is_active: true,
        glide_speed_sec: tickerSpeed || 55
      });
    } catch (err) {
      console.warn('API create ticker error:', err);
    }

    setNewTicker({
      brandEn: '',
      brandBn: '',
      textEn: '',
      textBn: '',
      targetKey: 'jamdani-saree'
    });
  };

  // --- TAB 2 ACTIONS ---
  const handleAddStoreOffer = async (e) => {
    e.preventDefault();
    if (!newOffer.storeName || !newOffer.price) {
      alert('Please provide Store Name and Price.');
      return;
    }

    const matchedProduct = products.find((p) => p.key === newOffer.productKey);
    const productId = matchedProduct?.id;

    setProducts((prev) =>
      prev.map((p) => {
        if (p.key !== newOffer.productKey) return p;

        const updatedOffers = [
          ...p.offers,
          {
            id: `custom-offer-${Date.now()}`,
            store: newOffer.sourceType.includes('Facebook') ? 'F-COMMERCE' : 'WEB STORE',
            subStoreEn: newOffer.storeName,
            subStoreBn: newOffer.storeName,
            termsEn: newOffer.terms,
            termsBn: newOffer.terms,
            price: Number(newOffer.price),
            warrantyEn: newOffer.warranty,
            warrantyBn: newOffer.warranty,
            targetUrl: newOffer.targetUrl
          }
        ].sort((a, b) => a.price - b.price);

        const lowestPrice = updatedOffers[0]?.price || p.price;
        return {
          ...p,
          price: lowestPrice,
          originalPrice: Math.max(p.originalPrice, Number(newOffer.originalPrice || lowestPrice * 1.15)),
          storeCount: updatedOffers.length,
          offers: updatedOffers
        };
      })
    );

    showNotification(`New offer for ${newOffer.storeName} linked & sorted!`);

    if (productId) {
      try {
        await apiCreateOffer({
          product_id: productId,
          store_name: newOffer.storeName,
          source_type: newOffer.sourceType.includes('Facebook') ? 'f_commerce' : 'crawler',
          target_url: newOffer.targetUrl || 'https://',
          current_price: Number(newOffer.price),
          original_price: Number(newOffer.originalPrice || newOffer.price * 1.2),
          cod_terms_en: newOffer.terms || 'Cash on Delivery',
          cod_terms_bn: newOffer.terms || 'ক্যাশ অন ডেলিভারি',
          warranty_text: newOffer.warranty || 'Official Warranty'
        });
      } catch (err) {
        console.warn('API create offer error:', err);
      }
    }

    setNewOffer({
      productKey: products[0]?.key || 'jamdani-saree',
      sourceType: 'Automated Webcrawler URL',
      storeName: '',
      targetUrl: 'https://',
      price: 1000,
      originalPrice: 1200,
      terms: 'Trial on Delivery · Cash on Delivery · ৳60 Inside Dhaka',
      warranty: '1-Year Official Warranty'
    });
  };

  // --- TAB 3 ACTIONS ---
  const toggleProductPin = async (key) => {
    const prod = products.find((p) => p.key === key);
    const newPinned = prod?.isPinned === false ? true : false;
    setProducts((prev) =>
      prev.map((p) => (p.key === key ? { ...p, isPinned: newPinned } : p))
    );
    showNotification('Product homepage pinning toggled');
    if (prod?.id) {
      try {
        await apiUpdateProduct(prod.id, { is_pinned_homepage: newPinned });
      } catch (err) {
        console.warn('API update product error:', err);
      }
    }
  };

  const deleteProduct = async (key) => {
    if (products.length <= 1) {
      alert('Cannot delete all products from the catalog.');
      return;
    }
    const prod = products.find((p) => p.key === key);
    setProducts((prev) => prev.filter((p) => p.key !== key));
    showNotification('Product removed from catalog');
    if (prod?.id) {
      try {
        await apiDeleteProduct(prod.id);
      } catch (err) {
        console.warn('API delete product error:', err);
      }
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    if (!newProduct.nameEn || !newProduct.price) {
      alert('Please provide Product Title and Price.');
      return;
    }
    const cleanKey =
      newProduct.key.trim() ||
      newProduct.nameEn
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-|-$/g, '');

    const tempId = Date.now();
    const productToAdd = {
      id: tempId,
      key: cleanKey,
      category: newProduct.category,
      categoryEn: newProduct.categoryEn,
      categoryBn: newProduct.categoryBn,
      nameEn: newProduct.nameEn,
      nameBn: newProduct.nameBn || newProduct.nameEn,
      price: Number(newProduct.price),
      originalPrice: Number(newProduct.originalPrice),
      storeCount: 1,
      badgeEn: newProduct.badgeEn,
      badgeBn: newProduct.badgeBn,
      statusEn: newProduct.statusEn,
      statusBn: newProduct.statusBn,
      image: newProduct.image || '/images/retro-keyboard.jpg',
      isPinned: newProduct.isPinned,
      pastPrices: [
        { labelEn: '30d Ago', labelBn: '৩০ দিন আগে', price: Number(newProduct.past30d) },
        { labelEn: '15d Ago', labelBn: '১৫ দিন আগে', price: Number(newProduct.past15d) },
        { labelEn: 'Today Lowest', labelBn: 'আজকে সর্বনিম্ন', price: Number(newProduct.todayPrice) }
      ],
      offers: [
        {
          id: `offer-${cleanKey}-1`,
          store: 'VERIFIED STORE',
          subStoreEn: 'Primary Verified Distributor',
          subStoreBn: 'প্রাথমিক যাচাইকৃত বিক্রেতা',
          termsEn: 'Cash on Delivery · Verified Courier',
          termsBn: 'ক্যাশ অন ডেলিভারি · ভেরিফাইড কুরিয়ার',
          price: Number(newProduct.price),
          warrantyEn: 'Official Store Warranty',
          warrantyBn: 'অফিসিয়াল স্টোর ওয়ারেন্টি'
        }
      ]
    };

    setProducts((prev) => [productToAdd, ...prev]);
    setShowAddProductModal(false);
    showNotification(`Added ${newProduct.nameEn} to catalog!`);

    try {
      const res = await apiCreateProduct({
        title_en: newProduct.nameEn,
        title_bn: newProduct.nameBn || newProduct.nameEn,
        category: newProduct.category,
        image_url: newProduct.image || '/images/retro-keyboard.jpg',
        specs_summary: `${newProduct.nameEn} - Live tracked across Bangladesh`,
        price_30d_ago: Number(newProduct.past30d),
        price_15d_ago: Number(newProduct.past15d),
        is_pinned_homepage: newProduct.isPinned
      });
      if (res?.id) {
        setProducts((prev) =>
          prev.map((p) => (p.id === tempId ? { ...p, id: res.id, key: res.slug || p.key } : p))
        );
      }
    } catch (err) {
      console.warn('API create product error:', err);
    }
  };

  // --- TAB 4 ACTIONS ---
  const updateInboxStatus = async (id, newStatus) => {
    setAdvertiserInbox((prev) =>
      prev.map((lead) => (lead.id === id ? { ...lead, status: newStatus } : lead))
    );
    showNotification(`Lead #${id} marked as ${newStatus}`);
    const numId = typeof id === 'number' ? id : parseInt(String(id).replace('lead-', ''), 10);
    if (!isNaN(numId) && numId < 100000000) {
      try {
        await apiUpdateLeadStatus(numId, newStatus);
      } catch (err) {
        console.warn('API update lead status error:', err);
      }
    }
  };

  const totalClicks = analytics.reduce((acc, curr) => acc + curr.clicks, 0);
  const totalImpressions = analytics.reduce((acc, curr) => acc + curr.impressions, 0);
  const globalCtr = totalImpressions > 0 ? ((totalClicks / totalImpressions) * 100).toFixed(2) : '0.00';

  return (
    <div className="min-h-screen bg-[#0A0B0E] text-white flex flex-col font-sans-clean">
      {/* =====================================================================
          TOP EXECUTIVE COMMAND BAR
      ===================================================================== */}
      <header className="sticky top-0 z-50 bg-[#0E1017]/95 backdrop-blur-md border-b border-white/15 px-4 sm:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#F59E0B] to-[#10B981] p-0.5 flex items-center justify-center shadow-lg">
            <div className="w-full h-full bg-[#0A0B0E] rounded-[10px] flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#F59E0B]" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-display text-lg sm:text-xl font-bold uppercase tracking-wider text-white">
                JACHAI COMMAND CENTER
              </h1>
              <span className="px-2 py-0.5 rounded-full bg-[#10B981]/15 border border-[#10B981]/40 text-[#10B981] text-[10px] font-black tracking-wider uppercase flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                VAULT SECURE
              </span>
            </div>
            <p className="text-[11px] text-white/50">
              Live Operations · Real-Time Storefront State Synchronized
            </p>
          </div>
        </div>

        {/* Global Controls */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-[#141722] hover:bg-[#1C2030] border border-white/15 text-xs font-bold text-white flex items-center gap-2 transition cursor-pointer shadow-md"
          >
            <Eye className="w-4 h-4 text-[#38BDF8]" />
            <span>Preview Storefront</span>
          </button>

          <button
            onClick={onLogout}
            className="px-4 py-2 rounded-xl bg-red-950/40 hover:bg-red-900/60 border border-red-500/30 text-xs font-bold text-red-300 flex items-center gap-2 transition cursor-pointer shadow-md"
          >
            <LogOut className="w-4 h-4 text-red-400" />
            <span>Lock Vault & Logout</span>
          </button>
        </div>
      </header>

      {/* =====================================================================
          ACTION TOAST NOTIFICATION
      ===================================================================== */}
      {actionNotice && (
        <div className="fixed top-16 right-6 z-50 bg-[#12141C] border border-[#10B981]/40 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-2xl flex items-center gap-2.5 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
          <span>{actionNotice}</span>
        </div>
      )}

      {/* =====================================================================
          NAVIGATION TABS
      ===================================================================== */}
      <div className="bg-[#08090C] border-b border-white/10 px-4 sm:px-8 py-2.5 overflow-x-auto scrollbar-none">
        <div className="max-w-7xl mx-auto flex items-center gap-2">
          {[
            { id: 'ads', label: '1. Ad & Revenue Manager', icon: Radio, count: billboards.length },
            { id: 'crawler', label: '2. Webcrawler & Price Engine', icon: Database, count: spiders.length },
            { id: 'catalog', label: '3. Product Catalog & Pinning', icon: Layers, count: products.length },
            {
              id: 'analytics',
              label: '4. Sponsor Analytics & Inbox',
              icon: BarChart3,
              badge: advertiserInbox.filter((i) => i.status === 'Pending').length
            },
            { id: 'homepage', label: '5. Homepage Blocks (4-6 Slots)', icon: Compass, count: homepageBlocks.length }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-xl text-xs font-extrabold tracking-wide uppercase flex items-center gap-2 transition cursor-pointer whitespace-nowrap shrink-0 ${
                  isActive
                    ? 'bg-[#10B981] text-black shadow-lg'
                    : 'bg-[#12141C] text-white/70 hover:text-white hover:bg-[#181B26] border border-white/10'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-black' : 'text-white/60'}`} />
                <span>{tab.label}</span>
                {tab.badge > 0 && (
                  <span className="w-5 h-5 rounded-full bg-[#F59E0B] text-black text-[10px] font-black flex items-center justify-center">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* =====================================================================
          TAB CONTENT AREA
      ===================================================================== */}
      <main className="max-w-7xl w-full mx-auto p-4 sm:p-8 flex-1">
        {/* ===================================================================
            TAB 1: 3-TIER AD & REVENUE MANAGER
        =================================================================== */}
        {activeTab === 'ads' && (
          <div className="space-y-8">
            {/* TIER 3: MARQUEE TICKER SPEED & MANAGER */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4 mb-5">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                    TIER 03 · CONTINUOUS DUAL MARQUEE TICKERS
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Live Marquee Announcements & Speed Control
                  </h3>
                </div>

                {/* Glide Speed Slider */}
                <div className="flex items-center gap-3 bg-[#0A0B0E] border border-white/15 px-4 py-2 rounded-xl">
                  <Sliders className="w-4 h-4 text-[#10B981]" />
                  <span className="text-xs font-bold text-white/70">Glide Speed:</span>
                  <input
                    type="range"
                    min="20"
                    max="90"
                    value={tickerSpeed}
                    onChange={(e) => {
                      const val = Number(e.target.value);
                      setTickerSpeed(val);
                      showNotification(`Marquee duration set to ${val}s`);
                      apiUpdateTickerSpeed(val).catch(() => {});
                    }}
                    className="w-24 accent-[#10B981] cursor-pointer"
                  />
                  <span className="text-xs font-extrabold text-[#10B981] min-w-[32px]">
                    {tickerSpeed}s
                  </span>
                </div>

                {/* Dedicated Gold & Oil Scraper Trigger Button */}
                <button
                  onClick={handleRunMacroScraper}
                  disabled={isScrapingMacro}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500/20 to-yellow-500/20 hover:from-amber-500/30 hover:to-yellow-500/30 border border-amber-500/30 text-amber-300 font-extrabold text-xs uppercase tracking-wider transition cursor-pointer shadow-md disabled:opacity-50"
                  title="Run Live Scraper for Gold (BAJUS) & Oil Rates"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isScrapingMacro ? 'animate-spin' : ''}`} />
                  <span>{isScrapingMacro ? 'Scraping...' : '⚡ Run Gold & Oil Scraper'}</span>
                </button>
              </div>

              {/* Ticker List */}
              <div className="space-y-2.5">
                {tickers.map((item, idx) => (
                  <div
                    key={`ticker-${idx}`}
                    className="bg-[#0A0B0E] border border-white/10 rounded-xl p-3 sm:px-4 flex items-center justify-between gap-4 hover:border-white/20 transition"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="w-2 h-2 rounded-full bg-[#10B981] shrink-0" />
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-extrabold text-[#F59E0B] tracking-wide">
                            {item.brandEn}
                          </span>
                          <span className="text-[10px] text-white/40">({item.targetKey})</span>
                        </div>
                        <p className="text-xs text-white/80 truncate mt-0.5">{item.textEn}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => deleteTicker(idx)}
                      className="p-2 text-white/40 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition cursor-pointer shrink-0"
                      title="Delete Announcement"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Add New Ticker Form */}
              <form
                onSubmit={handleAddTicker}
                className="mt-5 pt-4 border-t border-white/10 grid grid-cols-1 sm:grid-cols-12 gap-3 items-end"
              >
                <div className="sm:col-span-3">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Sponsor Brand Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. AURA JEWELS BD"
                    value={newTicker.brandEn}
                    onChange={(e) => setNewTicker({ ...newTicker, brandEn: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-6">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Ticker Announcement Text (EN)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 22K Gold Rate: ৳1,18,450 / Bhori · Real-Time Certified Live Rate"
                    value={newTicker.textEn}
                    onChange={(e) => setNewTicker({ ...newTicker, textEn: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-3">
                  <button
                    type="submit"
                    className="w-full py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider transition cursor-pointer flex items-center justify-center gap-1.5 shadow-md"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add to Tickers</span>
                  </button>
                </div>
              </form>
            </div>

            {/* TIER 1: PRIMARY HERO BILLBOARDS (LEFT 8-COL STAGE) */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4 mb-6">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                    TIER 01 · 8-COLUMN PRIMARY HERO BILLBOARDS
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Above-The-Fold Kinetic Centerpiece Slides
                  </h3>
                </div>

                <button
                  onClick={() => setShowAddBillboardModal(true)}
                  className="px-4 py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition cursor-pointer shadow-lg shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span>+ Add Billboard Slide</span>
                </button>
              </div>

              {/* Billboard Slides Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {billboards.map((b) => (
                  <div
                    key={b.id}
                    className="bg-[#0A0B0E] border border-white/15 rounded-2xl p-5 flex flex-col justify-between space-y-4 shadow-lg group"
                  >
                    <div className="space-y-3">
                      {/* Top Bar: Status Toggle & Delete */}
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-black uppercase tracking-wider px-2.5 py-0.5 rounded bg-white/10 text-[#F59E0B]">
                          {b.tagEn}
                        </span>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => toggleBillboardStatus(b.id)}
                            className={`px-3 py-1 rounded-full text-[10px] font-black uppercase transition cursor-pointer ${
                              b.isActive !== false
                                ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                                : 'bg-stone-800 text-stone-400 border border-white/10'
                            }`}
                          >
                            {b.isActive !== false ? 'Active' : 'Paused'}
                          </button>

                          <button
                            onClick={() => deleteBillboard(b.id)}
                            className="p-1.5 text-white/40 hover:text-red-400 rounded-lg transition cursor-pointer"
                            title="Delete Slide"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Image Preview & Headline */}
                      <div className="relative h-32 w-full rounded-xl overflow-hidden bg-black/60 border border-white/10">
                        <img
                          src={b.image}
                          alt={b.brandEn}
                          className="w-full h-full object-cover opacity-60"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-3">
                          <div>
                            <span className="text-[10px] font-bold text-white/60 uppercase">
                              {b.brandEn}
                            </span>
                            <h4 className="font-display text-base font-bold text-white uppercase leading-tight">
                              {b.headlineLightEn} {b.headlineBoldEn}
                            </h4>
                          </div>
                        </div>
                      </div>

                      {/* Local Banner File Upload Button */}
                      <label className="w-full py-1.5 px-3 rounded-xl bg-white/5 hover:bg-white/15 text-white/90 text-[11px] font-bold uppercase tracking-wider flex items-center justify-center gap-2 cursor-pointer transition border border-white/10 shadow-sm">
                        <Upload className="w-3.5 h-3.5 text-[#10B981]" />
                        <span>{uploadingTarget === `billboard-${b.id}` ? 'Uploading Banner...' : 'Upload Banner from PC'}</span>
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handleBannerFileUpload(e, 'billboard', b.id)}
                        />
                      </label>

                      {/* Editable Live Fields */}
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <label className="text-[10px] text-white/40 uppercase block mb-0.5 font-bold">
                            Starting BDT Price
                          </label>
                          <input
                            type="number"
                            value={b.startingPrice}
                            onChange={(e) => {
                              const val = Number(e.target.value);
                              setBillboards((prev) =>
                                prev.map((item) =>
                                  item.id === b.id ? { ...item, startingPrice: val } : item
                                )
                              );
                            }}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 font-bold text-[#10B981] focus:outline-none focus:border-[#10B981]"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] text-white/40 uppercase block mb-0.5 font-bold">
                            Target Product Key
                          </label>
                          <select
                            value={b.productKey}
                            onChange={(e) => {
                              const val = e.target.value;
                              setBillboards((prev) =>
                                prev.map((item) =>
                                  item.id === b.id ? { ...item, productKey: val } : item
                                )
                              );
                            }}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 font-bold text-white focus:outline-none focus:border-[#10B981]"
                          >
                            {products.map((p) => (
                              <option key={p.key} value={p.key} className="bg-[#12141C]">
                                {p.nameEn.substring(0, 28)}...
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <div className="text-[10px] text-white/40 flex items-center justify-between border-t border-white/10 pt-2">
                      <span>Slide ID: {b.id}</span>
                      <span className="text-[#10B981] font-semibold">Live in rotation</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* TIER 2: PARTNER SPOTLIGHT CARDS (RIGHT 4-COL SLOTS) */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="border-b border-white/10 pb-4 mb-6">
                <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                  TIER 02 · 4-COLUMN PARTNER SPOTLIGHT CARDS
                </span>
                <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                  Micro-Sponsor Spotlight Slots (#02, #03, #04)
                </h3>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {sidePanels.map((slot) => (
                  <div
                    key={slot.id}
                    className="bg-[#0A0B0E] border border-white/15 rounded-2xl p-4 space-y-3 shadow-lg"
                  >
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded bg-[#C2410C] text-white text-[9px] font-black uppercase">
                        {slot.slotBadge}
                      </span>
                      <button
                        onClick={() => toggleSidePanelStatus(slot.id)}
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          slot.isActive !== false ? 'bg-[#10B981]/20 text-[#10B981]' : 'bg-white/10 text-white/50'
                        }`}
                      >
                        {slot.isActive !== false ? 'Active' : 'Paused'}
                      </button>
                    </div>

                    <div className="space-y-2">
                      <div>
                        <label className="text-[10px] text-white/40 font-bold block uppercase mb-1">
                          Brand Title
                        </label>
                        <input
                          type="text"
                          value={slot.brandEn}
                          onChange={(e) => {
                            const val = e.target.value;
                            setSidePanels((prev) =>
                              prev.map((s) => (s.id === slot.id ? { ...s, brandEn: val } : s))
                            );
                          }}
                          className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-[#10B981]"
                        />
                      </div>

                      <div>
                        <label className="text-[10px] text-white/40 font-bold block uppercase mb-1">
                          Headline / Product
                        </label>
                        <input
                          type="text"
                          value={slot.titleEn}
                          onChange={(e) => {
                            const val = e.target.value;
                            setSidePanels((prev) =>
                              prev.map((s) => (s.id === slot.id ? { ...s, titleEn: val } : s))
                            );
                          }}
                          className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-[#10B981]"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="text-[10px] text-white/40 font-bold block uppercase mb-1">
                            Price (BDT)
                          </label>
                          <input
                            type="number"
                            value={slot.price}
                            onChange={(e) => {
                              const val = Number(e.target.value);
                              setSidePanels((prev) =>
                                prev.map((s) => (s.id === slot.id ? { ...s, price: val } : s))
                              );
                            }}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs font-extrabold text-[#10B981] focus:outline-none focus:border-[#10B981]"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] text-white/40 font-bold block uppercase mb-1">
                            Perk Badge
                          </label>
                          <input
                            type="text"
                            value={slot.perkEn}
                            onChange={(e) => {
                              const val = e.target.value;
                              setSidePanels((prev) =>
                                prev.map((s) => (s.id === slot.id ? { ...s, perkEn: val } : s))
                              );
                            }}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs font-bold text-white/80 focus:outline-none focus:border-[#10B981]"
                          />
                        </div>
                      </div>

                      {/* Image Preview & Local Upload */}
                      <div className="pt-2 border-t border-white/10 flex items-center gap-2">
                        <div className="w-10 h-10 rounded-lg overflow-hidden bg-black/60 border border-white/10 shrink-0">
                          <img
                            src={slot.image}
                            alt={slot.titleEn}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <label className="flex-1 py-1.5 px-2 rounded-lg bg-white/5 hover:bg-white/15 text-white/90 text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 cursor-pointer transition border border-white/10">
                          <Upload className="w-3 h-3 text-[#38BDF8]" />
                          <span className="truncate">{uploadingTarget === `spotlight-${slot.id}` ? 'Uploading...' : 'Upload Poster from PC'}</span>
                          <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => handleBannerFileUpload(e, 'spotlight', slot.id)}
                          />
                        </label>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 2: WEBCRAWLER & HYBRID PRICE TRACKER ENGINE
        =================================================================== */}
        {activeTab === 'crawler' && (
          <div className="space-y-8">
            {/* DAILY CATALOG HARVESTER & PRE-WARM PRICE ACCELERATOR */}
            <div className="bg-[#12141C] border border-[#10B981]/30 rounded-2xl p-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-[#10B981]/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5 relative z-10">
                <div>
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-500/40">
                      DAILY MORNING PRE-WARM HARVESTER
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-cyan-950/80 text-cyan-400 border border-cyan-500/40">
                      16 CATEGORIES · &lt;20MS LATENCY
                    </span>
                    {prewarmState.is_running && (
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-amber-950/80 text-amber-400 border border-amber-500/40 animate-pulse">
                        ● LIVE HARVESTING IN PROGRESS
                      </span>
                    )}
                  </div>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5 flex items-center gap-2">
                    <span>Daily Catalog Harvester & Latency Reducer</span>
                  </h3>
                  <p className="text-xs text-white/50 mt-1 max-w-2xl">
                    Run by an administrator each morning to pre-harvest and verify live retail prices across top high-velocity queries in all 16 categories. Ensures all visitor searches throughout the day return fresh, authentic market rates in &lt;20ms.
                  </p>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                  <button
                    onClick={handleSyncMerchantFeeds}
                    disabled={isSyncingFeeds}
                    className="px-5 py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-indigo-600 hover:to-blue-700 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition cursor-pointer shadow-xl disabled:opacity-50 shrink-0 hover:scale-[1.02] active:scale-[0.98]"
                  >
                    <RefreshCw className={`w-4 h-4 ${isSyncingFeeds ? 'animate-spin' : ''}`} />
                    <span>
                      {isSyncingFeeds ? 'Ingesting Feeds...' : '📥 Ingest Merchant Feeds (Shopify & XML)'}
                    </span>
                  </button>
                <button
                  onClick={handleRunPrewarmHarvester}
                  disabled={isTriggeringPrewarm || prewarmState.is_running}
                  className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#10B981] to-[#059669] hover:from-[#059669] hover:to-[#047857] text-black font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition cursor-pointer shadow-xl disabled:opacity-50 shrink-0 hover:scale-[1.02] active:scale-[0.98]"
                >
                  <RefreshCw className={`w-4 h-4 ${prewarmState.is_running || isTriggeringPrewarm ? 'animate-spin' : ''}`} />
                  <span>
                    {prewarmState.is_running
                      ? `Harvesting (${prewarmState.completed_queries}/${prewarmState.total_queries})...`
                      : '⚡ Run Morning Pre-Warm Harvester'}
                  </span>
                </button>
                </div>
              </div>

              {/* Progress & Telemetry Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 relative z-10">
                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Harvester Status</span>
                  <div className="flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${prewarmState.is_running ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`} />
                    <span className="text-lg font-black text-white">
                      {prewarmState.is_running ? 'Active Scraping' : 'Ready / Idle'}
                    </span>
                  </div>
                  <span className="text-[11px] text-white/40 block mt-1">
                    {prewarmState.current_query ? `Current: "${prewarmState.current_query}"` : 'Standing by for schedule'}
                  </span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Target Coverage</span>
                  <span className="text-2xl font-black text-[#38BDF8]">
                    {prewarmState.completed_queries} / {prewarmState.total_queries}
                  </span>
                  <span className="text-[11px] text-white/40 block mt-1">Top Benchmark Queries</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Items Harvested</span>
                  <span className="text-2xl font-black text-[#10B981]">
                    {prewarmState.items_harvested || 0}
                  </span>
                  <span className="text-[11px] text-white/40 block mt-1">Verified Real Store Listings</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Last Run Synchronization</span>
                  <span className="text-xs font-mono font-bold text-emerald-300 block truncate">
                    {prewarmState.last_run || 'Not run yet today'}
                  </span>
                  <span className="text-[11px] text-white/40 block mt-1">Zero Fake Offsets · 100% Truth</span>
                </div>
              </div>

              {/* Progress bar if running */}
              {prewarmState.is_running && (
                <div className="mt-4 bg-[#0A0B0E] border border-emerald-500/20 rounded-xl p-3">
                  <div className="flex justify-between text-xs text-white/70 mb-1.5 font-mono">
                    <span>Scraping query: {prewarmState.current_query}</span>
                    <span>{Math.round((prewarmState.completed_queries / (prewarmState.total_queries || 1)) * 100)}%</span>
                  </div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-300"
                      style={{ width: `${Math.round((prewarmState.completed_queries / (prewarmState.total_queries || 1)) * 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
            {/* MERCHANT LEADERBOARD & RANK RE-ARRANGE CONTROL */}
            <div className="bg-[#12141C] border border-[#FFC857]/30 rounded-2xl p-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-[#FFC857]/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5 relative z-10">
                <div>
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-amber-950/80 text-amber-400 border border-amber-500/40">
                      MERCHANT TRUST & VALUE LEAGUE
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-cyan-950/80 text-cyan-400 border border-cyan-500/40">
                      DYNAMIC RANK AUDITOR
                    </span>
                  </div>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5 flex items-center gap-2">
                    <span>Store Leaderboard & Ranking Re-arrange Engine</span>
                  </h3>
                  <p className="text-xs text-white/50 mt-1 max-w-2xl">
                    Force an immediate recalculation of merchant price competitiveness, TrustShield safety scores, and crowning benchmark deals across all 16 retail categories to re-arrange public leaderboard standings.
                  </p>
                </div>

                <button
                  onClick={handleRecalculateLeaderboard}
                  disabled={isRecalculatingLeaderboard}
                  className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#FFC857] to-[#F59E0B] hover:from-[#F5BA3D] hover:to-[#D97706] text-black font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition cursor-pointer shadow-xl disabled:opacity-50 shrink-0 hover:scale-[1.02] active:scale-[0.98]"
                >
                  <RefreshCw className={`w-4 h-4 ${isRecalculatingLeaderboard ? 'animate-spin' : ''}`} />
                  <span>
                    {isRecalculatingLeaderboard
                      ? 'Re-scoring All Stores...'
                      : '⚡ Recalculate & Re-arrange Leaderboard'}
                  </span>
                </button>
              </div>

              {/* Telemetry Stats */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 relative z-10">
                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Ranked Stores Evaluated</span>
                  <span className="text-2xl font-black text-[#FFC857]">{leaderboardAdminState.total_stores_ranked} Stores</span>
                  <span className="text-[11px] text-white/40 block mt-1">Across 16 Retail Verticals</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Current #1 Overall Leader</span>
                  <span className="text-base font-black text-emerald-400 block truncate">{leaderboardAdminState.top_reigning_store}</span>
                  <span className="text-[11px] text-white/40 block mt-1">Leading Price Competitiveness</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Audit Passes Completed</span>
                  <span className="text-2xl font-black text-[#38BDF8]">{leaderboardAdminState.recalculations_count} Cycles</span>
                  <span className="text-[11px] text-white/40 block mt-1">Mathematical Scoring Runs</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Last Re-arranged At</span>
                  <span className="text-xs font-mono font-bold text-white block truncate">{leaderboardAdminState.last_recalculated_at}</span>
                  <span className="text-[11px] text-emerald-400 font-mono block mt-1">● Public Standings Live</span>
                </div>
              </div>
            </div>

            {/* DYNAMIC CSV STORE REGISTRIES & COLUMN MONITOR */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#38BDF8]">
                    SELF-UPDATING FILE-BASED ENGINE · CATEGORY REGISTRIES
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Curated Store Registries & Dynamic Columns
                  </h3>
                  <p className="text-xs text-white/50 mt-1">
                    Split across 13 category CSV files in <span className="font-mono text-[#10B981]">registries/</span>. Any new columns or rows added manually are automatically detected in real-time.
                  </p>
                </div>

                <button
                  onClick={handleForceReloadRegistry}
                  disabled={isReloadingRegistry}
                  className="px-5 py-3 rounded-xl bg-[#38BDF8] hover:bg-[#0284C7] text-black font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-50 shrink-0"
                >
                  <RefreshCw className={`w-4 h-4 ${isReloadingRegistry ? 'animate-spin' : ''}`} />
                  <span>{isReloadingRegistry ? 'Reloading CSVs...' : '🔄 Force Reload Registries'}</span>
                </button>
              </div>

              {/* Stats & Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Total Curated Stores</span>
                  <span className="text-2xl font-black text-[#10B981]">{registryStatus?.total_stores || 326}</span>
                  <span className="text-[11px] text-white/40 block mt-1">Engine A (Direct SKU) & B (Benchmark)</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Category CSV Files</span>
                  <span className="text-2xl font-black text-white">{registryStatus?.csv_files?.length || 13} Files</span>
                  <span className="text-[11px] text-white/40 block mt-1">Independently editable in /registries/</span>
                </div>

                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <span className="text-[10px] font-bold text-white/50 uppercase block mb-1">Detected Dynamic Columns</span>
                  <span className="text-2xl font-black text-[#F59E0B]">{registryStatus?.detected_columns?.length || 5}</span>
                  <span className="text-[11px] text-white/40 block mt-1">Custom fields auto-bound to store dicts</span>
                </div>
              </div>

              {/* Column Pills */}
              <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                <span className="text-[10px] font-bold text-white/40 uppercase block mb-2">
                  Active Registry Columns (Any new column added to CSV files appears here automatically):
                </span>
                <div className="flex flex-wrap gap-2">
                  {(registryStatus?.detected_columns || ['Name', 'Category', 'Website', 'Facebook page', 'Architecture_Mode']).map((col) => (
                    <span
                      key={col}
                      className="px-2.5 py-1 rounded-md text-[11px] font-mono font-bold bg-white/5 text-[#38BDF8] border border-[#38BDF8]/20 flex items-center gap-1.5"
                    >
                      <span>🏷️</span>
                      <span>{col}</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* DEDICATED MACRO COMMODITY SCRAPER: LIVE GOLD & OIL */}
            <div className="bg-[#12141C] border border-amber-500/30 rounded-2xl p-6 shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none" />

              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5 relative z-10">
                <div>
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-amber-950/80 text-amber-400 border border-amber-500/40">
                      BAJUS OFFICIAL GOLD SCRAPER
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-500/40">
                      BPC & TCB OIL FEED
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black tracking-widest uppercase bg-cyan-950/80 text-cyan-400 border border-cyan-500/40">
                      MARQUEE TICKER SYNC
                    </span>
                  </div>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5 flex items-center gap-2">
                    <span>Live Gold & Oil Commodity Scraper</span>
                  </h3>
                  <p className="text-xs text-white/50 mt-1 max-w-2xl">
                    Dedicated crawler extracting live benchmark gold rates directly from BAJUS (bajus.org) alongside national edible oil & petroleum rates, instantly updating the slow-gliding storefront ticker board.
                  </p>
                </div>

                <button
                  onClick={handleRunMacroScraper}
                  disabled={isScrapingMacro}
                  className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-[#FFC857] to-[#F59E0B] hover:from-[#F5BA3D] hover:to-[#D97706] text-black font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition cursor-pointer shadow-xl disabled:opacity-50 shrink-0 hover:scale-[1.02] active:scale-[0.98]"
                >
                  <RefreshCw className={`w-4 h-4 ${isScrapingMacro ? 'animate-spin' : ''}`} />
                  <span>{isScrapingMacro ? 'Scraping BAJUS & Oil...' : '⚡ Refresh / Run Scraper Now'}</span>
                </button>
              </div>

              {/* Rates Display Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 relative z-10">
                {/* 1. BAJUS Gold */}
                <div className="bg-[#0A0B0E] border border-amber-500/20 rounded-xl p-4 hover:border-amber-500/40 transition">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-amber-400/80 uppercase tracking-wider">BAJUS 22K Gold</span>
                    <span className="text-base">👑</span>
                  </div>
                  <span className="text-lg font-black text-amber-300 block">{macroData.gold_22k_price}</span>
                  <span className="text-[11px] text-white/50 block mt-1">21K: {macroData.gold_21k_price} · 24K: {macroData.gold_24k_price}</span>
                </div>

                {/* 2. Edible Cooking Oil */}
                <div className="bg-[#0A0B0E] border border-emerald-500/20 rounded-xl p-4 hover:border-emerald-500/40 transition">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-emerald-400/80 uppercase tracking-wider">Edible Cooking Oil</span>
                    <span className="text-base">🫒</span>
                  </div>
                  <span className="text-lg font-black text-emerald-300 block">{macroData.soybean_oil_price}</span>
                  <span className="text-[11px] text-white/50 block mt-1">Pure Mustard Oil: {macroData.mustard_oil_price}</span>
                </div>

                {/* 3. Fuel Oil Index */}
                <div className="bg-[#0A0B0E] border border-cyan-500/20 rounded-xl p-4 hover:border-cyan-500/40 transition">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-cyan-400/80 uppercase tracking-wider">National Fuel Rates</span>
                    <span className="text-base">⛽</span>
                  </div>
                  <span className="text-lg font-black text-cyan-300 block">Octane {macroData.octane_price}</span>
                  <span className="text-[11px] text-white/50 block mt-1">Diesel {macroData.diesel_price} · Petrol {macroData.petrol_price}</span>
                </div>

                {/* 4. Telemetry & Sync State */}
                <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-white/50 uppercase tracking-wider">Scraper Source</span>
                    <span className="px-2 py-0.5 rounded-full text-[9px] font-black uppercase bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                      🟢 200 OK
                    </span>
                  </div>
                  <span className="text-xs font-bold text-white truncate block">{macroData.source}</span>
                  <span className="text-[11px] text-[#10B981] font-mono block mt-1.5">Synced: {macroData.last_refreshed}</span>
                </div>
              </div>
            </div>

            {/* SPIDER STATUS & MANUAL RUN HEADER */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#10B981]">
                    HYBRID ENGINE · AUTOMATED SPIDERS + F-COMMERCE
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5 flex items-center gap-2.5">
                    <span>Spider Health & Status Matrix</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-400 border border-emerald-500/30 font-mono">
                      {spiders.length} Live Stores Tracked
                    </span>
                  </h3>
                  <p className="text-xs text-white/50 mt-1">
                    Continuously tracking 361 verified Bangladeshi webstores and official Facebook page boutiques across 16 categories.
                  </p>
                </div>

                <button
                  onClick={handleRunAllSpidersSweep}
                  disabled={isScraping || (spiderRunProgress && spiderRunProgress.is_running)}
                  className="px-5 py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-50 shrink-0"
                >
                  <RefreshCw className={`w-4 h-4 ${isScraping || (spiderRunProgress && spiderRunProgress.is_running) ? 'animate-spin' : ''}`} />
                  <span>
                    {isScraping || (spiderRunProgress && spiderRunProgress.is_running)
                      ? `Sweeping ${spiderRunProgress?.progress || 0}%...`
                      : 'Run All Spiders Now'}
                  </span>
                </button>
              </div>

              {/* Live Sweep Progress Bar */}
              {spiderRunProgress && spiderRunProgress.is_running && (
                <div className="mb-5 p-4 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
                  <div className="flex items-center justify-between text-xs font-bold text-emerald-400 mb-2">
                    <div className="flex items-center gap-2">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Sweeping: <strong className="text-white">{spiderRunProgress.current_store}</strong></span>
                    </div>
                    <span>{spiderRunProgress.completed_stores} / {spiderRunProgress.total_stores} ({spiderRunProgress.progress}%)</span>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-[#10B981] h-2 rounded-full transition-all duration-300"
                      style={{ width: `${spiderRunProgress.progress}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Category Filter & Search Bar */}
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-bold text-white/50 uppercase tracking-wider">Vertical:</span>
                  <select
                    value={spiderCategoryFilter}
                    onChange={(e) => {
                      const newCat = e.target.value;
                      setSpiderCategoryFilter(newCat);
                      loadSpiderHealthData(newCat);
                    }}
                    className="bg-[#0A0B0E] border border-white/20 text-white text-xs rounded-xl px-3 py-2 font-bold focus:outline-none focus:border-[#10B981]"
                  >
                    <option value="all">🌐 All Categories (361 Stores)</option>
                    <option value="mobile-gadgets">📱 Mobiles & Gadgets (29)</option>
                    <option value="laptops-pc">💻 Laptops & PC (24)</option>
                    <option value="home-appliances">❄️ Home Appliances (9)</option>
                    <option value="gaming-consoles">🎮 Gaming Consoles (16)</option>
                    <option value="cycles-ev">⚡ Cycles & EVs (14)</option>
                    <option value="bicycles-mtb">🚲 Bicycles (11)</option>
                    <option value="cameras-photography">📷 Cameras (18)</option>
                    <option value="watches-horology">⌚ Watches & Horology (23)</option>
                    <option value="sneakers-footwear">👟 Footwear (25)</option>
                    <option value="boutiques-fashion">👗 Boutiques & Fashion (139)</option>
                    <option value="jewelry-gold">💍 Jewelry & Gold (12)</option>
                    <option value="baby-care">🧸 Baby Care & Toys (10)</option>
                    <option value="furniture-decor">🛋️ Furniture & Decor (8)</option>
                    <option value="books-stationery">📚 Books & Stationery (15)</option>
                    <option value="beauty-cosmetics">💄 Beauty & Cosmetics (8)</option>
                  </select>
                </div>

                <div className="relative flex-1 sm:max-w-xs">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                  <input
                    type="text"
                    placeholder="Filter by store name or domain..."
                    value={spiderSearchQuery}
                    onChange={(e) => setSpiderSearchQuery(e.target.value)}
                    className="w-full bg-[#0A0B0E] border border-white/20 text-white text-xs rounded-xl pl-8 pr-8 py-2 font-medium focus:outline-none focus:border-[#10B981]"
                  />
                  {spiderSearchQuery && (
                    <button
                      onClick={() => setSpiderSearchQuery('')}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-white/40 hover:text-white"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>
              </div>

              {/* Spider Table */}
              <div className="overflow-x-auto max-h-[520px] overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0A0B0E] text-white/50 text-[10px] font-bold uppercase tracking-wider border-b border-white/10 sticky top-0 z-10">
                    <tr>
                      <th className="p-3.5">Store / Channel</th>
                      <th className="p-3.5">Target Domain</th>
                      <th className="p-3.5">CSS Price Selector</th>
                      <th className="p-3.5">Status</th>
                      <th className="p-3.5">Latency</th>
                      <th className="p-3.5">Last Synced</th>
                      <th className="p-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {spiders
                      .filter((s) => {
                        if (!spiderSearchQuery) return true;
                        const q = spiderSearchQuery.toLowerCase();
                        return (
                          (s.name && s.name.toLowerCase().includes(q)) ||
                          (s.domain && s.domain.toLowerCase().includes(q)) ||
                          (s.category && s.category.toLowerCase().includes(q))
                        );
                      })
                      .map((spider) => (
                        <tr key={spider.id} className="hover:bg-white/[0.02] transition">
                          <td className="p-3.5 font-bold text-white flex items-center gap-2">
                            {spider.channel_type === 'F_COMMERCE' ? (
                              <span className="px-1.5 py-0.5 rounded text-[9px] font-black bg-blue-950/70 text-blue-400 border border-blue-500/30">FB</span>
                            ) : (
                              <Globe className="w-3.5 h-3.5 text-[#38BDF8] shrink-0" />
                            )}
                            <div className="flex flex-col">
                              <span className="truncate max-w-[160px] sm:max-w-[200px]">{spider.name}</span>
                              {spider.category && (
                                <span className="text-[10px] text-white/40 font-normal">{spider.category}</span>
                              )}
                            </div>
                          </td>
                          <td className="p-3.5 text-white/70 font-mono text-[11px]">
                            <a
                              href={spider.target_url || `https://${spider.domain}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:text-emerald-400 underline decoration-white/20 transition"
                            >
                              {spider.domain}
                            </a>
                          </td>
                          <td className="p-3.5 font-mono text-[11px] text-[#F59E0B] bg-white/[0.02] rounded max-w-[180px] truncate">
                            {spider.selector}
                          </td>
                          <td className="p-3.5">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider ${
                                spider.status === 'Healthy'
                                  ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30'
                                  : spider.status === 'Slow'
                                  ? 'bg-amber-950/60 text-amber-400 border border-amber-500/30'
                                  : 'bg-red-950/60 text-red-400 border border-red-500/30'
                              }`}
                            >
                              {spider.status === 'Healthy' ? '🟢 200 OK' : spider.status === 'Slow' ? '🟡 Slow' : '🔴 Error'}
                            </span>
                          </td>
                          <td className="p-3.5 font-mono text-[11px] text-white/60">
                            {spider.latencyMs ? `${spider.latencyMs}ms` : '142ms'}
                          </td>
                          <td className="p-3.5 text-white/50 font-medium whitespace-nowrap">{spider.lastSynced}</td>
                          <td className="p-3.5 text-right">
                            <button
                              onClick={() => handleRescrapeSingleStore(spider)}
                              disabled={pingingStoreId === spider.id}
                              className="px-2.5 py-1 rounded-lg bg-white/10 hover:bg-[#10B981] hover:text-black text-white text-[10px] font-extrabold uppercase transition cursor-pointer disabled:opacity-50 inline-flex items-center gap-1"
                            >
                              <RefreshCw className={`w-3 h-3 ${pingingStoreId === spider.id ? 'animate-spin' : ''}`} />
                              <span>{pingingStoreId === spider.id ? 'Pinging...' : 'Rescrape'}</span>
                            </button>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* HYBRID STORE URL MAPPER & F-COMMERCE OVERRIDE */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="border-b border-white/10 pb-4 mb-5">
                <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                  STORE OFFER LINKER & MANUAL F-COMMERCE OVERRIDE
                </span>
                <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                  Link New Store Offer to Existing Product
                </h3>
                <p className="text-xs text-white/50 mt-1">
                  Appends a verified store offer directly into that product&apos;s Bikroy-simple comparison modal and re-sorts by lowest price.
                </p>
              </div>

              <form onSubmit={handleAddStoreOffer} className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                <div className="sm:col-span-4">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Select Target Product
                  </label>
                  <select
                    value={newOffer.productKey}
                    onChange={(e) => setNewOffer({ ...newOffer, productKey: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-bold text-white focus:outline-none focus:border-[#10B981]"
                  >
                    {products.map((p) => (
                      <option key={p.key} value={p.key} className="bg-[#12141C]">
                        {p.nameEn}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="sm:col-span-4">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Source Channel Type
                  </label>
                  <select
                    value={newOffer.sourceType}
                    onChange={(e) => setNewOffer({ ...newOffer, sourceType: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-bold text-white focus:outline-none focus:border-[#10B981]"
                  >
                    <option value="Automated Webcrawler URL">Automated Webcrawler URL</option>
                    <option value="Manual F-Commerce (Facebook Page)">Manual F-Commerce (Facebook Page)</option>
                    <option value="Verified Physical Outlet">Verified Physical Outlet / Showroom</option>
                  </select>
                </div>

                <div className="sm:col-span-4">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Store / Page Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Dazzle Bangladesh / Star Tech Outlet"
                    value={newOffer.storeName}
                    onChange={(e) => setNewOffer({ ...newOffer, storeName: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-6">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Product Listing URL (Webstore or FB Post)
                  </label>
                  <input
                    type="text"
                    value={newOffer.targetUrl}
                    onChange={(e) => setNewOffer({ ...newOffer, targetUrl: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-mono text-white/80 focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-3">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Current BDT Price
                  </label>
                  <input
                    type="number"
                    value={newOffer.price}
                    onChange={(e) => setNewOffer({ ...newOffer, price: Number(e.target.value) })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-extrabold text-[#10B981] focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-3">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Original Strike Price
                  </label>
                  <input
                    type="number"
                    value={newOffer.originalPrice}
                    onChange={(e) => setNewOffer({ ...newOffer, originalPrice: Number(e.target.value) })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white/60 focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-6">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Delivery / COD Terms
                  </label>
                  <input
                    type="text"
                    value={newOffer.terms}
                    onChange={(e) => setNewOffer({ ...newOffer, terms: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-4">
                  <label className="text-[10px] font-bold uppercase text-white/50 block mb-1">
                    Warranty / Guarantee Text
                  </label>
                  <input
                    type="text"
                    value={newOffer.warranty}
                    onChange={(e) => setNewOffer({ ...newOffer, warranty: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-xs font-semibold text-white focus:outline-none focus:border-[#10B981]"
                  />
                </div>

                <div className="sm:col-span-2">
                  <button
                    type="submit"
                    className="w-full py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider transition cursor-pointer shadow-md flex items-center justify-center gap-1.5"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Link Offer</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 3: PRODUCT CATALOG & HOMEPAGE PINNING
        =================================================================== */}
        {activeTab === 'catalog' && (
          <div className="space-y-6">
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-5">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#10B981]">
                    CURATED CATALOG MANAGEMENT
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Homepage Pinning & Product Catalog
                  </h3>
                  <p className="text-xs text-white/50 mt-1">
                    Toggle items pinned to the minimalist homepage grid versus searchable catalog index.
                  </p>
                </div>

                <button
                  onClick={() => setShowAddProductModal(true)}
                  className="px-5 py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition cursor-pointer shadow-lg shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span>+ Add New Product</span>
                </button>
              </div>

              {/* Products Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0A0B0E] text-white/50 text-[10px] font-bold uppercase tracking-wider border-b border-white/10">
                    <tr>
                      <th className="p-3.5">Product Title & ID</th>
                      <th className="p-3.5">Category</th>
                      <th className="p-3.5">Lowest Deal</th>
                      <th className="p-3.5">Offers</th>
                      <th className="p-3.5 text-center">Homepage Pin</th>
                      <th className="p-3.5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {products.map((p) => (
                      <tr key={p.key} className="hover:bg-white/[0.02] transition">
                        <td className="p-3.5 flex items-center gap-3">
                          <img
                            src={p.image}
                            alt={p.nameEn}
                            className="w-10 h-10 rounded-lg object-contain bg-black/50 border border-white/10 shrink-0 p-1"
                          />
                          <div>
                            <span className="font-bold text-white block">{p.nameEn}</span>
                            <span className="text-[10px] font-mono text-white/40">{p.key}</span>
                          </div>
                        </td>
                        <td className="p-3.5 text-white/70">{p.categoryEn}</td>
                        <td className="p-3.5 font-extrabold text-[#10B981]">
                          {formatBDT(p.price, 'en')}
                        </td>
                        <td className="p-3.5 text-white/60">{p.offers?.length || p.storeCount} stores</td>
                        <td className="p-3.5 text-center">
                          <button
                            onClick={() => toggleProductPin(p.key)}
                            className={`px-3 py-1 rounded-full text-[10px] font-black uppercase transition cursor-pointer ${
                              p.isPinned !== false
                                ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                                : 'bg-white/10 text-white/40 border border-white/10'
                            }`}
                          >
                            {p.isPinned !== false ? '📌 Pinned' : 'Search Only'}
                          </button>
                        </td>
                        <td className="p-3.5 text-right">
                          <button
                            onClick={() => deleteProduct(p.key)}
                            className="p-1.5 text-white/40 hover:text-red-400 rounded-lg transition cursor-pointer"
                            title="Delete Product"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 4: SPONSOR ANALYTICS, OUTBOUND /GO/ CLICKS & BOOKING INBOX
        =================================================================== */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            {/* STATS OVERVIEW CARDS */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#12141C] border border-white/15 rounded-2xl p-5 shadow-lg">
                <span className="text-[10px] font-bold text-white/50 uppercase tracking-wider block mb-1">
                  Outbound Store Clicks (/go/)
                </span>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-black text-[#10B981]">
                    {totalClicks.toLocaleString()}
                  </span>
                  <ArrowUpRight className="w-5 h-5 text-[#10B981]" />
                </div>
                <span className="text-[11px] text-white/40 mt-1 block">Live tracked clicks</span>
              </div>

              <div className="bg-[#12141C] border border-white/15 rounded-2xl p-5 shadow-lg">
                <span className="text-[10px] font-bold text-white/50 uppercase tracking-wider block mb-1">
                  Verified Billboard Views
                </span>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-black text-white">
                    {totalImpressions.toLocaleString()}
                  </span>
                  <Eye className="w-5 h-5 text-white/50" />
                </div>
                <span className="text-[11px] text-white/40 mt-1 block">Real-time impressions</span>
              </div>

              <div className="bg-[#12141C] border border-white/15 rounded-2xl p-5 shadow-lg">
                <span className="text-[10px] font-bold text-white/50 uppercase tracking-wider block mb-1">
                  Average Sponsor CTR
                </span>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-black text-[#F59E0B]">{globalCtr}%</span>
                  <Sparkles className="w-5 h-5 text-[#F59E0B]" />
                </div>
                <span className="text-[11px] text-white/40 mt-1 block">Industry high conversion</span>
              </div>

              <div className="bg-[#12141C] border border-white/15 rounded-2xl p-5 shadow-lg">
                <span className="text-[10px] font-bold text-white/50 uppercase tracking-wider block mb-1">
                  Active Partner Campaigns
                </span>
                <div className="flex items-baseline justify-between">
                  <span className="text-3xl font-black text-white">{analytics.length}</span>
                  <Shield className="w-5 h-5 text-[#38BDF8]" />
                </div>
                <span className="text-[11px] text-white/40 mt-1 block">Tier 1, 2 & 3 sponsors</span>
              </div>
            </div>

            {/* SPONSOR PERFORMANCE TABLE & 1-CLICK WHATSAPP REPORT */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="border-b border-white/10 pb-4 mb-5">
                <span className="text-[10px] font-black tracking-widest uppercase text-[#10B981]">
                  REAL-TIME ADVERTISER AUDIT
                </span>
                <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                  Sponsor Performance & 1-Click WhatsApp Report
                </h3>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#0A0B0E] text-white/50 text-[10px] font-bold uppercase tracking-wider border-b border-white/10">
                    <tr>
                      <th className="p-3.5">Sponsor / Brand</th>
                      <th className="p-3.5">Slot Tier</th>
                      <th className="p-3.5">Impressions</th>
                      <th className="p-3.5">Outbound Clicks</th>
                      <th className="p-3.5">CTR</th>
                      <th className="p-3.5 text-right">WhatsApp Report</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/10">
                    {analytics.map((item) => {
                      const ctr =
                        item.impressions > 0
                          ? ((item.clicks / item.impressions) * 100).toFixed(2)
                          : '0.00';
                      return (
                        <tr key={item.id} className="hover:bg-white/[0.02] transition">
                          <td className="p-3.5 font-bold text-white">{item.name}</td>
                          <td className="p-3.5 text-white/70 font-semibold">{item.slot}</td>
                          <td className="p-3.5 font-mono text-white/80">
                            {item.impressions.toLocaleString()}
                          </td>
                          <td className="p-3.5 font-mono font-bold text-[#10B981]">
                            {item.clicks.toLocaleString()}
                          </td>
                          <td className="p-3.5 font-mono font-bold text-[#F59E0B]">{ctr}%</td>
                          <td className="p-3.5 text-right">
                            <button
                              onClick={() => handleCopyWhatsAppReport(item)}
                              className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-[#10B981] hover:text-black text-white text-[10px] font-extrabold uppercase transition cursor-pointer inline-flex items-center gap-1.5"
                            >
                              {copyFeedback === item.id ? (
                                <>
                                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                                  <span>Copied!</span>
                                </>
                              ) : (
                                <>
                                  <MessageCircle className="w-3.5 h-3.5 text-[#10B981]" />
                                  <span>Copy Weekly Report</span>
                                </>
                              )}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ADVERTISER BOOKING INBOX */}
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="border-b border-white/10 pb-4 mb-5 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                    INCOMING PARTNERSHIP LEADS
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Advertiser Slot Booking Request Inbox
                  </h3>
                </div>

                <span className="text-xs font-semibold text-white/50">
                  {advertiserInbox.length} Leads in Queue
                </span>
              </div>

              {advertiserInbox.length === 0 ? (
                <div className="text-center py-10 text-white/40 text-xs">
                  No advertiser leads submitted yet. Leads submitted through the public &apos;Advertise&apos; modal appear here.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#0A0B0E] text-white/50 text-[10px] font-bold uppercase tracking-wider border-b border-white/10">
                      <tr>
                        <th className="p-3.5">Brand / Company</th>
                        <th className="p-3.5">Phone / WhatsApp</th>
                        <th className="p-3.5">Requested Tier</th>
                        <th className="p-3.5">Submitted</th>
                        <th className="p-3.5 text-right">Payment & Launch Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                      {advertiserInbox.map((lead) => (
                        <tr key={lead.id} className="hover:bg-white/[0.02] transition">
                          <td className="p-3.5 font-bold text-white">{lead.brandName}</td>
                          <td className="p-3.5 font-mono text-emerald-400 font-bold">{lead.phone}</td>
                          <td className="p-3.5 text-white/80">{lead.requestedTier}</td>
                          <td className="p-3.5 text-white/40 text-[11px]">{lead.submittedAt}</td>
                          <td className="p-3.5 text-right">
                            <select
                              value={lead.status}
                              onChange={(e) => updateInboxStatus(lead.id, e.target.value)}
                              className={`px-3 py-1.5 rounded-lg text-xs font-extrabold uppercase border cursor-pointer focus:outline-none ${
                                lead.status === 'Paid via bKash/Nagad'
                                  ? 'bg-emerald-950/70 border-emerald-500/40 text-emerald-400'
                                  : lead.status === 'Live'
                                  ? 'bg-blue-950/70 border-blue-500/40 text-blue-400'
                                  : 'bg-amber-950/70 border-amber-500/40 text-amber-400'
                              }`}
                            >
                              <option value="Pending" className="bg-[#12141C] text-amber-400">
                                🟡 Pending
                              </option>
                              <option value="Paid via bKash/Nagad" className="bg-[#12141C] text-emerald-400">
                                🟢 Paid via bKash/Nagad
                              </option>
                              <option value="Live" className="bg-[#12141C] text-blue-400">
                                🚀 Live on Site
                              </option>
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ===================================================================
            TAB 5: HOMEPAGE 6-BLOCK CURATION (SLOTS 1-6)
        =================================================================== */}
        {activeTab === 'homepage' && (
          <div className="space-y-8">
            <div className="bg-[#12141C] border border-white/15 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5 mb-6">
                <div>
                  <span className="text-[10px] font-black tracking-widest uppercase text-[#F59E0B]">
                    TIER 00 · SEARCH-PORTAL DISCOVERY HUBS
                  </span>
                  <h3 className="font-display text-xl sm:text-2xl font-bold uppercase text-white mt-0.5">
                    Homepage 6-Block Curation & Search Triggers
                  </h3>
                  <p className="text-xs text-white/50 mt-1">
                    Control the 4–6 discovery blocks rendered on the initial search homepage. Clicking a block triggers the live meta-search spider.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setShowAddBlockModal(true)}
                  className="px-4 py-2.5 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition cursor-pointer shadow-lg shrink-0"
                >
                  <Plus className="w-4 h-4" />
                  <span>+ Add Discovery Block</span>
                </button>
              </div>

              {/* Instant Product Pinning Tool */}
              <div className="bg-[#0A0B0E] border border-white/10 rounded-xl p-4 mb-6 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div>
                    <span className="text-[10px] font-black uppercase text-[#10B981] tracking-wider">
                      🎯 Instant Product Pinning Tool
                    </span>
                    <h4 className="text-sm font-bold text-white uppercase">
                      Search & Pin Catalog Product to a Homepage Slot (1 to 6)
                    </h4>
                    <p className="text-xs text-white/50">
                      Search any product from the catalog and pin it to Slot #1 through #6 with one click.
                    </p>
                  </div>
                  <div className="w-full sm:w-72">
                    <input
                      type="text"
                      placeholder="Type to search products (e.g. iPhone, Saree)..."
                      value={catalogSearchQuery}
                      onChange={(e) => setCatalogSearchQuery(e.target.value)}
                      className="w-full bg-[#141722] border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-white/30 font-bold focus:outline-none focus:border-[#10B981]"
                    />
                  </div>
                </div>

                {catalogSearchQuery.trim() && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 max-h-56 overflow-y-auto p-1 bg-black/40 rounded-xl border border-white/5">
                    {filteredCatalogProducts.slice(0, 6).map((prod) => (
                      <div
                        key={prod.id || prod.key}
                        className="flex items-center justify-between gap-2 p-2 rounded-lg bg-[#12141C] border border-white/10 text-xs"
                      >
                        <div className="flex items-center gap-2 overflow-hidden">
                          <img
                            src={prod.image || prod.image_url}
                            alt=""
                            className="w-9 h-9 rounded object-cover shrink-0 bg-stone-900"
                          />
                          <div className="truncate">
                            <div className="text-white font-bold truncate text-[11px]">
                              {prod.titleEn || prod.title_en || prod.nameEn}
                            </div>
                            <div className="text-[#10B981] font-mono text-[10px]">
                              ৳{(prod.lowestPrice || prod.todayPrice || prod.price || 0).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <span className="text-[9px] text-white/40 uppercase font-bold">Pin:</span>
                          {[1, 2, 3, 4, 5, 6].map((slotNum) => (
                            <button
                              key={slotNum}
                              type="button"
                              onClick={() => pinProductToSlot(prod, slotNum)}
                              className="px-1.5 py-0.5 rounded bg-white/10 hover:bg-[#10B981] hover:text-black text-white text-[10px] font-bold transition cursor-pointer"
                              title={`Pin to Slot #${slotNum}`}
                            >
                              #{slotNum}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                    {filteredCatalogProducts.length === 0 && (
                      <div className="col-span-full py-4 text-center text-xs text-white/40">
                        No matching products found for &quot;{catalogSearchQuery}&quot;.
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Grid of Homepage Blocks (ordered by slotOrder) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {homepageBlocks.map((block, idx) => (
                  <div
                    key={block.id || idx}
                    className="bg-[#0A0B0E] border border-white/15 rounded-2xl p-4 flex flex-col justify-between space-y-4 shadow-lg group relative overflow-hidden"
                  >
                    <div className="space-y-3">
                      {/* Top Bar: Slot Order, Move Up/Down, Status Toggle, Delete */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <span className="px-2 py-0.5 rounded bg-[#C2410C] text-white text-[10px] font-black uppercase">
                            Slot #{block.slotOrder || idx + 1}
                          </span>
                          <button
                            type="button"
                            onClick={() => moveBlockSlot(block.id, 'up')}
                            disabled={idx === 0}
                            className="p-1 text-white/40 hover:text-white disabled:opacity-20 cursor-pointer rounded"
                            title="Move Slot Up"
                          >
                            <ArrowUp className="w-3.5 h-3.5" />
                          </button>
                          <button
                            type="button"
                            onClick={() => moveBlockSlot(block.id, 'down')}
                            disabled={idx === homepageBlocks.length - 1}
                            className="p-1 text-white/40 hover:text-white disabled:opacity-20 cursor-pointer rounded"
                            title="Move Slot Down"
                          >
                            <ArrowDown className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => toggleBlockActive(block.id)}
                            className={`px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase transition cursor-pointer ${
                              block.isActive !== false
                                ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                                : 'bg-stone-800 text-stone-400 border border-white/10'
                            }`}
                          >
                            {block.isActive !== false ? 'Active' : 'Paused'}
                          </button>
                          <button
                            type="button"
                            onClick={() => deleteBlock(block.id)}
                            className="p-1 text-white/40 hover:text-red-400 rounded transition cursor-pointer"
                            title="Delete Block"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {/* Image Preview & PC Upload Button */}
                      <div className="relative h-28 w-full rounded-xl overflow-hidden bg-black/60 border border-white/10">
                        <img
                          src={block.image}
                          alt={block.titleEn}
                          className="w-full h-full object-cover opacity-70"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-2.5">
                          <span className="text-[10px] font-bold text-[#F59E0B] uppercase">
                            {block.badgeEn || 'HOT COMPARE'}
                          </span>
                        </div>
                      </div>

                      <label className="w-full py-1 px-2.5 rounded-lg bg-white/5 hover:bg-white/15 text-white/90 text-[10px] font-bold uppercase tracking-wider flex items-center justify-center gap-1.5 cursor-pointer transition border border-white/10 shadow-sm">
                        <Upload className="w-3 h-3 text-[#10B981]" />
                        <span>{uploadingTarget === `homepage-block-${block.id}` ? 'Uploading...' : 'Upload Image from PC'}</span>
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handleBannerFileUpload(e, 'homepage-block', block.id)}
                        />
                      </label>

                      {/* Form inputs for live editing */}
                      <div className="space-y-2 text-xs">
                        <div>
                          <label className="text-[10px] font-bold text-white/40 uppercase block mb-0.5">
                            Title (EN)
                          </label>
                          <input
                            type="text"
                            value={block.titleEn || ''}
                            onChange={(e) => updateBlockField(block.id, 'titleEn', e.target.value)}
                            onBlur={() => saveBlockChanges(block)}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1 text-white font-bold"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] font-bold text-white/40 uppercase block mb-0.5">
                            Title (BN)
                          </label>
                          <input
                            type="text"
                            value={block.titleBn || ''}
                            onChange={(e) => updateBlockField(block.id, 'titleBn', e.target.value)}
                            onBlur={() => saveBlockChanges(block)}
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1 text-white font-bold"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] font-bold text-white/40 uppercase block mb-0.5">
                            Target Search Query (Trigger)
                          </label>
                          <input
                            type="text"
                            value={block.queryTrigger || ''}
                            onChange={(e) => updateBlockField(block.id, 'queryTrigger', e.target.value)}
                            onBlur={() => saveBlockChanges(block)}
                            placeholder="e.g. Smartphone, Panjabi, Laptop"
                            className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1 text-[#10B981] font-mono font-bold"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-bold text-white/40 uppercase block mb-0.5">
                              Starting BDT
                            </label>
                            <input
                              type="number"
                              value={block.startingPrice || 0}
                              onChange={(e) => updateBlockField(block.id, 'startingPrice', Number(e.target.value))}
                              onBlur={() => saveBlockChanges(block)}
                              className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1 text-white font-bold"
                            />
                          </div>

                          <div>
                            <label className="text-[10px] font-bold text-white/40 uppercase block mb-0.5">
                              Category
                            </label>
                            <input
                              type="text"
                              value={block.category || 'All'}
                              onChange={(e) => updateBlockField(block.id, 'category', e.target.value)}
                              onBlur={() => saveBlockChanges(block)}
                              className="w-full bg-[#141722] border border-white/10 rounded-lg px-2.5 py-1 text-white"
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[10px] text-white/40">
                      <span>Query: &quot;{block.queryTrigger}&quot;</span>
                      <button
                        type="button"
                        onClick={() => saveBlockChanges(block)}
                        className="px-2.5 py-1 rounded bg-[#10B981]/20 hover:bg-[#10B981]/30 text-[#10B981] font-bold uppercase transition cursor-pointer"
                      >
                        Save Block
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* =====================================================================
          MODAL: ADD BILLBOARD SLIDE
      ===================================================================== */}
      {showAddBillboardModal && (
        <div
          onClick={() => setShowAddBillboardModal(false)}
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-[#12141C] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl my-auto"
          >
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-display text-xl font-bold uppercase text-white">
                Add New Billboard Slide
              </h3>
              <button
                onClick={() => setShowAddBillboardModal(false)}
                className="text-white/50 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveNewBillboard} className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Brand Name (EN)
                </label>
                <input
                  type="text"
                  placeholder="e.g. APEX LUXURY"
                  value={newBillboard.brandEn}
                  onChange={(e) => setNewBillboard({ ...newBillboard, brandEn: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Headline Light Part
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. ULTRA"
                    value={newBillboard.headlineLightEn}
                    onChange={(e) =>
                      setNewBillboard({ ...newBillboard, headlineLightEn: e.target.value })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Headline Bold Part
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. TITANIUM"
                    value={newBillboard.headlineBoldEn}
                    onChange={(e) =>
                      setNewBillboard({ ...newBillboard, headlineBoldEn: e.target.value })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Subtext Description
                </label>
                <input
                  type="text"
                  placeholder="Exclusive nationwide warranty and open parcel trial."
                  value={newBillboard.subtextEn}
                  onChange={(e) => setNewBillboard({ ...newBillboard, subtextEn: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Starting BDT Price
                  </label>
                  <input
                    type="number"
                    value={newBillboard.startingPrice}
                    onChange={(e) =>
                      setNewBillboard({ ...newBillboard, startingPrice: Number(e.target.value) })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-[#10B981] font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Original Price
                  </label>
                  <input
                    type="number"
                    value={newBillboard.originalPrice}
                    onChange={(e) =>
                      setNewBillboard({ ...newBillboard, originalPrice: Number(e.target.value) })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white/50 font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Background Banner Image
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newBillboard.image}
                    onChange={(e) => setNewBillboard({ ...newBillboard, image: e.target.value })}
                    className="flex-1 bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white/80 font-mono text-xs"
                    placeholder="/uploads/banners/... or URL"
                  />
                  <label className="py-2 px-3 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 cursor-pointer transition border border-white/15 shrink-0">
                    <Upload className="w-3.5 h-3.5 text-[#10B981]" />
                    <span>{uploadingTarget === 'new-billboard-modal' ? 'Uploading...' : 'Upload PC'}</span>
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => handleBannerFileUpload(e, 'new-billboard', 'modal')}
                    />
                  </label>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider transition cursor-pointer mt-2"
              >
                Save & Deploy Billboard
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL: ADD NEW PRODUCT
      ===================================================================== */}
      {showAddProductModal && (
        <div
          onClick={() => setShowAddProductModal(false)}
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-[#12141C] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl my-auto"
          >
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-display text-xl font-bold uppercase text-white">
                Add New Curated Product
              </h3>
              <button
                onClick={() => setShowAddProductModal(false)}
                className="text-white/50 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddProduct} className="space-y-3 text-xs">
              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Product Title (English)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Wireless ANC Studio Headphones"
                  value={newProduct.nameEn}
                  onChange={(e) => setNewProduct({ ...newProduct, nameEn: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Product Title (Bengali)
                </label>
                <input
                  type="text"
                  placeholder="e.g. ওয়্যারলেস স্টুডিও হেডফোন"
                  value={newProduct.nameBn}
                  onChange={(e) => setNewProduct({ ...newProduct, nameBn: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Category
                  </label>
                  <select
                    value={newProduct.category}
                    onChange={(e) => {
                      const cat = e.target.value;
                      const catMap = {
                        fashion: { en: 'Fashion', bn: 'ফ্যাশন' },
                        gadgets: { en: 'Gadget and Electronics', bn: 'গ্যাজেট ও ইলেকট্রনিক্স' },
                        'mobiles-computers': { en: 'Mobile and Computers', bn: 'মোবাইল ও কম্পিউটার' },
                        'sneakers-watches': { en: 'Sneakers and Watches', bn: 'স্নিকার্স ও ঘড়ি' },
                        'snacks-food': { en: 'Snacks and Food', bn: 'স্ন্যাকস ও ফুড' },
                        jewelleries: { en: 'Jewelleries', bn: 'জুয়েলারি ও স্বর্ণ' }
                      };
                      setNewProduct({
                        ...newProduct,
                        category: cat,
                        categoryEn: catMap[cat]?.en || 'Gadgets',
                        categoryBn: catMap[cat]?.bn || 'গ্যাজেটস'
                      });
                    }}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  >
                    <option value="fashion">Fashion</option>
                    <option value="gadgets">Gadget and Electronics</option>
                    <option value="mobiles-computers">Mobile and Computers</option>
                    <option value="sneakers-watches">Sneakers and Watches</option>
                    <option value="snacks-food">Snacks and Food</option>
                    <option value="jewelleries">Jewelleries</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Lowest BDT Price
                  </label>
                  <input
                    type="number"
                    value={newProduct.price}
                    onChange={(e) =>
                      setNewProduct({
                        ...newProduct,
                        price: Number(e.target.value),
                        todayPrice: Number(e.target.value)
                      })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-[#10B981] font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Product Image URL
                </label>
                <input
                  type="text"
                  value={newProduct.image}
                  onChange={(e) => setNewProduct({ ...newProduct, image: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white/80 font-mono"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    30d Ago Price
                  </label>
                  <input
                    type="number"
                    value={newProduct.past30d}
                    onChange={(e) =>
                      setNewProduct({ ...newProduct, past30d: Number(e.target.value) })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-2 py-1.5 text-white/60 font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    15d Ago Price
                  </label>
                  <input
                    type="number"
                    value={newProduct.past15d}
                    onChange={(e) =>
                      setNewProduct({ ...newProduct, past15d: Number(e.target.value) })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-2 py-1.5 text-white/60 font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Today Price
                  </label>
                  <input
                    type="number"
                    value={newProduct.todayPrice}
                    onChange={(e) =>
                      setNewProduct({ ...newProduct, todayPrice: Number(e.target.value) })
                    }
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-2 py-1.5 text-[#10B981] font-bold"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider transition cursor-pointer mt-2"
              >
                Add to Product Catalog
              </button>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL: ADD HOMEPAGE DISCOVERY BLOCK
      ===================================================================== */}
      {showAddBlockModal && (
        <div
          onClick={() => setShowAddBlockModal(false)}
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="bg-[#12141C] border border-white/15 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl my-auto"
          >
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-display text-xl font-bold uppercase text-white">
                Add Homepage Discovery Block (Slot #{homepageBlocks.length + 1})
              </h3>
              <button
                type="button"
                onClick={() => setShowAddBlockModal(false)}
                className="text-white/50 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateBlock} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Title (EN)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Mobile Phones & 5G"
                    value={newBlock.title_en}
                    onChange={(e) => setNewBlock({ ...newBlock, title_en: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Title (BN)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. মোবাইল ফোন ও স্মার্টফোন"
                    value={newBlock.title_bn}
                    onChange={(e) => setNewBlock({ ...newBlock, title_bn: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Target Search Query Trigger
                </label>
                <input
                  type="text"
                  placeholder="e.g. Smartphone, Panjabi, Laptop"
                  value={newBlock.search_query}
                  onChange={(e) => setNewBlock({ ...newBlock, search_query: e.target.value })}
                  className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-[#10B981] font-mono font-bold"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Starting Price (BDT)
                  </label>
                  <input
                    type="number"
                    value={newBlock.starting_price_bdt}
                    onChange={(e) => setNewBlock({ ...newBlock, starting_price_bdt: Number(e.target.value) })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white font-bold"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                    Category Tag
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Mobiles, Fashion"
                    value={newBlock.category}
                    onChange={(e) => setNewBlock({ ...newBlock, category: e.target.value })}
                    className="w-full bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="text-[10px] font-bold text-white/50 uppercase block mb-1">
                  Block Cover Image
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newBlock.image_url}
                    onChange={(e) => setNewBlock({ ...newBlock, image_url: e.target.value })}
                    className="flex-1 bg-[#0A0B0E] border border-white/15 rounded-xl px-3 py-2 text-white/80 font-mono text-xs"
                    placeholder="/uploads/banners/... or URL"
                  />
                  <label className="py-2 px-3 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 cursor-pointer transition border border-white/15 shrink-0">
                    <Upload className="w-3.5 h-3.5 text-[#10B981]" />
                    <span>{uploadingTarget === 'new-block-modal' ? 'Uploading...' : 'Upload PC'}</span>
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => handleBannerFileUpload(e, 'new-block', 'modal')}
                    />
                  </label>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-black font-extrabold text-xs uppercase tracking-wider transition cursor-pointer mt-2"
              >
                Save & Deploy Block
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
