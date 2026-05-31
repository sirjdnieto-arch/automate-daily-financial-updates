import { TickerRow } from "../types";
import { countBySignal, getSignalMeta } from "../utils/signal";

const SIGNAL_ORDER = [
  "⚠️ ATENCIÓN KONKORDE",
  "🚀 COMPRA 100%",
  "🟡 COMPRA 50%",
  "👀 VIGILAR",
  "⏰ LLEGAS TARDE",
  "⚠️ VIGILAR SALIDA",
  "🔴 VENTA",
  "⛔ SIN SETUP",
  "⛔ NI DE COÑA",
];

const SHORT_LABELS: Record<string, string> = {
  "⚠️ ATENCIÓN KONKORDE": "Konk",
  "🚀 COMPRA 100%": "C100%",
  "🟡 COMPRA 50%": "C50%",
  "👀 VIGILAR": "Vigil",
  "⏰ LLEGAS TARDE": "Tarde",
  "⚠️ VIGILAR SALIDA": "Salida",
  "🔴 VENTA": "Venta",
  "⛔ SIN SETUP": "Sin",
  "⛔ NI DE COÑA": "NdC",
};

interface StatsBarProps {
  results: TickerRow[];
  selected: string;
  onSelect: (s: string) => void;
}

export function StatsBar({ results, selected, onSelect }: StatsBarProps) {
  const counts = countBySignal(results);
  const total = results.length;

  return (
    <div className="flex flex-wrap gap-2 pb-1">
      {/* Total */}
      <button
        onClick={() => onSelect("all")}
        className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition ${
          selected === "all"
            ? "border-slate-500 bg-slate-700 text-slate-100"
            : "border-slate-700/50 bg-slate-800/50 text-slate-400 hover:border-slate-600 hover:text-slate-200"
        }`}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
        Todo ({total})
      </button>

      {SIGNAL_ORDER.map((sig) => {
        const n = counts[sig] ?? 0;
        if (n === 0) return null;
        const meta = getSignalMeta(sig);
        const isActive = selected === sig;
        return (
          <button
            key={sig}
            onClick={() => onSelect(isActive ? "all" : sig)}
            className={`flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition ${
              isActive
                ? `${meta.bg} ${meta.border} ${meta.color} border`
                : "border-slate-700/50 bg-slate-800/40 text-slate-400 hover:border-slate-600 hover:text-slate-200"
            }`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${meta.dot}`} />
            {SHORT_LABELS[sig] ?? sig} ({n})
          </button>
        );
      })}
    </div>
  );
}
