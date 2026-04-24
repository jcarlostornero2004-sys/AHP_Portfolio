"use client";

import { motion } from "framer-motion";
import { Card } from "./Card";

interface StatCardProps {
  label: string;
  value: string;
  subtitle?: string;
  color?: "green" | "red" | "blue" | "gold" | "default";
  className?: string;
  icon?: string | React.ReactNode;
}

const colorMap = {
  green: "text-accent-green",
  red: "text-accent-red",
  blue: "text-accent-blue",
  gold: "text-accent-gold",
  default: "text-text-primary",
};

const topBorderMap = {
  green: "border-t-2 border-accent-green",
  red: "border-t-2 border-accent-red",
  blue: "border-t-2 border-accent-blue",
  gold: "border-t-2 border-accent-gold",
  default: "",
};

const glowMap = {
  green: "0 0 20px rgba(34, 197, 94, 0.08)",
  red: "0 0 20px rgba(239, 68, 68, 0.08)",
  blue: "0 0 20px rgba(59, 130, 246, 0.08)",
  gold: "0 0 20px rgba(245, 158, 11, 0.08)",
  default: "",
};

export function StatCard({
  label,
  value,
  subtitle,
  color = "default",
  className = "",
  icon,
}: StatCardProps) {
  const glow = glowMap[color];

  return (
    <div
      className={`card-hover ${topBorderMap[color]} bg-bg-secondary border border-border rounded-xl p-6 flex flex-col gap-1 ${className}`}
      style={glow ? { boxShadow: glow } : undefined}
    >
      <div className="flex items-start justify-between">
        <span className="text-sm font-medium text-text-secondary uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <span className="text-lg leading-none opacity-80 flex-shrink-0">{icon}</span>
        )}
      </div>
      <motion.span
        className={`text-3xl font-bold ${colorMap[color]}`}
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        {value}
      </motion.span>
      {subtitle && (
        <span className="text-xs text-text-secondary">{subtitle}</span>
      )}
    </div>
  );
}
