---
applyTo: "test-design/**"
---

# Test design rules

- `.feature` files use Gherkin; one file per feature ID; `@<FEATURE-ID>` and `@BR-<ID>-<n>` tags on scenarios.
- Prefer `Scenario Outline` + `Examples` for calculation matrices; every example row must be reproducible from
  the worked examples in `domain/calculations/`.
- Fixtures are **synthetic**: fake client names, generated identifiers, rounded market data. Name them
  `<FEATURE-ID>-<purpose>.json|csv`.
- Cover: happy path, each business rule boundary, validation errors, permission denial, and (for calculations)
  month-boundary / leap-year / negative-rate cases.
- Test steps must map to the step vocabulary in `test-design/README.md` so the tests repo can implement them
  without rewriting.
- Do not write implementation code here; the tests repo owns step definitions.
