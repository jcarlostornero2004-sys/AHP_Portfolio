"""
Módulo 0 — Cuestionario de perfil del inversor
================================================
15 preguntas que cubren 5 dimensiones:
  - Tolerancia al riesgo (3 preguntas)
  - Horizonte temporal (3 preguntas)
  - Situación financiera (4 preguntas)
  - Perfil psicológico (3 preguntas)
  - Conocimiento e información (2 preguntas)

Cada opción tiene una puntuación numérica del 1 al 4.
El perfil se determina por el porcentaje sobre el total:
  < 33 % → conservador
  < 66 % → moderado
  ≥ 66 % → agresivo
"""

from typing import Dict


# Scores se almacenan como {"_score": N} para usar el sistema de puntuación numérica
QUESTIONS = [
    # ─── Tolerancia al riesgo ───
    {
        "id": "risk_1",
        "texto": "¿Qué pérdida máxima en su cartera sería tolerable para usted en un año?",
        "opciones": [
            ("a", "No toleraría ninguna pérdida; prefiero preservar el capital ante todo.", {"_score": 1}),
            ("b", "Aceptaría perder hasta un 5 % si el potencial de ganancia es razonable.", {"_score": 2}),
            ("c", "Podría asumir pérdidas de entre el 10 % y el 20 % a cambio de mayor rentabilidad.", {"_score": 3}),
            ("d", "Asumiría pérdidas superiores al 25 % si a largo plazo el retorno esperado es elevado.", {"_score": 4}),
        ],
    },
    {
        "id": "risk_2",
        "texto": "Si su cartera cayera un 20 % en tres meses por volatilidad del mercado, ¿qué haría?",
        "opciones": [
            ("a", "Vendería todo inmediatamente para evitar más pérdidas.", {"_score": 1}),
            ("b", "Vendería una parte para reducir la exposición al riesgo.", {"_score": 2}),
            ("c", "Mantendría la posición y esperaría a que el mercado se recupere.", {"_score": 3}),
            ("d", "Aprovecharía la caída para comprar más activos a precios bajos.", {"_score": 4}),
        ],
    },
    {
        "id": "risk_3",
        "texto": "¿Con qué concepto relaciona mejor el término 'riesgo de inversión'?",
        "opciones": [
            ("a", "Peligro que debo evitar a toda costa.", {"_score": 1}),
            ("b", "Incertidumbre que hay que minimizar con activos seguros.", {"_score": 2}),
            ("c", "Variable que acepto gestionar a cambio de mayor rentabilidad.", {"_score": 3}),
            ("d", "Oportunidad: a mayor riesgo, mayor potencial de beneficio.", {"_score": 4}),
        ],
    },
    # ─── Horizonte temporal ───
    {
        "id": "time_1",
        "texto": "¿Cuál es su horizonte de inversión principal?",
        "opciones": [
            ("a", "Menos de 1 año; necesito liquidez en el corto plazo.", {"_score": 1}),
            ("b", "Entre 1 y 3 años.", {"_score": 2}),
            ("c", "Entre 3 y 7 años.", {"_score": 3}),
            ("d", "Más de 7 años; estoy dispuesto a inmovilizar el capital durante mucho tiempo.", {"_score": 4}),
        ],
    },
    {
        "id": "time_2",
        "texto": "¿Tiene previsto necesitar una parte significativa del capital invertido en los próximos 12 meses?",
        "opciones": [
            ("a", "Sí, necesitaré disponer de la mayor parte del dinero.", {"_score": 1}),
            ("b", "Es posible que necesite hasta un 30 % del capital.", {"_score": 2}),
            ("c", "Probablemente no, pero podría surgir algún imprevisto.", {"_score": 3}),
            ("d", "No; el capital está totalmente comprometido para el largo plazo.", {"_score": 4}),
        ],
    },
    {
        "id": "time_3",
        "texto": "¿En qué etapa de su ciclo vital se encuentra actualmente?",
        "opciones": [
            ("a", "Próximo a la jubilación o ya jubilado; priorizo la preservación del capital.", {"_score": 1}),
            ("b", "Madurez laboral (45-60 años); busco equilibrio entre crecimiento y seguridad.", {"_score": 2}),
            ("c", "Etapa media (30-45 años); puedo asumir algo de riesgo con horizonte largo.", {"_score": 3}),
            ("d", "Inicio de carrera (menos de 30 años); horizonte muy largo y máxima capacidad de recuperación.", {"_score": 4}),
        ],
    },
    # ─── Situación financiera ───
    {
        "id": "fin_1",
        "texto": "¿Qué porcentaje de sus ahorros totales representa el capital que desea invertir?",
        "opciones": [
            ("a", "Más del 75 %; es casi todo lo que tengo ahorrado.", {"_score": 1}),
            ("b", "Entre el 50 % y el 75 %.", {"_score": 2}),
            ("c", "Entre el 25 % y el 50 %.", {"_score": 3}),
            ("d", "Menos del 25 %; invierto solo la parte que puedo permitirme perder.", {"_score": 4}),
        ],
    },
    {
        "id": "fin_2",
        "texto": "¿Dispone de un fondo de emergencia separado de su inversión (equivalente a 3-6 meses de gastos)?",
        "opciones": [
            ("a", "No tengo fondo de emergencia.", {"_score": 1}),
            ("b", "Tengo algo ahorrado, pero no cubriría más de 1-2 meses.", {"_score": 2}),
            ("c", "Sí, cubro entre 3 y 6 meses de gastos.", {"_score": 3}),
            ("d", "Sí, y además tengo otras fuentes de liquidez disponibles (crédito, otros activos).", {"_score": 4}),
        ],
    },
    {
        "id": "fin_3",
        "texto": "¿Cuál es la estabilidad percibida de sus ingresos actuales?",
        "opciones": [
            ("a", "Mis ingresos son irregulares o inseguros (freelance, desempleo reciente, etc.).", {"_score": 1}),
            ("b", "Tengo ingresos regulares pero con cierta incertidumbre a medio plazo.", {"_score": 2}),
            ("c", "Mis ingresos son estables y predecibles (contrato indefinido, funcionario, etc.).", {"_score": 3}),
            ("d", "Tengo ingresos muy elevados y diversificados; una pérdida de inversión no afectaría mi nivel de vida.", {"_score": 4}),
        ],
    },
    {
        "id": "fin_4",
        "texto": "¿Cuál es el objetivo principal de esta inversión?",
        "opciones": [
            ("a", "Conservar el capital y obtener algo de rentabilidad por encima de la inflación.", {"_score": 1}),
            ("b", "Generar ingresos periódicos (rentas, dividendos).", {"_score": 2}),
            ("c", "Hacer crecer el patrimonio a largo plazo con riesgo moderado.", {"_score": 3}),
            ("d", "Maximizar la rentabilidad sin importar la volatilidad; busco multiplicar el capital.", {"_score": 4}),
        ],
    },
    # ─── Perfil psicológico ───
    {
        "id": "psy_1",
        "texto": "Cuando toma decisiones financieras importantes, ¿cómo describiría su proceso?",
        "opciones": [
            ("a", "Me dejo llevar por la seguridad y evito cualquier incertidumbre.", {"_score": 1}),
            ("b", "Busco consejo profesional antes de decidir y actúo con cautela.", {"_score": 2}),
            ("c", "Analizo la información disponible y asumo la decisión con cierta comodidad.", {"_score": 3}),
            ("d", "Actúo con rapidez; confío en mi criterio y la volatilidad no me incomoda.", {"_score": 4}),
        ],
    },
    {
        "id": "psy_2",
        "texto": "¿Cómo reacciona emocionalmente cuando ve que sus inversiones pierden valor en el mercado?",
        "opciones": [
            ("a", "Siento mucha angustia y me cuesta dormir o concentrarme.", {"_score": 1}),
            ("b", "Me preocupa, reviso la cartera a menudo y pienso en vender.", {"_score": 2}),
            ("c", "Me incomoda, pero mantengo la calma y no cambio mi estrategia precipitadamente.", {"_score": 3}),
            ("d", "Lo vivo con total tranquilidad; es parte del ciclo normal del mercado.", {"_score": 4}),
        ],
    },
    {
        "id": "psy_3",
        "texto": "¿Ha experimentado alguna vez pérdidas significativas en inversiones pasadas?",
        "opciones": [
            ("a", "Sí, y fue traumático; ahora soy muy averso al riesgo.", {"_score": 1}),
            ("b", "Sí, pero aprendí de ello y ahora soy más prudente.", {"_score": 2}),
            ("c", "No tengo experiencia previa en inversiones.", {"_score": 2}),
            ("d", "Sí, pero las asumí con naturalidad como parte del proceso inversor.", {"_score": 4}),
        ],
    },
    # ─── Conocimiento e información ───
    {
        "id": "know_1",
        "texto": "¿Cómo describiría su nivel de conocimiento sobre mercados financieros?",
        "opciones": [
            ("a", "Básico; apenas conozco la diferencia entre acciones, bonos y depósitos.", {"_score": 1}),
            ("b", "Intermedio; entiendo conceptos como diversificación, rentabilidad y riesgo.", {"_score": 2}),
            ("c", "Avanzado; comprendo métricas como VaR, beta, ratio de Sharpe y valoración de activos.", {"_score": 3}),
            ("d", "Experto; trabajo en el sector financiero o tengo formación especializada en inversiones.", {"_score": 4}),
        ],
    },
    {
        "id": "know_2",
        "texto": "¿Con qué frecuencia hace seguimiento de sus inversiones y de las condiciones del mercado?",
        "opciones": [
            ("a", "Nunca o casi nunca; prefiero delegar completamente en un gestor.", {"_score": 1}),
            ("b", "Ocasionalmente, cuando recibo informes periódicos o hay noticias relevantes.", {"_score": 2}),
            ("c", "Con regularidad (semanal o mensual); sigo las principales variables del mercado.", {"_score": 3}),
            ("d", "A diario; tengo alertas activas y gestiono activamente mi cartera.", {"_score": 4}),
        ],
    },
]

PROFILES_ORDER = ["conservador", "moderado", "agresivo"]

PROFILE_DESCRIPTIONS = {
    "conservador": "El inversor prioriza la preservación del capital y la seguridad sobre la rentabilidad. La metodología AHP pondera con máxima prioridad los criterios de minimización de riesgo: volatilidad, VaR y max drawdown.",
    "moderado": "El inversor busca un equilibrio entre rentabilidad y riesgo. Acepta cierta volatilidad a cambio de crecimiento moderado del capital. El modelo AHP equilibra los criterios de rentabilidad y riesgo con un portafolio diversificado.",
    "agresivo": "El inversor tiene alta tolerancia al riesgo y prioriza maximizar la rentabilidad a largo plazo. El modelo AHP asigna mayor peso a los criterios de rentabilidad esperada y alpha, aceptando mayor exposición al riesgo sistemático.",
}

_N = len(QUESTIONS)           # 15
_MIN_SCORE = _N * 1           # 15
_MAX_SCORE = _N * 4           # 60
_RANGE = _MAX_SCORE - _MIN_SCORE  # 45


def _pct_to_scores(pct: float) -> Dict[str, int]:
    """Convierte el porcentaje total en puntuaciones por perfil para visualización (escala 0-50)."""
    return {
        "conservador": round((1.0 - pct) * 50),
        "moderado":    round((1.0 - abs(pct * 2.0 - 1.0)) * 50),
        "agresivo":    round(pct * 50),
    }


def score_answers(answers: Dict[str, str]) -> tuple:
    """
    Calcula el perfil a partir de un diccionario de respuestas.

    Args:
        answers: dict con {question_id: "a"/"b"/"c"/"d"}

    Returns:
        (perfil, puntuaciones) — puntuaciones en escala 0-50 por perfil
    """
    total = 0
    for q in QUESTIONS:
        resp = answers.get(q["id"], "b")
        for letra, _, puntos in q["opciones"]:
            if letra == resp:
                total += puntos.get("_score", 2)
                break

    pct = (total - _MIN_SCORE) / _RANGE

    if pct < 0.33:
        profile = "conservador"
    elif pct < 0.66:
        profile = "moderado"
    else:
        profile = "agresivo"

    return profile, _pct_to_scores(pct)


def run_questionnaire(interactive: bool = True) -> tuple:
    """
    Ejecuta el cuestionario y devuelve el perfil resultante.

    Args:
        interactive: Si True, pregunta por consola.

    Returns:
        (perfil, puntuaciones)
    """
    dims = {
        "risk": "Tolerancia al riesgo",
        "time": "Horizonte temporal",
        "fin":  "Situación financiera",
        "psy":  "Perfil psicológico",
        "know": "Conocimiento e información",
    }

    if interactive:
        print("\n" + "=" * 60)
        print("  CUESTIONARIO DE PERFIL DEL INVERSOR")
        print(f"  {_N} preguntas · 5 dimensiones")
        print("=" * 60)

    given_answers: Dict[str, str] = {}
    last_dim = None

    for i, q in enumerate(QUESTIONS, 1):
        dim_key = q["id"].split("_")[0]
        if interactive and dim_key != last_dim:
            print(f"\n  ── {dims.get(dim_key, dim_key)} ──")
            last_dim = dim_key

        if interactive:
            print(f"\n  Pregunta {i}/{_N}: {q['texto']}\n")
            for letra, texto, _ in q["opciones"]:
                print(f"    {letra}) {texto}")

            while True:
                resp = input("\n  Tu respuesta (a/b/c/d): ").strip().lower()
                if resp in ("a", "b", "c", "d"):
                    break
                print("  Por favor, introduce a, b, c o d.")
        else:
            resp = "b"

        given_answers[q["id"]] = resp

    profile, scores = score_answers(given_answers)

    if interactive:
        print("\n" + "=" * 60)
        print(f"  TU PERFIL: {profile.upper()}")
        print("=" * 60)
        print(f"\n  {PROFILE_DESCRIPTIONS[profile]}")
        print("\n  Puntuaciones relativas:")
        for p, s in sorted(scores.items(), key=lambda x: -x[1]):
            bar = "█" * s + "░" * (50 - s)
            marker = " ◄" if p == profile else ""
            print(f"    {p:15s} {s:2d}/50  {bar[:30]}{marker}")
        print()

    return profile, scores


if __name__ == "__main__":
    run_questionnaire(interactive=True)
