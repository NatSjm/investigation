---
type: Attested Computation
title: Client role classification (importer / exporter / mixed)
description: Classifies a client per product group as IMPORTER, EXPORTER, MIXED or UNDETERMINED from the inbound share of the last 12 full months of actual movements.
tags: [calculation, clients]
status: stable
runtime: kotlin
parameters:
  - { name: inbound, type: Decimal, required: true }
  - { name: outbound, type: Decimal, required: true }
  - { name: minVolume, type: Decimal, required: true }
  - { name: importerThreshold, type: Decimal, required: true }
  - { name: exporterThreshold, type: Decimal, required: true }
executor:
  resource: backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/RoleClassifierTest.kt
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.py
generated: { by: copilot/doc-sync, at: 2026-10-09T08:00:00Z }
verified: { by: human:example-reviewer, at: 2026-10-08T15:00:00Z }
stale_after: 2027-01-06T00:00:00Z
sources:
  - id: impl
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/main/kotlin/com/acme/harbor/utils/RoleClassifier.kt
    title: RoleClassifier.kt
  - id: tests
    resource: https://git.example.com/harbor/harbor-backend/blob/main/harbor-core/src/test/kotlin/com/acme/harbor/utils/RoleClassifierTest.kt
    title: RoleClassifierTest.kt
# --- repo extensions ---
name: client_role_classification
used_by: [CLI-001, STR-001]
code_refs:
  - backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/RoleClassifier.kt
  - backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/RoleClassifierTest.kt
last_verified: 2026-10-08
---

# Client role classification (importer / exporter / mixed)

## Purpose
Determines the **client role** per product group: `IMPORTER`, `EXPORTER`, `MIXED` or `UNDETERMINED`
(`ClientRole` enum in `enums/ClientRole.kt`). Shown on the client overview cards (CLI-001) and used as the
sign of the stress-test exposure (STR-001). A manual **role override** set during a `CLIENT` session supersedes the
result (`client_role.source = MANUAL`); this calculation is the `source = ALGORITHM` path only.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|
| inbound | Decimal | units | `sum(movement_monthly.quantity)` where `direction = IN`, last 12 full months | ≥ 0 |
| outbound | Decimal | units | `sum(movement_monthly.quantity)` where `direction = OUT`, last 12 full months | ≥ 0 |

"Last 12 full months" = the 12 calendar months before the current month, on the shared month grid (`MonthGrid.kt`).

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|
| `role.min_volume` | 100 | per product group |
| `role.importer_threshold` | 0.65 | per product group |
| `role.exporter_threshold` | 0.35 | per product group |

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|
| role | `ClientRole` | — | — |
| share | Decimal | ratio | scale 4, HALF_EVEN (returned for display, not persisted) |

## Formula
$$ total = inbound + outbound \qquad share = \frac{inbound}{total} $$

Step list:
1. `total = inbound + outbound`; if `total < role.min_volume` → `UNDETERMINED` (stop).[^impl]
2. `share = inbound / total`, scale 4, HALF_EVEN.[^impl]
3. `share >= role.importer_threshold` → `IMPORTER`; `share <= role.exporter_threshold` → `EXPORTER`;
   otherwise `MIXED`.[^impl]

# Computation
```kotlin
// mirrors RoleClassifier.kt — pure Kotlin object, no Spring
object RoleClassifier {
    data class Thresholds(val minVolume: BigDecimal, val importer: BigDecimal, val exporter: BigDecimal)

    fun classify(inbound: BigDecimal, outbound: BigDecimal, t: Thresholds): ClientRole {
        val total = inbound + outbound
        if (total < t.minVolume) return ClientRole.UNDETERMINED
        val share = inbound.divide(total, 4, RoundingMode.HALF_EVEN)
        return when {
            share >= t.importer -> ClientRole.IMPORTER
            share <= t.exporter -> ClientRole.EXPORTER
            else -> ClientRole.MIXED
        }
    }
}
```

## Conventions
Month grid: 12 full calendar months before today (UTC) · Rounding: share scale 4, HALF_EVEN, compared **after**
rounding · Price basis: not used (quantities only) · Missing data: a month without rows counts as 0 ·
Both thresholds are inclusive (`>=` / `<=`) · Time zone: UTC.

## Worked examples
Copied from the executor test.[^tests] Thresholds: `min_volume = 100`, `importer = 0.65`, `exporter = 0.35`.

| # | Case | Inputs (inbound, outbound) | share | Expected output |
|---|---|---|---|---|
| 1 | typical importer | 800, 200 | 0.8000 | `IMPORTER` |
| 2 | typical exporter | 300, 700 | 0.3000 | `EXPORTER` |
| 3 | balanced | 500, 500 | 0.5000 | `MIXED` |
| 4 | below minimum volume | 40, 50 | — (total 90 < 100) | `UNDETERMINED` |
| 5 | importer boundary (inclusive) | 65, 35 | 0.6500 | `IMPORTER` |

## Performance notes
One call per client × product group on `getClientOverview` / `getClientRole`; inputs come from two indexed sums
over `movement_monthly`. No caching needed.

[^impl]: RoleClassifier.kt (harbor-backend, `core`, layer `utils`)
[^tests]: RoleClassifierTest.kt (harbor-backend, `core` tests, `utils`)
