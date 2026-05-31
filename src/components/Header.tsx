import { RefreshCw, Activity, Clock } from "lucide-react";
import { DashboardData } from "../types";

interface HeaderProps {
  data: DashboardData | null;
  loading: boolean;
  onRefresh: () => void;
}

export function Header({ data, loading, onRefresh }: HeaderProps) {
  const generatedAt = data?.generated_at
    ? new Date(data.generated_at)
    : null;

  const formatted = generatedAt
    ? generatedAt.toLocaleString("es-ES", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "Europe/Madrid",
      }) + " (Madrid)"
    : "–";

  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-[#0d0f14]/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between px-4 py-3">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 shadow-lg shadow-indigo-900/50">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-wide text-slate-100 sm:text-base">
              SOVEREIGN DASHBOARD
            </h1>
            <p className="hidden text-[10px] text-slate-500 sm:block">
              Semáforo técnico v3 — MACD · Koncorde · Bitman · BBWP · PVI
            </p>
          </div>
        </div>

        {/* Info + Refresh */}
        <div className="flex items-center gap-3">
          {data && (
            <div className="hidden items-center gap-1.5 rounded-md border border-slate-700/50 bg-slate-800/50 px-3 py-1.5 text-xs text-slate-400 sm:flex">
              <Clock className="h-3 w-3 text-slate-500" />
              <span>{formatted}</span>
              <span className="mx-1 text-slate-600">·</span>
              <span className="font-medium text-slate-300">
                {data.tickers_analyzed} tickers
              </span>
            </div>
          )}
          <button
            onClick={onRefresh}
            disabled={loading}
            className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-slate-600 hover:bg-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
            <span className="hidden sm:inline">Actualizar</span>
          </button>
        </div>
      </div>
    </header>
  );
}
