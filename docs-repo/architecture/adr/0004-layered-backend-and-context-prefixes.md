---
type: Decision
title: "ADR-0004: Layered backend (package-by-layer) with bounded contexts by class-name prefix"
description: harbor-backend keeps all business code in one core module organised by technical layer; the bounded context of a class is its name prefix, mapped in contexts.yml, and the docs pipeline (components.md, graph context nodes, docs-map globs) follows that mapping.
tags: [adr, architecture, backend, docs]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# ADR-0004: Layered backend (package-by-layer) with bounded contexts by class-name prefix

- **Status**: Accepted
- **Date**: 2026-10-09
- **Deciders**: harbor-platform-team
- **Related**: [Architecture overview](/architecture/overview.md), [Context map](/domain/context-map.md),
  [ADR-0002](/architecture/adr/0002-openapi-first-contracts.md), [ADR-0003](/architecture/adr/0003-grouping-in-kotlin-not-sql.md)

## Context
`harbor-backend` is organised like the real application it imitates: a root `pom.xml` with the modules `core`
(Spring Boot application) and `kafka_client` (topic constants, event payloads, serde), plus `init_docker_compose/` for
the local environment. Inside `core/src/main/kotlin/harbor/` the folders are **technical layers** (`api`, `manager`,
`service`, `dao`, `event`, `job`, `utils`, `client`, `validator`, `mapper`, `model`, ...), not business areas. A folder
therefore holds classes of every bounded context, and "open the module of context X" no longer exists as a
navigation step for people, agents or the docs scripts.

## Decision
- Keep **package-by-layer in one `core` module**. Allowed dependency direction: `api` -> `manager` -> `service` ->
  `dao` / `utils` / `client`; `event` and `job` call managers; `utils` is pure Kotlin.
- The **bounded context of a class is its name prefix** (`Product1*`, `Projection*`, `Peer*` -> `product1`;
  `Stress*` -> `stress`; ...). The mapping lives in one file, [`/contexts.yml`](/contexts.yml) (longest prefix wins;
  no match = `shared`), together with the FE feature folder and the spec ID prefix of each context.
- Each context has exactly one `manager/<Ctx>Manager.kt` with KDoc + `@docs <spec ID>`: the entry point for readers
  and the location of the context in the graph.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| One Maven module per context | context visible in the path; module boundaries enforced by the build | not how the codebase is built; restructuring is out of scope |
| Package-by-feature inside `core` | context visible in the path | same as above; mixed conventions during migration |
| Package-by-layer + name prefix (chosen) | matches the code as it is; one small mapping file | context is implicit; needs naming discipline and generated maps |

## Consequences for the docs
+ `contexts.yml` is the single source for context membership; `scripts/gen-graph.py` and `scripts/context-pack.py`
  read it, and `docs-map.yml` uses prefix globs (`be/core/src/main/kotlin/harbor/**/Product1*.kt`).
+ The BE kit generates `components.md` (one row per class: layer, stereotype, injected dependencies, tables, `@docs`,
  `file:line`); `codebase-map.md` lists modules -> layers -> classes; `api-index.md` shows the context in column `Tag`.
+ The graph has `context:<name>` nodes (located at the manager) instead of one node per Maven module, plus `class:` nodes with
  `depends-on` (constructor injection) and `persists-to` (tables) edges; communities = contexts.
− A class with a new, unmapped prefix is reported as `shared` until `contexts.yml` gets a line; reviewers check it.
− Spec `code_refs` point at layer paths (`be/core/src/main/kotlin/harbor/<layer>/<Class>.kt`); renaming a class moves
  it between contexts and must update `contexts.yml` and the affected specs together.
