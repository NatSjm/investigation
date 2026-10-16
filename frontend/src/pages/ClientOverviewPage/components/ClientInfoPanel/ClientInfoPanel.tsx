import { Link } from 'react-router-dom';
import { formatDateTime } from '@/utils/format';
import type { Session } from '@/types/meetings';
import type { ClientSummary } from '@/types/clients';

export interface ClientInfoPanelProps {
  client: ClientSummary;
  /** Open sessions of the client (`listSessions` with `status=OPEN`; the overview itself does not list them). */
  openSessions: Session[];
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
        <Link to={`/meetings/client?clientId=${client.clientId}`}>All meetings of this client</Link>
      </p>
    </aside>
  );
}
