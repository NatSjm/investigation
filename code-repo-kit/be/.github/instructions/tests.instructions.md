---
applyTo: "**/src/test/**"
description: "Unit and integration tests: worked-example naming, synthetic fixtures, small JSON, spec IDs in test names."
---
# Tests

- Unit tests of calculations (`core/src/test/kotlin/harbor/utils/<Class>Test.kt`) are the canonical worked examples; name them `<calculation_id>__<case>`
  (e.g. `monthly_projection__importer_two_cities`) so `harbor-docs/domain/calculations/*.md` can quote them.
- Fixtures: synthetic clients only (`CLIENT-TEST-*`), quantities and prices in round numbers, corridor codes from the
  domain (`VLD`, `NRL`, `CST`, `MRD`), no real company names or prices.
- Keep JSON/CSV fixtures under 100 lines; for larger scenarios build data in code with a builder.
- Controller tests go through the generated `*Api` interface contract (`MockMvc` against the OpenAPI paths) and send
  `X-Harbor-Session` for `/session/**` operations.
- Manager/service tests mock the injected dependencies listed in `components.md`. When fixing a bug, add the failing case first and mention the spec ID (`P1-001`, `STR-001`, ...) in the test name or KDoc.
- `GraphExportTest` (profile `graph-export`) runs only with `-Ddocs.graph=true`; never make it part of the default test loop.
