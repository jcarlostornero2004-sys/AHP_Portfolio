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
    """Run backtest synchronously."""
    from modules.backtester import run_backtest

    first_idx = market_data["metadata"]["indices"][0]
    bench_series = market_data["benchmarks"][first_idx]

    all_prices = pd.concat(
        [market_data["prices"][idx] for idx in market_data["metadata"]["indices"]],
        axis=1,
    )

    return run_backtest(
        prices=all_prices,
        benchmark_prices=bench_series,
        tickers=tickers,
        weights=weights,
        rf_annual=rf_annual,
        train_ratio=train_ratio,
        progress=False,
    )


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

    if "error" in result:
        return {"success": False, "error": result["error"]}

    # Serialize time series
    def series_to_list(s):
        if isinstance(s, pd.Series):
            return [
                {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 4)}
                for d, v in s.items()
            ]
        return []

    return {
        "success": True,
        "portfolio_series": series_to_list(result.get("serie_port")),
        "benchmark_series": series_to_list(result.get("serie_bench")),
        "drawdown_series": series_to_list(result.get("drawdown_series", pd.Series())),
        "train_metrics": {
            "total_return": round(float(result.get("rent_train", 0)) * 100, 2),
            "annualized_return": round(float(result.get("rent_anual_train", 0)) * 100, 2),
            "volatility": round(float(result.get("vol_train", 0)) * 100, 2),
            "sharpe": round(float(result.get("sharpe_train", 0)), 3),
            "sortino": round(float(result.get("sortino_train", 0)), 3),
            "max_drawdown": round(float(result.get("max_dd_train", 0)) * 100, 2),
            "beta": round(float(result.get("beta_train", 0)), 3),
            "alpha": round(float(result.get("alpha_train", 0)) * 100, 2),
            "beat_benchmark": False,
        },
        "test_metrics": {
            "total_return": round(float(result.get("rent_test", 0)) * 100, 2),
            "annualized_return": round(float(result.get("rent_anual_test", 0)) * 100, 2),
            "volatility": round(float(result.get("vol_test", 0)) * 100, 2),
            "sharpe": round(float(result.get("sharpe_test", 0)), 3),
            "sortino": round(float(result.get("sortino_test", 0)), 3),
            "max_drawdown": round(float(result.get("max_dd_test", 0)) * 100, 2),
            "beta": round(float(result.get("beta_test", 0)), 3),
            "alpha": round(float(result.get("alpha_test", 0)) * 100, 2),
            "beat_benchmark": result.get("batio_al_benchmark", False),
        },
    }
