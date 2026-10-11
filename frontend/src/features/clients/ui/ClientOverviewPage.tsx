import { Link, useNavigate, useParams } from 'react-router-dom';
import { useSessionStore } from '@/api/sessionStore';
import { useCreateSession, useSessions, type SessionKind } from '@/features/meetings';
import { useClientOverview } from '../api/useClientOverview';
import { ProductGroupCard } from './ProductGroupCard';
import { ClientInfoPanel } from './ClientInfoPanel';
import type { ProductGroup } from '../clients.types';

/**
 * `/clients/:clientId` - client info panel plus one card per product group.
 * Selecting a product group ("Start meeting" = CLIENT, "Prepare" = PREPARATION) creates the session
 * and navigates into the product overview; from then on requests carry `X-Harbor-Session`.
 * Open sessions are not part of `ClientOverview`; they come from `listSessions` filtered by client and status.
 */
export function ClientOverviewPage() {
  const { clientId = '' } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const setSession = useSessionStore((s) => s.setSession);
  const { data, isLoading, error } = useClientOverview(clientId);
  const openSessions = useSessions({ clientId, status: 'OPEN' });
  const createSession = useCreateSession(clientId);

  const start = async (productGroup: ProductGroup, kind: SessionKind) => {
    const { sessionId } = await createSession.mutateAsync({ productGroup, kind });
    setSession({ sessionId, productGroup, clientId });
    navigate(`/session/${sessionId}/${productGroup}`);
  };

  if (isLoading) return <p>Loading client...</p>;
  if (error || !data) return <p role="alert">Client {clientId} could not be loaded.</p>;

  return (
    <section className="page client-overview">
      <nav aria-label="Breadcrumb">
        <Link to="/clients">Clients</Link> / <span>{data.client.name}</span>
      </nav>
      <h1>{data.client.name}</h1>
      <div className="overview-grid">
        <ClientInfoPanel client={data.client} openSessions={openSessions.data ?? []} />
        <div className="product-cards">
          {data.productGroups.map((pg) => (
            <ProductGroupCard
              key={pg.productGroup}
              indicators={pg}
              busy={createSession.isPending}
              onStartMeeting={() => start(pg.productGroup, 'CLIENT')}
              onPrepare={() => start(pg.productGroup, 'PREPARATION')}
            />
          ))}
          {data.productGroups.length === 0 && <p>No movements recorded for this client yet.</p>}
        </div>
      </div>
      {createSession.error && <p role="alert">The session could not be created.</p>}
    </section>
  );
}
