# AGENTS.md - harbor-backend (Kotlin 1.9 / Spring Boot 3 / Maven: core + kafka_client / PostgreSQL + Flyway / Kafka)

Read by Copilot Chat (VS Code, JetBrains), Copilot CLI, the Copilot coding agent and other agent tools.
Copilot-specific extras are in `.github/copilot-instructions.md`; path-scoped rules in `.github/instructions/`.

## What this repository is
Backend of the Harbor platform: account representatives review a client's product movements in a **meeting
session**, model movements and peer simulations, compute monthly projections, cover ratios, market scenarios
and stress tests, and close the meeting with a PDF report.
Layout is **package-by-layer**: the root `pom.xml` has two modules - `core` (the Spring Boot application with all
business code in `core/src/main/kotlin/harbor/<layer>/`: `api`, `manager`, `service`, `dao`, `event`, `job`, `utils`,
`client`, `validator`, `mapper`, `model`, ...) and `kafka_client` (topic constants, event payloads, serde). The
bounded context of a class is its **name prefix** (`Product1*`, `Projection*`, `Stress*`, ...; mapping in the docs repo
`contexts.yml`): contexts `clients`, `meetings`, `imports`, `product1`, `product2`, `cover`, `market`, `stress`, `reports`, `admin`.
`init_docker_compose/` starts the local environment (PostgreSQL, Kafka, WireMock stubs of the external services).

## Read in this order (cheapest first) - never walk directories
1. `docs/_generated/index.md`, then `codebase-map.md` (modules -> layers -> classes, resource folders) or the one map
   that answers the question: `api-index.md` (endpoints, `Tag` = context), `events.md` (topics), `db-schema.md` (tables),
   `jobs.md` (scheduled jobs), `docs-tags.md` (spec ID -> code), `parameters.md` (admin parameter catalogue: key, seeded defaults per scope, readers, validator), `datasets.md` (named synthetic datasets: seeds and test fixtures with tables, row counts, sample rows).
2. The context's manager `core/src/main/kotlin/harbor/manager/<Ctx>Manager.kt` (KDoc + `@docs <ID>`).
3. Its dependencies from `components.md` (one row per class: layer, injected deps, tables, `@docs`, `file:line`).
4. One file + line range named in a map. Max 3 source files per question.
5. For "what breaks if" questions use the docs repo `generated/graph/<context>.md` instead of the maps.

## Contracts (source of truth)
- `core/src/main/resources/openapi/harbor-api.yaml` is the REST contract. The `*Api` server interfaces are **generated**
  from it into `target/generated-sources` at build time; the frontend client is generated from the same file.
  Never edit generated code. Change the contract first, regenerate (`mvn -q -pl core -am -DskipTests generate-sources`), then implement.
- `core/src/main/resources/openapi/harbor-events.yaml` (AsyncAPI) describes the Kafka topics;
  `core/src/main/resources/api/*.yaml` are the external service contracts (generated clients wrapped in `client/`).
- Every `/session/**` operation requires the header `X-Harbor-Session: <sessionId>` (defined once as
  `components/parameters/SessionHeader`); `component/SessionHeaderFilter` resolves it into `context/SessionContext`.
  Never read the header in controllers or managers.

## Conventions the generators rely on
- Context entry point = `manager/<Ctx>Manager.kt` with a KDoc block that ends with `@docs <ID>` directly above
  `@Service class` (e.g. `Product1Manager.kt` -> `@docs P1-001`).
- Business-prefix naming: every class starts with its context prefix from `contexts.yml` (`Product1Controller`,
  `ProjectionService`, `ProjectionDao`); classes without a known prefix are reported as `shared`.
- Controllers in `api/`: `@RestController class XxxController(...) : XxxApi` implementing `override fun <operationId>(...)`
  **without** `@*Mapping` annotations (they live on the generated interface). `api-index.md` joins harbor-api.yaml to these overrides.
- Kafka: topic names only via `Topics.<CONST>` (`kafka_client/src/main/kotlin/harbor/kafka/Topics.kt`, payloads in `kafka/events/`);
  listeners and publishers in `event/`: `@KafkaListener(topics = [Topics.X], groupId = "harbor-<context>")`,
  producers `kafkaTemplate.send(Topics.X, key, payload)`. Literals break `events.md`.
- Scheduled work: `@Scheduled(cron = "...")` methods in `job/` with a one-line KDoc -> `jobs.md`.
- Admin parameters: one constant per key in `enums/ParameterKey.kt`, seeds as `INSERT INTO parameter_set` in the migrations, reads only through `ParameterService` -> `parameters.md`. The meaning of a key is documented in the docs repo (calculation `## Parameters`), not in code.
- Datasets: every seed in `scripts/db/seed/*.sql` and every fixture in `core/src/test/resources/datasets/*.sql` starts with the header `-- dataset: <name>` / `-- purpose:` / `-- synthetic: yes` (`scripts/db/seed/README.md`) -> `datasets.md`; analysts cite them by name.
- Repositories in `dao/` (`*Dao`), constructor injection only - `components.md` reads dependencies and tables from it.
- Calculations: pure Kotlin in `core/src/main/kotlin/harbor/utils/`, KDoc with the formula and `@docs <calculation_id>`
  (e.g. `monthly_projection`), `BigDecimal` + `RoundingMode.HALF_EVEN`, a unit test per calculation in
  `core/src/test/kotlin/harbor/utils/` whose cases are the worked examples.
- Migrations: `core/src/main/resources/db/migration/V<n>__<name>.sql`, one column per line - `db-schema.md` is parsed from them.
- Files <= 400 lines (`scripts/check-file-size.py`). No real client data anywhere; synthetic values only.

## Commands
- `python3 scripts/docs/gen-all.py` regenerates `docs/_generated/*`; `--check` fails if they are stale (CI gate).
  Run it after changing an endpoint, topic, table, job, injected dependency or `@docs` tag and commit the regenerated maps.
- `python3 scripts/check-file-size.py --root . --max-lines 400 --baseline .filesize-baseline.txt`
- `mvn -q -pl core -am -DskipTests generate-sources` (regenerate `*Api` interfaces), `mvn test`.
- Local run: `docker compose -f init_docker_compose/docker-compose.yml up -d`, then start `core`.

## Where business rules live
Not here. Feature specs are in the docs repo (`harbor-docs/features/<context>/<ID>.md`, e.g. `P1-001`), formulas in
`harbor-docs/domain/calculations/<id>.md` (e.g. `monthly_projection`). Resolve an ID through `docs/_generated/docs-tags.md`
and cite it in answers, KDoc and commit messages; do not re-derive rules from code.
