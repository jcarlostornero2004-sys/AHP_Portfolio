"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { PortfolioDetail } from "../../types";

const LINE_COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"];

interface PortfolioCompareChartProps {
  portfolios: PortfolioDetail[];
}

function generateSyntheticSeries(
  portfolios: PortfolioDetail[],
  points = 24
): Record<string, string | number>[] {
  return Array.from({ length: points }, (_, i) => {
    const entry: Record<string, string | number> = { month: `M${i + 1}` };
    portfolios.forEach((p) => {
      const monthlyReturn = p.rentabilidad / 12;
      const monthlyVol = (p.volatilidad / 100) / Math.sqrt(12);
      // Deterministic pseudo-random using sine for reproducibility
      const noise = Math.sin(i * 7.3 + p.rentabilidad * 100) * monthlyVol;
      entry[p.name] = parseFloat(
        ((1 + monthlyReturn + noise) ** (i + 1)).toFixed(4)
      );
    });
    return entry;
  });
}

export function PortfolioCompareChart({ portfolios }: PortfolioCompareChartProps) {
  if (portfolios.length === 0) return null;

  const data = generateSyntheticSeries(portfolios);

  return (
    <div className="w-full">
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
            <XAxis
              dataKey="month"
              stroke="#8b949e"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="#8b949e"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v: number) => `${((v - 1) * 100).toFixed(0)}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#161b22",
                border: "1px solid #30363d",
                borderRadius: "8px",
                color: "#f0f6fc",
                fontSize: "12px",
              }}
              formatter={(value, name) => [
                typeof value === "number" ? `${((value - 1) * 100).toFixed(1)}%` : value,
                name,
              ]}
            />
            <Legend wrapperStyle={{ fontSize: "11px", color: "#8b949e" }} />
            {portfolios.map((p, i) => (
              <Line
                key={p.name}
                type="monotone"
                dataKey={p.name}
                stroke={LINE_COLORS[i % LINE_COLORS.length]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-text-secondary text-center mt-1 opacity-60">
        * Proyección estimada (24 meses) basada en métricas históricas
      </p>
    </div>
  );
}
