---
applyTo: "**/src/test/**"
---
# Tests

- Unit tests next to calculations are the canonical worked examples; name them `<calcId>__<case>` so the docs repo can reference them.
- Fixtures: synthetic clients only (`CLIENT-TEST-*`), notional values in round thousands, no real rates or names.
- Keep fixtures small (< 100 lines JSON); for larger scenarios build data in code with a builder.
- When fixing a bug, add the failing case to the test first and mention the spec ID in the test name or KDoc.
