---
name: calculation-spec
description: Document a business computation (monthly projection, cover ratio, scenario price path, stress test, role classification) as formula + parameters + worked examples copied from the unit test, so tests and analysts never need the Kotlin source. Use for files under domain/calculations/.
---

# Calculation spec (OKF Attested Computation)

1. Copy `domain/calculations/_template.md` -> `<snake_case_name>.md` (the `@docs` tag in code is this name).
2. Locate the implementation through `generated/be/docs-tags.md` (`@docs <name>` -> class `file:line`, layer `utils/`:
   `be/core/src/main/kotlin/harbor/utils/<Class>.kt`, test `be/core/src/test/kotlin/harbor/utils/<Class>Test.kt`); read the
   class **only** for the formula body, parameters and rounding - and its unit test for the worked examples.
3. Worked examples are **copied** from the test (inputs, expected outputs, test method name). Never invent or
   hand-compute rows; if the test lacks a case you need, write an open question "add test case for ...".
4. Write the formula in LaTeX-style Markdown (`$$ ... $$`) **and** as a plain step list; put the sanctioned code
   shape (signature + core expression, not the whole class) under `# Computation`.
5. Worked examples table: >= 3 rows - typical, boundary, degenerate (zero / empty / MIXED role).
6. State: rounding mode and scale, units and price basis, month-grid convention, parameter keys (`parameter_set`)
   with defaults, performance notes (`horizon months x scenarios x dimension values`).
7. Frontmatter: `runtime: kotlin`, `parameters[]`, `executor.resource` = the test file, `used_by[]`, `code_refs`.
8. Link back from every feature spec that uses it (`calculations[]`).

See `references/conventions.md` for the vocabulary (rounding, month grid, sign conventions, scenarios).
