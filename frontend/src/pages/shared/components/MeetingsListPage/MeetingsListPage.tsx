import { Link, useSearchParams } from 'react-router-dom';
import { DataTable, type Column } from '@/components/DataTable';
import { formatDateTime } from '@/utils/format';
import { DownloadPdfButton } from '@/pages/shared/components/DownloadPdfButton';
import { useSessions } from '@/pages/shared/hook/useSessions';
import type { Session, SessionFilter, SessionKind, SessionStatus } from '@/types/meetings';

const columns: Column<Session>[] = [
  {
    key: 'client',
    header: 'Client',
    render: (s) => <Link to={`/clients/${s.clientId}`}>{s.clientName ?? s.clientId}</Link>,
  },
  { key: 'productGroup', header: 'Product group', render: (s) => (s.productGroup === 'product1' ? 'Product 1' : 'Product 2') },
  { key: 'kind', header: 'Kind', render: (s) => (s.kind === 'CLIENT' ? 'Client meeting' : 'Preparation') },
  { key: 'status', header: 'Status' },
  { key: 'startedAt', header: 'Started', render: (s) => formatDateTime(s.startedAt) },
  { key: 'closedAt', header: 'Closed', render: (s) => formatDateTime(s.closedAt) },
  {
    key: 'actions',
    header: '',
    render: (s) => (
      <span className="row-actions">
        <Link to={`/session/${s.sessionId}/${s.status === 'OPEN' ? s.productGroup : 'summary'}`}>
          {s.status === 'OPEN' ? 'Continue' : 'Summary'}
        </Link>
        {s.status === 'CLOSED' && <DownloadPdfButton sessionId={s.sessionId} />}
      </span>
    ),
  },
];

export interface MeetingsListPageProps {
  /** Fixed session kind of the page (`ClientMeetingsPage`, `PreparationSessionsPage`); the kind filter is hidden then. */
  kind?: SessionKind;
  title?: string;
}

/**
 * Shared session list with filters; closed sessions expose the report PDF download.
 * Rendered by `/meetings/client` (kind CLIENT) and `/meetings/preparation` (kind PREPARATION).
 * @docs SES-001
 */
export function MeetingsListPage({ kind, title = 'Meetings' }: MeetingsListPageProps) {
  const [params, setParams] = useSearchParams();
  const filter: SessionFilter = {
    clientId: params.get('clientId') ?? undefined,
    status: (params.get('status') as SessionStatus | null) ?? undefined,
    kind: kind ?? (params.get('kind') as SessionKind | null) ?? undefined,
  };
  const { data, isLoading, error } = useSessions(filter);

  const update = (key: keyof SessionFilter, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };

  return (
    <section className="page meetings">
      <h1>{title}</h1>
      <form className="filters" onSubmit={(e) => e.preventDefault()}>
        <label>
          Status
          <select value={filter.status ?? ''} onChange={(e) => update('status', e.target.value)}>
            <option value="">All</option>
            <option value="OPEN">Open</option>
            <option value="CLOSED">Closed</option>
          </select>
        </label>
        {!kind && (
          <label>
            Kind
            <select value={filter.kind ?? ''} onChange={(e) => update('kind', e.target.value)}>
              <option value="">All</option>
              <option value="CLIENT">Client meeting</option>
              <option value="PREPARATION">Preparation</option>
            </select>
          </label>
        )}
        {filter.clientId && (
          <button type="button" onClick={() => update('clientId', '')}>
            Clear client filter
          </button>
        )}
      </form>
      {isLoading && <p>Loading sessions...</p>}
      {error && <p role="alert">Sessions could not be loaded.</p>}
      <DataTable columns={columns} rows={data ?? []} rowKey={(s) => s.sessionId} emptyMessage="No sessions" />
    </section>
  );
}
