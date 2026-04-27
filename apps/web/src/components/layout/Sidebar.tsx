"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { useProfileStore } from "../../hooks/useProfile";
import { PROFILE_COLORS, PROFILE_LABELS } from "../../lib/constants";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { href: "/market", label: "Mercado", icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" },
  { href: "/heatmap", label: "Mapa de Calor", icon: "M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" },
  { href: "/portfolio", label: "Cartera", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { href: "/backtest", label: "Backtest", icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" },
  { href: "/report", label: "Informe", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { href: "/", label: "Inicio", icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { profileResult } = useProfileStore();

  const profileColor = profileResult
    ? PROFILE_COLORS[profileResult.profile] || "#3b82f6"
    : null;
  const profileLabel = profileResult
    ? PROFILE_LABELS[profileResult.profile] || profileResult.profile
    : null;

  return (
    <aside
      className="fixed left-0 top-0 h-full w-64 border-r border-border flex flex-col z-40"
      style={{ background: "linear-gradient(180deg, #161b22 0%, #0d1117 100%)" }}
    >
      {/* Logo */}
      <Link href="/" className="flex items-center gap-3 px-6 py-5 border-b border-border relative">
        {/* Subtle glow line under logo area */}
        <div
          className="absolute bottom-0 left-6 right-6 h-px opacity-30"
          style={{ background: "linear-gradient(90deg, transparent, #3b82f6, transparent)" }}
        />
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0"
          style={{ background: "linear-gradient(135deg, #3b82f6, #06b6d4)" }}
        >
          {/* Stylized upward chart arc */}
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M2 13 L6 8 L10 10 L15 4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 4 H15 V7" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div>
          <h1 className="text-sm font-bold text-text-primary leading-tight">AHP Invest</h1>
          <p className="text-[10px] text-text-secondary">Robo Advisor</p>
        </div>
        {/* LIVE badge */}
        <div className="ml-auto flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-green pulse-live" />
          <span className="text-[9px] text-accent-green font-semibold tracking-wider">LIVE</span>
        </div>
      </Link>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map((item, index) => {
          const isActive = pathname === item.href;
          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: index * 0.05 }}
            >
              <Link
                href={item.href}
                className={`relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-accent-blue/15 text-accent-blue"
                    : "text-text-secondary hover:text-text-primary hover:bg-bg-tertiary"
                }`}
              >
                {/* Left accent bar when active */}
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-r bg-accent-blue" />
                )}
                <svg
                  className="w-5 h-5 shrink-0"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                </svg>
                {item.label}
              </Link>
            </motion.div>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-border space-y-3">
        {profileResult && profileColor && profileLabel && (
          <div className="flex items-center gap-2 px-1">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: profileColor }}
            />
            <span className="text-xs text-text-secondary truncate">
              Perfil:{" "}
              <span style={{ color: profileColor }} className="font-semibold">
                {profileLabel}
              </span>
            </span>
          </div>
        )}
        <Link
          href="/questionnaire"
          className="flex items-center gap-2 text-xs text-text-secondary hover:text-accent-blue transition-colors"
        >
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Reiniciar Cuestionario
        </Link>
      </div>
    </aside>
  );
}
