---
type: Attested Computation
title: Cover ratio per month
description: Share of the projected value of a month that is covered by valid cover policies, per sub-product and in total (scale 4); feeds the cover ratio charts and the uncovered quantity of the stress test.
tags: [calculation, cover]
status: draft
runtime: kotlin
parameters:
  - { name: value, type: Decimal, required: true }
  - { name: coveredShare, type: Decimal, required: true }
  - { name: month, type: LocalDate, required: true }
executor:
  resource: backend/core/src/test/kotlin/harbor/utils/CoverRatioCalculatorTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/doc-sync, at: 2026-10-09T08:00:00Z }
stale_after: 2027-01-07T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/core/src/main/kotlin/harbor/utils/CoverRatioCalculator.kt
    title: CoverRatioCalculator.kt
# --- repo extensions ---
name: cover_ratio
used_by: [COV-001, P1-001, P2-001, STR-001]
code_refs:
  - backend/core/src/main/kotlin/harbor/utils/CoverRatioCalculator.kt
  - backend/core/src/test/kotlin/harbor/utils/CoverRatioCalculatorTest.kt
last_verified: null
---

# Cover ratio per month

> **Draft** — formula taken from `CoverRatioCalculator.kt`; worked examples not yet copied from the unit test.

## Purpose
For every month `m` of the session horizon, the share of projected **value** that is covered by `cover_policy`
rows valid in `m`. Returned per sub-product by `getCoverSummary`, drawn as the cover ratio chart on the product
overview pages and stored in `projection_summary.cover_ratio`. The complement `1 − coverRatio(m)` gives the
uncovered quantity used by [stress_test_monthly](/domain/calculations/stress_test_monthly.md).

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| value(m, subProduct) | Decimal | price basis currency | `projection_by_subproduct.value` | ≥ 0 |
| coveredShare | Decimal | ratio | `cover_policy.covered_share` of the policy matching `client_id`, `product_group`, `sub_product` with `valid_from <= m <= valid_to` | 0..1 |

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| `cover.default_premium_rate` | 0.012 | used by quotes, not by this ratio |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| coveredValue(m) | Decimal | price basis currency | scale 2, HALF_EVEN |
| coverRatio(m) | Decimal | ratio | scale 4, HALF_EVEN; `0` when `totalValue = 0` |

## Formula
$$ coveredValue(m) = \sum_{rows} value_{row}(m) \cdot coveredShare_{policy(row, m)} $$
$$ coverRatio(m) = \frac{coveredValue(m)}{totalValue(m)} \quad (0 \text{ when } totalValue(m) = 0) $$

Step list:
1. For each projection row and month find the matching policy valid in `m` (none → `coveredShare = 0`).[^impl]
2. Sum `value × coveredShare` → `coveredValue(m)`; sum `value` → `totalValue(m)`.[^impl]
3. Divide at scale 4, HALF_EVEN; return `0` when `totalValue(m) = 0`.[^impl]

# Computation
```kotlin
// mirrors CoverRatioCalculator.kt — draft excerpt
object CoverRatioCalculator {
    fun ratio(coveredValue: BigDecimal, totalValue: BigDecimal): BigDecimal =
        if (totalValue.signum() == 0) BigDecimal.ZERO.setScale(4)
        else coveredValue.divide(totalValue, 4, RoundingMode.HALF_EVEN)
}
```

## Conventions
Month grid: session horizon · Rounding: ratio scale 4, HALF_EVEN · Policy matching: by `sub_product`; a policy
without `sub_product` matches all sub-products of the product group (**to confirm**) · Overlapping policies: shares
are summed and capped at 1 (**to confirm**) · Time zone: UTC.

## Worked examples
| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | typical | TODO (copy from `CoverRatioCalculatorTest`) | TODO |
| 2 | no policy in month | TODO | TODO |
| 3 | total value 0 | TODO | `0.0000` |

## Performance notes
Computed together with the projection refresh; policies per client are few (< 20).

## Change log
| Date | Change | Ref |
|---|---|---|
| 2026-10-09 | Draft created for the Harbor bundle | — |

[^impl]: CoverRatioCalculator.kt (harbor-backend, `core`, layer `utils`)
