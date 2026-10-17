# What to change in the enterprise project after step 3

Starting point: your docs repository was built from steps 1 to 3 of `ENTERPRISE-PLAYBOOK.md` **before** the frontend and
backend generators were rewritten and the Harbor repositories were regenerated (investigation commits `fc04e4f` to
`ed2fbe1`). Everything below is what those commits changed in files you have already copied, plus what the next steps
will expect. Nothing in your code repositories changes yet (that is step 6).

Paths below are the Harbor paths; in your repository replace `harbor-core` by `<app>-core`, `com/acme/harbor` by your
package path, `openapi_harbor.yaml` by `openapi_<app>.yaml`.

**Already applied sections 1 to 5 before 2026-10-16 midday?** Then start at section 6. It lists every change made after
investigation commit `5c8233a` (2026-10-16 09:55) on its own; the rows it repeats were added to sections 1 to 4 later and
need no second pass. **Applied section 6 as well?** Then only the sections after it are left: from section 7 on, every
batch of changes to this investigation repository gets a section of its own, headed by its commit range, with the
same four parts (re-copy whole, single rows, step 4 and later steps, playbook text). Apply the sections you have not
applied yet, in order.

## 1. Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/gen-graph.py` | `fe` lists in `contexts.yml` (page folders instead of one feature folder); FE page nodes folded into their context; backend sub-layers (`dao/repository`, ...) accepted; entities (`dao/model`) excluded from the graph; table comments and exact foreign keys from `generated/be/db/schema.json`; `be` entries with a wildcard (`"*StressTest"`, longest literal part wins); `depends-on` edges from the static calls listed in `components.md` |
| `scripts/collect-evidence.py` | reads the backend `scripts/docs/docs-gen.json` for the contract paths; copies external contracts from `api/<service>/` folders (yaml, yml or json); copies the database documentation folder (`db_docs.dir`) to `generated/be/db/` with frontmatter on its pages |
| `scripts/migration-status.py` | parses `fe: [PageA, PageB]` lists; `be` wildcard entries as in `gen-graph.py` |
| `scripts/context-pack.py` | FE-only contexts resolve to their first page node; the Data section carries the table pages (comments, relations, constraints) |
| `scripts/map-paths.py`, `scripts/graph-query.py` | only the usage examples changed; optional |
| `.github/prompts/context-map-from-code.prompt.md` | proposes `contexts.yml` with `fe` lists; backend sub-packages; wildcard `be` entries for product-first class names |
| `.github/prompts/source-priority-from-code.prompt.md` | backend sub-packages |
| `.github/prompts/docs-map-from-contexts.prompt.md` | **new**: drafts `docs-map.yml` from `contexts.yml` and the file trees (a wildcard entry becomes `**/*StressTest*.kt`) |

## 2. Docs repository: files where single rows change

The row numbers are those of the Harbor files; in your copies the same sentences carry your product names.

| File | Rows | Change |
|---|---|---|
| `features/_template.md` | `code_refs` (lines 20-21) | BE example `be/<module>/src/main/kotlin/<pkg>/manager/<Ctx>Manager.kt`; FE example `fe/src/pages/<Page>/<Page>.tsx` with the comment "the page(s) of the context (contexts.yml fe list); hooks and shared pieces from fe/codebase-map.md" (was `fe/src/features/<context>/index.ts`) |
| `domain/calculations/_template.md` | `executor.resource` (line 11), `code_refs` (lines 26-27) | `backend/<module>/src/main/kotlin/<pkg>/utils/<X>.kt` and `.../src/test/kotlin/<pkg>/utils/<X>Test.kt` (module folder and full package path) |
| `.github/instructions/features.instructions.md` | lines 22-23 | `code_refs` examples: `be/<module>/src/main/kotlin/<pkg>/<layer>/<Class>.kt`, `fe/src/pages/<Page>/...` |
| `.github/instructions/calculations.instructions.md` | lines 9 and 17 | same path shape for the unit test and the calculator |
| `.github/instructions/generated.instructions.md` | lines 17, 22-24 | module names (`<app>-core`, `kafka-client`), contract file `openapi_<app>.yaml`, external contracts from `api/<service>/` |
| `.github/agents/doc-sync.agent.md` | step 5 | the calculation package path `<module>/src/main/kotlin/<pkg>/utils/**` |
| `AGENTS.md` | read-order line 37 | "The backend is layered (`<module>/src/main/kotlin/<pkg>/<layer>/`): start at the context's `manager/<Ctx>Manager.kt`" |
| `.github/skills/calculation-spec/SKILL.md` | line 10 | calculator and test paths as above |
| `.github/skills/code-graph/references/graph-schema.md` | line 8 | example `location` with the module and package path |
| `.github/skills/code-graph/SKILL.md` | line 28 | `depends-on` = constructor injection **or a static call on a Kotlin object** (`Rounding.money(v)`) |
| `.github/skills/code-graph/references/subtask-mapping.md` | lines 8 and 12 | `openapi_<app>.yaml` instead of the old contract name; `class:*Repository` instead of `class:*Dao` |
| `.github/skills/write-feature-spec/references/source-priority.md` | rows 9-11 | regenerate with `/source-priority-from-code` (step 3 "With an agent"); the new rows read: test next to the calculator with the module path; "controller / service / validator / dao (repository, persistence service)"; "FE page component (`src/pages/<Page>/<Page>.tsx`) -> its hooks (`hook/use*.ts`) -> components (`components/<Name>/`)" |
| `architecture/overview.md`, `architecture/integrations.md`, `domain/context-map.md` | prose you rewrite anyway | describe the backend modules (`<app>-core`, `kafka-client` with schemas only), the `dao/*` and `client/*` sub-packages, topic constants per listener, and the FE pages column of the context map |

Step 3 table in the playbook now says **seven** instruction files (`contracts.instructions.md` was missing from the list).

## 3. Step 4 files (not written yet): the format changed

- `contexts.yml`: `fe` is a **list of page folders** (`fe: [BillingPage, InvoicePage]`, wildcards allowed, `fe: []` for a
  context without a page). Copy the comment header of the Harbor file; it explains the prefix rule and the page rule.
  A `be` entry may carry a wildcard over the whole class name (`stress: { be: [Stress, "*StressTest"] }`) for
  utility objects named product-first (`Product1StressTestUtils`); between two matching entries the longest literal
  part wins. Without it such a class lands in the product context, which is also a defensible cut.
- `docs-map.yml`: backend globs `be/<module>/src/main/kotlin/<pkg>/**/<Prefix>*.kt` (the `**/` spans the `dao/*` and
  `client/*` sub-packages); frontend globs per page folder `fe/src/pages/<Page>/**`, per types file, per shared piece;
  ignore the generated client `fe/src/services/openapi/**` (or your Orval output folder) and `**/src/test/**`.
  Draft both with `/context-map-from-code` and `/docs-map-from-contexts`, check with `scripts/map-paths.py`.

## 4. Step 6 (later): take the kits as they are now

Nothing to copy today. When you reach step 6, copy `code-repo-kit/be` and `code-repo-kit/fe` completely; they differ
from the versions you may have read earlier:

- Both flavours: `scripts/docs/docs-gen.json` (the layout), `scripts/docs/README.md` (key table), `_common.py` (shared),
  the new prompt `/adapt-docs-scripts` (security review and config proposal without running anything), `copilot-instructions.md`.
- Backend: every generator is config-driven; `layers.instructions.md`, `api.instructions.md`, `kafka.instructions.md`,
  `AGENTS.md`, `add-endpoint` and `explain-module` prompts describe sub-packages, `TOPIC` constants, `Dto` models, ShedLock.
- Frontend: instructions renamed (`pages.instructions.md`, `services.instructions.md` replace `features` and `api-client`),
  agents and prompts speak of pages, `gen-graph-fe.ts` reads the same `docs-gen.json`.

Backend `docs-gen.json` values already known from your answers: `base_package` = your three-segment package;
`modules` = `[]` (read from the root pom); `rest.open_api` = `<app>-core/src/main/resources/openapi/openapi_<app>.yaml`;
`rest.handler_match` = `operationId` (controllers implement the generated interfaces with `override fun`; parameter
annotations do not matter); `external_contracts_dir` = `<app>-core/src/main/resources/api`; `kafka.property_files` =
your `application.yml`; `kafka.schema_dirs` = `["kafka-client/src/main/resources"]`; `jobs.lock_annotation` =
`SchedulerLock`; `migrations.view_patterns` = `["*view*.sql"]`; `skip_generators` = `["gen-parameters.py", "gen-datasets.py"]`
(no parameter-key enum, no SQL datasets with the header convention); `test_pattern` as your tests are named;
`db_docs` = `{ "dir": "docs/db", "generate": false }` because your database documentation tool already writes that
folder (`readme.md`, `schema.json`, `schema/tables/*.md`, `schema/erd/*.mmd`) from the comments in the migrations; the
collector copies it as it is and the graph reads `schema.json` (table-level `parents`/`children` or column-level
`references` entries name the foreign keys; send one table with relations to confirm the shape).
`entry_layer` = `service` (the controller calls the service, which orchestrates and may call other services) and
`calculation_layer` = `utils` (the pure calculators and their unit tests, as in Harbor); the managers hold the business
logic the services delegate to. The source-priority rows then read: 9 BE context service `service/<Ctx>Service.kt`
(orchestration, which managers and services it calls); 10 BE manager `manager/<Class>.kt` (business rules, narrow
ranges); 11 BE unit test next to a calculator `<app>-core/src/test/kotlin/<pkg>/utils/<Class>Test.kt`; 12 BE calculator
`utils/<Class>.kt`, read after its test; then the FE rows; last controller (`api/`) -> service -> manager -> dao.
`AGENTS.md` line 37 and `features/_template.md` `code_refs` name `service/<Ctx>Service.kt` as the entry point instead
of the manager.
Utility objects with a product-first name (`Product1StressTestUtils`) match the product prefix; when such an object
belongs to another context, list a wildcard entry there (`stress: { be: [Stress, "*StressTest"] }`, the longest
literal part wins, the docs-map glob becomes `**/*StressTest*.kt`). Objects that call other objects statically
(`ClientSomethingUtils.hasSomething(...)`) are linked through `Depends on`, so the graph shows the helper chain of a
calculator and a service that calls a calculator without injecting it.
Frontend values: `pages_dir`, `hook_dirs`, `components_dir`, `route_files`, `route_constants`, `types`, `exclude_paths`
(the Orval output) and `test_pattern` follow the layout you described; `/adapt-docs-scripts` confirms each with a path.

## 5. Playbook

Sections 1, 3, 4, 5, 6 and 14 were updated for the page layout, the backend sub-packages, the config-driven generators,
the `/adapt-docs-scripts` flow (section 6, "With an agent") and the schema-only Kafka module (section 5). Sections 7 to
13 and 15 to 20 did not need changes.

## 6. Changes after 2026-10-16 midday (investigation commits `e0d96dc` to `8df619a`, handed over 2026-10-17 08:00)

Three topics: the database documentation folder as evidence (`docs/db` -> `generated/be/db/`), the backlog state of
the mapping check, and the two conventions of your utils layer (files of top-level functions, objects named
product-first that call other objects statically). Plus playbook text you read, not copy.

### 6.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/collect-evidence.py` | copies the backend folder named by `db_docs.dir` in `docs-gen.json` (default `docs/db`) to `generated/be/db/`: `.md`, `.json`, `.mmd`, `.svg`, `.png` only, `index.md` skipped, `readme.md` -> `README.md`, OKF frontmatter prepended to every page; the tool's own scripts under `docs/db/scripts/` are never copied |
| `scripts/gen-graph.py` | reads `generated/be/db/schema.json`: table note = table comment, foreign-key edges `fk <column>` from `parents` / `children` / column-level `references` (tolerant key names: `table`, `refTable`, `parentTable`, `tableName`, `column`, `refColumn`, `fkColumn`, ...), relations with `implied: true` kept and labelled `(implied, no constraint)`; regex foreign keys only when no `schema.json`; `be` entries with a wildcard (`"*StressTest"`, longest literal part wins); `depends-on` edges from the static calls that `components.md` now lists |
| `scripts/context-pack.py` | the `## Data` section carries the table page `generated/be/db/schema/tables/<table>.md` (H1 stripped, links rewritten, first 60 lines) and falls back to the `db-schema.md` section |
| `scripts/map-paths.py` | prints the spec of a matched row; `BACKLOG` for a matched row whose `specs: []` is empty (was `UNMAPPED`); `UNMAPPED` only when no glob matches |
| `scripts/check-freshness.py` | reports `BACKLOG <path>` for changed files of a backlog row and never fails on them |
| `scripts/migration-status.py` | `be` wildcard entries as in `gen-graph.py` |
| `.github/prompts/context-map-from-code.prompt.md` | wildcard `be` entries for product-first class names (`"*StressTest"`) |
| `.github/prompts/docs-map-from-contexts.prompt.md` | a wildcard entry becomes the glob `**/*StressTest*.kt` |

### 6.2 Docs repository: files where single rows change

| File | Row | Change |
|---|---|---|
| `.github/skills/write-feature-spec/references/source-priority.md` | row 4 (line 8) | add `generated/be/db/schema/tables/<table>.md` (table and column comments, relations) before `db-schema.md`; "Gives you" = "tables with their meaning" |
| `.github/skills/task-context/references/pack-anatomy.md` | `## Data` row (line 13) | "the page of every `tables[]` entry from `generated/be/db/schema/tables/<table>.md` (table comment, columns with comments, relations, constraints; first 60 lines), else the `generated/be/db-schema.md` section" |
| `.github/skills/code-graph/SKILL.md` | line 28 | `depends-on` = class -> class: constructor injection **or a static call on a Kotlin object** (`Rounding.money(v)`) |
| `.github/instructions/generated.instructions.md` | new row after `be/events.md` (line 21) | `be/db/README.md`, `be/db/schema.json`, `be/db/schema/tables/<table>.md`, `be/db/schema/erd/overview.mmd`: the database documentation (data dictionary, relations, constraints, ER diagram), from the backend `docs/db` folder, copied by the collector |
| `.github/agents/spec-writer.agent.md` | Data line (line 26) | "`table:*` nodes with the table and column comments from `generated/be/db/schema/tables/<table>.md` (column lists from `db-schema.md` when a table has no page)" |
| `.github/agents/architect.agent.md` | sources item 3 (line 14) | `generated/be/db/schema/tables/*.md` (`generated/be/db-schema.md` as fallback) |
| `contexts.yml` | comment header (lines 6-8) | the wildcard sentence: an entry with `*` is a wildcard over the whole class name, the longest literal part decides |
| `generated/manifest.yml` | - | written by the collector; the `db` entry (`Dir: generated/be/db`, `Source: backend`) appears on the next run, nothing to edit |

### 6.3 Step 4 (contexts.yml, docs-map.yml)

- `contexts.yml`: a `be` entry may be a wildcard (`stress: { be: [Stress, "*StressTest"] }`) for utility objects named
  product-first (`Product1StressTestUtils`); between two matching entries the longest literal part wins. Without it such
  a class lands in the product context, which is also a defensible cut.
- `docs-map.yml`: a row whose context has no spec yet keeps `specs: []`; `map-paths.py` prints `BACKLOG` for its paths,
  the freshness gate reports and passes. `UNMAPPED` now means "no glob matches", i.e. a missing row.
- The step 4 check in the playbook reads: one real path per context prints its spec, `BACKLOG` for a backlog row, and
  `UNMAPPED` only for paths you meant to leave out.

### 6.4 Step 6 (later): what changed in the kits

Take the kits as they are (section 4 still holds). The differences since midday, so you recognise them:

- `scripts/docs/docs-gen.json`: new key `db_docs: { dir, generate, database }`. Your value: `{ "dir": "docs/db", "generate": false }`
  because your database tool and its converter already write that folder from the migration comments; the collector
  copies it, the graph reads its `schema.json` (your `parents` entries `{ table, column, refColumn, onDeleteCascade, implied }`
  are read as they are).
- `scripts/docs/gen-db-docs.py` (new, run by `gen-all.py` unless `db_docs.generate` is false or it is in `skip_generators`):
  the kit's own writer of that folder from `COMMENT ON TABLE|COLUMN`; you do not run it.
- `scripts/docs/gen-all.py`: runs and checks the folder above (`--check` compares it, date line normalised).
- `scripts/docs/gen-components.py`: a Kotlin file with only top-level functions (`utils/Extensions.kt`) gets one row named
  after the file, kind `file (top-level functions)`; `Depends on` also lists the Kotlin objects (and classes with a
  companion) a declaration calls statically, so `Product1StressTestUtils -> ClientSomethingUtils` and
  `<Ctx>Service -> <Calculator>` become edges without injection.
- `scripts/docs/tag-candidates.py`: files of top-level functions are calculation candidates; extension functions
  (`fun BigDecimal.money()`) are listed as sub-calculations; wildcard `be` entries resolved as in `gen-graph.py`.
- `scripts/docs/README.md`: rows for `gen-db-docs.py`, the `db_docs.*` keys, the file-row and static-call conventions.
- `.github/instructions/migrations.instructions.md`: every new table gets `COMMENT ON TABLE`, every non-obvious column
  `COMMENT ON COLUMN`, in the same migration; the `docs/db` folder is committed with the migration when the kit generates
  it (for you: regenerated by your tool). `calculations.instructions.md`: the test of a file of top-level functions is
  `<File>Test.kt`. `AGENTS.md` and `copilot-instructions.md`: the `gen-all.py` lines mention `docs/db`.

### 6.5 Playbook text (read, nothing to copy)

- Pilot track before section 0: the five pieces, the deferred list, and the note on a knowledge base another team
  generated (quarantine under `confluence-import/`, migrate flows, rules, glossary, cross-check the tables).
- Section 1 item 6, section 3 acceptance, section 10 and the everyday sequence: the Copilot CLI does not load prompt
  files; after `/agent <name>` type `Follow .github/prompts/<name>.prompt.md with <input> = <value>, ...`.
- Section 5 contracts table: the database documentation row. Section 6 item 1: `db_docs`, and the paragraph on choosing
  `entry_layer` (the class the controller hands the request to: `service` for you) and `calculation_layer` (`utils`),
  with the managers as an ordinary source-priority row between them. Section 14: `gen-db-docs.py`.
- Section 4 check reworded (spec / `BACKLOG` / `UNMAPPED`); the `be` comment in the `contexts.yml` example mentions the
  wildcard form.

## 7. Changes after the section 6 hand-over (investigation commits `eeede0f` to `c70859f`, 2026-10-17 morning)

Two topics: the backend has Avro and JSON schemas but no AsyncAPI document, and two prompts for work you do now
(source priority after the layer decisions; the architecture pages after the external contracts).

### 7.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/context-pack.py` | the Kafka line of the Contracts section points at `generated/be/events.md` when `generated/asyncapi/backend.yaml` does not exist |
| `.github/prompts/source-priority-from-code.prompt.md` | inputs `entry` (`manager` \| `service`) and `tests` (root of the unit tests when they live apart from the code); the manager row follows the entry row; the test row always precedes the calculator row; reads `entry_layer` / `calculation_layer` from the backend `docs-gen.json` when present. Run: `/agent architect`, then `Follow .github/prompts/source-priority-from-code.prompt.md with product = <name>, backend = <path>, frontend = <path>, entry = service, tests = <unit-test root>` |
| `.github/prompts/integrations-from-contracts.prompt.md` | **new** (agent `architect`): refreshes the tables of `architecture/integrations.md` (Kafka, outbound REST per external contract, inbound REST per tag, jobs) and the C4 context diagram / "Contexts at a glance" of `architecture/overview.md` from `generated/openapi/external/*`, `backend.yaml`, `events.md`, `components.md`, `jobs.md`, `REPO_MAP.md`; prose stays yours. Run it after placing the external contracts (step 5) and after every collector run that changes them: `Follow .github/prompts/integrations-from-contracts.prompt.md with product = <name>, scope = both` |

### 7.2 Docs repository: files where single rows change

| File | Row | Change |
|---|---|---|
| `.github/agents/architect.agent.md` | sources item 3 (line 14) | `generated/asyncapi/backend.yaml` "(when present; else `generated/be/events.md` with the schema file paths)" |
| `.github/agents/architect.agent.md` | "Integration map refresh" task | names the prompt `integrations-from-contracts` and the overview parts it refreshes |
| `.github/agents/doc-sync.agent.md` | line 19 | "(or `generated/be/events.md` when the backend has no AsyncAPI document)" |
| `.github/agents/impact-analyst.agent.md` | line 27 | "(topics and schema files in `generated/be/events.md` when there is no AsyncAPI document)" |
| `.github/instructions/features.instructions.md` | line 20 | topics "from `generated/asyncapi/backend.yaml` (or from `generated/be/events.md`, which also names the schema file of each payload, when there is no AsyncAPI document)" |
| `.github/instructions/generated.instructions.md` | `asyncapi/backend.yaml` row (line 25) | "optional - a backend with Avro / JSON schemas only has none, and `be/events.md` (topic, producer, consumer, payload type, schema file path) is the Kafka source"; origin "`asyncapi` in the backend `docs-gen.json`; empty = none" |
| `.github/skills/task-context/SKILL.md` | line 31 | "(from `generated/be/events.md` when there is no AsyncAPI document)" |
| `.github/skills/task-context/references/pack-anatomy.md` | `## Contracts` row (line 12) | "(when the backend has no AsyncAPI document, the line points at `generated/be/events.md` instead)" |
| `.github/skills/gherkin-test-design/references/coverage-checklist.md` | line 28 | "(or with the schema file `generated/be/events.md` names for the topic)" |

### 7.3 Step 5 (contracts) and step 6 (later)

- Step 5: nothing goes under `generated/asyncapi/`; the own API and the external services' OpenAPI files under
  `generated/openapi/` are the whole hand-copied set. Then run `integrations-from-contracts` (7.1).
- Step 6 values: `asyncapi: ""`, `kafka.schema_dirs` = your schema folders (Avro and JSON). The collector copies
  nothing for an empty key; `events.md` links each payload type to the schema file of the same simple name; the
  classes generated from the schemas at build live under `target/` and are never scanned or read (a generated folder
  inside the source tree goes into `exclude_paths`). Check the payload column of `events.md` after the first run: a
  type without a link means the schema file name differs from the record or class name.
- Kit text (taken with the kits): `.github/instructions/kafka.instructions.md` (the AsyncAPI document is optional;
  generated event classes are never read or cited, the schema file is the contract); `scripts/docs/README.md`
  (`asyncapi` key: `""` when there is none).

### 7.4 Playbook text (read, nothing to copy)

- Section 5: the schemas-only row says to set `asyncapi: ""`; the "With an agent" paragraph names
  `integrations-from-contracts`. Section 18: the architecture-pages row names the prompt for the tables and diagram.
- Pilot track: the note on a knowledge base another team generated (quarantine, migrate, cross-check) - already in
  section 6.5 of this list.
