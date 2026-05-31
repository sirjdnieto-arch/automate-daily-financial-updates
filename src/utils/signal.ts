import { TickerRow } from "../types";

export function getSignalMeta(señal: string): {
  color: string;
  bg: string;
  border: string;
  dot: string;
  priority: number;
} {
  const s = señal.trim();
  if (s.includes("COMPRA 100%"))
    return { color: "text-emerald-300", bg: "bg-emerald-950/60", border: "border-emerald-500/40", dot: "bg-emerald-400", priority: 1 };
  if (s.includes("COMPRA 50%"))
    return { color: "text-yellow-300", bg: "bg-yellow-950/60", border: "border-yellow-500/40", dot: "bg-yellow-400", priority: 2 };
  if (s.includes("ATENCIÓN KONKORDE"))
    return { color: "text-purple-300", bg: "bg-purple-950/60", border: "border-purple-500/40", dot: "bg-purple-400", priority: 0 };
  if (s.includes("VIGILAR SALIDA"))
    return { color: "text-orange-300", bg: "bg-orange-950/60", border: "border-orange-500/40", dot: "bg-orange-400", priority: 5 };
  if (s.includes("VIGILAR"))
    return { color: "text-sky-300", bg: "bg-sky-950/60", border: "border-sky-500/40", dot: "bg-sky-400", priority: 3 };
  if (s.includes("LLEGAS TARDE"))
    return { color: "text-amber-300", bg: "bg-amber-950/60", border: "border-amber-500/40", dot: "bg-amber-400", priority: 4 };
  if (s.includes("VENTA"))
    return { color: "text-red-300", bg: "bg-red-950/60", border: "border-red-500/40", dot: "bg-red-400", priority: 6 };
  if (s.includes("NI DE COÑA"))
    return { color: "text-red-400", bg: "bg-red-950/80", border: "border-red-600/60", dot: "bg-red-600", priority: 8 };
  if (s.includes("SIN SETUP"))
    return { color: "text-slate-400", bg: "bg-slate-800/40", border: "border-slate-600/30", dot: "bg-slate-500", priority: 7 };
  return { color: "text-slate-400", bg: "bg-slate-800/40", border: "border-slate-600/30", dot: "bg-slate-500", priority: 9 };
}

export function getBadgeClass(cell: string): string {
  if (cell.includes("🟢")) return "text-emerald-400";
  if (cell.includes("🔴")) return "text-red-400";
  if (cell.includes("🟡")) return "text-yellow-400";
  if (cell.includes("🟠")) return "text-orange-400";
  if (cell.includes("📈")) return "text-emerald-400";
  if (cell.includes("📉")) return "text-red-400";
  if (cell.includes("⚡")) return "text-yellow-300";
  return "text-slate-400";
}

export function countBySignal(results: TickerRow[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (const r of results) {
    const k = r["Señal"];
    counts[k] = (counts[k] ?? 0) + 1;
  }
  return counts;
}
