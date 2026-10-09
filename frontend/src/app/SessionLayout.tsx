import { useEffect } from 'react';
import { NavLink, Outlet, useParams } from 'react-router-dom';
import { useSessionStore } from '@/api/sessionStore';
import { useSession } from '@/features/meetings';

/**
 * Layout for `/session/:sessionId/*`. Loads the session, mirrors it into the session store
 * (so the API middleware can send `X-Harbor-Session`) and renders the meeting step navigation:
 * Overview -> Scenarios -> Stress test -> Summary.
 */
export function SessionLayout() {
  const { sessionId = '' } = useParams<{ sessionId: string }>();
  const { data: session, isLoading, error } = useSession(sessionId);
  const setSession = useSessionStore((s) => s.setSession);
  const clear = useSessionStore((s) => s.clear);

  useEffect(() => {
    if (session) {
      setSession({ sessionId: session.sessionId, productGroup: session.productGroup, clientId: session.clientId });
    }
    return () => clear();
  }, [session, setSession, clear]);

  if (isLoading) return <p>Loading session...</p>;
  if (error || !session) return <p role="alert">Session {sessionId} could not be loaded.</p>;

  const base = `/session/${session.sessionId}`;
  const steps = [
    { to: `${base}/${session.productGroup}`, label: 'Overview' },
    { to: `${base}/scenarios`, label: 'Scenarios' },
    { to: `${base}/stress-test`, label: 'Stress test' },
    { to: `${base}/summary`, label: 'Summary' },
  ];

  return (
    <section className="session-layout">
      <header className="session-header">
        <h1>
          {session.clientName ?? session.clientId} - {session.productGroup === 'product1' ? 'Product 1' : 'Product 2'}
        </h1>
        <span className={`kind kind-${session.kind.toLowerCase()}`}>
          {session.kind === 'PREPARATION' ? 'Preparation' : 'Client meeting'} - {session.status}
        </span>
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
