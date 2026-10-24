"use client";

import React from "react";
import { formatBDT, StoreOfferItem } from "@/lib/api";
import { ExternalLink, Check, Clock } from "lucide-react";

interface OfferCardProps {
  offer: StoreOfferItem;
  isLowestPrice?: boolean;
}

export default function OfferCard({ offer, isLowestPrice = false }: OfferCardProps) {
  const deliveryText =
    offer.delivery_charge === null
      ? "Delivery at checkout"
      : offer.delivery_charge === 0
      ? "Free Delivery"
      : `৳${offer.delivery_charge} Delivery`;

  const outboundUrl = offer.source_url || offer.redirect_url || `/go/${offer.listing_id}`;
  const isHighRisk = offer.risk_level === "high" || Boolean(offer.trust_badge && offer.trust_badge.includes("Risk"));

  return (
    <div
      className={`rounded-xl p-6 border transition-all ${
        isHighRisk
          ? "bg-rose-50/70 border-2 border-rose-500 shadow-md ring-1 ring-rose-500/20"
          : isLowestPrice
          ? "bg-[#FFFFFF] border-2 border-[#14B8A6] shadow-md ring-1 ring-[#14B8A6]/20"
          : "bg-[#FFFFFF] border-[#DDE3EA] hover:border-[#14B8A6]/60 shadow-xs hover:shadow-sm"
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
        {/* Store & Product Information */}
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-black text-[#101B2D] text-lg tracking-tight uppercase">
              {offer.store_name}
            </span>
            {isLowestPrice && (
              isHighRisk ? (
                <span className="bg-rose-100 text-rose-700 border border-rose-300 text-[10px] font-black tracking-[0.18em] uppercase px-2.5 py-0.5 rounded flex items-center gap-1">
                  ⚠️ SUSPICIOUS LOW PRICE (RISKY)
                </span>
              ) : (
                <span className="bg-[#DCFCE7] text-[#166534] border border-[#166534]/20 text-[10px] font-black tracking-[0.18em] uppercase px-2.5 py-0.5 rounded">
                  LOWEST PRICE
                </span>
              )
            )}
            {offer.is_preseeded === false ? (
              <span className="bg-amber-100 text-amber-900 border border-amber-300 text-[10px] font-black uppercase px-2.5 py-0.5 rounded flex items-center gap-1 shadow-xs">
                ⚠️ UNVERIFIED MERCHANT · COD ONLY
              </span>
            ) : (
              <span className="bg-[#DCFCE7] text-[#166534] border border-[#166534]/20 text-[10px] font-bold uppercase px-2 py-0.5 rounded flex items-center gap-1">
                ✓ VERIFIED STORE
              </span>
            )}
            {offer.trust_badge && (
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                isHighRisk
                  ? "bg-rose-100 text-rose-700 border-rose-300"
                  : "bg-sky-50 text-sky-700 border-sky-200"
              }`}>
                {offer.trust_badge}
              </span>
            )}
            <span className="text-xs text-[#334155]">
              • {offer.store_type === "marketplace" ? "MARKETPLACE" : offer.store_type === "facebook_page" ? "F-COMMERCE" : "WEB STORE"}
            </span>
          </div>

          <p className="text-sm text-[#334155] line-clamp-1 font-medium">
            {offer.raw_title}
          </p>

          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-[#334155]">
            <span className="flex items-center gap-1 text-[#166534] font-semibold">
              <Check className="w-3.5 h-3.5" />
              {deliveryText}
            </span>
            {offer.cod_available && <span>• Cash on Delivery</span>}
            {offer.warranty_text && <span>• {offer.warranty_text}</span>}
            {offer.is_stale && (
              <span className="text-[#92400E] bg-[#FEF3C7] px-1.5 py-0.5 rounded flex items-center gap-1">
                <Clock className="w-3 h-3" /> Updated recently
              </span>
            )}
          </div>
        </div>

        {/* Price & Action */}
        <div className="flex sm:flex-col items-baseline sm:items-end justify-between sm:justify-center gap-3 pt-3 sm:pt-0 border-t sm:border-t-0 border-[#DDE3EA]">
          <div className="text-left sm:text-right">
            <div className={`text-2xl sm:text-3xl font-black tracking-tight text-[#101B2D]`}>
              {formatBDT(offer.current_price)}
            </div>
            {offer.original_price && offer.original_price > offer.current_price && (
              <span className="text-xs text-slate-400 line-through">
                {formatBDT(offer.original_price)}
              </span>
            )}
          </div>

          <a
            href={outboundUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center gap-1.5 px-5 py-3 text-xs font-black tracking-[0.18em] uppercase rounded-lg transition-all ${
              isLowestPrice
                ? "bg-[#FFC857] text-[#101B2D] hover:bg-[#F5BA3D] shadow-sm"
                : "border border-[#101B2D] text-[#101B2D] hover:bg-[#101B2D] hover:text-white"
            }`}
          >
            VISIT STORE
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
