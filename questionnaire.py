"""
Módulo 0 — Cuestionario de perfil del inversor (root shim)
===========================================================
Re-exporta desde modules.questionnaire para compatibilidad con código legacy.
"""

from modules.questionnaire import (
    QUESTIONS,
    PROFILES_ORDER,
    PROFILE_DESCRIPTIONS,
    score_answers,
    run_questionnaire,
)

__all__ = [
    "QUESTIONS",
    "PROFILES_ORDER",
    "PROFILE_DESCRIPTIONS",
    "score_answers",
    "run_questionnaire",
]
