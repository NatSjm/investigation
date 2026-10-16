# harbor-backend

Backend of **Harbor**, the meeting support application used by account representatives of a goods-trading
company. During a meeting with a client the representative reviews actual and modelled product movements,
looks at the monthly projection, checks how much of the value is covered by policies, defines market
scenarios and runs a stress test. Closing the meeting produces a report (JSON payload + PDF).

Stack: Kotlin 1.9, Spring Boot 3.3, Spring Data JPA + JDBC, Flyway (PostgreSQL), Spring Kafka, Maven.

## Layout

```
pom.xml                  root pom: modules harbor-core, kafka-client; dependency management (Spring Boot 3.3, Kotlin 1.9)
harbor-core/             the Spring Boot application - all business code, one package per technical layer
  src/main/kotlin/com/acme/harbor/HarborBackendApplication.kt
  src/main/kotlin/com/acme/harbor/HarborConstants.kt     application-wide constants (API base path, session header)
  src/main/kotlin/com/acme/harbor/<layer>/...             see the table below
  src/main/resources/api/            contracts of the external services -> generated REST clients
  src/main/resources/openapi/        openapi_harbor.yaml (REST contract), harbor-events.yaml (AsyncAPI, Kafka)
  src/main/resources/db/migration/   Flyway V1__..V9__*.sql
  src/main/resources/pdf/            meeting-report.html + report.css (template sent to document-service)
  src/main/resources/application.yml
  src/test/kotlin/com/acme/harbor/   unit tests (<Class>Test.kt next to the layer: utils/, validator/)
  src/test/resources/datasets/       integration-test fixtures (named datasets)
kafka-client/            event contracts only: src/main/resources/avro/*.avsc (events Harbor publishes), json_<service>/*.json (external
                         events); payload classes generated at build (avro-maven-plugin, jsonschema2pojo), no sources
init_docker_compose/     local environment: PostgreSQL, Kafka, WireMock for the five external services
scripts/docs/            generators of docs/_generated/*.md; the layout they read is scripts/docs/docs-gen.json
```

## Layers (`harbor-core/src/main/kotlin/com/acme/harbor/<layer>` = package `com.acme.harbor.<layer>`)

| Layer | Role | Examples |
|---|---|---|
| `api` | REST controllers implementing the generated `*Api` interfaces (`override fun <operationId>`, no mapping annotations); `HttpHeadersFactory` for downloads | `ClientController`, `Product1Controller`, `ScenarioController` |
| `api/error` | RFC 7807 problem bodies (used by the advice and the filters) | `ProblemDetails` |
| `api/technical` | technical endpoints outside the contract (the only hand-written `@GetMapping`s) | `TechnicalController` (`GET /api/v1/technical/version`) |
| `manager` | orchestration per bounded context, transactional boundary, KDoc with `@docs <spec ID>` - **read this first** | `ClientManager` (CLI-001), `Product1Manager` (P1-001), `StressManager` (STR-001) |
| `service` | business services used by the managers | `ProjectionService`, `ClientRoleService`, `StressTestService` |
| `utils` | calculations (pure Kotlin, KDoc with `@docs <calculation>`) and helpers | `ProjectionAggregator`, `RoleClassifier`, `MonthGrid`, `Rounding` |
| `validator` | business validation (throws `ValidationException` -> 400) | `MovementInputValidator`, `ScenarioValidator` |
| `dao/model` | JPA entities (`@Entity @Table`), one per table | `MeetingSession`, `CoverPolicy`, `Parameter` |
| `dao/repository` | Spring Data / JDBC repositories, one per table group | `MeetingSessionRepository`, `ProjectionRepository` (JDBC) |
| `dao/service` | persistence services over the repositories: lookups, filtered listings; no business rules | `MeetingSessionDaoService` |
| `dao/specification` | JPA specifications combined by the persistence services | `MeetingSessionSpecifications` |
| `dao/mapper` | JDBC row mappers | `ProjectionRowMapper` |
| `dao/converter` | JPA attribute converters (none yet) | - |
| `model` | domain models that are not entities (calculation inputs and results) | `ProjectionRow`, `ScenarioShock`, `ClientOverviewIndicators` |
| `mapper` | domain <-> generated API model mappers | `ProjectionMapper`, `ClientMapper` |
| `event` | Kafka publishers and listeners (topics and payloads from `kafka-client`) | `SessionEventsPublisher`, `ReportSessionClosedListener` |
| `job` | `@Scheduled` jobs | `DailyMovementImportJob`, `MonthlySnapshotJob` |
| `client/rest` | thin `@Component` wrappers over the generated clients of the external services | `MarketDataClient`, `CoverProviderClient` |
| `client/kafka` | the outbound Kafka producer used by the publishers (`producer.send(TOPIC, key, payload)`) | `EventProducer` |
| `component` | infrastructure components | `SessionHeaderFilter`, `XlsMovementParser`, `ReportTemplateLoader` |
| `context` | request / session context | `SessionContext`, `SessionScope`, `CurrentUser` |
| `config` | Spring configuration | `KafkaConfig`, `WebConfig`, `JacksonConfig`, `SchedulingConfig` |
| `advice` | `@RestControllerAdvice` -> RFC 7807 problem details | `GlobalExceptionAdvice` |
| `exception` | exceptions mapped by the advice | `NotFoundException`, `ValidationException`, `SessionClosedException` |
| `enums` | enums shared by all layers | `ProductGroup`, `ClientRole`, `StressDimension` |
| `databind` | Jackson (de)serializers | `MoneySerializer`, `PeriodDeserializer` |

The bounded context of a class is its name prefix (`Client*`, `Session*`/`Meeting*`, `Import*`/`Movement*`,
`Product1*`, `Product2*`, `Projection*`/`Peer*`, `Cover*`, `Market*`/`Scenario*`, `Stress*`, `Report*`,
`Parameter*`/`Admin*`), whatever the layer or sub-package. Technical classes (constants, config, advice, exceptions,
enums, databind, context, `ProblemDetails`, `EventProducer`, `MonthGrid`, `Rounding`) carry no prefix.

## Run locally

```
docker compose -f init_docker_compose/docker-compose.yml up -d    # postgres :5432, kafka :9092, wiremock :8089
mvn -q -DskipTests generate-sources                               # generated interfaces and clients (see below)
mvn -q -pl harbor-core -am spring-boot:run                        # http://localhost:8080/api/v1
```

Point the external services to WireMock with `HARBOR_*_URL=http://localhost:8089` (details and the full list in
`init_docker_compose/README.md`). Flyway creates the schema on start-up.

## Code generation (OpenAPI-first)

`harbor-core/pom.xml` runs openapi-generator during `generate-sources`; the output lands in `harbor-core/target/generated-sources`
and is **not committed**:

- `openapi/openapi_harbor.yaml` -> `kotlin-spring`, `interfaceOnly`: one interface per tag in `com.acme.harbor.api.generated`
  (`ClientsApi`, `MeetingsApi`, `Product1Api`, `Product2Api`, `CoverApi`, `MarketApi`, `StressApi`, `ReportsApi`,
  `AdminApi`) with the request mappings, models in `com.acme.harbor.api.generated.model` with the suffix `Dto` (`ClientDto`, `ProjectionRowDto`; openapi-generator `modelNameSuffix`). The frontend client is generated
  from the same file. Change the contract first, regenerate, then implement the `override fun`.
- `api/<service>.yaml` -> `kotlin` client (`jvm-spring-restclient`) per external service in
  `com.acme.harbor.client.generated.<name>` (`clientregistry`, `marketdata`, `coverprovider`, `documentservice`, `fileexchange`),
  wrapped by the classes in `com.acme.harbor.client.rest`.

Kafka topics and payloads are not generated: they live in `kafka-client` and are described in `openapi/harbor-events.yaml`.

## Session header rule

Selecting a product group on the client overview page creates a meeting session. Every request to a
`/api/v1/session/**` path (`HarborConstants.SESSION_PATH_PREFIX`) must carry `X-Harbor-Session: <sessionId>`;
`component/SessionHeaderFilter` resolves the open session through `dao/service/MeetingSessionDaoService` and binds it
to `SessionContext`. Missing header -> 428, unknown session -> 404, closed session -> 409.
Session-scoped controllers read `SessionContext.current()` and pass the scope to the manager.

## Kafka

| Topic (`TOPIC` constant of the class) | Schema (`kafka-client/src/main/resources`) | Producer | Consumers |
|---|---|---|---|
| `harbor.imports.movements-loaded` | `avro/MovementsLoaded.avsc` | `MovementsLoadedPublisher` | `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener` |
| `harbor.market.prices-updated` | `json_market-data/PricesUpdated.json` | external (market-data) | `MarketPricesListener` |
| `harbor.meetings.session-closed` | `avro/SessionClosed.avsc` | `SessionEventsPublisher` | `ReportSessionClosedListener`, `ClientRoleSessionClosedListener` |
| `harbor.reports.render-requested` | `avro/ReportRenderRequested.avsc` | `ReportRenderRequester` | external (document-service) |
| `harbor.reports.rendered` | `json_document-service/ReportRendered.json` | external (document-service) | `ReportRenderedListener` |

Every listener and publisher declares its topic as `const val TOPIC` in its companion object; listeners read `groupId` and
`autoStartup` from `harbor.kafka.*` properties. Publishers send through `client/kafka/EventProducer` (the only class holding the
`KafkaTemplate`); Harbor's own events travel as Avro JSON (`client/kafka/AvroJsonSerde`), external ones as plain JSON.
The statistical view `db/migration/statistical-views/create_view_client_overview.sql` is applied at start-up by
`component/StatisticalViewsInitializer`; jobs are guarded by ShedLock (`@SchedulerLock`, table `shedlock`, V10).

## Scheduled jobs (`job/`)

- `DailyMovementImportJob` (`0 0 2 * * *`): pulls new XLS files from file-exchange, parses them into
  `goods_movement`, publishes `harbor.imports.movements-loaded`. Manual trigger: `POST /admin/imports/run`.
- `MonthlySnapshotJob` (`0 0 3 1 * *`): rolls the previous month up into `movement_monthly`.

## Tests

`mvn -q test` runs the unit tests in `harbor-core/src/test/kotlin/com/acme/harbor/`: one test per calculation in `utils/`
(the worked examples quoted by the documentation) and the validator rules in `validator/`.

## Generated maps

`python3 scripts/docs/gen-all.py` writes `docs/_generated/*.md` (layers, components, API index, events, schema, jobs,
`@docs` tags, parameters, datasets) and the database documentation `docs/db/` (`schema.json`, `readme.md`, one page per
table under `schema/tables/`, `schema/erd/overview.mmd`) from the migrations and their `COMMENT ON` statements
(`V11__table_comments.sql` holds the comments of the first ten migrations); `--check` is the CI gate. The generators read the layout (modules, base package,
layers and sub-packages, contract paths, annotations) from `scripts/docs/docs-gen.json`; see `scripts/docs/README.md`.
