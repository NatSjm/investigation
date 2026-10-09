import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { ProjectionTablesDto } from '../../product1';
import type { Product2Overview, TransportMode } from '../product2.types';

/**
 * Product 2 overview (`getProduct2Overview`): four projection tables filtered by transport mode
 * plus cover ratio series. Session-scoped (`X-Harbor-Session` added by the client).
 * @docs P2-001
 */
export function useProduct2Overview(transportMode?: TransportMode) {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<Product2Overview>({
    queryKey: ['session', sessionId, 'product2', 'overview', transportMode ?? 'all'],
    queryFn: async () =>
      unwrap(await api.GET('/session/product2/overview', { params: { query: transportMode ? { transportMode } : {} } })) as Product2Overview,
    enabled: Boolean(sessionId),
  });
}

/**
 * Product 2 projection only (`getProduct2Projection`).
 * @docs P2-001
 */
export function useProduct2Projection() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<ProjectionTablesDto>({
    queryKey: ['session', sessionId, 'product2', 'projection'],
    queryFn: async () => unwrap(await api.GET('/session/product2/projection')),
    enabled: Boolean(sessionId),
  });
}
