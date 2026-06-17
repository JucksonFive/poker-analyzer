import { create } from "zustand";

/**
 * Global filter state that propagates across all features.
 *
 * When the user sets a date range or stake filter on the Dashboard,
 * it carries over to Hand Explorer, Player Analysis, etc.
 */
interface FilterState {
  /** Start of date range filter. */
  dateFrom: string | null;
  /** End of date range filter. */
  dateTo: string | null;
  /** Stake (small blind) filter. */
  stakeSB: number | null;
  /** Whether filters are active. */
  hasActiveFilters: boolean;

  setDateRange: (from: string | null, to: string | null) => void;
  setStake: (sb: number | null) => void;
  clearFilters: () => void;
}

export const useFilterStore = create<FilterState>((set, get) => ({
  dateFrom: null,
  dateTo: null,
  stakeSB: null,
  hasActiveFilters: false,

  setDateRange: (dateFrom, dateTo) =>
    set({ dateFrom, dateTo, hasActiveFilters: true }),

  setStake: (stakeSB) => set({ stakeSB, hasActiveFilters: true }),

  clearFilters: () =>
    set({
      dateFrom: null,
      dateTo: null,
      stakeSB: null,
      hasActiveFilters: false,
    }),
}));
