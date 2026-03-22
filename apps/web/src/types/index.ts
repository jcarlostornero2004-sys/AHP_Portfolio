// ─── Questionnaire ───

export interface QuestionOption {
  letter: string;
  text: string;
  scores: Record<string, number>;
}

export interface Question {
  id: string;
  text: string;
  options: QuestionOption[];
}

export interface QuestionsResponse {
  questions: Question[];
  total: number;
}

export interface ProfileResult {
  profile: string;
  description: string;
  scores: Record<string, number>;
}

// ─── Analysis ───

export interface CriterionInfo {
  name: string;
  weight: number;
  direction: string;
}

export interface RankingEntry {
  name: string;
  score: number;
  rank: number;
}

export interface PortfolioDetail {
  name: string;
  rentabilidad: number;
  volatilidad: number;
  sharpe: number;
  max_drawdown: number;
  beta: number;
  alpha: number;
  tickers: string;
  pesos: string;
}

export interface StockInfo {
  ticker: string;
  rentabilidad: number;
  sharpe: number;
  volatilidad: number;
  beta: number;
}

export interface AllocationEntry {
  ticker: string;
  weight: string;
}

export interface AnalysisResponse {
  success: boolean;
  profile: string;
  profile_description: string;
  scores: Record<string, number>;
  top_criteria: CriterionInfo[];
  ranking: RankingEntry[];
  portfolios: PortfolioDetail[];
  stocks: StockInfo[];
  winner: RankingEntry;
  allocation: AllocationEntry[];
  n_stocks_analyzed: number;
  n_stocks_selected: number;
  consistency_ratio: number;
  is_synthetic: boolean;
}

// ─── Market ───

export interface MarketStock {
  ticker: string;
  name: string;
  price: number;
  change_1d: number;
  change_7d: number;
  market_cap: number | null;
  volume: number | null;
  sector: string;
  index: string;
  sparkline: number[];
}

export interface MarketOverview {
  stocks: MarketStock[];
  last_updated: string;
  is_live: boolean;
}

export interface HeatmapEntry {
  ticker: string;
  name: string;
  sector: string;
  market_cap: number;
  daily_change: number;
  index: string;
}

export interface SentimentData {
  fear_greed_index: number;
  label: string;
  components: Record<string, number>;
}

// ─── Stock Detail ───

export interface StockHistory {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

// ─── Backtest ───

export interface BacktestMetrics {
  total_return: number;
  annualized_return: number;
  volatility: number;
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  beta: number;
  alpha: number;
  beat_benchmark: boolean;
}

export interface BacktestResponse {
  success: boolean;
  portfolio_series: { date: string; value: number }[];
  benchmark_series: { date: string; value: number }[];
  drawdown_series: { date: string; value: number }[];
  train_metrics: BacktestMetrics | null;
  test_metrics: BacktestMetrics | null;
  error?: string;
}
