'use client';

import React from 'react';

/**
 * Reusable JaChai Brand Logo Component
 * Uses the official brand logo from Resources/logo.png
 */
export default function JaChaiLogo({
  onTap,
  showMotto = true,
  className = '',
  size = 'default',
}) {
  const isCompact = size === 'compact';

  const handleClick = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (typeof onTap === 'function') {
      onTap();
    }
  };

  return (
    <div
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick(e);
        }
      }}
      className={`flex items-center gap-2 sm:gap-3 cursor-pointer select-none group focus:outline-none ${className}`}
      title="JaChai — যা চাই, করুন যাচাই (Return to Homepage)"
    >
      {/* Official JaChai Graphic Logo */}
      <img
        src="/logo.png"
        alt="JaChai"
        className={`object-contain transition-transform duration-200 group-hover:scale-[1.02] cursor-pointer ${
          isCompact ? 'h-6 sm:h-7 w-auto' : 'h-8 sm:h-9 lg:h-10 w-auto'
        }`}
      />

      {/* Official Motto Pill Badge: "যা চাই, করুন যাচাই" */}
      {showMotto && (
        <span
          className={`rounded-full bg-white border border-[#14532D]/30 text-[#14532D] font-extrabold tracking-wide shadow-md whitespace-nowrap cursor-pointer ${
            isCompact
              ? 'px-2 py-0.5 text-[9px]'
              : 'px-2.5 sm:px-3 py-0.5 sm:py-1 text-[10px] sm:text-[11px]'
          }`}
        >
          যা চাই, করুন যাচাই
        </span>
      )}
    </div>
  );
}
