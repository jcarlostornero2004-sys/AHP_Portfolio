"""
Módulo 6 v2 — Motor AHP Completo (15 criterios)
==================================================
Versión ampliada con 15 criterios en 5 categorías.

Proceso AHP (Saaty 1990):
  1. Construir jerarquía (objetivo → 15 criterios → 5 portafolios)
  2. Matrices de comparación pareada por criterio (automáticas)
  3. Matriz de comparación de criterios (basada en perfil)
  4. Vectores de prioridad + verificación de consistencia
  5. Síntesis global → ranking final

Autor: [Tu nombre] — TFG
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from profiles import CRITERIA, CRITERIA_ORDER, PROFILE_WEIGHTS


# ─────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────

RANDOM_CONSISTENCY_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
}


# ─────────────────────────────────────────────────────────────────
# FUNCIONES MATEMÁTICAS AHP
# ─────────────────────────────────────────────────────────────────

def priority_vector_eigenvector(matrix: np.ndarray) -> np.ndarray:
    """Vector de prioridad mediante autovector principal (método exacto)."""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_idx = np.argmax(eigenvalues.real)
    principal = eigenvectors[:, max_idx].real
    principal = np.abs(principal)
    total = principal.sum()
    if total == 0:
        return np.ones(len(principal)) / len(principal)
    return principal / total


def consistency_ratio(matrix: np.ndarray) -> Tuple[float, float, float, bool]:
    """Calcula λmax, CI, CR y si es consistente (CR < 0.10)."""
    n = matrix.shape[0]
    if n <= 2:
        return float(n), 0.0, 0.0, True

    w = priority_vector_eigenvector(matrix)
    w_safe = np.where(w > 1e-10, w, 1e-10)
    Aw = matrix @ w
    lambda_max = np.mean(Aw / w_safe)

    ci = (lambda_max - n) / (n - 1)
    ri = RANDOM_CONSISTENCY_INDEX.get(n, 1.59)
    cr = ci / ri if ri > 0 else 0.0

    return float(lambda_max), float(ci), float(np.abs(cr)), np.abs(cr) < 0.10


def build_pairwise_matrix(values: np.ndarray, direction: str = "maximize") -> np.ndarray:
    """
    Construye matriz de comparación pareada automáticamente.
    Método de Escobar (2015): interpolación proporcional en escala Saaty 1-9.
    """
    n = len(values)
    matrix = np.ones((n, n))

    if direction == "minimize":
        scores = 1.0 / (values + 1e-10)
    else:
        scores = values.copy()

    s_min, s_max = scores.min(), scores.max()
    if s_max - s_min < 1e-10:
        return matrix

    normalized = (scores - s_min) / (s_max - s_min)

    for i in range(n):
        for j in range(i + 1, n):
            diff = abs(normalized[i] - normalized[j])
            intensity = 1 + diff * 8  # mapear [0,1] → [1,9]
            intensity = max(1, min(9, round(intensity)))

            if normalized[i] >= normalized[j]:
                matrix[i, j] = intensity
                matrix[j, i] = 1.0 / intensity
            else:
                matrix[j, i] = intensity
                matrix[i, j] = 1.0 / intensity

    return matrix


def build_criteria_matrix(profile: str) -> np.ndarray:
    """Construye la matriz de comparación de criterios basada en el perfil."""
    weights = PROFILE_WEIGHTS[profile]
    criteria = CRITERIA_ORDER
    n = len(criteria)
    matrix = np.ones((n, n))

    w_values = np.array([weights[c] for c in criteria], dtype=float)

    for i in range(n):
        for j in range(i + 1, n):
            ratio = w_values[i] / w_values[j] if w_values[j] > 0 else 1

            if ratio >= 1:
                intensity = max(1, min(9, round(ratio)))
                matrix[i, j] = intensity
                matrix[j, i] = 1.0 / intensity
            else:
                intensity = max(1, min(9, round(1.0 / ratio)))
                matrix[j, i] = intensity
                matrix[i, j] = 1.0 / intensity

    return matrix


# ─────────────────────────────────────────────────────────────────
# CLASE PRINCIPAL: MOTOR AHP v2
# ─────────────────────────────────────────────────────────────────

class AHPEngine:
    """
    Motor AHP completo con 15 criterios y 5 categorías.

    Uso:
        engine = AHPEngine(profile="moderado")
        ranking = engine.run(portfolios_df)
        report = engine.get_full_report()
    """

    def __init__(self, profile: str = "moderado"):
        if profile not in PROFILE_WEIGHTS:
            raise ValueError(f"Perfil '{profile}' no válido. Opciones: {list(PROFILE_WEIGHTS.keys())}")

        self.profile = profile
        self.criteria = CRITERIA_ORDER
        self.n_criteria = len(self.criteria)

        # Resultados
        self.criteria_matrix: Optional[np.ndarray] = None
        self.criteria_weights: Optional[np.ndarray] = None
        self.criteria_cr: Optional[float] = None
        self.alt_matrices: Dict[str, np.ndarray] = {}
        self.alt_weights: Dict[str, np.ndarray] = {}
        self.alt_crs: Dict[str, float] = {}
        self.global_scores: Optional[np.ndarray] = None
        self.ranking: Optional[pd.DataFrame] = None
        self.portfolio_names: Optional[List[str]] = None

    def run(self, portfolios: pd.DataFrame, progress: bool = True) -> pd.DataFrame:
        """
        Ejecuta el proceso AHP completo.

        Args:
            portfolios: DataFrame con portafolios candidatos (P1-P5).
                        Debe tener columna 'nombre' y las 15 columnas de criterios.
        """
        if progress:
            print("\n" + "=" * 60)
            print(f"  MÓDULO 6 — MOTOR AHP (15 criterios)")
            print(f"  Perfil: {self.profile.upper()}")
            print("=" * 60)

        # Validar columnas
        if "nombre" not in portfolios.columns and portfolios.index.name != "nombre":
            if portfolios.index.dtype == object:
                self.portfolio_names = list(portfolios.index)
            else:
                self.portfolio_names = [f"P{i+1}" for i in range(len(portfolios))]
        else:
            self.portfolio_names = list(portfolios["nombre"]) if "nombre" in portfolios.columns else list(portfolios.index)

        n_port = len(self.portfolio_names)

        # Determinar qué criterios están disponibles en los datos
        available_criteria = [c for c in self.criteria if c in portfolios.columns]
        if progress:
            print(f"\n  Criterios disponibles: {len(available_criteria)}/{self.n_criteria}")

        # ═══ PASO 1: Matriz de criterios (basada en perfil) ═══
        criteria_weights_raw = PROFILE_WEIGHTS[self.profile]
        # Solo usar criterios disponibles
        active_criteria = available_criteria
        n_active = len(active_criteria)

        # Construir matriz de criterios solo con los activos
        crit_matrix = np.ones((n_active, n_active))
        w_vals = np.array([criteria_weights_raw[c] for c in active_criteria], dtype=float)

        for i in range(n_active):
            for j in range(i + 1, n_active):
                ratio = w_vals[i] / w_vals[j] if w_vals[j] > 0 else 1
                if ratio >= 1:
                    intensity = max(1, min(9, round(ratio)))
                    crit_matrix[i, j] = intensity
                    crit_matrix[j, i] = 1.0 / intensity
                else:
                    intensity = max(1, min(9, round(1.0 / ratio)))
                    crit_matrix[j, i] = intensity
                    crit_matrix[i, j] = 1.0 / intensity

        self.criteria_matrix = crit_matrix
        self.criteria_weights = priority_vector_eigenvector(crit_matrix)
        _, _, cr, ok = consistency_ratio(crit_matrix)
        self.criteria_cr = cr

        if progress:
            print(f"\n  Pesos de criterios (perfil {self.profile}):")
            sorted_idx = np.argsort(-self.criteria_weights)
            for idx in sorted_idx[:5]:
                c = active_criteria[idx]
                w = self.criteria_weights[idx]
                label = CRITERIA[c]["label"]
                bar = "█" * int(w * 50) + "░" * (10 - int(w * 50))
                print(f"    {bar} {w:.1%}  {label}")
            print(f"    ...")
            print(f"  CR criterios = {cr:.4f} {'✓' if ok else '✗ (> 0.10)'}")

        # ═══ PASO 2: Matrices de alternativas por criterio ═══
        W_alt = np.zeros((n_port, n_active))

        for j, criterion in enumerate(active_criteria):
            values = portfolios[criterion].values.astype(float)
            direction = CRITERIA[criterion]["dir"]

            pairwise = build_pairwise_matrix(values, direction)
            weights = priority_vector_eigenvector(pairwise)
            _, _, cr_alt, _ = consistency_ratio(pairwise)

            self.alt_matrices[criterion] = pairwise
            self.alt_weights[criterion] = weights
            self.alt_crs[criterion] = cr_alt
            W_alt[:, j] = weights

        # ═══ PASO 3: Síntesis global ═══
        self.global_scores = W_alt @ self.criteria_weights

        # ═══ PASO 4: Ranking ═══
        self.ranking = pd.DataFrame({
            "portafolio": self.portfolio_names,
            "score_ahp": self.global_scores,
            "score_pct": self.global_scores * 100,
        })
        self.ranking = self.ranking.sort_values("score_ahp", ascending=False).reset_index(drop=True)
        self.ranking["ranking"] = range(1, len(self.ranking) + 1)

        if progress:
            print(f"\n  {'─' * 50}")
            print(f"  RANKING FINAL:")
            for _, row in self.ranking.iterrows():
                bar_len = int(row["score_pct"] * 2)
                bar = "█" * bar_len
                marker = " ← MEJOR" if row["ranking"] == 1 else ""
                print(f"    #{int(row['ranking'])}  {row['portafolio']:4s}  {bar} {row['score_pct']:.1f}%{marker}")
            print(f"  {'─' * 50}")

        return self.ranking

    def get_criteria_report(self) -> pd.DataFrame:
        """Resumen de pesos de criterios."""
        active = [c for c in self.criteria if c in self.alt_weights]
        return pd.DataFrame({
            "criterio": active,
            "categoria": [CRITERIA[c]["cat"] for c in active],
            "label": [CRITERIA[c]["label"] for c in active],
            "peso_perfil": [PROFILE_WEIGHTS[self.profile][c] for c in active],
            "peso_ahp": self.criteria_weights,
            "peso_ahp_pct": self.criteria_weights * 100,
        })

    def get_consistency_report(self) -> pd.DataFrame:
        """Resumen de ratios de consistencia."""
        rows = [{"elemento": "Criterios", "CR": self.criteria_cr, "consistente": self.criteria_cr < 0.10}]
        for c, cr in self.alt_crs.items():
            rows.append({"elemento": f"Alt. ({CRITERIA[c]['label'][:30]})", "CR": cr, "consistente": cr < 0.10})
        return pd.DataFrame(rows)

    def get_full_report(self) -> Dict:
        """Devuelve todos los resultados para exportación."""
        return {
            "perfil": self.profile,
            "ranking": self.ranking,
            "criteria_weights": self.criteria_weights,
            "criteria_matrix": self.criteria_matrix,
            "criteria_cr": self.criteria_cr,
            "alt_matrices": self.alt_matrices,
            "alt_weights": self.alt_weights,
            "alt_crs": self.alt_crs,
            "global_scores": self.global_scores,
        }


# ─── DEMO ───
def demo():
    """Demo con datos ficticios (5 portafolios, 15 criterios)."""
    print("\n" + "█" * 60)
    print("  DEMO — Motor AHP v2 (15 criterios)")
    print("█" * 60)

    np.random.seed(42)

    portfolios = pd.DataFrame({
        "nombre":       ["P1", "P2", "P3", "P4", "P5"],
        "rentabilidad": [0.086, 0.085, 0.056, 0.161, 0.104],
        "sharpe":       [0.48, 0.47, 0.15, 0.72, 0.55],
        "sortino":      [0.71, 0.70, 0.22, 1.05, 0.82],
        "alpha":        [0.02, 0.019, -0.01, 0.08, 0.04],
        "volatilidad":  [0.18, 0.18, 0.29, 0.22, 0.19],
        "var_95":       [0.049, 0.049, 0.078, 0.061, 0.054],
        "cvar_95":      [0.065, 0.064, 0.102, 0.081, 0.071],
        "max_drawdown": [0.15, 0.14, 0.31, 0.25, 0.18],
        "beta":         [0.85, 0.84, 1.10, 1.05, 0.90],
        "tracking_error": [0.08, 0.08, 0.14, 0.12, 0.09],
        "rentab_kp":    [0.025, 0.024, -0.015, 0.065, 0.035],
        "cv":           [2.09, 2.12, 5.18, 1.37, 1.83],
        "skewness":     [0.12, 0.10, -0.25, -0.15, 0.08],
        "corr_media":   [0.35, 0.36, 0.55, 0.42, 0.30],
        "div_geo":      [0.72, 0.70, 0.45, 0.55, 0.78],
    })

    print("\n📊 Portafolios candidatos (15 criterios):")
    display_cols = ["nombre", "rentabilidad", "sharpe", "volatilidad", "var_95", "max_drawdown", "alpha", "beta"]
    print(portfolios[display_cols].to_string(index=False))

    for profile in ["conservador", "moderado", "agresivo", "muy_agresivo"]:
        engine = AHPEngine(profile=profile)
        ranking = engine.run(portfolios, progress=True)


if __name__ == "__main__":
    demo()
