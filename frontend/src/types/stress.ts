/**
 * View-model types for the stress test. Aliases of `StressTestResult`, `StressTestScenarioResult`, `StressTestRow`
 * from the contract (`stress` module, `StressTestController`; calculation `stress_test_monthly`).
 * @docs STR-001
 */
import type { components } from '@/services/openapi/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

/** Breakdown dimension of the stress table: `CITY` for Product 1, `TRANSPORT_MODE` for Product 2. */
export type Dimension = components['schemas']['DimensionKind'];

/** One month x dimension value of one scenario; `scenarioTransportPrice` feeds `TransportPriceChart`. */
export type StressRow = components['schemas']['StressTestRow'];

export type StressScenarioResult = components['schemas']['StressTestScenarioResult'];

export type StressTestResult = components['schemas']['StressTestResult'];

export const DIMENSION_LABEL: Record<Dimension, string> = {
  CITY: 'By city',
  TRANSPORT_MODE: 'By transport mode',
};

/** Default toggle position per product group (blueprint: city for Product 1, transport mode for Product 2). */
export function defaultDimension(productGroup: ProductGroup | null | undefined): Dimension {
  return productGroup === 'product2' ? 'TRANSPORT_MODE' : 'CITY';
}
