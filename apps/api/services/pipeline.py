"""
Pipeline service — orchestrates existing AHP modules.
Extracted from webapp/app.py and main.py.
"""

import math
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional

from modules.questionnaire import QUESTIONS, PROFILES_ORDER, PROFILE_DESCRIPTIONS, score_answers
from modules.profiles import get_profile_config, CRITERIA, CRITERIA_ORDER, PROFILE_WEIGHTS
from modules.stock_analysis import compute_returns, analyze_stocks
from modules.stock_filter import run_filtering
from modules.portfolio_builder import build_portfolios
from modules.ahp_engine_v2 import AHPEngine


def _safe_float(v, default: float = 0.0) -> float:
    """Convert value to a JSON-safe Python float, replacing NaN/Inf with default."""
    try:
        f = float(v)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except (TypeError, ValueError):
        return default


def generate_synthetic_data() -> dict:
    """Generate synthetic market data for demo/fallback."""
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    n_days = 504
    dates = pd.bdate_range(start="2023-01-02", periods=n_days)

    configs = {
        "sp500": {
            "AAPL": (0.12, 0.25), "MSFT": (0.18, 0.28), "NVDA": (0.25, 0.40),
            "GOOGL": (0.15, 0.27), "AMZN": (0.16, 0.30), "META": (0.20, 0.35),
            "JNJ": (0.05, 0.14), "PG": (0.04, 0.12), "JPM": (0.10, 0.22),
            "XOM": (0.08, 0.24), "KO": (0.03, 0.11), "V": (0.11, 0.20),
            "UNH": (0.09, 0.18), "HD": (0.10, 0.22), "MRK": (0.06, 0.17),
            "COST": (0.13, 0.21), "AVGO": (0.22, 0.35), "LLY": (0.19, 0.30),
        },
        "eurostoxx": {
            "SAP.DE": (0.14, 0.26), "SIE.DE": (0.08, 0.20), "SAN.MC": (0.06, 0.24),
            "MC.PA": (0.11, 0.22), "TTE.PA": (0.07, 0.26), "ASML.AS": (0.20, 0.32),
            "AIR.PA": (0.10, 0.24), "ALV.DE": (0.07, 0.18), "BNP.PA": (0.06, 0.22),
            "OR.PA": (0.09, 0.19), "DTE.DE": (0.08, 0.16), "BBVA.MC": (0.11, 0.25),
        },
        "nikkei": {
            "7203.T": (0.09, 0.22), "6758.T": (0.15, 0.30), "9984.T": (0.20, 0.35),
            "4502.T": (0.04, 0.16), "8306.T": (0.07, 0.20), "8035.T": (0.18, 0.32),
            "6861.T": (0.12, 0.25), "6902.T": (0.08, 0.19), "9433.T": (0.05, 0.14),
            "7974.T": (0.14, 0.28),
        },
    }

    all_prices, all_benchmarks = {}, {}
    for idx, stocks in configs.items():
        d = {}
        for t, (mu, sig) in stocks.items():
            r = np.random.normal(mu / 252, sig / np.sqrt(252), n_days)
            d[t] = 100 * np.exp(np.cumsum(r))
        all_prices[idx] = pd.DataFrame(d, index=dates)
        bmu = np.mean([s[0] for s in stocks.values()])
        bsig = np.mean([s[1] for s in stocks.values()]) * 0.7
        br = np.random.normal(bmu / 252, bsig / np.sqrt(252), n_days)
        all_benchmarks[idx] = pd.Series(1000 * np.exp(np.cumsum(br)), index=dates)

    return {
        "prices": all_prices,
        "benchmarks": all_benchmarks,
        "risk_free": {"sp500": 0.04, "eurostoxx": 0.025, "nikkei": 0.01},
        "stock_info": None,
        "metadata": {"indices": list(configs.keys()), "synthetic": True},
    }


def _fetch_live_data_impl() -> dict:
    """Internal: download market data (runs in a thread with timeout)."""
    from modules.data_loader import load_market_data
    return load_market_data(period_years=2, max_per_index=25, progress=False)


def load_live_data() -> dict:
    """Try loading real data from Yahoo Finance with a 45-second timeout, fall back to synthetic."""
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_live_data_impl)
            data = future.result(timeout=45)
        data["metadata"]["synthetic"] = False
        return data
    except FuturesTimeoutError:
        print("  Live data timed out after 45s, using synthetic data")
        return generate_synthetic_data()
    except Exception as e:
        print(f"  Real data unavailable ({e}), using synthetic data")
        return generate_synthetic_data()


def run_analysis_pipeline(profile: str, use_live: bool = True) -> dict:
    """
    Run the full AHP pipeline (M2-M6) for a given profile.

    Returns a dict matching the AnalysisResponse schema.
    """
    config = get_profile_config(profile)

    # M2: Load data
    market_data = load_live_data() if use_live else generate_synthetic_data()
    is_synthetic = market_data["metadata"].get("synthetic", True)

    # M3: Stock analysis
    all_analyses = []
    all_returns = {}
    for idx in market_data["metadata"]["indices"]:
        prices = market_data["prices"][idx]
        benchmark = market_data["benchmarks"][idx]
        rf = market_data["risk_free"][idx]
        analysis = analyze_stocks(prices, benchmark, rf, idx, progress=False)
        analysis["region"] = idx
        all_analyses.append(analysis)
        all_returns[idx] = compute_returns(prices)

    consolidated = pd.concat(all_analyses)

    # M4: Filtering
    avg_rf = np.mean(list(market_data["risk_free"].values()))
    market_vars = []
    for idx in market_data["metadata"]["indices"]:
        b = market_data["benchmarks"][idx]
        br = np.log(b / b.shift(1)).dropna()
        market_vars.append(br.var() * 252)

    selected = run_filtering(
        consolidated, config["filters"], avg_rf,
        np.mean(market_vars), stock_info=None,
        profile_name=profile, progress=False,
    )

    if selected.empty:
        return {
            "success": False,
            "error": "No stocks passed the risk filters for this profile. Try adjusting your answers.",
        }

    # M5: Portfolio construction
    all_ret = pd.concat(all_returns.values(), axis=1)
    first_idx = market_data["metadata"]["indices"][0]
    bench = market_data["benchmarks"][first_idx]
    bench_ret = np.log(bench / bench.shift(1)).dropna()

    best = build_portfolios(selected, all_ret, bench_ret, avg_rf, progress=False)

    if best.empty:
        return {
            "success": False,
            "error": "Could not generate portfolios with available stocks.",
        }

    # M6: AHP ranking
    engine = AHPEngine(profile=profile)
    ranking = engine.run(best, progress=False)

    # Serialize results
    weights = PROFILE_WEIGHTS[profile]
    sorted_criteria = sorted(weights.items(), key=lambda x: -x[1])
    top_criteria = [
        {"name": CRITERIA[c]["label"], "weight": w, "direction": CRITERIA[c]["dir"]}
        for c, w in sorted_criteria[:6]
    ]

    ranking_list = []
    for _, row in ranking.iterrows():
        ranking_list.append({
            "name": str(row["portafolio"]),
            "score": _safe_float(row["score_pct"], 0.0),
            "rank": int(row["ranking"]),
        })

    portfolios_detail = []
    for pname, prow in best.iterrows():
        portfolios_detail.append({
            "name": str(pname),
            "rentabilidad": round(_safe_float(prow.get("rentabilidad", 0)) * 100, 2),
            "volatilidad": round(_safe_float(prow.get("volatilidad", 0)) * 100, 2),
            "sharpe": round(_safe_float(prow.get("sharpe", 0)), 2),
            "max_drawdown": round(_safe_float(prow.get("max_drawdown", 0)) * 100, 2),
            "beta": round(_safe_float(prow.get("beta", 0)), 2),
            "alpha": round(_safe_float(prow.get("alpha", 0)) * 100, 2),
            "tickers": str(prow.get("tickers", "")),
            "pesos": str(prow.get("pesos", "")),
        })

    stocks_list = []
    for ticker, srow in selected.head(8).iterrows():
        stocks_list.append({
            "ticker": str(ticker),
            "rentabilidad": round(_safe_float(srow["rentabilidad"]) * 100, 2),
            "sharpe": round(_safe_float(srow["sharpe"]), 2),
            "volatilidad": round(_safe_float(srow["volatilidad"]) * 100, 2),
            "beta": round(_safe_float(srow["beta"]), 2),
        })

    winner = ranking_list[0]
    winner_name = ranking.iloc[0]["portafolio"]
    winner_data = best.loc[winner_name]

    allocation = []
    pesos_val = winner_data.get("pesos", "") if hasattr(winner_data, "get") else ""
    if isinstance(pesos_val, str) and pesos_val:
        for pair in pesos_val.split(", "):
            parts = pair.split(":")
            if len(parts) == 2:
                allocation.append({
                    "ticker": parts[0].strip(),
                    "weight": parts[1].strip(),
                })

    cr_val = _safe_float(engine.criteria_cr, 0.0)

    return {
        "success": True,
        "profile": profile,
        "profile_description": PROFILE_DESCRIPTIONS[profile],
        "scores": {},  # Not available without answers; populated by run_full_pipeline
        "top_criteria": top_criteria,
        "ranking": ranking_list,
        "portfolios": portfolios_detail,
        "stocks": stocks_list,
        "winner": winner,
        "allocation": allocation,
        "n_stocks_analyzed": int(len(consolidated)),
        "n_stocks_selected": int(len(selected)),
        "consistency_ratio": round(cr_val, 4),
        "is_synthetic": bool(is_synthetic),
        # Store internal data for backtest/export
        "_market_data": market_data,
        "_consolidated": consolidated,
        "_selected": selected,
        "_best_portfolios": best,
        "_ranking": ranking,
        "_engine": engine,
    }


def run_full_pipeline(answers: dict[str, str], use_live: bool = True) -> dict:
    """
    Run the complete pipeline starting from questionnaire answers.
    """
    profile, scores = score_answers(answers)
    result = run_analysis_pipeline(profile, use_live)

    if result.get("success"):
        result["scores"] = {k: v for k, v in scores.items() if v > 0}

    return result
