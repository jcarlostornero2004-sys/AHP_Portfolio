"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getMarketOverview, getSentiment } from "../../lib/api";
import { AppLayout } from "../../components/layout/AppLayout";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { StatCardSkeleton } from "../../components/ui/Skeleton";
import { SparklineChart } from "../../components/charts/SparklineChart";
import { FearGreedGauge } from "../../components/market/FearGreedGauge";
import { formatPercent, formatPrice, formatMarketCap } from "../../lib/formatters";
import { INDEX_LABELS } from "../../lib/constants";
import Link from "next/link";

export default function MarketPage() {
  const [filter, setFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("change_1d");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const { data: marketData, isLoading } = useQuery({
    queryKey: ["market-overview"],
    queryFn: getMarketOverview,
    refetchInterval: 30000,
  });

  const { data: sentiment } = useQuery({
    queryKey: ["sentiment"],
    queryFn: getSentiment,
    refetchInterval: 60000,
  });

  const stocks = marketData?.stocks ?? [];

  const filteredStocks = stocks
    .filter((s) => filter === "all" || s.index === filter)
    .sort((a, b) => {
      const aVal = (a[sortBy as keyof typeof a] as number) ?? 0;
      const bVal = (b[sortBy as keyof typeof b] as number) ?? 0;
      return sortDir === "desc" ? bVal - aVal : aVal - bVal;
    });

  const handleSort = (col: string) => {
    if (sortBy === col) {
      setSortDir(sortDir === "desc" ? "asc" : "desc");
    } else {
      setSortBy(col);
      setSortDir("desc");
    }
  };

  return (
    <AppLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Visión del Mercado</h1>
          <p className="text-text-secondary text-sm mt-1">
            {stocks.length} acciones monitorizadas
            {marketData?.is_live && (
              <span className="ml-2 inline-flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-accent-green pulse-live" />
                <span className="text-accent-green text-xs">Live</span>
              </span>
            )}
          </p>
        </div>
      </div>

      {/* Sentiment + Filters row */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        {/* Fear & Greed */}
        <Card className="flex items-center justify-center">
          {sentiment ? (
            <FearGreedGauge
              value={sentiment.fear_greed_index}
              label={sentiment.label}
            />
          ) : (
            <StatCardSkeleton />
          )}
        </Card>

        {/* Quick stats */}
        <Card>
          <span className="text-xs text-text-secondary uppercase">Acciones Positivas</span>
          <p className="text-2xl font-bold text-accent-green mt-1">
            {stocks.filter((s) => s.change_1d > 0).length}
          </p>
          <span className="text-xs text-text-secondary">
            de {stocks.length} total
          </span>
        </Card>
        <Card>
          <span className="text-xs text-text-secondary uppercase">Acciones Negativas</span>
          <p className="text-2xl font-bold text-accent-red mt-1">
            {stocks.filter((s) => s.change_1d < 0).length}
          </p>
          <span className="text-xs text-text-secondary">
            de {stocks.length} total
          </span>
        </Card>
        <Card>
          <span className="text-xs text-text-secondary uppercase">Cambio Medio</span>
          <p className={`text-2xl font-bold mt-1 ${
            (sentiment?.components?.avg_daily_change ?? 0) >= 0
              ? "text-accent-green"
              : "text-accent-red"
          }`}>
            {formatPercent(sentiment?.components?.avg_daily_change ?? 0)}
          </p>
          <span className="text-xs text-text-secondary">Hoy</span>
        </Card>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-4">
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
            {idx === "all" ? "Todas" : INDEX_LABELS[idx] || idx}
          </button>
        ))}
      </div>

      {/* Stock Table */}
      <Card className="overflow-hidden p-0">
        {isLoading ? (
          <div className="p-8 text-center text-text-secondary">Cargando datos de mercado...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-text-secondary text-xs uppercase border-b border-border">
                  <th className="text-left px-4 py-3">#</th>
                  <th className="text-left px-4 py-3">Ticker</th>
                  <th
                    className="text-right px-4 py-3 cursor-pointer hover:text-text-primary"
                    onClick={() => handleSort("price")}
                  >
                    Precio {sortBy === "price" && (sortDir === "desc" ? "↓" : "↑")}
                  </th>
                  <th
                    className="text-right px-4 py-3 cursor-pointer hover:text-text-primary"
                    onClick={() => handleSort("change_1d")}
                  >
                    24h % {sortBy === "change_1d" && (sortDir === "desc" ? "↓" : "↑")}
                  </th>
                  <th
                    className="text-right px-4 py-3 cursor-pointer hover:text-text-primary"
                    onClick={() => handleSort("change_7d")}
                  >
                    7d % {sortBy === "change_7d" && (sortDir === "desc" ? "↓" : "↑")}
                  </th>
                  <th className="text-center px-4 py-3">Gráfico 7d</th>
                  <th className="text-right px-4 py-3">Cap. Bursátil</th>
                  <th className="text-right px-4 py-3">Índice</th>
                </tr>
              </thead>
              <tbody>
                {filteredStocks.map((stock, i) => (
                  <tr
                    key={stock.ticker}
                    className="border-t border-border/30 hover:bg-bg-tertiary/50 transition-colors"
                  >
                    <td className="px-4 py-3 text-text-secondary">{i + 1}</td>
                    <td className="px-4 py-3">
                      <Link
                        href={`/stocks/${stock.ticker}`}
                        className="font-medium text-text-primary hover:text-accent-blue transition-colors"
                      >
                        {stock.ticker}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-right font-mono">
                      ${formatPrice(stock.price)}
                    </td>
                    <td
                      className={`px-4 py-3 text-right font-medium ${
                        stock.change_1d >= 0 ? "text-accent-green" : "text-accent-red"
                      }`}
                    >
                      {formatPercent(stock.change_1d)}
                    </td>
                    <td
                      className={`px-4 py-3 text-right ${
                        stock.change_7d >= 0 ? "text-accent-green" : "text-accent-red"
                      }`}
                    >
                      {formatPercent(stock.change_7d)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <div className="flex justify-center">
                        <SparklineChart data={stock.sparkline} width={80} height={24} />
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right text-text-secondary">
                      {formatMarketCap(stock.market_cap)}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <Badge color="gray">
                        {INDEX_LABELS[stock.index] || stock.index}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppLayout>
  );
}
