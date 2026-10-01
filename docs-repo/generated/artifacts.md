---
type: Document
title: Generated artifacts — how they are produced
description: What CI publishes into generated/ from the FE/BE repos (OpenAPI, AsyncAPI, DB schema, API surface, codebase map), which generator makes each, and how agents should use them.
tags: [generated, conventions]
status: stable
generated: { by: human:platform-team, at: 2026-09-30T19:00:00Z }
---

# Generated artifacts — DO NOT EDIT

Published by CI in the FE/BE repositories (see `../ci-examples/`). Each publish opens a PR here so the
`doc-sync` agent (or a human) can update affected specs. Every generated Markdown concept carries
`generated: { by: process:<be|fe>-ci, at }` and `stale_after` = +30 days, so staleness is visible in `index.md`.

| Path | Generator (in source repo) | Purpose for agents |
|---|---|---|
| `codebase-map.md` | `scripts/gen-codebase-map` (module list + `@Responsibility` KDoc/JSDoc tags + entry files) | navigation without directory listings |
| `api-surface/be/*.md` | Dokka (Markdown) with `-Xno-source-bodies` / custom detekt rule dump: public classes, functions, DTO fields, enums | understand contracts w/o implementation |
| `api-surface/fe/*.d.ts` | `tsc --declaration --emitDeclarationOnly` on `src/features/**/index.ts` | component props, hooks, types |
| `openapi/be.yaml` | springdoc-openapi at build time (`/v3/api-docs.yaml`) | REST contract |
| `asyncapi/be.yaml` | springwolf (Spring Kafka → AsyncAPI) | topics, schemas, producers/consumers |
| `db/schema.md` | Liquibase/Flyway applied to an empty DB → SchemaSpy / `pg_dump --schema-only` → Markdown + Mermaid `erDiagram` | data model |
| `fe/routes.md` | React Router config dump | screen inventory |
| `metrics.json` | LOC per module, last commit per module | freshness checks |

Token budget guideline: whole `generated/` should stay < ~150k tokens; agents read only the files they need.
