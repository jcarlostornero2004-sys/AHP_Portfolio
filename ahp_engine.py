"""
Módulo 6 — Motor AHP (Analytic Hierarchy Process)
==================================================
Implementación del proceso analítico jerárquico de Saaty (1990, 2003)
para la selección del mejor portafolio de acciones.

Basado en la metodología de Escobar (2015):
"Metodología para la toma de decisiones de inversión en portafolio
de acciones utilizando la técnica multicriterio AHP"

Autor: [Tu nombre] — TFG
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional


# =============================================================================
# CONSTANTES
# =============================================================================

# Escala de Saaty (1-9)
SAATY_SCALE = {
    1: "Igual importancia",
    2: "Intermedio",
    3: "Moderadamente más importante",
    4: "Intermedio",
    5: "Fuertemente más importante",
    6: "Intermedio",
    7: "Mucho más fuerte importancia",
    8: "Intermedio",
    9: "Importancia extrema",
}

# Índice de consistencia aleatorio (RI) según Saaty
# Para matrices de tamaño n = 1..15
RANDOM_CONSISTENCY_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
}

# Criterios AHP para evaluación de portafolios (basados en Escobar 2015)
# "maximize" = mayor es mejor; "minimize" = menor es mejor
CRITERIA_CONFIG = {
    "rentabilidad":  {"direction": "maximize", "label": "Rentabilidad anualizada"},
    "riesgo":        {"direction": "minimize", "label": "Riesgo (desv. estándar)"},
    "cv":            {"direction": "minimize", "label": "Coeficiente de variación"},
    "var":           {"direction": "minimize", "label": "Value at Risk (VaR 95%)"},
    "kp":            {"direction": "minimize", "label": "Coste de capital (CAPM)"},
    "rentab_kp":     {"direction": "maximize", "label": "Rentabilidad − Coste capital"},
}

# Pesos AHP por perfil de inversor (escala Saaty 1-9)
# Estos valores se usan para construir la matriz de comparación de CRITERIOS
PROFILE_WEIGHTS = {
    "conservador": {
        "rentabilidad": 2, "riesgo": 9, "cv": 7,
        "var": 9, "kp": 5, "rentab_kp": 3,
    },
    "moderado": {
        "rentabilidad": 5, "riesgo": 7, "cv": 6,
        "var": 7, "kp": 4, "rentab_kp": 5,
    },
    "agresivo": {
        "rentabilidad": 8, "riesgo": 4, "cv": 5,
        "var": 3, "kp": 5, "rentab_kp": 7,
    },
    "muy_agresivo": {
        "rentabilidad": 9, "riesgo": 2, "cv": 3,
        "var": 1, "kp": 4, "rentab_kp": 9,
    },
    "dividendos": {
        "rentabilidad": 4, "riesgo": 7, "cv": 6,
        "var": 8, "kp": 4, "rentab_kp": 5,
    },
    "tecnologico": {
        "rentabilidad": 8, "riesgo": 4, "cv": 5,
        "var": 3, "kp": 5, "rentab_kp": 7,
    },
    "esg": {
        "rentabilidad": 4, "riesgo": 6, "cv": 5,
        "var": 7, "kp": 4, "rentab_kp": 5,
    },
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def normalize_columns(matrix: np.ndarray) -> np.ndarray:
    """Normaliza cada columna dividiendo por la suma de la columna."""
    col_sums = matrix.sum(axis=0)
    col_sums[col_sums == 0] = 1  # evitar división por cero
    return matrix / col_sums


def priority_vector(matrix: np.ndarray) -> np.ndarray:
    """
    Calcula el vector de prioridad de una matriz de comparación pareada.
    Método: promedio de filas de la matriz normalizada por columnas.
    (Aproximación al autovector principal — Saaty 1990)
    """
    normalized = normalize_columns(matrix)
    return normalized.mean(axis=1)


def priority_vector_eigenvector(matrix: np.ndarray) -> np.ndarray:
    """
    Calcula el vector de prioridad usando el autovector principal exacto.
    Más preciso que el método de promedios para matrices grandes.
    """
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_idx = np.argmax(eigenvalues.real)
    principal = eigenvectors[:, max_idx].real
    return principal / principal.sum()


def consistency_ratio(matrix: np.ndarray) -> Tuple[float, float, float, bool]:
    """
    Calcula el ratio de consistencia (CR) de una matriz de comparación pareada.

    Returns:
        lambda_max: autovalor principal
        ci: índice de consistencia
        cr: ratio de consistencia
        is_consistent: True si CR < 0.10 (umbral de Saaty)
    """
    n = matrix.shape[0]

    if n <= 2:
        return float(n), 0.0, 0.0, True

    w = priority_vector_eigenvector(matrix)
    Aw = matrix @ w
    lambda_max = np.mean(Aw / w)

    ci = (lambda_max - n) / (n - 1)
    ri = RANDOM_CONSISTENCY_INDEX.get(n, 1.59)
    cr = ci / ri if ri > 0 else 0.0

    return float(lambda_max), float(ci), float(cr), cr < 0.10


# =============================================================================
# CONSTRUCCIÓN AUTOMÁTICA DE MATRICES PAREADAS
# =============================================================================

def build_pairwise_matrix_from_values(
    values: np.ndarray,
    direction: str = "maximize",
    scale_max: int = 9,
) -> np.ndarray:
    """
    Construye automáticamente la matriz de comparación pareada de Saaty
    a partir de los valores numéricos de cada alternativa para un criterio.

    Método basado en Escobar (2015):
    - Se identifican la mejor y peor alternativa para el criterio.
    - Se asigna 9 (o scale_max) a la comparación mejor vs peor.
    - Las demás comparaciones se interpolan proporcionalmente.

    Args:
        values: array con el valor del criterio para cada alternativa
        direction: "maximize" si mayor es mejor, "minimize" si menor es mejor
        scale_max: valor máximo de la escala de Saaty (por defecto 9)

    Returns:
        Matriz cuadrada de comparación pareada (n x n)
    """
    n = len(values)
    matrix = np.ones((n, n))

    if direction == "minimize":
        # Para criterios a minimizar, invertimos: menor valor = mejor
        scores = 1.0 / (values + 1e-10)  # evitar div/0
    else:
        scores = values.copy()

    # Normalizar scores al rango [0, 1]
    s_min, s_max = scores.min(), scores.max()
    if s_max - s_min < 1e-10:
        # Todos los valores son iguales → importancia igual
        return matrix

    normalized = (scores - s_min) / (s_max - s_min)

    for i in range(n):
        for j in range(i + 1, n):
            diff = abs(normalized[i] - normalized[j])
            # Mapear diferencia [0,1] → escala Saaty [1, scale_max]
            intensity = 1 + diff * (scale_max - 1)
            intensity = max(1, min(scale_max, round(intensity)))

            if normalized[i] >= normalized[j]:
                matrix[i, j] = intensity
                matrix[j, i] = 1.0 / intensity
            else:
                matrix[j, i] = intensity
                matrix[i, j] = 1.0 / intensity

    return matrix


def build_criteria_matrix(profile: str) -> np.ndarray:
    """
    Construye la matriz de comparación pareada de CRITERIOS
    basada en los pesos del perfil del inversor.

    Los pesos del perfil (escala 1-9) representan la importancia
    relativa de cada criterio. La matriz se construye comparando
    los pesos entre sí.
    """
    weights = PROFILE_WEIGHTS[profile]
    criteria = list(CRITERIA_CONFIG.keys())
    n = len(criteria)
    matrix = np.ones((n, n))

    w_values = np.array([weights[c] for c in criteria], dtype=float)

    for i in range(n):
        for j in range(i + 1, n):
            if w_values[i] >= w_values[j]:
                ratio = w_values[i] / w_values[j]
            else:
                ratio = w_values[j] / w_values[i]

            # Redondear al entero más cercano en escala Saaty
            intensity = max(1, min(9, round(ratio)))

            if w_values[i] >= w_values[j]:
                matrix[i, j] = intensity
                matrix[j, i] = 1.0 / intensity
            else:
                matrix[j, i] = intensity
                matrix[i, j] = 1.0 / intensity

    return matrix


# =============================================================================
# CLASE PRINCIPAL: MOTOR AHP
# =============================================================================

class AHPEngine:
    """
    Motor AHP para selección de portafolios.

    Implementa las 4 etapas del proceso AHP de Saaty:
    1. Definir la jerarquía (objetivo → criterios → alternativas)
    2. Construir matrices de comparación pareada
    3. Calcular vectores de prioridad y verificar consistencia
    4. Sintetizar prioridades globales para obtener el ranking final

    Uso:
        engine = AHPEngine(profile="moderado")
        result = engine.run(portfolios_df)
    """

    def __init__(self, profile: str = "moderado"):
        if profile not in PROFILE_WEIGHTS:
            raise ValueError(
                f"Perfil '{profile}' no reconocido. "
                f"Opciones: {list(PROFILE_WEIGHTS.keys())}"
            )
        self.profile = profile
        self.criteria = list(CRITERIA_CONFIG.keys())
        self.n_criteria = len(self.criteria)

        # Resultados (se llenan al ejecutar .run())
        self.criteria_matrix: Optional[np.ndarray] = None
        self.criteria_weights: Optional[np.ndarray] = None
        self.criteria_cr: Optional[float] = None
        self.alternative_matrices: Dict[str, np.ndarray] = {}
        self.alternative_weights: Dict[str, np.ndarray] = {}
        self.alternative_crs: Dict[str, float] = {}
        self.global_scores: Optional[np.ndarray] = None
        self.ranking: Optional[pd.DataFrame] = None
        self.portfolio_names: Optional[List[str]] = None

    def run(self, portfolios: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el proceso AHP completo.

        Args:
            portfolios: DataFrame donde cada fila es un portafolio candidato.
                        Debe contener las columnas: 'nombre', 'rentabilidad',
                        'riesgo', 'cv', 'var', 'kp', 'rentab_kp'

        Returns:
            DataFrame con el ranking final (portafolio, score, ranking)
        """
        self._validate_input(portfolios)
        self.portfolio_names = portfolios["nombre"].tolist()
        n_portfolios = len(self.portfolio_names)

        # === PASO 1: Matriz de comparación de criterios ===
        self.criteria_matrix = build_criteria_matrix(self.profile)
        self.criteria_weights = priority_vector_eigenvector(self.criteria_matrix)
        lmax, ci, cr, ok = consistency_ratio(self.criteria_matrix)
        self.criteria_cr = cr

        if not ok:
            print(f"⚠️  Ratio de consistencia de criterios = {cr:.4f} (> 0.10)")
            print("   La matriz de criterios no es perfectamente consistente.")
            print("   Considera ajustar los pesos del perfil.")

        # === PASO 2: Matrices de comparación por criterio ===
        for criterion in self.criteria:
            values = portfolios[criterion].values.astype(float)
            direction = CRITERIA_CONFIG[criterion]["direction"]

            pairwise = build_pairwise_matrix_from_values(values, direction)
            weights = priority_vector_eigenvector(pairwise)
            _, _, cr_alt, ok_alt = consistency_ratio(pairwise)

            self.alternative_matrices[criterion] = pairwise
            self.alternative_weights[criterion] = weights
            self.alternative_crs[criterion] = cr_alt

            if not ok_alt:
                print(
                    f"⚠️  Criterio '{criterion}': CR = {cr_alt:.4f} (> 0.10)"
                )

        # === PASO 3: Síntesis global ===
        # Construir la matriz de pesos de alternativas (n_portfolios x n_criteria)
        W_alternatives = np.column_stack(
            [self.alternative_weights[c] for c in self.criteria]
        )

        # Vector global = W_alternatives × criteria_weights
        self.global_scores = W_alternatives @ self.criteria_weights

        # === PASO 4: Ranking final ===
        self.ranking = pd.DataFrame({
            "portafolio": self.portfolio_names,
            "score_ahp": self.global_scores,
            "score_pct": self.global_scores * 100,
        })
        self.ranking = self.ranking.sort_values(
            "score_ahp", ascending=False
        ).reset_index(drop=True)
        self.ranking["ranking"] = range(1, len(self.ranking) + 1)

        return self.ranking

    def _validate_input(self, portfolios: pd.DataFrame):
        """Valida que el DataFrame tenga las columnas necesarias."""
        required = ["nombre"] + self.criteria
        missing = [c for c in required if c not in portfolios.columns]
        if missing:
            raise ValueError(
                f"Faltan columnas en el DataFrame: {missing}\n"
                f"Columnas requeridas: {required}\n"
                f"Columnas encontradas: {list(portfolios.columns)}"
            )

    def get_criteria_report(self) -> pd.DataFrame:
        """Devuelve un resumen de los pesos de los criterios."""
        return pd.DataFrame({
            "criterio": self.criteria,
            "label": [CRITERIA_CONFIG[c]["label"] for c in self.criteria],
            "peso_perfil": [
                PROFILE_WEIGHTS[self.profile][c] for c in self.criteria
            ],
            "peso_ahp": self.criteria_weights,
            "peso_ahp_pct": self.criteria_weights * 100,
        })

    def get_consistency_report(self) -> pd.DataFrame:
        """Devuelve un resumen de los ratios de consistencia."""
        rows = [{"elemento": "Criterios", "CR": self.criteria_cr,
                 "consistente": self.criteria_cr < 0.10}]
        for c in self.criteria:
            rows.append({
                "elemento": f"Alternativas ({c})",
                "CR": self.alternative_crs[c],
                "consistente": self.alternative_crs[c] < 0.10,
            })
        return pd.DataFrame(rows)

    def get_full_report(self) -> Dict:
        """Devuelve un diccionario con todos los resultados para exportar."""
        return {
            "perfil": self.profile,
            "criterios": {
                "matrix": self.criteria_matrix,
                "weights": self.criteria_weights,
                "cr": self.criteria_cr,
                "labels": [
                    CRITERIA_CONFIG[c]["label"] for c in self.criteria
                ],
            },
            "alternativas": {
                c: {
                    "matrix": self.alternative_matrices[c],
                    "weights": self.alternative_weights[c],
                    "cr": self.alternative_crs[c],
                }
                for c in self.criteria
            },
            "ranking": self.ranking,
            "global_scores": self.global_scores,
        }


# =============================================================================
# EJEMPLO DE USO Y DEMO
# =============================================================================

def demo():
    """
    Ejecuta una demo con datos ficticios que replican la estructura
    del artículo de Escobar (2015) — 5 portafolios, 6 criterios.
    """
    print("=" * 65)
    print("  DEMO — Motor AHP para selección de portafolios")
    print("  Basado en Escobar (2015) / Saaty (1990)")
    print("=" * 65)

    # Datos ficticios inspirados en la Tabla 7 de Escobar (2015)
    portfolios = pd.DataFrame({
        "nombre":      ["P1", "P2", "P3", "P4", "P5"],
        "rentabilidad": [0.086, 0.085, 0.056, 0.161, 0.104],
        "riesgo":       [0.719, 0.714, 1.140, 1.624, 0.793],
        "cv":           [8.39, 8.39, 20.44, 10.07, 7.60],
        "var":          [0.049, 0.049, 0.078, 0.110, 0.054],
        "kp":           [0.021, 0.021, 0.020, 0.021, 0.022],
        "rentab_kp":    [0.065, 0.064, 0.036, 0.140, 0.082],
    })

    print("\n📊 Portafolios candidatos:")
    print(portfolios.to_string(index=False))

    # Probar con diferentes perfiles
    for profile in ["conservador", "moderado", "agresivo", "muy_agresivo"]:
        print(f"\n{'─' * 65}")
        print(f"  Perfil: {profile.upper()}")
        print(f"{'─' * 65}")

        engine = AHPEngine(profile=profile)
        ranking = engine.run(portfolios)

        print("\n📋 Pesos de criterios:")
        criteria_report = engine.get_criteria_report()
        print(criteria_report[["label", "peso_ahp_pct"]].to_string(index=False))

        print(f"\n   CR criterios = {engine.criteria_cr:.4f}", end="")
        print(" ✅" if engine.criteria_cr < 0.10 else " ❌")

        print("\n🏆 Ranking final:")
        print(ranking[["ranking", "portafolio", "score_pct"]].to_string(index=False))

        print(f"\n   → Mejor portafolio: {ranking.iloc[0]['portafolio']}"
              f" ({ranking.iloc[0]['score_pct']:.1f}%)")

    # Reporte de consistencia del último perfil
    print(f"\n{'─' * 65}")
    print("  Reporte de consistencia (último perfil):")
    print(f"{'─' * 65}")
    print(engine.get_consistency_report().to_string(index=False))


if __name__ == "__main__":
    demo()
