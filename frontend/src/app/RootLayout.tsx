import { NavLink, Outlet } from 'react-router-dom';
import { useSessionStore } from '@/api/sessionStore';

const links = [
  { to: '/clients', label: 'Clients' },
  { to: '/meetings/client', label: 'Client meetings' },
  { to: '/meetings/preparation', label: 'Preparation sessions' },
  { to: '/admin/parameters', label: 'Parameters' },
  { to: '/admin/imports', label: 'Imports' },
];

/** Top navigation + current session badge; every page renders inside the outlet. */
export function RootLayout() {
  const sessionId = useSessionStore((s) => s.sessionId);
  return (
    <div className="app-shell">
      <header className="app-header">
        <strong className="app-brand">Harbor</strong>
        <nav aria-label="Main">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} className={({ isActive }) => (isActive ? 'active' : undefined)}>
              {l.label}
            </NavLink>
          ))}
        </nav>
        {sessionId && <span className="session-badge">Session {sessionId.slice(0, 8)}</span>}
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
