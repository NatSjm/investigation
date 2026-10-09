import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { MovementInput, ProjectionTablesDto } from '../../product1';

/**
 * Modelled movements per month for Product 2 (`putProduct2Movements`, modal 1).
 * Rows carry `transportMode` instead of `city`; returns the recomputed tables.
 * @docs P2-001
 */
export function useProduct2Movements() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<ProjectionTablesDto, Error, MovementInput[]>({
    mutationFn: async (movements) => unwrap(await api.PUT('/session/product2/movements', { body: { movements } })),
    onSuccess: (tables) => {
      queryClient.setQueryData(['session', sessionId, 'product2', 'projection'], tables);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product2'] });
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'cover'] });
    },
  });
}
