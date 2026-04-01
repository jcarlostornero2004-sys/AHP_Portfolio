"""
Word Report API router.
Generates a detailed step-by-step investment methodology report.
"""

import tempfile
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

from apps.api.routers.analysis import get_last_result

router = APIRouter(prefix="/api/report", tags=["report"])


class ReportRequest(BaseModel):
    answers: Optional[dict[str, str]] = None


@router.post("/word")
async def generate_word_report(req: ReportRequest = ReportRequest()):
    """Generate a detailed Word methodology report for the current portfolio."""
    last = get_last_result()
    if not last or "profile" not in last:
        raise HTTPException(
            status_code=400,
            detail="Ejecuta el análisis primero antes de generar el informe.",
        )
    try:
        report_path = _build_word_report(last, req.answers or {})
        profile = last["profile"]
        filename = f"Informe_AHP_{profile}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        return FileResponse(
            report_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────
# Document builder
# ─────────────────────────────────────────────────────────

def _build_word_report(data: dict, answers: dict) -> str:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()

    # ── Page layout (A4) ──────────────────────────────────
    sec = doc.sections[0]
    sec.page_width  = Inches(8.27)
    sec.page_height = Inches(11.69)
    for attr in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, attr, Inches(1.1))

    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10.5)
    doc.styles["Normal"].paragraph_format.space_after = Pt(5)

    # ── Color palette ────────────────────────────────────
    DARK  = RGBColor(0x1F, 0x2D, 0x3D)
    BLUE  = RGBColor(0x18, 0x5F, 0xA5)
    GOLD  = RGBColor(0xC8, 0xA0, 0x00)
    GRAY  = RGBColor(0x6C, 0x75, 0x7D)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    GREEN = RGBColor(0x1D, 0x6A, 0x3A)
    RED   = RGBColor(0xB0, 0x30, 0x20)

    PROFILE_COLORS = {
        "conservador": RGBColor(0x1A, 0x56, 0x9A),
        "moderado":    RGBColor(0x1A, 0x6A, 0x3E),
        "agresivo":    RGBColor(0xBF, 0x60, 0x00),
    }

    # ── Data extraction ──────────────────────────────────
    profile       = data.get("profile", "moderado")
    profile_label = profile.replace("_", " ").capitalize()
    P_CLR         = PROFILE_COLORS.get(profile, BLUE)
    winner        = data.get("winner", {})
    allocation    = data.get("allocation", [])
    ranking       = data.get("ranking", [])
    portfolios    = data.get("portfolios", [])
    stocks        = data.get("stocks", [])
    top_criteria  = data.get("top_criteria", [])
    scores        = data.get("scores", {})
    n_analyzed    = data.get("n_stocks_analyzed", 0)
    n_selected    = data.get("n_stocks_selected", 0)
    cr            = data.get("consistency_ratio", 0)
    is_synthetic  = data.get("is_synthetic", True)
    profile_desc  = data.get("profile_description", "")
    today         = datetime.now().strftime("%d de %B de %Y")
    winner_port   = next((p for p in portfolios if p.get("name") == winner.get("name")), {})

    # ── Helpers ──────────────────────────────────────────
    def cell_bg(cell, r, g, b):
        tc   = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd  = OxmlElement("w:shd")
        shd.set(qn("w:fill"), f"{r:02X}{g:02X}{b:02X}")
        shd.set(qn("w:val"), "clear")
        tcPr.append(shd)

    def thead(table, cols, r=0x18, g=0x5F, b=0xA5):
        row = table.rows[0]
        for i, txt in enumerate(cols):
            cell = row.cells[i]
            cell.text = ""
            run  = cell.paragraphs[0].add_run(txt)
            run.font.bold  = True
            run.font.color.rgb = WHITE
            run.font.size  = Pt(9)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            cell_bg(cell, r, g, b)

    def trow(row, vals, alt=False, center=False, bold=False):
        for i, v in enumerate(vals):
            cell = row.cells[i]
            cell.text = ""
            run  = cell.paragraphs[0].add_run(str(v))
            run.font.size  = Pt(9)
            run.font.bold  = bold
            if center:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if alt:
                cell_bg(cell, 0xEB, 0xF2, 0xFA)

    def h1(text, color=BLUE):
        p   = doc.add_paragraph()
        run = p.add_run(text)
        run.font.bold = True; run.font.size = Pt(16); run.font.color.rgb = color
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after  = Pt(6)
        return p

    def h2(text, color=DARK):
        p   = doc.add_paragraph()
        run = p.add_run(text)
        run.font.bold = True; run.font.size = Pt(12); run.font.color.rgb = color
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after  = Pt(4)
        return p

    def body(text, bold=False, italic=False, size=10.5, color=None):
        p   = doc.add_paragraph()
        run = p.add_run(text)
        run.font.size   = Pt(size)
        run.font.bold   = bold
        run.font.italic = italic
        if color:
            run.font.color.rgb = color
        return p

    def bullet(text):
        p   = doc.add_paragraph(style="List Bullet")
        run = p.add_run(text)
        run.font.size = Pt(10)

    def bar(val, max_val=9, w=14):
        f = int(round(val / max_val * w)) if max_val else 0
        return "█" * f + "░" * (w - f)

    # ═══════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════
    for _ in range(3):
        doc.add_paragraph()

    for line, size, clr in [
        ("INFORME METODOLÓGICO", 22, DARK),
        ("DE CONSTRUCCIÓN DE CARTERA", 22, DARK),
        ("", 6, DARK),
        ("Proceso Analítico Jerárquico (AHP) + Optimización de Markowitz", 13, BLUE),
    ]:
        p   = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.bold  = True
        run.font.size  = Pt(size)
        run.font.color.rgb = clr

    for _ in range(2):
        doc.add_paragraph()

    p   = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Perfil del Inversor:  {profile_label.upper()}")
    run.font.bold = True; run.font.size = Pt(20); run.font.color.rgb = P_CLR

    doc.add_paragraph()
    p   = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Portafolio Recomendado:  {winner.get('name','—')}   ·   Score AHP: {winner.get('score',0):.1f}%")
    run.font.size = Pt(12); run.font.color.rgb = GRAY

    for _ in range(4):
        doc.add_paragraph()

    for line, size in [(f"Generado el {today}", 10), ("AHP Portfolio Selector  —  TFG 2025", 9)]:
        p   = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.size = Pt(size); run.font.italic = True; run.font.color.rgb = GRAY

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════
    h1("RESUMEN EJECUTIVO")

    body(
        f"Este informe documenta, paso a paso, el proceso de construcción y selección de la cartera "
        f"óptima para un inversor con perfil {profile_label.upper()}. La metodología aplica el Proceso "
        f"Analítico Jerárquico (AHP) de Saaty (1990) combinado con la optimización media-varianza de "
        f"Markowitz (1952). Se analizaron {n_analyzed} acciones de tres índices internacionales, "
        f"seleccionando {n_selected} valores que superaron los filtros del perfil. A partir de ellos "
        f"se construyeron múltiples portafolios candidatos que fueron evaluados frente a 15 criterios "
        f"financieros en 5 categorías (Ratio de Consistencia: {cr} "
        f"{'✓' if cr < 0.10 else '⚠'})."
    )

    if winner_port:
        doc.add_paragraph()
        tbl = doc.add_table(rows=2, cols=6)
        tbl.style = "Table Grid"
        thead(tbl, ["Rentab. Anual", "Volatilidad", "Sharpe", "Max Drawdown", "Beta", "Alpha"])
        trow(tbl.rows[1], [
            f"{winner_port.get('rentabilidad',0):.2f}%",
            f"{winner_port.get('volatilidad',0):.2f}%",
            f"{winner_port.get('sharpe',0):.3f}",
            f"{winner_port.get('max_drawdown',0):.2f}%",
            f"{winner_port.get('beta',0):.3f}",
            f"{winner_port.get('alpha',0):.2f}%",
        ], center=True, bold=True)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 1. PERFIL DEL INVERSOR
    # ═══════════════════════════════════════════════════
    h1("1.  PERFIL DEL INVERSOR")
    h2("1.1  Clasificación del Perfil")

    body(
        "A través del cuestionario de 15 preguntas estructurado en 5 dimensiones (Tolerancia al Riesgo, "
        "Horizonte Temporal, Situación Financiera, Perfil Psicológico y Conocimiento), el sistema "
        "determinó el siguiente perfil inversor:"
    )
    p   = doc.add_paragraph()
    run = p.add_run(f"  Perfil asignado:  {profile_label.upper()}")
    run.font.bold = True; run.font.size = Pt(14); run.font.color.rgb = P_CLR
    body(profile_desc)

    if scores:
        h2("1.2  Puntuaciones por Perfil")
        body("Afinidad del inversor con cada perfil (escala 0-50 pts):")
        sorted_sc = sorted(scores.items(), key=lambda x: -x[1])
        tbl = doc.add_table(rows=len(sorted_sc) + 1, cols=3)
        tbl.style = "Table Grid"
        thead(tbl, ["Perfil", "Puntuación", "Afinidad relativa"])
        for i, (pn, ps) in enumerate(sorted_sc):
            trow(tbl.rows[i+1],
                 [pn.replace("_"," ").capitalize(), f"{ps} / 50 pts", bar(ps, 50, 20)],
                 alt=(i % 2 == 0))

    h2("1.3  Implicaciones del Perfil en la Estrategia")

    PROFILE_IMPL = {
        "conservador": [
            "Se priorizan large caps (>$10B market cap) con alta liquidez (>1M volumen diario)",
            "Los criterios de riesgo (VaR, CVaR, volatilidad, max drawdown) tienen el mayor peso AHP",
            "Se exigen métricas ajustadas por riesgo elevadas: Sharpe (7/9) y Sortino (8/9)",
            "El universo se restringe a empresas con historial probado y flujos de caja estables",
        ],
        "moderado": [
            "Se busca equilibrio entre rentabilidad esperada y control del riesgo",
            "Capitalización mínima $5B con volumen diario >750K acciones",
            "El AHP equilibra criterios de rendimiento y riesgo con pesos similares (5-8/9)",
            "Portafolio diversificado geográficamente entre los tres índices analizados",
        ],
        "agresivo": [
            "Se acepta mayor volatilidad a cambio de mayor potencial de rentabilidad",
            "Universo más amplio incluyendo mid caps ($2B+ market cap)",
            "El AHP prioriza rentabilidad (8/9), alpha de Jensen (7/9) y diferencial kp (7/9)",
            "Mayor concentración en activos de alto crecimiento potencial",
        ],
    }
    for impl in PROFILE_IMPL.get(profile, []):
        bullet(impl)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 2. UNIVERSO Y DATOS
    # ═══════════════════════════════════════════════════
    h1("2.  UNIVERSO DE INVERSIÓN Y DATOS UTILIZADOS")
    h2("2.1  Índices Analizados")

    body(
        "El análisis cubre el universo de acciones de tres grandes índices internacionales, "
        "garantizando diversificación geográfica y sectorial desde el inicio:"
    )
    tbl = doc.add_table(rows=4, cols=4)
    tbl.style = "Table Grid"
    thead(tbl, ["Índice", "Región", "Universo", "Por qué se incluye"])
    idx_data = [
        ("S&P 500",        "EE.UU.",  "500 mayores empresas americanas",
         "Mayor mercado de renta variable; alta liquidez y datos históricos fiables"),
        ("Eurostoxx 600",  "Europa",  "600 principales empresas europeas",
         "Diversificación geográfica; exposición al ciclo económico europeo"),
        ("Nikkei 225",     "Japón",   "225 empresas representativas de Tokio",
         "Tercera economía mundial; baja correlación histórica con mercados occidentales"),
    ]
    for i, row_data in enumerate(idx_data):
        trow(tbl.rows[i+1], row_data, alt=(i % 2 == 0))

    h2("2.2  Indicadores Financieros Calculados")
    body(
        f"Para cada acción se obtuvieron series históricas de precios diarios ajustados "
        f"de los últimos 2 años "
        f"({'Yahoo Finance — datos reales de mercado' if not is_synthetic else 'simulación Monte Carlo calibrada al mercado'}). "
        f"Se calcularon los 15 indicadores siguientes:"
    )

    METRICS = [
        ("Rentabilidad anualizada",     "Rendimiento compuesto anual del activo",                               "Rendimiento"),
        ("Ratio de Sharpe",             "Exceso de retorno por unidad de riesgo total",                         "Rendimiento"),
        ("Ratio de Sortino",            "Como Sharpe pero solo penaliza el riesgo a la baja",                   "Rendimiento"),
        ("Alpha de Jensen",             "Rentabilidad por encima de la predicción del CAPM",                    "Rendimiento"),
        ("Volatilidad (σ)",             "Desviación estándar anualizada de los retornos logarítmicos",          "Riesgo"),
        ("VaR 95%",                     "Pérdida máxima esperada anual con 95% de confianza",                   "Riesgo"),
        ("CVaR / Expected Shortfall",   "Pérdida media en el 5% de peores escenarios",                         "Riesgo"),
        ("Max Drawdown",                "Caída máxima desde máximo histórico al mínimo posterior",              "Riesgo"),
        ("Beta",                        "Sensibilidad del activo al movimiento del índice de referencia",       "Eficiencia"),
        ("Tracking Error",              "Desviación de retorno del portafolio vs benchmark",                    "Eficiencia"),
        ("Rentab. − Coste Capital (kp)","Exceso de rentabilidad sobre el coste de capital del portafolio",     "Eficiencia"),
        ("Coef. de Variación (CV)",     "Riesgo por unidad de rentabilidad (σ / μ)",                           "Estabilidad"),
        ("Asimetría (Skewness)",        "Sesgo de la distribución de retornos (positivo = favorable)",          "Estabilidad"),
        ("Correlación media",           "Correlación media entre todos los pares de activos de la cartera",     "Diversificación"),
        ("Diversificación geográfica",  "Proporción de activos de distinta región en el portafolio",            "Diversificación"),
    ]
    tbl = doc.add_table(rows=len(METRICS)+1, cols=3)
    tbl.style = "Table Grid"
    thead(tbl, ["Indicador", "Descripción y para qué se usa", "Categoría"])
    for i, (ind, desc, cat) in enumerate(METRICS):
        trow(tbl.rows[i+1], [ind, desc, cat], alt=(i % 2 == 0))

    body(
        f"Total acciones analizadas: {n_analyzed}  ·  Acciones que pasaron los filtros: {n_selected}",
        italic=True, size=9.5, color=GRAY
    )

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 3. FILTRADO DE ACCIONES
    # ═══════════════════════════════════════════════════
    h1("3.  FILTRADO Y SELECCIÓN DE ACCIONES")
    h2("3.1  Criterios de Pre-filtrado por Perfil")
    body(
        f"Antes de aplicar el AHP se filtra el universo para conservar solo los activos consistentes "
        f"con el perfil {profile_label.upper()}. Los filtros son cuantitativos y se aplican secuencialmente:"
    )

    FILTERS = {
        "conservador": [
            ("Capitalización mínima",    "$10.000 M",       "Garantiza alta liquidez y estabilidad; reduce riesgo de quiebra"),
            ("Volumen medio diario",     "> 1.000.000 acc.", "Permite entrar/salir sin mover precio; minimiza riesgo de liquidez"),
            ("Rentabilidad positiva",    "Obligatoria",      "Un perfil conservador no invierte en empresas en pérdidas"),
            ("Máx. acciones por índice", "80",               "Reduce ruido; selecciona las más representativas de cada mercado"),
            ("Acciones finales",         "12 valores",       "Diversificación eficiente sin over-diversification"),
        ],
        "moderado": [
            ("Capitalización mínima",    "$5.000 M",         "Balance entre liquidez y acceso a empresas de crecimiento"),
            ("Volumen medio diario",     "> 750.000 acc.",   "Liquidez adecuada para horizonte medio"),
            ("Rentabilidad positiva",    "Obligatoria",      "Se evitan empresas en pérdidas"),
            ("Máx. acciones por índice", "100",              "Universo más amplio que conservador"),
            ("Acciones finales",         "12 valores",       "Diversificación equilibrada"),
        ],
        "agresivo": [
            ("Capitalización mínima",    "$2.000 M",         "Incluye mid-caps con mayor potencial de revalorización"),
            ("Volumen medio diario",     "> 500.000 acc.",   "Liquidez mínima aceptable"),
            ("Rentabilidad positiva",    "Obligatoria",      "Criterio básico de viabilidad"),
            ("Máx. acciones por índice", "120",              "Universo amplio para capturar oportunidades"),
            ("Acciones finales",         "12 valores",       "Concentración en los mejores candidatos"),
        ],
    }

    fdata = FILTERS.get(profile, [])
    tbl = doc.add_table(rows=len(fdata)+1, cols=3)
    tbl.style = "Table Grid"
    thead(tbl, ["Filtro aplicado", f"Valor para perfil {profile_label}", "Justificación"])
    for i, row_data in enumerate(fdata):
        trow(tbl.rows[i+1], row_data, alt=(i % 2 == 0))

    if stocks:
        h2("3.2  Acciones Seleccionadas (Top 8 por puntuación de filtrado)")
        body(f"Las {n_selected} acciones que superaron todos los filtros. Las métricas corresponden al periodo de análisis (2 años):")
        tbl = doc.add_table(rows=len(stocks)+1, cols=5)
        tbl.style = "Table Grid"
        thead(tbl, ["Ticker", "Rentab. Anual", "Sharpe", "Volatilidad", "Beta"])
        for i, s in enumerate(stocks):
            trow(tbl.rows[i+1], [
                s.get("ticker",""),
                f"{s.get('rentabilidad',0):.2f}%",
                f"{s.get('sharpe',0):.3f}",
                f"{s.get('volatilidad',0):.2f}%",
                f"{s.get('beta',0):.3f}",
            ], alt=(i % 2 == 0), center=True)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 4. METODOLOGÍA AHP
    # ═══════════════════════════════════════════════════
    h1("4.  METODOLOGÍA AHP — PONDERACIÓN DE CRITERIOS")
    h2("4.1  ¿Qué es el AHP?")
    body(
        "El Proceso Analítico Jerárquico (AHP), desarrollado por Thomas L. Saaty (1990), es una técnica "
        "de decisión multicriterio que estructura problemas complejos mediante una jerarquía de criterios. "
        "El proceso consiste en:"
    )
    for step in [
        "Definir los 15 criterios financieros de evaluación relevantes para el objetivo inversor",
        "Construir una matriz de comparación por pares (15×15) usando la escala de Saaty (1-9)",
        "Calcular el vector de prioridades (eigenvector principal normalizado) → pesos de cada criterio",
        f"Verificar consistencia: Ratio de Consistencia (CR) = {cr}  {'✓ Consistente (CR < 0.10)' if cr < 0.10 else '⚠ Límite aceptable'}",
        "Aplicar los pesos obtenidos para puntuar y rankear los portafolios candidatos",
    ]:
        bullet(step)

    h2(f"4.2  Pesos AHP para Perfil {profile_label}")
    body(
        f"Los pesos reflejan la importancia relativa de cada criterio para el perfil {profile_label.upper()} "
        f"en la escala de Saaty (1 = importancia mínima, 9 = importancia máxima). "
        f"Los criterios con peso mayor dominan la selección del portafolio ganador:"
    )

    if top_criteria:
        tbl = doc.add_table(rows=len(top_criteria)+1, cols=4)
        tbl.style = "Table Grid"
        thead(tbl, ["Criterio", "Peso (Saaty)", "Visualización", "Objetivo"])
        for i, c in enumerate(top_criteria):
            trow(tbl.rows[i+1], [
                c.get("name",""),
                f"{c.get('weight',0)} / 9",
                bar(c.get("weight",0), 9, 12),
                "Maximizar" if c.get("direction") == "maximize" else "Minimizar",
            ], alt=(i % 2 == 0), center=True)

    h2("4.3  Justificación de los Pesos")
    WEIGHT_JUST = {
        "conservador": (
            "Para el perfil conservador los criterios de RIESGO reciben los pesos más altos (7-9/9). "
            "El CVaR y Max Drawdown tienen peso máximo porque este inversor no tolera pérdidas significativas. "
            "La rentabilidad bruta tiene el menor peso (2/9): se acepta sacrificar rendimiento a cambio de protección. "
            "El Sharpe (7/9) y Sortino (8/9) son altos porque miden rentabilidad ajustada por riesgo — el objetivo "
            "es el máximo rendimiento POR UNIDAD DE RIESGO, no el máximo rendimiento absoluto."
        ),
        "moderado": (
            "Para el perfil moderado se busca equilibrio. El Max Drawdown (8/9) y el Sharpe (8/9) lideran "
            "porque este inversor quiere limitar caídas máximas y maximizar eficiencia riesgo/retorno. "
            "La rentabilidad tiene peso medio (5/9) — importa, pero no a cualquier precio de riesgo. "
            "La correlación media entre activos (7/9) garantiza diversificación real. "
            "El beta moderado (6/9) asegura cierta independencia del movimiento general de mercado."
        ),
        "agresivo": (
            "Para el perfil agresivo, RENTABILIDAD (8/9) y ALPHA (7/9) lideran el ranking. "
            "Este inversor busca batir al mercado y maximizar el crecimiento del capital. "
            "El VaR y CVaR tienen peso bajo (3/9) porque se acepta la posibilidad de pérdidas mayores "
            "a cambio de mayor upside potencial. El diferencial rentabilidad-coste de capital (7/9) es "
            "prioritario para justificar el riesgo asumido sobre el coste de oportunidad."
        ),
    }
    body(WEIGHT_JUST.get(profile, ""))

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 5. CONSTRUCCIÓN DE PORTAFOLIOS (MARKOWITZ)
    # ═══════════════════════════════════════════════════
    h1("5.  CONSTRUCCIÓN DE PORTAFOLIOS — OPTIMIZACIÓN DE MARKOWITZ")
    h2("5.1  Método de Optimización")
    body(
        "Sobre las acciones seleccionadas en el paso anterior se aplica la teoría de portafolios de "
        "Markowitz (1952). Se calculan múltiples carteras candidatas resolviendo distintos "
        "problemas de optimización convexa:"
    )
    for step in [
        "Se calcula la matriz de covarianzas Σ de los retornos logarítmicos diarios de todos los activos",
        "Se definen pesos w = (w₁,...,wₙ) con restricciones: Σwᵢ = 1,  wᵢ ≥ 0  (solo posiciones largas)",
        "Portafolio Máximo Sharpe: max [ E(Rp) − Rf ] / σ(Rp)",
        "Portafolio Mínima Varianza: min σ²(Rp) = wᵀΣw",
        "Portafolio Máxima Rentabilidad: max E(Rp)",
        "Portafolio Equal Weight: wᵢ = 1/n  (benchmark igualitario como referencia)",
    ]:
        bullet(step)

    h2("5.2  Por qué el Porcentaje Específico de cada Acción")
    body(
        "Los pesos asignados a cada acción NO son arbitrarios. Son el resultado matemático de la "
        "optimización que maximiza el Ratio de Sharpe del portafolio completo, resolviendo:"
    )
    p   = doc.add_paragraph()
    run = p.add_run("    max  w'μ − Rf  /  √(w'Σw)")
    run.font.name = "Courier New"; run.font.size = Pt(12); run.font.bold = True
    run.font.color.rgb = BLUE
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    body(
        "Donde μ es el vector de rentabilidades esperadas y Σ la matriz de covarianzas. "
        "El resultado w* da los pesos exactos que maximizan el exceso de rentabilidad por unidad de riesgo. "
        "En la práctica, reciben más peso los activos que tienen:"
    )
    for reason in [
        "Mayor rentabilidad esperada individual",
        "Menor volatilidad propia",
        "Baja correlación con el resto de activos de la cartera (efecto diversificación)",
    ]:
        bullet(reason)

    if allocation:
        h2("5.3  Pesos Óptimos del Portafolio Ganador")
        body(f"Resultado de Markowitz para el portafolio {winner.get('name','')}:")
        tbl = doc.add_table(rows=len(allocation)+1, cols=4)
        tbl.style = "Table Grid"
        thead(tbl, ["Empresa (Ticker)", "% Asignado", "Visualización", "Sharpe individual"])
        for i, a in enumerate(allocation):
            ticker = a.get("ticker","")
            wstr   = a.get("weight","0%")
            sd     = next((s for s in stocks if s.get("ticker") == ticker), {})
            sharpe_ind = sd.get("sharpe", 0) if sd else 0
            try:
                wf = float(wstr.replace("%",""))
                vis = bar(wf, 100, 16)
            except Exception:
                vis = wstr
            trow(tbl.rows[i+1], [ticker, wstr, vis, f"{sharpe_ind:.3f}" if sharpe_ind else "—"],
                 alt=(i % 2 == 0), center=True)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 6. RANKING AHP
    # ═══════════════════════════════════════════════════
    h1("6.  RANKING AHP Y SELECCIÓN DEL PORTAFOLIO GANADOR")
    h2("6.1  Proceso de Puntuación AHP")
    body(
        f"El motor AHP evalúa los {len(portfolios)} portafolios candidatos frente a los 15 criterios. El proceso:"
    )
    for step in [
        "Para cada criterio, se normalizan los valores de todos los portafolios (escala 0-1)",
        "Se pondera cada valor normalizado por el peso AHP del criterio correspondiente",
        "Se suman ponderadamente para obtener la puntuación global de cada portafolio",
        "El portafolio con mayor puntuación total AHP es el ganador",
    ]:
        bullet(step)

    if ranking and portfolios:
        h2("6.2  Ranking Final")
        tbl = doc.add_table(rows=len(ranking)+1, cols=7)
        tbl.style = "Table Grid"
        thead(tbl, ["Pos.", "Portafolio", "Score AHP", "Rentab.", "Sharpe", "Volatil.", "Max DD"])
        for i, r in enumerate(ranking):
            pt = next((p for p in portfolios if p.get("name") == r.get("name")), {})
            row = tbl.rows[i+1]
            vals = [
                f"#{r.get('rank',i+1)}",
                r.get("name",""),
                f"{r.get('score',0):.1f}%",
                f"{pt.get('rentabilidad',0):.2f}%",
                f"{pt.get('sharpe',0):.3f}",
                f"{pt.get('volatilidad',0):.2f}%",
                f"{pt.get('max_drawdown',0):.2f}%",
            ]
            for j, v in enumerate(vals):
                cell = row.cells[j]
                cell.text = ""
                run = cell.paragraphs[0].add_run(v)
                run.font.size = Pt(9)
                run.font.bold = (i == 0)
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                if i == 0:
                    cell_bg(cell, 0xD4, 0xAF, 0x37)
                elif i % 2 == 0:
                    cell_bg(cell, 0xEB, 0xF2, 0xFA)

    h2("6.3  Por qué Ganó Este Portafolio")
    WINNER_REASONS = {
        "conservador": [
            f"Menor combinación de riesgo del conjunto: volatilidad {winner_port.get('volatilidad',0):.2f}%, max drawdown {winner_port.get('max_drawdown',0):.2f}%",
            f"Sharpe ratio {winner_port.get('sharpe',0):.3f}: máxima eficiencia riesgo/retorno entre los candidatos",
            f"Beta {winner_port.get('beta',0):.3f}: baja sensibilidad al mercado, reduce el riesgo sistemático",
            "Activos con baja correlación entre sí, maximizando el efecto real de diversificación",
        ],
        "moderado": [
            f"Mejor equilibrio rentabilidad/riesgo: {winner_port.get('rentabilidad',0):.2f}% de retorno con {winner_port.get('volatilidad',0):.2f}% de volatilidad",
            f"Sharpe ratio {winner_port.get('sharpe',0):.3f}, de los más altos del conjunto de candidatos",
            f"Max drawdown {winner_port.get('max_drawdown',0):.2f}% dentro de niveles tolerables para el perfil",
            "Composición que garantiza diversificación geográfica y sectorial",
        ],
        "agresivo": [
            f"Mayor rentabilidad anualizada: {winner_port.get('rentabilidad',0):.2f}%, superando a todos los candidatos",
            f"Alpha de Jensen {winner_port.get('alpha',0):.2f}%: genera valor por encima de lo que predice el CAPM",
            f"A pesar de mayor volatilidad ({winner_port.get('volatilidad',0):.2f}%), el Sharpe {winner_port.get('sharpe',0):.3f} sigue siendo positivo",
            "Los activos seleccionados presentan el mayor potencial de crecimiento histórico documentado",
        ],
    }
    for reason in WINNER_REASONS.get(profile, []):
        bullet(reason)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 7. PORTAFOLIO RECOMENDADO
    # ═══════════════════════════════════════════════════
    h1("7.  PORTAFOLIO RECOMENDADO — COMPOSICIÓN DETALLADA")

    p   = doc.add_paragraph()
    run = p.add_run(f"  ★  {winner.get('name','')}   —   Score AHP: {winner.get('score',0):.1f}%")
    run.font.bold = True; run.font.size = Pt(16); run.font.color.rgb = GOLD

    if winner_port:
        body("Métricas financieras:", bold=True)
        tbl = doc.add_table(rows=3, cols=6)
        tbl.style = "Table Grid"
        thead(tbl, ["Métrica", "Valor", "Métrica", "Valor", "Métrica", "Valor"])
        pairs = [
            ("Rentabilidad Anual",  f"{winner_port.get('rentabilidad',0):.2f}%"),
            ("Volatilidad",         f"{winner_port.get('volatilidad',0):.2f}%"),
            ("Ratio de Sharpe",     f"{winner_port.get('sharpe',0):.4f}"),
            ("Max Drawdown",        f"{winner_port.get('max_drawdown',0):.2f}%"),
            ("Beta",                f"{winner_port.get('beta',0):.4f}"),
            ("Alpha de Jensen",     f"{winner_port.get('alpha',0):.2f}%"),
        ]
        for row_idx in range(2):
            row = tbl.rows[row_idx+1]
            for col_idx in range(3):
                pi = row_idx*3 + col_idx
                if pi < len(pairs):
                    row.cells[col_idx*2].text = ""
                    row.cells[col_idx*2].paragraphs[0].add_run(pairs[pi][0]).font.size = Pt(9)
                    row.cells[col_idx*2+1].text = ""
                    rn = row.cells[col_idx*2+1].paragraphs[0].add_run(pairs[pi][1])
                    rn.font.size = Pt(9); rn.font.bold = True
                    row.cells[col_idx*2+1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if row_idx % 2 == 0:
                        cell_bg(row.cells[col_idx*2],   0xEB, 0xF2, 0xFA)
                        cell_bg(row.cells[col_idx*2+1], 0xEB, 0xF2, 0xFA)

    if allocation:
        body("\nComposición y justificación de la asignación de capital:", bold=True)
        body(
            "Los porcentajes son el resultado matemático de la optimización de Markowitz. "
            "Cada peso representa la fracción óptima de capital que maximiza el Ratio de Sharpe "
            "del portafolio completo, teniendo en cuenta la rentabilidad esperada, la volatilidad "
            "individual y las correlaciones cruzadas entre todos los activos:"
        )
        tbl = doc.add_table(rows=len(allocation)+1, cols=4)
        tbl.style = "Table Grid"
        thead(tbl, ["Empresa (Ticker)", "Asignación de Capital", "Sharpe Individual", "Rol en el portafolio"])
        for i, a in enumerate(allocation):
            ticker = a.get("ticker","")
            wstr   = a.get("weight","0%")
            sd     = next((s for s in stocks if s.get("ticker") == ticker), {})
            sharpe_ind = sd.get("sharpe", 0) if sd else 0
            try:
                wf   = float(wstr.replace("%",""))
                role = "Posición principal" if wf > 25 else "Posición media" if wf > 10 else "Diversificadora"
            except Exception:
                role = "—"
            trow(tbl.rows[i+1],
                 [ticker, wstr, f"{sharpe_ind:.3f}" if sharpe_ind else "—", role],
                 alt=(i % 2 == 0), center=True)

        body(
            "Las posiciones principales concentran capital en activos con alta rentabilidad ajustada por riesgo "
            "y baja correlación con el resto. Las posiciones diversificadoras reducen el riesgo global de la "
            "cartera gracias a su baja covarianza con los demás activos, aunque su Sharpe individual sea menor.",
            italic=True, size=9.5, color=GRAY
        )

    doc.add_page_break()

    # ═══════════════════════════════════════════════════
    # 8. REFERENCIAS
    # ═══════════════════════════════════════════════════
    h1("8.  REFERENCIAS BIBLIOGRÁFICAS")

    REFS = [
        "Saaty, T.L. (1990). How to make a decision: The Analytic Hierarchy Process. EJOR, 48(1), 9-26.",
        "Markowitz, H.M. (1952). Portfolio Selection. The Journal of Finance, 7(1), 77-91.",
        "Sharpe, W.F. (1966). Mutual Fund Performance. Journal of Business, 39(1), 119-138.",
        "Sortino, F.A. y Price, L.N. (1994). Performance Measurement in a Downside Risk Framework. Journal of Investing, 3(3), 59-64.",
        "Jensen, M.C. (1968). The Performance of Mutual Funds 1945-1964. Journal of Finance, 23(2), 389-416.",
        "Escobar, J.W. (2015). Selección de portafolios óptimos usando AHP. Contaduría y Administración, 60, 346-366.",
        "Elton, E.J. y Gruber, M.J. (1995). Modern Portfolio Theory and Investment Analysis. Wiley.",
        "Artzner, P. et al. (1999). Coherent Measures of Risk. Mathematical Finance, 9(3), 203-228.",
    ]
    for ref in REFS:
        bullet(ref)

    body(
        f"\nDocumento generado automáticamente por AHP Portfolio Selector el {today}. "
        f"Fuente de datos: {'Yahoo Finance (mercado real)' if not is_synthetic else 'Simulación Monte Carlo'}. "
        "Este informe es de carácter informativo y no constituye asesoramiento financiero regulado.",
        italic=True, size=9, color=GRAY
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)
    return tmp.name
