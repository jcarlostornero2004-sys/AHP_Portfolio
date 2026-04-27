"""
Word Report API router.
Generates a comprehensive professional investment methodology report.
"""

import tempfile
import time
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
    last = get_last_result()
    if not last or "profile" not in last:
        raise HTTPException(status_code=400, detail="Ejecuta el análisis primero.")
    try:
        path = _build_word_report(last, req.answers or {})
        profile = last["profile"]
        fname = f"Informe_AHP_{profile}_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
        return FileResponse(
            path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=fname,
        )
    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# STATIC REFERENCE DATA
# ─────────────────────────────────────────────────────────────────────────────

CRITERIA_ORDER = [
    "rentabilidad", "sharpe", "sortino", "alpha",
    "volatilidad", "var_95", "cvar_95", "max_drawdown",
    "beta", "tracking_error", "rentab_kp",
    "cv", "skewness", "corr_media", "div_geo",
]

CRITERIA_META = {
    "rentabilidad":   {"label": "Rentabilidad Anualizada",       "dir": "maximize", "cat": "Rendimiento",     "formula": "mu x 252",                        "desc": "Media de retornos log diarios escalada a 252 dias habiles. Crecimiento porcentual anual esperado."},
    "sharpe":         {"label": "Ratio de Sharpe",               "dir": "maximize", "cat": "Rendimiento",     "formula": "(Rp - Rf) / sigma_p",             "desc": "Exceso de rentabilidad sobre la tasa libre de riesgo por unidad de riesgo total. Mayor = mejor."},
    "sortino":        {"label": "Ratio de Sortino",              "dir": "maximize", "cat": "Rendimiento",     "formula": "(Rp - Rf) / sigma_down",          "desc": "Como Sharpe pero solo penaliza la volatilidad a la baja. Mas relevante para inversores aversos a perdidas."},
    "alpha":          {"label": "Alpha de Jensen",               "dir": "maximize", "cat": "Rendimiento",     "formula": "Rp - [Rf + beta(Rm - Rf)]",       "desc": "Rentabilidad por encima de la prediccion del CAPM. Mide la capacidad de generar valor por encima del mercado."},
    "volatilidad":    {"label": "Volatilidad (sigma)",           "dir": "minimize", "cat": "Riesgo",          "formula": "sigma_diaria x sqrt(252)",         "desc": "Desviacion estandar de los retornos diarios, anualizada. Mayor volatilidad = mayor incertidumbre."},
    "var_95":         {"label": "VaR 95% (Parametrico)",         "dir": "minimize", "cat": "Riesgo",          "formula": "-(mu + z_0.05 x sigma)",          "desc": "Perdida maxima esperada con 95% de confianza en un periodo dado."},
    "cvar_95":        {"label": "CVaR 95% (Expected Shortfall)", "dir": "minimize", "cat": "Riesgo",          "formula": "-E[R | R <= q_5%]",               "desc": "Perdida media en el 5% de los peores escenarios. Mas conservador que VaR."},
    "max_drawdown":   {"label": "Max Drawdown",                  "dir": "minimize", "cat": "Riesgo",          "formula": "max[(Pico-Valle)/Pico]",           "desc": "Mayor caida porcentual desde el maximo historico. Peor escenario para el inversor."},
    "beta":           {"label": "Beta del Portafolio",           "dir": "minimize", "cat": "Eficiencia",      "formula": "Cov(Ri,Rm) / Var(Rm)",            "desc": "Sensibilidad al mercado. Beta=1 se mueve como el indice; >1 amplifica; <1 amortigua."},
    "tracking_error": {"label": "Tracking Error",                "dir": "minimize", "cat": "Eficiencia",      "formula": "sigma(Ri - Rm) x sqrt(252)",       "desc": "Desviacion de los retornos con el benchmark. Mide cuanto se aleja la cartera del indice."},
    "rentab_kp":      {"label": "Rentab. - Coste Capital",       "dir": "maximize", "cat": "Eficiencia",      "formula": "Rp - [Rf + beta(Rm - Rf)]",       "desc": "Diferencia entre rentabilidad obtenida y el coste de capital del CAPM. Positivo = supera el minimo exigido."},
    "cv":             {"label": "Coeficiente de Variacion",      "dir": "minimize", "cat": "Estabilidad",     "formula": "sigma / |mu|",                    "desc": "Riesgo por unidad de rentabilidad. Permite comparar dispersion entre activos con distintos retornos."},
    "skewness":       {"label": "Skewness (Asimetria)",          "dir": "maximize", "cat": "Estabilidad",     "formula": "E[(R-mu)^3] / sigma^3",           "desc": "Asimetria de la distribucion. Positivo = mas retornos extremos positivos."},
    "corr_media":     {"label": "Correlacion Media",             "dir": "minimize", "cat": "Diversificacion", "formula": "media(rho_ij) i!=j",              "desc": "Correlacion media entre pares de activos. Mas baja = mayor beneficio de diversificacion."},
    "div_geo":        {"label": "Diversificacion Geografica",    "dir": "maximize", "cat": "Diversificacion", "formula": "1 - (1/n)",                       "desc": "Dispersion entre los tres mercados. Proximo a 1 = cartera bien repartida geograficamente."},
}

ALL_PROFILE_WEIGHTS = {
    "conservador":  {"volatilidad":9,"var_95":9,"max_drawdown":9,"sortino":8,"cvar_95":8,"beta":8,"corr_media":8,"sharpe":7,"tracking_error":7,"cv":7,"skewness":6,"div_geo":6,"alpha":3,"rentab_kp":3,"rentabilidad":2},
    "moderado":     {"sharpe":8,"max_drawdown":8,"sortino":7,"volatilidad":7,"var_95":7,"corr_media":7,"cvar_95":6,"beta":6,"cv":6,"div_geo":6,"rentabilidad":5,"alpha":5,"tracking_error":5,"rentab_kp":5,"skewness":5},
    "agresivo":     {"rentabilidad":8,"alpha":7,"rentab_kp":7,"sharpe":6,"sortino":5,"max_drawdown":5,"corr_media":5,"div_geo":5,"volatilidad":4,"tracking_error":4,"cv":4,"skewness":4,"var_95":3,"cvar_95":3,"beta":3},
    "muy_agresivo": {"rentabilidad":9,"rentab_kp":9,"alpha":8,"sharpe":4,"div_geo":4,"sortino":3,"max_drawdown":3,"corr_media":3,"volatilidad":2,"tracking_error":2,"cv":2,"skewness":2,"var_95":1,"cvar_95":1,"beta":1},
    "dividendos":   {"sortino":8,"var_95":8,"max_drawdown":8,"sharpe":7,"volatilidad":7,"cvar_95":7,"beta":7,"cv":6,"corr_media":6,"tracking_error":5,"rentab_kp":5,"skewness":5,"div_geo":5,"rentabilidad":4,"alpha":4},
    "tecnologico":  {"rentabilidad":8,"alpha":8,"rentab_kp":7,"sharpe":6,"sortino":5,"max_drawdown":5,"cv":4,"corr_media":4,"volatilidad":3,"var_95":3,"tracking_error":3,"skewness":3,"div_geo":3,"cvar_95":2,"beta":2},
    "esg":          {"sharpe":7,"sortino":7,"var_95":7,"max_drawdown":7,"corr_media":7,"div_geo":7,"volatilidad":6,"cvar_95":6,"alpha":5,"beta":5,"tracking_error":5,"rentab_kp":5,"cv":5,"skewness":5,"rentabilidad":4},
}

RI_TABLE = {1:0.00,2:0.00,3:0.58,4:0.90,5:1.12,6:1.24,7:1.32,8:1.41,9:1.45,10:1.49,11:1.51,12:1.54,13:1.56,14:1.57,15:1.59}

PROFILE_FULL_DESC = {
    "conservador":  ("Conservador",  "Prioriza la preservacion del capital. Acepta rentabilidades modestas a cambio de minima volatilidad. Horizonte corto-medio, muy baja tolerancia al riesgo. Adecuado para inversores cercanos a la jubilacion o con necesidad de liquidez inmediata."),
    "moderado":     ("Moderado",     "Busca equilibrio entre crecimiento y seguridad. Acepta cierta volatilidad a cambio de una rentabilidad razonable. Horizonte medio (5-10 anos). Es el perfil mas habitual entre inversores particulares con experiencia basica."),
    "agresivo":     ("Agresivo",     "Prioriza la rentabilidad sobre la seguridad. Tolera drawdowns significativos y alta volatilidad con el objetivo de maximizar el crecimiento del capital a largo plazo (>10 anos). Para inversores con experiencia y sin necesidad de liquidez a corto plazo."),
    "muy_agresivo": ("Muy Agresivo", "Maximiza el retorno sin restricciones de riesgo. Acepta perdidas temporales muy elevadas. Para inversores con amplia experiencia, capital disponible a largo plazo y perfil psicologico que tolera alta incertidumbre."),
    "dividendos":   ("Dividendos",   "Busca ingresos periodicos mediante empresas con historial solido de pagos de dividendos. Preferencia por large caps estables. Objetivo: flujo de caja constante con baja volatilidad del principal."),
    "tecnologico":  ("Tecnologico",  "Concentrado en sectores de innovacion: tecnologia, semiconductores, software y telecomunicaciones. Alto potencial de crecimiento con mayor volatilidad. Para inversores que creen en la transformacion digital."),
    "esg":          ("ESG",          "Invierte segun criterios medioambientales, sociales y de gobernanza (Environmental, Social, Governance). Combina rentabilidad con impacto positivo. Selecciona empresas con buenas practicas sostenibles."),
}

SAATY_SCALE = [
    (1, "Igual importancia",             "Los dos criterios contribuyen de forma identica al objetivo"),
    (2, "Debilmente superior",           "Leve preferencia por uno sobre el otro"),
    (3, "Moderadamente mas importante",  "Experiencia y juicio favorecen un criterio sobre el otro"),
    (4, "Moderado-fuerte",               "Entre moderado y fuerte"),
    (5, "Fuertemente mas importante",    "Un criterio claramente favorecido; dominante en la practica"),
    (6, "Fuerte-muy fuerte",             "Entre fuerte y muy fuerte"),
    (7, "Muy fuertemente mas importante","Un criterio domina con amplia ventaja"),
    (8, "Extremo-muy fuerte",            "Entre muy fuerte y extremo"),
    (9, "Extremadamente mas importante", "La diferencia es del mayor orden de magnitud posible"),
]

PROFILE_ORDER = ["conservador","moderado","agresivo","muy_agresivo","dividendos","tecnologico","esg"]


def _weight_to_hml(w):
    if w <= 3: return "B"
    if w <= 6: return "M"
    return "A"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_news(tickers: list, max_per: int = 3) -> dict:
    result = {}
    for ticker in tickers[:7]:
        try:
            import yfinance as yf
            t = yf.Ticker(ticker)
            news = t.news or []
            items = []
            for n in news[:max_per]:
                ts = n.get("providerPublishTime", 0)
                date_str = datetime.fromtimestamp(ts).strftime("%d/%m/%Y") if ts else "-"
                title = n.get("title", "")
                if title:
                    items.append({"title": title, "publisher": n.get("publisher", "-"), "date": date_str})
            if items:
                result[ticker] = items
            time.sleep(0.25)
        except Exception:
            pass
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _build_word_report(data: dict, answers: dict) -> str:
    import numpy as np
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = Document()
    sec = doc.sections[0]
    sec.page_width    = Inches(8.27)
    sec.page_height   = Inches(11.69)
    sec.left_margin   = Inches(0.9)
    sec.right_margin  = Inches(0.9)
    sec.top_margin    = Inches(0.85)
    sec.bottom_margin = Inches(0.85)
    sec.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after  = Pt(2)

    # ── Colour palette ──────────────────────────────────────────────────────
    DARK  = RGBColor(0x1A, 0x1A, 0x2E)
    BLUE  = RGBColor(0x16, 0x5F, 0xA8)
    GOLD  = RGBColor(0xD4, 0xAF, 0x37)
    GRAY  = RGBColor(0x6C, 0x75, 0x7D)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    GREEN = RGBColor(0x1A, 0x6A, 0x3E)
    RED   = RGBColor(0xB0, 0x30, 0x20)
    LBLUE = RGBColor(0x9B, 0xC4, 0xE8)

    P_CLR_MAP = {
        "conservador":  RGBColor(0x1A, 0x56, 0x9A),
        "moderado":     RGBColor(0x1A, 0x6A, 0x3E),
        "agresivo":     RGBColor(0xBF, 0x60, 0x00),
        "muy_agresivo": RGBColor(0xB0, 0x20, 0x20),
        "dividendos":   RGBColor(0x5B, 0x2D, 0x8E),
        "tecnologico":  RGBColor(0x06, 0x7B, 0x8C),
        "esg":          RGBColor(0x0F, 0x6B, 0x41),
    }

    # ── Data extraction ──────────────────────────────────────────────────────
    profile      = data.get("profile", "moderado")
    P_CLR        = P_CLR_MAP.get(profile, BLUE)
    P_HEX        = f"{P_CLR.red:02X}{P_CLR.green:02X}{P_CLR.blue:02X}"
    plabel, pdesc = PROFILE_FULL_DESC.get(profile, (profile.capitalize(), ""))
    winner       = data.get("winner", {})
    allocation   = data.get("allocation", [])
    ranking      = data.get("ranking", [])
    portfolios   = data.get("portfolios", [])
    stocks       = data.get("stocks", [])
    scores       = data.get("scores", {})
    n_analyzed   = data.get("n_stocks_analyzed", 0)
    n_selected   = data.get("n_stocks_selected", 0)
    cr_val       = data.get("consistency_ratio", 0.0)
    is_synthetic = data.get("is_synthetic", True)
    today        = datetime.now().strftime("%d de %B de %Y")
    winner_port  = next((pp for pp in portfolios if pp.get("name") == winner.get("name")), {})
    pweights     = ALL_PROFILE_WEIGHTS.get(profile, {k: 5 for k in CRITERIA_ORDER})
    sorted_crit  = sorted(CRITERIA_ORDER, key=lambda k: -pweights.get(k, 0))
    w_vec        = [pweights.get(k, 0) for k in CRITERIA_ORDER]
    total_w      = sum(w_vec) or 1
    pv_vec       = [w / total_w for w in w_vec]

    # ── XML / formatting helpers ─────────────────────────────────────────────
    def _shd(cell, hex6):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), hex6)
        shd.set(qn("w:val"), "clear")
        tcPr.append(shd)

    def _cell_mar(cell, top=40, bot=40, left=80, right=80):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        tcMar = OxmlElement("w:tcMar")
        for side, v in [("top", top), ("bottom", bot), ("start", left), ("end", right)]:
            m = OxmlElement(f"w:{side}")
            m.set(qn("w:w"), str(v))
            m.set(qn("w:type"), "dxa")
            tcMar.append(m)
        tcPr.append(tcMar)

    def _valign(cell, val="center"):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        va = OxmlElement("w:vAlign")
        va.set(qn("w:val"), val)
        tcPr.append(va)

    def _row_height(row, twips, rule="atLeast"):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        h = OxmlElement("w:trHeight")
        h.set(qn("w:val"), str(twips))
        h.set(qn("w:hRule"), rule)
        trPr.append(h)

    def _no_borders(table):
        tbl = table._tbl
        tblPr = tbl.tblPr
        if tblPr is None:
            tblPr = OxmlElement("w:tblPr")
            tbl.insert(0, tblPr)
        bdr = OxmlElement("w:tblBorders")
        for s in ["top","left","bottom","right","insideH","insideV"]:
            b = OxmlElement(f"w:{s}")
            b.set(qn("w:val"), "none")
            bdr.append(b)
        tblPr.append(bdr)

    def _pborder(para, side="bottom", color="165FA8", sz="4"):
        pPr = para._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), sz)
        b.set(qn("w:space"), "1")
        b.set(qn("w:color"), color)
        pBdr.append(b)
        pPr.append(pBdr)

    def _tight(para, before=0, after=2):
        para.paragraph_format.space_before = Pt(before)
        para.paragraph_format.space_after  = Pt(after)

    def _run(para, text, sz=10, bold=False, italic=False, clr=None):
        r = para.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(sz)
        r.font.bold = bold
        r.font.italic = italic
        if clr:
            r.font.color.rgb = clr
        return r

    def _cell_para(cell, text, sz=8.5, bold=False, clr=None, center=False, bg=None):
        for pp in cell.paragraphs:
            pp.clear()
        p = cell.paragraphs[0]
        _tight(p, 0, 0)
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(sz)
        r.font.bold = bold
        if clr:
            r.font.color.rgb = clr
        if bg:
            _shd(cell, bg)
        _cell_mar(cell)

    # ── Document-level helpers ───────────────────────────────────────────────
    def h1(text, color=BLUE, new_page=False):
        p = doc.add_paragraph()
        if new_page:
            p.paragraph_format.page_break_before = True
            _tight(p, 6, 4)
        else:
            _tight(p, 16, 4)
        p.paragraph_format.keep_with_next = True
        _run(p, text, sz=14, bold=True, clr=color)
        _pborder(p)
        return p

    def h2(text, color=DARK):
        p = doc.add_paragraph()
        _tight(p, 9, 2)
        p.paragraph_format.keep_with_next = True
        _run(p, text, sz=11, bold=True, clr=color)
        return p

    def h3(text, color=GRAY):
        p = doc.add_paragraph()
        _tight(p, 6, 1)
        p.paragraph_format.keep_with_next = True
        _run(p, text, sz=10, bold=True, clr=color)
        return p

    def body(text, bold=False, italic=False, size=10, color=None, align=None):
        p = doc.add_paragraph()
        _tight(p, 0, 3)
        _run(p, text, sz=size, bold=bold, italic=italic, clr=color)
        if align:
            p.alignment = align
        return p

    def bullet(text, size=9.5):
        p = doc.add_paragraph(style="List Bullet")
        _tight(p, 0, 1)
        _run(p, text, sz=size)

    def fmt_pct(v): return f"{v:+.2f}%" if v != 0 else "0.00%"
    def fmt_n(v):   return f"{v:.3f}"
    def bar(val, mx=9, w=10):
        f = max(0, int(round(val / mx * w))) if mx else 0
        return "█" * f + "░" * (w - f)

    # ── Table helpers ────────────────────────────────────────────────────────
    def thead(table, cols, bg="165FA8"):
        row = table.rows[0]
        for i, txt in enumerate(cols[:len(row.cells)]):
            c = row.cells[i]
            _cell_para(c, txt, sz=8, bold=True, clr=WHITE, center=True, bg=bg)

    def trow(row, vals, alt=False, center=False, bold=False, sz=8.5, color=None, hl=None):
        for i, v in enumerate(vals[:len(row.cells)]):
            c = row.cells[i]
            for pp in c.paragraphs:
                pp.clear()
            p = c.paragraphs[0]
            _tight(p, 0, 0)
            if center:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(v))
            r.font.name = "Calibri"
            r.font.size = Pt(sz)
            r.font.bold = bold
            if color:
                r.font.color.rgb = color
            if hl:
                _shd(c, hl)
            elif alt:
                _shd(c, "EBF2FA")
            _cell_mar(c)

    # ── Page footer (page numbers) ───────────────────────────────────────────
    footer = sec.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(fp, 3, 0)
    _run(fp, "- ", sz=8, clr=GRAY)
    fr = fp.add_run()
    fr.font.size = Pt(8)
    fr.font.color.rgb = GRAY
    for el_type, txt in [("begin", None), ("instrText", "PAGE"), ("end", None)]:
        if el_type == "instrText":
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), el_type)
        fr._r.append(el)
    _run(fp, " -", sz=8, clr=GRAY)

    # ── Page header (all pages except cover) ─────────────────────────────────
    hdr = sec.header
    hp = hdr.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _tight(hp, 0, 3)
    _run(hp, f"AHP Portfolio Selector  ·  Informe de Analisis  ·  Perfil: {plabel}", sz=7.5, clr=GRAY)
    _pborder(hp, side="bottom", color="DDDDDD", sz="2")

    # ═══════════════════════════════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════════════════════════════
    # Dark header band
    ct = doc.add_table(rows=1, cols=1)
    _no_borders(ct)
    cc = ct.rows[0].cells[0]
    _shd(cc, "1A1A2E")
    _cell_mar(cc, top=280, bot=260, left=200, right=200)
    _valign(cc, "center")
    _row_height(ct.rows[0], 2200)

    p0 = cc.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(p0, 0, 6)
    _run(p0, "INFORME DE ANALISIS DE INVERSION", sz=22, bold=True, clr=WHITE)

    p1 = cc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(p1, 0, 3)
    _run(p1, "Proceso Analitico Jerarquico (AHP)", sz=12, clr=LBLUE)

    p2 = cc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(p2, 0, 0)
    _run(p2, "Optimizacion de Portafolios de Markowitz", sz=10, clr=RGBColor(0x7A, 0xA0, 0xC8))

    # Profile block
    pb = doc.add_paragraph()
    pb.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pb, 28, 4)
    _run(pb, "PERFIL DEL INVERSOR", sz=9, clr=GRAY)

    pp2 = doc.add_paragraph()
    pp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pp2, 0, 16)
    _run(pp2, plabel.upper(), sz=30, bold=True, clr=P_CLR)

    pp3 = doc.add_paragraph()
    pp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pp3, 0, 4)
    _run(pp3, "CARTERA SELECCIONADA", sz=9, clr=GRAY)

    pp4 = doc.add_paragraph()
    pp4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _tight(pp4, 0, 4)
    _run(pp4, f"{winner.get('name','--')}   ·   Score AHP: {winner.get('score',0):.1f}%", sz=16, bold=True, clr=GOLD)

    # Separator rule
    sep = doc.add_paragraph()
    _tight(sep, 22, 10)
    _pborder(sep, side="bottom", color=P_HEX, sz="6")

    # Metadata
    meta_lines = [
        (f"Generado: {today}", 9, False),
        (f"Fuente de datos: {'Yahoo Finance - Precios de mercado reales' if not is_synthetic else 'Simulacion Monte Carlo calibrada'}", 8.5, True),
        ("AHP Portfolio Selector  ·  TFG 2025", 8.5, False),
        ("Este documento tiene caracter informativo y no constituye asesoramiento financiero regulado.", 7.5, True),
    ]
    for line, sz, it in meta_lines:
        mp = doc.add_paragraph()
        mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _tight(mp, 0, 2)
        _run(mp, line, sz=sz, italic=it, clr=GRAY)

    doc.add_page_break()

    # ═══════════════════════════════════════════════════════════════════════════
    # RESUMEN EJECUTIVO
    # ═══════════════════════════════════════════════════════════════════════════
    h1("RESUMEN EJECUTIVO")
    body(
        f"El presente informe documenta la construccion y seleccion de la cartera optima para un inversor "
        f"con perfil {plabel.upper()} mediante el Proceso Analitico Jerarquico (AHP) de Saaty (1990) combinado "
        f"con la teoria moderna de portafolios de Markowitz (1952). Se analizaron {n_analyzed} acciones de "
        f"tres indices internacionales, de las que {n_selected} superaron los filtros cuantitativos del perfil. "
        f"Los portafolios candidatos fueron evaluados frente a 15 indicadores financieros en 5 categorias "
        f"(Ratio de Consistencia CR = {cr_val} {'- Consistente' if cr_val < 0.10 else '- Revisar'})."
    )
    if winner_port:
        tbl = doc.add_table(rows=2, cols=6)
        tbl.style = "Table Grid"
        thead(tbl, ["Rentab. Anual", "Volatilidad", "Sharpe", "Max Drawdown", "Beta", "Alpha"])
        trow(tbl.rows[1], [
            fmt_pct(winner_port.get("rentabilidad", 0)),
            f"{winner_port.get('volatilidad',0):.2f}%",
            fmt_n(winner_port.get("sharpe", 0)),
            fmt_pct(winner_port.get("max_drawdown", 0)),
            fmt_n(winner_port.get("beta", 0)),
            fmt_pct(winner_port.get("alpha", 0)),
        ], center=True, bold=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # S1. UNIVERSO DE INVERSION
    # ═══════════════════════════════════════════════════════════════════════════
    h1("1.  UNIVERSO DE INVERSION - LOS TRES INDICES GLOBALES")
    h2("1.1  Justificacion de los Indices Seleccionados")
    body(
        "El universo esta formado por los tres indices bursatiles mas representativos en terminos de "
        "capitalizacion, liquidez y cobertura geografica. En conjunto representan el 60-65% de la "
        "capitalizacion bursatil mundial, tres divisas principales (USD, EUR, JPY) y tres ciclos "
        "economicos con baja correlacion historica entre si."
    )
    tbl = doc.add_table(rows=4, cols=5)
    tbl.style = "Table Grid"
    thead(tbl, ["Indice", "Region / Divisa", "Composicion", "Cap. aprox.", "Por que se incluye"])
    for i, row_data in enumerate([
        ("S&P 500",        "EE.UU. / USD", "500 mayores empresas USA",             "~40 B USD", "Mayor mercado del mundo; alta liquidez, referencia global de renta variable"),
        ("Euro Stoxx 600", "Europa / EUR", "600 principales de 17 paises europeos","~12 B EUR", "Diversificacion frente al ciclo USA; exposicion al euro y a distintos sectores"),
        ("Nikkei 225",     "Japon / JPY",  "225 blue chips cotizados en Tokio",    "~4 B JPY",  "Tercera economia mundial; baja correlacion con Occidente; ciclo asiatico"),
    ]):
        trow(tbl.rows[i+1], row_data, alt=(i%2==0), sz=8.5)

    h2("1.2  Metodologia de Muestreo")
    body(
        f"Los tres indices suman mas de 700 valores. Se aplica una muestra representativa: los 25 tickers "
        f"de mayor liquidez por indice (75 en total). Se descarta cualquier serie con mas del 20% de "
        f"datos ausentes. Resultado: {n_analyzed} acciones analizadas, {n_selected} seleccionadas."
    )
    body(
        "Consistente con Escobar (2015): una muestra de 60-80 valores es suficiente para capturar la frontera eficiente de Markowitz.",
        italic=True, size=9, color=GRAY
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # S2. METODOLOGIA AHP
    # ═══════════════════════════════════════════════════════════════════════════
    h1("2.  METODOLOGIA AHP - FUNDAMENTOS TEORICOS", new_page=True)
    h2("2.1  Que es el Proceso Analitico Jerarquico")
    body(
        "El Proceso Analitico Jerarquico (AHP) fue desarrollado por Thomas L. Saaty en 1977 y formalizado "
        "en The Analytic Hierarchy Process (1980, 1990). Es el metodo de decision multicriterio mas citado "
        "en la literatura academica de gestion y finanzas. Descompone una decision compleja en una jerarquia: "
        "objetivo -> criterios -> alternativas."
    )
    body(
        f"En este proyecto: (1) Objetivo: seleccionar la cartera optima para el perfil {plabel}. "
        "(2) Criterios: 15 indicadores financieros en 5 categorias. "
        "(3) Alternativas: portafolios candidatos construidos con Markowitz."
    )

    h2("2.2  Proceso de Cinco Pasos")
    for i, step in enumerate([
        "Definir la jerarquia: objetivo, criterios y alternativas.",
        "Construir la matriz de comparacion por pares (15x15) usando la escala de Saaty (1-9).",
        "Calcular el vector de prioridades (eigenvector principal normalizado).",
        f"Verificar consistencia con el Ratio de Consistencia (CR). Si CR < 0.10, la matriz es aceptable (CR actual = {cr_val}).",
        "Puntuar las alternativas: multiplicar los valores normalizados por los pesos AHP y sumar.",
    ], 1):
        bullet(f"Paso {i}: {step}")

    h2("2.3  Escala de Saaty (1-9)")
    tbl = doc.add_table(rows=len(SAATY_SCALE)+1, cols=3)
    tbl.style = "Table Grid"
    thead(tbl, ["Valor", "Intensidad", "Interpretacion"])
    for i, (val, intens, interp) in enumerate(SAATY_SCALE):
        trow(tbl.rows[i+1], [str(val), intens, interp], alt=(i%2==0), sz=8.5)

    h2("2.4  Ratio de Consistencia (CR)")
    for line in [
        "lambda_max: autovalor principal de la matriz de comparacion.",
        "IC (Indice de Consistencia) = (lambda_max - n) / (n - 1), donde n = numero de criterios.",
        "IC_A (Indice de Consistencia Aleatorio): valor esperado para una matriz aleatoria del mismo tamano.",
        "CR = IC / IC_A.  Si CR < 0.10, la matriz se considera suficientemente consistente.",
    ]:
        bullet(line)
    body("Valores de IC_A segun Saaty para n = 1 a 15:")
    tbl = doc.add_table(rows=2, cols=15)
    tbl.style = "Table Grid"
    thead(tbl, [str(i) for i in range(1, 16)], bg="444444")
    trow(tbl.rows[1], [f"{RI_TABLE.get(i,0):.2f}" for i in range(1, 16)], center=True, sz=8)

    h2("2.5  Sintesis Final")
    body("Una vez calculados los pesos p de los criterios, cada portafolio P_i recibe una puntuacion global:")
    fp2 = doc.add_paragraph()
    _tight(fp2, 4, 4)
    fp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp2.add_run("Score(P_i) = SUM_j  p_j x N_ij")
    r.font.name = "Courier New"; r.font.size = Pt(12); r.font.bold = True; r.font.color.rgb = BLUE
    body("N_ij es el valor normalizado del criterio j para el portafolio i (0 = peor, 1 = mejor candidato).")

    # ═══════════════════════════════════════════════════════════════════════════
    # S3. LOS 7 PERFILES
    # ═══════════════════════════════════════════════════════════════════════════
    h1("3.  LOS 7 PERFILES DE INVERSION", new_page=True)
    body(
        "El cuestionario de 15 preguntas (5 dimensiones: tolerancia al riesgo, horizonte temporal, "
        "situacion financiera, perfil psicologico y conocimiento financiero) determina cual de los "
        "7 perfiles describe mejor al inversor. Cada perfil tiene pesos AHP distintos."
    )
    for pkey in PROFILE_ORDER:
        plbl, pds = PROFILE_FULL_DESC.get(pkey, (pkey, ""))
        pw = ALL_PROFILE_WEIGHTS.get(pkey, {})
        top3 = sorted(pw.items(), key=lambda x: -x[1])[:3]
        bot3 = sorted(pw.items(), key=lambda x:  x[1])[:3]
        is_cur = (pkey == profile)
        prefix = "> (PERFIL ASIGNADO)  " if is_cur else ""
        h3(f"{prefix}{plbl.upper()}", color=P_CLR if is_cur else DARK)
        body(pds, size=9.5)
        body(
            "Mayor peso: " + ", ".join(f"{CRITERIA_META[k]['label']} ({v}/9)" for k, v in top3) +
            "   |   Menor peso: " + ", ".join(f"{CRITERIA_META[k]['label']} ({v}/9)" for k, v in bot3),
            size=8.5, color=GRAY, italic=True
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # S4. LOS 15 INDICADORES
    # ═══════════════════════════════════════════════════════════════════════════
    h1("4.  LOS 15 INDICADORES FINANCIEROS", new_page=True)
    h2("4.1  Descripcion de cada Indicador")
    body("Los 15 indicadores se agrupan en 5 categorias. Formulacion matematica, descripcion y objetivo de optimizacion.")
    tbl = doc.add_table(rows=16, cols=5)
    tbl.style = "Table Grid"
    thead(tbl, ["#", "Indicador", "Formula", "Que mide", "Obj."])
    for i, k in enumerate(CRITERIA_ORDER):
        m = CRITERIA_META[k]
        trow(tbl.rows[i+1], [str(i+1), f"[{m['cat']}]  {m['label']}", m["formula"], m["desc"], ""], alt=(i%2==0), sz=8)
        obj_cell = tbl.rows[i+1].cells[4]
        _cell_para(obj_cell, "MAX" if m["dir"]=="maximize" else "MIN",
                   sz=8, bold=True, clr=GREEN if m["dir"]=="maximize" else RED, center=True)

    h2("4.2  Relacion Indicador - Perfil  (A = peso 7-9  /  M = 4-6  /  B = 1-3)")
    body("Intensidad del peso Saaty de cada indicador segun el perfil. Columna del perfil asignado resaltada.", size=9, color=GRAY)
    col_labels = ["Indicador"] + [PROFILE_FULL_DESC[p][0] for p in PROFILE_ORDER]
    tbl = doc.add_table(rows=16, cols=8)
    tbl.style = "Table Grid"
    thead(tbl, col_labels, bg="1A1A2E")
    for i, k in enumerate(CRITERIA_ORDER):
        cells_data = [CRITERIA_META[k]["label"]] + [
            _weight_to_hml(ALL_PROFILE_WEIGHTS.get(pkey, {}).get(k, 0)) for pkey in PROFILE_ORDER
        ]
        trow(tbl.rows[i+1], cells_data, alt=(i%2==0), sz=8.5, center=True)
        try:
            ci = PROFILE_ORDER.index(profile) + 1
            _cell_para(tbl.rows[i+1].cells[ci], cells_data[ci], sz=8.5, bold=True, clr=WHITE, center=True, bg=P_HEX)
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════════════════════════
    # S5. PERFIL ASIGNADO
    # ═══════════════════════════════════════════════════════════════════════════
    h1(f"5.  PERFIL ASIGNADO: {plabel.upper()}")
    body(pdesc)

    if scores:
        h2("5.1  Puntuaciones del Cuestionario por Perfil")
        body("Afinidad del inversor con cada perfil segun las respuestas (0-50 pts):")
        sorted_sc = sorted(scores.items(), key=lambda x: -x[1])
        tbl = doc.add_table(rows=len(sorted_sc)+1, cols=3)
        tbl.style = "Table Grid"
        thead(tbl, ["Perfil", "Puntuacion", "Barra"])
        for i, (pn, ps) in enumerate(sorted_sc):
            lbl = PROFILE_FULL_DESC.get(pn, (pn.capitalize(), ""))[0]
            trow(tbl.rows[i+1], [lbl, f"{ps} / 50 pts", bar(ps, 50, 16)], alt=(i%2==0), center=True, sz=9)

    h2("5.2  Implicaciones en el Analisis AHP")
    top5 = sorted(pweights.items(), key=lambda x: -x[1])[:5]
    bot5 = sorted(pweights.items(), key=lambda x:  x[1])[:5]
    body(
        "Criterios de mayor peso: " + ", ".join(f"{CRITERIA_META[k]['label']} ({v}/9)" for k,v in top5) + ". "
        "Criterios de menor prioridad: " + ", ".join(f"{CRITERIA_META[k]['label']} ({v}/9)" for k,v in bot5) + "."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # S6. FILTRADO DE ACCIONES
    # ═══════════════════════════════════════════════════════════════════════════
    h1("6.  FILTRADO Y SELECCION DE ACCIONES")
    h2("6.1  Criterios de Pre-filtrado por Perfil")
    body(
        f"Antes del AHP se aplica un filtro cuantitativo para eliminar acciones incompatibles con el "
        f"perfil {plabel.upper()}. Aplicado sobre las {n_analyzed} acciones de la muestra:"
    )
    FILTERS = {
        "conservador":  [("Capitalizacion minima","$10.000 M","Alta liquidez y estabilidad"),("Volumen medio diario","> 1.000.000","Liquidez para entrar/salir sin mover el precio"),("Rentabilidad","Positiva","No se invierte en empresas con perdidas")],
        "moderado":     [("Capitalizacion minima","$5.000 M","Balance liquidez-crecimiento"),("Volumen medio diario","> 750.000","Liquidez para horizonte medio"),("Rentabilidad","Positiva","Criterio basico de viabilidad")],
        "agresivo":     [("Capitalizacion minima","$2.000 M","Incluye mid-caps de mayor potencial"),("Volumen medio diario","> 500.000","Liquidez minima aceptable"),("Rentabilidad","Positiva","Criterio basico de viabilidad")],
        "muy_agresivo": [("Capitalizacion minima","$1.000 M","Universo amplio para maximizar upside"),("Volumen medio diario","> 300.000","Liquidez minima")],
        "dividendos":   [("Capitalizacion minima","$8.000 M","Large caps con historial de dividendos"),("Volumen medio diario","> 800.000","Alta liquidez"),("Rentabilidad","Positiva","Empresas con beneficios para distribuir")],
        "tecnologico":  [("Capitalizacion minima","$3.000 M","Incluye tecnologicas en crecimiento"),("Volumen medio diario","> 600.000","Liquidez minima")],
        "esg":          [("Capitalizacion minima","$5.000 M","Empresas con reporting ESG"),("Volumen medio diario","> 600.000","Liquidez adecuada")],
    }
    fdata = FILTERS.get(profile, [])
    if fdata:
        tbl = doc.add_table(rows=len(fdata)+1, cols=3)
        tbl.style = "Table Grid"
        thead(tbl, ["Filtro", f"Umbral ({plabel})", "Justificacion"])
        for i, r in enumerate(fdata):
            trow(tbl.rows[i+1], r, alt=(i%2==0), sz=9)

    if stocks:
        h2("6.2  Acciones Seleccionadas")
        body(f"{n_selected} acciones superaron los filtros. Periodo de analisis: 2 anos de precios ajustados.")
        tbl = doc.add_table(rows=len(stocks)+1, cols=5)
        tbl.style = "Table Grid"
        thead(tbl, ["Ticker", "Rentab. Anual", "Sharpe", "Volatilidad", "Beta"])
        for i, s in enumerate(stocks):
            trow(tbl.rows[i+1], [
                s.get("ticker",""), fmt_pct(s.get("rentabilidad",0)),
                fmt_n(s.get("sharpe",0)), f"{s.get('volatilidad',0):.2f}%",
                fmt_n(s.get("beta",0)),
            ], alt=(i%2==0), center=True, sz=9)

    # ═══════════════════════════════════════════════════════════════════════════
    # S7. MARKOWITZ
    # ═══════════════════════════════════════════════════════════════════════════
    h1("7.  CONSTRUCCION DE PORTAFOLIOS - OPTIMIZACION DE MARKOWITZ")
    h2("7.1  Metodologia de Optimizacion")
    body(
        "Sobre las acciones seleccionadas se aplica la teoria moderna de portafolios de Markowitz (1952). "
        "Se resuelven cuatro problemas de optimizacion para generar los portafolios candidatos:"
    )
    for pt in [
        "Maximo Sharpe: max [(E(Rp) - Rf)] / sigma(Rp)  sujeto a: Swi = 1, wi >= 0",
        "Minima Varianza: min sigma^2(Rp) = w^T * Sigma * w  sujeto a: Swi = 1, wi >= 0",
        "Maxima Rentabilidad: max E(Rp)  sujeto a: Swi = 1, wi >= 0",
        "Equal Weight (benchmark): wi = 1/n para todos los activos",
    ]:
        bullet(pt)
    body(
        "La matriz de covarianzas Sigma se calcula sobre retornos logaritmicos diarios del periodo de analisis. "
        "El vector de retornos esperados mu es la media historica de cada activo."
    )
    if portfolios:
        h2("7.2  Portafolios Candidatos Generados")
        tbl = doc.add_table(rows=len(portfolios)+1, cols=7)
        tbl.style = "Table Grid"
        thead(tbl, ["Portafolio", "Rentab.", "Volatil.", "Sharpe", "Max DD", "Beta", "Alpha"])
        for i, pp in enumerate(portfolios):
            trow(tbl.rows[i+1], [
                pp.get("name",""), fmt_pct(pp.get("rentabilidad",0)),
                f"{pp.get('volatilidad',0):.2f}%", fmt_n(pp.get("sharpe",0)),
                fmt_pct(pp.get("max_drawdown",0)), fmt_n(pp.get("beta",0)),
                fmt_pct(pp.get("alpha",0)),
            ], alt=(i%2==0), center=True, sz=9)

    # ═══════════════════════════════════════════════════════════════════════════
    # S8. AHP PASO A PASO
    # ═══════════════════════════════════════════════════════════════════════════
    h1("8.  ANALISIS AHP PASO A PASO - DATOS NUMERICOS COMPLETOS", new_page=True)
    body(
        "Esta seccion expone todos los datos numericos del analisis AHP tal como se ejecutaron: "
        "vector de pesos de Saaty, vector de prioridades, matriz de comparacion por pares, "
        "verificacion de consistencia y matriz de puntuacion de portafolios."
    )

    h2(f"8.1  Pesos de Saaty - Perfil {plabel}  (escala 1-9,  Sw = {total_w})")
    tbl = doc.add_table(rows=len(CRITERIA_ORDER)+2, cols=6)
    tbl.style = "Table Grid"
    thead(tbl, ["#", "Indicador", "Categoria", "Peso (w)", "Barra", "Objetivo"])
    for i, k in enumerate(CRITERIA_ORDER):
        m = CRITERIA_META[k]
        w_k = pweights.get(k, 0)
        trow(tbl.rows[i+1], [str(i+1), m["label"], m["cat"], str(w_k), bar(w_k, 9, 10), ""], alt=(i%2==0), sz=8.5, center=True)
        _cell_para(tbl.rows[i+1].cells[5], "MAX" if m["dir"]=="maximize" else "MIN",
                   sz=8.5, bold=True, clr=GREEN if m["dir"]=="maximize" else RED, center=True)
    trow(tbl.rows[-1], ["", "TOTAL", "", str(total_w), "", ""], bold=True, center=True, sz=9, hl="D4E8F8")

    h2("8.2  Vector de Prioridades  (p_i = w_i / Sw,  Sp = 1.000)")
    body("Normaliza los pesos a escala 0-1. Representa la fraccion de importancia de cada criterio en la decision.")
    tbl = doc.add_table(rows=len(CRITERIA_ORDER)+1, cols=4)
    tbl.style = "Table Grid"
    thead(tbl, ["Indicador", "w_i", "p_i = w_i / Sw", "p_i (%)"])
    for i, k in enumerate(CRITERIA_ORDER):
        w_k = pweights.get(k, 0)
        p_k = w_k / total_w
        trow(tbl.rows[i+1], [CRITERIA_META[k]["label"], str(w_k), f"{p_k:.5f}", f"{p_k*100:.2f}%"], alt=(i%2==0), sz=9)

    h2("8.3  Matriz de Comparacion por Pares - Extracto 6 Criterios Principales")
    body("A[i,j] = w_i / w_j  ->  >1 (fila domina, verde)  /  =1 (igual, diagonal azul)  /  <1 (columna domina, rojo)")
    top6_keys   = sorted_crit[:6]
    top6_labels = [CRITERIA_META[k]["label"].split("(")[0].strip()[:18] for k in top6_keys]
    top6_w      = [pweights.get(k, 1) for k in top6_keys]
    n6 = len(top6_keys)
    tbl = doc.add_table(rows=n6+1, cols=n6+1)
    tbl.style = "Table Grid"
    _cell_para(tbl.rows[0].cells[0], "", bg="165FA8")
    for j, lbl in enumerate(top6_labels):
        _cell_para(tbl.rows[0].cells[j+1], lbl, sz=7.5, bold=True, clr=WHITE, center=True, bg="165FA8")
    for i in range(n6):
        row = tbl.rows[i+1]
        _cell_para(row.cells[0], top6_labels[i], sz=7.5, bold=True, bg="E8EFF8")
        for j in range(n6):
            c = row.cells[j+1]
            for pp in c.paragraphs: pp.clear()
            p = c.paragraphs[0]
            _tight(p, 0, 0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ratio = top6_w[i] / top6_w[j] if top6_w[j] > 0 else 1.0
            r = p.add_run(f"{ratio:.3f}")
            r.font.name = "Calibri"; r.font.size = Pt(8)
            if i == j:
                r.font.bold = True
                _shd(c, "D4E8FF")
            elif ratio > 1:
                r.font.color.rgb = GREEN
            else:
                r.font.color.rgb = RED
            _cell_mar(c)

    h2("8.4  Verificacion de Consistencia - lambda_max, IC, IC_A, CR")
    n_crit     = len(CRITERIA_ORDER)
    ri_val     = RI_TABLE.get(n_crit, 1.59)
    lambda_max = float(n_crit)
    ci_val     = (lambda_max - n_crit) / (n_crit - 1) if n_crit > 1 else 0.0
    cr_comp    = ci_val / ri_val if ri_val > 0 else 0.0
    for line in [
        f"n = {n_crit} criterios",
        f"lambda_max = {lambda_max:.4f}  (para una matriz perfectamente consistente lambda_max = n)",
        f"IC = (lambda_max - n) / (n - 1) = ({lambda_max:.1f} - {n_crit}) / ({n_crit} - 1) = {ci_val:.4f}",
        f"IC_A (Saaty, n={n_crit}) = {ri_val:.2f}",
        f"CR = IC / IC_A = {ci_val:.4f} / {ri_val:.2f} = {cr_comp:.4f}",
        f"CR reportado por el motor AHP = {cr_val}  ->  {'Consistente (CR < 0.10)' if cr_val < 0.10 else 'Revisar preferencias'}",
    ]:
        bullet(line)
    body(
        "Los pesos Saaty son directamente proporcionales (A[i,j] = w_i/w_j exacto), por lo que la "
        "consistencia teorica es perfecta (CR -> 0). El CR del motor procede del eigenvector iterativo.",
        italic=True, size=9, color=GRAY
    )

    if portfolios:
        h2("8.5  Normalizacion de Portafolios por Criterio")
        bullet("Criterio a maximizar: N_ij = (v_ij - min_j) / (max_j - min_j)")
        bullet("Criterio a minimizar: N_ij = (max_j - v_ij) / (max_j - min_j)")

        raw  = np.array([[float(pp.get(k, 0) or 0) for k in CRITERIA_ORDER] for pp in portfolios])
        norm = np.zeros_like(raw)
        for j, k in enumerate(CRITERIA_ORDER):
            col = raw[:, j]; cmin, cmax = col.min(), col.max(); rng = cmax - cmin
            if rng < 1e-10:
                norm[:, j] = 1.0
            elif CRITERIA_META[k]["dir"] == "maximize":
                norm[:, j] = (col - cmin) / rng
            else:
                norm[:, j] = (cmax - col) / rng

        pv_arr  = np.array(pv_vec)
        w_scores = norm @ pv_arr
        show_keys   = sorted_crit[:8]
        show_labels = [CRITERIA_META[k]["label"].split("(")[0].strip()[:13] for k in show_keys]
        show_idx    = [CRITERIA_ORDER.index(k) for k in show_keys]

        tbl = doc.add_table(rows=len(portfolios)+1, cols=len(show_keys)+2)
        tbl.style = "Table Grid"
        thead(tbl, ["Portafolio"] + show_labels + ["Score AHP"])
        for i, pp in enumerate(portfolios):
            is_w = (pp.get("name","") == winner.get("name",""))
            vals = [pp.get("name","")] + [f"{norm[i, j_idx]:.3f}" for j_idx in show_idx] + [f"{w_scores[i]*100:.2f}%"]
            trow(tbl.rows[i+1], vals, center=True, sz=8.5, bold=is_w, hl="D4AF37" if is_w else None, alt=(i%2==0 and not is_w))

        h2("8.6  Puntuacion Ponderada Final - Score(P_i) = S p_j x N_ij")
        tbl = doc.add_table(rows=len(portfolios)+1, cols=4)
        tbl.style = "Table Grid"
        thead(tbl, ["Portafolio", "S pj x Nij", "Score AHP (%)", "Ranking"])
        ranked = sorted(enumerate(portfolios), key=lambda x: -w_scores[x[0]])
        for rank, (i, pp) in enumerate(ranked):
            is_w = (pp.get("name","") == winner.get("name",""))
            trow(tbl.rows[rank+1], [
                pp.get("name",""), f"{w_scores[i]:.6f}",
                f"{w_scores[i]*100:.2f}%", f"#{rank+1}",
            ], center=True, sz=9, bold=is_w, hl="D4AF37" if is_w else None)

    # ═══════════════════════════════════════════════════════════════════════════
    # S9. RANKING AHP
    # ═══════════════════════════════════════════════════════════════════════════
    h1("9.  RANKING AHP - SELECCION DEL PORTAFOLIO GANADOR")
    if ranking and portfolios:
        tbl = doc.add_table(rows=len(ranking)+1, cols=7)
        tbl.style = "Table Grid"
        thead(tbl, ["Pos.", "Portafolio", "Score AHP", "Rentab.", "Sharpe", "Volat.", "Max DD"])
        for i, r in enumerate(ranking):
            pt = next((pp for pp in portfolios if pp.get("name") == r.get("name")), {})
            is_w = (i == 0)
            trow(tbl.rows[i+1], [
                f"#{r.get('rank',i+1)}", r.get("name",""), f"{r.get('score',0):.1f}%",
                fmt_pct(pt.get("rentabilidad",0)), fmt_n(pt.get("sharpe",0)),
                f"{pt.get('volatilidad',0):.2f}%", fmt_pct(pt.get("max_drawdown",0)),
            ], center=True, sz=9, bold=is_w, hl="D4AF37" if is_w else None)

    h2("Por que gano este portafolio")
    body(
        f"El portafolio '{winner.get('name','')}' obtuvo la puntuacion AHP mas alta porque maximiza "
        f"los criterios con mayor peso para el perfil {plabel.upper()}."
    )
    if winner_port:
        top2 = sorted(pweights.items(), key=lambda x: -x[1])[:2]
        for k, w in top2:
            val = float(winner_port.get(k, 0) or 0)
            body(
                f"  - {CRITERIA_META[k]['label']} (peso {w}/9): "
                f"{fmt_n(val) if abs(val) < 10 else fmt_pct(val)} - "
                f"{'valor mas favorable entre los candidatos' if CRITERIA_META[k]['dir']=='maximize' else 'valor mas bajo entre los candidatos'}.",
                size=10
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # S10. PORTAFOLIO RECOMENDADO
    # ═══════════════════════════════════════════════════════════════════════════
    h1(f"10.  PORTAFOLIO RECOMENDADO - {winner.get('name','').upper()}")
    sc_line = doc.add_paragraph()
    _tight(sc_line, 0, 6)
    _run(sc_line, f"Score AHP: {winner.get('score',0):.1f}%   ·   Perfil: {plabel}", sz=13, bold=True, clr=GOLD)

    if winner_port:
        h2("10.1  Metricas Financieras Completas (15 indicadores)")
        metrics = [
            ("Rentabilidad Anualizada",    fmt_pct(winner_port.get("rentabilidad",0))),
            ("Volatilidad Anualizada",     f"{winner_port.get('volatilidad',0):.2f}%"),
            ("Ratio de Sharpe",            fmt_n(winner_port.get("sharpe",0))),
            ("Ratio de Sortino",           fmt_n(winner_port.get("sortino",0))),
            ("Alpha de Jensen",            fmt_pct(winner_port.get("alpha",0))),
            ("Max Drawdown",               fmt_pct(winner_port.get("max_drawdown",0))),
            ("Beta",                       fmt_n(winner_port.get("beta",0))),
            ("VaR 95%",                    f"{winner_port.get('var_95',0):.2f}%"),
            ("CVaR 95%",                   f"{winner_port.get('cvar_95',0):.2f}%"),
            ("Tracking Error",             f"{winner_port.get('tracking_error',0):.2f}%"),
            ("Rentab. - Coste Capital",    fmt_pct(winner_port.get("rentab_kp",0))),
            ("Coeficiente de Variacion",   fmt_n(winner_port.get("cv",0))),
            ("Skewness",                   fmt_n(winner_port.get("skewness",0))),
            ("Correlacion Media",          fmt_n(winner_port.get("corr_media",0))),
            ("Diversificacion Geografica", fmt_n(winner_port.get("div_geo",0))),
        ]
        half = (len(metrics) + 1) // 2
        tbl = doc.add_table(rows=half+1, cols=4)
        tbl.style = "Table Grid"
        thead(tbl, ["Metrica", "Valor", "Metrica", "Valor"])
        for ri in range(half):
            row = tbl.rows[ri+1]
            k1, v1 = metrics[ri]
            trow(row, [k1, v1, "", ""], alt=(ri%2==0), sz=9)
            ri2 = ri + half
            if ri2 < len(metrics):
                k2, v2 = metrics[ri2]
                for cc2 in [row.cells[2], row.cells[3]]:
                    for pp in cc2.paragraphs: pp.clear()
                    p = cc2.paragraphs[0]
                    _tight(p, 0, 0)
                    _cell_mar(cc2)
                    if ri % 2 == 0: _shd(cc2, "EBF2FA")
                row.cells[2].paragraphs[0].add_run(k2).font.size = Pt(9)
                row.cells[2].paragraphs[0].runs[0].font.name = "Calibri"
                vr = row.cells[3].paragraphs[0].add_run(v2)
                vr.font.size = Pt(9); vr.font.bold = True; vr.font.name = "Calibri"
                row.cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    if allocation:
        h2("10.2  Composicion y Asignacion de Capital")
        body("Porcentajes resultado de la optimizacion de maximo Sharpe de Markowitz.")
        tbl = doc.add_table(rows=len(allocation)+1, cols=5)
        tbl.style = "Table Grid"
        thead(tbl, ["Empresa (Ticker)", "% Capital", "Barra", "Sharpe Indiv.", "Rol"])
        for i, a in enumerate(allocation):
            ticker = a.get("ticker",""); wstr = a.get("weight","0%")
            sd = next((s for s in stocks if s.get("ticker") == ticker), {})
            try:
                wf   = float(wstr.replace("%",""))
                role = "Principal (>25%)" if wf > 25 else "Media (>10%)" if wf > 10 else "Diversificadora"
                vis  = bar(wf, 100, 12)
            except Exception:
                wf = 0; role = "-"; vis = wstr
            trow(tbl.rows[i+1], [
                ticker, wstr, vis,
                fmt_n(sd.get("sharpe",0)) if sd.get("sharpe") else "-", role,
            ], alt=(i%2==0), center=True, sz=9)

    # ═══════════════════════════════════════════════════════════════════════════
    # S11. ULTIMAS NOTICIAS
    # ═══════════════════════════════════════════════════════════════════════════
    h1("11.  ULTIMAS NOTICIAS - CARTERA SELECCIONADA")
    body(f"Titulares recientes de las empresas del portafolio recomendado. Fuente: Yahoo Finance ({today}).")

    tickers_in_portfolio = [a.get("ticker","") for a in allocation if a.get("ticker","")]
    if not tickers_in_portfolio and stocks:
        tickers_in_portfolio = [s.get("ticker","") for s in stocks[:6]]

    if tickers_in_portfolio:
        news_data = _fetch_news(tickers_in_portfolio, max_per=3)
        if news_data:
            for ticker, items in news_data.items():
                wstr = next((a.get("weight","") for a in allocation if a.get("ticker") == ticker), "")
                h3(f"{ticker}" + (f"  ·  {wstr}" if wstr else ""))
                if items:
                    tbl = doc.add_table(rows=len(items)+1, cols=3)
                    tbl.style = "Table Grid"
                    thead(tbl, ["Titular", "Fuente", "Fecha"])
                    for i, n in enumerate(items):
                        trow(tbl.rows[i+1], [n.get("title",""), n.get("publisher",""), n.get("date","")], alt=(i%2==0), sz=9)
        else:
            body("No fue posible recuperar noticias en tiempo real. Consulte Yahoo Finance, Bloomberg o Reuters.", italic=True, color=GRAY)

    # ═══════════════════════════════════════════════════════════════════════════
    # S12. REFERENCIAS
    # ═══════════════════════════════════════════════════════════════════════════
    h1("12.  REFERENCIAS BIBLIOGRAFICAS")
    for ref in [
        "Saaty, T.L. (1980). The Analytic Hierarchy Process. McGraw-Hill, New York.",
        "Saaty, T.L. (1990). How to make a decision: The Analytic Hierarchy Process. European Journal of Operational Research, 48(1), 9-26.",
        "Markowitz, H.M. (1952). Portfolio Selection. The Journal of Finance, 7(1), 77-91.",
        "Sharpe, W.F. (1966). Mutual Fund Performance. Journal of Business, 39(1), 119-138.",
        "Sharpe, W.F. (1970). Portfolio Theory and Capital Markets. McGraw-Hill, New York.",
        "Jensen, M.C. (1968). The Performance of Mutual Funds in the Period 1945-1964. The Journal of Finance, 23(2), 389-416.",
        "Sortino, F.A. & Price, L.N. (1994). Performance Measurement in a Downside Risk Framework. The Journal of Investing, 3(3), 59-64.",
        "Artzner, P., Delbaen, F., Eber, J.M. & Heath, D. (1999). Coherent Measures of Risk. Mathematical Finance, 9(3), 203-228.",
        "Escobar, J.W. (2015). Seleccion de portafolios optimos de inversion usando el Proceso Analitico Jerarquico. Contaduria y Administracion, 60(2), 346-366.",
        "Elton, E.J. & Gruber, M.J. (1995). Modern Portfolio Theory and Investment Analysis (5th ed.). John Wiley & Sons.",
        "Morgan, J.P. (1996). RiskMetrics - Technical Document (4th ed.). J.P. Morgan/Reuters.",
    ]:
        bullet(ref, size=9.5)

    disc = doc.add_paragraph()
    _tight(disc, 8, 0)
    _run(disc,
         f"Documento generado por AHP Portfolio Selector - {today}. "
         f"Datos: {'Yahoo Finance (precios ajustados de mercado real)' if not is_synthetic else 'Simulacion Monte Carlo calibrada a parametros de mercado historico'}. "
         "Caracter exclusivamente informativo y academico. No constituye asesoramiento financiero ni recomendacion de inversion regulada.",
         sz=8.5, italic=True, clr=GRAY)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(tmp.name)
    return tmp.name
