import { create } from "zustand";

/** Global application state. */
interface AppState {
  /** Name of the hero (current user). Set during onboarding. */
  heroName: string;
  setHeroName: (name: string) => void;

  /** Whether the AI assistant feature is enabled. */
  aiEnabled: boolean;
  setAIEnabled: (enabled: boolean) => void;

  /** Currently selected poker site filter. */
  siteFilter: string | null;
  setSiteFilter: (site: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  heroName: "",
  setHeroName: (heroName) => set({ heroName }),

  aiEnabled: true,
  setAIEnabled: (aiEnabled) => set({ aiEnabled }),

  siteFilter: null,
  setSiteFilter: (siteFilter) => set({ siteFilter }),
}));
