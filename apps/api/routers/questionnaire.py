"""
Questionnaire API router.
"""

from fastapi import APIRouter

from modules.questionnaire import QUESTIONS, PROFILE_DESCRIPTIONS, score_answers
from apps.api.models.schemas import (
    QuestionsResponse, Question, QuestionOption,
    QuestionnaireSubmitRequest, ProfileResult,
)

router = APIRouter(prefix="/api/questionnaire", tags=["questionnaire"])


@router.get("/questions", response_model=QuestionsResponse)
async def get_questions():
    """Return all 15 questionnaire questions."""
    questions = []
    for q in QUESTIONS:
        options = [
            QuestionOption(letter=letra, text=texto, scores=puntos)
            for letra, texto, puntos in q["opciones"]
        ]
        questions.append(Question(id=q["id"], text=q["texto"], options=options))

    return QuestionsResponse(questions=questions, total=len(questions))


@router.post("/submit", response_model=ProfileResult)
async def submit_questionnaire(req: QuestionnaireSubmitRequest):
    """Score questionnaire answers and return investor profile."""
    profile, scores = score_answers(req.answers)

    return ProfileResult(
        profile=profile,
        description=PROFILE_DESCRIPTIONS[profile],
        scores={k: v for k, v in scores.items() if v > 0},
    )
