import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { CoverPolicy, CoverSummary } from '../cover.types';

/**
 * Cover ratio per month per sub-product for the current session (`getCoverSummary`).
 * @docs COV-001
 */
export function useCoverSummary() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<CoverSummary>({
    queryKey: ['session', sessionId, 'cover', 'summary'],
    queryFn: async () => unwrap(await api.GET('/session/cover/summary')),
    enabled: Boolean(sessionId),
  });
}

/**
 * Cover policies of a client across product groups (`listCoverPolicies`).
 * @docs COV-001
 */
export function useCoverPolicies(clientId: string) {
  return useQuery<CoverPolicy[]>({
    queryKey: ['clients', clientId, 'cover-policies'],
    queryFn: async () => unwrap(await api.GET('/clients/{clientId}/cover-policies', { params: { path: { clientId } } })),
    enabled: Boolean(clientId),
  });
}
