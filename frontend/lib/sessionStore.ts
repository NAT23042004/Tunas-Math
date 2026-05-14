// frontend/lib/sessionStore.ts
import { create } from 'zustand';
import type { Message } from '@/types';

interface SessionState {
  sessionId: string | null;
  messages: Message[];
  dialogueState: string;
  hintLevel: number;
  isStreaming: boolean;
  setSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  setStreaming: (val: boolean) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  messages: [],
  dialogueState: 'review',
  hintLevel: 0,
  isStreaming: false,
  setSession: (id) => set({ sessionId: id, messages: [], dialogueState: 'review', hintLevel: 0 }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  setStreaming: (val) => set({ isStreaming: val }),
  clearSession: () => set({ sessionId: null, messages: [], dialogueState: 'review', hintLevel: 0, isStreaming: false }),
}));
