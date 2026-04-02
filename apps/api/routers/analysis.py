"""
Analysis API router — runs the full AHP pipeline.
"""

import asyncio
from fastapi import APIRouter, HTTPException

from apps.api.models.schemas import AnalysisRequest, QuestionnaireSubmitRequest
from apps.api.services.pipeline import run_analysis_pipeline, run_full_pipeline

router = APIRouter(prefix="/api", tags=["analysis"])

# In-memory cache for last pipeline result
_last_result: dict = {}


@router.post("/analyze")
async def analyze(req: AnalysisRequest):
    """Run the full AHP pipeline for a given profile."""
    global _last_result

    try:
        result = await asyncio.to_thread(
            run_analysis_pipeline, req.profile, req.use_live
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error en el pipeline: {exc}")

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Pipeline failed"))

    _last_result = result

    # Strip internal data before returning
    response = {k: v for k, v in result.items() if not k.startswith("_")}
    return response


@router.post("/analyze/full")
async def analyze_full(req: QuestionnaireSubmitRequest):
    """Run the full pipeline from questionnaire answers (combines submit + analyze)."""
    global _last_result

    try:
        result = await asyncio.to_thread(
            run_full_pipeline, req.answers, True
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Error en el pipeline: {exc}")

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Pipeline failed"))

    _last_result = result

    response = {k: v for k, v in result.items() if not k.startswith("_")}
    return response


def get_last_result() -> dict:
    """Access the last pipeline result (used by other routers)."""
    return _last_result
