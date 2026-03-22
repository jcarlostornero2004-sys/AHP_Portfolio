"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AnalysisResponse, ProfileResult } from "../types";

interface ProfileState {
  // Questionnaire answers
  answers: Record<string, string>;
  setAnswer: (questionId: string, letter: string) => void;
  clearAnswers: () => void;

  // Profile result
  profileResult: ProfileResult | null;
  setProfileResult: (result: ProfileResult) => void;

  // Analysis results
  analysisResult: AnalysisResponse | null;
  setAnalysisResult: (result: AnalysisResponse) => void;

  // Loading state
  isAnalyzing: boolean;
  setIsAnalyzing: (loading: boolean) => void;
}

export const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      answers: {},
      setAnswer: (questionId, letter) =>
        set((state) => ({
          answers: { ...state.answers, [questionId]: letter },
        })),
      clearAnswers: () => set({ answers: {}, profileResult: null, analysisResult: null }),

      profileResult: null,
      setProfileResult: (result) => set({ profileResult: result }),

      analysisResult: null,
      setAnalysisResult: (result) => set({ analysisResult: result }),

      isAnalyzing: false,
      setIsAnalyzing: (loading) => set({ isAnalyzing: loading }),
    }),
    {
      name: "ahp-profile-storage",
    }
  )
);
