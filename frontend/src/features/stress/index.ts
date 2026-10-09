/**
 * @module stress — Stress test per scenario: monthly exposure table per dimension (city for Product 1, transport mode for Product 2) and transport price chart.
 * Stress test per scenario: monthly exposure table by city or transport mode plus the transport price chart.
 * @docs STR-001
 */
export { StressTestPage } from './ui/StressTestPage';
export { StressTable } from './ui/StressTable';
export { TransportPriceChart } from './ui/TransportPriceChart';
export { DimensionToggle } from './ui/DimensionToggle';
export { useStressTest } from './api/useStressTest';
export { useRunStressTest } from './api/useRunStressTest';
export type { Dimension, StressRow, StressScenarioResult, StressTestResult } from './stress.types';
export { defaultDimension, DIMENSION_LABEL } from './stress.types';
