import { Search, X } from "lucide-react";

interface SearchBarProps {
  value: string;
  onChange: (v: string) => void;
}

export function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-500" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar ticker... (AAPL, BTC-USD, BBVA.MC…)"
        className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 py-2 pl-9 pr-9 text-sm text-slate-200 placeholder-slate-600 outline-none focus:border-slate-600 focus:ring-1 focus:ring-slate-600 transition"
      />
      {value && (
        <button
          onClick={() => onChange("")}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
