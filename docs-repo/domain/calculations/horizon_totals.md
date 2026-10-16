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
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/calc-auditor, at: 2026-10-12T20:30:00Z }
stale_after: 2027-01-10T00:00:00Z
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
name: horizon_totals
used_by: [P1-001, P2-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/Rounding.kt
  - backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt
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
(`projection_*` tables via `ProjectionRepository`, or a fresh aggregation), so they cannot drift from the monthly figures.[^impl]

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
transport ROAD 1.20, price index 1.04 in month 1 and 1.06 in month 2). Only values the test asserts are listed.

| # | Case | Test method | Inputs | Expected output |
|---|---|---|---|---|
| 1 | one key over two months | `horizon totals sum the monthly tables per key and share the overall value` | P1-STD, Aldmoor, ROAD, IN, qty 100, unit price 12.50 in months 1 and 2 (plus the P1-PRM row of #2) | `bySubProduct` P1-STD: quantity **200.00**, value **2625.00**, landedCost **3156.25**, shareOfValue **0.6646** |
| 2 | second key, one month | same | P1-PRM, Carrow, ROAD, OUT, qty 100, unit price 12.50 in month 2 | `bySubProduct` P1-PRM landedCost **1511.25**; `byDimension` Carrow value **1325.00**; `byDirection` OUT value **1325.00** |
| 3 | overall line | same | the three rows of #1 and #2 | overall value **3950.00**, shareOfValue **1.0000**; sum of the `bySubProduct` values = overall value |
| 4 | empty projection | `horizon totals of an empty projection are zero` | no rows | overall value **0.00**, shareOfValue **0.0000**, `bySubProduct` empty |

Derivation of #1 (test comment): `2625.00 / 3950.00 = 0.66456...` → `0.6646`. Not a tie, so this row does not
distinguish HALF_EVEN from HALF_UP (see re-audit item 3).

## Audit 2026-10-12 (Run 3, superseded by the re-audit below)
Auditor: copilot/calc-auditor (Run 3). Files opened: `harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt`
(L100-L200, `totals` / `totalsOf`) and `harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt` (L75-L110).

| # | Item | Documentation says | Code/test says | Severity | Action |
|---|---|---|---|---|---|
| 1 | per-key sums | sum of the rounded monthly lines per key, scale 2 | `totalsOf`: `groupBy key`, `sumMoney` on quantity / value / landedCost; test `horizon totals sum the monthly tables per key and share the overall value` → 200.00 / 2625.00 / 3156.25 | MATCH | — |
| 2 | overall line | sums of the summary table, key `ALL`, share 1.0000 | `totals`: identical; same test → 3950.00 / 1.0000 | MATCH | — |
| 3 | share of value | `value_k / overall.value`, scale 4 HALF_EVEN, 0.0000 on zero | `Rounding.divideAsRatio`; same test → 0.6646 | MATCH | — |
| 4 | key order | as in the monthly tables | `toSortedMap()`; monthly keys are `sorted()` too | MATCH | — |
| 5 | empty projection | overall 0.00 / 0.0000, no keys | test `horizon totals of an empty projection are zero` | MATCH | — |
| 6 | derived, not persisted | recomputed from the loaded lines | `Tables.totals` is a computed property; `ProjectionRepository` loads the four tables only | MATCH | — |

Findings: 6 MATCH, no drift. Status stays `draft` until the owner's decision (Run 4).

## Audit 2026-10-12 (re-audit)
Auditor: copilot/calc-auditor. Files opened: `harbor-core/src/main/kotlin/com/acme/harbor/utils/ProjectionAggregator.kt`
(L20-L36, L78-L216) and `harbor-core/src/test/kotlin/com/acme/harbor/utils/ProjectionAggregatorTest.kt` (L1-L111). `Rounding.kt`
and `ProjectionRepository` were not opened; claims resting on them are marked. No `parameter_set` keys are read.

| # | Item | Documentation says | Code/test says | Severity | Action |
|---|---|---|---|---|---|
| 1 | per-key sums | `sumMoney` of quantity / value / landedCost per key over the horizon | `totalsOf` L184-L194: `groupBy key`, `sumMoney`; test L84-L87 → 200.00 / 2625.00 / 3156.25 | MATCH | — |
| 2 | overall line | sums of the summary table, key `ALL` | `totals` L166-L174; test L92-L93 → 3950.00 / 1.0000 | MATCH | — |
| 3 | share of value | `divideAsRatio(value_k, overall.value)`, scale 4 HALF_EVEN, `0.0000` on zero | L192 calls `Rounding.divideAsRatio`; test L88 (0.6646), L101 (0.0000). 0.66456 is not a tie and `Rounding.kt` was not opened, so the mode is not evidenced | MATCH | Q3: add a tie case |
| 4 | overall share | Outputs: "the overall line carries `1.0000`" | L173: `0.0000` when the overall value is 0, otherwise `1.0000` (Conventions already says so for an empty projection) | DOC-STALE | spec-writer: qualify the Outputs row |
| 5 | sum of shares | not stated; step 5 claims additivity for the sums only | each key's share is rounded on its own (L192) with no remainder correction, so a breakdown's shares can add up to other than 1.0000 (e.g. three equal keys) | UNDOCUMENTED | Q1 (owner) |
| 6 | key order | as in the monthly tables | L185 `toSortedMap()`; monthly keys L138 `sorted()` (natural string order) | MATCH | — |
| 7 | `UNKNOWN` key | not mentioned | rows without a city / transport mode are grouped under `UNKNOWN` (L131-L134, L214) and appear as an ordinary sorted key in the `byDimension` totals | UNDOCUMENTED | spec-writer: add to Conventions |
| 8 | empty projection | overall line of zeros, share `0.0000`, empty breakdowns | test L99-L102 asserts the overall value, the share and an empty `bySubProduct` only; empty `byDimension` / `byDirection` and zero quantity / landedCost follow from the code (L167-L173), not the test | MATCH | Q3: add assertions |
| 9 | derived, not persisted | recomputed wherever the tables are loaded | `Tables.totals` is a computed getter (L103-L104). Run 3's "`ProjectionRepository` loads the four tables only" is outside the two files and was not re-verified | MATCH | — |
| 10 | dimension filter | Conventions: `?city=` restricts the monthly `byDimension` table "and therefore its totals" | `aggregate` / `totals` take no filter. P1-001's code-based conflict callout (`Product1Manager.overview` L39): rows are filtered **before** aggregation, so all four tables and the overall line shrink | DOC-STALE | Q2 (owner, same as P1-001 city-filter question) |
| 11 | worked example 2 | P1-PRM value 1325.00, shareOfValue **0.3354** | the test asserts P1-PRM landedCost 1511.25 and Carrow / OUT value 1325.00; neither the P1-PRM value nor a share 0.3354 is asserted (0.3354 was hand-computed) | DOC-STALE | example restricted to test values (done); Q3 |
| 12 | worked-example provenance | rows without test method names | procedure step 6 requires the method name in each row | DOC-STALE | method names added (done) |
| 13 | breakdowns add up to overall | "by construction" for all three breakdowns | follows from the code (same valued rows, scale-2 sums are exact); test L94 asserts it for `bySubProduct` only | MATCH | Q3: assert for the other two |

Findings: 13 items: 7 MATCH, 4 DOC-STALE (2 fixed in the worked examples, 2 left to spec-writer / owner),
2 UNDOCUMENTED, 0 CODE-SUSPECT. No number was changed except removing the untested share 0.3354.

## Open questions
- [ ] Q1 (owner: harbor-platform-team) — Shares rounded per key can add up to 0.9999 or 1.0001 in a breakdown while
  the overall line shows 1.0000. Acceptable on screen (and in the PRS-001 mirror), or should the largest-remainder
  key absorb the difference? Then document it here and in BR-P1-001-11.
- [ ] Q2 (owner: harbor-platform-team) — City filter scope: decided by P1-001's open question; then rewrite the
  Conventions sentence on `?city=` (today it contradicts the code-based P1-001 finding).
- [ ] Q3 (backend, `ProjectionAggregatorTest`) — add test cases for a share that is a tie at scale 4 (HALF_EVEN
  evidence), the P1-PRM `bySubProduct` value and share, empty `byDimension` / `byDirection` with zero overall
  quantity / landedCost, and additivity of `byDimension` / `byDirection`. Worked examples gain rows only from these.

## Performance notes
Input is at most 60 months × (3 sub-products + 4 dimension values + 2 directions) = 540 lines per session; the totals
are computed in memory on every read of the tables and are not stored.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-12 | Created: totals split out of `monthly_projection` as their own concept; examples copied from `ProjectionAggregatorTest` | — |
| 2026-10-12 | Re-audit: 13 items (7 MATCH, 4 DOC-STALE, 2 UNDOCUMENTED); worked examples restricted to test-asserted values with method names; Q1-Q3 opened | — |

[^impl]: ProjectionAggregator.kt (harbor-backend, `core`, layer `utils`)
[^rounding]: Rounding.kt (harbor-backend, `core`, layer `utils`)
[^tests]: ProjectionAggregatorTest.kt (harbor-backend, `core` tests, `utils`)
