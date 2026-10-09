/**
 * @module clients — Client search, client overview (product group cards with key indicators and sparklines) and role classification.
 * Client search, client overview with product group cards (key indicators, sparklines, Start meeting / Prepare) and role classification.
 * @docs CLI-001
 */
export { ClientSearchPage } from './ui/ClientSearchPage';
export { ClientOverviewPage } from './ui/ClientOverviewPage';
export { ProductGroupCard } from './ui/ProductGroupCard';
export { ClientInfoPanel } from './ui/ClientInfoPanel';
export { useClientSearch } from './api/useClientSearch';
export { useClientOverview } from './api/useClientOverview';
export { useClientRole } from './api/useClientRole';
export type { ClientSummary, ClientOverview, ProductGroupIndicators, ClientRoleInfo, ClientRole } from './clients.types';
