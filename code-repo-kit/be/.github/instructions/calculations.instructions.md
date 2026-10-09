---
applyTo: "**/harbor/utils/**/*.kt"
description: "Pure Kotlin calculations in harbor/utils: KDoc formula, @docs <calculation_id>, BigDecimal HALF_EVEN, worked examples in the unit test."
---
# Calculation code (`core/src/main/kotlin/harbor/utils/**`)

- Pure Kotlin objects/classes, no Spring, no `*Dao` / `*Service` / `*Client` access; every input is a function argument
  (parameter values such as `tariff.rate` or `role.min_volume` are passed in, never looked up here).
- Every public calculation has KDoc with: formula in one line, units and scale, `@docs <calculation_id>`
  (`monthly_projection`, `cover_ratio`, `scenario_price_path`, `stress_test_monthly`, `client_role_classification`).
- Money and quantities: `BigDecimal`, `RoundingMode.HALF_EVEN`, scale from the spec (`monthly_projection` 2, `cover_ratio` 4).
  Round once at the end of a step, not per intermediate product.
- Monthly series iterate `YearMonth` via `MonthGrid`; cumulative columns are running sums over the horizon in month order.
- The worked examples live in the unit test (`core/src/test/kotlin/harbor/utils/<Class>Test.kt`),
  named `<calculation_id>__<case>`; `harbor-docs/domain/calculations/<calculation_id>.md` quotes them verbatim.
  Changing a formula = change the test, the KDoc and the docs page in the same change and set the page `status: draft`.
- Scenario/stress parameters (shock percentages, horizon, dimension kind) are explicit arguments - no hidden config reads.
- Do not open controllers, DAOs or migrations for calculation questions.
