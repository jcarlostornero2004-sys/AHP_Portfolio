"""
Módulo 8 — Backtesting
========================
Evalúa la capacidad predictiva de la metodología AHP:
  1. Divide los datos en periodo de entrenamiento y periodo de test
  2. Ejecuta la metodología completa con datos de entrenamiento
  3. Mide el rendimiento real del portafolio seleccionado en el periodo de test
  4. Compara contra el benchmark (buy & hold del índice)

Métricas de evaluación:
  - Rentabilidad acumulada (portafolio vs benchmark)
  - Ratio de Sharpe realizado
  - Max drawdown realizado
  - Alpha realizado

Autor: [Tu nombre] — TFG
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats


def split_data(
    prices: pd.DataFrame,
    train_ratio: float = 0.7,
    train_end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Divide los precios en periodos de entrenamiento y test.

    Args:
        prices: DataFrame de precios diarios
        train_ratio: proporción para entrenamiento (default 70%)
        train_end_date: fecha específica de corte (override de train_ratio)

    Returns:
        (prices_train, prices_test)
    """
    if train_end_date:
        train = prices[prices.index <= train_end_date]
        test = prices[prices.index > train_end_date]
    else:
        split_idx = int(len(prices) * train_ratio)
        train = prices.iloc[:split_idx]
        test = prices.iloc[split_idx:]

    return train, test


def compute_portfolio_performance(
    prices_test: pd.DataFrame,
    tickers: List[str],
    weights: Dict[str, float],
    benchmark_prices: pd.Series,
    rf_annual: float = 0.04,
) -> Dict:
    """
    Calcula el rendimiento real del portafolio en el periodo de test.

    Args:
        prices_test: precios del periodo de test
        tickers: acciones del portafolio
        weights: pesos de cada acción {ticker: peso}
        benchmark_prices: precios del benchmark en periodo test
        rf_annual: tasa libre de riesgo

    Returns:
        Dict con métricas de rendimiento real.
    """
    # Filtrar tickers disponibles
    available = [t for t in tickers if t in prices_test.columns]
    if not available:
        return {"error": "No hay tickers disponibles en el periodo de test"}

    # Normalizar pesos
    w = np.array([weights.get(t, 1.0 / len(available)) for t in available])
    w = w / w.sum()

    # Rendimientos del portafolio
    returns = np.log(prices_test[available] / prices_test[available].shift(1)).dropna()
    port_returns = (returns * w).sum(axis=1)

    # Rendimiento acumulado
    port_cumulative = (1 + port_returns).cumprod()
    total_return = port_cumulative.iloc[-1] - 1

    # Benchmark
    bench_returns = np.log(benchmark_prices / benchmark_prices.shift(1)).dropna()
    bench_aligned = bench_returns.reindex(port_returns.index).dropna()
    bench_cumulative = (1 + bench_aligned).cumprod()
    bench_total_return = bench_cumulative.iloc[-1] - 1

    # Métricas
    trading_days = 252
    n_days = len(port_returns)
    annualization = trading_days / n_days if n_days > 0 else 1

    rp_annual = port_returns.mean() * trading_days
    sigma_annual = port_returns.std() * np.sqrt(trading_days)
    sharpe_realized = (rp_annual - rf_annual) / sigma_annual if sigma_annual > 0 else 0

    # Max drawdown realizado
    cummax = port_cumulative.cummax()
    drawdowns = (port_cumulative - cummax) / cummax
    max_dd = -drawdowns.min()

    # Sortino realizado
    rf_daily = rf_annual / trading_days
    downside = port_returns[port_returns < rf_daily]
    sigma_down = downside.std() * np.sqrt(trading_days) if len(downside) > 0 else sigma_annual
    sortino_realized = (rp_annual - rf_annual) / sigma_down if sigma_down > 0 else 0

    # Beta y Alpha realizados
    if len(bench_aligned) > 20:
        combined = pd.DataFrame({"port": port_returns, "bench": bench_aligned}).dropna()
        cov = combined.cov().iloc[0, 1]
        var_b = combined["bench"].var()
        beta_realized = cov / var_b if var_b > 0 else 1.0
        rm_annual = bench_aligned.mean() * trading_days
        alpha_realized = rp_annual - (rf_annual + beta_realized * (rm_annual - rf_annual))
    else:
        beta_realized = 1.0
        alpha_realized = 0.0

    # VaR realizado
    var_95 = -np.percentile(port_returns, 5) * np.sqrt(trading_days)

    return {
        "periodo_test_inicio": str(port_returns.index[0].date()),
        "periodo_test_fin": str(port_returns.index[-1].date()),
        "n_dias_test": n_days,
        "tickers": available,
        "pesos": {t: float(w_i) for t, w_i in zip(available, w)},
        # Portafolio AHP
        "rentabilidad_total_port": float(total_return),
        "rentabilidad_anual_port": float(rp_annual),
        "volatilidad_port": float(sigma_annual),
        "sharpe_realizado": float(sharpe_realized),
        "sortino_realizado": float(sortino_realized),
        "max_drawdown_port": float(max_dd),
        "var_95_port": float(var_95),
        "beta_realizado": float(beta_realized),
        "alpha_realizado": float(alpha_realized),
        # Benchmark
        "rentabilidad_total_bench": float(bench_total_return),
        "rentabilidad_anual_bench": float(bench_aligned.mean() * trading_days),
        "volatilidad_bench": float(bench_aligned.std() * np.sqrt(trading_days)),
        # Comparación
        "exceso_rentabilidad": float(total_return - bench_total_return),
        "batio_al_benchmark": total_return > bench_total_return,
        # Series temporales (para gráficos)
        "serie_port": port_cumulative,
        "serie_bench": bench_cumulative,
    }


def run_backtest(
    prices: pd.DataFrame,
    benchmark_prices: pd.Series,
    tickers: List[str],
    weights: Dict[str, float],
    rf_annual: float = 0.04,
    train_ratio: float = 0.7,
    train_end_date: Optional[str] = None,
    progress: bool = True,
) -> Dict:
    """
    Ejecuta el backtest completo.

    Args:
        prices: precios completos (train + test)
        benchmark_prices: precios del benchmark completos
        tickers: acciones del portafolio seleccionado
        weights: pesos del portafolio
        rf_annual: tasa libre de riesgo
        train_ratio: proporción entrenamiento
        train_end_date: fecha de corte (opcional)
    """
    if progress:
        print("\n" + "=" * 60)
        print("  MÓDULO 8 — BACKTESTING")
        print("=" * 60)

    # Dividir datos
    prices_train, prices_test = split_data(prices, train_ratio, train_end_date)
    bench_train, bench_test = split_data(
        benchmark_prices.to_frame(), train_ratio, train_end_date
    )
    bench_test = bench_test.iloc[:, 0]

    if progress:
        print(f"\n  Periodo entrenamiento: {prices_train.index[0].date()} → {prices_train.index[-1].date()} ({len(prices_train)} días)")
        print(f"  Periodo test:          {prices_test.index[0].date()} → {prices_test.index[-1].date()} ({len(prices_test)} días)")
        print(f"  Portafolio: {', '.join(tickers)}")

    # Evaluar rendimiento real
    results = compute_portfolio_performance(
        prices_test, tickers, weights, bench_test, rf_annual
    )

    if progress and "error" not in results:
        print(f"\n  {'─' * 50}")
        print(f"  RESULTADOS DEL BACKTEST:")
        print(f"  {'─' * 50}")
        print(f"                        Portafolio AHP    Benchmark")
        print(f"  Rentab. total:        {results['rentabilidad_total_port']:>10.2%}     {results['rentabilidad_total_bench']:>10.2%}")
        print(f"  Rentab. anualizada:   {results['rentabilidad_anual_port']:>10.2%}     {results['rentabilidad_anual_bench']:>10.2%}")
        print(f"  Volatilidad:          {results['volatilidad_port']:>10.2%}     {results['volatilidad_bench']:>10.2%}")
        print(f"  Sharpe realizado:     {results['sharpe_realizado']:>10.2f}")
        print(f"  Sortino realizado:    {results['sortino_realizado']:>10.2f}")
        print(f"  Max Drawdown:         {results['max_drawdown_port']:>10.2%}")
        print(f"  Alpha realizado:      {results['alpha_realizado']:>10.2%}")
        print(f"  Beta realizado:       {results['beta_realizado']:>10.2f}")
        print(f"  {'─' * 50}")
        beaten = results["batio_al_benchmark"]
        excess = results["exceso_rentabilidad"]
        if beaten:
            print(f"  EL PORTAFOLIO AHP SUPERÓ AL BENCHMARK por {excess:.2%}")
        else:
            print(f"  El benchmark superó al portafolio AHP por {-excess:.2%}")
        print(f"  {'─' * 50}")

    return results


# ─── DEMO ───
def demo():
    """Demo de backtesting con datos sintéticos."""
    print("\n" + "█" * 60)
    print("  DEMO — Backtesting")
    print("█" * 60)

    np.random.seed(42)
    n_days = 504  # ~2 años
    dates = pd.bdate_range("2023-01-02", periods=n_days)

    # Simular precios
    tickers = ["AAPL", "MSFT", "GOOGL", "JNJ", "PG"]
    drifts = [0.12, 0.15, 0.10, 0.06, 0.05]
    vols_sim = [0.25, 0.28, 0.30, 0.15, 0.12]

    prices_data = {}
    for t, mu, sigma in zip(tickers, drifts, vols_sim):
        daily_r = np.random.normal(mu / 252, sigma / np.sqrt(252), n_days)
        prices_data[t] = 100 * np.exp(np.cumsum(daily_r))

    prices = pd.DataFrame(prices_data, index=dates)

    # Benchmark
    bench_r = np.random.normal(0.10 / 252, 0.18 / np.sqrt(252), n_days)
    benchmark = pd.Series(1000 * np.exp(np.cumsum(bench_r)), index=dates, name="SP500")

    # Simular que AHP seleccionó estas acciones con estos pesos
    selected_tickers = ["MSFT", "GOOGL", "AAPL"]
    selected_weights = {"MSFT": 0.40, "GOOGL": 0.35, "AAPL": 0.25}

    results = run_backtest(
        prices=prices,
        benchmark_prices=benchmark,
        tickers=selected_tickers,
        weights=selected_weights,
        rf_annual=0.04,
        train_ratio=0.7,
    )

    return results


if __name__ == "__main__":
    demo()
