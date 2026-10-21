"use client";

import React from "react";
import { formatBDT, PriceHistoryPoint } from "@/lib/api";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";

interface PriceHistoryChartProps {
  history: PriceHistoryPoint[];
  productName: string;
}

export default function PriceHistoryChart({ history, productName }: PriceHistoryChartProps) {
  if (!history || history.length === 0) {
    return (
      <div className="bg-[#FFFFFF] rounded-xl p-6 border border-[#DDE3EA] text-center text-[#334155] text-sm">
        No price history recorded yet for {productName}.
      </div>
    );
  }

  // Sort chronological
  const sorted = [...history].sort(
    (a, b) => new Date(a.captured_at).getTime() - new Date(b.captured_at).getTime()
  );

  const prices = sorted.map((p) => p.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const firstPrice = sorted[0].price;
  const latestPrice = sorted[sorted.length - 1].price;
  const priceDiff = latestPrice - firstPrice;

  // Chart dimensions
  const width = 560;
  const height = 140;
  const paddingX = 40;
  const paddingY = 24;

  const plotWidth = width - paddingX * 2;
  const plotHeight = height - paddingY * 2;
  const priceRange = maxPrice === minPrice ? 1 : maxPrice - minPrice;

  const points = sorted.map((pt, i) => {
    const x =
      sorted.length === 1
        ? width / 2
        : paddingX + (i / (sorted.length - 1)) * plotWidth;
    const y =
      maxPrice === minPrice
        ? height / 2
        : paddingY + plotHeight - ((pt.price - minPrice) / priceRange) * plotHeight;
    return { x, y, price: pt.price, date: pt.captured_at };
  });

  const pathData = points.reduce((acc, curr, idx) => {
    return idx === 0 ? `M ${curr.x} ${curr.y}` : `${acc} L ${curr.x} ${curr.y}`;
  }, "");

  return (
    <div className="bg-[#FFFFFF] rounded-xl p-6 border border-[#DDE3EA] shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5">
        <div>
          <h3 className="font-black text-[#101B2D] text-base uppercase tracking-tight">Price Trend</h3>
          <p className="text-xs text-[#334155]">Historical verified snapshots</p>
        </div>

        {priceDiff < 0 && (
          <span className="inline-flex items-center gap-1.5 text-xs font-black tracking-wider uppercase px-3 py-1 rounded bg-[#DCFCE7] text-[#166534] border border-[#166534]/20">
            <TrendingDown className="w-3.5 h-3.5" />
            Dropped {formatBDT(Math.abs(priceDiff))}
          </span>
        )}
        {priceDiff > 0 && (
          <span className="inline-flex items-center gap-1.5 text-xs font-black tracking-wider uppercase px-3 py-1 rounded bg-[#FEE2E2] text-[#B91C1C] border border-[#B91C1C]/20">
            <TrendingUp className="w-3.5 h-3.5" />
            Increased {formatBDT(priceDiff)}
          </span>
        )}
        {priceDiff === 0 && (
          <span className="inline-flex items-center gap-1 text-xs font-bold tracking-wider uppercase text-[#334155]">
            <Minus className="w-3.5 h-3.5" /> Price stable
          </span>
        )}
      </div>

      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto max-h-[160px]">
          {/* Subtle baseline */}
          <line
            x1={paddingX}
            y1={height - paddingY}
            x2={width - paddingX}
            y2={height - paddingY}
            stroke="#DDE3EA"
            strokeWidth="1"
          />

          {/* Line */}
          {pathData && (
            <path
              d={pathData}
              fill="none"
              stroke="#14B8A6"
              strokeWidth="2.5"
              strokeLinecap="round"
            />
          )}

          {/* Points */}
          {points.map((pt, idx) => {
            const dateStr = new Date(pt.date).toLocaleDateString("en-GB", {
              month: "short",
              day: "numeric",
            });
            return (
              <g key={idx}>
                <circle cx={pt.x} cy={pt.y} r="4" fill="#FFFFFF" stroke="#14B8A6" strokeWidth="2.5" />
                <text x={pt.x} y={pt.y - 10} textAnchor="middle" className="text-[11px] font-bold fill-[#101B2D]">
                  {formatBDT(pt.price)}
                </text>
                <text x={pt.x} y={height - paddingY + 16} textAnchor="middle" className="text-[10px] fill-[#334155]">
                  {dateStr}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
