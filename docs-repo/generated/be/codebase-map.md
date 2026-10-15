---
type: Document
title: "Codebase map (BE)"
description: "Backend modules, technical layers with their classes and resource folders; read the manager of a context first."
generated:
  by: process:gen-docs
  at: 2026-10-15
status: stable
---
# Codebase map (BE)

> Generated from `pom.xml modules + package-by-layer scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Layered backend: the business context of a class is its **name prefix** (`Product1*`, `Stress*` ...), not its folder.
Read order: the context's `manager/*Manager.kt` (KDoc + `@docs`) -> the service / dao / utils it depends on (components.md) -> one range.

## Modules

| Module | Purpose | Base package | Kotlin files | Layers |
|---|---|---|---|---|
| `core` | The Harbor Spring Boot application: all business code, package-by-layer under src/main/kotlin/harbor/ | `harbor` | 146 | `(root)` `advice` `api` `client` `component` `config` `context` `dao` `databind` `enums` `event` `exception` `job` `manager` `mapper` `model` `service` `utils` `validator` |
| `kafka_client` | Shared Kafka library: topic constants (harbor.kafka.Topics), event payload classes (harbor.kafka.events),     JSON serde and producer/consumer helper. No dependency on core; payloads use wire values (strings, UUIDs, dates). | `harbor.kafka` | 8 | `(root)` `events` |

Other top-level folders (not Maven modules): `init_docker_compose/`

## Layers of `core` (`core/src/main/kotlin/harbor/<layer>`)

| Layer | Role | Files | Classes |
|---|---|---|---|
| `(root)` |  | 1 | `HarborApplication` |
| `advice` | global exception handling (@RestControllerAdvice -> ProblemDetail) | 1 | `GlobalExceptionAdvice` |
| `api` | REST controllers implementing the generated *Api interfaces (one per contract tag) | 9 | `AdminController`, `ClientController`, `CoverController`, `Product1Controller`, `Product2Controller`, `ReportController`, `ScenarioController`, `SessionController`, `StressTestController` |
| `client` | wrappers over generated REST clients of external services (contracts in resources/api) | 5 | `ClientRegistryClient`, `CoverProviderClient`, `DocumentServiceClient`, `FileExchangeClient`, `MarketDataClient` |
| `component` | infrastructure components (filters, parsers, template loaders) | 7 | `ReportTemplateLoader`, `SessionHeaderFilter`, `WorkbookDelimitedReader`, `WorkbookReader`, `WorkbookReaderFactory`, `XlsMovementParser`, `XlsWorkbookOpener` |
| `config` | Spring configuration | 4 | `JacksonConfig`, `KafkaConfig`, `SchedulingConfig`, `WebConfig` |
| `context` | request / session context holders | 3 | `CurrentUser`, `SessionContext`, `SessionScope` |
| `dao` | repositories (Spring Data / JDBC) - tables per class in components.md | 17 | `BaselinePriceDao`, `ClientProfileDao`, `ClientRoleDao`, `CoverPolicyDao`, `CoverQuoteDao`, `GoodsMovementDao`, `ImportBatchDao`, `MarketScenarioDao`, `MeetingReportDao`, `MeetingSessionDao`, `MovementMonthlyDao`, `ParameterDao`, (+5) |
| `databind` | Jackson serializers / deserializers | 2 | `MoneySerializer`, `PeriodDeserializer` |
| `enums` | enumerations | 15 | `ClientRole`, `CoverPreference`, `DimensionKind`, `Direction`, `ImportStatus`, `ParameterKey`, `PriceBasis`, `ProductGroup`, `ReportStatus`, `RoleSource`, `ScenarioKind`, `SessionKind`, (+3) |
| `event` | Kafka listeners and publishers (topics in events.md) | 9 | `ClientRoleSessionClosedListener`, `MarketPricesListener`, `MovementsLoadedPublisher`, `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener`, `ReportRenderedListener`, `ReportRenderRequester`, `ReportSessionClosedListener`, `SessionEventsPublisher` |
| `exception` | exception types | 6 | `MissingParameterException`, `NotFoundException`, `SessionClosedException`, `SessionHeaderMissingException`, `SessionNotBoundException`, `ValidationException` |
| `job` | scheduled jobs (triggers in jobs.md) | 2 | `DailyMovementImportJob`, `MonthlySnapshotJob` |
| `manager` | orchestration per bounded context; transactional boundary; KDoc + @docs - READ FIRST | 10 | `AdminManager`, `ClientManager`, `CoverManager`, `ImportManager`, `MarketManager`, `MeetingManager`, `Product1Manager`, `Product2Manager`, `ReportManager`, `StressManager` |
| `mapper` | entity <-> DTO mappers | 9 | `ClientMapper`, `CoverMapper`, `ImportBatchMapper`, `ParameterMapper`, `ProjectionMapper`, `ReportMapper`, `ScenarioMapper`, `SessionMapper`, `StressMapper` |
| `model` | JPA entities and internal models | 19 | `BaselinePrice`, `ClientOverviewIndicators`, `ClientProfile`, `ClientRoleDecision`, `CoverPolicy`, `CoverQuote`, `GoodsMovement`, `ImportBatch`, `MarketScenario`, `MeetingReport`, `MeetingSession`, `MovementMonthly`, (+7) |
| `service` | business services used by managers | 15 | `BaselinePriceService`, `ClientOverviewService`, `ClientProfileService`, `ClientRoleService`, `CoverQuoteService`, `CoverRatioService`, `MovementImportService`, `ParameterService`, `PeerSimulationService`, `ProjectionInputAssembler`, `ProjectionService`, `ReportPayloadService`, `ScenarioService`, `SessionScopeService`, `StressTestService` |
| `utils` | calculations (pure Kotlin, @docs <calculation>) and helpers | 8 | `CoverRatioCalculator`, `MonthGrid`, `PeerBenchmark`, `ProjectionAggregator`, `RoleClassifier`, `Rounding`, `ScenarioPricePath`, `StressTestCalculator` |
| `validator` | request validation | 4 | `MovementInputValidator`, `ParameterValidator`, `RoleOverrideValidator`, `ScenarioValidator` |

## Resources of `core` (`core/src/main/resources`)

| Folder | Files |
|---|---|
| `api/` | `client-registry.yaml`, `cover-provider.yaml`, `document-service.yaml`, `file-exchange.yaml`, `market-data.yaml` |
| `db/` | `migration/V1__clients.sql`, `migration/V2__meetings.sql`, `migration/V3__movements.sql`, `migration/V4__session_inputs.sql`, `migration/V5__projection.sql`, `migration/V6__cover.sql`, `migration/V7__market_stress.sql`, `migration/V8__reports.sql`, `migration/V9__parameters.sql` |
| `openapi/` | `harbor-api.yaml`, `harbor-events.yaml` |
| `pdf/` | `meeting-report.html`, `report.css` |
| (root) | `application.yml` |

## Layers of `kafka_client` (`kafka_client/src/main/kotlin/harbor/kafka/<layer>`)

| Layer | Role | Files | Classes |
|---|---|---|---|
| `(root)` |  | 3 | `HarborKafkaClient`, `JsonSerde`, `Topics` |
| `events` |  | 5 | `MovementsLoadedEvent`, `PricesUpdatedEvent`, `ReportRendered`, `ReportRenderRequested`, `SessionClosedEvent` |

