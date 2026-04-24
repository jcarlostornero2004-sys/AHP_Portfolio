"use client";

import { motion } from "framer-motion";
import { Card } from "./Card";
import type { CriterionInfo, RankingEntry } from "../../types";
import { PROFILE_LABELS, PROFILE_COLORS } from "../../lib/constants";

interface ExplanationCardProps {
  profile: string;
  winner: RankingEntry;
  topCriteria: CriterionInfo[];
  consistencyRatio: number;
}

export function ExplanationCard({
  profile,
  winner,
  topCriteria,
  consistencyRatio,
}: ExplanationCardProps) {
  const profileLabel = PROFILE_LABELS[profile] || profile;
  const profileColor = PROFILE_COLORS[profile] || "#3b82f6";
  const top2 = topCriteria.slice(0, 2);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
    >
      <Card className="card-hover relative overflow-hidden">
        {/* Decorative top gradient accent */}
        <div
          className="absolute top-0 left-0 right-0 h-0.5"
          style={{ backgroundColor: profileColor }}
        />
        <div className="flex items-start gap-3">
          <div
            className="flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-xl"
            style={{ background: `${profileColor}20` }}
          >
            🧠
          </div>
          <div>
            <h3 className="text-sm font-semibold text-text-primary mb-1">
              ¿Por qué esta cartera?
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed">
              Dado tu perfil{" "}
              <span style={{ color: profileColor }} className="font-semibold">
                {profileLabel}
              </span>
              , el algoritmo AHP seleccionó la cartera{" "}
              <span className="text-text-primary font-semibold">
                &ldquo;{winner.name}&rdquo;
              </span>{" "}
              con una puntuación de{" "}
              <span className="text-accent-gold font-semibold">
                {winner.score.toFixed(1)}%
              </span>
              .{" "}
              {top2.length > 0 && (
                <>
                  Los criterios más determinantes fueron{" "}
                  {top2.map((c, i) => (
                    <span key={c.name}>
                      <span className="text-text-primary font-semibold">{c.name}</span>
                      {" "}
                      <span className="text-text-secondary">(peso {c.weight}/9)</span>
                      {i < top2.length - 1 ? " y " : ""}
                    </span>
                  ))}
                  .{" "}
                </>
              )}
              El índice de consistencia (CR={consistencyRatio}) confirma que la comparación
              es matemáticamente coherente.
            </p>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
