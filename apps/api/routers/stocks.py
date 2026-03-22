"""
Stocks API router — individual stock detail + history.
"""

import asyncio
from fastapi import APIRouter, HTTPException

from apps.api.services.market_data import get_stock_price, ALL_TICKERS

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("/{ticker}")
async def stock_detail(ticker: str):
    """Return detailed stock info and current price."""
    cached = get_stock_price(ticker.upper())
    if cached:
        return {
            "ticker": ticker.upper(),
            "name": cached.get("name", ticker),
            "sector": cached.get("sector", ""),
            "index": cached.get("index", ""),
            "price": cached.get("price", 0),
            "change_1d": cached.get("change_1d", 0),
            "indicators": {},
            "history": [],
        }

    raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found")


@router.get("/{ticker}/history")
async def stock_history(ticker: str, period: str = "6mo"):
    """Return price history for charting."""
    try:
        import yfinance as yf
        data = await asyncio.to_thread(
            lambda: yf.download(ticker, period=period, progress=False)
        )
        if data.empty:
            raise HTTPException(status_code=404, detail="No data available")

        history = []
        for date, row in data.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row.get("Open", 0)), 2),
                "high": round(float(row.get("High", 0)), 2),
                "low": round(float(row.get("Low", 0)), 2),
                "close": round(float(row.get("Close", 0)), 2),
                "volume": int(row.get("Volume", 0)),
            })

        return {"ticker": ticker.upper(), "data": history}

    except ImportError:
        raise HTTPException(status_code=503, detail="yfinance not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
