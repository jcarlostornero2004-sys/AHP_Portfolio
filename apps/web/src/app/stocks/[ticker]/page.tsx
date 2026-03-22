"use client";

import { use } from "react";
import { useQuery } from "@tanstack/react-query";
import { getStockDetail, getStockHistory } from "../../../lib/api";
import { AppLayout } from "../../../components/layout/AppLayout";
import { Card } from "../../../components/ui/Card";
import { StatCard } from "../../../components/ui/StatCard";
import { Badge } from "../../../components/ui/Badge";
import { EquityCurve } from "../../../components/charts/EquityCurve";
import { formatPercent, formatPrice } from "../../../lib/formatters";
import { INDEX_LABELS } from "../../../lib/constants";

export default function StockDetailPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = use(params);

  const { data: detail, isLoading: loadingDetail } = useQuery({
    queryKey: ["stock-detail", ticker],
    queryFn: () => getStockDetail(ticker),
  });

  const { data: history, isLoading: loadingHistory } = useQuery({
    queryKey: ["stock-history", ticker],
    queryFn: () => getStockHistory(ticker, "6mo"),
  });

  const isLoading = loadingDetail || loadingHistory;

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="w-8 h-8 border-3 border-accent-blue border-t-transparent rounded-full animate-spin" />
        </div>
      </AppLayout>
    );
  }

  const priceData =
    history?.data.map((d) => ({
      date: d.date,
      value: d.close,
    })) ?? [];

  const change = detail?.change_1d ?? 0;

  return (
    <AppLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{ticker.toUpperCase()}</h1>
            {detail?.index && (
              <Badge color="blue">
                {INDEX_LABELS[detail.index] || detail.index}
              </Badge>
            )}
            {detail?.sector && <Badge color="gray">{detail.sector}</Badge>}
          </div>
          <p className="text-text-secondary text-sm mt-1">{detail?.name || ticker}</p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold font-mono">
            ${formatPrice(detail?.price ?? 0)}
          </p>
          <p
            className={`text-lg font-medium ${
              change >= 0 ? "text-accent-green" : "text-accent-red"
            }`}
          >
            {formatPercent(change)} today
          </p>
        </div>
      </div>

      {/* Price Chart */}
      <Card className="mb-8">
        <h3 className="text-lg font-semibold mb-4">Price History (6 months)</h3>
        {priceData.length > 0 ? (
          <EquityCurve data={priceData} height={400} />
        ) : (
          <p className="text-text-secondary text-sm">No historical data available</p>
        )}
      </Card>

      {/* OHLCV Table */}
      {history && history.data.length > 0 && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Recent Price Data</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-text-secondary text-xs uppercase border-b border-border">
                  <th className="text-left px-3 py-2">Date</th>
                  <th className="text-right px-3 py-2">Open</th>
                  <th className="text-right px-3 py-2">High</th>
                  <th className="text-right px-3 py-2">Low</th>
                  <th className="text-right px-3 py-2">Close</th>
                  <th className="text-right px-3 py-2">Volume</th>
                </tr>
              </thead>
              <tbody>
                {history.data
                  .slice(-10)
                  .reverse()
                  .map((d) => (
                    <tr
                      key={d.date}
                      className="border-t border-border/30"
                    >
                      <td className="px-3 py-2 text-text-secondary">{d.date}</td>
                      <td className="px-3 py-2 text-right font-mono">{formatPrice(d.open)}</td>
                      <td className="px-3 py-2 text-right font-mono text-accent-green">
                        {formatPrice(d.high)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono text-accent-red">
                        {formatPrice(d.low)}
                      </td>
                      <td className="px-3 py-2 text-right font-mono font-medium">
                        {formatPrice(d.close)}
                      </td>
                      <td className="px-3 py-2 text-right text-text-secondary">
                        {(d.volume / 1e6).toFixed(1)}M
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </AppLayout>
  );
}
