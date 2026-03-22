"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ─── Questionnaire ───

class QuestionOption(BaseModel):
    letter: str
    text: str
    scores: dict[str, int]


class Question(BaseModel):
    id: str
    text: str
    options: list[QuestionOption]


class QuestionsResponse(BaseModel):
    questions: list[Question]
    total: int


class QuestionnaireSubmitRequest(BaseModel):
    answers: dict[str, str] = Field(
        ..., description="Map of question_id to answer letter (a/b/c/d)"
    )


class ProfileResult(BaseModel):
    profile: str
    description: str
    scores: dict[str, int]


# ─── Analysis ───

class AnalysisRequest(BaseModel):
    profile: str
    use_live: bool = True


class CriterionInfo(BaseModel):
    name: str
    weight: int
    direction: str


class RankingEntry(BaseModel):
    name: str
    score: float
    rank: int


class PortfolioDetail(BaseModel):
    name: str
    rentabilidad: float
    volatilidad: float
    sharpe: float
    max_drawdown: float
    beta: float
    alpha: float
    tickers: str
    pesos: str


class StockInfo(BaseModel):
    ticker: str
    rentabilidad: float
    sharpe: float
    volatilidad: float
    beta: float


class AllocationEntry(BaseModel):
    ticker: str
    weight: str


class AnalysisResponse(BaseModel):
    success: bool
    profile: str
    profile_description: str
    scores: dict[str, int]
    top_criteria: list[CriterionInfo]
    ranking: list[RankingEntry]
    portfolios: list[PortfolioDetail]
    stocks: list[StockInfo]
    winner: RankingEntry
    allocation: list[AllocationEntry]
    n_stocks_analyzed: int
    n_stocks_selected: int
    consistency_ratio: float
    is_synthetic: bool


class ErrorResponse(BaseModel):
    success: bool = False
    error: str


# ─── Market ───

class MarketStockEntry(BaseModel):
    ticker: str
    name: str = ""
    price: float
    change_1d: float = 0.0
    change_7d: float = 0.0
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    sector: str = ""
    index: str = ""
    sparkline: list[float] = []


class MarketOverviewResponse(BaseModel):
    stocks: list[MarketStockEntry]
    last_updated: str
    is_live: bool


class HeatmapEntry(BaseModel):
    ticker: str
    name: str = ""
    sector: str
    market_cap: float
    daily_change: float
    index: str


class HeatmapResponse(BaseModel):
    entries: list[HeatmapEntry]
    last_updated: str


class SentimentResponse(BaseModel):
    fear_greed_index: int = Field(..., ge=0, le=100)
    label: str  # "Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"
    components: dict[str, float]


# ─── Stocks ───

class StockDetailResponse(BaseModel):
    ticker: str
    name: str = ""
    sector: str = ""
    index: str = ""
    price: float = 0.0
    change_1d: float = 0.0
    indicators: dict[str, float] = {}
    history: list[dict] = []


class StockHistoryResponse(BaseModel):
    ticker: str
    data: list[dict]  # [{date, open, high, low, close, volume}]


# ─── Backtest ───

class BacktestRequest(BaseModel):
    tickers: list[str]
    weights: dict[str, float]
    profile: str
    train_ratio: float = 0.7


class BacktestMetrics(BaseModel):
    total_return: float
    annualized_return: float
    volatility: float
    sharpe: float
    sortino: float
    max_drawdown: float
    beta: float
    alpha: float
    beat_benchmark: bool


class BacktestResponse(BaseModel):
    success: bool
    portfolio_series: list[dict] = []  # [{date, value}]
    benchmark_series: list[dict] = []
    drawdown_series: list[dict] = []
    train_metrics: Optional[BacktestMetrics] = None
    test_metrics: Optional[BacktestMetrics] = None
    error: Optional[str] = None


# ─── Profiles ───

class ProfileWeights(BaseModel):
    profile: str
    description: str
    weights: dict[str, int]
    filters: dict


class ProfilesListResponse(BaseModel):
    profiles: list[ProfileWeights]
