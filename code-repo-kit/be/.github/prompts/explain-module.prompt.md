---
agent: code-reader
description: Explain a bounded context (its manager and the manager's dependencies from components.md) from the generated maps, in <= 20 lines.
argument-hint: "context name from contexts.yml, e.g. product1, meetings, stress"
---
Explain context `${input:context:product1}` for a developer who is new to it.

Use only `#file:docs/_generated/codebase-map.md`, `#file:docs/_generated/components.md` (rows whose class name starts with
one of the context's prefixes from `contexts.yml`), the other maps they point to (`api-index.md` filtered by `Tag`,
`events.md`, `jobs.md`) and the context's manager file (e.g. `harbor-core/src/main/kotlin/com/acme/harbor/manager/Product1Manager.kt`).
Cover: responsibility, entry points (operations from `openapi/openapi_harbor.yaml`, topics consumed/produced, scheduled jobs),
the manager's injected dependencies by layer (service, dao/repository, dao/service, client/rest, utils) and the tables they touch,
spec IDs from `@docs` (e.g. `P1-001`) and calculation IDs used (e.g. `monthly_projection`).
Finish with "Open next:" and at most 3 `file:line` suggestions.
