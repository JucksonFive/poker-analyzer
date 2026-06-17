import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { handsApi } from "@/api/client";
import { useFilterStore } from "@/stores/useFilterStore";
import { DataTable } from "@/shared/components/DataTable";
import { FilterBar } from "@/shared/components/FilterBar";
import type { HandSummary } from "@/shared/types/poker";

export default function HandExplorer() {
  const navigate = useNavigate();
  const { dateFrom, dateTo, stakeSB } = useFilterStore();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery<any>({
    queryKey: ["hands", page, dateFrom, dateTo, stakeSB],
    queryFn: () =>
      handsApi.list({
        page: String(page),
        page_size: "50",
        date_from: dateFrom ?? undefined,
        date_to: dateTo ?? undefined,
        stake_sb: stakeSB ? String(stakeSB) : undefined,
      }),
  });

  const hands: HandSummary[] = data?.hands ?? [];
  const total: number = data?.total ?? 0;

  const columns = [
    {
      header: "Date",
      accessor: (row: HandSummary) =>
        new Date(row.playedAt).toLocaleDateString(),
    },
    { header: "Site", accessor: "site" as const },
    {
      header: "Stake",
      accessor: (row: HandSummary) => `$${row.stakeSB}/$${row.stakeBB}`,
    },
    {
      header: "Cards",
      accessor: (row: HandSummary) =>
        row.heroCards.length > 0 ? row.heroCards.join(" ") : "—",
    },
    {
      header: "Result",
      accessor: (row: HandSummary) => (
        <span
          className={
            row.heroNetWon > 0
              ? "text-stat-positive"
              : row.heroNetWon < 0
                ? "text-stat-negative"
                : "text-slate-400"
          }
        >
          {row.heroNetWon < 0
            ? `-$${Math.abs(row.heroNetWon).toFixed(2)}`
            : `$${row.heroNetWon.toFixed(2)}`}
        </span>
      ),
      className: "font-mono text-right",
    },
    {
      header: "Players",
      accessor: "numPlayers" as const,
      className: "text-center",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-200">Hands</h1>
        <FilterBar />
      </div>

      {/* Search */}
      <div>
        <input
          type="text"
          placeholder="Search hands by player, cards, or hand number..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 placeholder-slate-500"
        />
      </div>

      {/* Table */}
      <DataTable
        columns={columns}
        data={hands}
        isLoading={isLoading}
        emptyMessage="No hands found. Import some hand histories to get started."
        onRowClick={(hand) => navigate(`/hands/${hand.id}`)}
      />

      {/* Pagination */}
      {total > 50 && (
        <div className="flex items-center justify-between text-sm text-slate-400">
          <span>
            Showing {(page - 1) * 50 + 1}–{Math.min(page * 50, total)} of{" "}
            {total}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page * 50 >= total}
              className="px-3 py-1 bg-slate-800 rounded hover:bg-slate-700 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
