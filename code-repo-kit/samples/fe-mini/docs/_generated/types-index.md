---
type: Document
title: Types index (FE)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# Types index (FE)

> Generated from `*.types.ts` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Exported `interface`/`type` declarations verbatim (types only, ~1 line per field). Mirrors BE DTOs - compare with `api-index.md`.

## `src/features/hedges/hedges.types.ts`
```ts
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
```

## `src/features/loans/loans.types.ts`
```ts
export interface Loan { id: string; principal: number; termMonths: number }
```

