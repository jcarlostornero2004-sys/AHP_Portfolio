"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { getQuestions, submitQuestionnaire, runAnalysis } from "../lib/api";
import { useProfileStore } from "../hooks/useProfile";
import { Button } from "../components/ui/Button";
import { Progress } from "../components/ui/Progress";
import { PROFILE_COLORS, PROFILE_LABELS } from "../lib/constants";

export default function QuestionnairePage() {
  const router = useRouter();
  const [currentQ, setCurrentQ] = useState(0);
  const [showReveal, setShowReveal] = useState(false);
  const {
    answers,
    setAnswer,
    clearAnswers,
    profileResult,
    setProfileResult,
    setAnalysisResult,
    isAnalyzing,
    setIsAnalyzing,
  } = useProfileStore();

  const { data: questionsData, isLoading, isError } = useQuery({
    queryKey: ["questions"],
    queryFn: getQuestions,
    retry: 2,
  });

  const questions = questionsData?.questions ?? [];
  const currentQuestion = questions[currentQ];
  const totalQuestions = questions.length;
  const progress = totalQuestions > 0 ? ((currentQ + 1) / totalQuestions) * 100 : 0;
  const allAnswered = questions.length > 0 && questions.every((q) => answers[q.id]);

  // Clear stale answers when question IDs change (e.g. after a questionnaire update)
  useEffect(() => {
    if (questions.length === 0) return;
    const questionIds = new Set(questions.map((q) => q.id));
    const hasStale = Object.keys(answers).some((id) => !questionIds.has(id));
    if (hasStale) clearAnswers();
  }, [questions]);

  const handleSelect = (questionId: string, letter: string) => {
    setAnswer(questionId, letter);
    if (currentQ < totalQuestions - 1) {
      setTimeout(() => setCurrentQ(currentQ + 1), 300);
    }
  };

  const handleSubmit = async () => {
    try {
      const result = await submitQuestionnaire(answers);
      setProfileResult(result);
      setShowReveal(true);

      setIsAnalyzing(true);
      try {
        const analysis = await runAnalysis(result.profile, true);
        setAnalysisResult(analysis);
      } catch {
        const analysis = await runAnalysis(result.profile, false);
        setAnalysisResult(analysis);
      } finally {
        setIsAnalyzing(false);
      }
    } catch (error) {
      console.error("Error submitting:", error);
    }
  };

  const handleGoToDashboard = () => {
    router.push("/dashboard");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-accent-blue border-t-transparent rounded-full animate-spin" />
          <p className="text-text-secondary">Cargando cuestionario...</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary">
        <div className="flex flex-col items-center gap-4 text-center px-4">
          <p className="text-accent-red font-medium">No se pudo conectar con el servidor.</p>
          <p className="text-text-secondary text-sm">
            Asegúrate de que el backend está corriendo en el puerto 8000 y recarga la página.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="mt-2 px-4 py-2 bg-accent-blue text-white rounded-lg text-sm cursor-pointer"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  // Profile reveal screen
  if (showReveal && profileResult) {
    const profileColor = PROFILE_COLORS[profileResult.profile] || "#3b82f6";
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-primary px-4">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="max-w-lg w-full"
        >
          <div
            className="rounded-2xl p-8 text-center border border-border"
            style={{ background: `linear-gradient(135deg, ${profileColor}20, ${profileColor}05)` }}
          >
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              <p className="text-sm text-text-secondary uppercase tracking-widest mb-2">
                Your Investor Profile
              </p>
              <h1
                className="text-5xl font-bold mb-4"
                style={{ color: profileColor }}
              >
                {PROFILE_LABELS[profileResult.profile] || profileResult.profile}
              </h1>
              <p className="text-text-secondary text-sm leading-relaxed mb-8">
                {profileResult.description}
              </p>

              <div className="space-y-2 mb-8">
                {Object.entries(profileResult.scores)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 4)
                  .map(([name, score]) => (
                    <div key={name} className="flex items-center gap-3">
                      <span className="text-xs text-text-secondary w-24 text-right">
                        {PROFILE_LABELS[name] || name}
                      </span>
                      <div className="flex-1 h-2 bg-bg-tertiary rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${(score / 50) * 100}%` }}
                          transition={{ delay: 0.5, duration: 0.8 }}
                          className="h-full rounded-full"
                          style={{
                            backgroundColor:
                              name === profileResult.profile ? profileColor : "#30363d",
                          }}
                        />
                      </div>
                      <span className="text-xs text-text-secondary w-8">{score}pts</span>
                    </div>
                  ))}
              </div>

              {isAnalyzing ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-8 h-8 border-3 border-accent-blue border-t-transparent rounded-full animate-spin" />
                  <p className="text-sm text-text-secondary">
                    Analyzing markets and building your portfolio...
                  </p>
                </div>
              ) : (
                <Button size="lg" onClick={handleGoToDashboard}>
                  View Your Dashboard
                </Button>
              )}
            </motion.div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Questionnaire
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-bg-primary px-4">
      <div className="w-full max-w-xl mb-8">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-lg font-semibold">AHP Portfolio Selector</h1>
          <span className="text-sm text-text-secondary">
            {currentQ + 1} / {totalQuestions}
          </span>
        </div>
        <Progress value={progress} />
      </div>

      <div className="w-full max-w-xl">
        <AnimatePresence mode="wait">
          {currentQuestion && (
            <motion.div
              key={currentQuestion.id}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.3 }}
              className="bg-bg-secondary border border-border rounded-2xl p-8"
            >
              <h2 className="text-xl font-semibold mb-6 leading-relaxed">
                {currentQuestion.text}
              </h2>

              <div className="space-y-3">
                {currentQuestion.options.map((opt) => {
                  const isSelected = answers[currentQuestion.id] === opt.letter;
                  return (
                    <button
                      key={opt.letter}
                      onClick={() => handleSelect(currentQuestion.id, opt.letter)}
                      className={`w-full text-left px-5 py-4 rounded-xl border transition-all duration-200 cursor-pointer ${
                        isSelected
                          ? "border-accent-blue bg-accent-blue/10 text-text-primary"
                          : "border-border bg-bg-tertiary/50 text-text-secondary hover:border-accent-blue/50 hover:bg-bg-tertiary"
                      }`}
                    >
                      <span
                        className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-medium mr-3 ${
                          isSelected
                            ? "bg-accent-blue text-white"
                            : "bg-bg-tertiary text-text-secondary"
                        }`}
                      >
                        {opt.letter.toUpperCase()}
                      </span>
                      {opt.text}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex justify-between mt-6">
          <Button
            variant="ghost"
            onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
            disabled={currentQ === 0}
          >
            Previous
          </Button>

          {currentQ < totalQuestions - 1 ? (
            <Button
              onClick={() => setCurrentQ(currentQ + 1)}
              disabled={!answers[currentQuestion?.id]}
            >
              Next
            </Button>
          ) : (
            <Button onClick={handleSubmit} disabled={!allAnswered || isAnalyzing}>
              {isAnalyzing ? "Analyzing..." : "See Results"}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
