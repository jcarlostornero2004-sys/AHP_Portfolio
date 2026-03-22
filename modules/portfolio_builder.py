"""
Módulo 5 — Construcción de portafolios candidatos
====================================================
Con las N acciones seleccionadas (Módulo 4):
  1. Genera combinaciones de portafolios (2 a N acciones)
  2. Calcula pesos óptimos vía Markowitz (mínima varianza)
  3. Calcula los 15 indicadores para cada portafolio
  4. Selecciona los 5 mejores portafolios (P1-P5) según criterios C1-C5

Basado en: Markowitz (1952), Escobar (2015, etapa 3).
"""

import numpy as np
import pandas as pd
from itertools import combinations
from scipy.optimize import minimize
from scipy import stats
from typing import List, Tuple, Dict, Optional


# ─────────────────────────────────────────────────────────────────
# OPTIMIZACIÓN DE MARKOWITZ
# ─────────────────────────────────────────────────────────────────

def portfolio_return(weights, mean_returns):
    """Rentabilidad esperada del portafolio."""
    return np.dot(weights, mean_returns) * 252


def portfolio_volatility(weights, cov_matrix):
    """Volatilidad (desv. est.) anualizada del portafolio."""
    return np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))


def min_variance_weights(mean_returns, cov_matrix, target_return=None):
    """
    Calcula los pesos de mínima varianza (Markowitz 1952).
    Si target_return es None, busca el portafolio de mínima varianza global.
    """
    n = len(mean_returns)
    init_weights = np.ones(n) / n
    bounds = tuple((0.05, 0.60) for _ in range(n))  # mín 5%, máx 60% por acción
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    if target_return is not None:
        constraints.append({
            "type": "eq",
            "fun": lambda w: portfolio_return(w, mean_returns) - target_return,
        })

    result = minimize(
        lambda w: portfolio_volatility(w, cov_matrix),
        init_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000},
    )

    if result.success:
        return result.x
    return init_weights  # fallback: pesos iguales


def max_sharpe_weights(mean_returns, cov_matrix, rf_annual=0.04):
    """Calcula los pesos que maximizan el ratio de Sharpe."""
    n = len(mean_returns)
    init_weights = np.ones(n) / n
    bounds = tuple((0.05, 0.60) for _ in range(n))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]

    def neg_sharpe(w):
        ret = portfolio_return(w, mean_returns)
        vol = portfolio_volatility(w, cov_matrix)
        if vol == 0:
            return 0
        return -(ret - rf_annual) / vol

    result = minimize(
        neg_sharpe,
        init_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    if result.success:
        return result.x
    return init_weights


# ─────────────────────────────────────────────────────────────────
# CÁLCULO DE MÉTRICAS DEL PORTAFOLIO
# ─────────────────────────────────────────────────────────────────

def compute_portfolio_metrics(
    weights: np.ndarray,
    returns_df: pd.DataFrame,
    benchmark_returns: pd.Series,
    rf_annual: float,
    tickers: List[str],
    portfolio_name: str,
) -> Dict:
    """
    Calcula los 15 indicadores para un portafolio dado.
    """
    # Rendimientos del portafolio
    port_returns = (returns_df[tickers] * weights).sum(axis=1)
    port_cumulative = (1 + port_returns).cumprod()

    # Alinear con benchmark
    aligned = pd.DataFrame({
        "port": port_returns,
        "bench": benchmark_returns,
    }).dropna()

    rp = port_returns.mean() * 252
    sigma = port_returns.std() * np.sqrt(252)
    rf_daily = rf_annual / 252
    rm = benchmark_returns.mean() * 252

    # Downside deviation (para Sortino)
    downside = port_returns[port_returns < rf_daily]
    sigma_down = downside.std() * np.sqrt(252) if len(downside) > 0 else sigma

    # Beta
    if len(aligned) > 30:
        cov_pb = aligned.cov().iloc[0, 1]
        var_b = aligned["bench"].var()
        beta = cov_pb / var_b if var_b > 0 else 1.0
    else:
        beta = 1.0

    # Alpha de Jensen
    alpha = rp - (rf_annual + beta * (rm - rf_annual))

    # Coste de capital CAPM
    kp = rf_annual + beta * (rm - rf_annual)

    # VaR paramétrico 95%
    z95 = stats.norm.ppf(0.05)
    var_95 = -(rp + z95 * sigma)

    # CVaR histórico 95%
    cutoff = port_returns.quantile(0.05)
    tail = port_returns[port_returns <= cutoff]
    cvar_95 = -tail.mean() * np.sqrt(252) if len(tail) > 0 else var_95

    # Max Drawdown
    cummax = port_cumulative.cummax()
    drawdowns = (port_cumulative - cummax) / cummax
    max_dd = -drawdowns.min()

    # Tracking error
    diff = aligned["port"] - aligned["bench"]
    te = diff.std() * np.sqrt(252)

    # Correlación media entre activos
    corr_matrix = returns_df[tickers].corr()
    n = len(tickers)
    if n > 1:
        mask = np.triu(np.ones((n, n), dtype=bool), k=1)
        corr_media = corr_matrix.values[mask].mean()
    else:
        corr_media = 1.0

    # Diversificación geográfica (índice HHI inverso)
    # Se calcula basándose en los índices de origen de cada acción
    # Simplificado: distribución uniforme por ahora
    div_geo = 1.0 - (1.0 / max(n, 1))

    return {
        "nombre": portfolio_name,
        "tickers": ", ".join(tickers),
        "n_acciones": n,
        "pesos": ", ".join([f"{t}:{w:.1%}" for t, w in zip(tickers, weights)]),
        # Cat 1: Rendimiento
        "rentabilidad": rp,
        "sharpe": (rp - rf_annual) / sigma if sigma > 0 else 0,
        "sortino": (rp - rf_annual) / sigma_down if sigma_down > 0 else 0,
        "alpha": alpha,
        # Cat 2: Riesgo
        "volatilidad": sigma,
        "var_95": var_95,
        "cvar_95": cvar_95,
        "max_drawdown": max_dd,
        # Cat 3: Eficiencia
        "beta": beta,
        "tracking_error": te,
        "rentab_kp": rp - kp,
        # Cat 4: Estabilidad
        "cv": sigma / abs(rp) if abs(rp) > 1e-10 else float("inf"),
        "skewness": float(port_returns.skew()),
        # Cat 5: Diversificación
        "corr_media": corr_media,
        "div_geo": div_geo,
        # Metadata
        "kp": kp,
    }


# ─────────────────────────────────────────────────────────────────
# GENERACIÓN Y SELECCIÓN DE PORTAFOLIOS
# ─────────────────────────────────────────────────────────────────

def generate_portfolios(
    selected_stocks: pd.DataFrame,
    returns_df: pd.DataFrame,
    benchmark_returns: pd.Series,
    rf_annual: float = 0.04,
    min_stocks: int = 3,
    max_stocks: int = 5,
    progress: bool = True,
) -> pd.DataFrame:
    """
    Genera portafolios candidatos con diferentes combinaciones de acciones.

    Args:
        selected_stocks: acciones filtradas (Módulo 4)
        returns_df: rendimientos diarios de todas las acciones
        benchmark_returns: rendimientos del benchmark
        rf_annual: tasa libre de riesgo
        min_stocks: mínimo de acciones por portafolio
        max_stocks: máximo de acciones por portafolio

    Returns:
        DataFrame con todos los portafolios y sus 15 métricas.
    """
    tickers = list(selected_stocks.index)
    n = len(tickers)

    if progress:
        print(f"\n  Generando portafolios con {n} acciones ({min_stocks} a {max_stocks} por portafolio)...")

    all_portfolios = []
    portfolio_count = 0

    import random
    for size in range(min_stocks, min(max_stocks + 1, n + 1)):
        combos = list(combinations(tickers, size))
        # Cap combinations to avoid very long computation
        if len(combos) > 200:
            random.seed(42)
            combos = random.sample(combos, 200)
        if progress:
            print(f"    {size} acciones: {len(combos)} combinaciones")

        for combo in combos:
            combo_list = list(combo)
            combo_returns = returns_df[combo_list].dropna()

            if len(combo_returns) < 60:
                continue

            mean_ret = combo_returns.mean().values
            cov = combo_returns.cov().values

            # Optimización 1: Mínima varianza
            w_minvar = min_variance_weights(mean_ret, cov)

            # Optimización 2: Máximo Sharpe
            w_sharpe = max_sharpe_weights(mean_ret, cov, rf_annual)

            for opt_name, weights in [("MinVar", w_minvar), ("MaxSharpe", w_sharpe)]:
                portfolio_count += 1
                name = f"E{size}-{portfolio_count}"

                metrics = compute_portfolio_metrics(
                    weights=weights,
                    returns_df=combo_returns,
                    benchmark_returns=benchmark_returns,
                    rf_annual=rf_annual,
                    tickers=combo_list,
                    portfolio_name=name,
                )
                metrics["optimizacion"] = opt_name
                all_portfolios.append(metrics)

    df = pd.DataFrame(all_portfolios)

    if progress:
        print(f"  → {len(df)} portafolios generados en total")

    return df


def select_best_portfolios(
    portfolios_df: pd.DataFrame,
    n_best: int = 5,
    progress: bool = True,
) -> pd.DataFrame:
    """
    Selecciona los 5 mejores portafolios según criterios C1-C5 de Escobar (2015).

    C1: Mejor balance rentabilidad/riesgo/CV (max Sharpe)
    C2: Menor probabilidad de pérdida (min VaR)
    C3: Menor coste de capital (min kp)
    C4: Mayor diferencia rentabilidad - kp
    C5: Menor max drawdown
    """
    if portfolios_df.empty:
        if progress:
            print("  → No hay portafolios para seleccionar.")
        return pd.DataFrame()

    if progress:
        print(f"\n  Seleccionando los {n_best} mejores portafolios (criterios C1-C5)...")

    selected = {}

    # C1: Mejor Sharpe ratio
    c1 = portfolios_df.sort_values("sharpe", ascending=False).iloc[0]
    selected["P1"] = {"criterio": "C1 (Max Sharpe)", "data": c1}

    # C2: Menor VaR
    c2 = portfolios_df.sort_values("var_95", ascending=True).iloc[0]
    selected["P2"] = {"criterio": "C2 (Min VaR)", "data": c2}

    # C3: Menor coste de capital
    c3 = portfolios_df.sort_values("kp", ascending=True).iloc[0]
    selected["P3"] = {"criterio": "C3 (Min kp)", "data": c3}

    # C4: Mayor rentab - kp
    c4 = portfolios_df.sort_values("rentab_kp", ascending=False).iloc[0]
    selected["P4"] = {"criterio": "C4 (Max Rentab-kp)", "data": c4}

    # C5: Menor max drawdown
    c5 = portfolios_df.sort_values("max_drawdown", ascending=True).iloc[0]
    selected["P5"] = {"criterio": "C5 (Min Drawdown)", "data": c5}

    # Construir DataFrame resultado
    rows = []
    for pname, info in selected.items():
        row = info["data"].to_dict()
        row["nombre"] = pname
        row["criterio_seleccion"] = info["criterio"]
        rows.append(row)

    result = pd.DataFrame(rows).set_index("nombre")

    # Eliminar duplicados (si el mismo portafolio gana en varios criterios)
    result = result[~result.index.duplicated(keep="first")]

    # Si tenemos menos de 5, completar con los mejores por Sortino
    if len(result) < n_best:
        remaining = portfolios_df[~portfolios_df["nombre"].isin(result.index)]
        remaining = remaining.sort_values("sortino", ascending=False)
        for _, row in remaining.iterrows():
            if len(result) >= n_best:
                break
            pname = f"P{len(result) + 1}"
            row_dict = row.to_dict()
            row_dict["criterio_seleccion"] = "Complemento (Sortino)"
            result.loc[pname] = row_dict

    if progress:
        print(f"\n  Portafolios candidatos para AHP:")
        for pname, row in result.iterrows():
            print(f"    {pname} [{row.get('criterio_seleccion', '')}]")
            print(f"       Rentab={row['rentabilidad']:.2%}  Vol={row['volatilidad']:.2%}  "
                  f"Sharpe={row['sharpe']:.2f}  MaxDD={row['max_drawdown']:.2%}")

    return result


def build_portfolios(
    selected_stocks: pd.DataFrame,
    returns_df: pd.DataFrame,
    benchmark_returns: pd.Series,
    rf_annual: float = 0.04,
    progress: bool = True,
) -> pd.DataFrame:
    """
    Pipeline completo del Módulo 5:
    genera todas las combinaciones y selecciona los 5 mejores.
    """
    if progress:
        print("\n" + "=" * 60)
        print("  MÓDULO 5 — CONSTRUCCIÓN DE PORTAFOLIOS")
        print("=" * 60)

    # Determinar tamaños de portafolio según acciones disponibles
    n = len(selected_stocks)
    min_s = 3
    max_s = min(n, 6)

    all_portfolios = generate_portfolios(
        selected_stocks, returns_df, benchmark_returns,
        rf_annual, min_s, max_s, progress,
    )

    best_5 = select_best_portfolios(all_portfolios, n_best=5, progress=progress)

    if progress:
        print(f"\n{'─' * 60}")
        print(f"  RESULTADO: {len(best_5)} portafolios listos para AHP")
        print(f"{'─' * 60}")

    return best_5


# ─── DEMO ───
def demo():
    """Demo con datos sintéticos."""
    from stock_analysis import demo_synthetic, compute_returns

    print("\n" + "=" * 60)
    print("  DEMO — Construcción de portafolios")
    print("=" * 60)

    # Generar datos sintéticos
    np.random.seed(42)
    n_days = 504
    dates = pd.bdate_range("2023-01-02", periods=n_days)

    tickers = ["AAPL", "MSFT", "GOOGL", "JNJ", "PG"]
    drifts = [0.12, 0.15, 0.10, 0.06, 0.05]
    vols_sim = [0.25, 0.28, 0.30, 0.15, 0.12]

    prices_data = {}
    for t, mu, sigma in zip(tickers, drifts, vols_sim):
        daily_r = np.random.normal(mu / 252, sigma / np.sqrt(252), n_days)
        prices_data[t] = 100 * np.exp(np.cumsum(daily_r))

    prices = pd.DataFrame(prices_data, index=dates)
    returns = compute_returns(prices)

    bench_r = np.random.normal(0.10 / 252, 0.18 / np.sqrt(252), n_days)
    benchmark = pd.Series(np.random.normal(0, 0.01, n_days), index=dates, name="bench")
    benchmark.iloc[:len(bench_r)] = bench_r

    # Análisis (simplificado)
    analysis = demo_synthetic()

    # Construir portafolios
    best = build_portfolios(
        selected_stocks=analysis,
        returns_df=returns,
        benchmark_returns=benchmark,
        rf_annual=0.04,
    )

    return best


if __name__ == "__main__":
    demo()
