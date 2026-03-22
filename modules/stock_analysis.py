"""
Módulo 3 — Análisis individual de acciones
=============================================
Calcula los 15 indicadores financieros para cada acción:

Cat 1 - Rendimiento:  rentabilidad, Sharpe, Sortino, Alpha Jensen
Cat 2 - Riesgo:       volatilidad, VaR 95%, CVaR 95%, Max Drawdown
Cat 3 - Eficiencia:   beta, tracking error, rentab-kp
Cat 4 - Estabilidad:  coef. variación, skewness
Cat 5 - Diversif.:    (se calculan a nivel portafolio, no individual)

Basado en: Markowitz (1952), Sharpe (1966, 1970), Sortino & Price (1994),
Morgan (1996), Artzner et al. (1999), Escobar (2015).
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Optional


# ─────────────────────────────────────────────────────────────────
# CÁLCULOS INDIVIDUALES POR ACCIÓN
# ─────────────────────────────────────────────────────────────────

def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calcula rendimientos logarítmicos diarios."""
    return np.log(prices / prices.shift(1)).dropna()


def annualized_return(returns: pd.Series, trading_days: int = 252) -> float:
    """Rentabilidad anualizada a partir de rendimientos diarios."""
    return returns.mean() * trading_days


def annualized_volatility(returns: pd.Series, trading_days: int = 252) -> float:
    """Volatilidad (desv. estándar) anualizada."""
    return returns.std() * np.sqrt(trading_days)


def sharpe_ratio(returns: pd.Series, rf_annual: float, trading_days: int = 252) -> float:
    """Ratio de Sharpe = (Rp - Rf) / σp."""
    rp = annualized_return(returns, trading_days)
    sigma = annualized_volatility(returns, trading_days)
    if sigma == 0:
        return 0.0
    return (rp - rf_annual) / sigma


def sortino_ratio(returns: pd.Series, rf_annual: float, trading_days: int = 252) -> float:
    """Ratio de Sortino = (Rp - Rf) / σ_downside."""
    rp = annualized_return(returns, trading_days)
    rf_daily = rf_annual / trading_days
    downside = returns[returns < rf_daily]
    if len(downside) == 0:
        return 0.0
    sigma_down = downside.std() * np.sqrt(trading_days)
    if sigma_down == 0:
        return 0.0
    return (rp - rf_annual) / sigma_down


def beta_stock(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Beta = Cov(Ri, Rm) / Var(Rm)."""
    aligned = pd.DataFrame({"stock": returns, "bench": benchmark_returns}).dropna()
    if len(aligned) < 30:
        return 1.0
    cov = aligned.cov().iloc[0, 1]
    var_m = aligned["bench"].var()
    if var_m == 0:
        return 1.0
    return cov / var_m


def alpha_jensen(
    returns: pd.Series,
    benchmark_returns: pd.Series,
    rf_annual: float,
    trading_days: int = 252,
) -> float:
    """Alpha de Jensen = Rp - [Rf + β(Rm - Rf)]."""
    rp = annualized_return(returns, trading_days)
    rm = annualized_return(benchmark_returns, trading_days)
    b = beta_stock(returns, benchmark_returns)
    return rp - (rf_annual + b * (rm - rf_annual))


def var_parametric(returns: pd.Series, confidence: float = 0.95, trading_days: int = 252) -> float:
    """VaR paramétrico anualizado (asumiendo normalidad)."""
    mu = annualized_return(returns, trading_days)
    sigma = annualized_volatility(returns, trading_days)
    z = stats.norm.ppf(1 - confidence)
    return -(mu + z * sigma)


def cvar_historical(returns: pd.Series, confidence: float = 0.95) -> float:
    """CVaR / Expected Shortfall (histórico, anualizado)."""
    cutoff = returns.quantile(1 - confidence)
    tail = returns[returns <= cutoff]
    if len(tail) == 0:
        return 0.0
    return -tail.mean() * np.sqrt(252)


def max_drawdown(prices: pd.Series) -> float:
    """Máximo drawdown (caída máxima desde pico)."""
    cummax = prices.cummax()
    drawdowns = (prices - cummax) / cummax
    return -drawdowns.min()


def coefficient_of_variation(returns: pd.Series) -> float:
    """Coeficiente de variación = σ / |μ|."""
    mu = returns.mean()
    if abs(mu) < 1e-10:
        return float("inf")
    return returns.std() / abs(mu)


def tracking_error(returns: pd.Series, benchmark_returns: pd.Series, trading_days: int = 252) -> float:
    """Tracking error anualizado = σ(Ri - Rm)."""
    aligned = pd.DataFrame({"stock": returns, "bench": benchmark_returns}).dropna()
    diff = aligned["stock"] - aligned["bench"]
    return diff.std() * np.sqrt(trading_days)


def cost_of_capital_capm(beta: float, rf_annual: float, rm_annual: float) -> float:
    """Coste de capital según CAPM: kp = Rf + β(Rm - Rf)."""
    return rf_annual + beta * (rm_annual - rf_annual)


# ─────────────────────────────────────────────────────────────────
# ANÁLISIS COMPLETO DE TODAS LAS ACCIONES
# ─────────────────────────────────────────────────────────────────

def analyze_stocks(
    prices: pd.DataFrame,
    benchmark_prices: pd.Series,
    rf_annual: float,
    index_key: str = "",
    progress: bool = True,
) -> pd.DataFrame:
    """
    Calcula todos los indicadores para cada acción de un índice.

    Args:
        prices: DataFrame de precios (columnas = tickers)
        benchmark_prices: Series de precios del benchmark
        rf_annual: tasa libre de riesgo anualizada
        index_key: nombre del índice (para metadata)
        progress: mostrar progreso

    Returns:
        DataFrame con una fila por acción y columnas con los indicadores.
    """
    returns = compute_returns(prices)
    bench_returns = compute_returns(benchmark_prices.to_frame()).iloc[:, 0]
    rm_annual = annualized_return(bench_returns)

    if progress:
        print(f"\n  Analizando {len(returns.columns)} acciones de {index_key}...")

    records = []
    for ticker in returns.columns:
        r = returns[ticker].dropna()
        p = prices[ticker].dropna()

        if len(r) < 60:
            continue

        b = beta_stock(r, bench_returns)
        kp = cost_of_capital_capm(b, rf_annual, rm_annual)
        ret_annual = annualized_return(r)

        record = {
            "ticker": ticker,
            "index": index_key,
            # Cat 1: Rendimiento
            "rentabilidad": ret_annual,
            "sharpe": sharpe_ratio(r, rf_annual),
            "sortino": sortino_ratio(r, rf_annual),
            "alpha": alpha_jensen(r, bench_returns, rf_annual),
            # Cat 2: Riesgo
            "volatilidad": annualized_volatility(r),
            "var_95": var_parametric(r),
            "cvar_95": cvar_historical(r),
            "max_drawdown": max_drawdown(p),
            # Cat 3: Eficiencia
            "beta": b,
            "tracking_error": tracking_error(r, bench_returns),
            "rentab_kp": ret_annual - kp,
            # Cat 4: Estabilidad
            "cv": coefficient_of_variation(r),
            "skewness": float(r.skew()),
            # Metadata
            "kp": kp,
            "n_days": len(r),
        }
        records.append(record)

    df = pd.DataFrame(records).set_index("ticker")

    if progress:
        print(f"  → {len(df)} acciones analizadas")
        print(f"    Rentab. media: {df['rentabilidad'].mean():.2%}")
        print(f"    Volatilidad media: {df['volatilidad'].mean():.2%}")
        print(f"    Sharpe medio: {df['sharpe'].mean():.2f}")

    return df


def analyze_all_indices(market_data: Dict, progress: bool = True) -> pd.DataFrame:
    """
    Ejecuta el análisis completo para todos los índices cargados.

    Args:
        market_data: output de data_loader.load_market_data()

    Returns:
        DataFrame consolidado con todas las acciones y sus indicadores.
    """
    if progress:
        print("\n" + "=" * 60)
        print("  MÓDULO 3 — ANÁLISIS INDIVIDUAL DE ACCIONES")
        print("=" * 60)

    all_analyses = []

    for idx in market_data["metadata"]["indices"]:
        prices = market_data["prices"][idx]
        benchmark = market_data["benchmarks"][idx]
        rf = market_data["risk_free"][idx]

        analysis = analyze_stocks(prices, benchmark, rf, idx, progress)
        all_analyses.append(analysis)

    consolidated = pd.concat(all_analyses)

    if progress:
        print(f"\n{'─' * 60}")
        print(f"  TOTAL: {len(consolidated)} acciones analizadas")
        print(f"  Rentab. positiva: {(consolidated['rentabilidad'] > 0).sum()}")
        print(f"  Rentab. negativa: {(consolidated['rentabilidad'] <= 0).sum()}")
        print(f"  Alpha positivo:   {(consolidated['alpha'] > 0).sum()}")
        print(f"{'─' * 60}")

    return consolidated


# ─────────────────────────────────────────────────────────────────
# DEMO CON DATOS SINTÉTICOS (sin necesidad de internet)
# ─────────────────────────────────────────────────────────────────

def demo_synthetic():
    """Demo con datos ficticios para probar los cálculos."""
    print("\n" + "=" * 60)
    print("  DEMO — Análisis individual (datos sintéticos)")
    print("=" * 60)

    np.random.seed(42)
    n_days = 504  # ~2 años
    dates = pd.bdate_range("2023-01-02", periods=n_days)

    # Generar precios simulados
    tickers = ["AAPL", "MSFT", "GOOGL", "JNJ", "PG"]
    drifts = [0.12, 0.15, 0.10, 0.06, 0.05]  # rentab. anual esperada
    vols = [0.25, 0.28, 0.30, 0.15, 0.12]     # volatilidad anual

    prices_data = {}
    for t, mu, sigma in zip(tickers, drifts, vols):
        daily_returns = np.random.normal(mu / 252, sigma / np.sqrt(252), n_days)
        prices_data[t] = 100 * np.exp(np.cumsum(daily_returns))

    prices = pd.DataFrame(prices_data, index=dates)

    # Benchmark (S&P 500 simulado)
    bench_returns = np.random.normal(0.10 / 252, 0.18 / np.sqrt(252), n_days)
    benchmark = pd.Series(1000 * np.exp(np.cumsum(bench_returns)), index=dates, name="SP500")

    rf = 0.04  # 4%

    results = analyze_stocks(prices, benchmark, rf, "demo", progress=True)

    print("\n  Resultados:")
    display_cols = ["rentabilidad", "sharpe", "sortino", "alpha",
                    "volatilidad", "var_95", "max_drawdown", "beta", "cv"]
    print(results[display_cols].round(4).to_string())

    return results


if __name__ == "__main__":
    demo_synthetic()
