"use client";

import { useState } from "react";
import { useProfileStore } from "../../hooks/useProfile";
import { AppLayout } from "../../components/layout/AppLayout";
import { Card } from "../../components/ui/Card";
import { StatCard } from "../../components/ui/StatCard";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { EquityCurve } from "../../components/charts/EquityCurve";
import { formatPercent } from "../../lib/formatters";
import { runBacktest } from "../../lib/api";
import type { BacktestResponse } from "../../types";
import { useRouter } from "next/navigation";

export default function BacktestPage() {
  const router = useRouter();
  const { analysisResult } = useProfileStore();
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const { profile, winner, allocation } = analysisResult;

  const handleRunBacktest = async () => {
    setLoading(true);
    setError(null);

    const tickers = allocation.map((a) => a.ticker);
    const weights: Record<string, number> = {};
    allocation.forEach((a) => {
      weights[a.ticker] = parseFloat(a.weight.replace("%", "")) / 100;
    });

    try {
      const res = await runBacktest(tickers, weights, profile);
      if (res.success) {
        setResult(res);
      } else {
        setError(res.error || "Backtest failed");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backtest failed");
    } finally {
      setLoading(false);
    }
  };

  const test = result?.test_metrics;
  const train = result?.train_metrics;

  return (
    <AppLayout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Backtesting</h1>
          <p className="text-text-secondary text-sm mt-1">
            Historical performance validation — {winner.name}
          </p>
        </div>
        <Button onClick={handleRunBacktest} disabled={loading}>
          {loading ? "Running backtest..." : "Run Backtest"}
        </Button>
      </div>

      {/* Portfolio being tested */}
      <Card className="mb-8">
        <h3 className="text-sm text-text-secondary uppercase mb-2">Testing Portfolio</h3>
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-lg font-bold">{winner.name}</span>
          {allocation.map((a) => (
            <Badge key={a.ticker} color="blue">
              {a.ticker}: {a.weight}
            </Badge>
          ))}
        </div>
      </Card>

      {error && (
        <Card className="mb-8 border-accent-red/30 bg-accent-red/5">
          <p className="text-accent-red text-sm">{error}</p>
        </Card>
      )}

      {result && (
        <>
          {/* Stat Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard
              label="Test Return"
              value={formatPercent(test?.total_return ?? 0)}
              subtitle="Out-of-sample"
              color={(test?.total_return ?? 0) >= 0 ? "green" : "red"}
            />
            <StatCard
              label="Test Sharpe"
              value={(test?.sharpe ?? 0).toFixed(3)}
              color="blue"
            />
            <StatCard
              label="Test Max DD"
              value={formatPercent(test?.max_drawdown ?? 0)}
              color="red"
            />
            <StatCard
              label="Beat Benchmark"
              value={test?.beat_benchmark ? "YES" : "NO"}
              color={test?.beat_benchmark ? "green" : "red"}
            />
          </div>

          {/* Equity Curve */}
          <Card className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <EquityCurve
              data={result.portfolio_series}
              benchmarkData={result.benchmark_series}
              height={350}
            />
            <div className="flex items-center gap-6 mt-3">
              <div className="flex items-center gap-2">
                <div className="w-4 h-0.5 bg-accent-green" />
                <span className="text-xs text-text-secondary">Portfolio</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-0.5 bg-text-secondary border-t border-dashed" />
                <span className="text-xs text-text-secondary">Benchmark</span>
              </div>
            </div>
          </Card>

          {/* Train vs Test Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <h3 className="text-lg font-semibold mb-4">
                Training Period <Badge color="blue">70%</Badge>
              </h3>
              <div className="space-y-3">
                {train && (
                  <>
                    <MetricRow label="Total Return" value={formatPercent(train.total_return)} positive={train.total_return >= 0} />
                    <MetricRow label="Annualized Return" value={formatPercent(train.annualized_return)} positive={train.annualized_return >= 0} />
                    <MetricRow label="Volatility" value={formatPercent(train.volatility)} />
                    <MetricRow label="Sharpe Ratio" value={train.sharpe.toFixed(3)} />
                    <MetricRow label="Sortino Ratio" value={train.sortino.toFixed(3)} />
                    <MetricRow label="Max Drawdown" value={formatPercent(train.max_drawdown)} positive={false} />
                    <MetricRow label="Beta" value={train.beta.toFixed(3)} />
                    <MetricRow label="Alpha" value={formatPercent(train.alpha)} positive={train.alpha >= 0} />
                  </>
                )}
              </div>
            </Card>

            <Card>
              <h3 className="text-lg font-semibold mb-4">
                Testing Period <Badge color="gold">30%</Badge>
              </h3>
              <div className="space-y-3">
                {test && (
                  <>
                    <MetricRow label="Total Return" value={formatPercent(test.total_return)} positive={test.total_return >= 0} />
                    <MetricRow label="Annualized Return" value={formatPercent(test.annualized_return)} positive={test.annualized_return >= 0} />
                    <MetricRow label="Volatility" value={formatPercent(test.volatility)} />
                    <MetricRow label="Sharpe Ratio" value={test.sharpe.toFixed(3)} />
                    <MetricRow label="Sortino Ratio" value={test.sortino.toFixed(3)} />
                    <MetricRow label="Max Drawdown" value={formatPercent(test.max_drawdown)} positive={false} />
                    <MetricRow label="Beta" value={test.beta.toFixed(3)} />
                    <MetricRow label="Alpha" value={formatPercent(test.alpha)} positive={test.alpha >= 0} />
                  </>
                )}
              </div>
            </Card>
          </div>
        </>
      )}
    </AppLayout>
  );
}

function MetricRow({
  label,
  value,
  positive,
}: {
  label: string;
  value: string;
  positive?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-text-secondary">{label}</span>
      <span
        className={`text-sm font-mono font-medium ${
          positive === undefined
            ? "text-text-primary"
            : positive
            ? "text-accent-green"
            : "text-accent-red"
        }`}
      >
        {value}
      </span>
    </div>
  );
}
