---
type: Attested Computation
title: Monthly projection (value, landed cost, cumulative value)
description: Per session and month computes value and landed cost of every movement row and groups them into the four cumulative projection tables (by sub-product, by dimension, by direction, summary).
tags: [calculation, product1, product2, projection]
status: stable
runtime: kotlin
parameters:
  - { name: quantity, type: Decimal, required: true }
  - { name: unitPrice, type: Decimal, required: true }
  - { name: priceIndex, type: Decimal, required: true }
  - { name: tariffRate, type: Decimal, required: true }
  - { name: handlingCost, type: Decimal, required: true }
  - { name: transportCost, type: Decimal, required: true }
executor:
  resource: backend/core/src/test/kotlin/harbor/utils/ProjectionAggregatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.ps1
generated: { by: copilot/doc-sync, at: 2026-10-09T08:00:00Z }
verified: { by: human:example-reviewer, at: 2026-10-08T15:00:00Z }
stale_after: 2027-01-06T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt
    title: ProjectionAggregator.kt
  - id: tests
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/test/kotlin/harbor/utils/ProjectionAggregatorTest.kt
    title: ProjectionAggregatorTest.kt
  - id: rounding
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/main/kotlin/harbor/utils/Rounding.kt
    title: Rounding.kt
# --- repo extensions ---
name: monthly_projection
used_by: [P1-001, P2-001, COV-001, STR-001, RPT-001]
code_refs:
  - backend/core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt
  - backend/core/src/main/kotlin/harbor/utils/Rounding.kt
  - backend/core/src/test/kotlin/harbor/utils/ProjectionAggregatorTest.kt
last_verified: 2026-10-08
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
| priceIndex(m) | Decimal | ratio | `baseline_price.price(m) / baseline_price.price(m0)` for the corridor | > 0; 1.00 when no baseline |
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
| quantity (grouped) | Decimal | units | sum, no rounding |

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

## Performance notes
Rows ≤ 60 months × ≤ 3 sub-products × ≤ 4 dimension values × 2 directions = 1 440 rows per session; computed in
memory on `getProduct1Projection` / `getProduct2Projection` and on `movements-loaded` refresh; result persisted
per session.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-09 | Rebuilt for the Harbor bundle; examples re-copied from `ProjectionAggregatorTest` | — |
| 2026-10-12 | Horizon totals (each table summed per key over the horizon, overall line, share of value) split out as [horizon_totals](horizon_totals.md); derived from these tables, never persisted | — |

[^impl]: ProjectionAggregator.kt (harbor-backend, `core`, layer `utils`)
[^rounding]: Rounding.kt (harbor-backend, `core`, layer `utils`)
[^tests]: ProjectionAggregatorTest.kt (harbor-backend, `core` tests, `utils`)
