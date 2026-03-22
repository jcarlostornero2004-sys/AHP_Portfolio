"""
Portfolio API router — cached pipeline results.
"""

from fastapi import APIRouter, HTTPException
from apps.api.routers.analysis import get_last_result

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/results")
async def portfolio_results():
    """Return the most recent pipeline results."""
    result = get_last_result()
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No analysis results available. Run the questionnaire first.",
        )

    response = {k: v for k, v in result.items() if not k.startswith("_")}
    return response
