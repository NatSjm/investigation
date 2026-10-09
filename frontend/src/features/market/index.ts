/**
 * @module market — Market scenarios per session: price / transport price paths (shocks) on top of the baseline curve from market-data.
 * Market scenarios of a session: price and transport price shocks on top of the baseline curve, with live path preview.
 * @docs MKT-001
 */
export { ScenariosPage } from './ui/ScenariosPage';
export { ScenarioEditor } from './ui/ScenarioEditor';
export { ShockRow } from './ui/ShockRow';
export { useScenarios } from './api/useScenarios';
export { useScenarioMutations } from './api/useScenarios';
export { useBaselinePrices } from './api/useBaselinePrices';
export type { Scenario, ScenarioRequest, ScenarioKind, Shock, BaselinePrices, BaselinePoint } from './market.types';
export { scenarioPricePath } from './market.types';
