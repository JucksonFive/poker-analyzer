import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { sessionsApi } from "@/api/client";
import { DataTable } from "@/shared/components/DataTable";
import { FilterBar } from "@/shared/components/FilterBar";
import { StatCard } from "@/shared/components/StatCard";
import type { SessionSummary } from "@/shared/types/poker";

export default function SessionTracker() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<any>({
    queryKey: ["sessions", page],
    queryFn: () =>
      sessionsApi.list({
        page: String(page),
        page_size: "50",
      }),
  });

  const sessions: SessionSummary[] = data?.sessions ?? [];
  const total: number = data?.total ?? 0;

  const totalHands = sessions.reduce((s, sess) => s + sess.handsCount, 0);
  const totalNet = sessions.reduce((s, sess) => s + sess.netResult, 0);

  const columns = [
    {
      header: "Date",
      accessor: (row: SessionSummary) =>
        new Date(row.startedAt).toLocaleDateString(),
    },
    { header: "Site", accessor: "site" as const },
    { header: "Table", accessor: "tableName" as const },
    {
      header: "Stake",
      accessor: (row: SessionSummary) =>
        `$${row.stakeSB}/$${row.stakeBB}`,
    },
    {
      header: "Hands",
      accessor: "handsCount" as const,
      className: "text-right font-mono",
    },
    {
      header: "Result",
      accessor: (row: SessionSummary) => (
        <span
          className={
            row.netResult > 0
              ? "text-stat-positive font-mono"
              : row.netResult < 0
                ? "text-stat-negative font-mono"
                : "text-slate-400 font-mono"
          }
        >
          {row.netResult < 0
            ? `-$${Math.abs(row.netResult).toFixed(2)}`
            : `$${row.netResult.toFixed(2)}`}
        </span>
      ),
      className: "text-right",
    },
    {
      header: "bb/100",
      accessor: (row: SessionSummary) => row.bbPer100.toFixed(1),
      className: "text-right font-mono",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-200">Sessions</h1>
        <FilterBar />
      </div>

      {/* Session summary cards */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Total Sessions"
          value={total}
          format="number"
        />
        <StatCard
          label="Total Hands"
          value={totalHands}
          format="number"
        />
        <StatCard
          label="Net Result"
          value={totalNet}
          format="currency"
          trend={totalNet > 0 ? "up" : totalNet < 0 ? "down" : "neutral"}
        />
      </div>

      <DataTable
        columns={columns}
        data={sessions}
        isLoading={isLoading}
        emptyMessage="No sessions found. Import hand histories to see sessions."
      />

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
