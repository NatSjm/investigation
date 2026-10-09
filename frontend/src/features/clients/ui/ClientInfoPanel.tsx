import { Link } from 'react-router-dom';
import { formatDateTime } from '@/shared/utils/format';
import type { ClientOverview, ClientSummary } from '../clients.types';

export interface ClientInfoPanelProps {
  client: ClientSummary;
  openSessions: ClientOverview['openSessions'];
}

/** Static client information (registry data) and the list of currently open sessions. */
export function ClientInfoPanel({ client, openSessions }: ClientInfoPanelProps) {
  return (
    <aside className="client-info">
      <h2>Client information</h2>
      <dl>
        <dt>Registry reference</dt>
        <dd>{client.externalRef}</dd>
        <dt>Country</dt>
        <dd>{client.country}</dd>
        <dt>Segment</dt>
        <dd>{client.segment}</dd>
      </dl>
      <h3>Open sessions</h3>
      {openSessions.length === 0 ? (
        <p className="hint">None</p>
      ) : (
        <ul>
          {openSessions.map((s) => (
            <li key={s.sessionId}>
              <Link to={`/session/${s.sessionId}/${s.productGroup}`}>
                {s.productGroup === 'product1' ? 'Product 1' : 'Product 2'} - {s.kind === 'CLIENT' ? 'meeting' : 'preparation'}
              </Link>
              <span className="hint"> started {formatDateTime(s.startedAt)}</span>
            </li>
          ))}
        </ul>
      )}
      <p>
        <Link to={`/meetings?clientId=${client.clientId}`}>All meetings of this client</Link>
      </p>
    </aside>
  );
}
