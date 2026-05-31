import { useState, useEffect } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { TickerRow } from "../types";
import { getSignalMeta, getBadgeClass } from "../utils/signal";

interface TickerCardProps {
  row: TickerRow;
  rank: number;
  forceOpen?: boolean;
}

function Cell({ label, value }: { label: string; value: string }) {
  const colorClass = getBadgeClass(value);
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] uppercase tracking-wide text-slate-600">{label}</span>
      <span className={`text-xs font-medium ${colorClass}`}>{value}</span>
    </div>
  );
}

export function TickerCard({ row, rank, forceOpen = false }: TickerCardProps) {
  const [open, setOpen] = useState(false);
  const isOpen = forceOpen || open;

  useEffect(() => {
    if (!forceOpen) setOpen(false);
  }, [forceOpen]);

  const meta = getSignalMeta(row["Señal"]);
  const razones = row["Razones"].split(" | ").filter(Boolean);

  return (
    <div
      className={`rounded-xl border ${meta.border} ${meta.bg} overflow-hidden transition-all duration-200`}
    >
      {/* ── Header ── */}
      <button
        className="w-full text-left"
        onClick={() => setOpen((v) => !v)}
      >
        <div className="flex items-center gap-3 px-4 py-3">
          {/* Rank */}
          <span className="min-w-[1.75rem] text-center text-xs font-bold text-slate-600">
            #{rank}
          </span>

          {/* Ticker */}
          <span className="w-[72px] shrink-0 text-sm font-bold tracking-wide text-slate-100">
            {row["Ticker"]}
          </span>

          {/* Signal badge */}
          <span
            className={`hidden shrink-0 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold sm:inline-flex ${meta.color} ${meta.border} ${meta.bg}`}
          >
            {row["Señal"]}
          </span>

          {/* Score */}
          <span className="ml-auto shrink-0 rounded-md bg-slate-800/60 px-2 py-0.5 text-xs font-bold text-slate-300">
            {row["Score"]}
          </span>

          {/* Chevron */}
          <span className="text-slate-500">
            {isOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </span>
        </div>

        {/* Mobile signal */}
        <div className="flex items-center gap-2 px-4 pb-2 sm:hidden">
          <span className={`text-xs font-semibold ${meta.color}`}>{row["Señal"]}</span>
        </div>

        {/* Quick metrics row */}
        <div className="grid grid-cols-4 gap-2 border-t border-slate-800/60 px-4 py-2 sm:grid-cols-7 md:grid-cols-9">
          <Cell label="Tendencia" value={row["Tendencia"]} />
          <Cell label="RSI" value={row["RSI"]} />
          <Cell label="MACD" value={row["MACD"]} />
          <Cell label="Konc" value={row["Koncorde"]} />
          <Cell label="PVI" value={row["PVI"]} />
          <Cell label="BBWP" value={row["BBWP"]} />
          <Cell label="Div" value={row["Div"]} />
          <Cell label="Velas⏱" value={row["Velas⏱"]} />
          <Cell label="Bitman" value={row["Bitman"].split(" (")[0]} />
        </div>
      </button>

      {/* ── Expandido ── */}
      {isOpen && (
        <div className="border-t border-slate-800/60 px-4 py-3">
          <p className="mb-1.5 text-[10px] uppercase tracking-widest text-slate-600">
            Análisis detallado
          </p>
          <div className="mb-2 text-xs text-slate-400">
            <span className="font-semibold text-slate-300">Bitman: </span>
            {row["Bitman"]}
          </div>
          <ul className="space-y-1.5">
            {razones.map((r, i) => {
              const bull = r.includes("🟢") || r.includes("📈");
              const bear = r.includes("🔴") || r.includes("📉");
              const warn = r.includes("⚠️") || r.includes("🟠") || r.includes("⚡");
              const colorClass = bull
                ? "text-emerald-400"
                : bear
                ? "text-red-400"
                : warn
                ? "text-amber-400"
                : "text-slate-400";
              return (
                <li key={i} className={`flex items-start gap-2 text-xs ${colorClass}`}>
                  <span className="mt-0.5 shrink-0 text-slate-600">→</span>
                  <span>{r}</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
