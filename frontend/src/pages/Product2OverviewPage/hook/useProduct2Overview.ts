import { useQuery } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { Projection } from '@/types/product1';
import type { Product2Overview, TransportMode } from '@/types/product2';

/**
 * Product 2 overview (`getProduct2Overview`): four projection tables filtered by transport mode
 * plus cover ratio series. Session-scoped (`X-Harbor-Session` via `sessionHeader()`).
 * @docs P2-001
 */
export function useProduct2Overview(transportMode?: TransportMode) {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<Product2Overview>({
    queryKey: ['session', sessionId, 'product2', 'overview', transportMode ?? 'all'],
    queryFn: async () =>
      unwrap(
        await api.GET('/session/product2/overview', {
          params: { header: sessionHeader(), query: transportMode ? { transportMode } : {} },
        }),
      ),
    enabled: Boolean(sessionId),
  });
}

/**
 * Product 2 projection only (`getProduct2Projection`).
 * @docs P2-001
 */
export function useProduct2Projection() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<Projection>({
    queryKey: ['session', sessionId, 'product2', 'projection'],
    queryFn: async () => unwrap(await api.GET('/session/product2/projection', { params: { header: sessionHeader() } })),
    enabled: Boolean(sessionId),
  });
}
