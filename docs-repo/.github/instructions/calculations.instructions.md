---
applyTo: "domain/calculations/**/*.md"
description: Rules for calculation concepts (OKF Attested Computation) - formula, parameters, worked examples, code refs.
---

# Calculation concept rules

- `type: Attested Computation`, `runtime: kotlin`, `parameters[]` listed; `executor.resource` is the unit test
  next to the implementation (`backend/core/src/test/kotlin/harbor/utils/<Class>Test.kt`).
- The implementation is authoritative. The doc quotes it: formula in `$$ ... $$` **and** as a step list, the
  sanctioned code shape under `# Computation`, and **worked examples copied from the unit test** - never invented,
  never recomputed by hand. If the test and the doc disagree, the doc gets `status: draft` and an open question.
- State rounding mode and scale (money `HALF_EVEN` scale 2, ratios scale 4), units, the month grid convention
  (`period` = first day of month), and performance notes (`horizon months x scenarios x dimension values`).
$1$2- `## Parameters` names `parameter_set` keys exactly as in `generated/be/parameters.md` (generated catalogue: seeded defaults, readers, validator). `validate-frontmatter.ps1` rejects a key the catalogue lacks and reports a catalogue key no document explains. The calculation owns the **meaning** of a key (unit, bound, formula it feeds); the admin spec `ADM-001` owns scope, versioning and validation.$2- `code_refs` point at `be/core/src/main/kotlin/harbor/utils/<Class>.kt` (file, optional `#Lx-Ly`)
  as resolved through `generated/be/docs-tags.md` (`@docs <name>`).
- Legacy descriptions (Confluence) are evidence, not truth: cite them in `sources[]` and mark any difference
  with `> ⚠️ CONFLICT (legacy: <page>)` until `calc-auditor` resolves it.
