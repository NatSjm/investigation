import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { StressTestResult } from '@/types/stress';

/**
 * Recomputes the stress test for all scenarios of the session (`runStressTest`, calculation
 * `stress_test_monthly`) and refreshes the cached results for both dimensions.
 * @docs STR-001
 */
export function useRunStressTest() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<StressTestResult, Error, void>({
    mutationFn: async () => unwrap(await api.POST('/session/stress-test', { params: { header: sessionHeader() } })),
    onSuccess: (result) => {
      queryClient.setQueryData(['session', sessionId, 'stress-test', result.dimension], result);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'stress-test'] });
    },
  });
}
