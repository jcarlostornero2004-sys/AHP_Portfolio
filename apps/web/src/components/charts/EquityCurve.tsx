"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface DataPoint {
  date: string;
  value: number;
}

interface EquityCurveProps {
  data: DataPoint[];
  benchmarkData?: DataPoint[];
  height?: number;
}

export function EquityCurve({ data, benchmarkData, height = 300 }: EquityCurveProps) {
  // Merge portfolio and benchmark data
  const merged = data.map((d, i) => ({
    date: d.date,
    portfolio: d.value,
    benchmark: benchmarkData?.[i]?.value,
  }));

  return (
    <div style={{ width: "100%", height }}>
      <ResponsiveContainer>
        <AreaChart data={merged} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="gradPortfolio" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
          <XAxis
            dataKey="date"
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
            tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
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
              `${(Number(value) * 100).toFixed(2)}%`,
              name === "portfolio" ? "Portfolio" : "Benchmark",
            ]}
          />
          {benchmarkData && (
            <Area
              type="monotone"
              dataKey="benchmark"
              stroke="#8b949e"
              fill="none"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
          )}
          <Area
            type="monotone"
            dataKey="portfolio"
            stroke="#22c55e"
            fill="url(#gradPortfolio)"
            strokeWidth={2}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
