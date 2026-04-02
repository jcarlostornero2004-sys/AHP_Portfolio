"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AppLayout } from "../../components/layout/AppLayout";
import { Card } from "../../components/ui/Card";
import { useProfileStore } from "../../hooks/useProfile";
import { downloadWordReport } from "../../lib/api";
import { PROFILE_LABELS, PROFILE_COLORS } from "../../lib/constants";

export default function ReportPage() {
  const router = useRouter();
  const { analysisResult, profileResult, answers } = useProfileStore();
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setDownloading(true);
    setError(null);
    try {
      await downloadWordReport(answers);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error generating report");
    } finally {
      setDownloading(false);
    }
  };

  if (!analysisResult || !profileResult) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
          <p className="text-text-secondary text-lg">No hay resultados de análisis.</p>
          <button
            onClick={() => router.push("/")}
            className="text-accent-blue hover:underline cursor-pointer"
          >
            Completa el cuestionario primero
          </button>
        </div>
      </AppLayout>
    );
  }

  const profileColor = PROFILE_COLORS[profileResult.profile] || "#3b82f6";
  const profileLabel = PROFILE_LABELS[profileResult.profile] || profileResult.profile;
  const winner = analysisResult.ranking?.[0];

  const sections = [
    { title: "Perfil del Inversor", desc: "Clasificación del perfil, puntuaciones por dimensión e implicaciones estratégicas." },
    { title: "Universo y Datos", desc: "Índices bursátiles considerados, los 15 indicadores financieros utilizados y su justificación." },
    { title: "Filtrado de Acciones", desc: "Criterios de filtrado aplicados según el perfil y las acciones seleccionadas del universo." },
    { title: "Metodología AHP", desc: "Proceso analítico jerárquico de Saaty, matriz de comparación pareada y pesos de criterios con tabla de prioridades." },
    { title: "Construcción Markowitz", desc: "Optimización media-varianza, maximización del ratio de Sharpe y justificación de los pesos individuales." },
    { title: "Ranking AHP Final", desc: "Puntuación de cada acción candidata, tabla de ranking y justificación del activo ganador." },
    { title: "Cartera Recomendada", desc: "Métricas de rendimiento, tabla de asignación con porcentajes y rol de cada posición." },
    { title: "Referencias Académicas", desc: "Bibliografía completa de los métodos y fuentes de datos utilizados." },
  ];

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Informe de Cartera</h1>
          <p className="text-text-secondary mt-1">
            Informe metodológico completo en formato Word — explica paso a paso cómo se construyó tu cartera.
          </p>
        </div>

        {/* Profile summary */}
        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center text-white font-bold text-lg shrink-0"
              style={{ backgroundColor: profileColor }}
            >
              {profileLabel.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p className="text-sm text-text-secondary">Perfil identificado</p>
              <p className="text-xl font-bold" style={{ color: profileColor }}>{profileLabel}</p>
              {winner && (
                <p className="text-sm text-text-secondary mt-0.5">
                  Activo ganador AHP: <span className="text-text-primary font-medium">{winner.name}</span>
                </p>
              )}
            </div>
          </div>
        </Card>

        {/* Report contents */}
        <Card className="p-6">
          <h2 className="text-base font-semibold mb-4">Contenido del informe</h2>
          <ol className="space-y-3">
            {sections.map((s, i) => (
              <li key={i} className="flex gap-3">
                <span
                  className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                  style={{ backgroundColor: profileColor }}
                >
                  {i + 1}
                </span>
                <div>
                  <p className="text-sm font-medium text-text-primary">{s.title}</p>
                  <p className="text-xs text-text-secondary mt-0.5">{s.desc}</p>
                </div>
              </li>
            ))}
          </ol>
        </Card>

        {/* Download */}
        <Card className="p-6">
          <div className="flex flex-col items-center gap-4 text-center">
            <svg className="w-12 h-12 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-text-primary">Informe_AHP_{profileLabel}.docx</p>
              <p className="text-xs text-text-secondary mt-1">Documento Word profesional con tablas, análisis completo y referencias.</p>
            </div>

            {error && (
              <p className="text-sm text-accent-red bg-accent-red/10 px-4 py-2 rounded-lg w-full">{error}</p>
            )}

            <button
              onClick={handleDownload}
              disabled={downloading}
              className="flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white transition-all disabled:opacity-60 cursor-pointer disabled:cursor-not-allowed"
              style={{ backgroundColor: profileColor }}
            >
              {downloading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generando informe...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Descargar Informe Word
                </>
              )}
            </button>
          </div>
        </Card>
      </div>
    </AppLayout>
  );
}
