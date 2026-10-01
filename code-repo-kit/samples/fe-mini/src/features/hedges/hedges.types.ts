/** Mirrors BE HedgeProposalDto. @docs HEDGE-001 */
export interface HedgeProposal {
  id: string;
  clientId: string;
  notional: number;
  fixedRate: number;
  startMonth: string;
  endMonth: string;
  status: 'DRAFT' | 'PROPOSED' | 'ACCEPTED';
}

export interface StressScenario {
  shiftBp: number;
  label?: string;
}

export type HedgeStatus = HedgeProposal['status'];
