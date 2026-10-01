/**
 * @module hedges
 * Hedge proposal screens for client meetings: proposal list, editor, stress-test chart.
 * @docs HEDGE-001
 */
export { HedgeProposalList } from './ui/HedgeProposalList';
export { HedgeStressChart } from './ui/HedgeStressChart';
export { useHedgeProposals } from './api/useHedgeProposals';
export type { HedgeProposal, StressScenario } from './hedges.types';
