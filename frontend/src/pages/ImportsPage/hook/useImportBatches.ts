import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/services/api/client';
import type { ImportBatch } from '@/types/admin';

/**
 * Import batch monitor (`listImportBatches`): daily XLS runs of the file-exchange import.
 * Refreshes every 15 s while a batch is running.
 * @docs ADM-001
 */
export function useImportBatches() {
  return useQuery<ImportBatch[]>({
    queryKey: ['admin', 'imports'],
    queryFn: async () => unwrap(await api.GET('/admin/imports')),
    refetchInterval: (query) => (query.state.data?.some((b) => b.status === 'RUNNING') ? 15_000 : false),
  });
}

/**
 * Starts an import run outside the nightly schedule (`triggerImport`).
 * @docs ADM-001
 */
export function useTriggerImport() {
  const queryClient = useQueryClient();
  return useMutation<ImportBatch, Error, void>({
    mutationFn: async () => unwrap(await api.POST('/admin/imports/run')),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'imports'] }),
  });
}
