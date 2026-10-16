import { Navigate, Outlet } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';

/** Set by the deployment (window-level flag) until roles arrive with the session; admin pages stay hidden otherwise. */
declare global {
  interface Window {
    HARBOR_ADMIN?: boolean;
  }
}

/**
 * Guard for the administration area (`/admin/**`): renders the child route when the current user may administer,
 * otherwise redirects to the client search. Pathless layout route in `Routing.tsx`.
 * @docs ADM-001
 */
export function AdminRoutesGuard() {
  const allowed = typeof window !== 'undefined' && window.HARBOR_ADMIN !== false;
  return allowed ? <Outlet /> : <Navigate to={ROUTES.CLIENTS} replace />;
}
