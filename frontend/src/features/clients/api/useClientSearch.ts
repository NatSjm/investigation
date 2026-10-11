import { useQuery } from '@tanstack/react-query';
import { api, unwrap } from '@/api/client';
import type { Client, ClientSummary } from '../clients.types';

/**
 * Client search (`searchClients`): proxies the client registry and merges the local profile.
 * Disabled until the query has at least two characters.
 * @docs CLI-001
 */
export function useClientSearch(q: string) {
  const term = q.trim();
  return useQuery<ClientSummary[]>({
    queryKey: ['clients', 'search', term],
    queryFn: async () => unwrap(await api.GET('/clients', { params: { query: { q: term } } })),
    enabled: term.length >= 2,
    placeholderData: (prev) => prev,
  });
}

/**
 * Single client profile (`getClient`).
 * @docs CLI-001
 */
export function useClient(clientId: string) {
  return useQuery<Client>({
    queryKey: ['clients', clientId],
    queryFn: async () => unwrap(await api.GET('/clients/{clientId}', { params: { path: { clientId } } })),
    enabled: Boolean(clientId),
  });
}
