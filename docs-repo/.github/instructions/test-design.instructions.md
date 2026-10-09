---
applyTo: "test-design/**"
description: Rules for Gherkin test design and synthetic fixtures handed to the tests repository.
---

# Test design rules

- `.feature` files use Gherkin; one file per feature ID; `@<FEATURE-ID>` on the Feature, `@BR-<ID>-<n>` and one
  layer tag (`@api @ui @calc @kafka`) on every scenario.
- Prefer `Scenario Outline` + `Examples` for calculation matrices; every example row must be reproducible from
  the worked examples in `domain/calculations/` (same rounding, same scale).
- Fixtures are **synthetic**: fake client names (`Client-SYN-*`), generated identifiers, rounded prices. Name them
  `<FEATURE-ID>-<purpose>.json|csv`, <= 200 lines each.
- Cover: happy path, each business rule boundary, validation errors, permission denial, missing/closed session
  header (`428` / `409`) for `/session/**` endpoints, and for calculations: first/last month of the horizon,
  zero quantities, importer vs exporter sign, MIXED role, rounding.
- Test steps must map to the step vocabulary in `test-design/README.md` so the tests repo can implement them
  without rewriting; add a step there first if a new one is needed.
- Do not write implementation code here; the tests repo owns step definitions.
