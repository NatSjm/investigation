import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, ensureOk, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { Scenario, ScenarioRequest } from '@/types/market';

/**
 * Scenarios of the current session (`listScenarios`).
 * @docs MKT-001
 */
export function useScenarios() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return useQuery<Scenario[]>({
    queryKey: ['session', sessionId, 'scenarios'],
    queryFn: async () => unwrap(await api.GET('/session/scenarios', { params: { header: sessionHeader() } })),
    enabled: Boolean(sessionId),
  });
}

/**
 * Create / update / delete scenarios (`createScenario`, `updateScenario`, `deleteScenario`).
 * Every change invalidates the scenario list and the stress test results of the session.
 * @docs MKT-001
 */
export function useScenarioMutations() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'scenarios'] });
    void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'stress-test'] });
  };

  const create = useMutation<Scenario, Error, ScenarioRequest>({
    mutationFn: async (body) => unwrap(await api.POST('/session/scenarios', { params: { header: sessionHeader() }, body })),
    onSuccess: invalidate,
  });

  const update = useMutation<Scenario, Error, { scenarioId: string; body: ScenarioRequest }>({
    mutationFn: async ({ scenarioId, body }) =>
      unwrap(await api.PUT('/session/scenarios/{scenarioId}', { params: { header: sessionHeader(), path: { scenarioId } }, body })),
    onSuccess: invalidate,
  });

  const remove = useMutation<void, Error, string>({
    mutationFn: async (scenarioId) =>
      ensureOk(await api.DELETE('/session/scenarios/{scenarioId}', { params: { header: sessionHeader(), path: { scenarioId } } })),
    onSuccess: invalidate,
  });

  return { create, update, remove };
}
