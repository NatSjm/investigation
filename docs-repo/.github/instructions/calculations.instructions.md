---
applyTo: "domain/calculations/**/*.md"
description: Rules for calculation concepts (OKF Attested Computation) - formula, parameters, worked examples, code refs.
---

# Calculation concept rules

- `type: Attested Computation`, `runtime: kotlin`, `parameters[]` listed; `executor.resource` is the unit test
  next to the implementation (`backend/harbor-core/src/test/kotlin/com/acme/harbor/utils/<Class>Test.kt`).
- The implementation is authoritative. The doc quotes it: formula in `$$ ... $$` **and** as a step list, the
  sanctioned code shape under `# Computation`, and **worked examples copied from the unit test** - never invented,
  never recomputed by hand. If the test and the doc disagree, the doc gets `status: draft` and an open question.
- State rounding mode and scale (money `HALF_EVEN` scale 2, ratios scale 4), units, the month grid convention
  (`period` = first day of month), and performance notes (`horizon months x scenarios x dimension values`).
- `used_by[]` lists every spec ID that links the calculation; keep it in sync with the specs' `calculations[]`.
- `## Parameters` names `parameter_set` keys exactly as in `generated/be/parameters.md` (generated catalogue: seeded defaults, readers, validator). `validate-frontmatter.py` rejects a key the catalogue lacks and reports a catalogue key no document explains. The calculation owns the **meaning** of a key (unit, bound, formula it feeds); the admin spec `ADM-001` owns scope, versioning and validation.
- `code_refs` point at `be/harbor-core/src/main/kotlin/com/acme/harbor/utils/<Class>.kt` and its test: the file only, never a
  line range or `file:line` (lines rot on the next commit and nothing refreshes them; a symbol survives). The place inside
  the file is named by symbol: the test method in the worked-example row, the function or property in an audit row.
  The file itself is resolved through `generated/be/docs-tags.md` (`@docs <name>`).
- **Provenance per step.** Until a person verifies the document, every numbered step of the Formula step list and the
  Conventions paragraph end, after their footnotes, with one source marker: `(source: code <sources-id>#<symbol>)`
  names the `sources[]` entry of the file and the function, property or constant that implements the step (`impl#build`,
  `rounding#divideAsRatio`), never a line; `(source: imported <sources-id>)`, `(source: person human:<id>)` and
  `(source: spec BR-<ID>-<n>)` as in `features/conventions.md`. The marker is what `calc-auditor` checks at Run 3 and the
  owner at Run 4 (open the symbol, not the file) and it stays after verification. `okf-validate.py --strict` warns on a
  draft step or paragraph without one; a calculation tagged `proposed` (no implementation yet) is exempt.
- Imported descriptions (Confluence) are evidence, not truth: cite them in `sources[]` and mark any difference
  with `> ⚠️ CONFLICT (imported: <page>)` until `calc-auditor` resolves it.
