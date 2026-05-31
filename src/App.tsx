import { useState, useEffect, useMemo } from "react";
import { ArrowUpDown, LayoutGrid, List } from "lucide-react";
import { DashboardData, TickerRow } from "./types";
import { Header } from "./components/Header";
import { StatsBar } from "./components/StatsBar";
import { TickerCard } from "./components/TickerCard";
import { Legend } from "./components/Legend";
import { SearchBar } from "./components/SearchBar";
import { LoadingScreen } from "./components/LoadingScreen";
import { ErrorScreen } from "./components/ErrorScreen";
import { SummaryCards } from "./components/SummaryCards";
import { getSignalMeta, getBadgeClass } from "./utils/signal";

// ──────────────────────────────────────────────────────────────
const DATA_URL = "./data/dashboard.json";

const SIGNAL_ORDER: Record<string, number> = {
  "⚠️ ATENCIÓN KONKORDE": 0,
  "🚀 COMPRA 100%": 1,
  "🟡 COMPRA 50%": 2,
  "👀 VIGILAR": 3,
  "⏰ LLEGAS TARDE": 4,
  "⚠️ VIGILAR SALIDA": 5,
  "🔴 VENTA": 6,
  "⛔ SIN SETUP": 7,
  "⛔ NI DE COÑA": 8,
};

type SortMode = "signal" | "ticker";
type ViewMode = "cards" | "compact";

// ──────────────────────────────────────────────────────────────
export default function App() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterSignal, setFilterSignal] = useState("all");
  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("signal");
  const [viewMode, setViewMode] = useState<ViewMode>("cards");
  const [expandAll, setExpandAll] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${DATA_URL}?t=${Date.now()}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json: DashboardData = await res.json();
      setData(json);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Error desconocido";
      setError(
        `No se pudo cargar dashboard.json (${msg}). ` +
        "Ejecuta el script Python o lanza el workflow de GitHub Actions."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const filtered = useMemo<TickerRow[]>(() => {
    if (!data) return [];
    let rows = data.results;

    if (filterSignal !== "all") {
      rows = rows.filter((r) => r["Señal"] === filterSignal);
    }

    if (search.trim()) {
      const q = search.trim().toUpperCase();
      rows = rows.filter((r) => r["Ticker"].toUpperCase().includes(q));
    }

    return [...rows].sort((a, b) => {
      if (sortMode === "ticker") return a["Ticker"].localeCompare(b["Ticker"]);
      const pa = SIGNAL_ORDER[a["Señal"]] ?? 99;
      const pb = SIGNAL_ORDER[b["Señal"]] ?? 99;
      return pa - pb || a["Ticker"].localeCompare(b["Ticker"]);
    });
  }, [data, filterSignal, search, sortMode]);

  return (
    <div className="min-h-screen bg-[#0d0f14] text-slate-100">
      <Header data={data} loading={loading} onRefresh={fetchData} />

      <main className="mx-auto max-w-[1600px] px-3 py-4 sm:px-4 sm:py-6">
        {loading && <LoadingScreen />}

        {!loading && error && (
          <ErrorScreen message={error} onRetry={fetchData} />
        )}

        {!loading && data && (
          <div className="space-y-4">
            <SummaryCards results={data.results} />

            <div className="flex flex-col gap-3">
              <SearchBar value={search} onChange={setSearch} />

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <StatsBar
                  results={data.results}
                  selected={filterSignal}
                  onSelect={setFilterSignal}
                />

                <div className="flex shrink-0 items-center gap-2">
                  {/* Sort */}
                  <div className="flex items-center gap-1 rounded-lg border border-slate-700/50 bg-slate-800/50 p-0.5">
                    {(["signal", "ticker"] as SortMode[]).map((m) => (
                      <button
                        key={m}
                        onClick={() => setSortMode(m)}
                        className={`flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium transition ${
                          sortMode === m
                            ? "bg-slate-700 text-slate-100"
                            : "text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        <ArrowUpDown className="h-3 w-3" />
                        {m === "signal" ? "Señal" : "A-Z"}
                      </button>
                    ))}
                  </div>

                  {/* View mode */}
                  <div className="flex items-center gap-1 rounded-lg border border-slate-700/50 bg-slate-800/50 p-0.5">
                    {(["cards", "compact"] as ViewMode[]).map((m) => (
                      <button
                        key={m}
                        onClick={() => setViewMode(m)}
                        className={`rounded-md p-1.5 transition ${
                          viewMode === m
                            ? "bg-slate-700 text-slate-100"
                            : "text-slate-500 hover:text-slate-300"
                        }`}
                      >
                        {m === "cards" ? (
                          <LayoutGrid className="h-3.5 w-3.5" />
                        ) : (
                          <List className="h-3.5 w-3.5" />
                        )}
                      </button>
                    ))}
                  </div>

                  {/* Expand all */}
                  <button
                    onClick={() => setExpandAll((v) => !v)}
                    className="rounded-lg border border-slate-700/50 bg-slate-800/50 px-2.5 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 transition"
                  >
                    {expandAll ? "Colapsar" : "Expandir"}
                  </button>
                </div>
              </div>
            </div>

            {/* Count */}
            <p className="text-xs text-slate-500">
              {filtered.length === data.results.length
                ? `${filtered.length} tickers analizados`
                : `${filtered.length} de ${data.results.length} tickers`}
            </p>

            {/* Results */}
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-16 text-center">
                <p className="text-slate-400">Sin resultados</p>
                <button
                  onClick={() => { setSearch(""); setFilterSignal("all"); }}
                  className="text-xs text-slate-600 underline hover:text-slate-400"
                >
                  Limpiar filtros
                </button>
              </div>
            ) : viewMode === "cards" ? (
              <div className="space-y-2">
                {filtered.map((row, i) => (
                  <TickerCard
                    key={row["Ticker"]}
                    row={row}
                    rank={i + 1}
                    forceOpen={expandAll}
                  />
                ))}
              </div>
            ) : (
              <CompactTable rows={filtered} />
            )}

            <Legend />
          </div>
        )}
      </main>

      <footer className="border-t border-slate-800/60 py-6 text-center text-[11px] text-slate-600">
        <p>
          Sovereign Dashboard v3 · Actualizado automáticamente cada madrugada vía{" "}
          <span className="text-slate-500">GitHub Actions</span>
        </p>
        <p className="mt-1">Solo informativo — no constituye asesoramiento financiero</p>
      </footer>
    </div>
  );
}

// ──────────────────────────────────────────────────────────────
// Compact table
// ──────────────────────────────────────────────────────────────

function CompactTable({ rows }: { rows: TickerRow[] }) {
  const cols: { key: keyof TickerRow; label: string }[] = [
    { key: "Ticker", label: "Ticker" },
    { key: "Señal", label: "Señal" },
    { key: "Score", label: "Score" },
    { key: "Tendencia", label: "Tend." },
    { key: "MACD", label: "MACD" },
    { key: "Koncorde", label: "Konc" },
    { key: "PVI", label: "PVI" },
    { key: "BBWP", label: "BBWP" },
    { key: "Div", label: "Div" },
    { key: "Velas⏱", label: "Velas⏱" },
  ];

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800/60 bg-slate-900/30">
      <table className="w-full min-w-[800px] text-xs">
        <thead>
          <tr className="border-b border-slate-800/60">
            <th className="px-3 py-2 text-left text-[10px] uppercase tracking-wider text-slate-600">#</th>
            {cols.map((c) => (
              <th key={c.key} className="px-3 py-2 text-left text-[10px] uppercase tracking-wider text-slate-600">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => {
            const meta = getSignalMeta(row["Señal"]);
            return (
              <tr key={row["Ticker"]} className="border-b border-slate-800/30 hover:bg-slate-800/20 transition">
                <td className="px-3 py-2 text-slate-600">{i + 1}</td>
                {cols.map((c) => {
                  const val = String(row[c.key]);
                  if (c.key === "Ticker") {
                    return <td key={c.key} className="px-3 py-2 font-bold text-slate-100">{val}</td>;
                  }
                  if (c.key === "Señal") {
                    return <td key={c.key} className={`px-3 py-2 font-semibold ${meta.color}`}>{val}</td>;
                  }
                  return (
                    <td key={c.key} className={`px-3 py-2 ${getBadgeClass(val)}`}>{val}</td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
