---
type: Document
title: Codebase map (FE)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# Codebase map (FE)

> Generated from `src/features/* + index.ts barrels` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Read the feature `index.ts` (public surface) and `*.types.ts` first; open components only for UI-level questions.

| Feature | Purpose | Entry | Files | Components | Hooks | Public exports | API calls |
|---|---|---|---|---|---|---|---|
| `hedges` | Hedge proposal screens for client meetings: proposal list, editor, stress-test chart. | `src/features/hedges/index.ts` | 5 | 2 | 1 | HedgeProposalList, HedgeStressChart, useHedgeProposals, HedgeProposal, StressScenario | <BASE>/{*}/proposals<br><BASE>/{*}/stress-test |
| `loans` | Loan proposal and repayment schedule screens. | `src/features/loans/index.ts` | 3 | 1 | 0 | LoanSchedule, Loan |  |
