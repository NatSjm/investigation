/**
 * @module product2 — Product 2 overview (corridor CST <-> MRD): projection tables per transport mode, modals and cover chart reused from product1.
 * Product 2 overview per transport mode, reusing the projection tables, cover chart and modals of product1.
 * @docs P2-001
 */
export { Product2OverviewPage } from './ui/Product2OverviewPage';
export { TransportModeSelector } from './ui/TransportModeSelector';
export { useProduct2Overview } from './api/useProduct2Overview';
export { useProduct2Projection } from './api/useProduct2Overview';
export { useProduct2Movements } from './api/useProduct2Movements';
export { usePeerSimulation2 } from './api/usePeerSimulation2';
export type { Product2Overview, TransportMode } from './product2.types';
export { P2_TRANSPORT_MODES, P2_SUB_PRODUCTS, P2_CITIES } from './product2.types';
