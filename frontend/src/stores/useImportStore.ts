import { create } from "zustand";

/** Import process state, exposed for the Import feature and progress indicators. */
interface ImportState {
  /** Whether an import is currently running. */
  isImporting: boolean;
  /** Hands processed so far in the current import. */
  handsProcessed: number;
  /** Total hands in the current import file(s). */
  handsTotal: number;
  /** Import errors encountered. */
  errors: string[];

  setImporting: (
    isImporting: boolean,
    handsProcessed?: number,
    handsTotal?: number,
  ) => void;
  setProgress: (processed: number, total: number) => void;
  addError: (error: string) => void;
  reset: () => void;
}

export const useImportStore = create<ImportState>((set) => ({
  isImporting: false,
  handsProcessed: 0,
  handsTotal: 0,
  errors: [],

  setImporting: (isImporting, handsProcessed = 0, handsTotal = 0) =>
    set({ isImporting, handsProcessed, handsTotal, errors: [] }),

  setProgress: (handsProcessed, handsTotal) =>
    set({ handsProcessed, handsTotal }),

  addError: (error) =>
    set((state) => ({ errors: [...state.errors, error] })),

  reset: () =>
    set({ isImporting: false, handsProcessed: 0, handsTotal: 0, errors: [] }),
}));
