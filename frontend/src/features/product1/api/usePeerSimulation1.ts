import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { PeerSimulationRequest, PeerSimulationResult } from '../product1.types';

/**
 * Peer simulation for Product 1 (`postProduct1PeerSimulation`, modal 2): monthly series of
 * similar products at peer firms (segment median x scaling factor), stored per session.
 * @docs P1-003
 */
export function usePeerSimulation1() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<PeerSimulationResult, Error, PeerSimulationRequest>({
    mutationFn: async (body) => unwrap(await api.POST('/session/product1/peer-simulation', { params: { header: sessionHeader() }, body })),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product1'] });
    },
  });
}
