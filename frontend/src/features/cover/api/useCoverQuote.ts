import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, sessionHeader, unwrap } from '@/api/client';
import { useSessionStore } from '@/api/sessionStore';
import type { CoverQuote, CoverQuoteRequest } from '../cover.types';

/**
 * Requests a quote for the uncovered value from the external cover provider (`requestCoverQuote`);
 * the backend stores it in `cover_quote` for the session.
 * @docs COV-001
 */
export function useCoverQuote() {
  const sessionId = useSessionStore((s) => s.sessionId);
  const queryClient = useQueryClient();
  return useMutation<CoverQuote, Error, CoverQuoteRequest>({
    mutationFn: async (body) => unwrap(await api.POST('/session/cover/quotes', { params: { header: sessionHeader() }, body })),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['session', sessionId, 'cover'] }),
  });
}
