import { create } from "zustand";
import { persist } from "zustand/middleware";
import { useEffect } from "react";

type Theme = "dark" | "light";

interface ThemeStore {
  theme: Theme;
  toggle: () => void;
}

const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: "dark",
      toggle: () => set((s) => ({ theme: s.theme === "dark" ? "light" : "dark" })),
    }),
    { name: "ahp-theme" }
  )
);

export function useTheme() {
  const { theme, toggle } = useThemeStore();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  return { theme, toggle };
}
