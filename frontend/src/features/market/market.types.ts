/**
 * View-model types for market scenarios. Aliases of `Scenario`, `ScenarioInput`, `Shock` and `BaselinePrices`
 * from the contract (`market` module, `ScenarioController`); `scenarioPricePath` is the FE preview.
 * @docs MKT-001
 */
import type { components } from '@/api/generated/schema';

export type ProductGroup = components['schemas']['ProductGroup'];

/** A shock applies from month index `fromMonth` (1-based within the horizon) onwards; changes are fractions. */
export type Shock = components['schemas']['Shock'];

/** Scenario payload sent on create / update (`ScenarioInput`). */
export type ScenarioRequest = components['schemas']['ScenarioInput'];

/** Who authored the scenario: the representative or the client (contract enum on `ScenarioInput.kind`). */
export type ScenarioKind = ScenarioRequest['kind'];

export type Scenario = components['schemas']['Scenario'];

export type BaselinePoint = components['schemas']['BaselinePricePoint'];

/** Baseline curve for the session's product group and corridor (fed by the market-data service). */
export type BaselinePrices = components['schemas']['BaselinePrices'];

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
