// Empty string = use relative URLs through Next.js proxy rewrites (no CORS issues)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// ─── Questionnaire ───

export async function getQuestions() {
  return fetchAPI<import("../types").QuestionsResponse>(
    "/api/questionnaire/questions"
  );
}

export async function submitQuestionnaire(answers: Record<string, string>) {
  return fetchAPI<import("../types").ProfileResult>(
    "/api/questionnaire/submit",
    { method: "POST", body: JSON.stringify({ answers }) }
  );
}

// ─── Analysis ───

export async function runAnalysis(profile: string, useLive = true) {
  return fetchAPI<import("../types").AnalysisResponse>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ profile, use_live: useLive }),
  });
}

export async function runFullAnalysis(answers: Record<string, string>) {
  return fetchAPI<import("../types").AnalysisResponse>("/api/analyze/full", {
    method: "POST",
    body: JSON.stringify({ answers }),
  });
}

// ─── Market ───

export async function getMarketOverview() {
  return fetchAPI<import("../types").MarketOverview>("/api/market/overview");
}

export async function getHeatmapData() {
  return fetchAPI<{ entries: import("../types").HeatmapEntry[]; last_updated: string }>(
    "/api/market/heatmap"
  );
}

export async function getSentiment() {
  return fetchAPI<import("../types").SentimentData>("/api/market/sentiment");
}

// ─── Stocks ───

export async function getStockDetail(ticker: string) {
  return fetchAPI<{
    ticker: string;
    name: string;
    sector: string;
    index: string;
    price: number;
    change_1d: number;
    indicators: Record<string, number>;
    history: import("../types").StockHistory[];
  }>(`/api/stocks/${ticker}`);
}

export async function getStockHistory(ticker: string, period = "6mo") {
  return fetchAPI<{ ticker: string; data: import("../types").StockHistory[] }>(
    `/api/stocks/${ticker}/history?period=${period}`
  );
}

// ─── Portfolio ───

export async function getPortfolioResults() {
  return fetchAPI<import("../types").AnalysisResponse>("/api/portfolio/results");
}

// ─── Backtest ───

export async function runBacktest(
  tickers: string[],
  weights: Record<string, number>,
  profile: string,
  trainRatio = 0.7
) {
  return fetchAPI<import("../types").BacktestResponse>("/api/backtest", {
    method: "POST",
    body: JSON.stringify({
      tickers,
      weights,
      profile,
      train_ratio: trainRatio,
    }),
  });
}

// ─── Export ───

export function getExcelDownloadUrl() {
  return `${API_BASE}/api/export/excel`;
}
