---
type: Attested Computation
title: Horizon totals (breakdown without months)
description: "Sums each monthly projection table over the whole session horizon per key (sub-product, city or transport mode, direction) and adds the overall line with every key's share of the total value."
tags: [calculation, product1, product2, projection]
status: draft
runtime: kotlin
parameters:
  - { name: quantity, type: Decimal, required: true }
  - { name: value, type: Decimal, required: true }
  - { name: landedCost, type: Decimal, required: true }
executor:
  resource: backend/core/src/test/kotlin/harbor/utils/ProjectionAggregatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.ps1
generated: { by: copilot/doc-sync, at: 2026-10-12T10:00:00Z }
stale_after: 2027-01-10T00:00:00Z
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
name: horizon_totals
used_by: [P1-001]
code_refs:
  - backend/core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt
  - backend/core/src/main/kotlin/harbor/utils/Rounding.kt
  - backend/core/src/test/kotlin/harbor/utils/ProjectionAggregatorTest.kt
last_verified: null
---

# Horizon totals (breakdown without months)

## Purpose
The monthly projection ([monthly_projection](monthly_projection.md)) answers "how much per month". The overview also
needs "how much in total, and split how" without the month axis: per sub-product, per city (Product 1) or transport
mode (Product 2), per direction, and overall. This calculation sums each of the three breakdown tables over the whole
session horizon per key and adds one overall line taken from the summary table, with every key's **share of value**.
The result is returned as `tables.totals` by `getProduct1Overview`, `getProduct1Projection`, `putProduct1Movements`
and their Product 2 counterparts, and shown as three separate tables under the monthly ones; the client screen
mirrors them (PRS-001).[^impl]

The totals are **derived, never persisted**: they are recomputed from the monthly lines wherever the tables are loaded
(`projection_*` tables via `ProjectionDao`, or a fresh aggregation), so they cannot drift from the monthly figures.[^impl]

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| quantity | Decimal | units | one monthly line (`ProjectionLine.quantity`) | ≥ 0 |
| value | Decimal | price basis currency | one monthly line (`ProjectionLine.value`), already rounded | ≥ 0 |
| landedCost | Decimal | price basis currency | one monthly line (`ProjectionLine.landedCost`), already rounded | ≥ 0 |

Grouping key per table: `sub_product`, dimension value (`city` or `transport_mode`), `direction`. The overall line uses
the summary table (`totalQuantity`, `totalValue`, `totalLandedCost`).

## Parameters
None. Everything comes from the monthly tables; the parameter snapshot is applied upstream by `monthly_projection`.

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| quantity | Decimal | units | sum of the monthly quantities, scale 2 |
| value | Decimal | price basis currency | sum of the rounded monthly values, scale 2 (no second rounding of the inputs) |
| landedCost | Decimal | price basis currency | sum of the rounded monthly landed costs, scale 2 |
| shareOfValue | Decimal | ratio | `value / overall.value`, scale 4, HALF_EVEN; `0.0000` when the overall value is 0; the overall line carries `1.0000` |

Keys are sorted as in the monthly tables. The overall line has the key `ALL`; it is identical in all three breakdowns.

## Formula
$$ total_k = \sum_{m \in horizon} line_{k,m} \quad \text{for quantity, value, landedCost} $$
$$ share_k = \frac{value_k}{\sum_{k'} value_{k'}} = \frac{value_k}{overall.value} $$

Step list:
1. Take the four monthly tables of the session (output of `monthly_projection`).[^impl]
2. Per breakdown table, group the lines by key and sum `quantity`, `value`, `landedCost` over all months of the
   horizon (`sumMoney`: add, then scale 2).[^impl][^rounding]
3. Overall line: the same sums over the summary table.[^impl]
4. `shareOfValue = divideAsRatio(value_k, overall.value)` (scale 4, HALF_EVEN, `0.0000` on a zero divisor).[^rounding]
5. By construction the keys of every breakdown add up to the overall line (the same rows are summed three ways).

# Computation
```kotlin
// mirrors ProjectionAggregator.totals / totalsOf — pure Kotlin, no Spring
fun totals(tables: Tables): Totals {
    val overallValue = tables.summary.map { it.totalValue }.sumMoney()
    val overall = Total(ALL, tables.summary.map { it.totalQuantity }.sumMoney(), overallValue,
        tables.summary.map { it.totalLandedCost }.sumMoney(),
        if (overallValue.signum() == 0) Rounding.ZERO_RATIO else BigDecimal.ONE.ratio())
    return Totals(totalsOf(tables.bySubProduct, overallValue), totalsOf(tables.byDimension, overallValue),
        totalsOf(tables.byDirection, overallValue), overall)
}

fun totalsOf(lines: List<Line>, overallValue: BigDecimal): List<Total> =
    lines.groupBy { it.key }.toSortedMap().map { (key, perMonth) ->
        val value = perMonth.map { it.value }.sumMoney()
        Total(key, perMonth.map { it.quantity }.sumMoney(), value, perMonth.map { it.landedCost }.sumMoney(),
            Rounding.divideAsRatio(value, overallValue))
    }
```

## Conventions
Rounding: inputs are the already rounded monthly figures (scale 2); sums are not rounded again beyond scale 2; the
share is scale 4 HALF_EVEN · Price basis: inherited from the monthly tables · Missing data: a key with no rows does
not appear; an empty projection yields an overall line of zeros with share `0.0000` and empty breakdowns · The
dimension filter of the overview (`?city=`) restricts the monthly `byDimension` table and therefore its totals too.

## Worked examples
Copied from the executor test.[^tests] Monthly lines as in `monthly_projection` (tariff 0.05, handling Aldmoor 0.80,
transport ROAD 1.20, price index 1.04 in month 1 and 1.06 in month 2).

| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | one key over two months | P1-STD: month 1 value 1300.00 / landed 1565.00, month 2 value 1325.00 / landed 1591.25, qty 100 each | quantity **200.00**, value **2625.00**, landedCost **3156.25**, shareOfValue **0.6646** |
| 2 | second key, one month | P1-PRM out of Carrow in month 2: qty 100, value 1325.00, landed 1325.00 × 1.05 + 100 × 1.20 | value **1325.00**, landedCost **1511.25**, shareOfValue **0.3354** |
| 3 | overall line | the two keys above | value **3950.00**, shareOfValue **1.0000**; `byDimension` Carrow and `byDirection` OUT both **1325.00** |
| 4 | empty projection | no rows | overall value **0.00**, shareOfValue **0.0000**, no keys |

Derivation of example 1: `2625.00 / 3950.00 = 0.66455...` → `0.6646` (HALF_EVEN at scale 4).

## Performance notes
Input is at most 60 months × (3 sub-products + 4 dimension values + 2 directions) = 540 lines per session; the totals
are computed in memory on every read of the tables and are not stored.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-12 | Created: totals split out of `monthly_projection` as their own concept; examples copied from `ProjectionAggregatorTest` | — |

[^impl]: ProjectionAggregator.kt (harbor-backend, `core`, layer `utils`)
[^rounding]: Rounding.kt (harbor-backend, `core`, layer `utils`)
[^tests]: ProjectionAggregatorTest.kt (harbor-backend, `core` tests, `utils`)
