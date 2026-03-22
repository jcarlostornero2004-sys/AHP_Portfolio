"""
Market data service — background polling + in-memory cache.
Provides real-time(ish) stock prices for the market overview.
Tickers are fetched dynamically from live sources via data_loader.
"""

import asyncio
import time
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from modules.data_loader import get_live_universe


# In-memory cache
_cache: dict = {
    "stocks": {},
    "last_updated": None,
    "is_live": False,
}

# Dynamically populated on first use
_universe_loaded = False
STOCK_UNIVERSE: dict = {}
ALL_TICKERS: list = []
TICKER_INDEX: dict = {}


def _ensure_universe():
    """Load stock universe from live sources (once, then cached in data_loader)."""
    global _universe_loaded, STOCK_UNIVERSE, ALL_TICKERS, TICKER_INDEX
    if _universe_loaded:
        return
    STOCK_UNIVERSE = get_live_universe()
    ALL_TICKERS = []
    for tickers in STOCK_UNIVERSE.values():
        ALL_TICKERS.extend(tickers)
    TICKER_INDEX = {}
    for idx, tickers in STOCK_UNIVERSE.items():
        for t in tickers:
            TICKER_INDEX[t] = idx
    _universe_loaded = True


async def poll_market_data():
    """Background task that polls yfinance for current prices."""
    # Load universe on first poll (runs in thread to avoid blocking)
    await asyncio.to_thread(_ensure_universe)
    while True:
        try:
            await asyncio.to_thread(_fetch_all_prices)
        except Exception as e:
            print(f"[market_data] Poll error: {e}")
        await asyncio.sleep(30)


def _fetch_all_prices():
    """Synchronous yfinance fetch — runs in thread pool."""
    _ensure_universe()
    try:
        import yfinance as yf

        data = yf.download(
            ALL_TICKERS,
            period="8d",
            interval="1d",
            progress=False,
            threads=True,
        )

        if data.empty:
            return

        close = data["Close"] if "Close" in data.columns else data.get("Adj Close", data)

        stocks = {}
        for ticker in ALL_TICKERS:
            try:
                if ticker not in close.columns:
                    continue
                series = close[ticker].dropna()
                if len(series) < 2:
                    continue

                current_price = float(series.iloc[-1])
                prev_price = float(series.iloc[-2])
                change_1d = (current_price - prev_price) / prev_price

                # 7-day sparkline
                sparkline = series.tail(7).tolist()

                # 7-day change
                if len(series) >= 7:
                    price_7d_ago = float(series.iloc[-7])
                    change_7d = (current_price - price_7d_ago) / price_7d_ago
                else:
                    change_7d = change_1d

                stocks[ticker] = {
                    "ticker": ticker,
                    "name": ticker,
                    "price": round(current_price, 2),
                    "change_1d": round(change_1d * 100, 2),
                    "change_7d": round(change_7d * 100, 2),
                    "market_cap": None,
                    "volume": None,
                    "sector": "",
                    "index": TICKER_INDEX.get(ticker, ""),
                    "sparkline": [round(float(v), 2) for v in sparkline],
                }
            except Exception:
                continue

        if stocks:
            _cache["stocks"] = stocks
            _cache["last_updated"] = datetime.now().isoformat()
            _cache["is_live"] = True

    except ImportError:
        print("[market_data] yfinance not available, generating synthetic prices")
        _generate_synthetic_prices()
    except Exception as e:
        print(f"[market_data] Fetch error: {e}")
        if not _cache["stocks"]:
            _generate_synthetic_prices()


def _generate_synthetic_prices():
    """Generate mock prices when yfinance is unavailable."""
    _ensure_universe()
    np.random.seed(42)
    stocks = {}
    for ticker in ALL_TICKERS:
        base_price = np.random.uniform(50, 500)
        change_1d = np.random.uniform(-5, 5)
        change_7d = np.random.uniform(-10, 10)
        sparkline = [round(base_price * (1 + np.random.uniform(-0.03, 0.03)), 2) for _ in range(7)]

        stocks[ticker] = {
            "ticker": ticker,
            "name": ticker,
            "price": round(base_price, 2),
            "change_1d": round(change_1d, 2),
            "change_7d": round(change_7d, 2),
            "market_cap": round(np.random.uniform(10e9, 3e12), 0),
            "volume": int(np.random.uniform(1e6, 100e6)),
            "sector": "",
            "index": TICKER_INDEX.get(ticker, ""),
            "sparkline": sparkline,
        }

    _cache["stocks"] = stocks
    _cache["last_updated"] = datetime.now().isoformat()
    _cache["is_live"] = False


def get_market_overview() -> dict:
    """Return current market data from cache."""
    if not _cache["stocks"]:
        _generate_synthetic_prices()

    return {
        "stocks": list(_cache["stocks"].values()),
        "last_updated": _cache["last_updated"] or datetime.now().isoformat(),
        "is_live": _cache["is_live"],
    }


def get_heatmap_data() -> dict:
    """Return data formatted for treemap heatmap."""
    if not _cache["stocks"]:
        _generate_synthetic_prices()

    entries = []
    for ticker, data in _cache["stocks"].items():
        entries.append({
            "ticker": ticker,
            "name": data.get("name", ticker),
            "sector": data.get("sector", "Unknown"),
            "market_cap": data.get("market_cap") or np.random.uniform(10e9, 3e12),
            "daily_change": data.get("change_1d", 0),
            "index": data.get("index", ""),
        })

    return {
        "entries": entries,
        "last_updated": _cache["last_updated"] or datetime.now().isoformat(),
    }


def get_sentiment() -> dict:
    """Compute a simple fear/greed index from market data."""
    if not _cache["stocks"]:
        _generate_synthetic_prices()

    changes = [s.get("change_1d", 0) for s in _cache["stocks"].values()]
    if not changes:
        return {"fear_greed_index": 50, "label": "Neutral", "components": {}}

    avg_change = np.mean(changes)
    positive_pct = sum(1 for c in changes if c > 0) / len(changes) * 100

    # Simple index: 0 = extreme fear, 100 = extreme greed
    index = int(np.clip(50 + avg_change * 10 + (positive_pct - 50) * 0.5, 0, 100))

    if index <= 20:
        label = "Extreme Fear"
    elif index <= 40:
        label = "Fear"
    elif index <= 60:
        label = "Neutral"
    elif index <= 80:
        label = "Greed"
    else:
        label = "Extreme Greed"

    return {
        "fear_greed_index": index,
        "label": label,
        "components": {
            "avg_daily_change": round(avg_change, 2),
            "positive_stocks_pct": round(positive_pct, 1),
            "n_stocks_tracked": len(changes),
        },
    }


def get_stock_price(ticker: str) -> Optional[dict]:
    """Get cached price data for a single ticker."""
    return _cache["stocks"].get(ticker)
