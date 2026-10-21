"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  formatBDT,
  getProductOffers,
  ProductOffersResponse,
  PriceHistoryPoint,
} from "@/lib/api";
import OfferCard from "@/components/OfferCard";
import PriceHistoryChart from "@/components/PriceHistoryChart";
import { ArrowLeft, CheckCircle2 } from "lucide-react";

export default function ProductDetailPage() {
  const params = useParams();
  const slug = typeof params?.slug === "string" ? params.slug : "";
  const [data, setData] = useState<ProductOffersResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    if (slug) {
      setLoading(true);
      getProductOffers(slug)
        .then((res) => {
          if (isMounted) {
            setData(res);
            setLoading(false);
          }
        })
        .catch(() => {
          if (isMounted) setLoading(false);
        });
    }
    return () => {
      isMounted = false;
    };
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-5 animate-pulse">
        <div className="h-5 w-32 bg-white/10 rounded" />
        <div className="h-10 w-2/3 bg-white/10 rounded" />
        <div className="h-28 bg-white/5 rounded-xl border border-white/10" />
        <div className="h-40 bg-white/5 rounded-xl border border-white/10" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-md mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl font-black text-white uppercase tracking-tight">Product not found</h1>
        <p className="text-xs text-[#8A8F98] mt-2">We could not locate offers for this product.</p>
        <Link
          href="/"
          className="mt-5 inline-flex items-center gap-2 text-xs font-black tracking-wider uppercase text-[#00E57A] hover:underline"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Search
        </Link>
      </div>
    );
  }

  // Sorted offers (cheapest first)
  const sortedOffers = [...data.offers].sort((a, b) => a.current_price - b.current_price);
  const cheapestOffer = sortedOffers[0];

  // Aggregate price history
  const combinedHistory: PriceHistoryPoint[] = [];
  const seen = new Set<string>();
  sortedOffers.forEach((o) => {
    o.price_history.forEach((h) => {
      const key = `${h.price}_${h.captured_at.slice(0, 10)}`;
      if (!seen.has(key)) {
        seen.add(key);
        combinedHistory.push(h);
      }
    });
  });

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-6">
      
      {/* Breadcrumb */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold tracking-wider uppercase text-[#8A8F98] hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Search
        </Link>
      </div>

      {/* Product Title Header */}
      <div className="bg-[#12141A] rounded-xl p-6 sm:p-8 border border-white/10 space-y-2">
        <div className="flex items-center gap-2 text-xs font-bold tracking-wider uppercase text-[#00E57A]">
          <span>{data.category}</span>
          {data.brand && <span className="text-[#8A8F98]">• {data.brand}</span>}
          {data.model && <span className="text-white/40 font-mono">• {data.model}</span>}
        </div>
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight uppercase">
          {data.product_name}
        </h1>
      </div>

      {/* Lowest Price Callout */}
      <div className="bg-[#141820] border border-[#00E57A]/40 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-black tracking-widest text-[#00E57A] uppercase flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-[#00E57A]" />
            Lowest Price
          </span>
          <div className="text-3xl sm:text-4xl font-black text-white mt-1">
            {formatBDT(data.lowest_price)}
          </div>
          {cheapestOffer && (
            <p className="text-xs text-[#8A8F98] mt-1">
              Available at <strong className="font-bold text-white uppercase">{cheapestOffer.store_name}</strong>
            </p>
          )}
        </div>

        <div className="text-xs font-bold tracking-wider uppercase text-[#8A8F98] self-start sm:self-auto">
          {data.offers_count} stores compared
        </div>
      </div>

      {/* Price History Chart */}
      <PriceHistoryChart history={combinedHistory} productName={data.product_name} />

      {/* Store Offers List: Compare all stores */}
      <div className="space-y-3.5">
        <div className="flex items-center justify-between text-xs font-bold tracking-wider uppercase text-[#8A8F98]">
          <h2 className="text-white text-sm">Store Comparison ({sortedOffers.length})</h2>
          <span>Sorted by lowest price</span>
        </div>

        <div className="space-y-3.5">
          {sortedOffers.map((offer, idx) => (
            <OfferCard
              key={offer.listing_id}
              offer={offer}
              isLowestPrice={idx === 0}
            />
          ))}
        </div>
      </div>

      {/* Simple Note */}
      <p className="text-center text-xs text-[#8A8F98]/50 pt-6">
        Prices and delivery terms are source-stated by respective sellers. JaChai does not take commissions.
      </p>
    </div>
  );
}
