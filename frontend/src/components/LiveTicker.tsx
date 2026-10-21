import React, { useEffect, useState } from 'react';

export default function LiveTicker() {
  const [ticker, setTicker] = useState({
    gold_22k_price: "৳1,18,500 / bhori",
    petrol_price: "৳125 / L",
    diesel_price: "৳105 / L",
    octane_price: "৳130 / L"
  });

  const fetchTickerData = async () => {
    try {
      const res = await fetch('/api/v1/macro-ticker');
      const data = await res.json();
      if (data) setTicker(data);
    } catch (e) {
      console.error("Failed to load live ticker macro data", e);
    }
  };

  useEffect(() => {
    fetchTickerData();
    const interval = setInterval(fetchTickerData, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 text-amber-400 py-2 px-4 text-sm overflow-hidden whitespace-nowrap flex items-center justify-between border-b border-slate-800 shadow-inner">
      <div className="flex space-x-8 items-center animate-pulse">
        <span className="flex items-center gap-1 font-medium">🏆 BAJUS Gold (22K): <strong>{ticker.gold_22k_price}</strong></span>
        <span className="text-slate-600">•</span>
        <span className="flex items-center gap-1 font-medium">⛽ Petrol: <strong>{ticker.petrol_price}</strong></span>
        <span className="text-slate-600">•</span>
        <span className="flex items-center gap-1 font-medium">Octane: <strong>{ticker.octane_price}</strong></span>
        <span className="text-slate-600">•</span>
        <span className="flex items-center gap-1 font-medium">Diesel: <strong>{ticker.diesel_price}</strong></span>
      </div>
      <div className="text-xs text-slate-400 hidden md:block">
        JaChai Market Intelligence & Live Macro Index
      </div>
    </div>
  );
}
