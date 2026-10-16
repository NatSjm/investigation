import { Navigate, useRoutes } from 'react-router-dom';
import { ROUTES } from '@/constants/routes';
import { RootLayout } from '@/components/layout/RootLayout';
import { PresentationLayout } from '@/components/layout/PresentationLayout';
import { AdminRoutesGuard } from './AdminRoutesGuard';
import { sessionRoutes } from './SessionRoutes';
import { ClientSearchPage } from '@/pages/ClientSearchPage/ClientSearchPage';
import { ClientOverviewPage } from '@/pages/ClientOverviewPage/ClientOverviewPage';
import { ClientMeetingsPage } from '@/pages/ClientMeetingsPage/ClientMeetingsPage';
import { PreparationSessionsPage } from '@/pages/PreparationSessionsPage/PreparationSessionsPage';
import { ParametersPage } from '@/pages/ParametersPage/ParametersPage';
import { ImportsPage } from '@/pages/ImportsPage/ImportsPage';
import { PresentationPage } from '@/pages/PresentationPage/PresentationPage';

/**
 * Route table (react-router v6 `useRoutes`). One route per line as `{ path: ROUTES.X, Component: XPage }` or
 * `{ path: ROUTES.X, element: <X /> }`: `scripts/docs/gen-routes.py` builds `docs/_generated/routes.md` from this file,
 * `SessionRoutes.tsx` and `src/constants/routes.ts`. Pathless `element` entries are layouts.
 * The client-facing window `/present/:sessionId` lives outside `RootLayout` (no navigation, no admin links).
 */
export function Routing() {
  return useRoutes([
    {
      element: <RootLayout />,
      children: [
        { path: ROUTES.HOME, element: <Navigate to={ROUTES.CLIENTS} replace /> },
        { path: ROUTES.CLIENTS, Component: ClientSearchPage },
        { path: ROUTES.CLIENT, Component: ClientOverviewPage },
        { path: ROUTES.MEETINGS, element: <Navigate to={ROUTES.CLIENT_MEETINGS} replace /> },
        { path: ROUTES.CLIENT_MEETINGS, Component: ClientMeetingsPage },
        { path: ROUTES.PREPARATION_SESSIONS, Component: PreparationSessionsPage },
        sessionRoutes,
        {
          element: <AdminRoutesGuard />,
          children: [
            { path: ROUTES.ADMIN_PARAMETERS, Component: ParametersPage },
            { path: ROUTES.ADMIN_IMPORTS, Component: ImportsPage },
          ],
        },
      ],
    },
    {
      element: <PresentationLayout />,
      children: [{ path: ROUTES.PRESENT, Component: PresentationPage }],
    },
  ]);
}
