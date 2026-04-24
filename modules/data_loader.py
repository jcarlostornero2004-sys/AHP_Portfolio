"""
Módulo 2 — Descarga de datos de mercado
=========================================
Descarga precios históricos y datos fundamentales de los componentes
de S&P 500, Eurostoxx 600 y Nikkei 225 usando yfinance.

Los tickers se obtienen dinámicamente de Wikipedia en tiempo real,
con fallback a listas hardcodeadas si la descarga falla.

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
import threading

warnings.filterwarnings("ignore")


# ─────────────────────────────────────────────────────────────────
# ÍNDICES Y SUS COMPONENTES
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

# ─────────────────────────────────────────────────────────────────
# FALLBACK TICKER LISTS (used when live fetching fails)
# ─────────────────────────────────────────────────────────────────

SP500_FALLBACK = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "UNH",
    "JNJ", "JPM", "V", "PG", "XOM", "HD", "MA", "CVX", "MRK", "ABBV",
    "PEP", "KO", "COST", "AVGO", "LLY", "WMT", "MCD", "CSCO", "TMO",
    "ACN", "ABT", "DHR", "NEE", "LIN", "TXN", "PM", "UNP", "RTX",
    "LOW", "HON", "INTC", "AMGN", "QCOM", "IBM", "CAT", "GS", "BA",
    "SBUX", "BLK", "MMM", "GE", "PFE", "CRM", "AMD", "NFLX", "DIS",
    "NKE", "ORCL", "ADBE", "PYPL", "ISRG", "MDLZ", "ADP", "GILD",
    "BKNG", "CI", "VRTX", "ADI", "REGN", "LRCX", "KLAC", "NOW",
    "PANW", "SNPS", "CDNS", "MRVL", "FTNT", "ANET", "CME", "MCO",
    "SHW", "ITW", "MNST", "AZO", "ECL", "CTAS", "IDXX", "DXCM",
    "MSI", "PCAR", "ODFL", "CPRT", "PAYX", "FAST", "VRSK", "BKR",
    "EW", "BIIB", "GIS", "SYK", "ZTS", "BDX", "AJG", "HUM",
    "PSA", "APH", "AME", "ROP", "PH", "TDG", "FICO", "AXON",
    "MCHP", "ANSS", "FSLR", "ENPH", "ON", "NXPI", "SWKS", "MPWR",
    "STZ", "DDOG", "ZS", "CRWD", "TTD", "TEAM", "MDB", "SNOW",
    "NET", "DASH", "COIN", "ABNB", "UBER", "LYFT", "SQ", "SHOP",
    "WDAY", "OKTA", "SPLK", "BILL", "HUBS", "VEEV", "CPNG", "PINS",
    "RIVN", "LCID", "F", "GM", "TM", "TSLA", "BAC", "WFC", "C",
    "MS", "SCHW", "USB", "PNC", "TFC", "AIG", "MET", "PRU", "AFL",
    "ALL", "TRV", "CB", "AON", "MMC", "SPGI", "ICE", "MSCI",
    "CMG", "YUM", "DPZ", "SBUX", "HLT", "MAR", "LVS", "WYNN",
    "CL", "EL", "KMB", "CHD", "CLX", "SJM", "HSY", "CPB",
    "SO", "DUK", "AEP", "D", "EXC", "SRE", "XEL", "WEC", "ES",
    "AWK", "AMT", "PLD", "CCI", "EQIX", "DLR", "SPG", "O", "VTR",
    "DE", "EMR", "ROK", "DOV", "GWW", "SWK", "FTV", "IR",
    "LMT", "RTX", "NOC", "GD", "HII", "LHX", "TDG", "HWM",
    "CVS", "MCK", "CAH", "ABC", "COR", "WST", "MTD", "A",
]

EUROSTOXX_FALLBACK = [
    "ASML.AS", "MC.PA", "SAP.DE", "SIE.DE", "TTE.PA", "SAN.PA",
    "AIR.PA", "ALV.DE", "BNP.PA", "DTE.DE", "OR.PA", "ABI.BR",
    "IBE.MC", "INGA.AS", "BAS.DE", "ENEL.MI", "ISP.MI", "ADS.DE",
    "DG.PA", "MUV2.DE", "PHIA.AS", "KER.PA", "AI.PA", "CS.PA",
    "ENI.MI", "SU.PA", "BAYN.DE", "BMW.DE", "VOW3.DE", "FRE.DE",
    "SAN.MC", "BBVA.MC", "TEF.MC", "ITX.MC", "REP.MC",
    "RMS.PA", "EL.PA", "CDI.PA", "BN.PA", "RI.PA", "SGO.PA",
    "VIV.PA", "DSY.PA", "HO.PA", "SW.PA", "ML.PA", "ORA.PA",
    "GLE.PA", "CA.PA", "LR.PA", "RNO.PA", "STM.PA", "ACA.PA",
    "MBG.DE", "DBK.DE", "DB1.DE", "IFX.DE", "HEN3.DE", "LIN.DE",
    "RWE.DE", "EON.DE", "FME.DE", "MTX.DE", "HEI.DE", "SHL.DE",
    "BEI.DE", "VNA.DE", "1COV.DE", "PAH3.DE", "ZAL.DE", "PUM.DE",
    "UCG.MI", "G.MI", "STLA.MI", "RACE.MI", "TEN.MI", "LDO.MI",
    "MONC.MI", "AMP.MI", "MB.MI", "BAMI.MI", "PST.MI", "CPR.MI",
    "AMS.MC", "CLNX.MC", "GRF.MC", "FER.MC", "CABK.MC", "MAP.MC",
    "ACX.MC", "ENG.MC", "ANA.MC", "CIE.MC", "VIS.MC", "COL.MC",
    "AGN.AS", "HEIA.AS", "WKL.AS", "DSM.AS", "AKZA.AS", "UNA.AS",
    "KPN.AS", "RAND.AS", "AD.AS", "NN.AS", "ASR.AS", "BESI.AS",
    "UCB.BR", "SOLB.BR", "KBC.BR", "COLR.BR", "ACKB.BR", "GBLB.BR",
]

NIKKEI_FALLBACK = [
    "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "6902.T",
    "4502.T", "7267.T", "9433.T", "6501.T", "6367.T", "8035.T",
    "4503.T", "7741.T", "9432.T", "6954.T", "8316.T", "4661.T",
    "3382.T", "7974.T", "2914.T", "8058.T", "6098.T", "4519.T",
    "8001.T", "6273.T", "7751.T", "9020.T", "1925.T", "6701.T",
    "6594.T", "4568.T", "6326.T", "4901.T", "6752.T", "4063.T",
    "6762.T", "7269.T", "8031.T", "8766.T", "8411.T", "3407.T",
    "5401.T", "4452.T", "7201.T", "6301.T", "2802.T", "9531.T",
    "8801.T", "9022.T", "9021.T", "4578.T", "6503.T", "4151.T",
    "3402.T", "6471.T", "6504.T", "8725.T", "8750.T", "9735.T",
    "2413.T", "4704.T", "4543.T", "9613.T", "2801.T", "6981.T",
    "7832.T", "9101.T", "9104.T", "7733.T", "3861.T", "4911.T",
    "6645.T", "7731.T", "6988.T", "8002.T", "8053.T", "8015.T",
]


# ─────────────────────────────────────────────────────────────────
# DYNAMIC TICKER FETCHING (real-time from Wikipedia)
# ─────────────────────────────────────────────────────────────────

# Cache for fetched tickers (thread-safe)
_ticker_cache: Dict[str, List[str]] = {}
_cache_lock = threading.Lock()
_cache_timestamp: Optional[float] = None
_CACHE_TTL = 3600  # Re-fetch every hour


def _wiki_read_html(url: str) -> list:
    """Read HTML tables from Wikipedia with proper headers to avoid 403."""
    import urllib.request
    from io import StringIO
    req = urllib.request.Request(url, headers={"User-Agent": "AHP-Portfolio/2.0 (educational project)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8")
    return pd.read_html(StringIO(html))


def fetch_sp500_tickers() -> List[str]:
    """Fetch S&P 500 components from Wikipedia in real time."""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = _wiki_read_html(url)
        df = tables[0]
        tickers = df["Symbol"].tolist()
        # Clean tickers: BRK.B → BRK-B (Yahoo Finance format)
        tickers = [t.replace(".", "-") for t in tickers]
        print(f"  [Live] Fetched {len(tickers)} S&P 500 tickers from Wikipedia")
        return tickers
    except Exception as e:
        print(f"  [Fallback] S&P 500 fetch failed ({e}), using {len(SP500_FALLBACK)} fallback tickers")
        return SP500_FALLBACK


def fetch_eurostoxx_tickers() -> List[str]:
    """Fetch Euro Stoxx 50 components from Wikipedia, extended with major European stocks."""
    try:
        url = "https://en.wikipedia.org/wiki/EURO_STOXX_50"
        tables = _wiki_read_html(url)
        tickers = []
        for table in tables:
            cols = [str(c).lower() for c in table.columns]
            if "ticker" in cols:
                idx = cols.index("ticker")
                tickers = table.iloc[:, idx].astype(str).tolist()
                break
            elif "symbol" in cols:
                idx = cols.index("symbol")
                tickers = table.iloc[:, idx].astype(str).tolist()
                break
        if tickers and len(tickers) >= 10:
            clean = [t.strip() for t in tickers if isinstance(t, str) and "." in t and len(t) < 15]
            print(f"  [Live] Fetched {len(clean)} Euro Stoxx 50 tickers from Wikipedia")
            # Supplement with our larger fallback list for broader European coverage
            combined = list(dict.fromkeys(clean + EUROSTOXX_FALLBACK))
            return combined
        raise ValueError("Could not find Ticker column in Euro Stoxx tables")
    except Exception as e:
        print(f"  [Fallback] Euro Stoxx fetch failed ({e}), using {len(EUROSTOXX_FALLBACK)} fallback tickers")
        return EUROSTOXX_FALLBACK


def fetch_nikkei_tickers() -> List[str]:
    """Fetch Nikkei 225 components. Tries Wikipedia's component list page, falls back to hardcoded."""
    try:
        # The main Nikkei 225 page doesn't list components in a table.
        # Try the dedicated components list page instead.
        url = "https://en.wikipedia.org/wiki/Nikkei_225#Components"
        tables = _wiki_read_html(url)
        tickers = []
        for table in tables:
            cols = [str(c).lower() for c in table.columns]
            for i, col in enumerate(cols):
                if "code" in col or "ticker" in col or "symbol" in col:
                    codes = table.iloc[:, i].astype(str).tolist()
                    tickers = [f"{c.strip()}.T" for c in codes if c.strip().isdigit() and len(c.strip()) == 4]
                    break
            if tickers and len(tickers) >= 50:
                break
        if tickers and len(tickers) >= 50:
            print(f"  [Live] Fetched {len(tickers)} Nikkei 225 tickers from Wikipedia")
            return tickers
        # Wikipedia doesn't have a components table for Nikkei — use expanded fallback
        print(f"  [Fallback] Nikkei components not in table format, using {len(NIKKEI_FALLBACK)} curated tickers")
        return NIKKEI_FALLBACK
    except Exception as e:
        print(f"  [Fallback] Nikkei fetch failed ({e}), using {len(NIKKEI_FALLBACK)} fallback tickers")
        return NIKKEI_FALLBACK


def get_live_universe(force_refresh: bool = False) -> Dict[str, List[str]]:
    """
    Get the full stock universe by fetching tickers from live sources.
    Results are cached for 1 hour to avoid hammering Wikipedia.
    Falls back to hardcoded lists on failure.
    """
    global _ticker_cache, _cache_timestamp

    with _cache_lock:
        now = time.time()
        if (not force_refresh
                and _ticker_cache
                and _cache_timestamp
                and (now - _cache_timestamp) < _CACHE_TTL):
            return _ticker_cache

    print("\n[Universe] Fetching live stock universe from web sources...")
    universe = {
        "sp500": fetch_sp500_tickers(),
        "eurostoxx": fetch_eurostoxx_tickers(),
        "nikkei": fetch_nikkei_tickers(),
    }

    total = sum(len(v) for v in universe.values())
    print(f"[Universe] Total: {total} tickers across {len(universe)} indices\n")

    with _cache_lock:
        _ticker_cache = universe
        _cache_timestamp = time.time()

    return universe


# Backward-compatible aliases (point to fallback lists for static imports)
SP500_SAMPLE = SP500_FALLBACK
EUROSTOXX_SAMPLE = EUROSTOXX_FALLBACK
NIKKEI_SAMPLE = NIKKEI_FALLBACK

# Default STOCK_UNIVERSE uses fallback; call get_live_universe() for real-time
STOCK_UNIVERSE = {
    "sp500": SP500_FALLBACK,
    "eurostoxx": EUROSTOXX_FALLBACK,
    "nikkei": NIKKEI_FALLBACK,
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
        timeout=30,
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
    data = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False, timeout=30)
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
            tnx = yf.download("^TNX", period="5d", progress=False, timeout=10)
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

    # Fetch tickers dynamically from live sources
    live_universe = get_live_universe()

    for idx in indices:
        if progress:
            print(f"\n--- {INDEX_CONFIG[idx]['label']} ---")

        tickers = live_universe.get(idx, STOCK_UNIVERSE[idx])[:max_per_index]
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
    if len(all_tickers) <= 500 and progress:
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
