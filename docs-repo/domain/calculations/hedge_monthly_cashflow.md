---
type: Attested Computation
title: Hedge monthly cashflow (fixed vs floating leg)
description: Monthly net cashflow of a payer swap hedging a floating-rate loan (ACT/360, HALF_EVEN 2dp); feeds the comparison graph and stress test.
tags: [calculation, hedges]
status: stable
runtime: kotlin
parameters:
  - { name: notional_m, type: Decimal, required: true }
  - { name: fixed_rate, type: Decimal, required: true }
  - { name: float_rate_m, type: Decimal, required: true }
  - { name: days_m, type: Int, required: true }
executor:
  resource: be/src/test/kotlin/com/bank/advisory/hedge/calc/MonthlyCashflowCalculatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.ps1
generated: { by: copilot/doc-sync, at: 2026-09-30T19:00:00Z }
verified: { by: human:example-quant, at: 2026-09-30T20:00:00Z }
stale_after: 2026-12-29T00:00:00Z
sources:
  - id: impl
    resource: https://git.bank/be/blob/main/hedge/src/main/kotlin/com/bank/advisory/hedge/calc/MonthlyCashflowCalculator.kt#L20-L95
    title: MonthlyCashflowCalculator.kt
  - id: tests
    resource: https://git.bank/be/blob/main/hedge/src/test/kotlin/com/bank/advisory/hedge/calc/MonthlyCashflowCalculatorTest.kt
    title: MonthlyCashflowCalculatorTest.kt
# --- repo extensions ---
name: hedge_monthly_cashflow
used_by: [HEDGE-001]
code_refs:
  - be/src/main/kotlin/com/bank/advisory/hedge/calc/MonthlyCashflowCalculator.kt#L20-L95
  - be/src/test/kotlin/com/bank/advisory/hedge/calc/MonthlyCashflowCalculatorTest.kt
last_verified: 2026-09-30
---

# Hedge monthly cashflow (fixed vs floating leg)

> **Example** — illustrative numbers, not the real bank formula.

## Purpose
Monthly net cashflow of a payer swap hedging a floating-rate loan; feeds the comparison graph and stress test.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| notional_m | Decimal | CCY | loan schedule for month m | ≥ 0 |
| fixed_rate | Decimal | % p.a. | proposal | any |
| float_rate_m | Decimal | % p.a. | market fixing / scenario | may be negative |
| days_m | Int | days | calendar | 28–31 |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| net_cashflow_m | Decimal | CCY | 2 dp, HALF_EVEN, per month |

## Formula
$$ net_m = notional_m \cdot (fixed\_rate - float\_rate_m) \cdot \frac{days_m}{360} $$

Step list:
1. Take notional at start of month m.
2. Compute accrual factor `days_m / 360` (ACT/360).[^impl]
3. Net = notional × (fixed − float) × factor; round HALF_EVEN to 2 dp.[^impl]

# Computation
```kotlin
// illustrative, mirrors MonthlyCashflowCalculator.kt#L40-L48
fun net(notional: BigDecimal, fixed: BigDecimal, float: BigDecimal, days: Int): BigDecimal =
    notional.multiply(fixed.subtract(float))
        .multiply(BigDecimal(days)).divide(BigDecimal(360), MathContext.DECIMAL128)
        .divide(BigDecimal(100), 2, RoundingMode.HALF_EVEN)
```

## Conventions
Day-count: ACT/360 · Rounding: HALF_EVEN 2dp per month · Calendar: TARGET · Negative rates: pass-through
(no floor) · Time zone: Europe/Warsaw.

## Worked examples
Copied from the executor test.[^tests]

| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | typical | 1,000,000; 3.00%; 2.50%; 30 | 416.67 |
| 2 | boundary (29-day Feb) | 1,000,000; 3.00%; 2.50%; 29 | 402.78 |
| 3 | negative float | 1,000,000; 3.00%; −0.50%; 31 | 3,013.89 |

## Performance notes
Computed for tenor ≤ 360 months × up to 20 stress scenarios per proposal; results cached per proposal version.

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-09-30 | Example created | — |

[^impl]: MonthlyCashflowCalculator.kt (BE, main)
[^tests]: MonthlyCashflowCalculatorTest.kt (BE, main)
