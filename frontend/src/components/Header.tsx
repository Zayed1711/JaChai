"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Search } from "lucide-react";

const CATEGORIES = [
  { label: "All", query: "" },
  { label: "Smartphones", query: "smartphone" },
  { label: "Men's Fashion", query: "shirt" },
  { label: "Electronics", query: "refrigerator" },
];

export default function Header() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const [searchTerm, setSearchTerm] = useState(initialQuery);

  useEffect(() => {
    setSearchTerm(initialQuery);
  }, [initialQuery]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      router.push(`/?q=${encodeURIComponent(searchTerm.trim())}`);
    } else {
      router.push("/");
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-[#101B2D] border-b border-[#DDE3EA]/20 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16 gap-4 sm:gap-8">
          
          {/* Logo: Official JaChai Logo */}
          <Link href="/" className="flex items-center gap-2.5 shrink-0 group">
            <img
              src="/logo.png"
              alt="JaChai"
              className="h-8 sm:h-9 w-auto object-contain transition-transform duration-200 group-hover:scale-[1.02]"
            />
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-[#C2410C] text-white border border-[#FB923C]/40 whitespace-nowrap">
              যাচাই
            </span>
          </Link>

          {/* Search Bar */}
          <form onSubmit={handleSubmit} className="flex-1 max-w-xl relative">
            <div className="relative flex items-center">
              <Search className="absolute left-3.5 w-4 h-4 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search products (e.g. S24 Ultra, Shirt, Walton)..."
                className="w-full pl-10 pr-24 py-2 bg-white border border-[#DDE3EA] rounded-xl text-sm text-[#101B2D] placeholder:text-slate-400 focus:outline-none focus:border-[#14B8A6] focus:ring-2 focus:ring-[#14B8A6]/20 transition-all"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchTerm("");
                    router.push("/");
                  }}
                  className="absolute right-20 text-xs text-slate-400 hover:text-slate-600"
                >
                  ✕
                </button>
              )}
              <button
                type="submit"
                className="absolute right-1 px-3.5 py-1.5 text-xs font-black bg-[#FFC857] hover:bg-[#F5BA3D] text-[#101B2D] rounded-lg transition-colors uppercase tracking-wider"
              >
                Compare
              </button>
            </div>
          </form>

          {/* Categories */}
          <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-slate-300">
            {CATEGORIES.map((cat) => {
              const isActive =
                cat.query === ""
                  ? !searchParams.get("q")
                  : searchParams.get("q")?.toLowerCase().includes(cat.query);
              return (
                <Link
                  key={cat.label}
                  href={cat.query ? `/?q=${cat.query}` : "/"}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    isActive
                      ? "bg-[#14B8A6] text-white font-semibold"
                      : "hover:text-white hover:bg-white/10"
                  }`}
                >
                  {cat.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
}
