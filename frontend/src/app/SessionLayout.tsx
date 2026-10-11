import { useEffect } from 'react';
import { NavLink, Outlet, useLocation, useParams } from 'react-router-dom';
import { useSessionStore } from '@/api/sessionStore';
import { useSession } from '@/features/meetings';
import { usePresentationPublisher } from '@/features/presentation';

/**
 * Layout for `/session/:sessionId/*`. Loads the session, mirrors it into the session store
 * (so `sessionHeader()` can send `X-Harbor-Session` on `/session/**` calls) and renders the meeting step navigation:
 * Overview -> Scenarios -> Stress test -> Summary.
 * Publishes the current sub-page (`route`) to the client screen (`/present/:sessionId`) on every navigation
 * and offers the "Open client screen" button that opens that window.
 */
export function SessionLayout() {
  const { sessionId = '' } = useParams<{ sessionId: string }>();
  const { pathname } = useLocation();
  const { data: session, isLoading, error } = useSession(sessionId);
  const setSession = useSessionStore((s) => s.setSession);
  const clear = useSessionStore((s) => s.clear);
  const publish = usePresentationPublisher(sessionId);

  useEffect(() => {
    if (session) {
      setSession({ sessionId: session.sessionId, productGroup: session.productGroup, clientId: session.clientId });
    }
    return () => clear();
  }, [session, setSession, clear]);

  useEffect(() => {
    publish({ type: 'route', path: pathname });
  }, [pathname, publish]);

  if (isLoading) return <p>Loading session...</p>;
  if (error || !session) return <p role="alert">Session {sessionId} could not be loaded.</p>;

  const base = `/session/${session.sessionId}`;
  const steps = [
    { to: `${base}/${session.productGroup}`, label: 'Overview' },
    { to: `${base}/scenarios`, label: 'Scenarios' },
    { to: `${base}/stress-test`, label: 'Stress test' },
    { to: `${base}/summary`, label: 'Summary' },
  ];

  const openClientScreen = () => window.open(`/present/${session.sessionId}`, '_blank', 'noopener');

  return (
    <section className="session-layout">
      <header className="session-header">
        <h1>
          {session.clientName ?? session.clientId} - {session.productGroup === 'product1' ? 'Product 1' : 'Product 2'}
        </h1>
        <span className={`kind kind-${session.kind.toLowerCase()}`}>
          {session.kind === 'PREPARATION' ? 'Preparation' : 'Client meeting'} - {session.status}
        </span>
        <button type="button" className="link" onClick={openClientScreen}>
          Open client screen
        </button>
      </header>
      <nav aria-label="Meeting steps" className="session-steps">
        {steps.map((s, i) => (
          <NavLink key={s.to} to={s.to} className={({ isActive }) => (isActive ? 'step active' : 'step')}>
            {i + 1}. {s.label}
          </NavLink>
        ))}
      </nav>
      <Outlet context={session} />
    </section>
  );
}
