import { create } from "zustand";

interface Message {
  role: "user" | "assistant";
  content: string;
  sql?: string;
  timestamp: Date;
}

/** AI assistant chat state. */
interface AIState {
  messages: Message[];
  isLoading: boolean;

  addMessage: (message: Message) => void;
  setIsLoading: (loading: boolean) => void;
  clearHistory: () => void;
}

export const useAIStore = create<AIState>((set) => ({
  messages: [],
  isLoading: false,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  setIsLoading: (isLoading) => set({ isLoading }),

  clearHistory: () => set({ messages: [] }),
}));
