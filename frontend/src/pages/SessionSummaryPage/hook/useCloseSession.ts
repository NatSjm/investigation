import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/services/api/client';
import { usePresentationPublisher } from '@/components/hook/usePresentationPublisher';
import type { Session } from '@/types/meetings';

/**
 * Closes a meeting session (`closeSession`). The backend stores the report payload and emits
 * `session-closed`, which triggers PDF rendering and the role override write-back.
 * Also tells an open client screen that the session is over (`session-closed` on the presentation channel).
 * @docs SES-001
 */
export function useCloseSession(sessionId: string) {
  const queryClient = useQueryClient();
  const publish = usePresentationPublisher(sessionId);
  return useMutation<Session, Error, void>({
    mutationFn: async () => unwrap(await api.POST('/sessions/{sessionId}/close', { params: { path: { sessionId } } })),
    onSuccess: (session) => {
      queryClient.setQueryData(['sessions', sessionId], session);
      void queryClient.invalidateQueries({ queryKey: ['sessions'] });
      void queryClient.invalidateQueries({ queryKey: ['reports', sessionId] });
      publish({ type: 'session-closed' });
    },
  });
}
