import { useEffect } from 'react';
import { Outlet, useParams } from 'react-router-dom';
import { useSessionStore } from '@/api/sessionStore';
import { useSession } from '@/features/meetings';

/**
 * Minimal layout for the client-facing window `/present/:sessionId`: no main navigation, no admin links,
 * no session controls - just a header (client name, product group) and the mirrored content.
 * Registered outside `RootLayout` in `routes.tsx`. The window has its own session store, which is
 * initialised from the route param so the session-scoped hooks send `X-Harbor-Session`.
 * @docs PRS-001
 */
export function PresentationLayout() {
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

  if (isLoading) return <p>Preparing the presentation...</p>;
  if (error || !session) return <p role="alert">This presentation is not available.</p>;

  return (
    <div className="app-shell presentation">
      <header className="app-header">
        <strong className="app-brand">Harbor</strong>
        <h1>
          {session.clientName ?? session.clientId} - {session.productGroup === 'product1' ? 'Product 1' : 'Product 2'}
        </h1>
      </header>
      <main className="app-main">
        <Outlet context={session} />
      </main>
    </div>
  );
}
