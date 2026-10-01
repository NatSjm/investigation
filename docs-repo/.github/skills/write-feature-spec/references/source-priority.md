# Source priority (cheapest first)

| # | Source | Cost | Gives you |
|---|---|---|---|
| 1 | `features/`, `domain/` | very low | existing rules, terms, formulas |
| 2 | `generated/codebase-map.md` | very low | which module/file owns the behaviour |
| 3 | `generated/openapi`, `asyncapi`, `db/schema.md` | low | contracts, topics, tables |
| 4 | `generated/api-surface/**` | low | public signatures, DTO fields, enums |
| 5 | `confluence-import/` | medium | legacy intent (may be stale) |
| 6 | BE source: controller → service → domain, narrow ranges | high | actual business rules |
| 7 | FE source: page → hooks → components | high | validation, UI flow |
| 8 | Tests in FE/BE repos | high | edge cases already covered |

Rules of thumb:
- One `view` of a 60–120 line range beats a whole file.
- Prefer reading the **test** for a service over the service itself when you need edge cases.
- If a fact is in `generated/`, cite it from there, not from source.
