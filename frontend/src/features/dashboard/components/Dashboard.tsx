import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/api/client";
import { useFilterStore } from "@/stores/useFilterStore";
import { useAppStore } from "@/stores/useAppStore";
import { StatCard } from "@/shared/components/StatCard";
import { FilterBar } from "@/shared/components/FilterBar";
import type { DashboardSummary } from "@/shared/types/poker";

export default function Dashboard() {
  const { heroName } = useAppStore();
  const { dateFrom, dateTo, stakeSB } = useFilterStore();

  const { data, isLoading } = useQuery<any>({
    queryKey: ["dashboard", heroName, dateFrom, dateTo, stakeSB],
    queryFn: () =>
      analyticsApi.summary({
        hero_name: heroName,
        date_from: dateFrom ?? undefined,
        date_to: dateTo ?? undefined,
        stake_sb: stakeSB ? String(stakeSB) : undefined,
      }),
    enabled: !!heroName,
  });

  const stats: DashboardSummary | undefined = data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-200">Dashboard</h1>
        <FilterBar />
      </div>

      {!heroName && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
          <h2 className="text-lg font-semibold text-slate-200 mb-2">
            Welcome to Poker Analytics
          </h2>
          <p className="text-slate-400 mb-4">
            Import your hand histories to get started. Set your hero name to
            see personalized stats.
          </p>
        </div>
      )}

      {isLoading && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="bg-slate-800 rounded-lg p-4 h-24 animate-pulse"
            >
              <div className="h-3 bg-slate-700 rounded w-16 mb-2" />
              <div className="h-6 bg-slate-700 rounded w-20" />
            </div>
          ))}
        </div>
      )}

      {stats && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Total Hands"
              value={stats.totalHands}
              format="number"
              subValue={`${stats.totalSessions} sessions`}
            />
            <StatCard
              label="Net Won"
              value={stats.netWon}
              format="currency"
              trend={stats.netWon > 0 ? "up" : stats.netWon < 0 ? "down" : "neutral"}
            />
            <StatCard
              label="bb/100"
              value={stats.bbPer100}
              format="number"
              trend={stats.bbPer100 > 0 ? "up" : stats.bbPer100 < 0 ? "down" : "neutral"}
            />
            <StatCard
              label="Win Rate"
              value={stats.winPct}
              format="percent"
              subValue={`${stats.winRate.toFixed(1)} bb/100`}
            />
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="VPIP" value={stats.vpip} format="percent" />
            <StatCard label="PFR" value={stats.pfr} format="percent" />
            <StatCard label="3Bet" value={stats.threeBet} format="percent" />
          </div>
        </>
      )}
    </div>
  );
}
