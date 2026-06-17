import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { handsApi } from "@/api/client";
import { PokerTable } from "@/shared/components/PokerTable";
import { StatCard } from "@/shared/components/StatCard";
import type { HandDetail } from "@/shared/types/poker";

export default function HandReplay() {
  const { handId } = useParams<{ handId: string }>();

  const { data, isLoading } = useQuery<any>({
    queryKey: ["hand", handId],
    queryFn: () => handsApi.get(Number(handId)),
    enabled: !!handId,
  });

  const hand: HandDetail | undefined = data;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400">
        Loading hand...
      </div>
    );
  }

  if (!hand) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400">
        Hand not found
      </div>
    );
  }

  const resultStr =
    hand.heroNetWon > 0
      ? `Won $${hand.heroNetWon.toFixed(2)}`
      : hand.heroNetWon < 0
        ? `Lost $${Math.abs(hand.heroNetWon).toFixed(2)}`
        : "Broke even";

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-semibold text-slate-200">
          Hand #{hand.handNumber}
        </h1>
        <span
          className={`text-sm px-2 py-1 rounded ${
            hand.heroNetWon > 0
              ? "bg-green-900/40 text-stat-positive"
              : hand.heroNetWon < 0
                ? "bg-red-900/40 text-stat-negative"
                : "bg-slate-800 text-slate-400"
          }`}
        >
          {resultStr}
        </span>
      </div>

      {/* Info bar */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Site" value={hand.site} format="text" />
        <StatCard label="Table" value={hand.tableName} format="text" />
        <StatCard
          label="Stake"
          value={`$${hand.stakeSB}/$${hand.stakeBB}`}
          format="text"
        />
        <StatCard
          label="Played"
          value={new Date(hand.playedAt).toLocaleString()}
          format="text"
        />
      </div>

      {/* Poker table */}
      <PokerTable
        board={hand.board}
        heroCards={hand.heroCards}
        potSize={hand.totalPot}
      />

      {/* Players */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-3">Players</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase">
              <th className="text-left px-4 py-2">Player</th>
              <th className="text-left px-4 py-2">Position</th>
              <th className="text-left px-4 py-2">Cards</th>
              <th className="text-right px-4 py-2">Result</th>
            </tr>
          </thead>
          <tbody>
            {hand.players.map((p) => (
              <tr key={p.playerName} className="border-b border-slate-800">
                <td className="px-4 py-3 text-slate-300">{p.playerName}</td>
                <td className="px-4 py-3 text-slate-400">{p.position}</td>
                <td className="px-4 py-3 font-mono text-slate-300">
                  {p.holeCards.length > 0 ? p.holeCards.join(" ") : "?? ??"}
                </td>
                <td
                  className={`px-4 py-3 text-right font-mono ${
                    p.netWon > 0
                      ? "text-stat-positive"
                      : p.netWon < 0
                        ? "text-stat-negative"
                        : "text-slate-400"
                  }`}
                >
                  {p.netWon < 0
                    ? `-$${Math.abs(p.netWon).toFixed(2)}`
                    : `$${p.netWon.toFixed(2)}`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Actions */}
      <div>
        <h2 className="text-lg font-semibold text-slate-200 mb-3">
          Actions
        </h2>
        <div className="space-y-1">
          {hand.actions.map((action, i) => (
            <div
              key={i}
              className="flex items-center gap-3 px-4 py-2 bg-slate-800 rounded text-sm"
            >
              <span className="text-slate-500 w-20">
                {action.street}
              </span>
              <span className="text-slate-200 font-medium">
                {action.player}
              </span>
              <span className="text-slate-400">{action.actionType}</span>
              {action.amount > 0 && (
                <span className="text-slate-400 font-mono">
                  ${action.amount.toFixed(2)}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
