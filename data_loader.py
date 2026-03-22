"""
Módulo 2 — Descarga de datos de mercado
=========================================
Descarga precios históricos y datos fundamentales de los componentes
de S&P 500, Eurostoxx 600 y Nikkei 225 usando yfinance.

También descarga:
  - Benchmarks: ^GSPC, ^STOXX, ^N225
  - Tasas libres de riesgo: ^TNX (US 10Y), proxy EUR y JPY
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
import time

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────
# ÍNDICES Y SUS COMPONENTES (tickers representativos)
# En producción, se usaría la lista completa de componentes.
# Aquí incluimos los principales de cada índice.
# ─────────────────────────────────────────────────────────────────

INDEX_CONFIG = {
    "sp500": {
        "benchmark": "^GSPC",
        "risk_free": "^TNX",         # US Treasury 10Y yield
        "region": "US",
        "currency": "USD",
        "label": "S&P 500",
    },
    "eurostoxx": {
        "benchmark": "^STOXX",
        "risk_free": None,           # Se aproxima con diferencial
        "region": "EU",
        "currency": "EUR",
        "label": "Eurostoxx 600",
    },
    "nikkei": {
        "benchmark": "^N225",
        "risk_free": None,           # Se aproxima con diferencial
        "region": "JP",
        "currency": "JPY",
        "label": "Nikkei 225",
    },
}

# Tickers representativos por índice (top liquidez)
# En la versión completa, se obtendrían dinámicamente de Wikipedia/fuentes
SP500_SAMPLE = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "UNH",
    "JNJ", "JPM", "V", "PG", "XOM", "HD", "MA", "CVX", "MRK", "ABBV",
    "PEP", "KO", "COST", "AVGO", "LLY", "WMT", "MCD", "CSCO", "TMO",
    "ACN", "ABT", "DHR", "NEE", "LIN", "TXN", "PM", "UNP", "RTX",
    "LOW", "HON", "INTC", "AMGN", "QCOM", "IBM", "CAT", "GS", "BA",
    "SBUX", "BLK", "MMM", "GE", "PFE",
]

EUROSTOXX_SAMPLE = [
    "ASML.AS", "MC.PA", "SAP.DE", "SIE.DE", "TTE.PA", "SAN.PA",
    "AIR.PA", "ALV.DE", "BNP.PA", "DTE.DE", "OR.PA", "ABI.BR",
    "IBE.MC", "INGA.AS", "BAS.DE", "ENEL.MI", "ISP.MI", "ADS.DE",
    "DG.PA", "MUV2.DE", "PHIA.AS", "KER.PA", "AI.PA", "CS.PA",
    "ENI.MI", "SU.PA", "BAYN.DE", "BMW.DE", "VOW3.DE", "FRE.DE",
    "SAN.MC", "BBVA.MC", "TEF.MC", "ITX.MC", "REP.MC",
]

NIKKEI_SAMPLE = [
    "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "6902.T",
    "4502.T", "7267.T", "9433.T", "6501.T", "6367.T", "8035.T",
    "4503.T", "7741.T", "9432.T", "6954.T", "8316.T", "4661.T",
    "3382.T", "7974.T", "2914.T", "8058.T", "6098.T", "4519.T",
    "8001.T", "6273.T", "7751.T", "9020.T", "1925.T", "6701.T",
]

STOCK_UNIVERSE = {
    "sp500": SP500_SAMPLE,
    "eurostoxx": EUROSTOXX_SAMPLE,
    "nikkei": NIKKEI_SAMPLE,
}


# ─────────────────────────────────────────────────────────────────
# FUNCIONES DE DESCARGA
# ─────────────────────────────────────────────────────────────────

def download_prices(
    tickers: List[str],
    start: str,
    end: str,
    progress: bool = True,
) -> pd.DataFrame:
    """
    Descarga precios de cierre ajustados para una lista de tickers.

    Returns:
        DataFrame con DatetimeIndex y una columna por ticker.
    """
    if progress:
        print(f"  Descargando {len(tickers)} tickers ({start} → {end})...")

    data = yf.download(
        tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
    )

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data[["Close"]]
        prices.columns = tickers[:1]

    # Eliminar tickers con demasiados NaN (> 20%)
    threshold = len(prices) * 0.2
    valid = prices.columns[prices.isnull().sum() < threshold]
    prices = prices[valid].ffill().dropna()

    if progress:
        print(f"  → {len(prices.columns)} tickers válidos, {len(prices)} días")

    return prices


def download_benchmark(
    index_key: str,
    start: str,
    end: str,
) -> pd.Series:
    """Descarga el benchmark de un índice."""
    cfg = INDEX_CONFIG[index_key]
    ticker = cfg["benchmark"]
    data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        return data["Close"].iloc[:, 0].ffill().dropna()
    return data["Close"].ffill().dropna()


def get_risk_free_rate(index_key: str) -> float:
    """
    Obtiene la tasa libre de riesgo anualizada para la región.
    Para EE.UU. usa ^TNX (Treasury 10Y).
    Para Europa y Japón, usa una aproximación.
    """
    if index_key == "sp500":
        try:
            tnx = yf.download("^TNX", period="5d", progress=False)
            if isinstance(tnx.columns, pd.MultiIndex):
                rate = tnx["Close"].iloc[-1, 0] / 100
            else:
                rate = tnx["Close"].iloc[-1] / 100
            return float(rate)
        except Exception:
            return 0.04  # fallback 4%
    elif index_key == "eurostoxx":
        return 0.025  # Bund 10Y aprox
    elif index_key == "nikkei":
        return 0.01   # JGB 10Y aprox
    return 0.03


def get_stock_info(tickers: List[str], progress: bool = True) -> pd.DataFrame:
    """
    Descarga información fundamental de las acciones:
    sector, market cap, dividend yield, etc.

    Returns:
        DataFrame con una fila por ticker.
    """
    if progress:
        print(f"  Descargando info fundamental de {len(tickers)} tickers...")

    records = []
    for i, ticker in enumerate(tickers):
        try:
            info = yf.Ticker(ticker).info
            records.append({
                "ticker": ticker,
                "name": info.get("shortName", ticker),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "dividend_yield": info.get("dividendYield", 0) or 0,
                "trailing_pe": info.get("trailingPE", None),
                "beta": info.get("beta", None),
                "currency": info.get("currency", "USD"),
            })
        except Exception:
            records.append({"ticker": ticker, "name": ticker})

        if progress and (i + 1) % 10 == 0:
            print(f"    ... {i+1}/{len(tickers)}")

    df = pd.DataFrame(records)
    df = df.set_index("ticker")
    return df


# ─────────────────────────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: CARGA COMPLETA
# ─────────────────────────────────────────────────────────────────

def load_market_data(
    period_years: int = 2,
    end_date: Optional[str] = None,
    indices: Optional[List[str]] = None,
    max_per_index: int = 50,
    progress: bool = True,
) -> Dict:
    """
    Carga completa de datos de mercado.

    Args:
        period_years: años de histórico (default 2)
        end_date: fecha final (default hoy)
        indices: lista de índices a cargar (default todos)
        max_per_index: máximo de tickers por índice
        progress: mostrar progreso

    Returns:
        dict con:
          'prices': {index_key: DataFrame de precios}
          'benchmarks': {index_key: Series de benchmark}
          'risk_free': {index_key: float}
          'stock_info': DataFrame con info fundamental
          'metadata': dict con fechas, conteos, etc.
    """
    if indices is None:
        indices = list(INDEX_CONFIG.keys())

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start_date = (datetime.strptime(end_date, "%Y-%m-%d") -
                  timedelta(days=period_years * 365)).strftime("%Y-%m-%d")

    if progress:
        print("\n" + "=" * 60)
        print("  MÓDULO 2 — DESCARGA DE DATOS DE MERCADO")
        print(f"  Periodo: {start_date} → {end_date}")
        print(f"  Índices: {', '.join(indices)}")
        print("=" * 60)

    all_prices = {}
    all_benchmarks = {}
    all_risk_free = {}
    all_tickers = []

    for idx in indices:
        if progress:
            print(f"\n--- {INDEX_CONFIG[idx]['label']} ---")

        tickers = STOCK_UNIVERSE[idx][:max_per_index]
        all_tickers.extend(tickers)

        # Precios
        prices = download_prices(tickers, start_date, end_date, progress)
        all_prices[idx] = prices

        # Benchmark
        if progress:
            print(f"  Descargando benchmark {INDEX_CONFIG[idx]['benchmark']}...")
        bench = download_benchmark(idx, start_date, end_date)
        all_benchmarks[idx] = bench

        # Tasa libre de riesgo
        rf = get_risk_free_rate(idx)
        all_risk_free[idx] = rf
        if progress:
            print(f"  Tasa libre de riesgo: {rf:.2%}")

    # Info fundamental (solo si hay pocos tickers para no saturar API)
    stock_info = None
    if len(all_tickers) <= 120 and progress:
        print(f"\n--- Información fundamental ---")
        stock_info = get_stock_info(all_tickers, progress)

    metadata = {
        "start_date": start_date,
        "end_date": end_date,
        "period_years": period_years,
        "indices": indices,
        "total_tickers": sum(len(p.columns) for p in all_prices.values()),
        "tickers_by_index": {k: list(v.columns) for k, v in all_prices.items()},
    }

    if progress:
        print(f"\n{'=' * 60}")
        print(f"  RESUMEN: {metadata['total_tickers']} acciones cargadas")
        for idx in indices:
            print(f"    {INDEX_CONFIG[idx]['label']:20s} → {len(all_prices[idx].columns)} acciones")
        print(f"{'=' * 60}")

    return {
        "prices": all_prices,
        "benchmarks": all_benchmarks,
        "risk_free": all_risk_free,
        "stock_info": stock_info,
        "metadata": metadata,
        "index_config": INDEX_CONFIG,
    }


if __name__ == "__main__":
    # Demo rápida con pocos tickers
    data = load_market_data(
        period_years=2,
        max_per_index=10,
        progress=True,
    )
