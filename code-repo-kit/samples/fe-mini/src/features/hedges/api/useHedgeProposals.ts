import { useQuery, useMutation } from '@tanstack/react-query';
import type { HedgeProposal, StressScenario } from '../hedges.types';

const BASE = '/api/v1/hedges';

export function useHedgeProposals(clientId: string) {
  return useQuery({
    queryKey: ['hedges', clientId],
    queryFn: () => fetch(`${BASE}/${clientId}/proposals`).then(r => r.json() as Promise<HedgeProposal[]>),
  });
}

export function useStressTest(proposalId: string) {
  return useMutation({
    mutationFn: (scenario: StressScenario) =>
      fetch(`${BASE}/${proposalId}/stress-test`, { method: 'POST', body: JSON.stringify(scenario) }).then(r => r.json()),
  });
}
