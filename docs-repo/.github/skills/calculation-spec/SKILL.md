---
name: calculation-spec
description: Document a financial calculation (monthly schedules, hedge valuation, stress test) as formula + inputs + worked examples so tests and analysts never need the Kotlin source. Use for files under domain/calculations/.
---

# Calculation spec

1. Copy `domain/calculations/_template.md` → `<snake_case_name>.md`.
2. Locate the function via `generated/codebase-map.md` → `generated/api-surface/be` (signature, parameter
   types). Read the implementation **only** for the formula body and rounding — narrow range.
3. Prefer the BE unit test as source of worked examples: copy its inputs/expected outputs (they are already
   verified). Cite `code_refs` with file:line.
4. Write the formula in LaTeX-style Markdown (`$$ ... $$`) **and** as a plain step list.
5. Worked examples table: ≥ 3 rows — typical, boundary, degenerate (zero/negative). Same rounding as code.
6. State: rounding mode, precision, day-count convention, time zone, currency handling, performance notes
   (e.g. "computed for 360 months × N scenarios").
7. Link back from every feature spec that uses it.

See `references/conventions.md` for day-count and rounding vocabulary.
