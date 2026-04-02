"""
FastAPI application — AHP Portfolio Selector API.
"""

import sys
import os
import asyncio
from contextlib import asynccontextmanager

# Ensure project root is in Python path for module imports
# Works both when run from project root (python -m apps.api.main) and
# from apps/api/ directory (uvicorn main:app)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.config import settings
from apps.api.routers import questionnaire, analysis, market, stocks, portfolio, backtest, export, report
from apps.api.ws.prices import router as ws_router
from apps.api.services.market_data import poll_market_data
from apps.api.services.ws_manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: start background tasks."""
    # Start background market data polling
    poll_task = asyncio.create_task(poll_market_data())
    print(f"[AHP API] Background market polling started (every {settings.ws_poll_interval_seconds}s)")
    yield
    # Cleanup
    poll_task.cancel()
    try:
        await poll_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title=settings.app_name,
    description="Real-time investor platform with AHP multi-criteria portfolio selection",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(questionnaire.router)
app.include_router(analysis.router)
app.include_router(market.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(backtest.router)
app.include_router(export.router)
app.include_router(report.router)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "questionnaire": "/api/questionnaire/questions",
            "analyze": "/api/analyze",
            "market": "/api/market/overview",
            "heatmap": "/api/market/heatmap",
            "sentiment": "/api/market/sentiment",
            "portfolio": "/api/portfolio/results",
            "backtest": "/api/backtest",
            "websocket": "/ws/prices",
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
