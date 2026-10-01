---
name: write-feature-spec
description: How to write or update a functional feature spec in this repo (structure, numbering, traceability, what to read first). Use when creating/refreshing files under features/.
---

# Write a feature spec

1. Copy `features/_template.md` → `features/<ctx>/<CTX>-<NNN>.md`. Next free number: `search` for `id: <CTX>-`.
2. Gather facts cheaply (see `references/source-priority.md`). Stop reading once every template section can be filled.
3. Write **Business rules** as `BR-<ID>-<n>: <MUST/MUST NOT statement>`; one testable assertion each.
4. Link calculations, never inline formulas.
5. Fill frontmatter fully: OKF `type: Feature Spec`, one-sentence `description`, `tags`, `status: draft`,
   `stale_after`, `generated: { by: copilot/<agent>, at: <ISO> }`, `sources[]` cited via `[^id]` footnotes.
   `last_verified` only after checking against `generated/`; never add `verified[].by: human:*` yourself.
6. Add `docs-map.yml` entries for every `code_refs` directory.
7. Run `scripts/validate-frontmatter.ps1 <file>`, `scripts/okf-validate.ps1 -Strict`, `scripts/build-index.ps1`.

Quality bar: a QA engineer must be able to write tests from the spec alone; an analyst must be able to slice
stories from it alone.
