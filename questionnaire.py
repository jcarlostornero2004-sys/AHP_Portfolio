"""
Módulo 0 — Cuestionario de perfil del inversor
================================================
12 preguntas que cubren:
  - Horizonte temporal
  - Tolerancia a pérdidas
  - Objetivo de inversión
  - Experiencia inversora
  - Reacción ante caídas
  - Preferencia de estabilidad vs crecimiento
  - Porcentaje de patrimonio a invertir
  - Necesidad de liquidez
  - Preferencia sectorial / temática
  - Importancia de la sostenibilidad (ESG)
  - Preferencia geográfica
  - Importancia de los dividendos

El resultado es un perfil de entre los 7 disponibles.
"""

from typing import Tuple, Dict


QUESTIONS = [
    {
        "id": "horizonte",
        "texto": "¿Cuál es tu horizonte temporal de inversión?",
        "opciones": [
            ("a", "Menos de 1 año", {"conservador": 4, "moderado": 1}),
            ("b", "Entre 1 y 3 años", {"conservador": 2, "moderado": 3}),
            ("c", "Entre 3 y 7 años", {"moderado": 2, "agresivo": 3}),
            ("d", "Más de 7 años", {"agresivo": 2, "muy_agresivo": 4}),
        ],
    },
    {
        "id": "tolerancia_perdida",
        "texto": "Si tu cartera pierde un 20% en un mes, ¿qué haces?",
        "opciones": [
            ("a", "Vendo todo inmediatamente", {"conservador": 5}),
            ("b", "Vendo parte para reducir riesgo", {"conservador": 2, "moderado": 2}),
            ("c", "No hago nada, espero a que se recupere", {"moderado": 2, "agresivo": 2}),
            ("d", "Compro más, es una oportunidad", {"agresivo": 2, "muy_agresivo": 4}),
        ],
    },
    {
        "id": "objetivo",
        "texto": "¿Cuál es tu principal objetivo de inversión?",
        "opciones": [
            ("a", "Preservar mi capital y no perder dinero", {"conservador": 5}),
            ("b", "Generar rentas periódicas (dividendos)", {"conservador": 1, "dividendos": 5}),
            ("c", "Crecimiento moderado con protección", {"moderado": 4}),
            ("d", "Máximo crecimiento del capital", {"agresivo": 3, "muy_agresivo": 3}),
        ],
    },
    {
        "id": "experiencia",
        "texto": "¿Cuánta experiencia tienes invirtiendo en bolsa?",
        "opciones": [
            ("a", "Ninguna, soy principiante", {"conservador": 3, "moderado": 1}),
            ("b", "Algo de experiencia (1-3 años)", {"moderado": 3}),
            ("c", "Experiencia intermedia (3-7 años)", {"moderado": 1, "agresivo": 3}),
            ("d", "Mucha experiencia (más de 7 años)", {"agresivo": 2, "muy_agresivo": 3}),
        ],
    },
    {
        "id": "volatilidad",
        "texto": "¿Qué nivel de fluctuación diaria aceptarías en tu cartera?",
        "opciones": [
            ("a", "Menos del 1% — prefiero estabilidad", {"conservador": 4, "dividendos": 1}),
            ("b", "Entre 1% y 3% — aceptable", {"moderado": 4}),
            ("c", "Entre 3% y 5% — puedo tolerarlo", {"agresivo": 4}),
            ("d", "Más del 5% — sin problema si la rentabilidad compensa", {"muy_agresivo": 5}),
        ],
    },
    {
        "id": "estabilidad_vs_crecimiento",
        "texto": "¿Qué prefieres?",
        "opciones": [
            ("a", "Ganar un 3% anual seguro", {"conservador": 4, "dividendos": 2}),
            ("b", "50% de probabilidad de ganar 10% o perder 2%", {"moderado": 4}),
            ("c", "50% de probabilidad de ganar 25% o perder 10%", {"agresivo": 4}),
            ("d", "50% de probabilidad de ganar 50% o perder 25%", {"muy_agresivo": 5}),
        ],
    },
    {
        "id": "porcentaje_patrimonio",
        "texto": "¿Qué porcentaje de tu patrimonio total vas a invertir en esta cartera?",
        "opciones": [
            ("a", "Menos del 10%", {"agresivo": 2, "muy_agresivo": 2}),
            ("b", "Entre el 10% y el 30%", {"moderado": 2, "agresivo": 2}),
            ("c", "Entre el 30% y el 60%", {"moderado": 3, "conservador": 1}),
            ("d", "Más del 60%", {"conservador": 4}),
        ],
    },
    {
        "id": "liquidez",
        "texto": "¿Necesitarás acceder a este dinero en los próximos 2 años?",
        "opciones": [
            ("a", "Sí, con seguridad", {"conservador": 5}),
            ("b", "Posiblemente", {"conservador": 2, "moderado": 2}),
            ("c", "Poco probable", {"moderado": 2, "agresivo": 2}),
            ("d", "No, es dinero que no necesito a corto plazo", {"agresivo": 2, "muy_agresivo": 3}),
        ],
    },
    {
        "id": "sector",
        "texto": "¿Tienes preferencia por algún sector o temática de inversión?",
        "opciones": [
            ("a", "No, quiero diversificación general", {"moderado": 2}),
            ("b", "Tecnología e innovación", {"tecnologico": 6}),
            ("c", "Empresas que pagan buenos dividendos", {"dividendos": 6}),
            ("d", "Empresas sostenibles y responsables (ESG)", {"esg": 6}),
        ],
    },
    {
        "id": "esg_importancia",
        "texto": "¿Qué importancia tiene para ti que las empresas sean sostenibles (ESG)?",
        "opciones": [
            ("a", "Es mi prioridad, aunque sacrifique algo de rentabilidad", {"esg": 5}),
            ("b", "Prefiero empresas ESG si no pierdo mucha rentabilidad", {"esg": 2, "moderado": 1}),
            ("c", "Me es indiferente", {"moderado": 1}),
            ("d", "Solo me importa la rentabilidad", {"agresivo": 1, "muy_agresivo": 2}),
        ],
    },
    {
        "id": "geografia",
        "texto": "¿Tienes preferencia geográfica para tu inversión?",
        "opciones": [
            ("a", "Prefiero diversificar entre EE.UU., Europa y Japón", {"moderado": 2, "conservador": 1}),
            ("b", "Principalmente EE.UU. (S&P 500)", {"agresivo": 1, "tecnologico": 2}),
            ("c", "Principalmente Europa (Eurostoxx)", {"moderado": 1}),
            ("d", "Me da igual, solo importan los números", {"agresivo": 1, "muy_agresivo": 1}),
        ],
    },
    {
        "id": "dividendos_importancia",
        "texto": "¿Qué importancia tienen los dividendos para ti?",
        "opciones": [
            ("a", "Fundamental, quiero ingresos recurrentes", {"dividendos": 5, "conservador": 1}),
            ("b", "Importante pero no decisivo", {"dividendos": 2, "moderado": 2}),
            ("c", "Prefiero que la empresa reinvierta en crecimiento", {"agresivo": 2, "tecnologico": 2}),
            ("d", "Irrelevante", {"muy_agresivo": 2}),
        ],
    },
]

PROFILES_ORDER = [
    "conservador", "moderado", "agresivo", "muy_agresivo",
    "dividendos", "tecnologico", "esg",
]

PROFILE_DESCRIPTIONS = {
    "conservador": "Priorizas la protección del capital. Tu cartera se orientará a acciones de baja volatilidad, bajo VaR y alta estabilidad.",
    "moderado": "Buscas un equilibrio entre rentabilidad y protección. Tu cartera ponderará ratios ajustados por riesgo como Sharpe y Sortino.",
    "agresivo": "Priorizas el crecimiento del capital. Tu cartera buscará alta rentabilidad y alpha, aceptando mayor volatilidad.",
    "muy_agresivo": "Buscas máxima rentabilidad sin restricciones de riesgo. Tu cartera se orientará a maximizar alpha y rentabilidad-kp.",
    "dividendos": "Buscas rentas periódicas estables. Tu cartera se centrará en empresas con historial sólido de dividendos crecientes.",
    "tecnologico": "Apuestas por el sector tecnológico. Tu cartera se concentrará en IT y comunicaciones, buscando crecimiento.",
    "esg": "Inviertes con criterios de sostenibilidad. Tu cartera incluirá solo empresas con rating ESG alto y buena diversificación.",
}


def run_questionnaire(interactive: bool = True) -> Tuple[str, Dict[str, int]]:
    """
    Ejecuta el cuestionario y devuelve el perfil resultante.

    Args:
        interactive: Si True, pregunta por consola. Si False, devuelve
                     la función de scoring para uso programático.

    Returns:
        (perfil, puntuaciones): nombre del perfil y dict con puntos acumulados
    """
    scores = {p: 0 for p in PROFILES_ORDER}

    if interactive:
        print("\n" + "=" * 60)
        print("  CUESTIONARIO DE PERFIL DEL INVERSOR")
        print("  Responde las 12 preguntas para determinar tu perfil")
        print("=" * 60)

    for i, q in enumerate(QUESTIONS, 1):
        if interactive:
            print(f"\n--- Pregunta {i}/12 ---")
            print(f"{q['texto']}\n")
            for letra, texto, _ in q["opciones"]:
                print(f"  {letra}) {texto}")

            while True:
                resp = input("\nTu respuesta (a/b/c/d): ").strip().lower()
                if resp in ["a", "b", "c", "d"]:
                    break
                print("  Por favor, introduce a, b, c o d.")
        else:
            resp = "b"  # default for non-interactive

        for letra, texto, puntos in q["opciones"]:
            if letra == resp:
                for perfil, pts in puntos.items():
                    scores[perfil] += pts
                break

    # Determinar perfil ganador
    profile = max(scores, key=scores.get)

    if interactive:
        print("\n" + "=" * 60)
        print(f"  TU PERFIL: {profile.upper().replace('_', ' ')}")
        print("=" * 60)
        print(f"\n  {PROFILE_DESCRIPTIONS[profile]}")
        print(f"\n  Puntuaciones: ", end="")
        sorted_scores = sorted(scores.items(), key=lambda x: -x[1])
        for p, s in sorted_scores:
            if s > 0:
                marker = " <--" if p == profile else ""
                print(f"\n    {p:15s} {s:3d} pts{marker}", end="")
        print("\n")

    return profile, scores


def score_answers(answers: Dict[str, str]) -> Tuple[str, Dict[str, int]]:
    """
    Calcula el perfil a partir de un diccionario de respuestas.
    Útil para uso programático o integración con interfaces.

    Args:
        answers: dict con {question_id: "a"/"b"/"c"/"d"}

    Returns:
        (perfil, puntuaciones)
    """
    scores = {p: 0 for p in PROFILES_ORDER}

    for q in QUESTIONS:
        resp = answers.get(q["id"], "b")
        for letra, texto, puntos in q["opciones"]:
            if letra == resp:
                for perfil, pts in puntos.items():
                    scores[perfil] += pts
                break

    profile = max(scores, key=scores.get)
    return profile, scores


if __name__ == "__main__":
    profile, scores = run_questionnaire(interactive=True)
