import { useQuery } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { BaselinePrices } from '../market.types';

/**
 * Baseline price and transport price curve for the session's corridor (`getBaselinePrices`),
 * read from `baseline_price` which the market-data service keeps up to date.
 * @docs MKT-001
 */
export function useBaselinePrices() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<BaselinePrices>({
    queryKey: ['session', sessionId, 'market', 'baseline'],
    queryFn: async () => unwrap(await api.GET('/session/market/baseline', { params: { header: sessionHeader() } })),
    enabled: Boolean(sessionId),
    staleTime: 5 * 60_000,
  });
}
