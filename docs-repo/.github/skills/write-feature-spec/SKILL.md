---
name: write-feature-spec
description: How to write or update a functional feature spec in this repo (structure, numbering, traceability, what to read first, how to use the graph and the manager). Use when creating or refreshing files under features/.
---

# Write a feature spec

1. `python3 scripts/context-pack.py --task <ID or community>`; read the pack. For a new spec the graph neighbourhood of
   the community is your structure (see `references/source-priority.md`).
2. Copy `features/_template.md` -> `features/<ctx>/<CTX>-<NNN>.md`. Next free number: `search` for `id: <CTX>-`. One spec per screen (the first of a context is its main screen); a modal or sub-capability with rules of its own gets its own number and is cited from the screen spec, never restated (`features/conventions.md`, "Shaping specs").
3. Fill **API / Events / Data / UI flow / Calculations** from the graph and contracts in the pack
   (`operationId`, exact topic and table names); class-level detail from `generated/be/components.md`.
   Frontmatter `api[]` holds only the operations whose handler is in this context; an operation the screen calls
   but another context handles stays in the API / Events table with `owned by <SPEC-ID>` in its Purpose column
   (`features/conventions.md`, "Owned versus called operations"). Stop reading once every template section can be filled.
4. Fill **Summary / Actors / Business rules** from the manager file named on the `context:` node (layer
   `manager/`, `<Ctx>Manager.kt`) - the only source file you open. Rules: `BR-<ID>-<n>: <MUST / MUST NOT statement>`, one testable assertion each,
   ending after the footnote with `(source: code manager#<method>)`, the method whose code or KDoc states the rule
   (a symbol, never a line range; `(source: imported conf-<slug>)` for a rule only an imported page states;
   `features/conventions.md`, "Provenance per rule").
5. Link calculations, never inline formulas; thresholds and defaults are quoted from the calculation concept.
6. Frontmatter: `type: Feature Spec`, one-sentence `description`, `tags`, `status: draft`, `stale_after`,
   `generated: { by: copilot/<agent>, at: <ISO> }`, `sources[]` cited via `[^id]`. `last_verified` only after
   checking against `generated/`; never add `verified.by: human:*` yourself.
7. Add `docs-map.yml` entries for every `code_refs` directory.
8. Run `python3 scripts/validate-frontmatter.py <file>`, `python3 scripts/okf-validate.py --strict`,
   `python3 scripts/build-index.py`; log.

Quality bar: a QA engineer must be able to write tests from the spec alone; an analyst must be able to slice
stories from it alone; a developer must find every code location through `code_refs` / the graph.
