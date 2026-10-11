/**
 * @module product1 — Product 1 overview (corridor VLD <-> NRL): four cumulative projection tables per city hub, cover ratio chart, movement and peer simulation modals.
 * Product 1 overview per city hub: the four cumulative projection tables, cover ratio chart, movement input and peer simulation modals.
 * @docs P1-001
 */
export { Product1OverviewPage } from './ui/Product1OverviewPage';
export { ProjectionTables } from './ui/ProjectionTables';
export { CoverRatioChart } from './ui/CoverRatioChart';
export { MovementInputModal } from './ui/MovementInputModal';
export { PeerSimulationModal } from './ui/PeerSimulationModal';
export { CitySelector } from './ui/CitySelector';
export { useProduct1Overview } from './api/useProduct1Overview';
export { useProduct1Projection } from './api/useProduct1Overview';
export { useProduct1Movements } from './api/useProduct1Movements';
export { usePeerSimulation1 } from './api/usePeerSimulation1';
export type { ProductOverview, Projection, ProjectionTables as ProjectionTablesDto, ProjectionRow, ProjectionSummaryRow, MovementInput, MovementDimension, PeerSimulationRequest, PeerSimulationResult, CoverSeries, CoverSeriesPoint } from './product1.types';
export { P1_CITIES, P1_SUB_PRODUCTS } from './product1.types';
