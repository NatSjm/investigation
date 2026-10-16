import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/services/api/client';
import type { Session, SessionFilter } from '@/types/meetings';

/**
 * Session list for the Meetings page (`listSessions`), filterable by client, status and kind.
 * @docs SES-001
 */
export function useSessions(filter: SessionFilter = {}) {
  return useQuery<Session[]>({
    queryKey: ['sessions', filter],
    queryFn: async () => unwrap(await api.GET('/sessions', { params: { query: filter } })),
  });
}

/**
 * One session by id (`getSession`); used by `SessionLayout` to populate the session store.
 * @docs SES-001
 */
export function useSession(sessionId: string) {
  return useQuery<Session>({
    queryKey: ['sessions', sessionId],
    queryFn: async () => unwrap(await api.GET('/sessions/{sessionId}', { params: { path: { sessionId } } })),
    enabled: Boolean(sessionId),
  });
}
