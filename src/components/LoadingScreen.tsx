import { Activity } from "lucide-react";

export function LoadingScreen() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-2 border-slate-700 border-t-violet-500 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Activity className="h-5 w-5 text-violet-500" />
        </div>
      </div>
      <div className="text-center">
        <p className="text-sm font-medium text-slate-300">Cargando datos de mercado…</p>
        <p className="mt-1 text-xs text-slate-500">Analizando {'>'}100 tickers</p>
      </div>
      {/* Skeleton */}
      <div className="mt-4 w-full max-w-2xl space-y-3 px-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-16 rounded-xl bg-slate-800/40 animate-pulse"
            style={{ opacity: 1 - i * 0.15 }}
          />
        ))}
      </div>
    </div>
  );
}
