/**
 * View-model types for market scenarios. Mirror `Scenario`, `Shock` and `BaselinePrices`
 * from the contract (`market` module, `ScenarioController`).
 * @docs MKT-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

export type ScenarioKind = 'BASE' | 'ADVERSE' | 'CUSTOM';

/** A shock applies from month index `fromMonth` (1-based within the horizon) onwards; changes are fractions. */
export interface Shock {
  fromMonth: number;
  priceChangePct: number;
  transportChangePct: number;
}

export interface Scenario {
  scenarioId: string;
  name: string;
  kind: ScenarioKind;
  shocks: Shock[];
  createdBy: string;
  createdAt: string;
}

export interface ScenarioRequest {
  name: string;
  kind: ScenarioKind;
  shocks: Shock[];
}

export interface BaselinePoint {
  period: string;
  price: number;
  transportPrice: number;
}

/** Baseline curve for the session's product group and corridor (fed by the market-data service). */
export interface BaselinePrices {
  productGroup: ProductGroup;
  corridor: string;
  asOf: string;
  points: BaselinePoint[];
}

export interface ScenarioPathPoint extends BaselinePoint {
  scenarioPrice: number;
  scenarioTransportPrice: number;
}

/**
 * Client-side preview of calculation `scenario_price_path` (authoritative in backend `core/src/main/kotlin/harbor/utils/ScenarioPricePath.kt`):
 * `price_s(m) = baseline(m) * prod(1 + priceChangePct)` over shocks with `fromMonth <= m`; same for transport.
 */
export function scenarioPricePath(baseline: BaselinePoint[], shocks: Shock[]): ScenarioPathPoint[] {
  return baseline.map((point, index) => {
    const month = index + 1;
    const active = shocks.filter((s) => s.fromMonth <= month);
    const priceFactor = active.reduce((f, s) => f * (1 + s.priceChangePct), 1);
    const transportFactor = active.reduce((f, s) => f * (1 + s.transportChangePct), 1);
    return {
      ...point,
      scenarioPrice: round2(point.price * priceFactor),
      scenarioTransportPrice: round2(point.transportPrice * transportFactor),
    };
  });
}

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}
