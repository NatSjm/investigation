/**
 * View-model types for the stress test. Mirror `StressTestResult`, `StressRow` from the contract
 * (`stress` module, `StressTestController`; calculation `stress_test_monthly`).
 * @docs STR-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

/** Breakdown dimension of the stress table: `CITY` for Product 1, `TRANSPORT_MODE` for Product 2. */
export type Dimension = 'CITY' | 'TRANSPORT_MODE';

export interface SeriesPoint {
  period: string;
  value: number;
}

/** One month x dimension value of one scenario. */
export interface StressRow {
  period: string;
  dimensionValue: string;
  exposure: number;
  transportCostDelta: number;
  cumulativeExposure: number;
}

export interface StressScenarioResult {
  scenarioId: string;
  scenarioName: string;
  rows: StressRow[];
  /** Scenario transport price per month (`scenario_price_path`), drawn in `TransportPriceChart`. */
  transportPricePath: SeriesPoint[];
}

export interface StressTestResult {
  dimension: Dimension;
  computedAt: string;
  scenarios: StressScenarioResult[];
}

export const DIMENSION_LABEL: Record<Dimension, string> = {
  CITY: 'By city',
  TRANSPORT_MODE: 'By transport mode',
};

/** Default toggle position per product group (blueprint: city for Product 1, transport mode for Product 2). */
export function defaultDimension(productGroup: ProductGroup | null | undefined): Dimension {
  return productGroup === 'product2' ? 'TRANSPORT_MODE' : 'CITY';
}
