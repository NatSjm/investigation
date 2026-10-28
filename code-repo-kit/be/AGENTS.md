# AGENTS.md - harbor-backend (Kotlin 1.9 / Spring Boot 3 / Maven: harbor-core + kafka-client / PostgreSQL + Flyway / Kafka)

Read by Copilot Chat (VS Code, JetBrains), Copilot CLI, the Copilot coding agent and other agent tools.
Copilot-specific extras are in `.github/copilot-instructions.md`; path-scoped rules in `.github/instructions/`.

## What this repository is
Backend of the Harbor platform: account representatives review a client's product movements in a **meeting
session**, model movements and peer simulations, compute monthly projections, cover ratios, market scenarios
and stress tests, and close the meeting with a PDF report.
Layout is **package-by-layer**: the root `pom.xml` has two modules - `harbor-core` (the Spring Boot application with
all business code in `harbor-core/src/main/kotlin/com/acme/harbor/<layer>/`: `api` (+ `api/error`, `api/technical`),
`manager`, `service`, `dao` (`dao/model` entities, `dao/repository`, `dao/service`, `dao/mapper`, `dao/specification`,
`dao/converter`), `event`, `job`, `utils`, `client` (`client/rest`, `client/kafka`), `validator`, `mapper`, `model`, ...)
and `kafka-client` (event schemas: Avro and JSON Schema, payload classes generated at build, no sources). The layer list with roles is `scripts/docs/docs-gen.json`.
The bounded context of a class is its **name prefix** (`Product1*`, `Projection*`, `Stress*`, ...; mapping in the docs
repo `contexts.yml`): contexts `clients`, `meetings`, `imports`, `product1`, `product2`, `cover`, `market`, `stress`,
`reports`, `admin`. `init_docker_compose/` starts the local environment (PostgreSQL, Kafka, WireMock stubs of the external services).

## Read in this order (cheapest first) - never walk directories
1. `docs/_generated/index.md`, then `codebase-map.md` (modules -> layers -> classes, resource folders) or the one map
   that answers the question: `api-index.md` (endpoints, `Tag` = context), `events.md` (topics, payload fields), `db-schema.md` (tables),
   `jobs.md` (scheduled jobs), `docs-tags.md` (spec ID -> code), `parameters.md` (admin parameter catalogue: key, seeded defaults per scope, readers, validator), `datasets.md` (named synthetic datasets: seeds and test fixtures with tables, row counts, sample rows).
2. The context's manager `harbor-core/src/main/kotlin/com/acme/harbor/manager/<Ctx>Manager.kt` (KDoc + `@docs <ID>`).
3. Its dependencies from `components.md` (one row per class: layer, injected deps, tables, `@docs`, `file:line`).
4. One file + line range named in a map. Max 3 source files per question.
5. For "what breaks if" questions use the docs repo `generated/graph/<context>.md` instead of the maps.

## Contracts (source of truth)
- `harbor-core/src/main/resources/openapi/openapi_harbor.yaml` is the REST contract. The `*Api` server interfaces are **generated**
  from it into `target/generated-sources` at build time; the frontend client is generated from the same file.
  Never edit generated code. Change the contract first, regenerate (`mvn -q -pl harbor-core -am -DskipTests generate-sources`), then implement.
  The only hand-written request mappings are the technical endpoints in `api/technical/` (listed as `(no contract)` in `api-index.md`).
- `harbor-core/src/main/resources/openapi/harbor-events.yaml` (AsyncAPI) describes the Kafka topics;
  `harbor-core/src/main/resources/api/*.yaml` are the external service contracts (generated clients wrapped in `client/rest/`).
- Every `/session/**` operation requires the header `X-Harbor-Session: <sessionId>` (defined once as
  `components/parameters/SessionHeader`, constant `HarborConstants.SESSION_HEADER`); `component/SessionHeaderFilter`
  resolves it into `context/SessionContext`. Never read the header in controllers or managers.

## Conventions the generators rely on
- Context entry point = `manager/<Ctx>Manager.kt` with a KDoc block that ends with `@docs <ID>` directly above
  `@Service class` (e.g. `Product1Manager.kt` -> `@docs P1-001`).
- Business-prefix naming: every class starts with its context prefix from `contexts.yml` (`Product1Controller`,
  `ProjectionService`, `ProjectionRepository`, `MeetingSessionDaoService`); classes without a known prefix are reported as `shared`.
- Controllers in `api/`: `@RestController class XxxController(...) : XxxApi` implementing `override fun <operationId>(...)`
  **without** `@*Mapping` annotations (they live on the generated interface; parameter annotations such as `@Valid`, `@RequestBody`, `@RequestHeader` are
  inherited). Generated models end in `Dto` (`ClientDto`). `api-index.md` joins openapi_harbor.yaml to these overrides.
  Problem bodies come from `api/error/ProblemDetails`, download headers from `api/HttpHeadersFactory`.
- Kafka: topic names only via the `TOPIC` constant of the listener or publisher class (companion object `const val TOPIC` of that class in `event/`; payload schemas in `kafka-client/src/main/resources/avro` and
  `json_<service>`, classes generated at build);
  listeners and publishers in `event/`: `@KafkaListener(topics = [TOPIC], groupId = "${harbor.kafka.groups.<context>}", autoStartup = "${harbor.kafka.listeners.auto-startup:true}")`,
  producers `producer.send(TOPIC, key, payload)` through `client/kafka/EventProducer`. Literals break `events.md`.
- Scheduled work: `@Scheduled(cron = "...")` + `@SchedulerLock(name = "...")` (ShedLock, table `shedlock`) methods in `job/` with a one-line KDoc -> `jobs.md`.
- Admin parameters: one constant per key in `enums/ParameterKey.kt`, seeds as `INSERT INTO parameter_set` in the migrations, reads only through `ParameterService` -> `parameters.md`. The meaning of a key is documented in the docs repo (calculation `## Parameters`), not in code.
- Datasets: every seed in `scripts/db/seed/*.sql` and every fixture in `harbor-core/src/test/resources/datasets/*.sql` starts with the header `-- dataset: <name>` / `-- purpose:` / `-- synthetic: yes` (`scripts/db/seed/README.md`) -> `datasets.md`; analysts cite them by name.
- Persistence: entities in `dao/model/` (`@Entity @Table(name = "...")`), repositories in `dao/repository/` (`*Repository`,
  Spring Data or JDBC), persistence services in `dao/service/` (`*DaoService`: lookups and filtered listings over
  `dao/specification/`), row mappers in `dao/mapper/`; constructor injection only - `components.md` reads dependencies and tables from it.
- Calculations: pure Kotlin in `harbor-core/src/main/kotlin/com/acme/harbor/utils/`, KDoc with the formula and `@docs <calculation_id>`
  (e.g. `monthly_projection`), `BigDecimal` + `RoundingMode.HALF_EVEN`, a unit test per calculation in
  `harbor-core/src/test/kotlin/com/acme/harbor/utils/` whose cases are the worked examples.
- Migrations: `harbor-core/src/main/resources/db/migration/V<n>__<name>.sql`, one column per line - `db-schema.md` is parsed from them.
- Files <= 400 lines (`scripts/check-file-size.py`). No real client data anywhere; synthetic values only.

## Commands
- `python3 scripts/docs/gen-all.py` regenerates `docs/_generated/*` and the database documentation `docs/db/` (`schema.json`,
  one page per table from the migration comments, ER diagram); `--check` fails if they are stale (CI gate).
  Run it after changing an endpoint, topic, table, job, injected dependency or `@docs` tag and commit the regenerated maps.
  The layout the generators read (modules, base package, layers, contract paths) is `scripts/docs/docs-gen.json`.
- `python3 scripts/check-file-size.py --root . --max-lines 400 --baseline .filesize-baseline.txt`
- `mvn -q -pl harbor-core -am -DskipTests generate-sources` (regenerate `*Api` interfaces), `mvn test`.
- Local run: `docker compose -f init_docker_compose/docker-compose.yml up -d`, then start `harbor-core`.

## Where business rules live
Not here. Feature specs are in the docs repo (`harbor-docs/features/<context>/<ID>.md`, e.g. `P1-001`), formulas in
`harbor-docs/domain/calculations/<id>.md` (e.g. `monthly_projection`). Resolve an ID through `docs/_generated/docs-tags.md`
and cite it in answers, KDoc and commit messages; do not re-derive rules from code.
