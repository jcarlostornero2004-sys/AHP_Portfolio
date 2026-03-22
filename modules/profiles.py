"""
Módulo 1 — Motor de perfiles
==============================
Traduce el perfil del inversor en:
  1. Pesos AHP para los 15 criterios (escala Saaty 1-9)
  2. Filtros de universo de acciones (sector, dividendos, ESG)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field


# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE LOS 15 CRITERIOS
# ─────────────────────────────────────────────────────────────────

CRITERIA = {
    # Cat 1: Rendimiento
    "rentabilidad":     {"cat": "rendimiento",     "dir": "maximize", "label": "Rentabilidad anualizada"},
    "sharpe":           {"cat": "rendimiento",     "dir": "maximize", "label": "Ratio de Sharpe"},
    "sortino":          {"cat": "rendimiento",     "dir": "maximize", "label": "Ratio de Sortino"},
    "alpha":            {"cat": "rendimiento",     "dir": "maximize", "label": "Alpha de Jensen"},
    # Cat 2: Riesgo
    "volatilidad":      {"cat": "riesgo",          "dir": "minimize", "label": "Volatilidad (desv. est.)"},
    "var_95":           {"cat": "riesgo",          "dir": "minimize", "label": "VaR 95%"},
    "cvar_95":          {"cat": "riesgo",          "dir": "minimize", "label": "CVaR / Expected Shortfall"},
    "max_drawdown":     {"cat": "riesgo",          "dir": "minimize", "label": "Max Drawdown"},
    # Cat 3: Eficiencia de mercado
    "beta":             {"cat": "eficiencia",      "dir": "minimize", "label": "Beta del portafolio"},
    "tracking_error":   {"cat": "eficiencia",      "dir": "minimize", "label": "Tracking error vs benchmark"},
    "rentab_kp":        {"cat": "eficiencia",      "dir": "maximize", "label": "Rentabilidad − Coste capital"},
    # Cat 4: Estabilidad
    "cv":               {"cat": "estabilidad",     "dir": "minimize", "label": "Coeficiente de variación"},
    "skewness":         {"cat": "estabilidad",     "dir": "maximize", "label": "Asimetría (Skewness)"},
    # Cat 5: Diversificación
    "corr_media":       {"cat": "diversificacion", "dir": "minimize", "label": "Correlación media inter-activos"},
    "div_geo":          {"cat": "diversificacion", "dir": "maximize", "label": "Diversificación geográfica"},
}

CRITERIA_ORDER = list(CRITERIA.keys())


# ─────────────────────────────────────────────────────────────────
# PESOS AHP POR PERFIL (escala Saaty 1-9)
# ─────────────────────────────────────────────────────────────────

PROFILE_WEIGHTS = {
    "conservador": {
        "rentabilidad": 2, "sharpe": 7, "sortino": 8, "alpha": 3,
        "volatilidad": 9, "var_95": 9, "cvar_95": 8, "max_drawdown": 9,
        "beta": 8, "tracking_error": 7, "rentab_kp": 3,
        "cv": 7, "skewness": 6,
        "corr_media": 8, "div_geo": 6,
    },
    "moderado": {
        "rentabilidad": 5, "sharpe": 8, "sortino": 7, "alpha": 5,
        "volatilidad": 7, "var_95": 7, "cvar_95": 6, "max_drawdown": 8,
        "beta": 6, "tracking_error": 5, "rentab_kp": 5,
        "cv": 6, "skewness": 5,
        "corr_media": 7, "div_geo": 6,
    },
    "agresivo": {
        "rentabilidad": 8, "sharpe": 6, "sortino": 5, "alpha": 7,
        "volatilidad": 4, "var_95": 3, "cvar_95": 3, "max_drawdown": 5,
        "beta": 3, "tracking_error": 4, "rentab_kp": 7,
        "cv": 4, "skewness": 4,
        "corr_media": 5, "div_geo": 5,
    },
    "muy_agresivo": {
        "rentabilidad": 9, "sharpe": 4, "sortino": 3, "alpha": 8,
        "volatilidad": 2, "var_95": 1, "cvar_95": 1, "max_drawdown": 3,
        "beta": 1, "tracking_error": 2, "rentab_kp": 9,
        "cv": 2, "skewness": 2,
        "corr_media": 3, "div_geo": 4,
    },
    "dividendos": {
        "rentabilidad": 4, "sharpe": 7, "sortino": 8, "alpha": 4,
        "volatilidad": 7, "var_95": 8, "cvar_95": 7, "max_drawdown": 8,
        "beta": 7, "tracking_error": 5, "rentab_kp": 5,
        "cv": 6, "skewness": 5,
        "corr_media": 6, "div_geo": 5,
    },
    "tecnologico": {
        "rentabilidad": 8, "sharpe": 6, "sortino": 5, "alpha": 8,
        "volatilidad": 3, "var_95": 3, "cvar_95": 2, "max_drawdown": 5,
        "beta": 2, "tracking_error": 3, "rentab_kp": 7,
        "cv": 4, "skewness": 3,
        "corr_media": 4, "div_geo": 3,
    },
    "esg": {
        "rentabilidad": 4, "sharpe": 7, "sortino": 7, "alpha": 5,
        "volatilidad": 6, "var_95": 7, "cvar_95": 6, "max_drawdown": 7,
        "beta": 5, "tracking_error": 5, "rentab_kp": 5,
        "cv": 5, "skewness": 5,
        "corr_media": 7, "div_geo": 7,
    },
}


# ─────────────────────────────────────────────────────────────────
# FILTROS DE UNIVERSO POR PERFIL
# ─────────────────────────────────────────────────────────────────

@dataclass
class UniverseFilters:
    """Filtros que se aplican al universo de acciones antes del análisis."""
    min_market_cap_bn: float = 1.0           # Cap. mínima en miles de millones USD
    min_avg_volume: int = 500_000            # Volumen medio diario mínimo
    exclude_negative_returns: bool = True     # Excluir acciones con rentab. negativa
    # Filtros temáticos (None = no filtrar)
    sectors_gics: Optional[List[str]] = None  # Filtrar por sectores GICS
    min_dividend_yield: Optional[float] = None
    min_dividend_years: Optional[int] = None  # Años consecutivos pagando dividendo
    min_esg_percentile: Optional[float] = None  # Percentil mínimo ESG (0-100)
    # Parámetros de selección
    max_stocks_per_index: int = 50           # Máx. acciones a considerar por índice
    final_n_stocks: int = 8                  # N acciones finales para portafolios
    description: str = ""


PROFILE_FILTERS = {
    "conservador": UniverseFilters(
        min_market_cap_bn=10.0,
        min_avg_volume=1_000_000,
        max_stocks_per_index=80,
        final_n_stocks=12,
        description="Large caps líquidas, diversificadas, sin filtro sectorial",
    ),
    "moderado": UniverseFilters(
        min_market_cap_bn=5.0,
        min_avg_volume=750_000,
        max_stocks_per_index=100,
        final_n_stocks=12,
        description="Mid-large caps diversificadas",
    ),
    "agresivo": UniverseFilters(
        min_market_cap_bn=2.0,
        min_avg_volume=500_000,
        max_stocks_per_index=120,
        final_n_stocks=12,
        description="Amplio universo, incluye mid caps",
    ),
    "muy_agresivo": UniverseFilters(
        min_market_cap_bn=1.0,
        min_avg_volume=500_000,
        max_stocks_per_index=150,
        final_n_stocks=15,
        description="Universo máximo, incluye small-mid caps",
    ),
    "dividendos": UniverseFilters(
        min_market_cap_bn=5.0,
        min_avg_volume=750_000,
        min_dividend_yield=2.0,
        min_dividend_years=5,
        max_stocks_per_index=80,
        final_n_stocks=12,
        description="Dividend yield > 2%, historial >= 5 años",
    ),
    "tecnologico": UniverseFilters(
        min_market_cap_bn=2.0,
        min_avg_volume=500_000,
        sectors_gics=["Technology", "Communication Services",
                      "Information Technology", "Semiconductors"],
        max_stocks_per_index=100,
        final_n_stocks=12,
        description="Sectores GICS tecnología y comunicaciones",
    ),
    "esg": UniverseFilters(
        min_market_cap_bn=5.0,
        min_avg_volume=750_000,
        min_esg_percentile=70.0,
        max_stocks_per_index=80,
        final_n_stocks=12,
        description="Rating ESG percentil >= 70",
    ),
}


# ─────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def get_profile_config(profile: str) -> dict:
    """
    Devuelve la configuración completa para un perfil.

    Returns:
        dict con keys: 'profile', 'weights', 'filters', 'criteria'
    """
    if profile not in PROFILE_WEIGHTS:
        raise ValueError(f"Perfil '{profile}' no reconocido. Opciones: {list(PROFILE_WEIGHTS.keys())}")

    return {
        "profile": profile,
        "weights": PROFILE_WEIGHTS[profile],
        "filters": PROFILE_FILTERS[profile],
        "criteria": CRITERIA,
        "criteria_order": CRITERIA_ORDER,
    }


def print_profile_summary(profile: str):
    """Imprime un resumen legible del perfil."""
    cfg = get_profile_config(profile)
    w = cfg["weights"]
    f = cfg["filters"]

    print(f"\n{'=' * 60}")
    print(f"  PERFIL: {profile.upper().replace('_', ' ')}")
    print(f"  {f.description}")
    print(f"{'=' * 60}")

    print(f"\n  Filtros de universo:")
    print(f"    Market cap mínima:   ${f.min_market_cap_bn:.0f}B")
    print(f"    Volumen medio mín.:  {f.min_avg_volume:,.0f}")
    print(f"    Stocks por índice:   {f.max_stocks_per_index}")
    print(f"    N final de acciones: {f.final_n_stocks}")
    if f.sectors_gics:
        print(f"    Sectores GICS:       {', '.join(f.sectors_gics)}")
    if f.min_dividend_yield:
        print(f"    Dividend yield mín.: {f.min_dividend_yield}%")
    if f.min_dividend_years:
        print(f"    Años dividendo mín.: {f.min_dividend_years}")
    if f.min_esg_percentile:
        print(f"    ESG percentil mín.:  {f.min_esg_percentile}%")

    print(f"\n  Pesos AHP (top 5 criterios):")
    sorted_w = sorted(w.items(), key=lambda x: -x[1])
    for c, peso in sorted_w[:5]:
        label = CRITERIA[c]["label"]
        bar = "█" * peso + "░" * (9 - peso)
        print(f"    {bar} {peso}  {label}")

    print(f"\n  Pesos AHP (bottom 3 criterios):")
    for c, peso in sorted_w[-3:]:
        label = CRITERIA[c]["label"]
        bar = "█" * peso + "░" * (9 - peso)
        print(f"    {bar} {peso}  {label}")


if __name__ == "__main__":
    for p in PROFILE_WEIGHTS:
        print_profile_summary(p)
