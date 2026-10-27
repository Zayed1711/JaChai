"use client";

import React from "react";
import dynamic from "next/dynamic";
import ErrorBoundary from "../components/ErrorBoundary";

const App = dynamic(() => import("../App"), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-[#F5F7FA] flex flex-col items-center justify-center text-[#101B2D] font-mono text-sm">
      <div className="w-10 h-10 border-4 border-[#0F766E] border-t-transparent rounded-full animate-spin mb-4" />
      <div className="font-bold tracking-widest text-xs uppercase text-[#64748B]">
        INITIALIZING JACHAI LIVE PRICING...
      </div>
    </div>
  ),
});

export default function HomePage() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
}
