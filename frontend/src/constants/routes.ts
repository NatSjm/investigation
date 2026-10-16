/**
 * Route paths of the application. `Routing.tsx` and `SessionRoutes.tsx` register them with `useRoutes`;
 * `scripts/docs/gen-routes.py` resolves `ROUTES.<KEY>` through this file, so every path is a plain string here
 * (no template literals, no helpers).
 */
export const ROUTES = {
  HOME: '/',
  CLIENTS: '/clients',
  CLIENT: '/clients/:clientId',
  MEETINGS: '/meetings',
  CLIENT_MEETINGS: '/meetings/client',
  PREPARATION_SESSIONS: '/meetings/preparation',
  /** Parent of the meeting steps; children are relative (`product1`, `scenarios`, ...). */
  SESSION: '/session/:sessionId',
  ADMIN_PARAMETERS: '/admin/parameters',
  ADMIN_IMPORTS: '/admin/imports',
  /** Client-facing window, rendered outside the main layout. */
  PRESENT: '/present/:sessionId',
} as const;

/** Relative paths of the meeting steps under `ROUTES.SESSION`. */
export const SESSION_STEPS = {
  PRODUCT1: 'product1',
  PRODUCT2: 'product2',
  SCENARIOS: 'scenarios',
  STRESS_TEST: 'stress-test',
  SUMMARY: 'summary',
} as const;
