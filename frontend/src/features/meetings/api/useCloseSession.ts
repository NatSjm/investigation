import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { Session } from '../meetings.types';

/**
 * Closes a meeting session (`closeSession`). The backend stores the report payload and emits
 * `session-closed`, which triggers PDF rendering and the role override write-back.
 * @docs MTG-001
 */
export function useCloseSession(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<Session, Error, void>({
    mutationFn: async () => unwrap(await api.POST('/sessions/{sessionId}/close', { params: { path: { sessionId } } })),
    onSuccess: (session) => {
      queryClient.setQueryData(['sessions', sessionId], session);
      void queryClient.invalidateQueries({ queryKey: ['sessions'] });
      void queryClient.invalidateQueries({ queryKey: ['reports', sessionId] });
    },
  });
}
