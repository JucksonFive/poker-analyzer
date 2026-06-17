import { useFilterStore } from "@/stores/useFilterStore";
import { cn } from "@/shared/utils/cn";

interface FilterBarProps {
  showStake?: boolean;
  showDate?: boolean;
  className?: string;
}

/**
 * Global filter bar for date range and stake.
 * Filters propagate to all features via useFilterStore.
 */
export function FilterBar({
  showStake = true,
  showDate = true,
  className,
}: FilterBarProps) {
  const { dateFrom, dateTo, stakeSB, setDateRange, setStake } =
    useFilterStore();

  return (
    <div className={cn("flex items-center gap-3 flex-wrap", className)}>
      {showDate && (
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400">From</label>
          <input
            type="date"
            value={dateFrom ?? ""}
            onChange={(e) =>
              setDateRange(e.target.value || null, dateTo)
            }
            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-slate-200"
          />
          <label className="text-xs text-slate-400">To</label>
          <input
            type="date"
            value={dateTo ?? ""}
            onChange={(e) =>
              setDateRange(dateFrom, e.target.value || null)
            }
            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-slate-200"
          />
        </div>
      )}

      {showStake && (
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400">Stake (SB)</label>
          <select
            value={stakeSB ?? ""}
            onChange={(e) =>
              setStake(e.target.value ? Number(e.target.value) : null)
            }
            className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-sm text-slate-200"
          >
            <option value="">All</option>
            <option value="0.01">$0.01</option>
            <option value="0.02">$0.02</option>
            <option value="0.05">$0.05</option>
            <option value="0.10">$0.10</option>
            <option value="0.25">$0.25</option>
            <option value="0.50">$0.50</option>
            <option value="1.00">$1.00</option>
            <option value="2.00">$2.00</option>
            <option value="5.00">$5.00</option>
          </select>
        </div>
      )}
    </div>
  );
}
