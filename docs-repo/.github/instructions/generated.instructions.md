---
applyTo: "generated/**"
description: Generated artifacts are read-only inputs published by the code repositories' CI.
---

# Generated artifacts

These files are produced by CI in the code repositories (`code-repo-kit/ci/docs-maps.yml`, `ci-examples/`).
**Do not edit.** If something looks wrong, fix the generator or the source code and let CI republish. A hook in
`.github/hooks/docs-quality.json` blocks edits here.

Use them as your primary, cheap context (each file is a few hundred tokens):

| Path | Content | Produced by |
|---|---|---|
| `graph/REPO_MAP.md`, `graph/<community>.md`, `graph/graph.json` | architectural graph joined from the maps: contexts, endpoints, classes (`depends-on`, `persists-to`), topics, tables, FE features/routes/hooks, spec links, spec coverage | `scripts/gen-graph.ps1` (this repo) |
| `be/codebase-map.md` | BE Maven modules (`core`, `kafka_client`) -> layers -> classes + resource folders | `scripts/docs/gen-codebase-map.ps1` (BE) |
| `be/components.md` | one row per architectural class: layer, stereotype, injected deps, tables, `@docs`, `file:line` | `scripts/docs/gen-codebase-map.ps1` (BE) |
| `be/api-index.md` | every operation of the contract with `operationId`, `Tag` (= context), implementing handler `file:line` | `gen-api-index.ps1` (contract-first) |
| `be/events.md`, `be/db-schema.md`, `be/jobs.md`, `be/docs-tags.md` | Kafka topics, tables from migrations ("Used in:" lists classes), scheduled jobs, `@docs` tags | BE generators |
| `fe/codebase-map.md`, `fe/routes.md`, `fe/types-index.md`, `fe/docs-tags.md` | FE features with API calls, routes, exported types, `@docs` tags | FE generators |
| `openapi/backend.yaml` | the REST contract both FE and BE are generated from | copied from `backend/core/src/main/resources/openapi/harbor-api.yaml` |
| `openapi/external/*.yaml` | contracts between the backend and the external services (client-registry, market-data, cover-provider, document-service, file-exchange) | copied from `backend/core/src/main/resources/api/` |
| `asyncapi/backend.yaml` | Kafka topics and payload schemas | copied from `backend/core/src/main/resources/openapi/harbor-events.yaml` |
| `analytics/coverage-matrix.md` | BR <-> story <-> scenario coverage | `scripts/coverage-matrix.ps1` (this repo) |

Reading rules:
- For "what exists / what fields" use the contract (`components/schemas`), never DTO source files.
- For "where is it implemented" use `api-index.md` / `components.md` / `docs-tags.md` locations, never a repository search.
- The business context of a BE class is its name prefix, mapped in `contexts.yml`; never infer it from the folder (folders are layers).
- Markdown concepts here carry `generated.by: process:<generator>` and `generated.at`; treat anything older than
  the last code change in that area as potentially stale and say so.
- YAML / JSON artifacts are outside the OKF concept set and are not indexed.
