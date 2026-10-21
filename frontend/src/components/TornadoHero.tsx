"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { Flame, ArrowRight, ShieldCheck, Sparkles } from "lucide-react";

interface BillboardCard {
  id: string;
  tag: string;
  tagColor: string;
  title: string;
  subtitle: string;
  priceNote: string;
  slug: string;
  badge: string;
  bgGradient: string;
}

const BILLBOARD_ITEMS: BillboardCard[] = [
  {
    id: "tornado-1",
    tag: "Lowest Price In Bangladesh",
    tagColor: "bg-orange-500 text-white",
    title: "Samsung Galaxy S24 Ultra",
    subtitle: "Titanium Gray 12GB/256GB • 1 Year Official BD Warranty",
    priceNote: "From ৳ 1,39,999 (Saved ৳ 30,000 on DarazMall)",
    slug: "samsung-galaxy-s24-ultra",
    badge: "Daraz vs Star Tech Verified",
    bgGradient: "from-slate-900 via-indigo-950 to-emerald-950",
  },
  {
    id: "tornado-2",
    tag: "Viral F-Commerce Trend",
    tagColor: "bg-emerald-500 text-white",
    title: "Old Money Textured Cuban Collar Shirt",
    subtitle: "Breathable Waffle Knit • Cash on Delivery inside Dhaka ৳60",
    priceNote: "From ৳ 1,850 (Original ৳ 2,500)",
    slug: "old-money-textured-cuban-collar-shirt",
    badge: "Verified F-Commerce Page",
    bgGradient: "from-amber-950 via-stone-900 to-emerald-950",
  },
  {
    id: "tornado-3",
    tag: "Mega Campaign Sponsored",
    tagColor: "bg-purple-600 text-white",
    title: "Daraz 11.11 & Tech Deals Preview",
    subtitle: "Real-time crawler verified discounts across 10,000+ local sellers",
    priceNote: "Real Price Drop Tracker Enabled",
    slug: "samsung-galaxy-s24-ultra",
    badge: "Zero Fake Discounts",
    bgGradient: "from-purple-950 via-slate-900 to-zinc-950",
  },
];

export default function TornadoHero() {
  const [activeIndex, setActiveIndex] = useState(0);
  const [scrollY, setScrollY] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Scroll reaction to produce dynamic 3D tornado skew
  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        // Offset scroll relative to component top
        setScrollY(rect.top);
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Auto-advance billboard
  useEffect(() => {
    const timer = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % BILLBOARD_ITEMS.length);
    }, 4500);
    return () => clearInterval(timer);
  }, []);

  // Compute dynamic 3D scroll tilt
  const scrollTilt = Math.max(-12, Math.min(12, scrollY * 0.03));

  return (
    <div
      ref={containerRef}
      className="relative overflow-hidden py-6 sm:py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto"
      style={{ perspective: "1200px" }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-800">
          <Flame className="w-4 h-4 text-orange-500 animate-pulse" />
          <span>Tornado Billboard • Real-Time Deal Tracker</span>
        </div>
        <div className="flex items-center gap-1.5">
          {BILLBOARD_ITEMS.map((_, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setActiveIndex(idx)}
              className={`h-1.5 transition-all rounded-full ${
                idx === activeIndex
                  ? "w-6 bg-emerald-600"
                  : "w-1.5 bg-gray-200 hover:bg-gray-300"
              }`}
              aria-label={`Slide ${idx + 1}`}
            />
          ))}
        </div>
      </div>

      {/* 3D Carousel Stage */}
      <div
        className="relative h-[220px] sm:h-[250px] transition-transform duration-500 ease-out"
        style={{
          transformStyle: "preserve-3d",
          transform: `rotateX(${scrollTilt}deg)`,
        }}
      >
        {BILLBOARD_ITEMS.map((item, index) => {
          const offset = (index - activeIndex + BILLBOARD_ITEMS.length) % BILLBOARD_ITEMS.length;

          // Tornado math: rotateY and depth translation
          let rotateY = 0;
          let translateZ = 0;
          let translateX = 0;
          let scale = 1;
          let opacity = 0;
          let zIndex = 0;

          if (offset === 0) {
            // Front active card
            rotateY = 0;
            translateZ = 0;
            translateX = 0;
            scale = 1;
            opacity = 1;
            zIndex = 30;
          } else if (offset === 1) {
            // Right trailing card
            rotateY = -22;
            translateZ = -90;
            translateX = 45;
            scale = 0.92;
            opacity = 0.75;
            zIndex = 20;
          } else if (offset === BILLBOARD_ITEMS.length - 1) {
            // Left trailing card
            rotateY = 22;
            translateZ = -90;
            translateX = -45;
            scale = 0.92;
            opacity = 0.75;
            zIndex = 20;
          }

          return (
            <div
              key={item.id}
              onClick={() => setActiveIndex(index)}
              className="absolute inset-0 rounded-2xl cursor-pointer p-6 sm:p-8 flex flex-col justify-between shadow-xl transition-all duration-700 ease-out border border-white/10"
              style={{
                transform: `translateX(${translateX}%) translateZ(${translateZ}px) rotateY(${rotateY}deg) scale(${scale})`,
                opacity,
                zIndex,
                pointerEvents: offset === 0 ? "auto" : "auto",
                background: `linear-gradient(135deg, var(--tw-gradient-stops))`,
              }}
            >
              {/* Card Inner Background */}
              <div
                className={`absolute inset-0 rounded-2xl bg-linear-to-br ${item.bgGradient} opacity-95 -z-10`}
              />

              {/* Header Badges */}
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-md tracking-wide ${item.tagColor}`}>
                    {item.tag}
                  </span>
                  <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-300 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded-md">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                    {item.badge}
                  </span>
                </div>
                <span className="text-white/60 text-xs font-mono">
                  #0{index + 1}
                </span>
              </div>

              {/* Title & Price Information */}
              <div className="my-auto">
                <h2 className="text-xl sm:text-3xl font-black text-white tracking-tight line-clamp-1">
                  {item.title}
                </h2>
                <p className="text-xs sm:text-sm text-gray-300 line-clamp-1 mt-1">
                  {item.subtitle}
                </p>
                <div className="mt-3 flex items-center gap-2">
                  <span className="text-sm sm:text-base font-bold text-orange-400 bg-orange-950/60 border border-orange-500/30 px-2.5 py-1 rounded-lg">
                    {item.priceNote}
                  </span>
                </div>
              </div>

              {/* Action Link */}
              <div className="flex items-center justify-between pt-2 border-t border-white/10">
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                  Deterministic price crawl
                </span>
                <Link
                  href={`/p/${item.slug}`}
                  className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-xl transition-all shadow-md hover:translate-x-0.5"
                >
                  Compare Prices
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

