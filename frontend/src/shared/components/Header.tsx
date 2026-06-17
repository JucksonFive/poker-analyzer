import { useFilterStore } from "@/stores/useFilterStore";

export function Header() {
  const { dateFrom, dateTo, stakeSB, clearFilters, hasActiveFilters } =
    useFilterStore();

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-900 flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        {hasActiveFilters && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Filters:</span>
            {dateFrom && (
              <span className="bg-slate-800 px-2 py-1 rounded text-slate-300">
                {dateFrom} → {dateTo || "now"}
              </span>
            )}
            {stakeSB && (
              <span className="bg-slate-800 px-2 py-1 rounded text-slate-300">
                ${stakeSB} SB
              </span>
            )}
            <button
              onClick={clearFilters}
              className="text-blue-400 hover:text-blue-300"
            >
              Clear
            </button>
          </div>
        )}
      </div>

      <div className="text-sm text-slate-400">
        Poker Analytics Platform
      </div>
    </header>
  );
}
