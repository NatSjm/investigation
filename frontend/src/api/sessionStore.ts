import { create } from 'zustand';

export type ProductGroup = 'product1' | 'product2';

/**
 * Current meeting session as selected on the client overview page.
 * The `api` client middleware reads `sessionId` and sends it as `X-Harbor-Session`
 * on every `/session/**` request; `SessionLayout` keeps it in sync with the URL.
 */
export interface SessionState {
  sessionId: string | null;
  productGroup: ProductGroup | null;
  clientId: string | null;
  setSession: (next: { sessionId: string; productGroup: ProductGroup; clientId: string }) => void;
  clear: () => void;
}

const initial = { sessionId: null, productGroup: null, clientId: null };

export const useSessionStore = create<SessionState>()((set) => ({
  ...initial,
  setSession: ({ sessionId, productGroup, clientId }) => set({ sessionId, productGroup, clientId }),
  clear: () => set({ ...initial }),
}));

/** Non-hook accessor for use outside React (middleware, download helpers). */
export const getSessionId = (): string | null => useSessionStore.getState().sessionId;
