import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { PeerSimulationRequest, PeerSimulationResult } from '../../product1';

/**
 * Peer simulation for Product 2 (`postProduct2PeerSimulation`, modal 2).
 * @docs P2-003
 */
export function usePeerSimulation2() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<PeerSimulationResult, Error, PeerSimulationRequest>({
    mutationFn: async (body) => unwrap(await api.POST('/session/product2/peer-simulation', { params: { header: sessionHeader() }, body })),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'product2'] });
    },
  });
}
