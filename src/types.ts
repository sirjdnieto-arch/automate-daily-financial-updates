export interface TickerRow {
  Ticker: string;
  Tendencia: string;
  RSI: string;
  MACD: string;
  Koncorde: string;
  PVI: string;
  Bitman: string;
  Div: string;
  BBWP: string;
  "Velas⏱": string;
  Score: string;
  Señal: string;
  Razones: string;
}

export interface DashboardData {
  generated_at: string;
  tickers_analyzed: number;
  results: TickerRow[];
}

export type FilterSignal =
  | "all"
  | "🚀 COMPRA 100%"
  | "🟡 COMPRA 50%"
  | "⚠️ ATENCIÓN KONKORDE"
  | "👀 VIGILAR"
  | "⏰ LLEGAS TARDE"
  | "⚠️ VIGILAR SALIDA"
  | "🔴 VENTA"
  | "⛔ SIN SETUP"
  | "⛔ NI DE COÑA";

export type SortKey = keyof TickerRow;
export type SortDir = "asc" | "desc";
