# scripts/docs (harbor-backend)

| Script | Needs | Output |
|---|---|---|
| `gen-*.py`, `gen-all.py [--check]` | Python 3.11+ (standard library) | `docs/_generated/*.md` regex maps (`codebase-map`, `components`, `api-index`, `events`, `db-schema`, `jobs`, `docs-tags`, `parameters`, `datasets`, `index`) |
| `tag-candidates.py --contexts <docs repo>/contexts.yml` | same | inventory for the docs-tagger agent (stdout or `--out`) |
| (components) files of top-level functions | - | a Kotlin file without a class (`utils/Extensions.kt`) is one row of `components.md` named after the file, kind `file`; `tag-candidates.py` lists its functions, extension receivers included |
| `gen-db-docs.py` (run by `gen-all.py`) | same | `docs/db/`: `schema.json`, `schema/tables/<table>.md`, `schema/erd/overview.mmd`, `readme.md` from the migrations and their `COMMENT ON` statements; off when a database tool writes that folder |
| `templates/GraphExportTest.kt` (kit) | the repo's Spring test classpath | `docs/_generated/graph-export-be.json` precise graph from the running context |

## Layout: `docs-gen.json`
The generators do not hard-code the folder layout; they read `scripts/docs/docs-gen.json` next to them (or `--config <file>`).
Every key is optional and falls back to the values below (the Harbor layout). Nested blocks (`rest`, `kafka`, ...) are
merged key by key, so a partial block keeps the other defaults.

| Key | Meaning | Harbor value |
|---|---|---|
| `modules` | build modules (folders with a `pom.xml`); empty = `<modules>` of the root `pom.xml`, `["."]` for a single-module build (Gradle: list them) | `[]` (pom: `harbor-core`, `kafka-client`) |
| `source_root` | main sources inside a module | `src/main/kotlin` |
| `test_root` | unit tests inside a module (named `<Class>Test.kt` next to the calculation) | `src/test/kotlin` |
| `resources_root` | resources listed per folder in `codebase-map.md` | `src/main/resources` |
| `base_package` | package whose sub-packages are the layers; empty = shortest package of each module | `com.acme.harbor` |
| `layers` | layer name -> one-line role; a key with a slash (`dao/model`) makes that sub-package a layer of its own, any other sub-package folds into its parent | `advice`, `api`, `api/error`, `api/model`, `api/technical`, `api/validation`, `client/rest`, `client/kafka`, `component`, `config`, `context`, `dao/model`, `dao/repository`, `dao/service`, `dao/mapper`, `dao/converter`, `dao/specification`, `databind`, `enums`, `event`, `exception`, `job`, `manager`, `mapper`, `model`, `service`, `utils`, `validator` |
| `list_all_layers` | layers whose classes are all listed in `codebase-map.md` (others cut at 12) | api, manager, job, event, client/*, utils, validator, component, service, dao/service |
| `entry_layer` | the layer read first per context; `tag-candidates.py` proposes `<PREFIX>-NNN` tags for its classes | `manager` |
| `calculation_layer` | pure calculations; `tag-candidates.py` proposes `snake_case` calculation IDs for its classes | `utils` |
| `stereotypes` | annotations shown in the Kind column | RestControllerAdvice, RestController, Service, Component, Configuration, Repository, Entity, SpringBootApplication |
| `repository_bases` | Spring Data base interfaces whose first type argument is the entity (table inherited) | JpaRepository, CrudRepository, PagingAndSortingRepository, ListCrudRepository |
| `test_pattern` | regex on file names that marks tests (never scanned as components) | `(Test\|IT\|Spec)\.(kt\|java)$` |
| `exclude_paths` | repo-relative folders never read (generated sources outside `target/`, vendored code) | `[]` |
| `rest.open_api` | the REST contract (`openapi_<app>.yaml` style); empty = auto-detect (`api/openapi.yaml`, else the first OpenAPI document under `src/main/resources`) | `harbor-core/src/main/resources/openapi/openapi_harbor.yaml` |
| `rest.handler_match` | `operationId`: the handler is the method named like the operation, found with `rest.handler_pattern` (controllers implementing generated interfaces); `mapping`: the handler is the `@GetMapping("/x")` method whose verb + path equal the operation (hand-written controllers, class `@RequestMapping` prefix and `const val` paths resolved) | `operationId` |
| `rest.handler_pattern` | regex with one group = the operationId of a handler method | `override\s+fun\s+(\w+)\s*\(` |
| `rest.controller_annotation` | classes scanned for handlers | `RestController` |
| `rest.session_header` / `rest.session_marker` | header name added to the Params column when the operation's contract text contains the marker | `X-Harbor-Session` / `SessionHeader` |
| `asyncapi` | the Kafka contract (index.md, collector) | `harbor-core/src/main/resources/openapi/harbor-events.yaml` |
| `external_contracts_dir` | OpenAPI files of the external services the backend calls, directly in the folder or one sub-folder per service (`api/<service>/<file>.yaml\|.yml\|.json`); read by index.md and the docs collector | `harbor-core/src/main/resources/api` |
| `db_docs.dir` | the database documentation folder the docs collector copies (`readme.md`, `schema.json`, `schema/tables/*.md`, `schema/erd/*.mmd`), whoever writes it | `docs/db` |
| `db_docs.generate` | `true`: `gen-all.py` rebuilds that folder from the migrations with `gen-db-docs.py` (comments from `COMMENT ON TABLE\|COLUMN`); `false`: a database documentation tool (tbls, SchemaSpy, ...) owns the folder and only its layout must match | `true` |
| `db_docs.database` | `databaseType`, `name`, `schema` written into `schema.json` | postgresql / harbor / public |
| `kafka.listener_annotation` | consumer annotation (`topics = [...]`, `groupId`) | `KafkaListener` |
| `kafka.producer_pattern` | regex whose first group is the topic expression of a producer call | `\.send\(\s*([^,)]+)` |
| `kafka.property_files` | application.yml / .properties files that resolve `${...}` placeholders in topic names and `groupId` | `harbor-core/src/main/resources/application.yml` |
| `kafka.schema_dirs` | folders (recursive) holding the payload schemas or classes; a file named like the listener parameter type is linked in the Payload column | `kafka-client/src/main/resources` |
| `jobs.annotation` | scheduling annotation (`cron`, `fixedDelay`, `fixedRate`) | `Scheduled` |
| `jobs.lock_annotation` | distributed-lock annotation on the same method (ShedLock `@SchedulerLock(name, lockAtMostFor)`), shown in the Lock column; empty = none | `SchedulerLock` |
| `migrations.dir_pattern` / `migrations.file_patterns` | where the SQL migrations live and how they are named (Flyway) | `/db/migration/`, `V*.sql`, `R*.sql` |
| `migrations.view_patterns` | SQL files under the migrations folder that define views (`CREATE [OR REPLACE] VIEW`), listed in a Views section | `*view*.sql` |
| `parameters.*` | the parameter-key enum, its table and columns (`key_column`, `value_column`, `scope_columns`, `valid_from_column`) and the layer of the validators | `ParameterKey`, `parameter_set`, `key`, `value`, `scope_product_group`/`scope_country`/`scope_value`, `valid_from`, `validator` |
| `datasets.seed_dirs` / `datasets.fixture_dirs` | folders of the local seeds and of the integration-test fixtures (header contract in `gen-datasets.py`) | `scripts/db/seed`, `harbor-core/src/test/resources/datasets` |
| `docs_tags_include` | file patterns scanned for `@docs` tags (whole repo minus `exclude_paths`) | `*.kt`, `*.java` |
| `skip_generators` | generator scripts `gen-all.py` does not run and leaves out of `index.md` (a repository without a parameter enum skips `gen-parameters.py`, one without SQL datasets `gen-datasets.py`) | `[]` |

What a generator still assumes beyond the config: Kotlin or Java sources with one top-level class per file and a
`package` line; constructor injection (`class X(private val dep: Dep)`) for the Depends-on column; topic names as
string literals, `const val` constants (the declaring class first, then any module) or `${property}` placeholders - SpEL
expressions are shown as `<expr>`; Flyway-style SQL migrations (Liquibase XML/YAML changelogs are not parsed - point the patterns at SQL
changelogs or keep a SQL dump of the schema under a migration-like folder); `@Scheduled`-style triggers (Quartz job
classes are not detected); the parameter enum declares its constants as `NAME("key")`; `@docs <ID>` is one ID per
`@docs` line in the KDoc directly above the declaration.

The business context of a class is its name prefix (docs repo `contexts.yml`, `be` lists), never its folder; the
layered layout is why `components.md` carries the layer and the dependencies of every class. The precise graph
(`GraphExportTest.kt`, DI edges through interfaces, exact mappings, entity -> table) is optional and comes from the
Spring context in CI.
