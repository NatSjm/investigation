import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { CreateSessionRequest, CreateSessionResponse } from '../meetings.types';

/**
 * Creates a meeting session for a client and product group (`createSession`).
 * `kind = CLIENT` for a real meeting, `PREPARATION` for a dry run by the representative.
 * Resolves with the new `sessionId`; the caller stores it and navigates into the session.
 * @docs SES-001
 */
export function useCreateSession(clientId: string) {
  const queryClient = useQueryClient();
  return useMutation<CreateSessionResponse, Error, CreateSessionRequest>({
    mutationFn: async (body) =>
      unwrap(await api.POST('/clients/{clientId}/sessions', { params: { path: { clientId } }, body })),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['sessions'] });
      void queryClient.invalidateQueries({ queryKey: ['clients', clientId, 'overview'] });
    },
  });
}
