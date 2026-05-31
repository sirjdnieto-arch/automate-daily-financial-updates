import { Info } from "lucide-react";
import { useState } from "react";

const LEGEND = [
  { signal: "🚀 COMPRA 100%", desc: "5/5 🟢 (MACD+Media ≤5v) + Bitman impulso alcista" },
  { signal: "🟡 COMPRA 50%", desc: "4/5 o 5/5 🟢 con MACD y Media ≤5v simultáneos" },
  { signal: "⚠️ ATENCIÓN KONKORDE", desc: "Verde K < 0 y Azul K > 0 — señal independiente potente" },
  { signal: "👀 VIGILAR", desc: "3/5 activas — preparar entrada, falta confirmación" },
  { signal: "⏰ LLEGAS TARDE", desc: "Condiciones activas pero señal >5v — riesgo elevado" },
  { signal: "⚠️ VIGILAR SALIDA", desc: "Señales activas pero empieza desactivación" },
  { signal: "🔴 VENTA", desc: "Mayoría de señales desactivadas — salir o no entrar" },
  { signal: "⛔ SIN SETUP", desc: "Sin confluencia suficiente — esperar" },
  { signal: "⛔ NI DE COÑA", desc: "Presión bajista máxima — prohibido comprar" },
];

const INDICADORES = [
  { key: "M", desc: "MACD — velas desde que GAP>0 y acelerando" },
  { key: "Az", desc: "Azul Koncorde — velas desde positivo↑" },
  { key: "Me", desc: "Media K — velas dentro del área Koncorde" },
  { key: "B", desc: "Bitman — velas desde inicio Impulso Alcista" },
];

export function Legend() {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl border border-slate-700/40 bg-slate-800/30">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-4 py-3 text-xs font-medium text-slate-400 hover:text-slate-300"
      >
        <Info className="h-3.5 w-3.5" />
        <span>Leyenda del sistema</span>
        <span className="ml-auto text-slate-600">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="border-t border-slate-700/40 px-4 pb-4 pt-3">
          <div className="grid gap-4 sm:grid-cols-2">
            {/* Señales */}
            <div>
              <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-600">
                Señales
              </p>
              <ul className="space-y-1.5">
                {LEGEND.map((l) => (
                  <li key={l.signal} className="text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">{l.signal}</span>
                    <span className="ml-1">→ {l.desc}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Velas⏱ */}
            <div>
              <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-600">
                Velas⏱ (contador)
              </p>
              <ul className="space-y-1.5">
                {INDICADORES.map((i) => (
                  <li key={i.key} className="text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">{i.key}:</span>{" "}
                    {i.desc}
                  </li>
                ))}
              </ul>

              <div className="mt-4">
                <p className="mb-2 text-[10px] uppercase tracking-widest text-slate-600">
                  Indicadores clave
                </p>
                <ul className="space-y-1 text-xs text-slate-400">
                  <li><span className="text-slate-300">BBWP</span> — BB Width Percentile 13/252 — expansión/compresión</li>
                  <li><span className="text-slate-300">Koncorde</span> — Verde/Azul/Marrón — dinero institucional (Blai5)</li>
                  <li><span className="text-slate-300">Bitman</span> — Ciclos ADX + AO — fase de mercado</li>
                  <li><span className="text-slate-300">PVI</span> — Price Volume Index — dinero inteligente en días alcistas</li>
                  <li><span className="text-slate-300">MCG25</span> — McGinley Dynamic 25 — soporte/resistencia dinámico</li>
                </ul>
              </div>

              <div className="mt-4 rounded-lg border border-slate-700/40 bg-slate-900/40 p-3">
                <p className="text-[10px] text-slate-500">
                  ⚠️ Este dashboard es exclusivamente informativo. No constituye
                  asesoramiento financiero. Opera con responsabilidad.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
