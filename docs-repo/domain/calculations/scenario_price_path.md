---
type: Attested Computation
title: Scenario price path (price and transport price per month)
description: Applies the shocks of a market scenario multiplicatively to the baseline price and transport price curve from the shock's start month onwards.
tags: [calculation, market]
status: draft
runtime: kotlin
parameters:
  - { name: baselinePrice, type: Decimal, required: true }
  - { name: baselineTransport, type: Decimal, required: true }
  - { name: shocks, type: List<Shock>, required: true }
  - { name: month, type: Int, required: true }
executor:
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ScenarioPricePathTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/doc-sync, at: 2026-10-09T08:00:00Z }
stale_after: 2027-01-07T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/main/kotlin/com/acme/harbor/utils/ScenarioPricePath.kt
    title: ScenarioPricePath.kt
# --- repo extensions ---
name: scenario_price_path
used_by: [MKT-001, STR-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/ScenarioPricePath.kt
  - backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/ScenarioPricePathTest.kt
last_verified: null
---

# Scenario price path (price and transport price per month)

> **Draft** — formula taken from `ScenarioPricePath.kt`; worked examples not yet copied from the unit test.

## Purpose
Turns a `market_scenario` (name, kind, `shocks jsonb`) into two monthly series over the session horizon:
`price_s(m)` and `transportPrice_s(m)`. Shown as the transport price chart per scenario on the Stress test page
and consumed by [stress_test_monthly](/domain/calculations/stress_test_monthly.md).

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| baseline(m) | Decimal | price basis currency / unit | `baseline_price.price` for the session corridor | > 0 |
| transportBaseline(m) | Decimal | price basis currency / unit | `baseline_price.transport_price` | > 0 |
| shocks[] | `Shock(fromMonth, priceChangePct, transportChangePct)` | month index, ratio | `market_scenario.shocks` | `fromMonth` within horizon; pct > −1 |

## Parameters
None from `parameter_set`.

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| price_s(m) | Decimal | price basis currency / unit | scale 4, HALF_EVEN |
| transportPrice_s(m) | Decimal | price basis currency / unit | scale 4, HALF_EVEN |

## Formula
$$ price_s(m) = baseline(m) \cdot \prod_{shock:\, fromMonth \le m} (1 + priceChangePct_{shock}) $$
$$ transportPrice_s(m) = transportBaseline(m) \cdot \prod_{shock:\, fromMonth \le m} (1 + transportChangePct_{shock}) $$

Step list:
1. Sort shocks by `fromMonth`.[^impl]
2. For each month `m` multiply the baseline by `(1 + pct)` of every shock whose `fromMonth <= m` (shocks are
   cumulative, not replacing).[^impl]
3. Round to scale 4; the baseline scenario is the empty shock list.[^impl]

# Computation
```kotlin
// mirrors ScenarioPricePath.kt — draft excerpt
object ScenarioPricePath {
    fun factor(shocks: List<Shock>, month: Int, pct: (Shock) -> BigDecimal): BigDecimal =
        shocks.filter { it.fromMonth <= month }
            .fold(BigDecimal.ONE) { acc, s -> acc * (BigDecimal.ONE + pct(s)) }

    fun price(baseline: BigDecimal, shocks: List<Shock>, month: Int): BigDecimal =
        (baseline * factor(shocks, month) { it.priceChangePct }).setScale(4, RoundingMode.HALF_EVEN)
}
```

## Conventions
Month grid: session horizon, `fromMonth` is a 0-based index on that grid (**to confirm**) · Rounding: scale 4,
HALF_EVEN per month · Price basis: corridor leg of `session_client_config.price_basis` · Missing baseline month:
carry the last known value forward (**to confirm**) · Time zone: UTC.

## Worked examples
| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | single shock | TODO (copy from `ScenarioPricePathTest`) | TODO |
| 2 | two cumulative shocks | TODO | TODO |
| 3 | no shocks (baseline) | TODO | equals baseline |

## Performance notes
`months × scenarios`; shocks per scenario ≤ 12. Computed on demand, not persisted.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-09 | Draft created for the Harbor bundle | — |

[^impl]: ScenarioPricePath.kt (harbor-backend, `core`, layer `utils`)
