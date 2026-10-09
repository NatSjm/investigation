import type { RouteObject } from 'react-router-dom';
import { ParametersPage, ImportsPage } from '@/features/admin';

/**
 * Admin area (outside meetings): parameter sets and import batch monitor.
 * Spread into the root route list in `routes.tsx`; same `{ path, element }` object form.
 */
export const adminRoutes: RouteObject[] = [
  { path: '/admin/parameters', element: <ParametersPage /> },
  { path: '/admin/imports', element: <ImportsPage /> },
];
