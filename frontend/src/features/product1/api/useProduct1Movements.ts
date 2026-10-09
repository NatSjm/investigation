import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { MovementInput, ProjectionTables } from '../product1.types';

/**
 * Modelled movements per month for Product 1 (`putProduct1Movements`, modal 1).
 * Replaces the session's `session_movement_input` rows and returns the recomputed tables.
 * @docs P1-001
 */
export function useProduct1Movements() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<ProjectionTables, Error, MovementInput[]>({
    mutationFn: async (movements) => unwrap(await api.PUT('/session/product1/movements', { body: { movements } })),
    onSuccess: (tables) => {
      queryClient.setQueryData(['session', sessionId, 'product1', 'projection'], tables);
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product1'] });
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'cover'] });
    },
  });
}
