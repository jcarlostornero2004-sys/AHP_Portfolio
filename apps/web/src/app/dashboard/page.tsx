"use client";

import { motion } from "framer-motion";
import { useProfileStore } from "../../hooks/useProfile";
import { AppLayout } from "../../components/layout/AppLayout";
import { StatCard } from "../../components/ui/StatCard";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { AllocationPie } from "../../components/charts/AllocationPie";
import { ExplanationCard } from "../../components/ui/ExplanationCard";
import { PortfolioCompareChart } from "../../components/charts/PortfolioCompareChart";
import { PROFILE_COLORS, PROFILE_LABELS, RANKING_COLORS } from "../../lib/constants";
import { formatPercent } from "../../lib/formatters";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const { analysisResult } = useProfileStore();

  if (!analysisResult) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
          <p className="text-text-secondary text-lg">Todavía no hay resultados de análisis.</p>
          <button
            onClick={() => router.push("/questionnaire")}
            className="text-accent-blue hover:underline cursor-pointer"
          >
            Completa primero el cuestionario
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
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Panel de Control</h1>
            <p className="text-text-secondary text-sm mt-1">
              Perfil:{" "}
              <span style={{ color: profileColor }}>
                {PROFILE_LABELS[profile] || profile}
              </span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge color={is_synthetic ? "gold" : "green"}>
              {is_synthetic ? "Datos Simulados" : "Datos Reales"}
            </Badge>
            <Badge color="blue">CR: {consistency_ratio}</Badge>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-8">
          <StatCard
            label="Puntuación AHP"
            value={`${winner.score.toFixed(1)}%`}
            subtitle={`Ganadora: ${winner.name}`}
            color="gold"
            icon="🏆"
          />
          <StatCard
            label="Rentabilidad"
            value={formatPercent(winnerPortfolio?.rentabilidad ?? 0)}
            subtitle="Anualizada"
            color={(winnerPortfolio?.rentabilidad ?? 0) >= 0 ? "green" : "red"}
            icon="📈"
          />
          <StatCard
            label="Sharpe"
            value={winnerPortfolio?.sharpe.toFixed(2) ?? "—"}
            subtitle="Ajustada al riesgo"
            color="blue"
            icon="🛡️"
          />
          <StatCard
            label="Alpha"
            value={formatPercent(winnerPortfolio?.alpha ?? 0)}
            subtitle="Jensen's Alpha"
            color={(winnerPortfolio?.alpha ?? 0) >= 0 ? "green" : "red"}
            icon="⚡"
          />
          <StatCard
            label="Acciones Analizadas"
            value={String(n_stocks_analyzed)}
            subtitle={`${n_stocks_selected} seleccionadas`}
            icon="🔍"
          />
          <StatCard
            label="Max Drawdown"
            value={formatPercent(winnerPortfolio?.max_drawdown ?? 0)}
            subtitle="Caída máxima"
            color="red"
            icon="📉"
          />
        </div>

        {/* Explanation Card */}
        <div className="mb-8">
          <ExplanationCard
            profile={profile}
            winner={winner}
            topCriteria={top_criteria}
            consistencyRatio={consistency_ratio}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* AHP Ranking */}
          <Card className="lg:col-span-2">
            <h3 className="text-lg font-semibold mb-4">Ranking AHP</h3>
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
                        {entry.score.toFixed(1)}%
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
              Asignación Ganadora ({winner.name})
            </h3>
            {allocation.length > 0 ? (
              <AllocationPie allocation={allocation} />
            ) : (
              <p className="text-text-secondary text-sm">Sin datos de asignación</p>
            )}
          </Card>
        </div>

        {/* Criteria & Portfolios */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Top Criteria */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Criterios AHP Principales</h3>
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
            <h3 className="text-lg font-semibold mb-4">Carteras Candidatas</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-text-secondary text-xs uppercase">
                    <th className="text-left pb-3">Nombre</th>
                    <th className="text-right pb-3">Rentab.</th>
                    <th className="text-right pb-3">Sharpe</th>
                    <th className="text-right pb-3">Volat.</th>
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
                          <span className="ml-2 text-accent-gold text-xs">Ganadora</span>
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

        {/* Portfolio Compare Chart */}
        <Card className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Proyección Comparativa de Carteras</h3>
            <span className="text-xs text-text-secondary bg-bg-tertiary px-2 py-1 rounded-full">
              Estimación 24M
            </span>
          </div>
          <PortfolioCompareChart portfolios={portfolios} />
        </Card>
      </motion.div>
    </AppLayout>
  );
}
