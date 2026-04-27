"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";

// ─── Data ────────────────────────────────────────────────────────────────────

const PROFILES = [
  {
    key: "conservador",
    label: "Conservador",
    color: "#3b82f6",
    icon: "🛡️",
    description:
      "Prioriza la preservación del capital por encima de todo. Acepta rentabilidades modestas a cambio de mínima volatilidad y máxima estabilidad. Horizonte corto-medio, bajo tolerancia al riesgo.",
    criteria: ["Mínimo VaR y CVaR", "Alta estabilidad (CV bajo)", "Beta < 1"],
  },
  {
    key: "moderado",
    label: "Moderado",
    color: "#22c55e",
    icon: "⚖️",
    description:
      "Busca un equilibrio entre crecimiento y seguridad. Acepta cierta volatilidad a cambio de una rentabilidad razonable. Horizonte medio, perfil más común entre inversores particulares.",
    criteria: ["Ratio Sharpe equilibrado", "Volatilidad moderada", "Alpha positivo"],
  },
  {
    key: "agresivo",
    label: "Agresivo",
    color: "#f59e0b",
    icon: "📈",
    description:
      "Prioriza la rentabilidad sobre la seguridad. Tolera drawdowns significativos y alta volatilidad si el potencial de ganancia es elevado. Horizonte largo plazo.",
    criteria: ["Máxima rentabilidad", "Alto Sortino", "Alpha Jensen alto"],
  },
  {
    key: "muy_agresivo",
    label: "Muy Agresivo",
    color: "#ef4444",
    icon: "🚀",
    description:
      "Maximiza el retorno sin restricciones de riesgo. Acepta pérdidas temporales muy elevadas. Ideado para inversores con experiencia, capital disponible y horizonte muy largo.",
    criteria: ["Rentabilidad máxima sin límite", "Tracking error alto", "Beta > 1"],
  },
  {
    key: "dividendos",
    label: "Dividendos",
    color: "#8b5cf6",
    icon: "💰",
    description:
      "Busca ingresos periódicos mediante empresas con historial sólido de dividendos. Preferencia por acciones estables y de alta capitalización. Objetivo: flujo de caja constante.",
    criteria: ["Baja volatilidad", "CV mínimo", "Beta cercana a 1"],
  },
  {
    key: "tecnologico",
    label: "Tecnológico",
    color: "#06b6d4",
    icon: "💻",
    description:
      "Concentrado en sectores de innovación (tecnología, semiconductores, software). Alto potencial de crecimiento con mayor volatilidad. Para inversores que creen en la transformación digital.",
    criteria: ["Alpha alto", "Rentabilidad > benchmark", "Sharpe competitivo"],
  },
  {
    key: "esg",
    label: "ESG",
    color: "#10b981",
    icon: "🌱",
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
    icon: "📈",
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
    icon: "⚠️",
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
    icon: "⚡",
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
          "Diferencia entre la rentabilidad obtenida y el coste de capital exigido por el CAPM. Un valor positivo indica que el activo supera el retorno mínimo exigido por su nivel de riesgo.",
        ref: "CAPM — Escobar (2015)",
      },
    ],
  },
  {
    id: "estabilidad",
    label: "Estabilidad",
    color: "#f59e0b",
    icon: "📊",
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
    icon: "🌐",
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
  { icon: "📋", title: "Cuestionario", desc: "15 preguntas sobre tu perfil de riesgo, horizonte temporal y objetivos" },
  { icon: "🔍", title: "Análisis", desc: "El sistema descarga y analiza 60+ acciones de S&P 500, Eurostoxx y Nikkei" },
  { icon: "🧮", title: "AHP", desc: "El algoritmo multicriterio pondera los 15 indicadores según tu perfil" },
  { icon: "🏆", title: "Resultado", desc: "Obtienes la cartera óptima con su composición, métricas y proyección" },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <motion.h2
      className="text-3xl font-bold text-center mb-2"
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.h2>
  );
}

function SectionSubtitle({ children }: { children: React.ReactNode }) {
  return (
    <motion.p
      className="text-text-secondary text-center mb-12 max-w-2xl mx-auto"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      {children}
    </motion.p>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [activeCategory, setActiveCategory] = useState("rendimiento");
  const activeGroup = INDICATOR_CATEGORIES.find((c) => c.id === activeCategory)!;

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">

      {/* ── Navbar ── */}
      <nav className="sticky top-0 z-50 flex items-center justify-between px-6 py-4 border-b border-border"
        style={{ background: "rgba(13,17,23,0.85)", backdropFilter: "blur(16px)" }}>
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
        <div className="flex items-center gap-3">
          <Link href="/dashboard" className="text-sm text-text-secondary hover:text-text-primary transition-colors hidden sm:block">
            Dashboard
          </Link>
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
            AHP Invest analiza más de 60 acciones globales con 15 indicadores financieros y
            selecciona la cartera óptima para tu perfil usando el <strong className="text-text-primary">Proceso Analítico Jerárquico</strong>.
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
            { v: "60+", l: "Acciones analizadas" },
            { v: "15", l: "Indicadores financieros" },
            { v: "7", l: "Perfiles de inversión" },
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

      {/* ── Cómo funciona el proceso ── */}
      <section className="px-6 py-20">
        <div className="max-w-5xl mx-auto">
          <SectionTitle>El proceso en 4 pasos</SectionTitle>
          <SectionSubtitle>De tu perfil inversor a una cartera óptima, en minutos.</SectionSubtitle>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {STEPS.map((s, i) => (
              <motion.div key={s.title} className="glass rounded-2xl p-6 card-hover text-center"
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <div className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mx-auto mb-4"
                  style={{ background: "rgba(59,130,246,0.12)" }}>
                  {s.icon}
                </div>
                <div className="text-xs text-accent-blue font-semibold uppercase tracking-widest mb-1">Paso {i + 1}</div>
                <h3 className="font-semibold text-text-primary mb-2">{s.title}</h3>
                <p className="text-xs text-text-secondary leading-relaxed">{s.desc}</p>
              </motion.div>
            ))}
          </div>
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
            {[
              {
                icon: "🔢",
                title: "Comparaciones por pares",
                text: "AHP descompone la decisión en comparaciones binarias entre criterios. Para cada par de indicadores, se establece cuál es más importante y en qué grado (escala 1–9 de Saaty). Esto genera una matriz de preferencias consistente.",
              },
              {
                icon: "📐",
                title: "Vector de prioridades (eigenvector)",
                text: "A partir de la matriz de comparaciones, se calcula el autovector principal (eigenvector). Sus componentes normalizados representan el peso relativo de cada criterio, garantizando coherencia matemática.",
              },
              {
                icon: "✅",
                title: "Índice de Consistencia (CR)",
                text: "AHP mide si las comparaciones son lógicamente coherentes mediante el Ratio de Consistencia (CR). Si CR < 0.10, la matriz es aceptable. Si es mayor, las preferencias son contradictorias y deben revisarse.",
              },
              {
                icon: "🏆",
                title: "Ranking final de carteras",
                text: "Cada cartera candidata es evaluada respecto a los 15 indicadores financieros con los pesos calculados. La puntuación AHP final combina todos los criterios ponderados para elegir la cartera óptima para tu perfil.",
              },
            ].map((c, i) => (
              <motion.div key={c.title} className="glass rounded-2xl p-6 card-hover"
                initial={{ opacity: 0, x: i % 2 === 0 ? -16 : 16 }} whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}>
                <div className="text-2xl mb-3">{c.icon}</div>
                <h3 className="font-semibold text-text-primary mb-2">{c.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{c.text}</p>
              </motion.div>
            ))}
          </div>

          {/* Base científica */}
          <motion.div className="bg-bg-secondary border border-border rounded-2xl p-6"
            initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            <h3 className="font-semibold text-text-primary mb-3 flex items-center gap-2">
              <span>📚</span> Base científica y referencias
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
      <section className="px-6 py-20 border-t border-border">
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
                <span>{cat.icon}</span>
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
          <motion.div
            key={activeCategory}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
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
      <section className="px-6 py-20 border-t border-border">
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
                {/* Color top bar */}
                <div className="absolute top-0 left-0 right-0 h-0.5" style={{ backgroundColor: p.color }} />
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center text-lg flex-shrink-0"
                    style={{ backgroundColor: `${p.color}20` }}>
                    {p.icon}
                  </div>
                  <h3 className="font-semibold text-text-primary" style={{ color: p.color }}>{p.label}</h3>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed mb-3">{p.description}</p>
                <div className="space-y-1">
                  {p.criteria.map((c) => (
                    <div key={c} className="flex items-center gap-1.5 text-xs text-text-secondary">
                      <span style={{ color: p.color }}>✓</span>
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
      <section className="px-6 py-24 border-t border-border text-center">
        <motion.div className="max-w-xl mx-auto"
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }} transition={{ duration: 0.6 }}>
          <div className="text-4xl mb-4">🧠</div>
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
