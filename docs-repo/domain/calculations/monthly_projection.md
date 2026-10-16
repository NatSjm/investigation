---
type: Attested Computation
title: Monthly projection (value, landed cost, cumulative value)
description: Per session and month computes value and landed cost of every movement row and groups them into the four cumulative projection tables (by sub-product, by dimension, by direction, summary).
tags: [calculation, product1, product2, projection]
status: draft
runtime: kotlin
parameters:
  - { name: quantity, type: Decimal, required: true }
  - { name: unitPrice, type: Decimal, required: true }
  - { name: priceIndex, type: Decimal, required: true }
  - { name: tariffRate, type: Decimal, required: true }
  - { name: handlingCost, type: Decimal, required: true }
  - { name: transportCost, type: Decimal, required: true }
executor:
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/calc-auditor, at: 2026-10-12T12:00:00Z }
# verified: re-verification (Run 4) due after the audit of 2026-10-12; previous: human:example-reviewer 2026-10-08
stale_after: 2027-01-06T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt
    title: ProjectionAggregator.kt
  - id: tests
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt
    title: ProjectionAggregatorTest.kt
  - id: rounding
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/main/kotlin/com/acme/harbor/utils/Rounding.kt
    title: Rounding.kt
# --- repo extensions ---
name: monthly_projection
used_by: [P1-001, P1-002, P2-001, P2-002, COV-001, STR-001, RPT-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/Rounding.kt
  - backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt
last_verified: null
---

# Monthly projection (value, landed cost, cumulative value)

## Purpose
For every month `m` of the session horizon (12-60 months, default `projection.horizon_months_default = 24`) and
every movement row (actual `movement_monthly` merged with modelled `session_movement_input`) the aggregator
computes **value** and **landed cost**, then groups the rows into the four cumulative tables persisted as
`projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction` and `projection_summary`.
Grouping happens here, not in SQL ([ADR-0003](/architecture/adr/0003-grouping-in-kotlin-not-sql.md)), so cover,
stress test and reports see identical figures.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| quantity | Decimal | units | movement row (`quantity`) | ≥ 0 |
| unitPrice | Decimal | price basis currency / unit | movement row (`unit_price`) | ≥ 0 |
| priceIndex(m) | Decimal | ratio | `baseline_price.price(m) / baseline_price.price(m0)` for the corridor, `m0` = first month of the grid | > 0, scale 4; `1` when `m0` has no price |
| tariffRate(productGroup, country) | Decimal | ratio | parameter `tariff.rate` | ≥ 0 |
| handlingCost(city) | Decimal | price basis currency / unit | parameter `handling.cost` | ≥ 0 |
| transportCost(mode) | Decimal | price basis currency / unit | parameter `transport.cost` | ≥ 0 |

Grouping keys per row: `period`, `sub_product`, `city`, `transport_mode`, `direction`. Dimension = `city` for
`product1`, `transport_mode` for `product2`.

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| `tariff.rate` | per product group + country | `scope_product_group`, `scope_country` |
| `handling.cost` | per city | `scope_value = city` |
| `transport.cost` | per transport mode | `scope_value = mode` |
| `projection.horizon_months_default` | 24 | global |

Values are read from `meeting_session.parameter_snapshot`, never live from `parameter_set`.

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| value | Decimal | price basis currency | scale 2, HALF_EVEN, per row |
| landed_cost | Decimal | price basis currency | scale 2, HALF_EVEN, per row |
| cumulative_value | Decimal | price basis currency | running sum of rounded group `value` over months |
| quantity (grouped) | Decimal | units | sum, scale 2 (`sumMoney`) |

## Formula
$$ value_m = qty \cdot unitPrice \cdot priceIndex(m) $$
$$ landedCost_m = value_m \cdot (1 + tariffRate) + qty \cdot handlingCost(city) + qty \cdot transportCost(mode) $$
$$ cumulativeValue_m = \sum_{k \le m} value_k \quad \text{(per group)} $$

Step list:
1. Build the month grid `m0 .. m0 + horizon - 1` (`MonthGrid.kt`).
2. For each row and month compute `value` and round (scale 2, HALF_EVEN).[^impl][^rounding]
3. Compute `landedCost` from the **rounded** value, round again.[^impl]
4. Group by sub-product / dimension value / direction / all, summing `quantity`, `value`, `landed_cost`.[^impl]
5. Per group, `cumulative_value(m) = cumulative_value(m-1) + value(m)`.[^impl]

# Computation
```kotlin
// mirrors ProjectionAggregator.kt — pure Kotlin, no Spring; Rounding.money = setScale(2, HALF_EVEN)
class ProjectionAggregator(private val params: ProjectionParams) {
    fun rowValue(qty: BigDecimal, unitPrice: BigDecimal, priceIndex: BigDecimal): BigDecimal =
        Rounding.money(qty * unitPrice * priceIndex)

    fun landedCost(value: BigDecimal, qty: BigDecimal, city: String, mode: TransportMode, group: ProductGroup, country: PriceBasis) =
        Rounding.money(
            value * (BigDecimal.ONE + params.tariffRate(group, country)) +
                qty * params.handlingCost(city) +
                qty * params.transportCost(mode)
        )

    fun aggregate(rows: List<ProjectionRow>, grid: MonthGrid): ProjectionTables =
        ProjectionTables(
            bySubProduct = cumulative(rows.groupBy { it.period to it.subProduct }, grid),
            byDimension  = cumulative(rows.groupBy { it.period to it.dimensionValue }, grid),
            byDirection  = cumulative(rows.groupBy { it.period to it.direction }, grid),
            summary      = cumulative(rows.groupBy { it.period to Unit }, grid),
        )
}
```

## Conventions
Month grid: calendar months from the session start month, horizon from `session_client_config.horizon_months` ·
Rounding: HALF_EVEN scale 2 per row, before grouping; cumulative sums add rounded values · Price basis:
`session_client_config.price_basis` selects the `unit_price` / baseline leg (`VLD|NRL`, `CST|MRD`) · Missing data:
modelled row replaces the actual row with the same grouping key; months without rows yield 0 and still appear ·
Time zone: UTC.

## Worked examples
Copied from the executor test.[^tests] Parameters: `tariffRate = 0.05`, `handlingCost(Aldmoor) = 0.80`,
`transportCost(ROAD) = 1.20`.

| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | typical month 1 | qty 100, unitPrice 12.50, priceIndex 1.04 | value **1300.00**, landedCost **1565.00** |
| 2 | month 2, cumulative | qty 100, unitPrice 12.50, priceIndex 1.06 | value **1325.00**, landedCost **1591.25**, cumulativeValue **2625.00** |
| 3 | rounding HALF_EVEN (ties to even) | 1.005 → ; 1.015 → | **1.00** ; **1.02** |

Derivation of example 1: `100 × 12.50 × 1.04 = 1300.00`;
`1300.00 × 1.05 + 100 × 0.80 + 100 × 1.20 = 1365.00 + 80.00 + 120.00 = 1565.00`.

## Audit 2026-10-12
Auditor: copilot/calc-auditor (Run 3). Files opened: `harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt`
(L36-L230) and `harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt` (L1-L130); parameter defaults from
`V9__parameters.sql` as listed in the pack. Items 8-11 concern the row assembly in `ProjectionInputAssembler.kt`,
which the pack names as a code reference of P1-001; they were observed there, outside the two audited files, and
need an owner decision rather than a documentation edit.

| # | Item | Documentation says | Code/test says | Severity | Action |
|---|---|---|---|---|---|
| 1 | value formula | `qty × unitPrice × priceIndex(m)`, scale 2 HALF_EVEN | `valueRow`: identical; test `value and landed cost of one row` → 1300.00 | MATCH | — |
| 2 | landed cost formula | `value × (1 + tariffRate) + qty × handlingCost(city) + qty × transportCost(mode)` from the rounded value | identical; same test → 1565.00 | MATCH | — |
| 3 | cumulative value | running sum of rounded group values per key | `group`: `cumulative += value` per key over the grid; test `second month with price index 1_06 and cumulative value` → 2625.00 | MATCH | — |
| 4 | rounding | HALF_EVEN scale 2 per row | `Rounding.money`; test `rounding is HALF_EVEN at scale 2` (1.005 → 1.00, 1.015 → 1.02) | MATCH | — |
| 5 | parameter defaults | tariff 0.05 (product1/VLD), handling Aldmoor 0.80, transport ROAD 1.20 | `V9__parameters.sql` L39, L46, L53: same values | MATCH | — |
| 6 | worked examples 1-3 | 1300.00 / 1565.00; 1325.00 / 1591.25 / 2625.00; 1.00 / 1.02 | same values in the three test methods | MATCH | — |
| 7 | grouped quantity | "sum, no rounding" | `sumMoney()` sets scale 2 on quantities too (`100.00`) | DOC-STALE | Outputs corrected (scale 2) |
| 8 | price index | "`price(m) / price(m0)`, 1.00 when no baseline" | `BaselinePriceService.priceIndex`: `price(m) / price(grid.start)` at scale 4, `1` when the first month has no price | DOC-STALE | Inputs corrected (scale 4, `m0` = grid start) |
| 9 | month grid start | "calendar months from the session start month" | `MonthGrid.startingAfter(today)`: the month after the current month, i.e. it moves while a session stays open across a month end | DOC-STALE | open question Q1 |
| 10 | actual rows | "actual `movement_monthly` merged with modelled rows" | months without modelled input carry the actual rows of the same calendar month one year earlier forward (last 12 full months repeat) | UNDOCUMENTED | open question Q2; add to Conventions once decided |
| 11 | replacement rule | "a modelled row replaces the actual row with the same grouping key" (also BR-P1-001-3) | any modelled input for a month discards **all** actual rows of that month; no test covers either behaviour | CODE-SUSPECT | open question Q2; add test case |

Findings: 6 MATCH, 3 DOC-STALE, 1 UNDOCUMENTED, 1 CODE-SUSPECT. The formulas and worked examples hold; the drift is
in how the input rows are assembled. `used_by` specs P1-001, P2-001, COV-001, STR-001 and RPT-001 inherit Q1 and Q2.

## Open questions
- [ ] Q1 (owner: harbor-platform-team) — Grid start: this concept and P1-001 say the grid starts at the session
  start month; the code starts at the month after today, so an open session's grid shifts at a month end. Which is
  intended? If the code is right, change the Conventions line and BR-P1-001-1; if the doc is right, pin the grid to
  `meeting_session.started_at`.
- [ ] Q2 (owner: harbor-platform-team) — Replacement granularity and carry-forward: BR-P1-001-3 says a modelled row
  replaces the actual row with the same `(period, sub_product, city, direction)`; the code replaces the whole month
  and, for months without modelled input, repeats the actual month one year earlier. Confirm the rule, then add a
  test case to `ProjectionAggregatorTest` or a service test for the assembler.

## Performance notes
Rows ≤ 60 months × ≤ 3 sub-products × ≤ 4 dimension values × 2 directions = 1 440 rows per session; computed in
memory on `getProduct1Projection` / `getProduct2Projection` and on `movements-loaded` refresh; result persisted
per session.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-09 | Rebuilt for the Harbor bundle; examples re-copied from `ProjectionAggregatorTest` | — |
| 2026-10-12 | Horizon totals (each table summed per key over the horizon, overall line, share of value) split out as [horizon_totals](horizon_totals.md); derived from these tables, never persisted | — |
| 2026-10-12 | Run 3 audit: 6 MATCH, 3 DOC-STALE (corrected), 1 UNDOCUMENTED, 1 CODE-SUSPECT → status draft, open questions Q1-Q2 for the owner | — |

[^impl]: ProjectionAggregator.kt (harbor-backend, `core`, layer `utils`)
[^rounding]: Rounding.kt (harbor-backend, `core`, layer `utils`)
[^tests]: ProjectionAggregatorTest.kt (harbor-backend, `core` tests, `utils`)
