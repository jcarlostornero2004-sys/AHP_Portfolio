"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getHeatmapData } from "../../lib/api";
import { AppLayout } from "../../components/layout/AppLayout";
import { INDEX_LABELS } from "../../lib/constants";
import { formatPercent } from "../../lib/formatters";
import Link from "next/link";

function getHeatColor(change: number): string {
  if (change <= -5) return "#991b1b";
  if (change <= -3) return "#b91c1c";
  if (change <= -1) return "#dc2626";
  if (change < 0) return "#ef4444";
  if (change === 0) return "#374151";
  if (change < 1) return "#22c55e";
  if (change < 3) return "#16a34a";
  if (change < 5) return "#15803d";
  return "#166534";
}

export default function HeatmapPage() {
  const [filter, setFilter] = useState<string>("all");

  const { data, isLoading } = useQuery({
    queryKey: ["heatmap"],
    queryFn: getHeatmapData,
    refetchInterval: 30000,
  });

  const entries = (data?.entries ?? []).filter(
    (e) => filter === "all" || e.index === filter
  );

  // Sort by market cap for visual sizing
  const sorted = [...entries].sort((a, b) => (b.market_cap || 0) - (a.market_cap || 0));

  // Compute relative sizes
  const totalCap = sorted.reduce((sum, e) => sum + (e.market_cap || 1), 0);

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Market Heatmap</h1>
          <p className="text-text-secondary text-sm mt-1">
            Stock performance by market cap
          </p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        {["all", "sp500", "eurostoxx", "nikkei"].map((idx) => (
          <button
            key={idx}
            onClick={() => setFilter(idx)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors cursor-pointer ${
              filter === idx
                ? "bg-accent-blue text-white"
                : "bg-bg-secondary text-text-secondary hover:bg-bg-tertiary"
            }`}
          >
            {idx === "all" ? "All" : INDEX_LABELS[idx] || idx}
          </button>
        ))}
      </div>

      {/* Heatmap Grid */}
      {isLoading ? (
        <div className="h-[60vh] flex items-center justify-center text-text-secondary">
          Loading heatmap...
        </div>
      ) : (
        <div className="flex flex-wrap gap-1 min-h-[60vh]">
          {sorted.map((entry) => {
            const pct = Math.max((entry.market_cap || 1) / totalCap * 100, 2);
            const size = Math.max(Math.sqrt(pct) * 40, 80);

            return (
              <Link
                key={entry.ticker}
                href={`/stocks/${entry.ticker}`}
                className="flex flex-col items-center justify-center rounded-lg transition-all duration-200 hover:ring-2 hover:ring-white/20 hover:scale-105"
                style={{
                  backgroundColor: getHeatColor(entry.daily_change),
                  width: `${size}px`,
                  height: `${size}px`,
                  minWidth: "80px",
                  minHeight: "80px",
                  flexGrow: pct,
                }}
              >
                <span className="text-white font-bold text-sm">
                  {entry.ticker.replace(".T", "").replace(".DE", "").replace(".PA", "").replace(".MC", "").replace(".AS", "")}
                </span>
                <span
                  className={`text-xs font-medium ${
                    entry.daily_change >= 0 ? "text-green-200" : "text-red-200"
                  }`}
                >
                  {formatPercent(entry.daily_change)}
                </span>
              </Link>
            );
          })}
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center justify-center gap-1 mt-6">
        {[-5, -3, -1, 0, 1, 3, 5].map((v) => (
          <div key={v} className="flex flex-col items-center">
            <div
              className="w-8 h-4 rounded-sm"
              style={{ backgroundColor: getHeatColor(v) }}
            />
            <span className="text-[10px] text-text-secondary mt-1">{v}%</span>
          </div>
        ))}
      </div>
    </AppLayout>
  );
}
