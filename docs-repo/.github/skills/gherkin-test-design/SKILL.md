---
name: gherkin-test-design
description: Write Gherkin test cases and synthetic fixtures from a feature spec using the shared step vocabulary; coverage checklist for calculations, APIs (incl. the session header), UI and Kafka. Use when producing files under test-design/.
---

# Gherkin test design

1. Work from the context pack: the spec's BRs, the **Worked examples** tables of linked calculations, and the
   graph neighbourhood (test scope). Nothing else unless blocked.
2. One `.feature` per feature ID. Tags: `@<ID>` on Feature; `@BR-<ID>-<n>` and one layer tag
   (`@api @ui @calc @kafka`) per scenario; `@needs-review` when the spec or calculation is `draft` / `unverified` / `STALE`.
3. Use only steps from `test-design/README.md`; if a new step is required, add it there first.
4. Calculations -> `Scenario Outline` with `Examples` copied from worked examples (same rounding, same scale).
5. Session-scoped endpoints: one scenario for missing header (`428`), one for a closed session (`409`).
6. Coverage checklist (`references/coverage-checklist.md`) fully ticked in the chat summary.
7. Fixtures: synthetic only; patterns in `test-design/fixtures/README.md`; <= 200 lines each.
8. Add produced paths to the spec frontmatter `tests:`; run `./scripts/coverage-matrix.ps1`.
