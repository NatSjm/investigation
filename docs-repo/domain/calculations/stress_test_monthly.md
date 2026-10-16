---
type: Attested Computation
title: Stress test per month, scenario and dimension value
description: Monthly exposure, transport cost delta and cumulative exposure of a session under a market scenario, signed by the client role and broken down by city or transport mode.
tags: [calculation, stress]
status: stable
runtime: kotlin
parameters:
  - { name: role, type: Enum, required: true }
  - { name: uncoveredQty, type: Decimal, required: true }
  - { name: totalQty, type: Decimal, required: true }
  - { name: scenarioPrice, type: Decimal, required: true }
  - { name: baselinePrice, type: Decimal, required: true }
  - { name: scenarioTransport, type: Decimal, required: true }
  - { name: baselineTransport, type: Decimal, required: true }
executor:
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/StressTestCalculatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/doc-sync, at: 2026-10-09T08:00:00Z }
verified: { by: human:example-reviewer, at: 2026-10-08T15:00:00Z }
stale_after: 2027-01-06T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/main/kotlin/com/acme/harbor/utils/StressTestCalculator.kt
    title: StressTestCalculator.kt
  - id: tests
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/test/kotlin/com/acme/harbor/utils/StressTestCalculatorTest.kt
    title: StressTestCalculatorTest.kt
# --- repo extensions ---
name: stress_test_monthly
used_by: [STR-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/StressTestCalculator.kt
  - backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/StressTestCalculatorTest.kt
last_verified: 2026-10-08
---

# Stress test per month, scenario and dimension value

## Purpose
For every scenario of a session, every month of the horizon and every **dimension value** (city for Product 1,
transport mode for Product 2) the calculator produces `exposure`, `transport_cost_delta` and `cumulative_exposure`,
persisted in `stress_test_result` and shown as the monthly table on the Stress test page (STR-001).
Sign convention: a price rise hurts an importer (positive exposure = additional cost) and benefits an exporter.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| role | `ClientRole` | — | session effective role: `meeting_session.role_override` else [client_role_classification](/domain/calculations/client_role_classification.md) | `IMPORTER`, `EXPORTER`, `MIXED` (`UNDETERMINED` → treated as `MIXED`) |
| uncoveredQty(m, d) | Decimal | units | `projection_by_dimension.quantity × (1 − coverRatio(m))` per dimension value `d` | ≥ 0 |
| inQty / outQty (MIXED only) | Decimal | units | uncovered quantity per direction from `projection_by_direction` | ≥ 0 |
| totalQty(m, d) | Decimal | units | `projection_by_dimension.quantity` | ≥ 0 |
| price_s(m), transport_s(m) | Decimal | price basis currency / unit | [scenario_price_path](/domain/calculations/scenario_price_path.md) | > 0 |
| baseline(m), transportBaseline(m) | Decimal | price basis currency / unit | `baseline_price` | > 0 |

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| `stress.rounding_scale` | 2 | global |
| `role.importer_threshold` / `role.exporter_threshold` | 0.65 / 0.35 | via `client_role_classification` (sign only) |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| exposure | Decimal | price basis currency | `stress.rounding_scale` (2), HALF_EVEN, per month and dimension value |
| transport_cost_delta | Decimal | price basis currency | same |
| cumulative_exposure | Decimal | price basis currency | running sum of `exposure + transport_cost_delta` over months |

## Formula
$$ sign = \begin{cases} +1 & IMPORTER \\ -1 & EXPORTER \\ 0 & MIXED \text{ (use net direction quantity)} \end{cases} $$
$$ exposure_m = uncoveredQty_m \cdot (price_s(m) - baseline(m)) \cdot sign $$
$$ exposure_m^{MIXED} = (inQty_m - outQty_m) \cdot (price_s(m) - baseline(m)) $$
$$ transportCostDelta_m = totalQty_m \cdot (transport_s(m) - transportBaseline(m)) $$
$$ cumulativeExposure_m = \sum_{k \le m} (exposure_k + transportCostDelta_k) $$

Step list:
1. Resolve the effective role of the session (override wins).[^impl]
2. Per scenario, month and dimension value compute `exposure` with the role sign; for `MIXED` use the net
   uncovered quantity `inQty − outQty` instead of `uncoveredQty × sign`.[^impl]
3. Compute `transportCostDelta` on the **total** quantity (cover does not apply to transport).[^impl]
4. Round both to `stress.rounding_scale`; `cumulativeExposure` adds the rounded `exposure + transportCostDelta`.[^impl]

# Computation
```kotlin
// mirrors StressTestCalculator.kt — pure Kotlin, no Spring
class StressTestCalculator(private val scale: Int = 2) {
    private fun r(v: BigDecimal) = v.setScale(scale, RoundingMode.HALF_EVEN)

    fun month(role: ClientRole, q: Quantities, p: Prices): StressMonth {
        val priceDiff = p.scenarioPrice - p.baselinePrice
        val exposure = when (role) {
            ClientRole.IMPORTER -> q.uncovered * priceDiff
            ClientRole.EXPORTER -> q.uncovered * priceDiff.negate()
            else -> (q.uncoveredIn - q.uncoveredOut) * priceDiff          // MIXED / UNDETERMINED
        }
        val transportDelta = q.total * (p.scenarioTransport - p.baselineTransport)
        return StressMonth(r(exposure), r(transportDelta))
    }

    fun cumulative(months: List<StressMonth>): List<StressMonth> {
        var acc = BigDecimal.ZERO.setScale(scale)
        return months.map { m -> acc += m.exposure + m.transportCostDelta; m.copy(cumulativeExposure = acc) }
    }
}
```

## Conventions
Month grid: session horizon · Rounding: HALF_EVEN, `stress.rounding_scale` (2), per month before the running sum ·
Price basis: `session_client_config.price_basis` for both baseline and scenario · Missing data: a month without
projection rows yields 0 exposure and 0 delta but is still emitted · Sign: positive = extra cost for the client ·
Time zone: UTC.

## Worked examples
Copied from the executor test.[^tests] Common inputs: `uncoveredQty = 100`, `totalQty = 150`,
baseline price `10.00`, baseline transport `2.00`, scenario transport `2.50`.

| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | importer, month 1 | `IMPORTER`, price 10.00 → 11.00, transport 2.00 → 2.50 | exposure **100.00**, transportCostDelta **75.00**, cumulative **175.00** |
| 2 | importer, month 2 (cumulative) | `IMPORTER`, price 10.00 → 12.00, transport 2.00 → 2.50 | exposure **200.00**, transportCostDelta **75.00**, cumulative **450.00** |
| 3 | exporter sign | `EXPORTER`, price 10.00 → 11.00, transport 2.00 → 2.50 | exposure **−100.00**, cumulative **−25.00** |
| 4 | mixed, net direction | `MIXED`, uncovered in 60 / out 40, price 10.00 → 11.00 | exposure **20.00** |

Derivation of example 1: `100 × (11.00 − 10.00) × (+1) = 100.00`; `150 × (2.50 − 2.00) = 75.00`;
`100.00 + 75.00 = 175.00`.
Example 2: `175.00 + (200.00 + 75.00) = 450.00`. Example 3: `−100.00 + 75.00 = −25.00`.

## Performance notes
`months (≤ 60) × scenarios (≤ 10 per session) × dimension values (4)` = at most 2 400 rows per `runStressTest`;
previous results of the session are deleted and re-inserted in one transaction.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-09 | Rebuilt for the Harbor bundle; examples re-copied from `StressTestCalculatorTest` | — |

[^impl]: StressTestCalculator.kt (harbor-backend, `core`, layer `utils`)
[^tests]: StressTestCalculatorTest.kt (harbor-backend, `core` tests, `utils`)
