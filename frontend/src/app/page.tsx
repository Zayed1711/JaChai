"use client";

import React, { Suspense } from "react";
import App from "../App";

export default function HomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#F5F7FA] flex items-center justify-center text-[#101B2D] font-mono text-sm">INITIALIZING JACHAI...</div>}>
      <App />
    </Suspense>
  );
}