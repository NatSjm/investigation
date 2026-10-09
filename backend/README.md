# harbor-backend

Backend of **Harbor**, the meeting support application used by account representatives of a goods-trading
company. During a meeting with a client the representative reviews actual and modelled product movements,
looks at the monthly projection, checks how much of the value is covered by policies, defines market
scenarios and runs a stress test. Closing the meeting produces a report (JSON payload + PDF).

Stack: Kotlin 1.9, Spring Boot 3.3, Spring Data JPA + JDBC, Flyway (PostgreSQL), Spring Kafka, Maven.

## Layout

```
pom.xml                  root pom: modules core, kafka_client; dependency management (Spring Boot 3.3, Kotlin 1.9)
core/                    the Spring Boot application - all business code, one package per technical layer
  src/main/kotlin/harbor/HarborApplication.kt
  src/main/kotlin/harbor/<layer>/...
  src/main/resources/api/            contracts of the external services -> generated REST clients
  src/main/resources/openapi/        harbor-api.yaml (REST contract), harbor-events.yaml (AsyncAPI, Kafka)
  src/main/resources/db/migration/   Flyway V1__..V9__*.sql
  src/main/resources/pdf/            meeting-report.html + report.css (template sent to document-service)
  src/main/resources/application.yml
  src/test/kotlin/harbor/utils/      unit tests of the calculations (the worked examples quoted by the docs)
kafka_client/            shared library: harbor.kafka.Topics, harbor.kafka.events.*, JsonSerde, HarborKafkaClient
init_docker_compose/     local environment: PostgreSQL, Kafka, WireMock for the five external services
```

## Layers (`core/src/main/kotlin/harbor/<layer>` = package `harbor.<layer>`)

| Layer | Role | Examples |
|---|---|---|
| `api` | REST controllers implementing the generated `*Api` interfaces (`override fun <operationId>`, no mapping annotations) | `ClientController`, `Product1Controller`, `ScenarioController` |
| `manager` | orchestration per bounded context, transactional boundary, KDoc with `@docs <spec ID>` - **read this first** | `ClientManager` (CLI-001), `Product1Manager` (P1-001), `StressManager` (STR-001) |
| `service` | business services used by the managers | `ProjectionService`, `ClientRoleService`, `StressTestService` |
| `utils` | calculations (pure Kotlin, KDoc with `@docs <calculation>`) and helpers | `ProjectionAggregator`, `RoleClassifier`, `MonthGrid`, `Rounding` |
| `validator` | request validation (throws `ValidationException` -> 400) | `MovementInputValidator`, `ScenarioValidator` |
| `dao` | Spring Data / JDBC repositories, one per table group | `MeetingSessionDao`, `ProjectionDao` |
| `model` | JPA entities (`@Table`) and internal models | `MeetingSession`, `CoverPolicy`, `ProjectionRow` |
| `mapper` | entity / DTO mappers to the generated API models | `ProjectionMapper`, `ClientMapper` |
| `event` | Kafka publishers and listeners (topics and payloads from `kafka_client`) | `SessionEventsPublisher`, `ReportSessionClosedListener` |
| `job` | `@Scheduled` jobs | `DailyMovementImportJob`, `MonthlySnapshotJob` |
| `client` | thin `@Component` wrappers over the generated clients of the external services | `MarketDataClient`, `CoverProviderClient` |
| `component` | infrastructure components | `SessionHeaderFilter`, `XlsMovementParser`, `ReportTemplateLoader` |
| `context` | request / session context | `SessionContext`, `SessionScope`, `CurrentUser` |
| `config` | Spring configuration | `KafkaConfig`, `WebConfig`, `JacksonConfig`, `SchedulingConfig` |
| `advice` | `@RestControllerAdvice` -> RFC 7807 problem details | `GlobalExceptionAdvice` |
| `exception` | exceptions mapped by the advice | `NotFoundException`, `ValidationException`, `SessionClosedException` |
| `enums` | enums shared by all layers | `ProductGroup`, `ClientRole`, `StressDimension` |
| `databind` | Jackson (de)serializers | `MoneySerializer`, `PeriodDeserializer` |

The bounded context of a class is its name prefix (`Client*`, `Session*`/`Meeting*`, `Import*`/`Movement*`,
`Product1*`, `Product2*`, `Projection*`/`Peer*`, `Cover*`, `Market*`/`Scenario*`, `Stress*`, `Report*`,
`Parameter*`/`Admin*`). Technical classes (config, advice, exceptions, enums, databind, context, `MonthGrid`,
`Rounding`) carry no prefix.

## Run locally

```
docker compose -f init_docker_compose/docker-compose.yml up -d    # postgres :5432, kafka :9092, wiremock :8089
mvn -q -DskipTests generate-sources                               # generated interfaces and clients (see below)
mvn -q -pl core -am spring-boot:run                               # http://localhost:8080/api/v1
```

Point the external services to WireMock with `HARBOR_*_URL=http://localhost:8089` (details and the full list in
`init_docker_compose/README.md`). Flyway creates the schema on start-up.

## Code generation (OpenAPI-first)

`core/pom.xml` runs openapi-generator during `generate-sources`; the output lands in `core/target/generated-sources`
and is **not committed**:

- `openapi/harbor-api.yaml` -> `kotlin-spring`, `interfaceOnly`: one interface per tag in `harbor.api.generated`
  (`ClientsApi`, `MeetingsApi`, `Product1Api`, `Product2Api`, `CoverApi`, `MarketApi`, `StressApi`, `ReportsApi`,
  `AdminApi`) with the request mappings, models in `harbor.api.generated.model`. The frontend client is generated
  from the same file. Change the contract first, regenerate, then implement the `override fun`.
- `api/<service>.yaml` -> `kotlin` client (`jvm-spring-restclient`) per external service in
  `harbor.client.generated.<name>` (`clientregistry`, `marketdata`, `coverprovider`, `documentservice`, `fileexchange`),
  wrapped by the classes in `harbor.client`.

Kafka topics and payloads are not generated: they live in `kafka_client` and are described in `openapi/harbor-events.yaml`.

## Session header rule

Selecting a product group on the client overview page creates a meeting session. Every request to a
`/api/v1/session/**` path must carry `X-Harbor-Session: <sessionId>`; `component/SessionHeaderFilter` resolves the
open session and binds it to `SessionContext`. Missing header -> 428, unknown session -> 404, closed session -> 409.
Session-scoped controllers read `SessionContext.current()` and pass the scope to the manager.

## Kafka

| Topic (`harbor.kafka.Topics`) | Producer | Consumers |
|---|---|---|
| `MOVEMENTS_LOADED` | `MovementsLoadedPublisher` | `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener` |
| `PRICES_UPDATED` | external (market-data) | `MarketPricesListener` |
| `SESSION_CLOSED` | `SessionEventsPublisher` | `ReportSessionClosedListener`, `ClientRoleSessionClosedListener` |
| `REPORT_RENDER_REQUESTED` | `ReportRenderRequester` | external (document-service) |
| `REPORT_RENDERED` | external (document-service) | `ReportRenderedListener` |

## Scheduled jobs (`job/`)

- `DailyMovementImportJob` (`0 0 2 * * *`): pulls new XLS files from file-exchange, parses them into
  `goods_movement`, publishes `harbor.imports.movements-loaded`. Manual trigger: `POST /admin/imports/run`.
- `MonthlySnapshotJob` (`0 0 3 1 * *`): rolls the previous month up into `movement_monthly`.

## Tests

`mvn -q test` runs the unit tests in `core/src/test/kotlin/harbor/`: one test per calculation in `utils/`
(the worked examples quoted by the documentation) and the validator rules in `validator/`.
