import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { playersApi } from "@/api/client";
import { useAppStore } from "@/stores/useAppStore";
import { StatCard } from "@/shared/components/StatCard";
import { DataTable } from "@/shared/components/DataTable";
import type { PlayerStats } from "@/shared/types/poker";

export default function PlayerAnalysis() {
  const { playerName } = useParams<{ playerName: string }>();
  const { siteFilter } = useAppStore();
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(
    playerName ?? null,
  );
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<any>({
    queryKey: ["players", page, siteFilter],
    queryFn: () =>
      playersApi.list({
        page: String(page),
        page_size: "50",
        site: siteFilter ?? undefined,
      }),
    enabled: !selectedPlayer,
  });

  const { data: playerProfile, isLoading: profileLoading } = useQuery<any>({
    queryKey: ["player", selectedPlayer, siteFilter],
    queryFn: () =>
      playersApi.get(selectedPlayer!, siteFilter ?? "PokerStars"),
    enabled: !!selectedPlayer && !!siteFilter,
  });

  // Player list view
  if (!selectedPlayer) {
    const players = data?.players ?? [];
    const columns = [
      { header: "Player", accessor: "playerName" as const },
      { header: "Site", accessor: "site" as const },
      {
        header: "Hands",
        accessor: "totalHands" as const,
        className: "text-right font-mono",
      },
      {
        header: "VPIP",
        accessor: (row: any) => `${row.stats?.vpip?.toFixed?.(1)}%` ?? "—",
        className: "font-mono",
      },
      {
        header: "PFR",
        accessor: (row: any) => `${row.stats?.pfr?.toFixed?.(1)}%` ?? "—",
        className: "font-mono",
      },
      {
        header: "bb/100",
        accessor: (row: any) => {
          const v = row.stats?.bbPer100;
          return v !== undefined ? v.toFixed(1) : "—";
        },
        className: "font-mono text-right",
      },
    ];

    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-semibold text-slate-200">Players</h1>
        <DataTable
          columns={columns}
          data={players}
          isLoading={isLoading}
          emptyMessage="No players found. Import hand histories to see player stats."
          onRowClick={(player: any) => setSelectedPlayer(player.playerName)}
        />
      </div>
    );
  }

  // Player detail view
  if (profileLoading) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400">
        Loading player stats...
      </div>
    );
  }

  const stats: PlayerStats | undefined = playerProfile?.stats ?? playerProfile;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSelectedPlayer(null)}
          className="text-slate-400 hover:text-slate-200"
        >
          ← Back
        </button>
        <h1 className="text-2xl font-semibold text-slate-200">
          {selectedPlayer}
        </h1>
        {playerProfile?.playerType && (
          <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">
            {playerProfile.playerType}
          </span>
        )}
      </div>

      {stats && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="Total Hands"
              value={stats.totalHands}
              format="number"
            />
            <StatCard label="VPIP" value={stats.vpip} format="percent" />
            <StatCard label="PFR" value={stats.pfr} format="percent" />
            <StatCard label="3Bet" value={stats.threeBet} format="percent" />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="CBet"
              value={stats.cbet}
              format="percent"
            />
            <StatCard
              label="Fold to CBet"
              value={stats.foldToCbet}
              format="percent"
            />
            <StatCard
              label="Aggression"
              value={stats.aggressionFactor}
              format="number"
            />
            <StatCard
              label="WTSD"
              value={stats.wtsd}
              format="percent"
            />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              label="W$SD"
              value={stats.wsd}
              format="percent"
            />
            <StatCard
              label="bb/100"
              value={stats.bbPer100}
              format="number"
              trend={stats.bbPer100 > 0 ? "up" : "down"}
            />
            <StatCard
              label="Net Won"
              value={stats.netWon}
              format="currency"
              trend={stats.netWon > 0 ? "up" : stats.netWon < 0 ? "down" : "neutral"}
            />
            <StatCard
              label="Fold to 3Bet"
              value={stats.foldToThreeBet}
              format="percent"
            />
          </div>

          {playerProfile?.leaks?.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-slate-200 mb-3">
                Detected Leaks
              </h2>
              <ul className="space-y-2">
                {playerProfile.leaks.map((leak: string, i: number) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-amber-400"
                  >
                    <span>⚠</span>
                    <span>{leak}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}
