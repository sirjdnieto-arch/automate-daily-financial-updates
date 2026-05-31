import { AlertCircle, RefreshCw } from "lucide-react";

interface ErrorScreenProps {
  message: string;
  onRetry: () => void;
}

export function ErrorScreen({ message, onRetry }: ErrorScreenProps) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-4 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-950/60 border border-red-700/40">
        <AlertCircle className="h-6 w-6 text-red-400" />
      </div>
      <div>
        <p className="text-sm font-semibold text-red-300">Error al cargar los datos</p>
        <p className="mt-1 text-xs text-slate-500 max-w-sm">{message}</p>
      </div>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-300 hover:bg-slate-700 transition"
      >
        <RefreshCw className="h-3.5 w-3.5" />
        Reintentar
      </button>
      <p className="text-xs text-slate-600 max-w-md">
        Si el dashboard está corriendo en local, asegúrate de que el archivo{" "}
        <code className="text-slate-400">public/data/dashboard.json</code> existe.
        En GitHub Pages el archivo se genera automáticamente cada madrugada.
      </p>
    </div>
  );
}
