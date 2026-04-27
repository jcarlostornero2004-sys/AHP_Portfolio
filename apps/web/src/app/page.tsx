"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";
import { useTheme } from "../hooks/useTheme";

// ─── Icon helper ─────────────────────────────────────────────────────────────

function Ic({ d, size = 20, className = "" }: { d: string; size?: number; className?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"
      className={className}>
      <path d={d} />
    </svg>
  );
}

const IC = {
  sun:        "M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z",
  moon:       "M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z",
  clipboard:  "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
  database:   "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4",
  matrix:     "M3 10h18M3 6h18M10 3v18M14 3v18",
  badge:      "M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z",
  tableGrid:  "M3 10h18M3 6h18M10 3v18M14 3v18",
  barChart:   "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  checkCircle:"M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  trendUp:    "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
  book:       "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253",
  info:       "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  arrowDown:  "M19 9l-7 7-7-7",
};

// ─── Data ────────────────────────────────────────────────────────────────────

const PROFILES = [
  {
    key: "conservador",
    label: "Conservador",
    color: "#3b82f6",
    description:
      "Prioriza la preservación del capital por encima de todo. Acepta rentabilidades modestas a cambio de mínima volatilidad y máxima estabilidad. Horizonte corto-medio, baja tolerancia al riesgo.",
    criteria: ["Mínimo VaR y CVaR", "Alta estabilidad (CV bajo)", "Beta < 1"],
  },
  {
    key: "moderado",
    label: "Moderado",
    color: "#22c55e",
    description:
      "Busca un equilibrio entre crecimiento y seguridad. Acepta cierta volatilidad a cambio de una rentabilidad razonable. Horizonte medio, perfil más común entre inversores particulares.",
    criteria: ["Ratio Sharpe equilibrado", "Volatilidad moderada", "Alpha positivo"],
  },
  {
    key: "agresivo",
    label: "Agresivo",
    color: "#f59e0b",
    description:
      "Prioriza la rentabilidad sobre la seguridad. Tolera drawdowns significativos y alta volatilidad si el potencial de ganancia es elevado. Horizonte largo plazo.",
    criteria: ["Máxima rentabilidad", "Alto Sortino", "Alpha Jensen alto"],
  },
  {
    key: "muy_agresivo",
    label: "Muy Agresivo",
    color: "#ef4444",
    description:
      "Maximiza el retorno sin restricciones de riesgo. Acepta pérdidas temporales muy elevadas. Ideado para inversores con experiencia, capital disponible y horizonte muy largo.",
    criteria: ["Rentabilidad máxima sin límite", "Tracking error alto", "Beta > 1"],
  },
  {
    key: "dividendos",
    label: "Dividendos",
    color: "#8b5cf6",
    description:
      "Busca ingresos periódicos mediante empresas con historial sólido de dividendos. Preferencia por acciones estables y de alta capitalización. Objetivo: flujo de caja constante.",
    criteria: ["Baja volatilidad", "CV mínimo", "Beta cercana a 1"],
  },
  {
    key: "tecnologico",
    label: "Tecnológico",
    color: "#06b6d4",
    description:
      "Concentrado en sectores de innovación (tecnología, semiconductores, software). Alto potencial de crecimiento con mayor volatilidad. Para inversores que creen en la transformación digital.",
    criteria: ["Alpha alto", "Rentabilidad > benchmark", "Sharpe competitivo"],
  },
  {
    key: "esg",
    label: "ESG",
    color: "#10b981",
    description:
      "Invierte según criterios medioambientales, sociales y de gobernanza. Combina rentabilidad con impacto positivo. Empresas con buenas prácticas sostenibles y transparencia corporativa.",
    criteria: ["Diversificación geográfica", "Correlación baja", "Tracking error controlado"],
  },
];

const INDICATOR_CATEGORIES = [
  {
    id: "rendimiento",
    label: "Rendimiento",
    color: "#22c55e",
    indicators: [
      {
        name: "Rentabilidad Anualizada",
        formula: "μ × 252",
        description:
          "Media de rendimientos logarítmicos diarios escalada a 252 días hábiles. Mide el crecimiento porcentual anual esperado de la inversión.",
        ref: "Markowitz (1952)",
      },
      {
        name: "Ratio de Sharpe",
        formula: "(Rp − Rf) / σp",
        description:
          "Exceso de rentabilidad sobre la tasa libre de riesgo por unidad de riesgo total. Cuanto mayor, mejor relación rentabilidad/riesgo.",
        ref: "Sharpe (1966)",
      },
      {
        name: "Ratio de Sortino",
        formula: "(Rp − Rf) / σ↓",
        description:
          "Variante del Sharpe que penaliza sólo la volatilidad negativa (downside deviation). Más relevante para inversores que temen las pérdidas.",
        ref: "Sortino & Price (1994)",
      },
      {
        name: "Alpha de Jensen",
        formula: "Rp − [Rf + β(Rm − Rf)]",
        description:
          "Rentabilidad que supera a la predicha por el CAPM dada la exposición al mercado. Alpha positivo indica que el gestor genera valor por encima del mercado.",
        ref: "Jensen (1968)",
      },
    ],
  },
  {
    id: "riesgo",
    label: "Riesgo",
    color: "#ef4444",
    indicators: [
      {
        name: "Volatilidad",
        formula: "σ × √252",
        description:
          "Desviación estándar de los rendimientos diarios, anualizada. Mide la dispersión de los retornos; mayor volatilidad implica mayor incertidumbre.",
        ref: "Markowitz (1952)",
      },
      {
        name: "VaR 95% (Paramétrico)",
        formula: "−(μ + z₀.₀₅ × σ)",
        description:
          "Pérdida máxima esperada con 95% de confianza bajo distribución normal. Si VaR = 10%, en 1 de cada 20 períodos se espera perder al menos ese porcentaje.",
        ref: "Morgan (1996)",
      },
      {
        name: "CVaR 95% (Expected Shortfall)",
        formula: "−E[R | R ≤ q₅%]",
        description:
          "Media de las pérdidas en el 5% peor de los casos. Más conservador que el VaR porque considera la magnitud de las pérdidas extremas, no sólo su probabilidad.",
        ref: "Artzner et al. (1999)",
      },
      {
        name: "Max Drawdown",
        formula: "máx[(Pico − Valle) / Pico]",
        description:
          "Mayor caída porcentual desde un pico histórico hasta el valle siguiente antes de recuperarse. Indica el peor escenario vivido por un inversor que compró en máximos.",
        ref: "Escobar (2015)",
      },
    ],
  },
  {
    id: "eficiencia",
    label: "Eficiencia",
    color: "#3b82f6",
    indicators: [
      {
        name: "Beta (β)",
        formula: "Cov(Ri, Rm) / Var(Rm)",
        description:
          "Sensibilidad del activo a los movimientos del mercado. Beta = 1 se mueve igual que el índice; β > 1 amplifica los movimientos; β < 1 los amortigua.",
        ref: "CAPM — Sharpe (1970)",
      },
      {
        name: "Tracking Error",
        formula: "σ(Ri − Rm) × √252",
        description:
          "Desviación estándar de la diferencia de rendimientos entre el activo y su benchmark. Mide cuánto se aleja la cartera del índice de referencia.",
        ref: "Escobar (2015)",
      },
      {
        name: "Rentabilidad − Coste de Capital",
        formula: "Rp − kp = Rp − [Rf + β(Rm − Rf)]",
        description:
          "Diferencia entre la rentabilidad obtenida y el coste de capital exigido por el CAPM. Un valor positivo indica que el activo supera el retorno mínimo exigido.",
        ref: "CAPM — Escobar (2015)",
      },
    ],
  },
  {
    id: "estabilidad",
    label: "Estabilidad",
    color: "#f59e0b",
    indicators: [
      {
        name: "Coeficiente de Variación",
        formula: "σ / |μ|",
        description:
          "Riesgo relativo por unidad de rendimiento esperado. Permite comparar la dispersión entre activos con distintas rentabilidades medias; menor CV indica mayor consistencia.",
        ref: "Estadística descriptiva",
      },
      {
        name: "Skewness (Asimetría)",
        formula: "E[(R − μ)³] / σ³",
        description:
          "Mide la asimetría de la distribución de rendimientos. Skewness positivo indica que los retornos extremos positivos son más frecuentes; negativo implica colas de pérdida más largas.",
        ref: "Sortino & Price (1994)",
      },
    ],
  },
  {
    id: "diversificacion",
    label: "Diversificación",
    color: "#8b5cf6",
    indicators: [
      {
        name: "Correlación Media",
        formula: "media(ρᵢⱼ) para i ≠ j",
        description:
          "Media de las correlaciones entre pares de activos de la cartera. Cuanto más baja, mayor beneficio de diversificación; activos poco correlacionados reducen el riesgo conjunto.",
        ref: "Markowitz (1952)",
      },
      {
        name: "Diversificación Geográfica",
        formula: "1 − (1/n)",
        description:
          "Medida simplificada de dispersión entre mercados (S&P 500, Eurostoxx, Nikkei). Un valor próximo a 1 indica que la cartera está repartida entre múltiples regiones geográficas.",
        ref: "Escobar (2015)",
      },
    ],
  },
];

const STEPS = [
  {
    iconPath: IC.clipboard,
    title: "Cuestionario",
    desc: "15 preguntas sobre perfil de riesgo, horizonte temporal y objetivos financieros personales.",
    anchor: "#perfiles",
  },
  {
    iconPath: IC.database,
    title: "Datos de mercado",
    desc: "25 acciones representativas por índice — 75 intentadas, ~60 superan el filtro de calidad.",
    anchor: "#analisis",
  },
  {
    iconPath: IC.matrix,
    title: "Algoritmo AHP",
    desc: "El método multicriterio pondera los 15 indicadores según tu perfil inversor.",
    anchor: "#ahp",
  },
  {
    iconPath: IC.badge,
    title: "Cartera óptima",
    desc: "Ranking AHP, composición de la cartera seleccionada y métricas detalladas.",
    anchor: "#indicadores",
  },
];

const AHP_CARDS = [
  {
    iconPath: IC.tableGrid,
    title: "Comparaciones por pares",
    text: "AHP descompone la decisión en comparaciones binarias entre criterios. Para cada par de indicadores, se establece cuál es más importante y en qué grado (escala 1–9 de Saaty). Esto genera una matriz de preferencias consistente.",
  },
  {
    iconPath: IC.barChart,
    title: "Vector de prioridades (eigenvector)",
    text: "A partir de la matriz de comparaciones, se calcula el autovector principal (eigenvector). Sus componentes normalizados representan el peso relativo de cada criterio, garantizando coherencia matemática.",
  },
  {
    iconPath: IC.checkCircle,
    title: "Índice de Consistencia (CR)",
    text: "AHP mide si las comparaciones son lógicamente coherentes mediante el Ratio de Consistencia (CR). Si CR < 0.10, la matriz es aceptable. Si es mayor, las preferencias son contradictorias y deben revisarse.",
  },
  {
    iconPath: IC.trendUp,
    title: "Ranking final de carteras",
    text: "Cada cartera candidata es evaluada respecto a los 15 indicadores con los pesos calculados. La puntuación AHP final combina todos los criterios ponderados para elegir la cartera óptima.",
  },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <motion.h2 className="text-3xl font-bold text-center mb-2"
      initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }} transition={{ duration: 0.5 }}>
      {children}
    </motion.h2>
  );
}

function SectionSubtitle({ children }: { children: React.ReactNode }) {
  return (
    <motion.p className="text-text-secondary text-center mb-12 max-w-2xl mx-auto"
      initial={{ opacity: 0 }} whileInView={{ opacity: 1 }}
      viewport={{ once: true }} transition={{ duration: 0.5, delay: 0.1 }}>
      {children}
    </motion.p>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [activeCategory, setActiveCategory] = useState("rendimiento");
  const { theme, toggle } = useTheme();
  const activeGroup = INDICATOR_CATEGORIES.find((c) => c.id === activeCategory)!;

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">

      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 border-b border-border nav-bg">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}>
            <svg width="16" height="16" viewBox="0 0 18 18" fill="none">
              <path d="M2 13 L6 8 L10 10 L15 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M12 4 H15 V7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="font-bold text-text-primary">AHP Invest</span>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary transition-colors hidden sm:block px-3 py-2">
            Dashboard
          </Link>
          <button
            onClick={toggle}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-border text-text-secondary hover:text-text-primary hover:border-accent-blue/50 transition-colors cursor-pointer"
            title={theme === "dark" ? "Cambiar a tema claro" : "Cambiar a tema oscuro"}
          >
            {theme === "dark"
              ? <Ic d={IC.sun} size={16} />
              : <Ic d={IC.moon} size={16} />
            }
          </button>
          <Link href="/questionnaire"
            className="px-4 py-2 rounded-lg text-sm font-semibold text-white transition-opacity hover:opacity-80"
            style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}>
            Empezar análisis →
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="relative flex flex-col items-center justify-center text-center px-6 pt-20 pb-16 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] rounded-full opacity-[0.07] blur-3xl pointer-events-none"
          style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }} />

        <motion.div className="relative z-10 max-w-3xl"
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-blue/10 border border-accent-blue/20 text-accent-blue text-xs font-medium mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-green pulse-live" />
            Robo Advisor · Método AHP · Mercados Globales
          </span>
          <h1 className="text-5xl md:text-6xl font-extrabold leading-tight mb-5">
            Invierte con <span className="gradient-text">método científico</span>
          </h1>
          <p className="text-lg text-text-secondary max-w-xl mx-auto mb-10 leading-relaxed">
            AHP Invest selecciona una muestra representativa de los tres grandes índices mundiales,
            evalúa 15 indicadores financieros por acción y construye la cartera óptima para tu perfil
            mediante el <strong className="text-text-primary">Proceso Analítico Jerárquico</strong>.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link href="/questionnaire"
              className="px-8 py-3.5 rounded-xl text-white font-semibold text-base transition-opacity hover:opacity-90"
              style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}>
              Comenzar análisis →
            </Link>
            <a href="#ahp" className="px-8 py-3.5 rounded-xl text-text-secondary font-medium text-base border border-border hover:text-text-primary hover:bg-bg-tertiary transition-colors">
              ¿Cómo funciona?
            </a>
          </div>
        </motion.div>
      </section>

      {/* ── Stats ── */}
      <section className="px-6 py-10 border-y border-border">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { v: "~60",      l: "Acciones por análisis" },
            { v: "15",       l: "Indicadores financieros" },
            { v: "7",        l: "Perfiles de inversión" },
            { v: "CR < 0.1", l: "Consistencia AHP garantizada" },
          ].map((s, i) => (
            <motion.div key={s.l} initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }} transition={{ delay: i * 0.08 }}>
              <div className="text-3xl font-extrabold gradient-text">{s.v}</div>
              <div className="text-xs text-text-secondary mt-1">{s.l}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Proceso en 4 pasos ── */}
      <section className="px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <SectionTitle>El proceso en 4 pasos</SectionTitle>
          <SectionSubtitle>
            Haz clic en cada paso para saltar directamente a su explicación detallada.
          </SectionSubtitle>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {STEPS.map((s, i) => (
              <motion.a
                key={s.title}
                href={s.anchor}
                className="glass rounded-2xl p-6 card-hover text-center block cursor-pointer no-underline"
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}
              >
                <div className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4 text-accent-blue"
                  style={{ background: "rgba(59,130,246,0.12)" }}>
                  <Ic d={s.iconPath} size={22} />
                </div>
                <div className="text-xs text-accent-blue font-semibold uppercase tracking-widest mb-1">Paso {i + 1}</div>
                <h3 className="font-semibold text-text-primary mb-2">{s.title}</h3>
                <p className="text-xs text-text-secondary leading-relaxed mb-3">{s.desc}</p>
                <span className="text-xs text-accent-blue/60 font-medium">Ver detalle ↓</span>
              </motion.a>
            ))}
          </div>
        </div>
      </section>

      {/* ── Por qué ~60 acciones ── */}
      <section id="analisis" className="px-6 pb-16">
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="bg-bg-secondary border border-border rounded-2xl p-6"
            initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <div className="flex items-start gap-3 mb-4">
              <span className="text-accent-blue mt-0.5 flex-shrink-0">
                <Ic d={IC.info} size={18} />
              </span>
              <h3 className="font-semibold text-text-primary">Por qué el análisis usa ~60 acciones y no las 700+ del universo completo</h3>
            </div>
            <div className="space-y-3 text-sm text-text-secondary leading-relaxed pl-7">
              <p>
                Los tres índices de referencia (S&P 500, Euro Stoxx 50, Nikkei 225) agrupan en total más de 700 valores.
                Descargar y procesar 2 años de datos históricos para todos ellos en tiempo real llevaría varios minutos,
                lo que es inviable para una aplicación web de uso inmediato.
              </p>
              <p>
                El sistema adopta una <strong className="text-text-primary">muestra representativa</strong>: selecciona los
                25 tickers más líquidos y representativos de cada índice (75 en total), descarga su histórico de precios
                y aplica un <strong className="text-text-primary">filtro de calidad</strong> que descarta cualquier serie
                con más del 20 % de datos ausentes o erróneos. Normalmente entre 55 y 70 acciones superan este filtro:
                ese es el número que aparece en el dashboard como «acciones analizadas».
              </p>
              <p>
                Este enfoque está en línea con la práctica habitual en investigación financiera
                (Escobar, 2015): trabajar con una muestra acotada y de calidad garantizada es preferible
                a incorporar datos ruidosos o incompletos que distorsionen los indicadores de riesgo y rentabilidad.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Qué es AHP ── */}
      <section id="ahp" className="px-6 py-20 border-t border-border">
        <div className="max-w-4xl mx-auto">
          <SectionTitle>¿Qué es el método AHP?</SectionTitle>
          <SectionSubtitle>
            El Proceso Analítico Jerárquico (Analytic Hierarchy Process) fue desarrollado por Thomas L. Saaty
            en 1990 y es uno de los métodos de decisión multicriterio más utilizados en finanzas y gestión empresarial.
          </SectionSubtitle>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {AHP_CARDS.map((c, i) => (
              <motion.div key={c.title} className="glass rounded-2xl p-6 card-hover"
                initial={{ opacity: 0, x: i % 2 === 0 ? -16 : 16 }} whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3 text-accent-blue"
                  style={{ background: "rgba(59,130,246,0.12)" }}>
                  <Ic d={c.iconPath} size={18} />
                </div>
                <h3 className="font-semibold text-text-primary mb-2">{c.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{c.text}</p>
              </motion.div>
            ))}
          </div>

          <motion.div className="bg-bg-secondary border border-border rounded-2xl p-6"
            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            <h3 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
              <span className="text-accent-blue"><Ic d={IC.book} size={16} /></span>
              Base científica y referencias
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-text-secondary">
              {[
                "Saaty, T.L. (1990) — Método AHP original",
                "Markowitz, H. (1952) — Teoría moderna de carteras",
                "Sharpe, W.F. (1966, 1970) — Ratio Sharpe y CAPM",
                "Sortino & Price (1994) — Downside deviation",
                "Artzner et al. (1999) — CVaR / Expected Shortfall",
                "Escobar, J.W. (2015) — AHP aplicado a selección de carteras",
              ].map((r) => (
                <div key={r} className="flex items-start gap-2">
                  <span className="text-accent-blue mt-0.5">▸</span>
                  <span>{r}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── 15 Indicadores ── */}
      <section id="indicadores" className="px-6 py-20 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <SectionTitle>Los 15 Indicadores Financieros</SectionTitle>
          <SectionSubtitle>
            El algoritmo evalúa cada cartera candidata según 15 métricas agrupadas en 5 categorías.
            Cada indicador recibe un peso AHP diferente dependiendo de tu perfil.
          </SectionSubtitle>

          {/* Category tabs */}
          <div className="flex flex-wrap gap-2 justify-center mb-8">
            {INDICATOR_CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer ${
                  activeCategory === cat.id
                    ? "text-white"
                    : "bg-bg-secondary border border-border text-text-secondary hover:text-text-primary"
                }`}
                style={activeCategory === cat.id ? { backgroundColor: cat.color } : undefined}
              >
                {cat.label}
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                  activeCategory === cat.id ? "bg-white/20" : "bg-bg-tertiary"
                }`}>
                  {cat.indicators.length}
                </span>
              </button>
            ))}
          </div>

          {/* Indicators grid */}
          <motion.div key={activeCategory} className="grid grid-cols-1 md:grid-cols-2 gap-4"
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            {activeGroup.indicators.map((ind) => (
              <div key={ind.name} className="bg-bg-secondary border border-border rounded-xl p-5 card-hover">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-text-primary text-sm">{ind.name}</h4>
                  <span className="text-[10px] text-text-secondary bg-bg-tertiary px-2 py-0.5 rounded-full ml-2 flex-shrink-0">
                    {ind.ref}
                  </span>
                </div>
                <code className="text-xs font-mono px-2 py-1 rounded-md mb-3 block w-fit"
                  style={{ backgroundColor: `${activeGroup.color}18`, color: activeGroup.color }}>
                  {ind.formula}
                </code>
                <p className="text-xs text-text-secondary leading-relaxed">{ind.description}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── 7 Perfiles ── */}
      <section id="perfiles" className="px-6 py-20 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <SectionTitle>Los 7 Perfiles de Inversión</SectionTitle>
          <SectionSubtitle>
            El cuestionario determina cuál de estos perfiles se adapta mejor a ti.
            Cada perfil aplica pesos AHP distintos para priorizar los indicadores que más importan según tus objetivos.
          </SectionSubtitle>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {PROFILES.map((p, i) => (
              <motion.div
                key={p.key}
                className="bg-bg-secondary border border-border rounded-xl p-5 card-hover relative overflow-hidden"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
              >
                <div className="absolute top-0 left-0 right-0 h-0.5" style={{ backgroundColor: p.color }} />
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
                    style={{ backgroundColor: `${p.color}18`, color: p.color }}>
                    {p.label.charAt(0)}
                  </div>
                  <h3 className="font-semibold" style={{ color: p.color }}>{p.label}</h3>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed mb-3">{p.description}</p>
                <div className="space-y-1">
                  {p.criteria.map((c) => (
                    <div key={c} className="flex items-center gap-1.5 text-xs text-text-secondary">
                      <span className="w-1 h-1 rounded-full flex-shrink-0" style={{ backgroundColor: p.color }} />
                      {c}
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section id="cta" className="px-6 py-24 border-t border-border text-center">
        <motion.div className="max-w-xl mx-auto"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <h2 className="text-3xl font-bold mb-4">¿Listo para descubrir tu cartera ideal?</h2>
          <p className="text-text-secondary mb-8 leading-relaxed">
            El cuestionario tarda menos de 3 minutos. El algoritmo se encarga del resto:
            análisis, optimización y ranking multicriterio completamente automatizados.
          </p>
          <Link href="/questionnaire"
            className="inline-block px-10 py-4 rounded-xl text-white font-semibold text-base transition-opacity hover:opacity-90"
            style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}>
            Empezar el cuestionario →
          </Link>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-border px-6 py-6 text-center text-xs text-text-secondary">
        AHP Invest — Basado en Saaty (1990), Markowitz (1952), Escobar (2015) · Proyecto académico TFG
      </footer>
    </div>
  );
}
