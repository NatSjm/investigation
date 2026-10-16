---
type: Document
title: "Codebase map (BE)"
description: "Backend modules, technical layers with their classes and resource folders; read the manager of a context first."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Codebase map (BE)

> Generated from `pom.xml modules + package-by-layer scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Layered backend: the business context of a class is its **name prefix** (`Product1*`, `Stress*` ...), not its folder.
Read order: the context's `manager/*` class (KDoc + `@docs`) -> the classes it depends on (components.md) -> one range.

## Modules

| Module | Purpose | Base package | Kotlin files | Layers |
|---|---|---|---|---|
| `harbor-core` | The Harbor Spring Boot application: all business code, package-by-layer under src/main/kotlin/com/acme/harbor/ | `com.acme.harbor` | 154 | `(root)` `advice` `api` `api/error` `api/technical` `client/kafka` `client/rest` `component` `config` `context` `dao/mapper` `dao/model` `dao/repository` `dao/service` `dao/specification` `databind` `enums` `event` `exception` `job` `manager` `mapper` `model` `service` `utils` `validator` |
| `kafka-client` | Shared Kafka library: topic constants (com.acme.harbor.kafka.Topics), event payload classes (com.acme.harbor.kafka.events), JSON serde and producer/consumer helper. No dependency on core; payloads use wire values (strings, UUIDs, dates). | `com.acme.harbor` | 8 | `kafka` |

Other top-level folders (not build modules): `init_docker_compose/`

## Layers of `harbor-core` (`harbor-core/src/main/kotlin/com/acme/harbor/<layer>`)

| Layer | Role | Files | Classes |
|---|---|---|---|
| `(root)` |  | 2 | `HarborBackendApplication`, `HarborConstants` |
| `advice` | global exception handling (@RestControllerAdvice -> ProblemDetail) | 1 | `GlobalExceptionAdvice` |
| `api` | REST controllers implementing the generated *Api interfaces (one per contract tag) | 10 | `AdminController`, `ClientController`, `CoverController`, `HttpHeadersFactory`, `Product1Controller`, `Product2Controller`, `ReportController`, `ScenarioController`, `SessionController`, `StressTestController` |
| `api/error` | problem body factory (RFC 7807) and error models | 1 | `ProblemDetails` |
| `api/technical` | technical endpoints outside the contract (version, operations) | 1 | `TechnicalController` |
| `client/kafka` | outbound Kafka producer used by the publishers in event/ | 1 | `EventProducer` |
| `client/rest` | wrappers over generated REST clients of external services (contracts in resources/api) | 5 | `ClientRegistryClient`, `CoverProviderClient`, `DocumentServiceClient`, `FileExchangeClient`, `MarketDataClient` |
| `component` | infrastructure components (filters, parsers, template loaders) | 7 | `ReportTemplateLoader`, `SessionHeaderFilter`, `WorkbookDelimitedReader`, `WorkbookReader`, `WorkbookReaderFactory`, `XlsMovementParser`, `XlsWorkbookOpener` |
| `config` | Spring configuration | 4 | `JacksonConfig`, `KafkaConfig`, `SchedulingConfig`, `WebConfig` |
| `context` | request / session context holders | 3 | `CurrentUser`, `SessionContext`, `SessionScope` |
| `dao/mapper` | row and entity mappers of the persistence layer | 1 | `ProjectionRowMapper` |
| `dao/model` | JPA entities (one per table) | 16 | `BaselinePrice`, `ClientProfile`, `ClientRoleDecision`, `CoverPolicy`, `CoverQuote`, `GoodsMovement`, `ImportBatch`, `MarketScenario`, `MeetingReport`, `MeetingSession`, `MovementMonthly`, `Parameter`, (+4) |
| `dao/repository` | Spring Data / JDBC repositories - tables per class in components.md | 17 | `BaselinePriceRepository`, `ClientProfileRepository`, `ClientRoleRepository`, `CoverPolicyRepository`, `CoverQuoteRepository`, `GoodsMovementRepository`, `ImportBatchRepository`, `MarketScenarioRepository`, `MeetingReportRepository`, `MeetingSessionRepository`, `MovementMonthlyRepository`, `ParameterRepository`, (+5) |
| `dao/service` | persistence services over the repositories (lookups, filtered listings); no business rules | 1 | `MeetingSessionDaoService` |
| `dao/specification` | JPA specifications (dynamic filters) | 1 | `MeetingSessionSpecifications` |
| `databind` | Jackson serializers / deserializers | 2 | `MoneySerializer`, `PeriodDeserializer` |
| `enums` | enumerations | 15 | `ClientRole`, `CoverPreference`, `DimensionKind`, `Direction`, `ImportStatus`, `ParameterKey`, `PriceBasis`, `ProductGroup`, `ReportStatus`, `RoleSource`, `ScenarioKind`, `SessionKind`, (+3) |
| `event` | Kafka listeners and publishers (topics in events.md) | 9 | `ClientRoleSessionClosedListener`, `MarketPricesListener`, `MovementsLoadedPublisher`, `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener`, `ReportRenderedListener`, `ReportRenderRequester`, `ReportSessionClosedListener`, `SessionEventsPublisher` |
| `exception` | exception types | 6 | `MissingParameterException`, `NotFoundException`, `SessionClosedException`, `SessionHeaderMissingException`, `SessionNotBoundException`, `ValidationException` |
| `job` | scheduled jobs (triggers in jobs.md) | 2 | `DailyMovementImportJob`, `MonthlySnapshotJob` |
| `manager` | orchestration per bounded context; transactional boundary; KDoc + @docs - READ FIRST | 10 | `AdminManager`, `ClientManager`, `CoverManager`, `ImportManager`, `MarketManager`, `MeetingManager`, `Product1Manager`, `Product2Manager`, `ReportManager`, `StressManager` |
| `mapper` | domain <-> API model mappers | 9 | `ClientMapper`, `CoverMapper`, `ImportBatchMapper`, `ParameterMapper`, `ProjectionMapper`, `ReportMapper`, `ScenarioMapper`, `SessionMapper`, `StressMapper` |
| `model` | domain models that are not entities (calculation inputs and results) | 3 | `ClientOverviewIndicators`, `ProjectionRow`, `ScenarioShock` |
| `service` | business services used by managers | 15 | `BaselinePriceService`, `ClientOverviewService`, `ClientProfileService`, `ClientRoleService`, `CoverQuoteService`, `CoverRatioService`, `MovementImportService`, `ParameterService`, `PeerSimulationService`, `ProjectionInputAssembler`, `ProjectionService`, `ReportPayloadService`, `ScenarioService`, `SessionScopeService`, `StressTestService` |
| `utils` | calculations (pure Kotlin, @docs <calculation>) and helpers | 8 | `CoverRatioCalculator`, `MonthGrid`, `PeerBenchmark`, `ProjectionAggregator`, `RoleClassifier`, `Rounding`, `ScenarioPricePath`, `StressTestCalculator` |
| `validator` | business validation of requests and inputs | 4 | `MovementInputValidator`, `ParameterValidator`, `RoleOverrideValidator`, `ScenarioValidator` |

## Resources of `harbor-core` (`harbor-core/src/main/resources`)

| Folder | Files |
|---|---|
| `api/` | `client-registry.yaml`, `cover-provider.yaml`, `document-service.yaml`, `file-exchange.yaml`, `market-data.yaml` |
| `db/` | `migration/V1__clients.sql`, `migration/V2__meetings.sql`, `migration/V3__movements.sql`, `migration/V4__session_inputs.sql`, `migration/V5__projection.sql`, `migration/V6__cover.sql`, `migration/V7__market_stress.sql`, `migration/V8__reports.sql`, `migration/V9__parameters.sql` |
| `openapi/` | `harbor-api.yaml`, `harbor-events.yaml` |
| `pdf/` | `meeting-report.html`, `report.css` |
| (root) | `application.yml` |

