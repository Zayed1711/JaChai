"use client";

import React, { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ArrowUpRight, Zap, Shield, Sparkles, Crosshair } from "lucide-react";

export default function ScrollBillboard() {
  const containerRef = useRef<HTMLDivElement>(null);

  // Map scroll progress across the 300vh height
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  // Frame 1: Walton Refrigerator (Progress 0.0 - 0.33)
  const opacity1 = useTransform(scrollYProgress, [0, 0.22, 0.33], [1, 1, 0]);
  const y1 = useTransform(scrollYProgress, [0, 0.22, 0.33], [0, 0, -90]);
  const scale1 = useTransform(scrollYProgress, [0, 0.22, 0.33], [1, 1, 0.94]);

  // Frame 2: Samsung Galaxy S24 Ultra (Progress 0.33 - 0.66)
  const opacity2 = useTransform(scrollYProgress, [0.30, 0.40, 0.60, 0.70], [0, 1, 1, 0]);
  const y2 = useTransform(scrollYProgress, [0.30, 0.40, 0.60, 0.70], [90, 0, 0, -90]);
  const scale2 = useTransform(scrollYProgress, [0.30, 0.40, 0.60, 0.70], [0.92, 1, 1, 0.94]);

  // Frame 3: bKash Cashback Offer (Progress 0.66 - 1.0)
  const opacity3 = useTransform(scrollYProgress, [0.65, 0.75, 1], [0, 1, 1]);
  const y3 = useTransform(scrollYProgress, [0.65, 0.75, 1], [90, 0, 0]);
  const scale3 = useTransform(scrollYProgress, [0.65, 0.75, 1], [0.92, 1, 1]);

  return (
    <div
      ref={containerRef}
      className="relative min-h-[300vh] bg-[#0F1115] text-white selection:bg-[#00F59B] selection:text-black"
    >
      {/* Viewport Locker: Sticky full-screen container */}
      <div className="sticky top-0 h-screen w-full overflow-hidden flex items-center justify-center px-4 sm:px-8">
        
        {/* Subtle Tactical Background Grid Lines */}
        <div className="absolute inset-0 pointer-events-none opacity-15 bg-[radial-gradient(#00F59B_1px,transparent_1px)] [background-size:32px_32px]" />
        
        {/* Top & Bottom Cinematic Edge Bars */}
        <div className="absolute top-6 left-6 right-6 flex items-center justify-between text-xs font-mono tracking-widest text-emerald-400/70 border-b border-white/10 pb-3 pointer-events-none">
          <div className="flex items-center gap-2">
            <Crosshair className="w-4 h-4 text-[#00F59B]" />
            <span>BILLBOARD_SYS // SECTOR_01</span>
          </div>
          <span className="hidden sm:inline">LIVE SCROLL INTERPOLATION • BANGLADESH CRAWLER</span>
          <span className="text-[#00F59B]">ONLINE // 100% DETERMINISTIC</span>
        </div>

        {/* Scroll Progress Bar at Side */}
        <div className="absolute right-6 top-1/2 -translate-y-1/2 hidden lg:flex flex-col items-center gap-3 text-xs font-mono text-zinc-500 pointer-events-none">
          <span>01</span>
          <div className="w-1 h-32 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              style={{ scaleY: scrollYProgress, originY: 0 }}
              className="w-full h-full bg-[#00F59B] shadow-[0_0_12px_#00F59B]"
            />
          </div>
          <span>03</span>
        </div>

        {/* ========================================================= */}
        {/* AD FRAME 1: WALTON INVERTER REFRIGERATOR                   */}
        {/* ========================================================= */}
        <motion.div
          style={{ opacity: opacity1, y: y1, scale: scale1 }}
          className="absolute inset-0 max-w-7xl mx-auto flex flex-col justify-center px-4 sm:px-12 py-16"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Content Column */}
            <div className="lg:col-span-7 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-none border border-[#00F59B]/40 bg-emerald-950/40 text-[#00F59B] text-xs font-mono font-bold tracking-widest uppercase">
                <Zap className="w-3.5 h-3.5" />
                WALTON APPLIANCES // INVERTER SERIES
              </div>

              <div className="space-y-1">
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-white">
                  ULTRA COOLING.
                </h2>
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-[#00F59B] to-teal-300">
                  ZERO COMPROMISE.
                </h2>
              </div>

              <p className="text-sm sm:text-lg text-zinc-400 font-medium max-w-xl leading-relaxed">
                550L Direct Cool with Intelligent Inverter Compressor. Save up to 60% electricity with a 12-Year Official Compressor Warranty.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  MARKET SPREAD: <span className="text-[#00F59B] font-bold">SAVE ৳ 14,500</span>
                </div>
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  NATIONWIDE FREE DELIVERY
                </div>
              </div>

              <div className="pt-4 flex items-center gap-4">
                <a
                  href="/p/walton-inverter-refrigerator"
                  className="group relative inline-flex items-center gap-3 bg-[#00F59B] text-black font-black uppercase tracking-widest text-sm sm:text-base px-8 py-4 rounded-none skew-x-[-6deg] hover:bg-white hover:text-black transition-all shadow-[0_0_30px_rgba(0,245,155,0.5)] active:scale-95 cursor-pointer"
                >
                  <span className="skew-x-[6deg] flex items-center gap-2">
                    CLAIM DEAL // ৳ 42,990
                    <ArrowUpRight className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </span>
                </a>
                <span className="text-xs font-mono text-zinc-500">FRAME 01 / 03</span>
              </div>
            </div>

            {/* Right Product Cutout Graphic */}
            <div className="lg:col-span-5 relative flex items-center justify-center">
              <div className="relative w-full max-w-md aspect-square rounded-3xl bg-gradient-to-tr from-emerald-950/60 via-zinc-900/80 to-transparent border border-white/10 p-8 flex flex-col justify-between overflow-hidden shadow-2xl">
                <div className="flex justify-between items-start text-xs font-mono text-emerald-400">
                  <span>W-INV-550L</span>
                  <span className="px-2 py-0.5 bg-emerald-500/20 rounded">A+++ ENERGY</span>
                </div>
                
                {/* Stylized Product Cutout Silhouette */}
                <div className="my-auto text-center space-y-2 py-8">
                  <div className="w-28 h-56 mx-auto bg-gradient-to-b from-zinc-800 via-zinc-900 to-black rounded-lg border-2 border-emerald-500/40 shadow-[0_0_40px_rgba(0,245,155,0.2)] flex flex-col justify-between p-3">
                    <div className="w-full h-1 bg-emerald-500/80 rounded" />
                    <div className="text-[10px] font-mono text-zinc-500 tracking-widest">WALTON</div>
                    <div className="w-4 h-12 bg-zinc-700/60 rounded-xs ml-auto" />
                  </div>
                  <div className="text-xs font-mono text-zinc-400 tracking-wider">
                    DEEP FROST • ACTIVE DEODORIZER
                  </div>
                </div>

                <div className="flex justify-between items-end text-xs font-mono text-zinc-500 border-t border-white/10 pt-3">
                  <span>VERIFIED BY: DARAZ + WALTON BD</span>
                  <span className="text-[#00F59B] font-bold">IN STOCK</span>
                </div>
              </div>
            </div>

          </div>
        </motion.div>

        {/* ========================================================= */}
        {/* AD FRAME 2: SAMSUNG GALAXY S24 ULTRA                       */}
        {/* ========================================================= */}
        <motion.div
          style={{ opacity: opacity2, y: y2, scale: scale2 }}
          className="absolute inset-0 max-w-7xl mx-auto flex flex-col justify-center px-4 sm:px-12 py-16 pointer-events-none data-[active=true]:pointer-events-auto"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Content Column */}
            <div className="lg:col-span-7 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-none border border-[#00F59B]/40 bg-emerald-950/40 text-[#00F59B] text-xs font-mono font-bold tracking-widest uppercase">
                <Sparkles className="w-3.5 h-3.5" />
                FLAGSHIP SPOTLIGHT // 200MP AI SENSOR
              </div>

              <div className="space-y-1">
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-white">
                  TITANIUM POWER.
                </h2>
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-300 to-[#00F59B]">
                  SMARTEST PRICE.
                </h2>
              </div>

              <p className="text-sm sm:text-lg text-zinc-400 font-medium max-w-xl leading-relaxed">
                Snapdragon 8 Gen 3 with Galaxy AI, 12GB/256GB Titanium Gray. Real-time crawler analysis shows authentic ৳ 30,000 drop from launch price.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  LOWEST SPREAD: <span className="text-[#00F59B] font-bold">৳ 1,39,999</span> (REG. ৳ 1,69,999)
                </div>
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  OFFICIAL BD WARRANTY
                </div>
              </div>

              <div className="pt-4 flex items-center gap-4 pointer-events-auto">
                <a
                  href="/p/samsung-galaxy-s24-ultra"
                  className="group relative inline-flex items-center gap-3 bg-[#00F59B] text-black font-black uppercase tracking-widest text-sm sm:text-base px-8 py-4 rounded-none skew-x-[-6deg] hover:bg-white hover:text-black transition-all shadow-[0_0_30px_rgba(0,245,155,0.5)] active:scale-95 cursor-pointer"
                >
                  <span className="skew-x-[6deg] flex items-center gap-2">
                    CLAIM DEAL // ৳ 1,39,999
                    <ArrowUpRight className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </span>
                </a>
                <span className="text-xs font-mono text-zinc-500">FRAME 02 / 03</span>
              </div>
            </div>

            {/* Right Product Cutout Graphic */}
            <div className="lg:col-span-5 relative flex items-center justify-center">
              <div className="relative w-full max-w-md aspect-square rounded-3xl bg-gradient-to-tr from-amber-950/40 via-zinc-900/80 to-emerald-950/40 border border-white/10 p-8 flex flex-col justify-between overflow-hidden shadow-2xl">
                <div className="flex justify-between items-start text-xs font-mono text-orange-400">
                  <span>SM-S928B/DS</span>
                  <span className="px-2 py-0.5 bg-orange-500/20 text-orange-300 rounded">200MP QUAD-CAM</span>
                </div>
                
                {/* Stylized Phone Silhouette */}
                <div className="my-auto text-center space-y-2 py-6">
                  <div className="w-36 h-56 mx-auto bg-gradient-to-b from-zinc-700 via-zinc-900 to-black rounded-2xl border-2 border-orange-500/40 shadow-[0_0_40px_rgba(249,115,22,0.2)] flex flex-col justify-between p-3 relative">
                    <div className="absolute top-2 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-zinc-800 border border-zinc-600" />
                    <div className="mt-6 flex flex-col gap-1 items-start pl-1">
                      <div className="w-4 h-4 rounded-full bg-zinc-950 border border-zinc-700" />
                      <div className="w-4 h-4 rounded-full bg-zinc-950 border border-zinc-700" />
                      <div className="w-4 h-4 rounded-full bg-zinc-950 border border-zinc-700" />
                    </div>
                    <div className="text-[10px] font-mono text-zinc-400 tracking-widest text-center">
                      SAMSUNG
                    </div>
                  </div>
                  <div className="text-xs font-mono text-zinc-400 tracking-wider">
                    TITANIUM GRAY • S-PEN INCLUDED
                  </div>
                </div>

                <div className="flex justify-between items-end text-xs font-mono text-zinc-500 border-t border-white/10 pt-3">
                  <span>DARAZMALL VS STAR TECH</span>
                  <span className="text-[#00F59B] font-bold">2 STORES ACTIVE</span>
                </div>
              </div>
            </div>

          </div>
        </motion.div>

        {/* ========================================================= */}
        {/* AD FRAME 3: BKASH CASHBACK & VOUCHER                       */}
        {/* ========================================================= */}
        <motion.div
          style={{ opacity: opacity3, y: y3, scale: scale3 }}
          className="absolute inset-0 max-w-7xl mx-auto flex flex-col justify-center px-4 sm:px-12 py-16 pointer-events-none data-[active=true]:pointer-events-auto"
        >
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Content Column */}
            <div className="lg:col-span-7 space-y-5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-none border border-pink-500/40 bg-pink-950/40 text-pink-400 text-xs font-mono font-bold tracking-widest uppercase">
                <Shield className="w-3.5 h-3.5" />
                PAYMENT PARTNER // INSTANT REBATE
              </div>

              <div className="space-y-1">
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-white">
                  EXTRA 15% CASHBACK.
                </h2>
                <h2 className="text-5xl sm:text-7xl lg:text-8xl font-black uppercase tracking-tighter leading-none text-transparent bg-clip-text bg-gradient-to-r from-pink-500 via-rose-400 to-[#00F59B]">
                  TAP &amp; SAVE.
                </h2>
              </div>

              <p className="text-sm sm:text-lg text-zinc-400 font-medium max-w-xl leading-relaxed">
                Pay with bKash on any JaChai verified store to unlock an instant 15% cashback rebate up to ৳ 1,500. Zero convenience fees, credited directly to wallet.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-2">
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  CODE: <span className="text-[#00F59B] font-bold">BKASH15</span>
                </div>
                <div className="px-4 py-2 bg-zinc-900/90 border border-white/10 font-mono text-xs sm:text-sm text-zinc-300">
                  ALL ONLINE &amp; F-COMMERCE STORES
                </div>
              </div>

              <div className="pt-4 flex items-center gap-4 pointer-events-auto">
                <a
                  href="/?q=bkash"
                  className="group relative inline-flex items-center gap-3 bg-[#00F59B] text-black font-black uppercase tracking-widest text-sm sm:text-base px-8 py-4 rounded-none skew-x-[-6deg] hover:bg-white hover:text-black transition-all shadow-[0_0_30px_rgba(0,245,155,0.5)] active:scale-95 cursor-pointer"
                >
                  <span className="skew-x-[6deg] flex items-center gap-2">
                    CLAIM REBATE // BKASH15
                    <ArrowUpRight className="w-5 h-5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                  </span>
                </a>
                <span className="text-xs font-mono text-zinc-500">FRAME 03 / 03</span>
              </div>
            </div>

            {/* Right Vault Cutout Graphic */}
            <div className="lg:col-span-5 relative flex items-center justify-center">
              <div className="relative w-full max-w-md aspect-square rounded-3xl bg-gradient-to-tr from-pink-950/40 via-zinc-900/80 to-emerald-950/40 border border-white/10 p-8 flex flex-col justify-between overflow-hidden shadow-2xl">
                <div className="flex justify-between items-start text-xs font-mono text-pink-400">
                  <span>BKASH-OFFICIAL-PROMO</span>
                  <span className="px-2 py-0.5 bg-pink-500/20 text-pink-300 rounded">INSTANT CREDIT</span>
                </div>
                
                {/* Stylized Digital Vault Graphic */}
                <div className="my-auto text-center space-y-3 py-6">
                  <div className="w-36 h-36 mx-auto rounded-full bg-gradient-to-tr from-pink-600 via-rose-500 to-[#00F59B] p-1 shadow-[0_0_50px_rgba(236,72,153,0.3)] flex items-center justify-center">
                    <div className="w-full h-full rounded-full bg-black flex flex-col items-center justify-center">
                      <span className="text-3xl font-black text-white">15%</span>
                      <span className="text-[10px] font-mono text-[#00F59B] tracking-widest uppercase">CASHBACK</span>
                    </div>
                  </div>
                  <div className="text-xs font-mono text-zinc-300 tracking-wider">
                    AUTOMATIC CHECKOUT REBATE
                  </div>
                </div>

                <div className="flex justify-between items-end text-xs font-mono text-zinc-500 border-t border-white/10 pt-3">
                  <span>VALID ACROSS BANGLADESH</span>
                  <span className="text-[#00F59B] font-bold">LIMITED TIME</span>
                </div>
              </div>
            </div>

          </div>
        </motion.div>

      </div>
    </div>
  );
}

