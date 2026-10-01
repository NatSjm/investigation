---
applyTo: "**/calc/**/*.kt"
---
# Calculation code

- Every public calculation function has KDoc with: formula in one line, units/scale, `@docs <calculation-id>`.
- The matching spec is `advisory-docs/domain/calculations/<calculation-id>.md` (OKF `Attested Computation`).
  If the formula changes, change the spec in the same PR and bump its `status` to `draft`.
- Worked examples in the spec must be copied from (or into) the unit test next to the code - one source of truth.
- Monthly series: iterate `YearMonth`, day-count via a named function, never inline `/360`.
- Stress tests: parameters (`shiftBp`, curve name) are explicit arguments - no hidden config reads.
- Do not open `persistence/` or controllers for calculation questions; inputs are in the function signature.
