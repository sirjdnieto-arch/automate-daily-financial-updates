import { TrendingUp, TrendingDown, Minus, Zap } from "lucide-react";
import { TickerRow } from "../types";

interface SummaryCardsProps {
  results: TickerRow[];
}

export function SummaryCards({ results }: SummaryCardsProps) {
  const compras100 = results.filter((r) => r["Señal"].includes("COMPRA 100%")).length;
  const compras50  = results.filter((r) => r["Señal"].includes("COMPRA 50%")).length;
  const ventas     = results.filter((r) =>
    r["Señal"].includes("VENTA") || r["Señal"].includes("NI DE COÑA")
  ).length;
  const atencion   = results.filter((r) => r["Señal"].includes("KONKORDE")).length;
  const vigilar    = results.filter((r) => r["Señal"].includes("VIGILAR")).length;
  const total      = results.length;

  const bulls = compras100 + compras50;
  const bearPct = total ? Math.round((ventas / total) * 100) : 0;
  const bullPct = total ? Math.round((bulls / total) * 100) : 0;

  const cards = [
    {
      label: "Compras activas",
      value: `${bulls}`,
      sub: `${compras100} 100% · ${compras50} 50%`,
      icon: TrendingUp,
      color: "text-emerald-400",
      bg: "bg-emerald-950/40",
      border: "border-emerald-800/30",
      pill: `${bullPct}%`,
      pillColor: "bg-emerald-900/60 text-emerald-300",
    },
    {
      label: "Presión bajista",
      value: `${ventas}`,
      sub: "Venta + NdC",
      icon: TrendingDown,
      color: "text-red-400",
      bg: "bg-red-950/40",
      border: "border-red-800/30",
      pill: `${bearPct}%`,
      pillColor: "bg-red-900/60 text-red-300",
    },
    {
      label: "Vigilar / Tarde",
      value: `${vigilar}`,
      sub: "Seguimiento activo",
      icon: Minus,
      color: "text-amber-400",
      bg: "bg-amber-950/30",
      border: "border-amber-800/20",
      pill: `${total ? Math.round((vigilar / total) * 100) : 0}%`,
      pillColor: "bg-amber-900/40 text-amber-300",
    },
    {
      label: "Atención Konkorde",
      value: `${atencion}`,
      sub: "Verde K < 0 · Azul K > 0",
      icon: Zap,
      color: "text-purple-400",
      bg: "bg-purple-950/40",
      border: "border-purple-800/30",
      pill: `${total ? Math.round((atencion / total) * 100) : 0}%`,
      pillColor: "bg-purple-900/60 text-purple-300",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`rounded-xl border ${c.border} ${c.bg} px-4 py-3 flex flex-col gap-2`}
        >
          <div className="flex items-center justify-between">
            <p className="text-[11px] font-medium text-slate-500">{c.label}</p>
            <c.icon className={`h-3.5 w-3.5 ${c.color}`} />
          </div>
          <div className="flex items-end gap-2">
            <span className={`text-2xl font-bold ${c.color}`}>{c.value}</span>
            <span className={`mb-0.5 rounded-full px-1.5 py-0.5 text-[10px] font-semibold ${c.pillColor}`}>
              {c.pill}
            </span>
          </div>
          <p className="text-[10px] text-slate-600">{c.sub}</p>
        </div>
      ))}
    </div>
  );
}
