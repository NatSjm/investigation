---
applyTo: "generated/**"
---

# Generated artifacts

These files are produced by CI pipelines in the FE/BE repos (see `ci-examples/`). **Do not edit.**
If something looks wrong, fix the generator or the source code and let CI republish.

Use them as your primary, cheap context:

- `codebase-map.md` — module → responsibility → entry files (start here).
- `graph/REPO_MAP.md`, `graph/<community>.md`, `graph/graph.json` — architectural graph joined from the BE/FE maps
  by `scripts/gen-graph.ps1` (impact, flows, spec coverage). Query with `scripts/graph-query.ps1` or VS Code `#impact`.
- `be/`, `fe/` — lib-free regex maps pushed by the code repos (`api-index`, `events`, `db-schema`, `routes`, `docs-tags`, ...)
  plus optional precise exports `graph-export-be.json` / `graph-export-fe.json`.
- `api-surface/be/*.md` — Kotlin public signatures (Dokka/detekt-derived), no bodies.
- `api-surface/fe/*.d.ts` — exported TS types/props/hooks.
- `openapi/*.yaml` — REST contract (springdoc).
- `asyncapi/*.yaml` — Kafka topics, schemas, producers/consumers.
- `db/schema.md` — tables/columns/FKs + Mermaid ERD (from Liquibase/Flyway state).

OKF: Markdown concepts in this folder (`codebase-map.md`, `artifacts.md`) carry frontmatter with
`generated.by: process:<pipeline-id>`, `generated.at`, and a short `stale_after`; they never carry a human
`verified[]` entry. Non-Markdown artifacts (YAML/JSON/`.d.ts`) are outside the OKF concept set and are not indexed.
