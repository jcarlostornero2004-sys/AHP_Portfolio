"use client";

import { useProfileStore } from "../../hooks/useProfile";
import { AppLayout } from "../../components/layout/AppLayout";
import { StatCard } from "../../components/ui/StatCard";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { AllocationPie } from "../../components/charts/AllocationPie";
import { PROFILE_COLORS, PROFILE_LABELS, RANKING_COLORS } from "../../lib/constants";
import { formatPercent } from "../../lib/formatters";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const { analysisResult, profileResult } = useProfileStore();

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

  const {
    profile,
    winner,
    ranking,
    portfolios,
    allocation,
    n_stocks_analyzed,
    n_stocks_selected,
    consistency_ratio,
    is_synthetic,
    top_criteria,
  } = analysisResult;

  const winnerPortfolio = portfolios.find((p) => p.name === winner.name);
  const profileColor = PROFILE_COLORS[profile] || "#3b82f6";

  return (
    <AppLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-text-secondary text-sm mt-1">
            Profile:{" "}
            <span style={{ color: profileColor }}>
              {PROFILE_LABELS[profile] || profile}
            </span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge color={is_synthetic ? "gold" : "green"}>
            {is_synthetic ? "Synthetic Data" : "Live Data"}
          </Badge>
          <Badge color="blue">CR: {consistency_ratio}</Badge>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-8">
        <StatCard
          label="AHP Score"
          value={`${winner.score}%`}
          subtitle={`Winner: ${winner.name}`}
          color="gold"
        />
        <StatCard
          label="Return"
          value={formatPercent(winnerPortfolio?.rentabilidad ?? 0)}
          subtitle="Annualized"
          color={(winnerPortfolio?.rentabilidad ?? 0) >= 0 ? "green" : "red"}
        />
        <StatCard
          label="Sharpe"
          value={winnerPortfolio?.sharpe.toFixed(2) ?? "—"}
          subtitle="Risk-adjusted"
          color="blue"
        />
        <StatCard
          label="Alpha"
          value={formatPercent(winnerPortfolio?.alpha ?? 0)}
          subtitle="Jensen's Alpha"
          color={(winnerPortfolio?.alpha ?? 0) >= 0 ? "green" : "red"}
        />
        <StatCard
          label="Stocks Analyzed"
          value={String(n_stocks_analyzed)}
          subtitle={`${n_stocks_selected} selected`}
        />
        <StatCard
          label="Max Drawdown"
          value={formatPercent(winnerPortfolio?.max_drawdown ?? 0)}
          subtitle="Worst decline"
          color="red"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* AHP Ranking */}
        <Card className="lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4">AHP Ranking</h3>
          <div className="space-y-3">
            {ranking.map((entry, i) => (
              <div key={entry.name} className="flex items-center gap-4">
                <span
                  className="text-lg font-bold w-8 text-center"
                  style={{ color: RANKING_COLORS[i] || "#6b7280" }}
                >
                  #{entry.rank}
                </span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{entry.name}</span>
                    <span className="text-sm text-text-secondary">
                      {entry.score}%
                    </span>
                  </div>
                  <div className="h-3 bg-bg-tertiary rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{
                        width: `${entry.score * 2}%`,
                        backgroundColor: RANKING_COLORS[i] || "#6b7280",
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Allocation */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">
            Winner Allocation ({winner.name})
          </h3>
          {allocation.length > 0 ? (
            <AllocationPie allocation={allocation} />
          ) : (
            <p className="text-text-secondary text-sm">No allocation data</p>
          )}
        </Card>
      </div>

      {/* Criteria & Portfolios */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Criteria */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">Top AHP Criteria</h3>
          <div className="space-y-3">
            {top_criteria.map((c) => (
              <div key={c.name} className="flex items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm">{c.name}</span>
                    <div className="flex items-center gap-2">
                      <Badge color={c.direction === "maximize" ? "green" : "red"}>
                        {c.direction === "maximize" ? "MAX" : "MIN"}
                      </Badge>
                      <span className="text-xs text-text-secondary">{c.weight}/9</span>
                    </div>
                  </div>
                  <div className="h-2 bg-bg-tertiary rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full bg-accent-blue"
                      style={{ width: `${(c.weight / 9) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Portfolios Table */}
        <Card>
          <h3 className="text-lg font-semibold mb-4">Portfolio Candidates</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-text-secondary text-xs uppercase">
                  <th className="text-left pb-3">Name</th>
                  <th className="text-right pb-3">Return</th>
                  <th className="text-right pb-3">Sharpe</th>
                  <th className="text-right pb-3">Vol</th>
                  <th className="text-right pb-3">Beta</th>
                </tr>
              </thead>
              <tbody>
                {portfolios.map((p) => (
                  <tr
                    key={p.name}
                    className={`border-t border-border/50 ${
                      p.name === winner.name ? "bg-accent-gold/5" : ""
                    }`}
                  >
                    <td className="py-2.5 font-medium">
                      {p.name}
                      {p.name === winner.name && (
                        <span className="ml-2 text-accent-gold text-xs">Winner</span>
                      )}
                    </td>
                    <td
                      className={`text-right ${
                        p.rentabilidad >= 0 ? "text-accent-green" : "text-accent-red"
                      }`}
                    >
                      {formatPercent(p.rentabilidad)}
                    </td>
                    <td className="text-right">{p.sharpe.toFixed(2)}</td>
                    <td className="text-right text-text-secondary">
                      {p.volatilidad.toFixed(1)}%
                    </td>
                    <td className="text-right text-text-secondary">
                      {p.beta.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}
