---
request: quarterly-view-across-products
title: "Quarterly view on the Product 1 and Product 2 overviews, carried into the stress test table"
status: confirmed
generated: { by: copilot/analyst, at: 2026-10-20T13:00:00Z }
contexts: [product1, product2, stress, presentation]
specs: [P1-001, P2-001, STR-001, PRS-001]
flows: [/flows/client-presentation.md]
pack: .context/p1-001-p2-001-str-001-flows-client-presentation-md-horizon-t.md
---

# Quarterly view on the Product 1 and Product 2 overviews, carried into the stress test table

## Request
> Let the representative switch the Product 1 and Product 2 overviews to a quarterly view and carry it into the
> stress test table.

## Reading
Both product overviews show the **projection** as four cumulative tables with one row per **month** of the session
horizon (P1-001, P2-001); the **stress test** page shows, per scenario, a monthly table of exposure, transport cost
delta and cumulative exposure (STR-001). The request adds a second **period** of the same tables - one row per
calendar quarter - chosen by the representative on the product screen and kept when the meeting moves on to the
stress test. Nothing changes in what is computed per month or stored: the quarterly rows are a roll-up of the
persisted monthly lines, the way the horizon totals already are (`horizon_totals`: derived, never persisted). The
client window mirrors the product and stress pages with their filters (flow client-presentation, PRS-001), so it has
to follow the period too.
**I read this as: P1-001 + P2-001 + STR-001 + PRS-001 (mirror) + new roll-up calculation - right?**
Confirmed by the analyst on 2026-10-20 (acceptance run).

## Parts
| # | Part of the request | State | Context | Owner (spec / calculation / flow) | Evidence |
|---|---|---|---|---|---|
| 1 | Product 1 overview tables per quarter | changed | product1 | P1-001 | BR-P1-001-1 (one row per month of `horizon_months`); `getProduct1Overview`, `getProduct1Projection`; `component:ProjectionTables` (`src/pages/shared/components/ProjectionTables/ProjectionTables.tsx:70`) |
| 2 | Product 2 overview tables per quarter | changed | product2 | P2-001 | BR-P2-001-1 (as BR-P1-001-1), BR-P2-001-9; same shared component and pipeline |
| 3 | Stress test table per quarter | changed | stress | STR-001 | BR-STR-001-1 (every month of the horizon), BR-STR-001-3 (`cumulative_exposure` running sum); `getStressTest?dimension=` (`StressTestController.kt:23`) |
| 4 | Client window follows the chosen period | changed | presentation | PRS-001, flow client-presentation step 6 | BR-PRS-001-4 (the `view` message carries city, transport mode, stress dimension - no period yet) |
| 5 | The quarter roll-up itself | new | product1 (shared aggregator `utils/ProjectionAggregator`, used by stress and reports too) | new calculation `quarterly_rollup` | `horizon_totals` is the pattern: sums of the rounded monthly lines, derived at load time, never stored (BR-P1-001-11) |
| 6 | Horizon totals | unchanged | product1, product2 | `horizon_totals` | sums over the whole horizon do not depend on the period of the rows (BR-P1-001-11, BR-P2-001-9) |
| 7 | Monthly storage and recalculation | unchanged | product1, product2, stress | `monthly_projection`, `stress_test_monthly`, flow session-inputs-recalculation | the stored tables stay monthly; the modal response carries monthly tables (BR-P1-002-3) |
| 8 | Report | question | reports | RPT-001 | the payload copies the four projection tables and the stress rows (RPT-001 Summary); whether the report follows the period is an owner decision |

## Trust
P1-001, P2-001, STR-001, PRS-001: `draft · unverified`; flows client-presentation and meeting-journey:
`draft · unverified`; `horizon_totals`, `monthly_projection`: `draft · unverified` (audited, formulas MATCH);
`stress_test_monthly`: `human-reviewed`. STR-001 carries an open conflict with its legacy page (importer threshold,
transport cost delta) that the quarterly view does not touch. Every story derived here is `needs-spec-review`.

## What is reused, what changes, what is built
- **Reused as is**: `monthly_projection`, `cover_ratio`, `stress_test_monthly`, `horizon_totals`; the stored
  `projection_*` and `stress_test_result` tables; `ProjectionTables`, `CoverRatioChart`, the stress table and the
  presentation mirrors (they render rows; the row set changes).
- **Changed**: `getProduct1Overview`, `getProduct1Projection`, `getProduct2Overview`, `getProduct2Projection`,
  `getStressTest` gain a `period` query parameter (`MONTH` default, `QUARTER`); the product and stress pages gain a
  period toggle that is published in the `view` message; the presentation mirrors request data with the period.
- **Built**: `quarterly_rollup` - sums of quantity, value, landed cost (and exposure, transport cost delta) per
  calendar quarter from the monthly lines, cumulative figures taken from the quarter's last month, cover ratio per
  quarter as a ratio of sums; one function in `utils/ProjectionAggregator` (or beside it) with a unit test whose
  cases become the worked examples.

## Contracts
Changed operations: `getProduct1Overview`, `getProduct1Projection` (product1), `getProduct2Overview`,
`getProduct2Projection` (product2), `getStressTest` (stress) - new optional query parameter `period`. No new
service, no new controller. Proposal: `contracts/proposed/quarterly-view-across-products.openapi.yaml` (cited as
**proposed**, stories labelled `needs-contract`). `putProduct1Movements` / `putProduct2Movements` keep returning
monthly tables (question 3).

## Data
Tables read: `projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction`, `projection_summary`,
`stress_test_result`. No table changes, no migration: quarterly rows are derived at load time like the totals.
Datasets: `sessions-open` (seed, open Product 1 session with a 24-month horizon).

## Flows
- client-presentation, step 6: the `view` message gains `period`; the product and stress mirrors use it (PRS-001).
- session-inputs-recalculation: unchanged (recalculation stays monthly; a quarterly view re-rolls on the next request).
- No new flow: the behaviour is a parameter of existing screens along the meeting journey.

## Calculations
- Used as is: `monthly_projection`, `cover_ratio`, `stress_test_monthly`, `horizon_totals`, `scenario_price_path`.
- New: `quarterly_rollup` (draft concept `domain/calculations/quarterly_rollup.md`): inputs the monthly lines of the
  four projection tables or the stress rows; outputs one line per calendar quarter and key; formula sums per quarter,
  cumulative = the last month of the quarter, cover ratio = covered value / value of the quarter; worked examples to
  come from the unit test.

## Gaps and questions
1. Quarters are calendar quarters (Jan-Mar, ...)? The month grid starts the month after today (`monthly_projection`
   audit Q1), so the first and last quarters of a horizon are usually partial - show them as partial quarters, or
   drop them? Owner decision; BR-P1-001-12 assumes calendar quarters shown as partial.
2. Does the report (RPT-001) follow the period chosen in the meeting, or stay monthly? Owner decision; no story
   until decided (part 8).
3. The movement modal (P1-002 / P2-002) stays monthly; its response carries monthly tables (BR-P1-002-3) and the
   screen re-rolls them - confirm that the modal is usable while the quarterly view is on.
4. Cover ratio per quarter: ratio of the quarter's covered value to its value (not the mean of monthly ratios) -
   confirm (goes into `quarterly_rollup` Conventions).
Forwarded: `spec-writer` - none (the proposed rules are written below); `calc-auditor` - audit `quarterly_rollup`
once the unit test exists; `architect` - not needed (no new service).

## Proposed rules introduced
BR-P1-001-12, BR-P2-001-10, BR-STR-001-9, BR-PRS-001-11 (marker **proposed**, request `quarterly-view-across-products`).

## Stories outline
Epic `work-items/quarterly-view-across-products.yml`:
- S1 Roll the monthly projection lines up to quarters (`quarterly_rollup`, `[BE]` utils + unit test) - BR-P1-001-12, BR-P2-001-10.
- S2 Serve the product overview and projection by period (`period` on four operations, toggle on both product
  pages, `view` message) - BR-P1-001-12, BR-P2-001-10; depends on S1.
- S3 Serve the stress test by period (`getStressTest?period=`, toggle on the stress page) - BR-STR-001-9; depends on S1.
- S4 Mirror the period in the client window - BR-PRS-001-11; depends on S2, S3.
- Report: no story until question 2 is decided.

## Sources
- pack: `python3 scripts/context-pack.py --task P1-001 --task P2-001 --task STR-001 --task flows/client-presentation.md --task horizon_totals --budget 1600` (built 2026-10-20T12:10:11Z)
- catalogue: `generated/catalogue.md` (generated 2026-10-20)
- no other file opened
