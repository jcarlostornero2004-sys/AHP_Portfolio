"use client";

import Link from "next/link";
import { motion } from "framer-motion";

const features = [
  {
    icon: "🧮",
    title: "¿Qué es AHP?",
    description:
      "El Proceso Analítico Jerárquico (Saaty, 1990) es un método matemático de decisión multicriterio que compara carteras según 15 indicadores financieros con consistencia matemática garantizada.",
  },
  {
    icon: "📡",
    title: "Análisis en tiempo real",
    description:
      "Descarga datos reales de Yahoo Finance para más de 60 acciones de S&P 500, Eurostoxx 600 y Nikkei 225. Si la red falla, cambia a datos sintéticos automáticamente.",
  },
  {
    icon: "🎯",
    title: "Resultados personalizados",
    description:
      "7 perfiles de inversión (conservador, moderado, agresivo…) con pesos AHP distintos. El cuestionario de 15 preguntas determina tu perfil y filtra las acciones adecuadas.",
  },
];

const stats = [
  { value: "500+", label: "Acciones Analizadas" },
  { value: "7", label: "Perfiles de Inversión" },
  { value: "15", label: "Indicadores Financieros" },
  { value: "AHP", label: "Método Validado" },
];

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" as const } },
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary text-text-primary">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
          >
            <svg width="16" height="16" viewBox="0 0 18 18" fill="none">
              <path d="M2 13 L6 8 L10 10 L15 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M12 4 H15 V7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="font-bold text-text-primary">AHP Invest</span>
        </div>
        <Link
          href="/"
          className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-80"
          style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
        >
          Empezar análisis →
        </Link>
      </nav>

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center text-center px-6 pt-24 pb-20 overflow-hidden">
        {/* Background glow blobs */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
        />

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="relative z-10 max-w-3xl"
        >
          <motion.div variants={itemVariants}>
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-blue/10 border border-accent-blue/20 text-accent-blue text-xs font-medium mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-accent-green pulse-live" />
              Robo Advisor con método AHP
            </span>
          </motion.div>

          <motion.h1
            variants={itemVariants}
            className="text-5xl md:text-6xl font-extrabold leading-tight mb-6"
          >
            Tu dinero,{" "}
            <span className="gradient-text">optimizado con</span>
            <br />
            matemáticas e IA
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="text-lg text-text-secondary max-w-xl mx-auto mb-10 leading-relaxed"
          >
            Responde 15 preguntas, seleccionamos las mejores acciones de 3 índices
            globales y construimos tu cartera óptima con el algoritmo AHP.
          </motion.p>

          <motion.div variants={itemVariants} className="flex items-center justify-center gap-4">
            <Link
              href="/"
              className="px-8 py-3.5 rounded-xl text-white font-semibold text-base transition-opacity hover:opacity-90"
              style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
            >
              Empezar análisis →
            </Link>
            <Link
              href="/dashboard"
              className="px-8 py-3.5 rounded-xl text-text-secondary font-medium text-base border border-border hover:text-text-primary hover:bg-bg-tertiary transition-colors"
            >
              Ver Dashboard
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Animated stats */}
      <section className="px-8 py-12 border-y border-border">
        <motion.div
          className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          {stats.map((s) => (
            <motion.div key={s.label} variants={itemVariants} className="text-center">
              <div className="text-4xl font-extrabold gradient-text mb-1">{s.value}</div>
              <div className="text-sm text-text-secondary">{s.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Feature cards */}
      <section className="px-8 py-20">
        <motion.div
          className="max-w-5xl mx-auto"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
        >
          <motion.h2
            variants={itemVariants}
            className="text-3xl font-bold text-center mb-12"
          >
            Cómo funciona
          </motion.h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((f) => (
              <motion.div
                key={f.title}
                variants={itemVariants}
                className="glass rounded-2xl p-6 card-hover"
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-4"
                  style={{ background: "rgba(59,130,246,0.12)" }}
                >
                  {f.icon}
                </div>
                <h3 className="text-base font-semibold text-text-primary mb-2">{f.title}</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{f.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* CTA */}
      <section className="px-8 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="max-w-xl mx-auto"
        >
          <h2 className="text-3xl font-bold mb-4">¿Listo para invertir mejor?</h2>
          <p className="text-text-secondary mb-8">
            Completa el cuestionario en menos de 3 minutos y obtén tu cartera personalizada.
          </p>
          <Link
            href="/"
            className="inline-block px-10 py-4 rounded-xl text-white font-semibold text-base transition-opacity hover:opacity-90"
            style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
          >
            Empezar ahora →
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-8 py-6 text-center text-xs text-text-secondary">
        AHP Invest — Basado en Saaty (1990), Markowitz (1952), Escobar (2015)
      </footer>
    </div>
  );
}
