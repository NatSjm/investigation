import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/services/api/client';
import { useSessionStore } from '@/services/api/sessionStore';
import type { MovementInput, Projection } from '@/types/product1';

/**
 * Modelled movements per month for Product 2 (`putProduct2Movements`, modal 1).
 * Rows carry `transportMode` instead of `city`; returns the recomputed projection.
 * @docs P2-002
 */
export function useProduct2Movements() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<Projection, Error, MovementInput[]>({
    mutationFn: async (movements) =>
      unwrap(await api.PUT('/session/product2/movements', { params: { header: sessionHeader() }, body: { movements } })),
    onSuccess: (projection) => {
      queryClient.setQueryData(['session', sessionId, 'product2', 'projection'], projection);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product2'] });
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'cover'] });
    },
  });
}
