import { useQuery } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { ProductOverview, Projection } from '@/types/product1';

/**
 * Product 1 overview (`getProduct1Overview`): the four projection tables filtered by city hub
 * plus the cover ratio chart series. Session-scoped (`X-Harbor-Session` via `sessionHeader()`).
 * @docs P1-001
 */
export function useProduct1Overview(city?: string) {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<ProductOverview>({
    queryKey: ['session', sessionId, 'product1', 'overview', city ?? 'all'],
    queryFn: async () =>
      unwrap(await api.GET('/session/product1/overview', { params: { header: sessionHeader(), query: city ? { city } : {} } })),
    enabled: Boolean(sessionId),
  });
}

/**
 * Product 1 projection only (`getProduct1Projection`): the four tables without chart series,
 * used after modal submissions to refresh numbers cheaply.
 * @docs P1-001
 */
export function useProduct1Projection() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<Projection>({
    queryKey: ['session', sessionId, 'product1', 'projection'],
    queryFn: async () => unwrap(await api.GET('/session/product1/projection', { params: { header: sessionHeader() } })),
    enabled: Boolean(sessionId),
  });
}
