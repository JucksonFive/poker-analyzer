/** Shared TypeScript types for poker domain concepts. */

/** A playing card: rank + suit, e.g., "Ah", "Td". */
export type Card = string;

/** Poker rank values. */
export type Rank =
  | "2" | "3" | "4" | "5" | "6" | "7" | "8"
  | "9" | "T" | "J" | "Q" | "K" | "A";

/** Poker suits. */
export type Suit = "c" | "d" | "h" | "s";

/** Position at a 6-max table. */
export type Position = "EP" | "MP" | "CO" | "BTN" | "SB" | "BB";

/** Betting streets. */
export type Street = "preflop" | "flop" | "turn" | "river";

/** Action types. */
export type ActionType = "fold" | "check" | "call" | "bet" | "raise" | "all_in";

/** A single action taken by a player during a hand. */
export interface Action {
  player: string;
  actionType: ActionType;
  amount: number;
  street: Street;
  isAllIn: boolean;
}

/** A player's stats computed from raw hand data. */
export interface PlayerStats {
  playerName: string;
  site: string;
  totalHands: number;
  vpip: number;
  pfr: number;
  threeBet: number;
  foldToThreeBet: number;
  cbet: number;
  foldToCbet: number;
  aggressionFactor: number;
  wtsd: number;
  wsd: number;
  bbPer100: number;
  netWon: number;
}

/** Hand summary for lists/tables. */
export interface HandSummary {
  id: number;
  handNumber: string;
  site: string;
  tableName: string;
  stakeSB: number;
  stakeBB: number;
  playedAt: string;
  heroPosition: Position | null;
  heroCards: Card[];
  heroNetWon: number;
  totalPot: number;
  numPlayers: number;
}

/** Full hand detail for replay. */
export interface HandDetail {
  id: number;
  handNumber: string;
  site: string;
  tableName: string;
  stakeSB: number;
  stakeBB: number;
  maxPlayers: number;
  playedAt: string;
  board: Card[];
  players: HandPlayer[];
  actions: Action[];
  totalPot: number;
  rake: number;
  heroCards: Card[];
  heroNetWon: number;
}

/** A player in a hand. */
export interface HandPlayer {
  playerName: string;
  position: Position;
  holeCards: Card[];
  netWon: number;
}

/** Dashboard aggregated stats. */
export interface DashboardSummary {
  totalHands: number;
  totalSessions: number;
  netWon: number;
  bbPer100: number;
  vpip: number;
  pfr: number;
  threeBet: number;
  winRate: number;
  winPct: number;
  periodStart: string | null;
  periodEnd: string | null;
}

/** Profit chart data point. */
export interface ProfitChartPoint {
  date: string;
  netWon: number;
  cumulative: number;
  hands: number;
}
