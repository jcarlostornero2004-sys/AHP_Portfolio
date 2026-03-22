"""
Main v2 — Pipeline completo AHP Portfolio Selector
=====================================================
Ejecuta todos los módulos en secuencia:
  M0: Cuestionario → perfil inversor
  M1: Perfil → pesos AHP + filtros
  M2: Descarga de datos (o sintéticos)
  M3: Análisis individual de acciones
  M4: Filtrado y selección
  M5: Construcción de portafolios (Markowitz)
  M6: Motor AHP (15 criterios)
  M7: Exportación a Excel
  M8: Backtesting

Uso:
  python main.py                          # Pipeline completo (datos sintéticos)
  python main.py --profile moderado       # Saltar cuestionario
  python main.py --live                   # Datos reales de Yahoo Finance
  python main.py --live --profile agresivo
  python main.py --backtest               # Incluir backtesting
"""

import sys
import argparse
import numpy as np
import pandas as pd
from datetime import datetime

from questionnaire import run_questionnaire
from profiles import get_profile_config, print_profile_summary
from stock_analysis import compute_returns, analyze_stocks
from stock_filter import run_filtering
from portfolio_builder import build_portfolios
from ahp_engine_v2 import AHPEngine
from excel_export import export_to_excel
from backtester import run_backtest


def generate_synthetic_data():
    """Genera datos sintéticos realistas para 15 acciones de 3 índices."""
    np.random.seed(42)
    n_days = 504
    dates = pd.bdate_range("2023-01-02", periods=n_days)

    all_configs = {
        "sp500": {
            "AAPL":  {"drift": 0.12, "vol": 0.25, "sector": "Technology"},
            "MSFT":  {"drift": 0.18, "vol": 0.28, "sector": "Technology"},
            "JNJ":   {"drift": 0.05, "vol": 0.14, "sector": "Healthcare"},
            "PG":    {"drift": 0.04, "vol": 0.12, "sector": "Consumer Staples"},
            "JPM":   {"drift": 0.10, "vol": 0.22, "sector": "Financials"},
        },
        "eurostoxx": {
            "SAP.DE":  {"drift": 0.14, "vol": 0.26, "sector": "Technology"},
            "SIE.DE":  {"drift": 0.08, "vol": 0.20, "sector": "Industrials"},
            "SAN.MC":  {"drift": 0.06, "vol": 0.24, "sector": "Financials"},
            "MC.PA":   {"drift": 0.11, "vol": 0.22, "sector": "Consumer Discretionary"},
            "TTE.PA":  {"drift": 0.07, "vol": 0.26, "sector": "Energy"},
        },
        "nikkei": {
            "7203.T":  {"drift": 0.09, "vol": 0.22, "sector": "Automotive"},
            "6758.T":  {"drift": 0.15, "vol": 0.30, "sector": "Technology"},
            "9984.T":  {"drift": 0.20, "vol": 0.35, "sector": "Technology"},
            "4502.T":  {"drift": 0.04, "vol": 0.16, "sector": "Healthcare"},
            "8306.T":  {"drift": 0.07, "vol": 0.20, "sector": "Financials"},
        },
    }

    all_prices = {}
    all_benchmarks = {}
    stock_info_rows = []

    for index_name, stocks in all_configs.items():
        prices_dict = {}
        for ticker, cfg in stocks.items():
            daily_r = np.random.normal(cfg["drift"] / 252, cfg["vol"] / np.sqrt(252), n_days)
            prices_dict[ticker] = 100 * np.exp(np.cumsum(daily_r))
            stock_info_rows.append({
                "ticker": ticker, "sector": cfg["sector"],
                "market_cap": np.random.uniform(50e9, 500e9),
                "dividend_yield": np.random.uniform(0.005, 0.04),
                "index": index_name,
            })
        all_prices[index_name] = pd.DataFrame(prices_dict, index=dates)

        bench_drift = np.mean([s["drift"] for s in stocks.values()])
        bench_vol = np.mean([s["vol"] for s in stocks.values()]) * 0.7
        bench_r = np.random.normal(bench_drift / 252, bench_vol / np.sqrt(252), n_days)
        all_benchmarks[index_name] = pd.Series(
            1000 * np.exp(np.cumsum(bench_r)), index=dates, name=index_name
        )

    stock_info = pd.DataFrame(stock_info_rows).set_index("ticker")
    risk_free = {"sp500": 0.04, "eurostoxx": 0.025, "nikkei": 0.01}

    return {
        "prices": all_prices, "benchmarks": all_benchmarks,
        "risk_free": risk_free, "stock_info": stock_info,
        "metadata": {
            "start_date": str(dates[0].date()), "end_date": str(dates[-1].date()),
            "indices": list(all_configs.keys()),
            "total_tickers": sum(len(v) for v in all_configs.values()),
            "synthetic": True,
        },
    }


def run_pipeline(
    profile_override=None, use_live_data=False,
    do_backtest=False, excel_filename=None,
):
    print("\n" + "█" * 60)
    print("  AHP PORTFOLIO SELECTOR — Pipeline completo")
    print("  S&P 500 · Eurostoxx 600 · Nikkei 225")
    print("  15 criterios · 5 categorías · 7 perfiles")
    print("█" * 60)

    # ═══ M0: CUESTIONARIO ═══
    if profile_override:
        profile = profile_override
        print(f"\n  Perfil proporcionado: {profile.upper()}")
    else:
        profile, scores = run_questionnaire(interactive=True)

    # ═══ M1: PERFIL ═══
    config = get_profile_config(profile)
    print_profile_summary(profile)

    # ═══ M2: DATOS ═══
    if use_live_data:
        try:
            from data_loader import load_market_data
            market_data = load_market_data(
                period_years=2,
                max_per_index=config["filters"].max_stocks_per_index,
                progress=True,
            )
        except Exception as e:
            print(f"\n  Error con datos reales: {e}")
            print("  Usando datos sintéticos...")
            market_data = generate_synthetic_data()
    else:
        print("\n  Usando datos sintéticos (usa --live para datos reales)")
        market_data = generate_synthetic_data()

    # ═══ M3: ANÁLISIS INDIVIDUAL ═══
    print("\n" + "=" * 60)
    print("  MÓDULO 3 — ANÁLISIS INDIVIDUAL DE ACCIONES")
    print("=" * 60)

    all_analyses = []
    all_returns = {}

    for idx in market_data["metadata"]["indices"]:
        prices = market_data["prices"][idx]
        benchmark = market_data["benchmarks"][idx]
        rf = market_data["risk_free"][idx]
        analysis = analyze_stocks(prices, benchmark, rf, idx, progress=True)
        analysis["region"] = idx
        all_analyses.append(analysis)
        all_returns[idx] = compute_returns(prices)

    consolidated = pd.concat(all_analyses)
    print(f"\n  TOTAL: {len(consolidated)} acciones analizadas")

    # ═══ M4: FILTRADO ═══
    avg_rf = np.mean(list(market_data["risk_free"].values()))
    market_vars = []
    for idx in market_data["metadata"]["indices"]:
        bench = market_data["benchmarks"][idx]
        bench_ret = np.log(bench / bench.shift(1)).dropna()
        market_vars.append(bench_ret.var() * 252)
    avg_market_var = np.mean(market_vars)

    selected = run_filtering(
        analysis=consolidated, filters=config["filters"],
        rf_annual=avg_rf, market_variance=avg_market_var,
        stock_info=market_data.get("stock_info"),
        profile_name=profile, progress=True,
    )

    # ═══ M5: PORTAFOLIOS ═══
    all_returns_combined = pd.concat(all_returns.values(), axis=1)
    first_idx = market_data["metadata"]["indices"][0]
    bench_series = market_data["benchmarks"][first_idx]
    bench_returns = np.log(bench_series / bench_series.shift(1)).dropna()

    best_portfolios = build_portfolios(
        selected_stocks=selected, returns_df=all_returns_combined,
        benchmark_returns=bench_returns, rf_annual=avg_rf, progress=True,
    )

    # ═══ M6: AHP ═══
    engine = AHPEngine(profile=profile)
    ranking = engine.run(best_portfolios, progress=True)
    ahp_report = engine.get_full_report()

    # ═══ M7: EXCEL ═══
    if excel_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        excel_filename = f"AHP_Portfolio_{profile}_{timestamp}.xlsx"

    export_to_excel(
        profile=profile, filters=config["filters"],
        portfolios=best_portfolios, ranking=ranking,
        ahp_report=ahp_report, analysis=consolidated,
        filename=excel_filename, progress=True,
    )

    # ═══ M8: BACKTESTING ═══
    backtest_results = None
    if do_backtest:
        winner_name = ranking.iloc[0]["portafolio"]
        winner_data = best_portfolios.loc[winner_name]

        if "pesos" in winner_data and isinstance(winner_data["pesos"], str):
            bt_tickers = []
            bt_weights = {}
            for pair in winner_data["pesos"].split(", "):
                parts = pair.split(":")
                if len(parts) == 2:
                    t = parts[0].strip()
                    w = float(parts[1].strip().replace("%", "")) / 100
                    bt_tickers.append(t)
                    bt_weights[t] = w
        else:
            bt_tickers = list(selected.index[:3])
            bt_weights = {t: 1.0 / len(bt_tickers) for t in bt_tickers}

        all_prices_combined = pd.concat(
            [market_data["prices"][idx] for idx in market_data["metadata"]["indices"]],
            axis=1,
        )

        backtest_results = run_backtest(
            prices=all_prices_combined, benchmark_prices=bench_series,
            tickers=bt_tickers, weights=bt_weights,
            rf_annual=avg_rf, train_ratio=0.7, progress=True,
        )

    # ═══ RESUMEN FINAL ═══
    winner = ranking.iloc[0]
    print("\n" + "█" * 60)
    print("  PIPELINE COMPLETADO")
    print("█" * 60)
    print(f"\n  Perfil:              {profile.upper()}")
    print(f"  Acciones analizadas: {len(consolidated)}")
    print(f"  Acciones filtradas:  {len(selected)}")
    print(f"  Portafolios creados: {len(best_portfolios)}")
    print(f"  Criterios AHP:       15 (5 categorías)")
    print(f"  CR criterios:        {ahp_report['criteria_cr']:.4f} (consistente)")
    print(f"\n  PORTAFOLIO GANADOR:  {winner['portafolio']}")
    print(f"  Puntuación AHP:      {winner['score_pct']:.1f}%")
    print(f"\n  Excel generado:      {excel_filename}")
    if backtest_results and "error" not in backtest_results:
        beaten = backtest_results["batio_al_benchmark"]
        icon = "SUPERÓ" if beaten else "no superó"
        print(f"  Backtesting:         El portafolio {icon} al benchmark")
    print("\n" + "█" * 60)

    return {
        "profile": profile, "ranking": ranking,
        "best_portfolios": best_portfolios, "analysis": consolidated,
        "selected": selected, "ahp_report": ahp_report,
        "backtest": backtest_results, "excel_file": excel_filename,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AHP Portfolio Selector")
    parser.add_argument("--profile", type=str, default=None,
        help="Perfil (conservador/moderado/agresivo/muy_agresivo/dividendos/tecnologico/esg)")
    parser.add_argument("--live", action="store_true", help="Datos reales (Yahoo Finance)")
    parser.add_argument("--backtest", action="store_true", help="Incluir backtesting")
    parser.add_argument("--output", type=str, default=None, help="Nombre del Excel")
    args = parser.parse_args()

    run_pipeline(
        profile_override=args.profile, use_live_data=args.live,
        do_backtest=args.backtest, excel_filename=args.output,
    )
