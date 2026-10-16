import type { RouteObject } from 'react-router-dom';
import { ROUTES, SESSION_STEPS } from '@/constants/routes';
import { SessionLayout } from '@/components/layout/SessionLayout';
import { Product1OverviewPage } from '@/pages/Product1OverviewPage/Product1OverviewPage';
import { Product2OverviewPage } from '@/pages/Product2OverviewPage/Product2OverviewPage';
import { ScenariosPage } from '@/pages/ScenariosPage/ScenariosPage';
import { StressTestPage } from '@/pages/StressTestPage/StressTestPage';
import { SessionSummaryPage } from '@/pages/SessionSummaryPage/SessionSummaryPage';

/**
 * Meeting steps under `/session/:sessionId`: `SessionLayout` syncs `:sessionId` into the session store and renders the
 * step navigation; the children are relative paths (react-router v6). Spliced into the root route list in `Routing.tsx`.
 * @docs SES-001
 */
export const sessionRoutes: RouteObject = {
  path: ROUTES.SESSION,
  element: <SessionLayout />,
  children: [
    { path: SESSION_STEPS.PRODUCT1, Component: Product1OverviewPage },
    { path: SESSION_STEPS.PRODUCT2, Component: Product2OverviewPage },
    { path: SESSION_STEPS.SCENARIOS, Component: ScenariosPage },
    { path: SESSION_STEPS.STRESS_TEST, Component: StressTestPage },
    { path: SESSION_STEPS.SUMMARY, Component: SessionSummaryPage },
  ],
};
