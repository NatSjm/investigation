import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { Parameter, ParameterUpsertRequest, ProductGroup } from '../admin.types';

/**
 * Parameter sets (`listParameters`), optionally filtered by product group.
 * @docs ADM-001
 */
export function useParameters(productGroup?: ProductGroup) {
  return useQuery<Parameter[]>({
    queryKey: ['admin', 'parameters', productGroup ?? 'all'],
    queryFn: async () => unwrap(await api.GET('/admin/parameters', { params: { query: productGroup ? { productGroup } : {} } })),
  });
}

/**
 * Creates or updates one parameter by key (`upsertParameter`); scope fields select the row.
 * @docs ADM-001
 */
export function useUpsertParameter() {
  const queryClient = useQueryClient();
  return useMutation<Parameter, Error, { key: string; body: ParameterUpsertRequest }>({
    mutationFn: async ({ key, body }) => unwrap(await api.PUT('/admin/parameters/{key}', { params: { path: { key } }, body })),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'parameters'] }),
  });
}
