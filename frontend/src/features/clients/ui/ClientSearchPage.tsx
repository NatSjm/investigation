import { useState } from 'react';
import { Link } from 'react-router-dom';
import { DataTable, type Column } from '@/shared/ui/DataTable';
import { useClientSearch } from '../api/useClientSearch';
import type { ClientSummary } from '../clients.types';

const columns: Column<ClientSummary>[] = [
  { key: 'name', header: 'Client', render: (c) => <Link to={`/clients/${c.clientId}`}>{c.name}</Link> },
  { key: 'externalRef', header: 'Registry ref' },
  { key: 'country', header: 'Country' },
  { key: 'segment', header: 'Segment' },
];

/** `/clients` - search box backed by the client registry; results link to the overview page. */
export function ClientSearchPage() {
  const [q, setQ] = useState('');
  const { data, isFetching, error } = useClientSearch(q);

  return (
    <section className="page client-search">
      <h1>Clients</h1>
      <form role="search" onSubmit={(e) => e.preventDefault()}>
        <label htmlFor="client-search">Search by name or registry reference</label>
        <input
          id="client-search"
          type="search"
          autoFocus
          value={q}
          placeholder="At least two characters"
          onChange={(e) => setQ(e.target.value)}
        />
        {isFetching && <span className="hint">Searching...</span>}
      </form>
      {error && <p role="alert">Search failed. Please retry.</p>}
      <DataTable
        columns={columns}
        rows={data ?? []}
        rowKey={(c) => c.clientId}
        emptyMessage={q.trim().length < 2 ? 'Type to search' : 'No clients match'}
      />
    </section>
  );
}
