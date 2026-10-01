---
type: Attested Computation      # OKF §10
title: <Human title>
description: <One sentence: what business quantity it produces.>
tags: [calculation, <context>]
status: draft
runtime: kotlin                 # required for this type
parameters:                     # the only things an agent may bind — never re-derive the formula
  - { name: <param>, type: <Decimal|Int|LocalDate>, required: true }
executor:
  resource: <be/src/test/kotlin/.../XxxTest.kt>     # the BE unit test that runs the sanctioned computation
  receipt: [test_class, inputs, expected, actual]
attester:
  resource: /scripts/attest-calculation.ps1          # compares worked-examples table with test output (stub)
generated: { by: copilot/doc-sync, at: 2026-01-01T00:00:00Z }
# verified: { by: human:<quant-or-analyst>, at: <ISO> }
# stale_after: <ISO>
sources:
  - id: impl
    resource: <code URL#Lx-Ly>
    title: <Calculator.kt>
# --- repo extensions ---
name: <snake_case_name>
used_by: [CTX-000]
code_refs:
  - be/src/main/kotlin/...#L10-L80
  - be/src/test/kotlin/...        # source of worked examples
last_verified: null
---

# <Human title>

## Purpose
What business quantity it produces and where it is shown.

## Inputs
| Name | Type | Unit | Source | Constraints |
|---|---|---|---|---|

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
Day-count: · Rounding: · Calendar: · Negative rates: · Time zone:

## Worked examples
| # | Case | Inputs | Expected output |
|---|---|---|---|
| 1 | typical | | |
| 2 | boundary | | |
| 3 | degenerate | | |

## Performance notes
e.g. computed for `months × scenarios`; caching; batch size.

## Change log
| Date | Change | Ref |
|---|---|---|
