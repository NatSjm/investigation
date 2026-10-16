import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/services/api/client';
import type { RoleOverrideRequest, Session } from '@/types/meetings';

/**
 * Manual role override during a meeting (`setRoleOverride`): replaces the algorithm result
 * (`client_role_classification`) for this session with a reason; written back on session close.
 * @docs SES-001
 */
export function useRoleOverride(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<Session, Error, RoleOverrideRequest>({
    mutationFn: async (body) =>
      unwrap(await api.PUT('/sessions/{sessionId}/role', { params: { path: { sessionId } }, body })),
    onSuccess: (session) => {
      queryClient.setQueryData(['sessions', sessionId], session);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId] });
    },
  });
}
