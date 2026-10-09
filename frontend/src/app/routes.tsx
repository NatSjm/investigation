import { createBrowserRouter, Navigate } from 'react-router-dom';
import { RootLayout } from './RootLayout';
import { SessionLayout } from './SessionLayout';
import { adminRoutes } from './AdminRoutes';
import { ClientSearchPage, ClientOverviewPage } from '@/features/clients';
import { MeetingsListPage, SessionSummaryPage } from '@/features/meetings';
import { Product1OverviewPage } from '@/features/product1';
import { Product2OverviewPage } from '@/features/product2';
import { ScenariosPage } from '@/features/market';
import { StressTestPage } from '@/features/stress';

/**
 * Object routes (react-router v6). Keep one route per line in the `{ path, element }` form:
 * `scripts/docs/gen-routes.ps1` builds `docs/_generated/routes.md` from it.
 * Session routes are absolute children of `SessionLayout`, which syncs `:sessionId` into the session store.
 */
export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <Navigate to="/clients" replace /> },
      { path: '/clients', element: <ClientSearchPage /> },
      { path: '/clients/:clientId', element: <ClientOverviewPage /> },
      { path: '/meetings', element: <MeetingsListPage /> },
      {
        path: '/session/:sessionId',
        element: <SessionLayout />,
        children: [
          { path: '/session/:sessionId/product1', element: <Product1OverviewPage /> },
          { path: '/session/:sessionId/product2', element: <Product2OverviewPage /> },
          { path: '/session/:sessionId/scenarios', element: <ScenariosPage /> },
          { path: '/session/:sessionId/stress-test', element: <StressTestPage /> },
          { path: '/session/:sessionId/summary', element: <SessionSummaryPage /> },
        ],
      },
      ...adminRoutes,
    ],
  },
]);
