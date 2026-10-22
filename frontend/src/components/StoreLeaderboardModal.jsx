'use client';

import React, { useState, useEffect } from 'react';
import {
  Award,
  ShieldCheck,
  Globe,
  MessageCircle,
  ExternalLink,
  X,
  TrendingDown,
  Building2,
  ArrowRight,
  Loader2,
  AlertCircle,
  ChevronDown,
  Layers
} from 'lucide-react';
import { fetchLeaderboard, trackOutboundClick } from '../api';

export default function StoreLeaderboardModal({
  isOpen,
  onClose,
  lang = 'en',
  categoriesList = [],
  onSelectProductDeal,
}) {
  const [selectedCat, setSelectedCat] = useState('all');
  const [selectedPillar, setSelectedPillar] = useState('price');
  const [catDropdownOpen, setCatDropdownOpen] = useState(false);
  const dropdownRef = React.useRef(null);
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setCatDropdownOpen(false);
      }
    }
    if (catDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [catDropdownOpen]);

  const activeCategoryObj = categoriesList.find((c) => c.id === selectedCat);
  const activeCatLabel =
    selectedCat === 'all'
      ? lang === 'bn'
        ? 'সব ক্যাটাগরি'
        : 'All Categories'
      : activeCategoryObj
      ? lang === 'bn'
        ? activeCategoryObj.bn
        : activeCategoryObj.en
      : selectedCat;

  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    setLoading(true);
    setError(null);

    fetchLeaderboard(selectedCat, selectedPillar, 20)
      .then((res) => {
        if (isMounted) {
          setStores(res?.stores || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.warn('Leaderboard fetch error:', err);
          setError(err.message || 'Failed to load leaderboard data.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isOpen, selectedCat, selectedPillar]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-5xl max-h-[92vh] flex flex-col bg-[#0A0D14] border border-[#FFC857]/40 rounded-3xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* HEADER SECTION */}
        <div className="relative p-6 sm:p-8 bg-gradient-to-b from-[#131926] to-[#0A0D14] border-b border-white/10 shrink-0">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFC857]/15 border border-[#FFC857]/40 text-[#FFC857] text-[11px] font-bold tracking-wider uppercase mb-2.5">
                <Award className="w-3.5 h-3.5" />
                <span>
                  {lang === 'bn' ? 'ভেরিফায়েড মার্চেন্ট ট্রাস্ট ও ভ্যালু ইনডেক্স' : 'VERIFIED MERCHANT TRUST & VALUE INDEX'}
                </span>
              </div>
              <h2 className="font-display text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                {lang === 'bn' ? 'জাতীয় শপ লিডারবোর্ড' : 'National Store Leaderboard'}
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl leading-relaxed">
                {lang === 'bn'
                  ? 'বাংলাদেশের নির্ভরযোগ্য রিটেইলারদের নিরপেক্ষ র্যাংকিং। সর্বনিম্ন বাজারদর, ট্রাস্টশিল্ড ভেরিফিকেশন এবং নির্দিষ্ট অফার বিশ্লেষণের ভিত্তিতে গাণিতিকভাবে নির্ধারিত।'
                  : 'Objective benchmark ranking of verified Bangladeshi retailers. Mathematically determined by lowest price frequency, TrustShield accreditation, and transparent deal savings.'}
              </p>
            </div>

            <button
              onClick={onClose}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white border border-white/10 transition cursor-pointer"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* FILTER CONTROLS */}
          <div className="mt-6 flex flex-col md:flex-row md:items-center justify-between gap-4 pt-4 border-t border-white/10">
            {/* PILLAR SELECTOR */}
            <div className="flex items-center gap-1.5 p-1 bg-white/5 rounded-xl border border-white/10 shrink-0">
              <button
                type="button"
                onClick={() => setSelectedPillar('price')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                  selectedPillar === 'price'
                    ? 'bg-[#FFC857] text-[#0A0D14] shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <TrendingDown className="w-3.5 h-3.5" />
                <span>{lang === 'bn' ? 'সেরা বাজারদর' : 'Price Champions'}</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedPillar('trust')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                  selectedPillar === 'trust'
                    ? 'bg-[#FFC857] text-[#0A0D14] shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>{lang === 'bn' ? 'নিরাপত্তা ও ট্রাস্ট' : 'TrustShield Safety'}</span>
              </button>

              <button
                type="button"
                onClick={() => setSelectedPillar('momentum')}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                  selectedPillar === 'momentum'
                    ? 'bg-[#FFC857] text-[#0A0D14] shadow-md'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Building2 className="w-3.5 h-3.5" />
                <span>{lang === 'bn' ? 'জনপ্রিয় স্টোর' : 'Shopper Momentum'}</span>
              </button>
            </div>

            {/* CATEGORY DROPDOWN MENU */}
            <div className="relative shrink-0" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setCatDropdownOpen((prev) => !prev)}
                className="flex items-center justify-between gap-3 px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-xl border border-white/15 transition cursor-pointer text-xs font-semibold min-w-[200px] sm:min-w-[240px] shadow-sm hover:border-[#FFC857]/50"
              >
                <div className="flex items-center gap-2 truncate">
                  <Layers className="w-3.5 h-3.5 text-[#FFC857] shrink-0" />
                  <span className="truncate">{activeCatLabel}</span>
                </div>
                <ChevronDown
                  className={`w-4 h-4 text-slate-400 transition-transform duration-200 shrink-0 ${
                    catDropdownOpen ? 'rotate-180 text-[#FFC857]' : ''
                  }`}
                />
              </button>

              {catDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 max-h-72 overflow-y-auto bg-[#0E131F]/95 backdrop-blur-xl border border-white/15 rounded-xl shadow-2xl py-1.5 z-50 text-xs custom-scrollbar">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedCat('all');
                      setCatDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3.5 py-2.5 flex items-center justify-between transition cursor-pointer ${
                      selectedCat === 'all'
                        ? 'bg-[#FFC857]/20 text-[#FFC857] font-bold'
                        : 'text-slate-300 hover:bg-white/5 hover:text-white'
                    }`}
                  >
                    <span>{lang === 'bn' ? 'সব ক্যাটাগরি' : 'All Categories'}</span>
                    {selectedCat === 'all' && <span className="w-1.5 h-1.5 rounded-full bg-[#FFC857]" />}
                  </button>

                  <div className="my-1 border-t border-white/10" />

                  {categoriesList
                    .filter((c) => c.id !== 'all')
                    .map((cat) => {
                      const isSelected = selectedCat === cat.id;
                      return (
                        <button
                          key={cat.id}
                          type="button"
                          onClick={() => {
                            setSelectedCat(cat.id);
                            setCatDropdownOpen(false);
                          }}
                          className={`w-full text-left px-3.5 py-2 flex items-center justify-between transition cursor-pointer ${
                            isSelected
                              ? 'bg-[#FFC857]/20 text-[#FFC857] font-bold'
                              : 'text-slate-300 hover:bg-white/5 hover:text-white'
                          }`}
                        >
                          <span className="truncate pr-2">{lang === 'bn' ? cat.bn : cat.en}</span>
                          {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-[#FFC857] shrink-0" />}
                        </button>
                      );
                    })}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* STORE LIST BODY */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 sm:p-8 space-y-4">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-center">
              <Loader2 className="w-10 h-10 text-[#FFC857] animate-spin mb-4" />
              <p className="text-sm text-slate-400 font-medium">
                {lang === 'bn'
                  ? 'মার্কেট ডাটা ও ভেরিফায়েড ডিল বিশ্লেষণ করা হচ্ছে...'
                  : 'Analyzing verified retailer metrics and crowning deals...'}
              </p>
            </div>
          ) : error ? (
            <div className="p-8 text-center bg-red-500/10 border border-red-500/20 rounded-2xl max-w-md mx-auto">
              <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-2" />
              <p className="text-xs text-red-300 mb-4">{error}</p>
              <button
                onClick={() => setSelectedCat('all')}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition"
              >
                Reset Filters
              </button>
            </div>
          ) : stores.length === 0 ? (
            <div className="py-16 text-center text-slate-500 text-sm">
              {lang === 'bn' ? 'কোনো স্টোর পাওয়া যায়নি।' : 'No stores found for this category.'}
            </div>
          ) : (
            stores.map((store) => {
              const rank = store.rank || 1;
              const isTop1 = rank === 1;
              const isTop2 = rank === 2;
              const isTop3 = rank === 3;

              const rankBadgeClass = isTop1
                ? 'bg-gradient-to-br from-[#FFC857] to-[#F59E0B] text-black shadow-lg shadow-[#FFC857]/20 border border-[#FFC857]'
                : isTop2
                ? 'bg-gradient-to-br from-[#E2E8F0] to-[#94A3B8] text-black border border-[#CBD5E1]'
                : isTop3
                ? 'bg-gradient-to-br from-[#F59E0B] to-[#B45309] text-white border border-[#D97706]'
                : 'bg-white/10 text-slate-300 border border-white/10';

              const cardBorder = isTop1
                ? 'border-[#FFC857]/40 bg-gradient-to-b from-[#181D2A] to-[#0E121B]'
                : 'border-white/10 bg-[#0E121B]';

              return (
                <div
                  key={store.store_name}
                  className={`p-5 sm:p-6 rounded-2xl border ${cardBorder} shadow-lg transition hover:border-white/20 flex flex-col gap-4`}
                >
                  {/* STORE HEADER ROW */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="flex items-center gap-3.5">
                      <div
                        className={`w-9 h-9 rounded-xl flex items-center justify-center font-extrabold text-sm shrink-0 ${rankBadgeClass}`}
                      >
                        #{rank}
                      </div>

                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="text-base sm:text-lg font-extrabold text-white tracking-tight">
                            {store.store_name}
                          </h3>
                          <span className="px-2 py-0.5 rounded-md bg-white/5 text-slate-400 text-[10px] font-semibold uppercase tracking-wider border border-white/10">
                            {store.category}
                          </span>
                        </div>

                        <div className="flex flex-wrap items-center gap-1.5 mt-1.5 text-[10px] font-semibold text-slate-400">
                          {store.badges?.map((badge, bIdx) => (
                            <span
                              key={bIdx}
                              className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            >
                              ✓ {badge}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* TRUSTSHIELD SCORE BADGE */}
                    <div className="flex items-center gap-2 self-start sm:self-center bg-[#07090E] px-3 py-1.5 rounded-xl border border-white/10">
                      <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                      <div className="text-left">
                        <span className="block text-[11px] font-black text-white">
                          {store.trust_score}/100
                        </span>
                        <span className="block text-[9px] text-slate-400 uppercase font-semibold">
                          TrustShield
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* CROWNING BENCHMARK DEAL BOX */}
                  {store.crowning_deal && (
                    <div className="p-4 rounded-xl bg-[#07090E] border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold text-[#FFC857] tracking-wider uppercase block">
                          {lang === 'bn'
                            ? 'যে স্পেসিফিক ডিলের মাধ্যমে শীর্ষে অবস্থান:'
                            : 'CROWNING BENCHMARK DEAL THAT WON THIS RANKING:'}
                        </span>

                        <div className="flex items-baseline gap-2 flex-wrap">
                          <span className="text-sm font-bold text-white">
                            {store.crowning_deal.product_title}
                          </span>
                          <span className="text-xs font-extrabold text-emerald-400">
                            ৳{store.crowning_deal.store_price?.toLocaleString()}
                          </span>

                          {store.crowning_deal.savings_bdt > 0 && (
                            <span className="text-[11px] font-semibold text-slate-400">
                              (৳{store.crowning_deal.savings_bdt?.toLocaleString()} below market average)
                            </span>
                          )}
                        </div>
                      </div>

                      {store.crowning_deal.product_slug && onSelectProductDeal && (
                        <button
                          type="button"
                          onClick={() => {
                            onClose();
                            onSelectProductDeal(store.crowning_deal.product_slug);
                          }}
                          className="px-3.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition flex items-center gap-1.5 shrink-0 cursor-pointer self-start sm:self-center"
                        >
                          <span>{lang === 'bn' ? 'ডিল যাচাই করুন' : 'View Comparison Deal'}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-[#FFC857]" />
                        </button>
                      )}
                    </div>
                  )}

                  {/* OUTBOUND REDIRECT LINKS ROW */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-white/5">
                    <span className="text-[11px] text-slate-400">
                      {lang === 'bn' ? 'সরাসরি শোরুমে প্রবেশ করুন:' : 'Direct Merchant Destinations:'}
                    </span>

                    <div className="flex items-center gap-2">
                      {store.website_url ? (
                        <a
                          href={store.website_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={() => trackOutboundClick(store.store_name, 'leaderboard_website', store.website_url)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-xs font-bold text-cyan-300 border border-cyan-500/30 transition cursor-pointer shadow-sm"
                        >
                          <Globe className="w-3.5 h-3.5 text-cyan-400" />
                          <span>{lang === 'bn' ? 'অফিসিয়াল ওয়েবসাইট' : 'Visit Website'}</span>
                          <ExternalLink className="w-3 h-3 text-cyan-400/60" />
                        </a>
                      ) : (
                        <span className="text-[10px] text-slate-400 italic">No web domain</span>
                      )}

                      {store.facebook_url && (
                        <a
                          href={store.facebook_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={() => trackOutboundClick(store.store_name, 'leaderboard_facebook', store.facebook_url)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-500/10 hover:bg-blue-500/20 text-xs font-bold text-blue-300 border border-blue-500/30 transition cursor-pointer shadow-sm"
                        >
                          <MessageCircle className="w-3.5 h-3.5 text-blue-400" />
                          <span>{lang === 'bn' ? 'ফেসবুক পেজ' : 'Facebook Page'}</span>
                          <ExternalLink className="w-3 h-3 text-blue-400/60" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* MODAL FOOTER */}
        <div className="p-4 bg-[#07090E] border-t border-white/10 flex items-center justify-between text-[11px] text-slate-400 shrink-0">
          <span>
            {lang === 'bn'
              ? 'বাজারদর ও ট্রাস্ট স্কোর সম্পূর্ণ নিরপেক্ষ এবং স্বয়ংক্রিয়ভাবে আপডেটেড।'
              : 'All rankings and TrustShield scores are mathematically independent and updated daily.'}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs transition cursor-pointer"
          >
            {lang === 'bn' ? 'ফিরে যান' : 'Back to Storefront'}
          </button>
        </div>
      </div>
    </div>
  );
}

