---
type: Attested Computation
title: Quarterly roll-up of monthly projection and stress rows (proposed)
description: "Rolls the persisted monthly lines of the four projection tables and of the stress test rows up to one line per calendar quarter and key: sums of quantity, value, landed cost, exposure and transport cost delta, cumulative figures from the quarter's last month, cover ratio as a ratio of sums. Proposed by the request quarterly-view-across-products; not implemented."
tags: [calculation, product1, product2, stress, proposed]
status: draft
runtime: kotlin
parameters:
  - { name: lines, type: List, required: true }
  - { name: period, type: Enum, required: true }
executor:
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/QuarterlyRollupTest.kt   # to be written with the implementation (story S1)
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/analyst, at: 2026-10-20T13:20:00Z }
stale_after: 2027-01-18T00:00:00Z
sources:
  - id: request
    resource: /work-items/quarterly-view-across-products.md
    title: "Request analysis: quarterly view across products"
  - id: totals
    resource: /domain/calculations/horizon_totals.md
    title: "Horizon totals (the pattern: derived, never persisted)"
# --- repo extensions ---
name: quarterly_rollup
used_by: [P1-001, P2-001, STR-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt      # intended home (not implemented)
last_verified: null
---

# Quarterly roll-up of monthly projection and stress rows (proposed)

> **Proposed** — introduced by the request analysis [quarterly-view-across-products](/work-items/quarterly-view-across-products.md)
> (BR-P1-001-12, BR-P2-001-10, BR-STR-001-9). Nothing in the code computes this yet; the Formula is the intended
> behaviour, the Worked examples come from the unit test once story S1 is implemented, then `calc-auditor` audits it.

## Purpose
The product overviews and the stress test page show one row per **month** of the session horizon. With
`period = QUARTER` the same tables show one row per **calendar quarter**: the quarterly rows are a roll-up of the
persisted monthly lines, derived wherever the tables are loaded, never stored - the same pattern as
[horizon_totals](horizon_totals.md). Returned by `getProduct1Overview`, `getProduct1Projection`,
`getProduct2Overview`, `getProduct2Projection` and `getStressTest` when `period = QUARTER`; mirrored by the client
window (PRS-001).

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| lines | monthly lines of one table | - | `projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction`, `projection_summary` (output of `monthly_projection`), or `stress_test_result` rows of one scenario | one line per month and key, already rounded |
| period | Enum | - | query parameter `period` (`MONTH`, `QUARTER`) | `MONTH` returns the lines unchanged |

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| none | | |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| quarter | String | - | `YYYY-Qn` of the calendar quarter |
| quantity, value, landedCost | Decimal | as the monthly line | sum of the rounded monthly figures of the quarter, scale 2 (no second rounding) |
| cumulativeValue | Decimal | price basis currency | the `cumulativeValue` of the quarter's last month present in the horizon |
| coverRatio (summary table) | Decimal | ratio | `coveredValue(quarter) / value(quarter)`, scale 4 HALF_EVEN; `0.0000` when the value is 0 (ratio of sums, not a mean of monthly ratios - to confirm) |
| exposure, transportCostDelta (stress rows) | Decimal | price basis currency | sum over the quarter's months, scale 2 |
| cumulativeExposure (stress rows) | Decimal | price basis currency | the value of the quarter's last month present in the horizon |

## Formula
$$ x_{q,k} = \sum_{m \in q} x_{m,k} \quad \text{for quantity, value, landedCost, exposure, transportCostDelta} $$
$$ cumulative_{q,k} = cumulative_{last(q),k} \qquad coverRatio_q = \frac{\sum_{m \in q} coveredValue_m}{\sum_{m \in q} value_m} $$

Step list:
1. Group the monthly lines of one table by `(calendar quarter of period, key)`; a quarter with fewer than three
   months in the horizon (the first and the last one, since the grid starts the month after today) is a **partial
   quarter** and is kept (open question Q1).
2. Sum the additive figures per group (add the rounded monthly values, scale 2).
3. Take the cumulative figures from the group's last month.
4. For the summary table compute the cover ratio from the quarter's covered value and value (scale 4, HALF_EVEN,
   `0.0000` on a zero value).
5. Keys and quarters keep the order of the monthly tables; `tables.totals` are not touched (they sum the whole horizon).

# Computation
```kotlin
// Not implemented. Intended shape beside ProjectionAggregator.totals: a pure function
// fun rollUp(lines: List<Line>, period: Period): List<Line> - grouping by (quarterOf(period), key),
// sumMoney() for the additive figures, last month for the cumulative ones, Rounding.divideAsRatio for the ratio.
```

## Conventions
Quarter: calendar quarter of the line's `period` (`YYYY-Qn`), partial quarters kept · Rounding: sums of the already
rounded monthly figures, scale 2; ratios scale 4 HALF_EVEN · Price basis: inherited from the monthly lines ·
Missing data: a key with no rows in a quarter does not appear; an empty table yields an empty result · The stored
tables and the recalculation flow stay monthly; the roll-up is applied on read.

## Worked examples
| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | two months of one quarter | TODO (from `QuarterlyRollupTest`, story S1) | TODO |
| 2 | partial first quarter | TODO | TODO |
| 3 | cover ratio of a quarter as a ratio of sums | TODO | TODO |
| 4 | stress cumulative exposure = last month of the quarter | TODO | TODO |

## Open questions
- [ ] Q1 (owner: harbor-platform-team) — partial first and last quarters: shown as such, or dropped? (request analysis question 1)
- [ ] Q2 (owner: harbor-platform-team) — cover ratio per quarter as a ratio of sums (here) or as the mean of the
  monthly ratios? (request analysis question 4)
