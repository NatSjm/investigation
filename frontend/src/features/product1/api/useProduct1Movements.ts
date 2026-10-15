import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { MovementInput, Projection } from '../product1.types';

/**
 * Modelled movements per month for Product 1 (`putProduct1Movements`, modal 1).
 * Replaces the session's `session_movement_input` rows and returns the recomputed projection.
 * @docs P1-002
 */
export function useProduct1Movements() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<Projection, Error, MovementInput[]>({
    mutationFn: async (movements) =>
      unwrap(await api.PUT('/session/product1/movements', { params: { header: sessionHeader() }, body: { movements } })),
    onSuccess: (projection) => {
      queryClient.setQueryData(['session', sessionId, 'product1', 'projection'], projection);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product1'] });
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'cover'] });
    },
  });
}
