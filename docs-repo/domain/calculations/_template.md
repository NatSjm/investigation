---
type: Attested Computation      # OKF §10
title: <Human title>
description: <One sentence: what business quantity it produces.>
tags: [calculation, <context>]
status: draft
runtime: kotlin                 # required for this type
parameters:                     # the only things an agent may bind — never re-derive the formula
  - { name: <param>, type: <Decimal|Int|LocalDate|Enum>, required: true }
executor:
  resource: backend/core/src/test/kotlin/harbor/utils/<X>Test.kt   # unit test running the sanctioned computation
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.ps1          # compares worked-examples table with test output (stub)
generated: { by: copilot/doc-sync, at: 2026-01-01T00:00:00Z }
# verified: { by: human:<reviewer>, at: <ISO> }
# stale_after: <ISO>
sources:
  - id: impl
    resource: <code URL#Lx-Ly>
    title: <X>.kt
# --- repo extensions ---
name: <snake_case_name>
used_by: [CTX-000]
code_refs:
  - backend/core/src/main/kotlin/harbor/utils/<X>.kt#L10-L80
  - backend/core/src/test/kotlin/harbor/utils/<X>Test.kt        # source of worked examples
last_verified: null
---

# <Human title>

## Purpose
What business quantity it produces and on which page / table it is shown.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|

## Parameters
| Key (`parameter_set.key`) | Default | Scope |
|---|---|---|

## Outputs
| Name | Type | Unit | Precision / rounding |
|---|---|---|---|

## Formula
$$ … $$

Step list:
1. …
2. …

# Computation
```kotlin
// Sanctioned implementation, copied verbatim (narrow range) from code_refs; agents bind parameters only.
```

## Conventions
Month grid: · Rounding: · Price basis: · Missing data: · Time zone:

## Worked examples
| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | typical | | |
| 2 | boundary | | |
| 3 | degenerate | | |

## Performance notes
e.g. computed for `months × scenarios × dimension values`; caching; batch size.

## Change log
| Date | Change | Ref |
|---|---|---|
