"""
Backtest API router.
"""

import asyncio
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

from apps.api.models.schemas import BacktestRequest
from apps.api.routers.analysis import get_last_result

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


def _run_backtest(tickers, weights, market_data, rf_annual, train_ratio):
    """Run backtest synchronously, computing metrics for both train and test periods."""
    from modules.backtester import split_data, compute_portfolio_performance

    first_idx = market_data["metadata"]["indices"][0]
    bench_series = market_data["benchmarks"][first_idx]

    all_prices = pd.concat(
        [market_data["prices"][idx] for idx in market_data["metadata"]["indices"]],
        axis=1,
    )

    prices_train, prices_test = split_data(all_prices, train_ratio)
    bench_df = bench_series.to_frame()
    bench_train_df, bench_test_df = split_data(bench_df, train_ratio)
    bench_train = bench_train_df.iloc[:, 0]
    bench_test = bench_test_df.iloc[:, 0]

    train = compute_portfolio_performance(prices_train, tickers, weights, bench_train, rf_annual)
    test = compute_portfolio_performance(prices_test, tickers, weights, bench_test, rf_annual)

    return {"train": train, "test": test}


@router.post("")
async def run_backtest_endpoint(req: BacktestRequest):
    """Run backtesting on a portfolio."""
    last = get_last_result()
    if not last or "_market_data" not in last:
        raise HTTPException(
            status_code=400,
            detail="Run the analysis pipeline first before backtesting.",
        )

    market_data = last["_market_data"]
    avg_rf = np.mean(list(market_data["risk_free"].values()))

    try:
        result = await asyncio.to_thread(
            _run_backtest, req.tickers, req.weights,
            market_data, avg_rf, req.train_ratio,
        )
    except Exception as e:
        return {"success": False, "error": str(e)}

    train = result.get("train", {})
    test = result.get("test", {})

    if "error" in train or "error" in test:
        return {"success": False, "error": train.get("error") or test.get("error")}

    def series_to_list(s):
        if isinstance(s, pd.Series):
            return [
                {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 4)}
                for d, v in s.items()
            ]
        return []

    def metrics(r, beat_bench):
        return {
            "total_return": round(float(r.get("rentabilidad_total_port", 0)) * 100, 2),
            "annualized_return": round(float(r.get("rentabilidad_anual_port", 0)) * 100, 2),
            "volatility": round(float(r.get("volatilidad_port", 0)) * 100, 2),
            "sharpe": round(float(r.get("sharpe_realizado", 0)), 3),
            "sortino": round(float(r.get("sortino_realizado", 0)), 3),
            "max_drawdown": round(float(r.get("max_drawdown_port", 0)) * 100, 2),
            "beta": round(float(r.get("beta_realizado", 0)), 3),
            "alpha": round(float(r.get("alpha_realizado", 0)) * 100, 2),
            "beat_benchmark": beat_bench,
        }

    return {
        "success": True,
        "portfolio_series": series_to_list(test.get("serie_port")),
        "benchmark_series": series_to_list(test.get("serie_bench")),
        "drawdown_series": [],
        "train_metrics": metrics(train, train.get("batio_al_benchmark", False)),
        "test_metrics": metrics(test, test.get("batio_al_benchmark", False)),
    }
