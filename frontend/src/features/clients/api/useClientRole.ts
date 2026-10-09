import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { ClientRoleInfo, ProductGroup } from '../clients.types';

/**
 * Role classification (`getClientRole`): algorithm result (`client_role_classification`,
 * 12 months of actual movements) plus the manual override history.
 * @docs CLI-001
 */
export function useClientRole(clientId: string, productGroup: ProductGroup) {
  return useQuery<ClientRoleInfo>({
    queryKey: ['clients', clientId, 'role', productGroup],
    queryFn: async () =>
      unwrap(await api.GET('/clients/{clientId}/role', { params: { path: { clientId }, query: { productGroup } } })),
    enabled: Boolean(clientId),
  });
}
