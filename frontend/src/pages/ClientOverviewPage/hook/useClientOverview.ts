import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/services/api/client';
import type { ClientOverview } from '@/types/clients';

/**
 * Client overview (`getClientOverview`): per product group the last-12-month volume and value,
 * classified role, cover ratio, open sessions and sparkline series.
 * @docs CLI-001
 */
export function useClientOverview(clientId: string) {
  return useQuery<ClientOverview>({
    queryKey: ['clients', clientId, 'overview'],
    queryFn: async () => unwrap(await api.GET('/clients/{clientId}/overview', { params: { path: { clientId } } })),
    enabled: Boolean(clientId),
  });
}
