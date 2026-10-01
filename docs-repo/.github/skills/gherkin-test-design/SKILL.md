---
name: gherkin-test-design
description: Write Gherkin test cases and synthetic fixtures from a feature spec using the shared step vocabulary; coverage checklist for banking calculations, APIs, UI and Kafka. Use when producing files under test-design/.
---

# Gherkin test design

1. Read the spec's BRs and the **Worked examples** tables of linked calculations. Nothing else unless blocked.
2. One `.feature` per feature ID. Tags: `@<ID>` on Feature; `@BR-<ID>-<n>` and one layer tag
   (`@api @ui @calc @kafka`) per scenario.
3. Use only steps from `test-design/README.md` vocabulary; if a new step is required, add it there first.
4. Calculations → `Scenario Outline` with `Examples` copied from worked examples (same rounding).
5. Coverage checklist (`references/coverage-checklist.md`) must be fully ticked in the chat summary.
6. Fixtures: synthetic only; generate via patterns in `test-design/fixtures/README.md`.
7. Add produced paths to the spec frontmatter `tests:`.
