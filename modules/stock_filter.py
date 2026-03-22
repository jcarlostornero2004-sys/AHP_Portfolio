"""
Módulo 4 v2 — Filtrado y selección de acciones por perfil
============================================================
Cada perfil filtra y ORDENA las acciones de forma diferente:

  Conservador:  ordena por mín. volatilidad + mín. drawdown
  Moderado:     ordena por máx. Sharpe (rentabilidad ajustada)
  Agresivo:     ordena por máx. rentabilidad + máx. alpha
  Muy agresivo: ordena por máx. alpha + máx. rentab-kp
  Dividendos:   ordena por máx. Sortino + filtra div yield
  Tecnológico:  filtra sector tech + ordena por máx. alpha
  ESG:          filtra ESG + ordena por máx. Sharpe

Esto garantiza que cada perfil selecciona acciones DISTINTAS.
"""

import pandas as pd
import numpy as np
from typing import Optional
from profiles import UniverseFilters


# ─────────────────────────────────────────────────────────────────
# CRITERIOS DE RANKING POR PERFIL
# ─────────────────────────────────────────────────────────────────

PROFILE_RANKING_CRITERIA = {
    "conservador": {
        "primary": ("volatilidad", True),       # menor volatilidad
        "secondary": ("max_drawdown", True),     # menor drawdown
        "tertiary": ("sortino", False),          # mayor Sortino
    },
    "moderado": {
        "primary": ("sharpe", False),            # mayor Sharpe
        "secondary": ("sortino", False),         # mayor Sortino
        "tertiary": ("cv", True),                # menor CV
    },
    "agresivo": {
        "primary": ("rentabilidad", False),      # mayor rentabilidad
        "secondary": ("alpha", False),           # mayor alpha
        "tertiary": ("sharpe", False),           # mayor Sharpe
    },
    "muy_agresivo": {
        "primary": ("alpha", False),             # mayor alpha
        "secondary": ("rentab_kp", False),       # mayor rentab-kp
        "tertiary": ("rentabilidad", False),     # mayor rentabilidad
    },
    "dividendos": {
        "primary": ("sortino", False),           # mayor Sortino
        "secondary": ("sharpe", False),          # mayor Sharpe
        "tertiary": ("volatilidad", True),       # menor volatilidad
    },
    "tecnologico": {
        "primary": ("alpha", False),             # mayor alpha
        "secondary": ("rentabilidad", False),    # mayor rentabilidad
        "tertiary": ("sharpe", False),           # mayor Sharpe
    },
    "esg": {
        "primary": ("sharpe", False),            # mayor Sharpe
        "secondary": ("volatilidad", True),      # menor volatilidad
        "tertiary": ("sortino", False),          # mayor Sortino
    },
}

# Criterios adicionales de EXCLUSIÓN por perfil
PROFILE_EXCLUSIONS = {
    "conservador": {
        "max_volatilidad": 0.30,       # excluir vol > 30%
        "max_drawdown": 0.35,          # excluir drawdown > 35%
        "max_beta": 1.3,               # excluir beta > 1.3
    },
    "moderado": {
        "max_volatilidad": 0.45,
        "max_drawdown": 0.50,
    },
    "agresivo": {
        "min_rentabilidad": 0.0,       # al menos rentabilidad positiva
    },
    "muy_agresivo": {
        "min_rentabilidad": -0.05,     # tolera ligeras pérdidas
    },
    "dividendos": {
        "max_volatilidad": 0.35,
        "max_drawdown": 0.40,
    },
    "tecnologico": {},
    "esg": {
        "max_volatilidad": 0.40,
    },
}


# ─────────────────────────────────────────────────────────────────
# FILTROS SECUENCIALES
# ─────────────────────────────────────────────────────────────────

def filter_negative_returns(df, progress=True):
    """Paso 1: Descartar acciones con rentabilidad negativa."""
    before = len(df)
    filtered = df[df["rentabilidad"] > 0].copy()
    if progress:
        print(f"  [Filtro 1] Rentabilidad positiva: {before} → {len(filtered)}")
    return filtered


def filter_beta_ratio(df, rf_annual, market_variance, progress=True):
    """Paso 2: Razón beta de Elton y Gruber (1978)."""
    before = len(df)
    df = df.copy()

    df["razon_beta"] = np.where(
        df["beta"].abs() > 0.01,
        (df["rentabilidad"] - rf_annual) / df["beta"],
        0,
    )
    df = df.sort_values("razon_beta", ascending=False)

    # Calcular C*
    n = len(df)
    if n == 0 or market_variance == 0:
        return df

    num_sum, den_sum, c_star = 0, 0, 0
    for _, row in df.iterrows():
        bi = row["beta"]
        if abs(bi) < 0.01:
            continue
        vol_sq = row["volatilidad"] ** 2 + 1e-10
        num_sum += bi * (row["rentabilidad"] - rf_annual) / vol_sq
        den_sum += bi ** 2 / vol_sq
        c_star = market_variance * num_sum / (1 + market_variance * den_sum)

    filtered = df[df["razon_beta"] > c_star].copy()
    if len(filtered) < 8:
        filtered = df.head(max(8, len(df) // 3)).copy()

    if progress:
        print(f"  [Filtro 2] Razón beta (Elton-Gruber): {before} → {len(filtered)} (C*={c_star:.4f})")
    return filtered


def filter_by_profile(df, profile_name, filters, stock_info=None, progress=True):
    """Paso 3: Filtros específicos del perfil + exclusiones."""
    before = len(df)

    # Unir info fundamental si disponible
    if stock_info is not None and len(stock_info) > 0:
        common = df.index.intersection(stock_info.index)
        if len(common) > 0:
            info_cols = [c for c in ["sector", "market_cap", "dividend_yield"] if c in stock_info.columns]
            if info_cols:
                df = df.join(stock_info[info_cols], how="left")

        # Filtros del UniverseFilters
        if "market_cap" in df.columns and filters.min_market_cap_bn > 0:
            min_cap = filters.min_market_cap_bn * 1e9
            df = df[(df["market_cap"] >= min_cap) | (df["market_cap"].isna())]

        if filters.sectors_gics and "sector" in df.columns:
            df = df[df["sector"].isin(filters.sectors_gics) | df["sector"].isna()]

        if filters.min_dividend_yield and "dividend_yield" in df.columns:
            min_dy = filters.min_dividend_yield / 100
            df = df[(df["dividend_yield"] >= min_dy) | (df["dividend_yield"].isna())]

    # Exclusiones por perfil
    exclusions = PROFILE_EXCLUSIONS.get(profile_name, {})
    if "max_volatilidad" in exclusions:
        df = df[df["volatilidad"] <= exclusions["max_volatilidad"]]
    if "max_drawdown" in exclusions and "max_drawdown" in df.columns:
        df = df[df["max_drawdown"] <= exclusions["max_drawdown"]]
    if "max_beta" in exclusions:
        df = df[df["beta"] <= exclusions["max_beta"]]
    if "min_rentabilidad" in exclusions:
        df = df[df["rentabilidad"] >= exclusions["min_rentabilidad"]]

    if progress:
        print(f"  [Filtro 3] Filtros de perfil ({profile_name}): {before} → {len(df)}")
        excl_applied = [k for k in exclusions if k.startswith(("max_", "min_"))]
        if excl_applied:
            print(f"             Exclusiones: {', '.join(excl_applied)}")

    return df


def select_final_stocks_by_profile(df, profile_name, n_stocks=8, progress=True):
    """
    Paso 4: Selección final DIFERENCIADA por perfil.
    Cada perfil ordena por criterios distintos.
    """
    before = len(df)

    criteria = PROFILE_RANKING_CRITERIA.get(profile_name, {
        "primary": ("sharpe", False),
        "secondary": ("sortino", False),
        "tertiary": ("rentabilidad", False),
    })

    # Crear score compuesto: 50% primario + 30% secundario + 20% terciario
    df = df.copy()

    for key, (col, ascending) in criteria.items():
        if col in df.columns:
            vals = df[col].copy()
            # Normalizar al rango [0, 1]
            vmin, vmax = vals.min(), vals.max()
            if vmax - vmin > 1e-10:
                normalized = (vals - vmin) / (vmax - vmin)
            else:
                normalized = pd.Series(0.5, index=vals.index)

            if ascending:  # menor es mejor → invertir
                normalized = 1 - normalized

            if key == "primary":
                df["_score"] = normalized * 0.50
            elif key == "secondary":
                df["_score"] += normalized * 0.30
            elif key == "tertiary":
                df["_score"] += normalized * 0.20

    df = df.sort_values("_score", ascending=False)
    selected = df.head(n_stocks).copy()

    if "_score" in selected.columns:
        selected = selected.drop(columns=["_score"])
    if "_score" in df.columns:
        df = df.drop(columns=["_score"])

    if progress:
        primary_col = criteria["primary"][0]
        primary_asc = "MIN" if criteria["primary"][1] else "MAX"
        print(f"  [Selección] Top {n_stocks} por perfil {profile_name} "
              f"(principal: {primary_asc} {primary_col}): {before} → {len(selected)}")
        for ticker, row in selected.iterrows():
            rentab = row.get("rentabilidad", 0)
            sharpe = row.get("sharpe", 0)
            vol = row.get("volatilidad", 0)
            alpha = row.get("alpha", 0)
            print(f"      {ticker:10s}  Rentab={rentab:.2%}  Sharpe={sharpe:.2f}  "
                  f"Vol={vol:.2%}  Alpha={alpha:.2%}")

    return selected


# ─────────────────────────────────────────────────────────────────
# PIPELINE COMPLETO
# ─────────────────────────────────────────────────────────────────

def run_filtering(
    analysis, filters, rf_annual=0.04, market_variance=0.03,
    stock_info=None, profile_name="moderado", progress=True,
):
    """
    Pipeline de filtrado completo, ahora con perfil.

    Args:
        analysis: DataFrame del Módulo 3
        filters: UniverseFilters del perfil
        rf_annual: tasa libre de riesgo
        market_variance: varianza del mercado
        stock_info: info fundamental (opcional)
        profile_name: nombre del perfil (NUEVO)
    """
    if progress:
        print(f"\n{'=' * 60}")
        print(f"  MÓDULO 4 — FILTRADO (perfil: {profile_name.upper()})")
        print(f"  Universo inicial: {len(analysis)} acciones")
        print(f"{'=' * 60}")

    df = analysis.copy()
    df = filter_negative_returns(df, progress)
    df = filter_beta_ratio(df, rf_annual, market_variance, progress)
    df = filter_by_profile(df, profile_name, filters, stock_info, progress)
    df = select_final_stocks_by_profile(df, profile_name, filters.final_n_stocks, progress)

    if progress:
        print(f"\n{'─' * 60}")
        print(f"  RESULTADO: {len(df)} acciones seleccionadas para portafolios")
        print(f"{'─' * 60}")

    return df


# ─── DEMO ───
def demo():
    from stock_analysis import demo_synthetic
    from profiles import get_profile_config

    analysis = demo_synthetic()

    for profile_name in ["conservador", "agresivo"]:
        config = get_profile_config(profile_name)
        selected = run_filtering(
            analysis=analysis,
            filters=config["filters"],
            rf_annual=0.04,
            market_variance=0.03,
            profile_name=profile_name,
        )


if __name__ == "__main__":
    demo()
