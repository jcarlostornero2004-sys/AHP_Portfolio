"use client";

import { useProfileStore } from "../../hooks/useProfile";
import { AppLayout } from "../../components/layout/AppLayout";
import { Card } from "../../components/ui/Card";
import { StatCard } from "../../components/ui/StatCard";
import { Badge } from "../../components/ui/Badge";
import { AllocationPie } from "../../components/charts/AllocationPie";
import { PROFILE_COLORS, PROFILE_LABELS, RANKING_COLORS } from "../../lib/constants";
import { formatPercent, formatNumber } from "../../lib/formatters";
import { useRouter } from "next/navigation";

export default function PortfolioPage() {
  const router = useRouter();
  const { analysisResult } = useProfileStore();

  if (!analysisResult) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
          <p className="text-text-secondary text-lg">No analysis results yet.</p>
          <button
            onClick={() => router.push("/")}
            className="text-accent-blue hover:underline cursor-pointer"
          >
            Take the questionnaire first
          </button>
        </div>
      </AppLayout>
    );
  }

  const { profile, winner, ranking, portfolios, allocation, top_criteria, consistency_ratio } =
    analysisResult;

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">AHP Portfolio Analysis</h1>
          <p className="text-text-secondary text-sm mt-1">
            15 criteria, 5 categories, Saaty methodology
          </p>
        </div>
        <Badge color="blue">Consistency Ratio: {consistency_ratio}</Badge>
      </div>

      {/* Winner highlight */}
      <Card className="mb-8 border-accent-gold/30 bg-accent-gold/5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-accent-gold uppercase tracking-wider font-medium">
              Recommended Portfolio
            </p>
            <h2 className="text-3xl font-bold text-text-primary mt-1">
              {winner.name}
            </h2>
            <p className="text-text-secondary text-sm mt-1">
              AHP Score: {winner.score}% — Rank #{winner.rank}
            </p>
          </div>
          <div className="text-right">
            {allocation.map((a) => (
              <span
                key={a.ticker}
                className="inline-block bg-bg-tertiary text-text-primary text-xs px-2 py-1 rounded ml-1 mb-1"
              >
                {a.ticker}: {a.weight}
              </span>
            ))}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Ranking bars */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">AHP Global Ranking</h3>
          <div className="space-y-4">
            {ranking.map((entry, i) => {
              const port = portfolios.find((p) => p.name === entry.name);
              return (
                <div key={entry.name}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span
                        className="text-lg font-bold"
                        style={{ color: RANKING_COLORS[i] || "#6b7280" }}
                      >
                        #{entry.rank}
                      </span>
                      <span className="font-medium">{entry.name}</span>
                      {entry.name === winner.name && (
                        <Badge color="gold">Winner</Badge>
                      )}
                    </div>
                    <span className="text-sm text-text-secondary font-mono">
                      {entry.score}%
                    </span>
                  </div>
                  <div className="h-4 bg-bg-tertiary rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${entry.score * 2}%`,
                        backgroundColor: RANKING_COLORS[i] || "#6b7280",
                      }}
                    />
                  </div>
                  {port && (
                    <div className="flex gap-4 mt-1 text-xs text-text-secondary">
                      <span>Return: {formatPercent(port.rentabilidad)}</span>
                      <span>Sharpe: {port.sharpe.toFixed(2)}</span>
                      <span>Vol: {port.volatilidad.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </Card>

        {/* Allocation chart */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">Winner Composition</h3>
          <AllocationPie allocation={allocation} />
        </Card>
      </div>

      {/* Full portfolio comparison table */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Portfolio Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-text-secondary text-xs uppercase border-b border-border">
                <th className="text-left px-3 py-3">Portfolio</th>
                <th className="text-right px-3 py-3">AHP Score</th>
                <th className="text-right px-3 py-3">Return</th>
                <th className="text-right px-3 py-3">Volatility</th>
                <th className="text-right px-3 py-3">Sharpe</th>
                <th className="text-right px-3 py-3">Max DD</th>
                <th className="text-right px-3 py-3">Beta</th>
                <th className="text-right px-3 py-3">Alpha</th>
                <th className="text-left px-3 py-3">Composition</th>
              </tr>
            </thead>
            <tbody>
              {portfolios.map((p) => {
                const rank = ranking.find((r) => r.name === p.name);
                const isWinner = p.name === winner.name;
                return (
                  <tr
                    key={p.name}
                    className={`border-t border-border/30 ${
                      isWinner ? "bg-accent-gold/5" : ""
                    }`}
                  >
                    <td className="px-3 py-3 font-medium">
                      {p.name}
                      {isWinner && (
                        <span className="ml-2 text-accent-gold text-xs">★</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right font-mono">
                      {rank?.score ?? "—"}%
                    </td>
                    <td
                      className={`px-3 py-3 text-right ${
                        p.rentabilidad >= 0 ? "text-accent-green" : "text-accent-red"
                      }`}
                    >
                      {formatPercent(p.rentabilidad)}
                    </td>
                    <td className="px-3 py-3 text-right text-text-secondary">
                      {p.volatilidad.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 text-right">{p.sharpe.toFixed(2)}</td>
                    <td className="px-3 py-3 text-right text-accent-red">
                      {formatPercent(p.max_drawdown)}
                    </td>
                    <td className="px-3 py-3 text-right text-text-secondary">
                      {p.beta.toFixed(2)}
                    </td>
                    <td
                      className={`px-3 py-3 text-right ${
                        p.alpha >= 0 ? "text-accent-green" : "text-accent-red"
                      }`}
                    >
                      {formatPercent(p.alpha)}
                    </td>
                    <td className="px-3 py-3 text-text-secondary text-xs">
                      {p.tickers}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </AppLayout>
  );
}
