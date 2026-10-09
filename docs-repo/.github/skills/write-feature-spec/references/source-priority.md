# Source priority (cheapest first)

| # | Source | Cost | Gives you |
|---|---|---|---|
| 1 | the context pack (`.context/<task>.md`) | very low | everything below that already exists, budgeted |
| 2 | `features/`, `domain/` | very low | existing rules, terms, formulas, worked examples |
| 3 | `generated/graph/<community>.md` | very low | endpoints, classes, tables, topics, routes, hooks with `file:line` |
| 4 | `generated/openapi/backend.yaml`, `asyncapi/backend.yaml`, `generated/be/db-schema.md` | low | contracts, schemas, topics, tables |
| 5 | `generated/be/components.md` | low | every class of the context: layer, injected deps (validators, mappers, clients), tables, `@docs`, `file:line` |
| 6 | `generated/be/*.md`, `generated/fe/*.md` | low | handlers, jobs, routes, types, `@docs` locations |
| 7 | `confluence-import/` | medium | legacy intent (may be stale - cite, verify, never copy numbers) |
| 8 | BE manager file (`manager/<Ctx>Manager.kt`, named on the `context:` node) | medium | responsibilities, orchestration, rule intent |
| 9 | BE unit test next to a calculator (`core/src/test/kotlin/harbor/utils/<Class>Test.kt`) | medium | edge cases and worked examples |
| 10 | BE controller / service / validator / dao, narrow ranges | high | validation details, error codes |
| 11 | FE page -> hooks -> components | high | UI flow details, client-side validation |

Rules of thumb:
- One `file:line` range of 40-120 lines beats a whole file; never a whole layer.
- Prefer the **test** over the service when you need edge cases.
- If a fact is in `generated/`, cite it from there, not from source.
- Everything from level 7 downwards is cited in `sources[]`; anything you could not source is an open question.
