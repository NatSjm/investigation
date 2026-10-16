import { useQuery } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { Dimension, StressTestResult } from '@/types/stress';

/**
 * Stress test results of the session (`getStressTest`) for one dimension (`CITY` | `TRANSPORT_MODE`).
 * Returns the stored `stress_test_result` rows per scenario; run `useRunStressTest` to recompute.
 * @docs STR-001
 */
export function useStressTest(dimension: Dimension) {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<StressTestResult>({
    queryKey: ['session', sessionId, 'stress-test', dimension],
    queryFn: async () => unwrap(await api.GET('/session/stress-test', { params: { header: sessionHeader(), query: { dimension } } })),
    enabled: Boolean(sessionId),
  });
}
