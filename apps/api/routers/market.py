"""
Market data API router — overview, heatmap, sentiment.
"""

from fastapi import APIRouter
from apps.api.services.market_data import get_market_overview, get_heatmap_data, get_sentiment

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/overview")
async def market_overview():
    """Return current stock prices and changes for all tracked tickers."""
    return get_market_overview()


@router.get("/heatmap")
async def market_heatmap():
    """Return sector-grouped stock data for treemap visualization."""
    return get_heatmap_data()


@router.get("/sentiment")
async def market_sentiment():
    """Return computed fear/greed index."""
    return get_sentiment()
