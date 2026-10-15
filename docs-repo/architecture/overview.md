---
type: Document
title: Architecture overview (arc42-lite, C4 context and containers)
description: How architecture documentation is organised plus the C4 context and container diagrams of Harbor (frontend, layered backend core with kafka_client library, PostgreSQL, Kafka, five external services).
tags: [architecture, c4]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
stale_after: 2027-01-07T00:00:00Z
sources:
  - id: codebase-map
    resource: /generated/be/codebase-map.md
    title: Codebase map (CI-generated)
  - id: components
    resource: /generated/be/components.md
    title: Component index (CI-generated)
---

# Architecture

arc42-lite structure. Diagrams are Mermaid (renders in GitHub/GitLab/IDE; no binary files).

| File | Content |
|---|---|
| this page | C4 level 1 (context) and level 2 (containers) |
| `03-components.md` | C4 level 3 per bounded context (generated skeleton from `generated/be/components.md`) |
| `04-runtime.md` | key sequences: start meeting, projection refresh, stress test run, report rendering |
| `05-deployment.md` | environments, topology |
| [integrations.md](/architecture/integrations.md) | REST and Kafka integrations with contract anchors |
| `hld/<ID>.md` | high-level designs per feature/epic (agent `architect`) |
| `adr/` | Architecture Decision Records: [ADR-0001](/architecture/adr/0001-docs-as-code.md), [ADR-0002](/architecture/adr/0002-openapi-first-contracts.md), [ADR-0003](/architecture/adr/0003-grouping-in-kotlin-not-sql.md), [ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md) |

Repositories: `harbor-backend` (Kotlin 1.9 / Spring Boot 3 / Maven `core` + `kafka_client` / PostgreSQL with Flyway / Kafka),
`harbor-frontend` (React 18 / TypeScript / react-router / openapi-fetch), `harbor-docs` (this bundle).
Remotes: `https://git.example.com/harbor/<repo>`.

## C4 level 1 — context

```mermaid
C4Context
  title Harbor — system context
  Person(rep, "Account representative", "Runs client meetings and preparation sessions")
  Person(client, "Client", "Sees overview tables, scenarios and the report during the meeting")
  Person(admin, "Platform admin", "Maintains parameter sets, monitors imports")
  System(harbor, "Harbor", "React frontend + Kotlin/Spring backend + PostgreSQL + Kafka")
  System_Ext(registry, "client-registry", "Client master data (search, profile)")
  System_Ext(market, "market-data", "Baseline price and transport price curves")
  System_Ext(coverp, "cover-provider", "Quotes for the uncovered share")
  System_Ext(docsvc, "document-service", "Renders the meeting report PDF")
  System_Ext(filex, "file-exchange", "Daily XLS movement files")
  Rel(rep, harbor, "Searches clients, starts sessions, models movements and scenarios")
  Rel(client, harbor, "Views during the meeting")
  Rel(admin, harbor, "Edits parameters, triggers imports")
  Rel(harbor, registry, "GET /registry/clients", "REST")
  Rel(harbor, market, "GET /prices, /transport-prices", "REST")
  Rel(market, harbor, "harbor.market.prices-updated", "Kafka")
  Rel(harbor, coverp, "POST /quotes", "REST")
  Rel(harbor, docsvc, "render-requested / rendered", "Kafka + REST")
  Rel(harbor, filex, "GET /files, /files/{id}/content", "REST")
```

## C4 level 2 — containers

The backend is one Spring Boot application, Maven module `core`, organised **by technical layer**
(`core/src/main/kotlin/harbor/<layer>/`). Kafka topic constants, event payloads and the serde live in the library
module `kafka_client`, used by `core`. Bounded contexts of the [context map](/domain/context-map.md) are not folders:
a class belongs to a context by its **name prefix** (`/contexts.yml`, see [ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md)).
Only `core` is deployed; `init_docker_compose/` starts PostgreSQL, Kafka and WireMock stubs of the external services for local runs.

```mermaid
C4Container
  title Harbor — containers
  Person(rep, "Account representative")
  Container(fe, "harbor-frontend", "React 18 / TypeScript", "Routes per feature; openapi-fetch client adds X-Harbor-Session")
  Container_Boundary(be, "harbor-backend (base path /api/v1)") {
    Container(core, "core", "Spring Boot / Kotlin", "Layers api -> manager -> service -> dao / utils / client; event, job, validator, mapper, model; Flyway V1..V9; contracts in resources/openapi and resources/api")
    Container(kc, "kafka_client", "Kotlin library", "Topics constants, event payloads, JsonSerde, HarborKafkaClient")
  }
  Container(local, "init_docker_compose", "docker compose", "Local env only: postgres, kafka, wiremock (5 external services)")
  ContainerDb(pg, "PostgreSQL", "Flyway-managed schema", "client_profile .. parameter_set")
  ContainerQueue(kafka, "Kafka", "5 topics", "harbor.imports.*, harbor.market.*, harbor.meetings.*, harbor.reports.*")
  System_Ext(ext, "External services", "client-registry, market-data, cover-provider, document-service, file-exchange")
  Rel(rep, fe, "Uses", "HTTPS")
  Rel(fe, core, "REST /api/v1 (generated client)", "JSON")
  Rel(core, kc, "uses")
  Rel(core, pg, "JPA / JDBC (dao)")
  Rel(kc, kafka, "produces / consumes (event)")
  Rel(core, ext, "REST (client, generated *Api)")
  Rel(ext, kafka, "prices-updated, rendered")
```

### Layers of `core`

| Layer | Role | Examples |
|---|---|---|
| `api` | REST controllers implementing the generated `*Api` interfaces | `Product1Controller`, `SessionController` |
| `manager` | one per context: orchestration, transaction boundary, KDoc + `@docs <ID>` | `Product1Manager` (P1-001), `MeetingManager` (SES-001) |
| `service` | business services used by managers | `ProjectionService`, `StressTestService` |
| `dao` | repositories (tables per class in `generated/be/components.md`) | `ProjectionDao`, `MeetingSessionDao` |
| `utils` | pure Kotlin calculations (`@docs <calculation>`) | `ProjectionAggregator`, `StressTestCalculator` |
| `event` / `job` | Kafka listeners and publishers / `@Scheduled` jobs | `SessionEventsPublisher`, `DailyMovementImportJob` |
| `client` | wrappers over generated clients of the external services | `ClientRegistryClient`, `MarketDataClient` |
| `validator`, `mapper`, `model`, `component`, `context`, `config`, `advice`, ... | validation, DTO mapping, entities, filters, session context, configuration, error handling | `SessionHeaderFilter`, `SessionContext` |

### Contexts at a glance

| Context (BE prefixes) | Entry point (`@docs`) | Owns tables | Produces / consumes |
|---|---|---|---|
| `clients` (`Client*`) | `ClientManager.kt` (CLI-001) | `client_profile`, `client_role` | consumes `harbor.meetings.session-closed` |
| `meetings` (`Session*`, `Meeting*`) | `MeetingManager.kt` (SES-001) | `meeting_session`, `session_client_config` | produces `harbor.meetings.session-closed` |
| `imports` (`Import*`, `Movement*`, ...) | `ImportManager.kt` (IMP-001) | `import_batch`, `goods_movement`, `movement_monthly` | produces `harbor.imports.movements-loaded` |
| `product1` / `product2` (`Product1*`, `Projection*`, `Peer*` / `Product2*`) | `Product1Manager.kt` (P1-001) / `Product2Manager.kt` (P2-001) | `session_movement_input`, `session_peer_simulation`, `projection_*` | consume `harbor.imports.movements-loaded` |
| `cover` (`Cover*`) | `CoverManager.kt` (COV-001) | `cover_policy`, `cover_quote` | — |
| `market` (`Market*`, `Scenario*`, `BaselinePrice*`) | `MarketManager.kt` (MKT-001) | `market_scenario`, `baseline_price` | consumes `harbor.market.prices-updated` |
| `stress` (`Stress*`) | `StressManager.kt` (STR-001) | `stress_test_result` | — |
| `reports` (`Report*`) | `ReportManager.kt` (RPT-001) | `meeting_report` | consumes `session-closed`, `rendered`; produces `render-requested` |
| `admin` (`Admin*`, `Parameter*`) | `AdminManager.kt` (ADM-001) | `parameter_set` | — |
| `shared` (no prefix) | — | — | config, filters, `utils` helpers (`MonthGrid`, `Rounding`); `kafka_client` |

## Cross-cutting rules
- **OpenAPI-first** ([ADR-0002](/architecture/adr/0002-openapi-first-contracts.md)): `backend/core/src/main/resources/openapi/harbor-api.yaml`
  is the contract; controllers implement generated `*Api` interfaces; the frontend uses the generated client.
- **Session scoping**: selecting a product group on the client overview creates a `meeting_session`; every
  `/session/**` request carries `X-Harbor-Session` (see [SES-001](/features/meetings/SES-001.md)).
- **Grouping in Kotlin, not SQL** ([ADR-0003](/architecture/adr/0003-grouping-in-kotlin-not-sql.md)): the four
  projection tables are aggregated by `utils/ProjectionAggregator.kt` and reused by cover, stress and reports.
- **Calculations** are pure Kotlin in `core/src/main/kotlin/harbor/utils/`, each attested in `domain/calculations/` with
  worked examples copied from its unit test.
- **Layers and prefixes** ([ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md)): `api` -> `manager`
  -> `service` -> `dao` / `utils` / `client`; the class-name prefix decides the context.
