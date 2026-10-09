import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { Report } from '../reports.types';

/**
 * Report payload of a closed session (`getReport`). Polls while the PDF is still being rendered.
 * @docs RPT-001
 */
export function useReport(sessionId: string, enabled = true) {
  return useQuery<Report>({
    queryKey: ['reports', sessionId],
    queryFn: async () => unwrap(await api.GET('/sessions/{sessionId}/report', { params: { path: { sessionId } } })),
    enabled: enabled && Boolean(sessionId),
    refetchInterval: (query) => (query.state.data?.status === 'PENDING' ? 5_000 : false),
  });
}

/**
 * Requests a fresh render of the report (`regenerateReport`), e.g. after a failed document-service run.
 * @docs RPT-001
 */
export function useRegenerateReport(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<Report, Error, void>({
    mutationFn: async () => unwrap(await api.POST('/sessions/{sessionId}/report', { params: { path: { sessionId } } })),
    onSuccess: (report) => queryClient.setQueryData(['reports', sessionId], report),
  });
}
