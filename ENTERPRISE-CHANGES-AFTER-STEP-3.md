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
| `.github/prompts/integrations-from-contracts.prompt.md` | **new** (agent `architect`): refreshes the tables of `architecture/integrations.md` (Kafka, outbound REST per external contract, inbound REST per tag, jobs) and the C4 context diagram / "Contexts at a glance" of `architecture/overview.md` from `generated/openapi/external/*`, `backend.yaml`, `events.md`, `components.md`, `jobs.md`, `REPO_MAP.md`; prose stays yours. Run it after placing the external contracts (step 5) and after every collector run that changes them: `Follow .github/prompts/integrations-from-contracts.prompt.md with product = <name>, scope = both`. Once, while your overview is still the Harbor text, in a second run after `scope = integrations`: `scope = overview-draft` rewrites the whole `overview.md` as `status: draft` (file table, repositories, both C4 diagrams, layers table, contexts table, evidenced cross-cutting rules; `> ❓ TODO (human)` for hosting, authentication and the rest) |

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

### 7.3b Step 6 shortest path (kit)

- `code-repo-kit/apply-kit.py` takes `--pilot` (no hooks, no workflows, no `docs-maps.yml`) and `--replace OLD=NEW`
  (repeatable; rewrites the Harbor names in the copied `.md`, `.yml`, `.json`, `.kt` files, longest first, never in the
  scripts) and ends with the list of copied text files that still mention Harbor. One run per repository, then
  `docs-gen.json` by hand with the values of section 4 and the `asyncapi` / `kafka.schema_dirs` values of 7.3, then
  `gen-all.py`. Playbook section 6 opens with this shortest path and, below it, the pilot checklist by hand: two
  tables (backend, frontend) of what to copy from the kit to which path and what to reword, what not to copy, then
  the four steps (run `gen-all.py` and read the tables, fix a missed row with the agent, commit, back to the docs repo).

### 7.4 Playbook text (read, nothing to copy)

- Section 5: the schemas-only row says to set `asyncapi: ""`; the "With an agent" paragraph names
  `integrations-from-contracts`. Section 18: the architecture-pages row names the prompt for the tables and diagram.
- Pilot track: the note on a knowledge base another team generated (quarantine, migrate, cross-check) - already in
  section 6.5 of this list.

## 8. Layer names that differ from Harbor's (investigation commits after `79df6ad`, 2026-10-18)

One topic: the graph builder no longer hard-codes Harbor's layer names and `manager` as the entry point.

### 8.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/gen-graph.py` | reads `generated/be/docs-gen.json` (`entry_layer`, `graph_layers`, `graph_exclude_layers`; Harbor's names when missing; `--be-config` overrides); the context node's entry point is the class `<Prefix><Layer>` of the entry layer (`<Ctx>Service` for you), else the shortest entry-layer class of the context; its note reads `entry point X (service)` |
| `scripts/collect-evidence.py` | copies the backend `scripts/docs/docs-gen.json` to `generated/be/docs-gen.json` (and the frontend one to `generated/fe/`) |
| `scripts/graph-viewer.py` | **new**: `python3 scripts/graph-viewer.py --community <id>` writes `.context/graph-viewer.html`, a self-contained page you open in any browser (Python and a browser, no server, no other tool); one community at a time, filter, neighbours, node details |

### 8.2 Step 4 / pilot piece 4

- Copying the maps by hand: copy the backend `scripts/docs/docs-gen.json` to `generated/be/docs-gen.json` as well,
  else the graph falls back to Harbor's layer names and to `manager` as the entry layer (your context nodes would
  carry no entry point and classes of layers Harbor does not have would be left out).

### 8.3 Step 6 (kits)

- `docs-gen.json`: two new keys, `graph_layers` (layers whose classes become graph nodes; the entry layer is always
  included; a sub-layer counts through its parent) and `graph_exclude_layers` (data layers: entities, API models).
  Set them when your folder names differ from Harbor's; with Harbor's names they can stay as copied.
- The `applyTo` globs of `.github/instructions/*.instructions.md` name folders (`api`, `utils`, `event`,
  `client/kafka`, `db/migration`): rename them to your folders when you reword the files.

### 8.4 Playbook text (read, nothing to copy)

- Pilot track piece 4 and section 6 item 1: the sentence on layer names that differ; the pilot checklist row for
  `docs-gen.json` names the three keys and the `applyTo` globs.

## 9. Views outside the migrations folder (investigation commits after `26d3618`, 2026-10-18)

One topic: `gen-db-schema.py` found view files only under `migrations.dir_pattern` (`/db/migration/`), so your
`<app>-core/src/main/resources/db/statistical-views/` folder produced an empty Views section. A new optional key
names further folders.

### 9.1 Step 6 (kit): files to re-copy whole

| File | Why |
|---|---|
| `scripts/docs/gen-db-schema.py` | a view file is taken when its path matches `migrations.dir_pattern` **or** any fragment of the new `migrations.view_dirs` (default `[]`, today's behaviour); the docstring says so |
| `scripts/docs/docs-gen.json` | the key `migrations.view_dirs` with its default `[]` |
| `scripts/docs/README.md` | one row for `migrations.view_dirs`; the `view_patterns` row mentions it |
| `.github/prompts/adapt-docs-scripts.prompt.md` | step 2 asks for `view_patterns` and `view_dirs` next to the other decision keys |

### 9.2 Your `docs-gen.json`

- Set `migrations.view_dirs` to `["/db/statistical-views/"]` (keep `migrations.view_patterns` = `["*view*.sql"]`);
  `gen-all.py` then lists your statistical views in the Views section of `db-schema.md`.

### 9.3 Playbook text (read, nothing to copy)

- Section 6, pilot checklist row for `docs-gen.json`: the clause on `migrations.view_dirs`.

## 10. The adapt-docs-scripts safety gate (investigation commits after `d7dd720`, 2026-10-18)

One topic: the agent running `/adapt-docs-scripts` stopped at step 1 on two deletions, as the prompt told it to:
`gen-db-docs.py` removed its whole `schema/` folder before rewriting it, and `gen-all.py --check` creates and removes
temporary folders in the system temp directory. Both were the scripts' own output, but the rule said "deletes outside
`docs/_generated`" and nothing more. The script now deletes files only, and the rule says what a script's own output is.
Nothing else in the gate changed; a stop on downloads, uploads, source edits or `exec` / `eval` still holds.

### 10.1 Step 6 (kit): files to re-copy whole

| File | Why |
|---|---|
| `scripts/docs/gen-db-docs.py` | no `rmtree`: pages of tables dropped since the last run are removed file by file inside `schema/tables/` and `schema/erd/` of `--out`; other files in the folder are left alone; `shutil` no longer imported |
| `scripts/docs/gen-all.py` | a comment at the `--check` branch: throwaway copy in a `tempfile.mkdtemp` folder, removed in the same run, nothing under the repository written or deleted |
| `scripts/docs/README.md` | the `gen-all.py` and `gen-db-docs.py` rows say the same in one clause each |
| `.github/prompts/adapt-docs-scripts.prompt.md` | step 1 defines "a script's own output": its `--out` folder (`docs/_generated/<file>`; `db_docs.dir` for `gen-db-docs.py`, file-by-file removal of dropped pages included) and a temp folder it creates with `tempfile.mkdtemp` and removes in the same run; `db_docs.generate` is a value the agent proposes in step 2, not a reason to stop; the stop sentence now reads "deletes or writes outside its own output as defined above" |

### 10.2 What to do

- Re-copy the four files, then run the prompt again. With `db_docs.generate = false` (your value, section 6.4)
  `gen-db-docs.py` never runs in your repository; the gate judges the script text, so the wording matters anyway.
- Expected security table rows: `gen-all.py` - writes "`docs/_generated` (and `db_docs.dir` when enabled); `--check`: a
  temp folder it removes", processes "the sibling generators with `sys.executable`"; `gen-db-docs.py` - writes "under
  `--out` only (removes dropped table pages there, file by file)"; every other script "under `--out` only".

### 10.3 Playbook text (read, nothing to copy)

- Section 6, "With an agent", item 1: the parenthesis on what a person checks in the security table names
  `db_docs.dir`, the file-by-file removal and the `--check` temp folder.

## 11. Bytecode cache and temp-folder cleanup in the kit scripts (investigation commits after `6b48a81`, 2026-10-18)

One topic: the agent running `/adapt-docs-scripts` stopped at step 1 again, this time on two findings in `gen-all.py`.
Importing `_common.py` created `scripts/docs/__pycache__` (a write next to the scripts, and the child interpreters were
started without `-B`), and `--check` created `tempfile.mkdtemp` folders whose `shutil.rmtree` was skipped by the early
`sys.exit` after a failed generator and by the `sys.exit(1)` on stale output (no `try/finally`). Every script now sets
`sys.dont_write_bytecode = True` before its `from _common import` line, `gen-all.py` starts the generators with `-B`,
and every temp folder a `--check` run creates is removed in a `finally` block on every exit path. Output text and exit
codes are unchanged. The prompt says that a bytecode cache is not a write to review and that a theoretical failure
path or a property of the interpreter is a note in the table, not a stop; the stop sentence itself is unchanged.
`_common.py` and `docs-gen.json` are not touched.

### 11.1 Step 6 (kit): files to re-copy whole

| File | Why |
|---|---|
| `scripts/docs/gen-all.py` (both kits) | `sys.dont_write_bytecode = True` before the `_common` import; the generators are started with `[sys.executable, '-B', script, ...]`; the body from the first `mkdtemp` to the end runs inside `try/finally`, and the `finally` removes every folder this run created with `tempfile.mkdtemp` (a `tmp_dirs` list, nothing else), also after a failed generator (`sys.exit(r.returncode)`) and after stale output (`sys.exit(1)`); messages and exit codes as before |
| `scripts/docs/gen-api-index.py`, `gen-codebase-map.py`, `gen-components.py`, `gen-datasets.py`, `gen-db-docs.py`, `gen-db-schema.py`, `gen-docs-tags.py`, `gen-events.py`, `gen-jobs.py`, `gen-parameters.py`, `tag-candidates.py` (backend kit) | one line each: `sys.dont_write_bytecode = True` before `from _common import` (`import sys` added where it was missing); nothing else |
| `scripts/docs/gen-codebase-map.py`, `gen-components.py`, `gen-docs-tags.py`, `gen-routes.py`, `gen-types-index.py`, `tag-candidates.py` (frontend kit) | the same line |
| `scripts/docs/README.md` (both kits) | the `gen-all.py` row: the `--check` temp folder is removed in a `finally` block, also after a failed generator or stale output; no bytecode cache (`sys.dont_write_bytecode`, children started with `-B`) |
| `.github/prompts/adapt-docs-scripts.prompt.md` (both kits) | step 1, one sentence before the stop sentence: the scripts set `sys.dont_write_bytecode = True` and `gen-all.py` starts the generators with `-B`, so a bytecode cache (`__pycache__`) is not a write to review; the `--check` temp folders are removed in a `finally` block on every exit path; a theoretical failure path or a property of the interpreter is a note in the verdict column, not a stop |

### 11.2 What to do

- Re-copy the files of 11.1 (in the backend: twelve scripts, the README, the prompt; your `docs-gen.json` and
  `_common.py` stay as they are). Delete a `scripts/docs/__pycache__` folder an earlier run left behind (untracked;
  `__pycache__/` in `.gitignore` if it is not there yet). Then run the prompt again.
- Expected security table rows: `gen-all.py` - writes "`docs/_generated` (and `db_docs.dir` when enabled); `--check`:
  temp folders it creates and removes in a `finally` block", processes "the sibling generators with
  `sys.executable -B`"; every other script "under `--out` only"; no row names `__pycache__` as a write; a verdict may
  carry a note (a theoretical path), not a stop.
- Checked on Harbor: no `__pycache__` under `scripts/docs` after `gen-all.py` and after `gen-all.py --check`; no temp
  folder left after a generator crash (bad config values), a forced failure of `gen-db-docs.py` or of a generator in
  the middle of the list, and stale output (exit 1).

### 11.3 Docs repository

Nothing changes: no file of the docs repository and no playbook text is touched by this section.

## 12. Whole-graph view in the graph viewer (investigation commits after `b3fd6f8`, 2026-10-19)

One topic: while tuning `contexts.yml` you want to see every community in one picture, to spot a page or a class that
landed in the wrong context. `scripts/graph-viewer.py` now opens its dropdown with a first entry `(all communities)`
that draws every node and edge of `graph.json`, nodes coloured by community (a stable palette, a legend in the side
panel; a legend entry opens that community). The layout is per community: cluster centres on a circle, members around
them, repulsion only inside a community, so the page stays usable at 1500 nodes / 4000 edges (checked with a synthetic
graph of that size; the Harbor graph, 301 nodes, lays out in well under a second). The text filter works across the
whole graph and dims what does not match (the single-community mode hides it, as before); click for details, drag and
wheel zoom are unchanged; the neighbours checkbox is disabled in this mode because it has nothing to add. A new flag
`--all` opens the page on that entry, the same as `--community "(all communities)"`; `--community <id>` and the output
path and defaults are as before. Standard library only, no network, no library in the page.

### 12.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/graph-viewer.py` | `(all communities)` entry (whole graph, community colours and legend, per-community cluster layout, filter dims non-matching nodes, neighbours checkbox disabled), `--all` flag; the single-community mode, `--community`, `--out` and the default output `.context/graph-viewer.html` unchanged |

### 12.2 Kits

Nothing changes: no file of the backend or frontend kit is touched by this section. The `scripts/README.md` row of the
docs repository and the playbook (section 8, the sentence on `--all`; the section 14 catalogue row) say the same as
12.1 and are read, not copied.

## 13. API calls of hooks that call a generated client (investigation commits after `3b4db43`, 2026-10-19)

One topic: in a frontend whose hooks call an Orval-generated client (`src/services/openapi/...`), the `API calls`
column of `codebase-map.md` was empty because the hooks name generated functions, not literal paths, and the
page-to-endpoint `calls` edges of the graph were missing for those pages. `gen-codebase-map.py` now reads the generated
client itself when the new `docs-gen.json` key `generated_client.dirs` names its folders (the folders may stay in
`exclude_paths`: only this generator reads them, the page scan still skips them). Every exported function of the
generated files yields the literal path of its body and its method (Orval's axios, custom-mutator, fetch and
react-query / swr shapes, including the `use<Name>` / `get<Name>QueryKey` / `get<Name>Url` wrappers, which map back
to the operation); a hook that imports such a name from a generated folder and uses it adds `METHOD /path` to the
column. Literal calls found by `api_call_pattern` are unchanged (bare paths); with `dirs: []` (the default, and the
Harbor value) the output is byte-identical to before. `gen-graph.py` of the docs repository reads both forms of the
cell: a `METHOD /path` entry folds onto the backend endpoint with that method and path suffix only, a bare path onto
every method as before; the Harbor graph is unchanged. The TypeScript exporter `gen-graph-fe.ts` keeps literal calls
only (README sentence); the generated-client calls reach the graph through the map.

### 13.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/gen-graph.py` | `API calls` cell entries of the form `METHOD /path` fold onto the endpoint with that method (bare paths as before) |

### 13.2 Frontend kit: files to re-copy whole (into the frontend repository's `scripts/docs/` and `.github/prompts/`)

| File | Why |
|---|---|
| `scripts/docs/gen-codebase-map.py` | `generated_client` parser (function name -> `METHOD /path` from the generated files, wrapper aliases, fetch-client url helpers), calls resolved through the hook's imports; the rest unchanged |
| `scripts/docs/README.md` | `generated_client` key row; the paragraph on generated clients (how the column is filled) replaces "the column stays empty"; the exporter keeps literal calls only |
| `.github/prompts/adapt-docs-scripts.prompt.md` | step 2 fills `generated_client` from one generated file and one hook; step 4 makes a non-Orval client shape a config case; step 5 expects `METHOD /path` entries |

### 13.3 Frontend repository: single key (a filled `docs-gen.json` is not re-copied)

Add to `scripts/docs/docs-gen.json` the block below, with the generated client folders of the repository (the same
paths as in `exclude_paths`); the four patterns are optional and default to Orval's shapes, listed in the kit's
`docs-gen.json` and the README for a client that looks different:

```json
"generated_client": { "dirs": ["src/services/openapi"] }
```

Then `python3 scripts/docs/gen-all.py --root .` and check that every page whose hooks import from the generated folder
has `METHOD /path` entries in the `API calls` column; after `collect-evidence.py` and `gen-graph.py` in the docs
repository those pages gain `calls` edges to the backend endpoints.

### 13.4 Playbook (read only)

Section 6, the `docs-gen.json` row of the frontend table: `generated_client.dirs` among the keys to fill. Section 14,
the `gen-codebase-map.py` catalogue row: API calls are literal paths and `METHOD /path` for generated-client calls. No
backend kit file changes.

## 14. Confluence HTML export importer (investigation commits after `dce39f5`, 2026-10-19)

One topic: the Confluence pages arrive as the standard "Export space to HTML" (or the same pages re-arranged one folder
per page, `<Title>_<pageId>/<pageId>.html` with the images next to it), two page trees of one space (business,
technical), and the quarantine wants one Markdown page per Confluence page with the header block. The new
`scripts/confluence-import.py` (standard library, no pandoc) reads the export kept under
`confluence-import/raw-html/<section>/` and writes `confluence-import/<KEY>/<section>/<slug>.md`: header block
(`source`, `title`, `section`, `confluence_id`, `url` with `--base-url`, `author`, `last_modified` parsed from the
page-metadata line, `path` and `parent` from the breadcrumbs, `source_lang` with `--lang`, `status: imported`,
`attachments`, `attachments_not_imported`, `imported_from`), the quarantine banner, and the body converted to GitHub
Markdown (headings shifted under the title, nested and task lists, tables with merged cells flattened and marked, code
macros with their language, info/note/warning/tip panels as quoted blocks, expand sections, status lozenges, links
between exported pages rewritten to the Markdown files, images the page shows copied to `<KEY>/_attachments/<slug>/`,
anything unknown kept as raw HTML with a comment; `--body html` keeps the body as HTML instead). A page whose
`confluence_id` already sits under `<KEY>/_done/` is never rewritten (the export newer than the migrated copy is
flagged); the generated files of a page gone from the export are removed (only files with `imported_from`, never
`_done/`). The inventory of `confluence-import/README.md` is regenerated between markers, one table per section, with
the guessed context from `contexts.yml` (title and spec IDs, as `migration-status.py` does); only its **Known state**
column is hand-edited and survives a re-import. `--check` writes nothing and exits 1 when the quarantine is out of
date. Checked on a synthetic Harbor export (both layouts, images, cross-section links, page links by id, an attachment
that is not an image, a page already in `_done/`, a page removed from the export, `--section`, `--no-images`,
`--body html`); `migration-status.py` lists the imported pages as Run 2 due without a change.

### 14.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/confluence-import.py` | **new**: the importer described above |
| `scripts/README.md` | the `confluence-import.py` row; `confluence-export.py` marked as the REST route |
| `confluence-import/README.md` | the two ways in, the folder layout, the import commands, rule 6 (only the images a page shows are imported; client data deleted before the import) and rule 8 (generated pages are regenerated, only the Known state column is hand-edited) - keep your own inventory rows; the generated part is added between markers on the first run |
| `.github/instructions/confluence-import.instructions.md` | `raw-html/` never edited or read; pages with `imported_from` regenerated; images are evidence of a screen |
| `.github/agents/confluence-migrator.agent.md` | input accepts `<space>/<section>/<page>.md` and reads the `section`, `path`, `attachments` headers; step 6 moves the page to `<space>/_done/` and leaves `_attachments/` in place |

### 14.2 What to do

1. Keep the HTML export under `confluence-import/raw-html/<section>/` (one folder per page tree you migrate: business,
   technical). Delete every screenshot or table with client data from it first.
2. `python3 scripts/confluence-import.py --src confluence-import/raw-html --space <KEY> --lang <code> --base-url <url>`
   with your space key; then `--check` must be clean, `migration-status.py --scope all` lists the pages as Run 2 due.
3. Fill the **Known state** column of the generated inventory (class and target concept per page); everything else in
   that table is regenerated.
4. Do not copy the synthetic pages of this repository (`confluence-import/raw-html/**`, `confluence-import/HARBOR/**`).

### 14.3 Playbook, runbook, handbook (read only)

Playbook section 9 (the import paragraph), section 13 (Confluence changes), section 14 (the catalogue row) and section
18 (the inventory row); runbook step 3 and the layout table row; handbook tree and flow C. No kit file changes.

## 15. Legacy pages in the source priority (investigation commits after `736c7e8`, 2026-10-20)

One topic: row 7 of the source-priority reference named the whole `confluence-import/` folder, written before the
folder gained `raw-html/` (the HTML export as received) and `<SPACE>/_attachments/` (images). An agent following the
row could open the raw HTML instead of the Markdown page. The row now names
`confluence-import/<SPACE>/<section>/<page>.md`, says the pack's "Legacy pages" section lists them and `_done/` holds
the migrated ones, and excludes `raw-html/` and `_attachments/` explicitly. Cost and "gives you" unchanged.

### 15.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/skills/write-feature-spec/references/source-priority.md` | row 7 as above; rows 8 and below are the ones `source-priority-from-code` rewrites for your layout, so re-copy before running that prompt, or edit row 7 by hand if you already did |

### 15.2 Kits, playbook

Nothing changes.

## 16. Catalogue for free-text requests (investigation commits after `e84398f`, 2026-10-20)

A request from an analyst arrives in free text and names no context or ID ("when imports change, do the stress
numbers refresh?", "a dashboard with the cover ratio trend and a new churn score"); it often spans several contexts
and mixes existing and new work. `context-pack.py` resolved free text by counting keyword hits in spec titles,
descriptions, tags and aliases and picked one winner, which was wrong for most such requests (flows were never
searched, no synonyms, one subject only). The new `scripts/gen-catalogue.py` writes `generated/catalogue.md`: one
page, one line each, for every context of `contexts.yml` (also those with code but no spec yet), flow, spec with its
aliases, calculation with its parameters and the specs using it, API endpoint (also those the code exposes but the
contract does not describe), Kafka topic with producer and consumer classes, table with its owning context, external
service, and glossary term with its aliases. The agent reads it, picks the subjects itself (several, of several kinds)
and builds one pack per subject; what matches no line is new work placed in the context it belongs to. The analyst
agent's step 1, the task-context skill, AGENTS.md, the Copilot instructions and the README say so; the collector's
`--graph` also rebuilds the catalogue; CI checks it with `--check`. This is step 1 of a larger change (multi-subject
packs, placement of new work, cross-context epics, the analyst's resolve -> gather -> analyse -> produce procedure
follow in their own sections).

### 16.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/gen-catalogue.py` | new |
| `scripts/collect-evidence.py` | `--graph` also runs `gen-catalogue.py` |
| `scripts/README.md` | `gen-catalogue.py` row, collector row, local loop |
| `.github/skills/task-context/SKILL.md` | free text goes through the catalogue first; `candidates:` rule |
| `.github/agents/analyst.agent.md` | step 1: resolve the subjects through the catalogue, one pack per subject |
| `.github/workflows/docs-quality.yml`, `.github/workflows/copilot-setup-steps.yml`, `ci-examples/collect-evidence.yml` | `python3 scripts/gen-catalogue.py --check` |

### 16.2 What to do

1. Run `python3 scripts/gen-catalogue.py` once and commit `generated/catalogue.md` (it is a generated concept; `build-index.py`
   lists it in `generated/index.md`). Rerun it after every evidence snapshot (`collect-evidence.py --graph` does) and
   after adding a spec, calculation, flow or glossary term; CI fails when it is stale.
2. `AGENTS.md`: the paragraph after "Work task-scoped" (free text -> catalogue first), read-order step 1, the
   "Catalogue" row of the commands table. `.github/copilot-instructions.md`: the sentence after the context-pack line.
   `README.md` "Layout": the catalogue sentence. Your own wording, same content, if you rewrote these files in step 4.

### 16.3 Playbook (read only)

Step 3 copy list (`gen-catalogue.py`), commands table (Catalogue row), step 8 (the collector also writes the
catalogue; what the page is), step 14 procedure step 1, scripts table (`gen-catalogue.py` row).

## 17. One pack for several subjects; flows and contexts as subjects (investigation commits after `8cca612`, 2026-10-20)

Step 2 of the analyst request flow. `context-pack.py` took one subject; a request about several contexts needed
several packs that repeated the same flow, graph and contract sections, and neither a flow nor a context could be a
subject. Now `--task` may be repeated: one pack, the known H2 headings kept, per-subject blocks headed
`### <task> (<kind>: <path>)` inside `Subject` / `Spec` / `Calculation` / `Flow` / `Context overview` / `Specs in the
flow`, shared sections (`Calculations`, `Flows`, `Graph neighbourhood`, `Contracts`, `Data`, `Related`, `Legacy pages`)
list each item once, a calculation or flow that is itself a subject is not repeated as a linked one, the default
budget is 500 + 300 per extra subject. New subject kinds: a flow (`flows/<name>.md`, `flow:<name>`, `FLOW-<name>`:
`## Flow` body, `## Specs in the flow` = Summary plus the rules the flow text cites per spec, graph impact of its
`code_refs`, Kafka line from `channels[]`) and a context (`context:<name>` from `contexts.yml`: `## Context overview`
= specs or "none yet" with the ID the first one gets, flows, endpoints with operationId and summary, tables owned,
calculations implemented by its classes, topics, classes by layer, FE pages with routes, its integrations rows,
overview lines, proposed contracts - the overview for placing new work; FE-only contexts use their first page for the
graph). Free-text fallback: function words dropped, title / aliases / id hits count double, glossary aliases map to
the term (reported as `glossary:`), flows are scored too, three candidates. Single-subject packs for IDs,
calculations and graph nodes are byte-identical to before (checked on 23 packs); `context:<name>` gains the overview.

### 17.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/context-pack.py` | as above |
| `scripts/gen-catalogue.py` | the how-to paragraph of the catalogue says one pack with a `--task` per subject; rerun it |
| `.github/skills/task-context/SKILL.md`, `.github/skills/task-context/references/pack-anatomy.md` | build examples, anatomy rows for `Flow`, `Context overview`, `Specs in the flow`, the merged-pack and resolution sections, escalation step 4 |
| `.github/agents/analyst.agent.md` | step 1: one pack, `--task` per subject, `context:<name>` for new work |
| `.github/prompts/context-pack.prompt.md` | several subjects separated by ` + ` |
| `scripts/README.md` | `context-pack.py` row |

### 17.2 What to do

`AGENTS.md`: the free-text paragraph and the "Task context pack" command row; `.github/copilot-instructions.md`: the
free-text sentence (same content as the analyst step). Rerun `python3 scripts/gen-catalogue.py`.

### 17.3 Playbook (read only)

Commands table (context pack row), step 14 procedure step 1, scripts table (`context-pack.py` row).

## 18. Request epics and the analysis document (investigation commits after `3a65431`, 2026-10-20)

Step 3 of the analyst request flow. Work items were one file per spec (`work-items/<ID>.yml`, `feature:` equal to
the file name, every rule cited from that one spec), so a request spanning contexts had no home. A second shape,
the **request epic**: `work-items/<slug>.yml` (`request: <slug>` lowercase kebab-case, `analysis:`, `specs: [...]`
= every spec a story cites, optional `flows:` and `contexts:`), same epic / stories / subtasks structure, a story
may cite rules of several specs, and beside it the **analysis document** `work-items/<slug>.md` written first from
`work-items/_analysis-template.md` (Request verbatim, Reading the analyst confirms, Parts with state unchanged /
changed / new and evidence, Trust, reused / changed / built, Contracts, Data, Flows, Calculations, Gaps, Stories
outline, Sources). Principle kept: nothing new without a rule - a new behaviour gets a draft rule or draft spec
from `spec-writer` first, a new operation a proposed contract, a new calculation a draft concept; then the stories.
`validate-work-items.py` checks both shapes (request name and slug form, every `specs[]` entry exists, the analysis
file exists, each cited rule belongs to a listed spec and exists there; feature epics unchanged); `coverage-matrix.py`
counts a request epic's stories for every spec they cite (a story counts for a spec when it cites one of its rules).

### 18.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/validate-work-items.py`, `scripts/coverage-matrix.py` | as above |
| `work-items/_schema.yml`, `work-items/_analysis-template.md` (new), `work-items/README.md` | both shapes documented; the template |
| `.github/instructions/work-items.instructions.md` | request epics, nothing new without a rule |
| `.github/skills/jira-work-items/SKILL.md`, `.github/skills/jira-work-items/references/slicing-heuristics.md` | "Request epics" section; cross-context and existing + new slicing |
| `scripts/README.md` | `validate-work-items.py` row |

### 18.2 What to do

Nothing beyond the copy; existing `work-items/<ID>.yml` files validate as before. Rerun `python3 scripts/coverage-matrix.py`
(byte-identical while there is no request epic).

### 18.3 Playbook (read only)

Nothing changes.

## 19. The analyst's procedure for a free-text request (investigation commits after `7169ac1`, 2026-10-20)

Step 4 of the analyst request flow. The analyst agent now works resolve -> gather -> analyse -> produce: subjects from
`generated/catalogue.md` (new work placed in its context, contexts with code but no spec included), one merged pack
with a `--task` per subject, a trust check, **question mode** (answer with citations, facts / unverified / unknown,
one line on how the question was read, evidence requests into Open questions), **analyse** (the analysis document
from the template; the Reading line and the Parts table are shown and the agent stops until the analyst confirms;
then `status: confirmed`), **nothing new without a rule** (draft rule or spec via `spec-writer`, proposed contract,
draft calculation, ADR / HLD via `architect` - before any story), **produce** (feature epic by ID or request epic
with `specs[]` and `depends_on` across contexts, validated), analytics mode and the `file:line` rule unchanged.
New prompt `analyse-request` (modes `question` | `analysis` | `work-items`); handoffs to `test-designer`,
`spec-writer` and `architect` take a request slug; `test-designer` builds one pack per spec of a request's `specs[]`
and writes scenarios into each spec's feature file; `hld-from-spec` and the architect accept a request slug (HLD
from the analysis document).

### 19.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | the procedure above (replace your copy, re-apply your product name and `../<be>` / `../<fe>` paths) |
| `.github/prompts/analyse-request.prompt.md` | new |
| `.github/agents/test-designer.agent.md`, `.github/prompts/tests-from-spec.prompt.md` | request slug input, one feature file per spec |
| `.github/agents/architect.agent.md`, `.github/prompts/hld-from-spec.prompt.md` | HLD for a request epic |

### 19.2 What to do

`.github/copilot-instructions.md`: the `/analyse-request` row of the job table. `README.md` quick start: the
`/analyse-request` bullet. `AGENTS.md`: the sentence in "Agents, prompts, skills". Your own wording, same content.

### 19.3 Playbook (read only)

Step 13 (test with three free-text change requests), step 14 (the agent file block replaced by the new procedure).

## 20. Acceptance run of the analyst request flow; proposed rules (investigation commits after `fc55b39`, 2026-10-20)

Step 5. Six requests in free text, expected breakdowns written beforehand, worked through the new procedure with
Claude in the analyst role (never Copilot): R1 quarterly view across Product 1, Product 2 and the stress test; R2
analytics dashboard from two existing calculations and a new churn score; R3 Excel download of the stress test
from the client window (new operation in an existing context vs a new renderer); R4 nightly import of cover
policies from the provider (new integration, context without a spec); R5 a question (import during an open
meeting: is the stress test rerun, what does the report contain); R6 premium estimate column on the cover chart
(cover context, no spec). Result: all six readings named the expected subjects from the catalogue; the merged
packs (2-5 subjects, 640-1600 lines) carried the evidence for every Parts row; R5 was answered from the flow with
citations; R6 and R4 stopped at the gate (a context without a spec cannot hold a rule - COV-001 first); R1 went
through to the epic. Two gaps in the conventions surfaced and are closed:

- **Proposed rules.** A `new` or `changed` part needs a rule a story can cite before the code exists. Convention
  (`features/conventions.md`, Business rules): the rule continues the spec's numbering with the marker **proposed**
  (request `<slug>`) after the ID; stories cite it (`needs-spec-review`); `doc-sync` removes the marker when the
  code implements it or marks it withdrawn. The analysis document lists the proposed rules it introduced.
- **Proposal file of a request.** `contracts/conventions.md`: a request epic keeps its contract proposal in
  `contracts/proposed/<slug>.openapi.yaml` with `x-request`, `x-specs`, and `x-extends` for a changed operation.

Harbor examples produced by the run (keep them as worked examples, or delete them in your copy): the analysis
`work-items/quarterly-view-across-products.md` (status confirmed) with the epic `work-items/quarterly-view-across-products.yml`
(four stories, `depends_on` across contexts, four open questions), the proposed rules BR-P1-001-12, BR-P2-001-10,
BR-STR-001-9, BR-PRS-001-11 with the proposed-contract notes under the API tables and change-log rows, the draft
calculation `domain/calculations/quarterly_rollup.md` (formula intended, worked examples TODO from the future test),
the proposal `contracts/proposed/quarterly-view-across-products.openapi.yaml`; and the analysis
`work-items/premium-estimate-on-cover-chart.md` (status draft, stopped: COV-001 needed first, questions to the owner).

### 20.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `features/conventions.md` | the "Proposed rules" bullet under Business rules (or add the bullet to your own conventions) |
| `contracts/conventions.md` | the request-proposal paragraph |
| `work-items/quarterly-view-across-products.md`, `.yml`, `work-items/premium-estimate-on-cover-chart.md` | optional: worked examples of a request epic and of an analysis that stops at the gate (Harbor content) |

### 20.2 What to do

Nothing else; the specs, the draft calculation and the proposal are Harbor content.

### 20.3 Playbook (read only)

Nothing changes (step 13 already asks for the three free-text requests).

## 21. Context pack: no budget by default (investigation commits after `24c9880`, 2026-10-20)

The default budget (500 lines, +300 per extra subject) was an estimate and already cut a single spec's pack (P1-001:
511 lines truncated, 971 complete). Every item in a pack is bounded on its own (a spec reduced to key sections above
200 lines, a table page 60 lines, a legacy page 5, a graph neighbourhood 80 per subject), so the pack now holds
everything its subjects need by default; `--budget N` remains as a cap for a tool with a context limit (lower-ranked
sections go first, the footer names them). Footer and summary line say "no budget: every section complete".

### 21.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/context-pack.py`, `scripts/README.md` | as above |
| `.github/skills/task-context/SKILL.md`, `.github/skills/task-context/references/pack-anatomy.md`, `.github/agents/analyst.agent.md` | "rebuild wider" became "drop the budget you set / add a subject"; size wording |

### 21.2 What to do

`AGENTS.md`: the pack-size words in "Work task-scoped" and the `[--budget N]` command row.

### 21.3 Playbook (read only)

Commands table (context pack row), step 14 procedure step 2.

## 22. Where a generated Markdown knowledge base goes (investigation commits after `358a519`, 2026-10-20)

A knowledge base another team generated (a tester's RAG knowledge base, `rag.md`) is hand-placed as
`confluence-import/<SPACE>/<name>.md` with the quarantine header block and a row in the README's "Current pages"
table, never under `confluence-import/raw-html/`: that folder holds only the HTML export, the importer reads only
`.html` files there and agents never open it, so a Markdown file there is invisible. Without an `imported_from`
header the importer never touches it. Nothing else changes.

### 22.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `confluence-import/README.md` | the "A Markdown file from elsewhere" bullet under "Two ways in" (or add the bullet by hand: your README has your own inventory) |

### 22.2 What to do

If `rag.md` is already in `raw-html/`, move it to `confluence-import/<SPACE>/rag.md`, add the header block
(`source`, `title`, `author`, `last_modified`, `status: imported`) and a "Current pages" row.

### 22.3 Playbook (read only)

The "A knowledge base another team already generated" paragraph before section 0 names the file and the folder.

## 23. The analyst may read code located through the maps (investigation commits after `eeb6aa4`, 2026-10-20)

One topic: the analyst could open code only at a `file:line` the pack itself named, and only when the task was
blocked. While the specs of a context are thin drafts, which is the normal state in the pilot, the pack often names no
range for the fact an analysis needs, so the analyst could only stop and hand off. Now, when the pack, a rebuilt pack
and the graph leave a question open that the answer or the analysis needs, the analyst reads at most **five ranges per
task**, 40-120 lines each, in `../backend` or `../frontend`. It locates them through the generated maps (a `file:line`
the pack names, `graph-query.py --find`, `generated/be/components.md`, `generated/fe/codebase-map.md` and
`components.md`, the `@docs` tags), never by searching code or walking folders. A finding is evidence, never a rule:
cited as `code-read <file:line>` with the commit from `generated/manifest.yml` in the analysis document, appended to
the spec's Open questions, and a story resting on it is `needs-spec-review` with its acceptance criteria still citing a
(draft) rule. Five ranges used and still open is a documentation gap: open question, handoff, stop. The other agents'
code access is unchanged.

### 23.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | description and role sentence; step 2 (rebuild the pack before any code), step 4 (a question may be answered from code as unverified), step 9 rewritten as above - if you adapted the file's domain sentence, re-apply it |
| `.github/prompts/analyse-request.prompt.md` | steps 2 and 3 name step 9 and the five-range limit for the whole request |
| `work-items/_analysis-template.md` | Parts evidence may be `code-read <file:line>`; Sources lists the code ranges read, how each was located, the commit and the question it answered |
| `.github/skills/task-context/SKILL.md` | the analyst line under "When the pack is not enough" (it also named the wrong step) |
| `scripts/context-pack.py` | the pack footer rule mentions the analyst's five ranges; the rest unchanged |

### 23.2 Docs repository: single rows

`.github/copilot-instructions.md`, the analyst row of the routing table: "context pack; up to five code ranges located
through the maps when it leaves a question open". `CONCEPT.md`, the context pack paragraph: the same exception in one
clause. Analysis documents already written are not touched.

### 23.3 Playbook and guides (read only)

Playbook section 0 (the safety table row and the paragraph on letting Copilot read the code), section 12 (the summary
of the analyst agent), 17.2 (the decision, revised with its reason) and section 15 (the catalogue row); `GUIDE.md`,
`HANDBOOK.md` and `ANALYST-DOCS-SETUP.md` say the same. No kit file changes.

## 24. Checks once at the end of a task; page components in the map (investigation commits after `35b86cb`, 2026-10-21)

Two changes of the same day, listed together so that one pass applies both.

**Checks once, at the end of a task.** Agents ran `okf-validate.py --strict` after nearly every step. Their own files
rarely asked for it, but `AGENTS.md` ("Before finishing any edit"), the `okf` skill (three times) and the
`okf-validate` skill's description ("before committing any doc change") did, and every step of a task counted as
"finishing". The runs checked almost nothing: the validator skips `work-items/` (the analyst's main output) and reads
only `.md`, and the `agentStop` hook runs the same checks anyway. Now the checks run once, after the last edit of a
task, for the kind of file it changed (a work-item file: `validate-work-items.py`; a spec or a calculation:
`validate-frontmatter.py`, `build-index.py`, `okf-validate.py --strict`), never after each edit, and a task that
changed no file runs none. The validator still reads the whole bundle and runs no git command (a `--changed` option
that asked git for the changed files was tried and withdrawn the same day; nothing below names it). It changes in two
ways:

- `--path <folder or file>` resolves links from the bundle root (the folder whose `index.md` carries `okf_version`)
  and lets only that folder or file fail; the problems of the other files are one count line. Before, `--path
  features --strict` reported 55 broken links on a clean bundle and failed.
- A past `stale_after` is listed as `stale` and never fails a run. Before, `--strict` (and with it the hook and CI)
  would have started failing on 2026-11-03 without any edit (first date: `generated/analytics/coverage-matrix.md`;
  about 25 concepts between 2027-01-06 and 2027-01-18), and the only "fix" within an agent's reach was to move the
  date. The reference checker never reported staleness; the index badges and the coverage matrix still do.

**Page components in the map; the exporter reads the tsconfig.** The shaping step's agent could not see the components
defined inside page folders. `components.md` listed only the shared library (`src/components/**`); `codebase-map.md`
names a page's components without `file:line`; and the TypeScript exporter lost almost every `renders` / `uses` edge,
because it built its program with fixed compiler options and ignored the repository's `tsconfig.json`, so every
`@/...` import stayed unresolved (Harbor: 3 `renders`, 0 `uses`). Now:

- `gen-components.py` writes a second table, **Page components**: one row per exported component under
  `<pages_dir>/<Page>/<components_dir>/` (shared folders included) with its page, purpose, props, where it is rendered
  (`file:line` of the JSX tag, first per file, its own definition excluded) and the repository's own hooks it calls.
  The library table is unchanged; the file's title becomes "Components (FE)". The new table's first column is
  `Page component`, so the docs repository's `gen-graph.py`, which reads every `Component` row as a library component,
  skips it: an older docs repository is safe too.
- `gen-graph-fe.ts` takes its compiler options from the repository's `tsconfig.json`; a Vite-style root config that
  only lists `references` hands over to the referenced config whose files include `src`. Harbor: 53 `renders` and 62
  `uses` edges (graph 852 edges, was 740), e.g. which modals each overview page renders and which hooks it uses.
- The playbook's shaping prompt reads the pages' `codebase-map.md` rows and the Page components table, may open each
  page's entry file (the architect opens no code unless asked) and lists what only a developer can answer.

### 24.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/okf-validate.py` | `--path` checked against the whole bundle, the `stale` level outside the gate, the summary line `N of M concept file(s) checked (...)` with an "other files" line under `--path`; no git, no `subprocess` |
| `.github/skills/okf-validate/SKILL.md` | description (once at the end of a task that changed concepts, never after each edit), the command row, the paragraph on `--path` and the whole bundle, the `stale` level, the exit code |
| `.github/skills/okf/SKILL.md` | produce and maintain step 3 (after the last edit, not per file); "Validate once, at the end of the task" |
| `.github/agents/analyst.agent.md` | new section "Checks (once, after the last edit of the task)": what you changed -> what you run, nothing for a question, a pack or analytics (if you adapted the file's domain sentence, re-apply it) |
| `.github/prompts/okf-validate.prompt.md` | step 4: re-run once after the fixes; `stale` lines are reported to their owners, never "fixed" |
| `.github/skills/okf/PORTING.md`, `scripts/README.md` | the port's additions; the `okf-validate.py` row |

### 24.2 Docs repository: single rows

| File | Rows | Change |
|---|---|---|
| `AGENTS.md` | Commands table, Validate row; the sentence "Before finishing any edit: ..." under the table | row: `okf-validate.py --strict` (the whole bundle; `--path <folder or file>` lets only that part fail), `[<file>]` on the two other validators; the sentence becomes the section `## Checks: once, at the end of a task, for what it changed` (copy it from the Harbor file) |
| `.github/copilot-instructions.md` | Guard rails paragraph | the hook runs the validators when an agent stops, so run the checks yourself once, after the last edit of a task that changed files; `stale` lines never fail it |
| `.github/prompts/okf-produce.prompt.md` | the final step | "Then, once after the last edit, run `build-index.py` and `okf-validate.py --strict`" |
| `.github/skills/spec-lifecycle/SKILL.md` | the "Finish with" bullet | add "The `agentStop` hook repeats the checks." |
| `CONCEPT.md` | the validators row of the tooling table | "agents once after the last edit of a task, for what they changed" |

The final validation step of the other agents, skills and prompts stays `okf-validate.py --strict`.

### 24.3 Frontend kit: files to re-copy whole (into the frontend repository's `scripts/docs/`)

| File | Why |
|---|---|
| `scripts/docs/gen-components.py` | the Page components table; the library table unchanged |
| `scripts/docs/gen-graph-fe.ts` | compiler options from the repository's tsconfig (`compilerOptions()`); the console line names the config it used; rebuild `out/` afterwards |
| `scripts/docs/README.md` | the `components_dir` and `shared_dir` rows; the exporter paragraph (tsconfig; an older export: run it again) |
| `scripts/docs/gen-all.py`, `scripts/docs/gen-codebase-map.py` | one sentence each: the index line of `components.md`, the pointer under the codebase map's intro |

### 24.4 Frontend repository: single rows

| File | Rows | Change |
|---|---|---|
| `AGENTS.md` | "Read in this order", item 1 | `components.md` (shared UI library, then page components: where each is rendered and which hooks it calls) |
| `.github/agents/code-reader.agent.md` | Procedure, step 1 | new row: "where is page component X rendered / which hooks does it call" -> `components.md`, Page components |

### 24.5 What to do

1. Docs repository: nothing beyond the copies and rows above. The hook (`.github/hooks/docs-quality.json`) and CI
   (`.github/workflows/docs-quality.yml`) keep running the whole bundle with `--strict`; with stale dates out of the
   gate they fail only on real problems.
2. Frontend repository: `python3 scripts/docs/gen-all.py --root .` and check the Page components table: it lists the
   components under `src/pages/<Page>/components/` (an empty table means `components_dir` is wrong), and for each
   dialog the Rendered by column points at the file that opens it. If the repository runs the exporter, also
   `npx tsc -p scripts/docs/tsconfig.gen.json` and `node scripts/docs/out/gen-graph-fe.js src
   docs/_generated/graph-export-fe.json`: the console line must name your tsconfig (`tsconfig.app.json` in a Vite
   repository). Commit `docs/_generated/`.
3. Docs repository: `python3 scripts/collect-evidence.py --graph` (or your collector job).
4. Re-run the shaping prompt (playbook section 10) for a context whose spec list is still provisional.

### 24.6 Playbook and guides (read only)

Playbook section 3 (item 5, Commands table and Checks), section 10 (the paragraph after the four runs; "With an
agent, the shaping step", the prompt as above), section 14 (the `okf-validate.py` and `gen-components.py` rows) and
section 18 (the context-map prompt finishes with `--strict`); `HANDBOOK.md` section 4 (the scripts row);
`ANALYST-DOCS-SETUP.md` step 4 (the `AGENTS.md` template: Validate row and the Checks section). The Claude wrappers in
`.claude/commands/` changed too; they belong to this investigation repository only.

## 25. The frontend exporter runs on TypeScript 7 (investigation commits after `25c6633`, 2026-10-21)

The frontend repository is on TypeScript 7.0.2, the native compiler. `gen-graph-fe.ts` was written against the
TypeScript 5/6 compiler API (`ts.createProgram`, `getTypeChecker`, `ts.findConfigFile`): under 7 the bare `typescript`
import resolves to a stub that exports only `version`, and `tsconfig.gen.json`'s `moduleResolution: node` is an error
(removed option). The script now uses the API that 7 ships: `typescript/unstable/sync` (a client of the bundled
compiler process) for the program, the checker and symbols, and `typescript/unstable/ast` for the node classes and
`is*` guards. It opens every listed source file in that process, which picks the file's project the way the language
server does: the nearest `tsconfig.json` that includes it (a Vite-style root config that only lists `references`
hands over to the referenced one; a file no tsconfig includes lands in the inferred project, relative imports only),
so the hand-written config selection of section 24 is gone; the console line names each config used and how many
files it covered. Symbols come back with their declaration's file path, which the script compares with the listed
files as before. The listed files are sorted, so the export is written in the same order on every file system.
Tested on Harbor (identical node and edge sets: 129 nodes, 267 edges, 53 `renders`, 62 `uses`; the graph is
unchanged at 852 edges) and on two scratch repositories: a Vite-style root `tsconfig.json` with only `references`
(hands over to `tsconfig.app.json`, `@/` imports and an `export *` barrel resolve) and one without any tsconfig
(inferred project, relative imports resolve). Both API modules are marked unstable by the TypeScript team: a later
7.x may rename something, and then this script is the only file to touch.

### 25.1 Frontend repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/docs/gen-graph-fe.ts` | TypeScript 7 API (`typescript/unstable/sync`, `typescript/unstable/ast`), project per file from the compiler process, sorted file list, header comment |
| `scripts/docs/tsconfig.gen.json` | `target` ES2022, `module` ESNext, `moduleResolution` bundler (`node` was removed in 7) |
| `scripts/docs/README.md` | the exporter's Needs cell (7.0 or later), the paragraph on what the exporter sees (compiler process, nearest tsconfig, inferred project, `tsconfig.gen.json`, no `baseUrl`), the IDE note's module name |

### 25.2 Frontend repository: what to check before the first run

- `tsconfig.json`: no `baseUrl` (TypeScript 7 rejects it, TS5102) and relative `paths` entries (`"@/*": ["./src/*"]`,
  TS5090). Harbor needed both edits; a repository that already builds with 7 has them.
- `package.json`: `typescript` at `^7.0.2`, `@types/node` as before. `openapi-typescript` 7.x declares a peer dependency
  on `typescript@^5`: `npm install` prints a warning, nothing fails.
- Run `npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json`
  from the repository root; the console line should name the repository's tsconfig and the number of files it covered.
  A file reported as "no project" or "not in <config>" is one the tsconfig does not include: widen `include` or accept
  the inferred project's relative-only resolution for it.

### 25.3 Docs repository

Nothing to copy: `gen-graph.py` reads the same JSON shape. After the next `collect-evidence.py --graph` run
`generated/fe/graph-export-fe.json` differs only in order (and the manifest in its hash); the graph files stay as they
are. `code-repo-kit/README.md` (investigation only) names the TypeScript 7 requirement in the kit's file list.

## 26. How to fill the Known state column (investigation commits after `e05e285`, 2026-10-22)

One topic: the **Known state** column of the quarantine inventory had no written vocabulary, only the class list of
the migrator and a few words in the runbook. The quarantine README gains a section "Triage: the Known state column",
placed between the quarantine rules and the tables it describes: where the column is (the hand-kept "Current pages"
table and every table of the generated inventory), who reads it (people only: no agent reads the table, so a page's
note is quoted in the request that starts its run), what to write (class with who takes it, condition, target), finished
examples, the one-line rule (a `|` splits the cell and the importer keeps only the last piece), that notes are kept by
page path (a page renamed in Confluence starts again at `to triage`), what a wrong note costs, and what happens after
migration (the row takes the `_done/` path and the importer replaces the triage note with `migrated <date>` or
`obsolete` from the page header; a fuller sentence written then stays). The `process` class is described as how the
team works, not product behaviour: behaviour across contexts is `feature-spec` with a flow as target. Rule 8 points at
the section. Checked: a re-import keeps the section and a filled note, and a note containing `|` keeps only its last
piece; the importer's `--check`, `okf-validate.py --strict` and `build-index.py --check` are clean.

### 26.1 Docs repository: one section to copy (the README holds your inventory, so it is not re-copied whole)

Copy the section from its heading `## Triage: the Known state column` to the line before `## Current pages` into your
`confluence-import/README.md`, right after the quarantine rules, and append `; what to write: "Triage" below` to the
last sentence of rule 8. Your inventory and your notes stay as they are. The section writes `<KEY>` for the space key
and names the inventory markers without spelling them out: do not add the full marker comment to it, because the
importer replaces everything from the first marker it finds.

### 26.2 Runbook and playbook (read only)

Runbook step 3 and playbook section 9 point at the section; the playbook adds that no agent reads the column. No kit
file and no script changes.

## 27. Block lists in frontmatter were read across keys (investigation commits after `6a7009c`, 2026-10-23)

One bug, found on the first enterprise spec. `scripts/_common.py` `get_list()` reads a frontmatter list written either
inline (`api: ["GET /a", "GET /b"]`) or as a block (`api:` followed by indented `- ` lines). The block form used a
DOTALL regex, so the item pattern ran across lines and the list went on until the end of the frontmatter: every
indented `- ` line of the keys below was returned as an item of the key above. A spec whose `api`, `events`, `tables`
and `calculations` are block lists therefore had its calculation links and table names inside `api[]`. Harbor never
showed it because every Harbor spec writes those four lists inline. The enterprise `spec-writer` wrote them as blocks
(valid, and the template shows the block form for `code_refs`), and the first context pack listed five calculation
documents under Contracts as "not found in the contract (verify the path)".

Who reads lists through this helper: `context-pack.py` (`api`, `events`, `channels`, `calculations`, `flows`, `specs`,
`contexts`, `code_refs`, `tables`, `used_by`, `tags`, `aliases` - the Contracts, Flows, Calculations and Graph sections of
a pack), `gen-catalogue.py` (the API, Events, Flows and Specs columns) and `migration-status.py` (`specs` and
`contexts` of flows). `validate-frontmatter.py`, `build-index.py` and `gen-graph.py` match their fields with their own
patterns and were not affected, which is why the validators stayed green on a spec with the symptom.

The fix: the block regex has no DOTALL flag any more, an item is one line (`[^\r\n]*`), and only a line that starts
with indentation and `- ` continues the list, so the next top-level key ends it. Checked with a frontmatter whose
`api`, `tables` and `calculations` are block lists (each key returns its own items) and on the whole Harbor bundle:
`okf-validate.py --strict`, `build-index.py --check`, `validate-frontmatter.py`, `validate-work-items.py`,
`gen-catalogue.py --check` and `gen-graph.py --check` clean, outputs unchanged (inline lists were never affected).

### 27.1 Docs repository: one file to re-copy whole

| File | Why |
|---|---|
| `scripts/_common.py` | `get_list()` block form: no DOTALL, one line per item, the next top-level key ends the list |

### 27.2 Afterwards, in your repository

If any spec, calculation or flow writes `api`, `events`, `channels`, `tables`, `calculations`, `flows`, `specs` or
`contexts` as a block list, its packs and the catalogue carried the extra items: delete `.context/` (git-ignored,
rebuilt on the next `context-pack.py` run) and run `python3 scripts/gen-catalogue.py` once; `gen-catalogue.py --check`
tells you whether the catalogue changed. No kit file, no agent, no prompt and no playbook change; writing the lists
inline is still fine and is what the Harbor specs do.

## 28. Owned operations in `api[]`; a source marker per business rule (investigation commits after `0947b9e`, 2026-10-23)

Two conventions, both prompted by the first enterprise spec and its agent's review of it. **Owned versus called
operations:** the spec-writer filled `api[]` with every endpoint of the graph neighbourhood (twelve on a screen that
handles three), and every consumer reads `api[]` as scope - the context pack pulls a contract excerpt per entry, the
coverage matrix counts endpoints by it, the test designer tags API tests from it. Now `api[]` lists only the operations
whose handler belongs to the spec's context (the endpoint's community in the graph; `api: []` for a frontend-only
context); every operation the screen calls still appears in the API / Events table, and one handled by another context
carries `owned by <SPEC-ID>` (or `owned by <context>, no spec yet`) in its Purpose column. A called operation reaches
the pack through the spec that owns it, so until that context has a skeleton its contract excerpt is not in the pack -
the reason to finish every Run 1 before Run 2. **Provenance per rule** (pattern F of `EXTERNAL-PATTERNS.md`, adopted
2026-10-22): until a person verifies the spec, every rule ends, after its footnotes, with one marker:
`(source: code <sources-id>#<symbol>)` names the `sources[]` entry of the file and the method, function or component
whose code or KDoc states the rule - a symbol, never a line range, because lines rot on the next commit and nothing
refreshes them while a symbol survives edits inside the file; `(source: legacy <sources-id>)`,
`(source: contract <operationId>)`, `(source: person human:<id>)`, and `(source: spec BR-<ID>-<n>)` for a mirrored rule
that defers to another rule. Proposed and withdrawn rules carry none. The marker is what the owner checks at Run 4 (the
method, not the file) and it stays after verification. `okf-validate.py --strict` warns on a draft, unverified
`Feature Spec` whose rule has no marker, whose marker names no `sources[].id`, or whose code marker names no symbol.

Applied to Harbor: the eleven draft specs carry 68 markers, read from the manager, service, validator, listener, modal
and page files their `sources[]` name (the three mirrored product-2 specs mostly `spec BR-P1-...`); the two verified
specs are exempt. `PRS-001` (frontend-only) had six called operations in `api[]`: now `api: []`, the table names the
owners (SES-001, P1-001, P2-001, MKT-001, STR-001), and the catalogue's endpoint lines no longer list PRS-001 as a spec
of those operations. Where the footnoted file did not state the rule, a `sources[]` entry for the file that does was
added (MKT-001 listener, STR-001 calculator, PRS-001 layout). Checked: the validator reports the three warning kinds on
a throwaway spec copy and zero on the bundle; `validate-frontmatter.py`, `validate-work-items.py`, `build-index.py`,
`gen-graph.py --check` clean; catalogue and coverage matrix regenerated (PRS-001 lines only).

### 28.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/okf-validate.py` | the marker warnings (draft, unverified Feature Spec: no marker, unknown `sources[].id`, code marker without symbol) |
| `.github/skills/spec-lifecycle/references/run-checklist.md` | Run 1: `api[]` owned only, a marker per rule; Run 4: check the symbol each marker names |
| `.github/skills/okf-validate/SKILL.md` | the warn bullet names the repo rule |
| `.github/skills/okf/PORTING.md` | the additions paragraph names the repo rule (CRLF file) |

### 28.2 Docs repository: sections and sentences to merge (your copies carry your own wording)

| File | Where | What |
|---|---|---|
| `features/conventions.md` | "Business rules", after the `sources[]` bullet | the **Provenance per rule** bullet |
| `features/conventions.md` | "References inside a spec", after the Endpoints bullet | the **Owned versus called operations** bullet |
| `.github/instructions/features.instructions.md` | after the numbering bullet; after the endpoints bullet | one bullet each |
| `.github/agents/spec-writer.agent.md` | step 2 API / Events; steps 3 and 4 | `api` owned only, table with owner; marker `code manager#<method>`, `legacy conf-<slug>` |
| `.github/agents/confluence-migrator.agent.md` | step 2, target exists | every rule it adds ends with `(source: legacy conf-<slug>)`; never the code form |
| `.github/agents/doc-sync.agent.md` | step 4 | a rule it adds or rewrites ends with the code or contract marker; `api[]` owned only |
| `.github/skills/write-feature-spec/SKILL.md` | steps 3 and 4 | the same two sentences |
| `AGENTS.md` | Provenance bullet | one sentence naming both rules |

### 28.3 Afterwards, in your repository

Refresh the first spec with `spec-from-code` once the rules are in (it keeps the file and its change log and reworks
the API section and the rule markers); do not rerun the skeleton. Every later skeleton follows the rules from the start.
Until the markers are in, `okf-validate.py --strict` warns on each draft rule, so copy the validator together with the
conventions and refresh the drafts in the same change, or keep the old validator until the refresh is done. Playbook
section 10 (Run 1 paragraph) and `EXTERNAL-PATTERNS.md` pattern F (applied note) are read only.

## 29. Spec prefixes of 3 to 5 characters (investigation commits after `c944aed`, 2026-10-23)

A review of the ID scheme asked two things: may a spec prefix be longer than three letters, and may a context name
carry a hyphen (`billing-configuration`). Nothing in the kit blocks either: every reader of `contexts.yml` parses the
key as `[\w-]+`, and every place that matches a spec ID (`validate-frontmatter.py`, `okf-validate.py`,
`coverage-matrix.py`, `migration-status.py`, `context-pack.py`, `validate-work-items.py`) matches `[A-Z][A-Z0-9]*`
before the dash, so `TARIF-001` and `BR-TARIF-001-3` pass. The prefix must stay one token of capitals and digits:
`TA-RIF-001` fails. The only text that said otherwise was one line of the architect prompt `context-map-from-code`
("2-3 uppercase letters"); it now says 3-5 uppercase letters or digits, one token, unique, from the word the code and
the business both use. Longer than five stops being readable in rule IDs, Gherkin tags and Jira keys.

### 29.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/prompts/context-map-from-code.prompt.md` | the spec-prefix sentence of the table bullet |

### 29.2 Renaming a context or cutting one in two (no kit file involved)

Do it before Run 1 of the context: a prefix ends up in file names, rule IDs, `@docs` tags, Jira keys and test names,
and nothing cites it yet at that stage. When the cut follows a class split in the code (one class family per product
type, `InvoicingDomestic*` and `InvoicingExport*` out of `Invoicing*`), split the code first and rerun the generators,
because specs cite symbols (`code_refs`, the provenance markers). Then `contexts.yml` (keys, prefixes; the longer
prefix wins, so `InvoicingDomestic` beats `Invoicing` without a wildcard entry), the folders under `features/` with
their `index.md` and the `context:` line of any draft, `docs-map.yml` rows, `domain/context-map.md`, the "Contexts at
a glance" table of `architecture/overview.md`, the context list and the ID line of `AGENTS.md`, the prefix table of
`features/conventions.md`, Known state notes in the Confluence inventory that name a target context. Then
`gen-graph.py`, `build-index.py`, `migration-status.py`, `gen-catalogue.py`, delete `.context/`, and check with
`map-paths.py` (one real path per context) and `graph-query.py --node context:<name>`. The pieces still named after
the undivided family (a controller, a result entity and its table, the page if one serves both halves) go to the
context whose screen spec documents the page; the other context's first spec cites that screen and mirrors identical
rules as `(source: spec BR-...)` (`features/conventions.md`, "Shaping specs" items 4 and 5).

## 30. Skeleton prompt: an optional entry file (investigation commits after `d2299ce`, 2026-10-24)

A context node carries one entry point: the class `<Prefix><EntryLayer>` when it exists, else the shortest class of the
entry layer. Run 1 reads exactly that file for Summary, Actors and Business rules. A context whose entry layer holds
one class per screen and no orchestrator above them (a hedge service and a scenario service behind two pages, no
`<Prefix>Service`) therefore gets the first screen's class as entry point, and the skeleton of the second screen would
be drafted from the wrong file. The prompt takes a third, optional argument, the entry file:
`/spec-skeleton-from-graph <ctx> <ID> service/<ScreenClass>.kt` (CLI: "Follow .github/prompts/spec-skeleton-from-graph.prompt.md
with community = <ctx>, id = <ID>, entry = service/<ScreenClass>.kt"). The spec-writer reads it instead of the node's
file, still one source file, and everything after the skeleton is unchanged: the spec's own `code_refs` and source
markers name the right class. Splitting such a context by prefix is the other answer, when the class names allow it.

### 30.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/prompts/spec-skeleton-from-graph.prompt.md` | the `entry` input and the sentence that uses it |
| `.github/agents/spec-writer.agent.md` | step 3: the entry file the call names replaces the node's file |
| `.github/skills/spec-lifecycle/SKILL.md` | Run 1 row: the third argument |
| `.github/skills/spec-lifecycle/references/run-checklist.md` | Run 1: the source-file item |

Your copies name the service layer where these name the manager (`entry_layer` = `service`); keep that wording when you
merge. Playbook section 10 (Run 1 paragraph) is read only.

## 31. Calculation `code_refs`: files, never line ranges (investigation commits after `454a5bc`, 2026-10-24)

Found on the first enterprise calculation audit: `calc-auditor` wrote `utils/<Class>.kt:<line>` into `code_refs`. It
was following the kit: `domain/calculations/_template.md` carried `#L10-L80` and `URL#Lx-Ly` as examples and
`.github/instructions/calculations.instructions.md` said "file, optional `#Lx-Ly`", while the spec rule adopted in
section 28 says a symbol, never a line range, because lines rot on the next commit and nothing refreshes them. The four
files now agree: `code_refs` and `sources[]` name the calculator and its test as files; the place inside a file is a
symbol, the test method in a worked-example row, the function or property in an audit row; the `file:line` of
`generated/be/docs-tags.md` says where the auditor reads and never enters the concept. Strip the `:<line>` suffixes
from your calculation documents' `code_refs` by hand (no validator rejects them; a flow's `code_refs` with a line
suffix match no graph node in `context-pack.py --files`, so its impact section comes back empty).

### 31.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `domain/calculations/_template.md` | the two `code_refs` lines and the `sources[].resource` placeholder |
| `.github/instructions/calculations.instructions.md` | the `code_refs` bullet |
| `.github/agents/calc-auditor.agent.md` | step 2: `file:line` is where you read, not what you write |
| `.github/skills/calculation-spec/SKILL.md` | step 7: file only, symbol in the rows |

## 32. Calculations: a source marker per Formula step (investigation commits after `a3340ca`, 2026-10-24)

Section 31 took the line numbers out of the calculation documents; this section puts the symbols in. Pattern F of
`EXTERNAL-PATTERNS.md`, applied to specs in section 28, now applies to calculations: until a person verifies the
document, every numbered step of the Formula step list and the Conventions paragraph end, after their footnotes, with
one marker, `(source: code <sources-id>#<symbol>)` naming the `sources[]` entry of the file and the function, property
or constant that implements the step (`impl#build`, `rounding#divideAsRatio`), or the legacy / person / spec form of the
spec rule. `code_refs` stay files (machines read them: impact, docs-map, the freshness gate); the marker is what a
reader follows (a function is a unit of meaning and survives edits inside the file; a line is true for one commit).
`calc-auditor` opens the symbol each marker names at Run 3 and compares the step with it; a symbol that no longer
exists or does not do what the step says is a `DOC-STALE` finding. `okf-validate.py --strict` warns on a draft,
unverified `Attested Computation` whose Formula step or Conventions paragraph has no marker, whose marker names no
`sources[].id`, or whose code marker has no symbol; a calculation tagged `proposed` (no implementation yet) is exempt.
Applied to Harbor: 24 markers on the five draft calculations, symbols read from the calculator files; the two verified
documents and the proposed roll-up untouched. Checked: the validator reports the three warning kinds on a throwaway
copy and zero on the bundle; `build-index.py --check` and `validate-frontmatter.py` clean.

Reading the calculators for the symbols also showed one audit candidate: `scenario_price_path` says "round to scale 4"
in step 3 while `ScenarioPricePath.apply` rounds with `money()` (scale 2). Left for `calc-auditor`, not fixed here.

### 32.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/okf-validate.py` | the Attested Computation marker warnings (step without marker, unknown `sources[].id`, code marker without symbol; `proposed` tag exempt) |
| `domain/calculations/_template.md` | step list and Conventions line carry the marker placeholders |
| `.github/agents/calc-auditor.agent.md` | step 2: open the symbol each marker names; a stale symbol is `DOC-STALE`; a step without marker gets one |
| `.github/skills/calculation-spec/SKILL.md` | steps 4 and 6: the marker per step and on the Conventions paragraph |
| `.github/skills/okf-validate/SKILL.md` | the warn bullet names the calculation rule |
| `.github/skills/okf/PORTING.md` | the additions paragraph names the calculation rule (CRLF file) |

### 32.2 Docs repository: sections and sentences to merge

| File | Where | What |
|---|---|---|
| `.github/instructions/calculations.instructions.md` | after the `code_refs` bullet | the **Provenance per step** bullet |
| `AGENTS.md` | provenance bullet of Hard rules | "so does every Formula step and the Conventions paragraph of a calculation" |

Your calculation documents written before this section: run `audit-calculation` on each (the auditor adds the markers
from what it reads) or add them by hand, one symbol per step; until then `okf-validate.py --strict` warns on each draft
step, so copy the validator together with the instructions and refresh the drafts in the same change.

## 33. Graph viewer: the `docs` community is selectable (investigation commits after `7b0edf8`, 2026-10-24)

Spec and calculation nodes carry the community `docs` in `graph.json`, while the file's `communities` list names the
code communities only (contexts, `shared`, `fe-app`, `fe-shared`, page communities). `graph-viewer.py` built its
dropdown from that list, so `docs` appeared in the legend of the whole-graph view with its node count but could not be
opened: the legend click did nothing and `--community docs` fell back to the whole graph. The dropdown now adds every
community found on nodes that the list lacks, and the start community is checked against the same set. Open the
`docs` entry to see the specs and calculations alone, with the neighbours option on to see the classes, endpoints and
pages their `implemented-by` edges reach. Agents never read the page; this changes nothing for them.

### 33.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/graph-viewer.py` | the dropdown options for node-only communities |

## 34. Analyst: a free reading pass when a question still blocks (investigation commits after `69095ed`, 2026-10-24)

Section 23 gave the analyst five code ranges per task, located through the maps, and made "five used and still open"
a stop. In a context whose documentation has not caught up, which is the normal state during migration, the stop
lands on the analyst: no answer, no epic, a handoff that waits for a spec run. The documentation gap became the
analyst's failure. Now a question that still blocks the answer or the analysis after the five ranges earns one
**free reading pass** over `../backend` and `../frontend`: search by text, open whole files, follow the chain from
the controller through the service and validator to the test, no range limit (analyst agent step 10). Three
disciplines keep the method intact. The pass is for a blocking question only: curiosity, a check of what the pack
already says and "is this intended" never earn it, because code says what the system does, not whether it is
wanted. The files read are listed in the analysis document's Sources (one chat line for a question), so the cost
stays visible. And every finding keeps the step 9 discipline: `code-read <file:line>` with the manifest commit,
unverified, `needs-spec-review`, an Open question in the spec whose item names `code-read`. That item is what
`coverage-matrix.py` counts in the new **answered from code** column (`openQuestionsFromCode` in the JSON): the
open questions the analyst had to settle from source, per spec, the documentation gaps that cost analyst time;
the migration lead orders the next spec runs by it. A Copilot CLI session without the sibling folders counts as
code not reachable: record the question and stop, as before. The spec-writer (manager file only in Run 1) and
the calculation auditor (the symbol each marker names) keep their narrower reading on purpose.

### 34.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | description and role sentence; step 4 (step 9 or 10); step 8 (the new column); step 9's last bullet hands over to step 10; step 10 new - if you adapted the file's domain sentence, re-apply it |
| `.github/prompts/analyse-request.prompt.md` | steps 2 and 3 name the pass |
| `.github/skills/task-context/SKILL.md` | the analyst paragraph under "When the pack is not enough" |
| `.github/skills/docs-analytics/SKILL.md` | the "Where did the documentation run out?" row, the report shape |
| `work-items/_analysis-template.md` | Parts evidence may come from step 10; Sources lists the free pass files |
| `scripts/coverage-matrix.py` | `open_items()` (an item with its continuation lines), the **answered from code** column and JSON field, the footnote |
| `scripts/context-pack.py` | the pack footer rule names steps 9 and 10; the rest unchanged |

### 34.2 Docs repository: single rows

`.github/copilot-instructions.md`, the analyst row of the routing table: "..., then a free reading pass for a question
that still blocks". `CONCEPT.md`, the context pack paragraph: the same clause. Run `python3 scripts/coverage-matrix.py`
once after copying so `generated/analytics/coverage-matrix.md` carries the column; existing Open questions written
under section 23 already cite `code-read` and are counted without any edit.

### 34.3 Playbook and guides (read only)

Playbook section 0 (safety table row, the paragraph on letting Copilot read the code), section 12 (the analyst
summary), section 15 (the catalogue row) and 17.2 (a second revision paragraph with the reason); `GUIDE.md`,
`HANDBOOK.md` and `ANALYST-DOCS-SETUP.md` (step 10 added to its agent copy) say the same. No kit file changes.

## 35. Analyst: the documentation folders are free after the pack (investigation commits after `e06b5bf`, 2026-10-24)

"Read the pack, not the repository" was written to keep agents out of the code and swept the documentation along:
the pack was the only sanctioned way into `features/`, `domain/` and the other folders, so an analyst that wanted a
neighbour spec, a table page or a legacy page had to rebuild the pack with another `--task` first. Those folders are
the agent's own material, cheap and safe to read, and the detour bought nothing. The analyst now opens or searches
`features/`, `domain/`, `flows/`, `architecture/`, `contracts/`, `work-items/`, `test-design/`, `generated/` and the
imported pages under `confluence-import/<SPACE>/` freely after the pack, with no limit and no rebuild first; the raw
Confluence HTML and the attachments stay off limits as before. The pack stays mandatory: it is the recorded slice a
task starts from (the analysis document cites it), the only source of the graph neighbourhood with its cross-context
edges, and the way to a merged slice over several subjects. Rebuilding it is for the record, not a precondition for
reading. Other agents keep opening the documentation files their procedure names, and code access is unchanged
(steps 9 and 10, section 34).

### 35.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | step 2: the folders the analyst may open after the pack, when to rebuild instead - if you adapted the file's domain sentence, re-apply it |
| `.github/skills/task-context/SKILL.md` | the footer rule wording, the Consume bullet on the documentation folders, step 4 of the escalation |
| `scripts/context-pack.py` | the pack footer rule; the rest unchanged |

### 35.2 Docs repository: sentences to merge

| File | Where | What |
|---|---|---|
| `AGENTS.md` | the context pack paragraph | "Read the pack first. ... the analyst opens or searches the documentation folders freely ...; other agents open the documentation files their procedure names; code only at the `file:line` the pack names" in place of "Read the pack, not the repository ..." |
| `CONCEPT.md` | the context pack paragraph and the summary table row | the same change in one clause each |
| `.github/copilot-instructions.md` | the analyst row of the routing table | "context pack, then the documentation folders freely; ..." |

### 35.3 Playbook and guides (read only)

Playbook section 1 (the quoted sentence) and 17.2 (a third revision paragraph); `HANDBOOK.md` part 4, `GUIDE.md`
and `ANALYST-DOCS-SETUP.md` say the same. No kit file changes.

## 36. Database documentation: the ER diagram parses and `ALTER TABLE` foreign keys are relations (investigation commits after `1aba808`, 2026-10-25)

Two defects of `gen-db-docs.py`, both seen on the first enterprise run. The ER diagram wrote a column that is both
primary and foreign key as `uuid summary_periods_id PK FK`; Mermaid wants the keys comma-separated (`PK, FK`) and
stopped on the line ("Expecting 'BLOCK_STOP', 'ATTRIBUTE_WORD', ',', 'COMMENT', got 'ATTRIBUTE_KEY'"). And the
relations were incomplete: the migration parser knew only an inline `REFERENCES` and a `FOREIGN KEY` constraint
written inside the `CREATE TABLE` body, with plain names; a foreign key added later (`ALTER TABLE x ADD CONSTRAINT
fk FOREIGN KEY (...) REFERENCES y`), a schema-qualified or quoted table name (`public.x`, `"x"`), the second column
of an `ALTER TABLE ... ADD COLUMN a, ADD COLUMN b` statement, a `CREATE TABLE` followed by `WITH (...)` and a
composite foreign key all went missing, in `schema.json`, the table pages and the diagram alike (`db-schema.md` had
the same gaps). The DDL reader is now one module, `scripts/docs/_migrations.py`, shared by `gen-db-docs.py` and
`gen-db-schema.py`: statements and column lists are split with comments, string literals and dollar quotes honoured,
and it reads `CREATE TABLE` (plain, schema-qualified or quoted names, column and table constraints, the multi-word
PostgreSQL types), `ALTER TABLE` with several actions per statement (`ADD [COLUMN]`, `ADD [CONSTRAINT] FOREIGN KEY
| PRIMARY KEY | UNIQUE | CHECK`, `DROP [COLUMN]`, `DROP CONSTRAINT`, `RENAME [COLUMN]`, `ALTER COLUMN ... TYPE | SET|DROP
NOT NULL | SET|DROP DEFAULT`), `DROP TABLE` and `COMMENT ON TABLE|COLUMN`. A schema prefix is dropped and names are
lower-cased, as before. A composite key is one relation (`columns` holds every column; the diagram label is quoted,
`"a_id, b_id"`); the shapes of `schema.json`, the table pages and the diagram are otherwise unchanged. Checked on a
throwaway migration set with every syntax above (4 tables, 7 relations, all found) and on the Harbor backend (same
21 tables and 18 relations as before, the two `PK, FK` lines the only diagram change); both diagrams parsed by
Mermaid 11.4.1 in a browser. The `gen-graph.py` fallback that reads relations from the `db-schema.md` diagram when
`schema.json` is absent accepts the quoted label.

### 36.1 Backend repository (kit `be/scripts/docs/`): files to re-copy whole

| File | Why |
|---|---|
| `scripts/docs/_migrations.py` | new: the shared migration reader |
| `scripts/docs/gen-db-docs.py` | reads through `_migrations.py`; the ER diagram writes `PK, FK` and quotes a composite relationship label; the rest unchanged |
| `scripts/docs/gen-db-schema.py` | reads through `_migrations.py`; one relationship per foreign key in its diagram; a column added by a later migration keeps its `(+<migration>)` suffix |
| `scripts/docs/README.md` | a row for `_migrations.py` |

Then rerun `python3 scripts/docs/gen-all.py` in the backend and commit `docs/db/` and `docs/_generated/db-schema.md`
(the collector copies `docs/db/` to the docs repository on its next run). If relations are still missing after the
rerun, the migrations use a syntax the reader does not know: send one such statement.

### 36.2 Docs repository: single rows

| File | Where | What |
|---|---|---|
| `scripts/gen-graph.py` | the `erDiagram` fallback loop after the `db_relations` loop | the relationship regex accepts a quoted label: `:\s*"?([\w, ]+?)"?\s*$` in place of `:\s*(\w+)`, with the comment line above it |

### 36.3 Playbook (read only)

Section 14: the `gen-db-schema.py` and `gen-db-docs.py` rows name `_migrations.py` and the `ALTER TABLE` foreign keys.

## 37. Context pack: the sanctioned code shape of a calculation is in the pack, by rule (investigation commits after `bed8293`, 2026-10-25)

The `task-context` skill described the Calculations section of a pack as "Purpose, Formula, Conventions, Worked
examples (never the Kotlin block)", and `pack-anatomy.md` said "never the code block" for a calculation subject.
`context-pack.py` did neither consistently: the `# Computation` block of a concept is a level-1 heading between
`## Formula` and `## Conventions`, the section cutter used for a calculation linked from a spec stops only at the
next `##`, so the block rode along inside Formula (as a stray `# Computation` heading in the pack), while the cutter
used when the calculation is itself the subject stops at `#` too and replaced the block with a pointer line. Decision:
the block stays in the pack. It is 10-15 lines per calculation, it is the most precise statement of rounding mode,
scale and inclusive thresholds on the page, and it is documentation the analyst may open anyway. Both branches now
include it: for a calculation subject the `Calculation` section lists Purpose, Inputs, Outputs, Formula,
**Computation** (demoted to `##`), Conventions, Worked examples, Audit, Open questions and the pointer line is gone;
for a linked calculation the `# Computation` heading inside Formula is demoted to `**Computation**`. The skill, the
anatomy reference and the investigation notes say the block is included. Checked on the `client_role_classification`
and `CLI-001` packs.

### 37.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/context-pack.py` | calculation-subject branch includes `# Computation` demoted to `##`, no pointer line; linked-calculation branch demotes the heading to `**Computation**` |
| `.github/skills/task-context/SKILL.md` | anatomy item 3: Formula with the sanctioned code shape, Audit listed |
| `.github/skills/task-context/references/pack-anatomy.md` | the `## Calculation` row lists Computation instead of "never the code block" |

No generated file changes; `.context/` packs are rebuilt on the next run.

## 38. Analyst: progressive disclosure inside the pack (investigation commits after `058c674`, 2026-10-26)

The bundle discloses progressively (index to index, one line per concept, open only what you need), but the
analyst's procedure said "build one pack, read it top to bottom" for every input. A small question ("how do we know
a client is an exporter?") therefore resolved to the spec CLI-001 and read its 521-line pack, five table pages and
the graph neighbourhood included, when the answer is the Formula of `client_role_classification`, the calculation
the glossary alias *Exporter* points at, in about twenty lines. Two causes: subject resolution had no rule for the
narrowest kind, and question mode reused the change-request pack. Now **a question takes the narrowest subject that
answers it** - the calculation for "how is it computed or classified", the spec for "what does the screen show or
allow", the flow for "in which order across contexts", never `context:<name>` (it places new work) - and is built
with `--budget 200`; the analyst reads the Subject with its badge and the section the question names, follows a
`... (truncated: see <path>)` pointer only when the answer needs it, and drops the budget (escalation step 1, as
before) only for the merged slice. **A change request keeps the full pack read top to bottom**: every section feeds
the epic and the analysis document cites the pack. No script change: the ranked truncation already keeps the
Subject, the spec or calculation body and the linked calculations whole at budget 200 and turns the rest into
pointers (CLI-001: about 215 lines; `client_role_classification`: 131 lines, nothing truncated). HANDBOOK 2.6 also
lost its stale "default 500 lines": the pack has no default cap.

### 38.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | step 1: narrowest subject for a question; step 2: change request full pack top to bottom, question `--budget 200` and one section read |
| `.github/prompts/analyse-request.prompt.md` | steps 1 and 2 say the same |
| `.github/skills/task-context/SKILL.md` | the disclosure paragraph under the title, a question example in Build, the first Consume bullet |

### 38.2 Docs repository: single sentences to merge

| File | Where | What |
|---|---|---|
| `AGENTS.md` | the pack paragraph, after "**Read the pack first.** It is the recorded slice the task starts from" | ": a change request takes the full pack top to bottom; a question takes the narrowest subject (calculation, spec or flow, never a context) with `--budget 200` and reads the Subject and the section it names, the rest stays a pointer" |
| `CONCEPT.md` | "How the analyst works", move 2 | replace "It reads the pack top to bottom and nothing else." with the change-request / question sentences of section 38 |
| `.github/copilot-instructions.md` | routing row of `/analyse-request` | the Reads cell adds "(a question: the narrowest subject, `--budget 200`, one section read)" |

### 38.3 Playbook (read only)

Section 3 item 2 (the AGENTS.md sentence), the analyst summary in section 12, and 17.9.

## 39. Analyst: a question searches the documentation folders before it rebuilds the pack (investigation commits after `83ed2a2`, 2026-10-26)

Section 35 allowed the analyst to open or search the documentation folders after the pack, in a sentence of step 2;
the numbered escalation ladder still began with "rebuild without the budget" and "rebuild with the neighbour as
another subject", and an agent takes the numbered steps. So a question whose section did not answer most likely
produced another subject's whole slice (body, calculations, graph neighbourhood) where one grep and one opened
document would do. Now question mode says it: when the section read does not answer, search `features/`, `domain/`,
`flows/`, `architecture/`, `contracts/`, `generated/` and `confluence-import/<SPACE>/` for the term, open the
document that matches and cite it; rebuild the pack (another `--task`, no budget) only when the question turns out
structural (which endpoint, table or topic, who calls what: the graph section) or spans several subjects. The skill's
escalation step 1 is split the same way (question: search first; change request or structural / multi-subject
question: rebuild), the later steps keep their numbers.

### 39.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/analyst.agent.md` | step 4 opens with the search-first sentence |
| `.github/prompts/analyse-request.prompt.md` | step 2 says the same |
| `.github/skills/task-context/SKILL.md` | escalation step 1 split for questions |

### 39.2 Docs repository: one sentence to merge

| File | Where | What |
|---|---|---|
| `CONCEPT.md` | "How the analyst works", move 3 | "For a question it answers from the section it read, searching the documentation folders for the term when that section does not answer and rebuilding the pack only for a structural or multi-subject question" |

### 39.3 Playbook (read only)

17.9, last sentences.

## 40. Confluence migrator: targets from the catalogue, a page may touch several specs (investigation commits after `aefa08d`, 2026-10-26)

The migrator's step 2 found "the existing target" by running the pack script with the page title as free text,
the keyword matcher the `task-context` skill itself calls a fallback not to be trusted across contexts, and the
procedure spoke of one target. A legacy page often describes the behaviour of several contexts; with a title naming
one of them the matcher returned one spec and everything was merged there, rules of the other context included
(against "Ownership is by rule, not by component"); with a title naming neither, a new spec was created next to two
existing skeletons; and a context named in the message could act as a filter, so one context's facts were merged,
the page moved to `_done/`, and the other context's facts were lost without the board ever showing the page again
(`migration-status.py` lists a page under every context it mentions, but only while it is outside `_done/`).
Step 2 now starts from `generated/catalogue.md`, like the analyst: name every spec the page touches, a context given
in the message is the primary target and never a filter, build one pack for the named specs, keep the title matcher
as the fallback for a page whose words match no catalogue line. Each fact is merged into the spec of the context that
owns that behaviour; a sequence across contexts belongs to a flow, or to an Open question in the primary spec when no
flow exists; every spec touched gets the `sources[]` entry. A page is processed once and moves to `_done/` when every
spec it touches has received its facts (step 6); when a context it describes has no spec yet, the rest is recorded as
an Open question in the primary spec and the page stays in place so the board keeps listing it, to be rerun after
that context's Run 1 (only new facts are merged then). The "never rewrite more than the page" rule says explicitly
that several specs for one page are normal.

### 40.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/confluence-migrator.agent.md` | step 2 rewritten (catalogue, every spec touched, ownership by rule, flow or Open question, no-spec-yet case), step 6 "processed once", the Never line |
| `.github/skills/spec-lifecycle/references/run-checklist.md` | Run 2 items: specs named from the catalogue, fact per owning spec, `sources[]` in every spec touched, `_done/` only when every context has a spec |

### 40.2 Docs repository: single rows to merge

| File | Where | What |
|---|---|---|
| `.github/skills/spec-lifecycle/SKILL.md` | the Run 2 row | "(one page per run; the page may touch several specs, each fact goes to the context that owns it)", Reads: "the page, the catalogue, the pack" |
| `CONCEPT.md` | the lifecycle list, item 2 | the sentence of section 40 in short (specs named from the catalogue, fact per owning context, flow for a sequence, `_done/` once every context has a spec) |
| `.github/copilot-instructions.md` | the routing row of `confluence-migrator` | Reads: "the page, `generated/catalogue.md` (every spec the page touches), the pack, generated maps" |

### 40.3 Playbook (read only)

Section 10, "Run 2, legacy pages".

## 41. Context pack: the UI flow survives the spec reduction (investigation commits after `ca41b7e`, 2026-10-26)

A spec body longer than 200 lines, or than 60 % of a `--budget`, is reduced to key sections before the ranked
truncation runs. The keep list was Summary, Actors, Business rules, API, Data, Calculations, Edge cases, Open
questions; `UI flow` was not in it. With the question budget of 200 (section 38) every spec over 120 body lines
(Harbor: P1-001, ADM-001) was reduced, so a "what does the screen show or allow" question, the one a spec subject
exists for, got a pack without the screen's flow and only the pointer "reduced to key sections". `UI flow` is now
kept (10-15 lines per spec); the task-context skill's anatomy item 2 and the `## Spec` row of `pack-anatomy.md` list
the sections kept and both triggers of the reduction. Measured at budget 200: P1-001 221 lines and ADM-001 213
lines, both reduced, both with the UI flow section; CLI-001 unchanged (not reduced).

### 41.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `scripts/context-pack.py` | `UI flow` in the spec reduction keep list |
| `.github/skills/task-context/SKILL.md` | anatomy item 2 names the kept sections and both triggers |
| `.github/skills/task-context/references/pack-anatomy.md` | the `## Spec` row says the same |

## 42. Legacy architecture pages reach the architect (investigation commits after `d9d90a8`, 2026-10-27)

The triage table of `confluence-import/README.md` and the runbook sent `architecture`, `decision` and still-relevant
`process` pages to `architect`, but nothing carried them there: `architect.agent.md` had no task for a legacy page and
did not read `confluence-import/`; the migrator classified these pages and then handled them like feature pages
(only `calculation` was handed off); the runbook listed them under the migrator in one bullet and under the
architect in the next; and `migration-status.py` printed `@confluence-migrator` for every page without a context
(Harbor: `technical/deployment-notes.md`, `technical/kafka-topics.md`). Now:

- `architect` has a **Legacy page** task: one page per run, after `/integrations-from-contracts` (scope
  `integrations`, and `overview-draft` while the overview carries the reference text), not after the specs; target by
  content (overview prose; `manual` rows and prose of `integrations.md`; a draft ADR with the alternatives the page
  gives, a missing one as an open question; a document under `architecture/` for a procedure); claims checked against
  `generated/`, a `gen` row or existing prose never edited, a difference is a CONFLICT callout; glossary terms;
  `sources[]` and `generated.by: copilot/architect`, `status: draft`; page to `_done/` unless a part was handed off.
  Hand-offs to `confluence-migrator` (feature part) and `calc-auditor` (formula part).
- `confluence-migrator` hands these pages to `architect` without editing; a `feature-spec + architecture` page is
  merged for its feature part first, then handed on, and the architect moves it (the last agent moves the page).
- `migration-status.py` routes a page whose title reads as architecture (`ARCH_TITLE`: architecture, integration,
  deployment, infrastructure, hosting, Kafka, decision, with the Czech stems) to `@architect`: inside a context's
  Run 2 line, or in a new "Architecture pages" block for pages without a context. The title wins over a formula word
  in the body. Check the list of stems against your export's titles.

### 42.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/architect.agent.md` | description, hand-offs, the "Legacy page" task, `log.md` line |
| `.github/agents/confluence-migrator.agent.md` | description, hand-off to `architect`, step 1 routes architecture / decision / process pages, step 6 "the last agent moves the page" |
| `scripts/migration-status.py` | `ARCH_TITLE`, the `architecture?` kind, `@architect` routing, the "Architecture pages" block, the order-of-work sentence; regenerate `migration/all.md` after copying |

### 42.2 Docs repository: single rows to merge

| File | Where | What |
|---|---|---|
| `.github/copilot-instructions.md` | routing table, after the `architect` row | new row: legacy architecture / decision / process page -> `architecture/`, agent `architect` (task "Legacy page"), reads the page, `architecture/`, generated maps and contracts |
| `.github/agents/migration-lead.agent.md` | procedure step 1 | the generated file also lists "the architecture pages (by title) with their `@architect` command" |
| `.github/instructions/confluence-import.instructions.md` | after the formula-page bullet | "An architecture, decision or still-relevant process page is handled by `architect` (task "Legacy page", into `architecture/`), not by `confluence-migrator`." |
| `CONCEPT.md` | agents table, rows `architect` and `confluence-migrator` | architect: job adds legacy architecture, decision and process pages, reads the page, writes glossary and `_done/`, hands off to migrator / calc-auditor; migrator: hands off also to `architect` |
| `confluence-import/README.md` | Triage class table, rows `architecture` and `decision` | the command `@architect <page>` (task "Legacy page", after `/integrations-from-contracts` for `architecture`) |

### 42.3 Playbook (read only)

Section 9, "With an agent" (item 3 new), and section 10, "Architecture pages" after Run 2. `MIGRATION-RUNBOOK.md`
Step 5, `GUIDE.md` and `HANDBOOK.md` agent tables say the same.

## 43. The migrator never creates a spec; two corrections to section 42 (investigation commits after `3a9f380`, 2026-10-27)

Apply 42 and 43 together: 43.1 re-copies the same three files as 42.1 in their later state, so a file copied once
from the commits of 43 carries both.

**Candidate specs.** The migrator's step 2 kept a bullet from the first version, "no target -> create from the
matching template (or hand to `spec-writer` if the context has a graph community)". It contradicts the lifecycle
("No `features/<ctx>/<ID>.md` exists -> Run 1. Never start from a legacy page") and the shaping decision the lead
takes with a developer before Run 1 (`features/conventions.md`, "Shaping specs"); the `spec-writer` hand-off it
names does not exist; and its condition is true for nearly every context, so it chose nothing. A page about a
modal, sub-capability or screen that no spec of its context covers now gets no spec from the migrator: when the facts
fit an existing spec within the size caps they are merged there, otherwise the migrator leaves one line the board
reads under the primary spec's Open questions, `- [ ] candidate spec: <title> (legacy conf-<slug>; owner: migration
lead) - <what the page describes>`, keeps the page out of `_done/` and reports it. `migration-status.py` lists every
such line as `**Shaping - candidate spec**` under the context, with the next free spec number proposed for
`/spec-skeleton-from-graph`; the lead and a developer confirm the spec (or fold it into an existing one), Run 1
writes it from the code, the page is rerun and only the new facts are merged. A new spec has two origins: the code
(Run 1) and a request the analyst takes to a context without a spec; a Confluence page is never one. A "Never"
line says so in the migrator.

**Corrections to 42.** (a) An architecture page that mentions a context was listed inside that context's runs as
"Run 2 - legacy merge" with the `@architect` command, counted as a legacy merge and blocking the context's "ready"
state, against the rule that these pages are not a spec's run. The board now lists architecture pages once, in the
"Architecture pages" block (with the contexts each mentions), counts them in the summary line separately and
excludes them from every context. (b) The migrator's step 6 said a page with an architecture part is moved by
`architect`, which was wrong when the architect had taken the page first and handed its feature part to the
migrator; both agents now say "the last agent that takes the page moves it", in either direction. (c) A mixed page
(`feature-spec + architecture`) whose feature part left a candidate spec or hit a context without a spec must stay
out of `_done/` for the rerun, but the hand-off told the architect to move it; the migrator's hand-off now says
whether the page may move, and the architect's step 6 respects it. (d) The same for a `feature-spec + calculation`
page: the triage README said "the migrator takes the page once and hands the formula part to the calc-auditor",
but the migrator's procedure only knew the pure formula page (hand off and stop), the auditor set the page header
and never moved the page to `_done/` nor cited it in the concept, and nothing sent the screen rules of a page that
reached the auditor first back to the migrator. The migrator now merges the screen rules of a mixed page (a rule
that quotes a threshold links the calculation concept instead of carrying the value) and hands the formula part
on with whether the page may move; the auditor cites the page in the concept's `sources[]`, moves it when it is the
last agent, and has a hand-off to the migrator for the screen rules of a page that reached it first. The board's
formula-page line says when to run the migrator instead.

### 43.1 Docs repository: files to re-copy whole

| File | Why |
|---|---|
| `.github/agents/calc-auditor.agent.md` | hand-off to `confluence-migrator`; step 5: `sources[]`, move to `_done/` when last, screen rules never the auditor's |
| `.github/agents/confluence-migrator.agent.md` | step 1: classification from the content, one class or two joined by `+`, with the test for a formula part (how a number is computed, not a value the screen shows); step 2: the "no spec covers the capability" bullet (candidate line) replaces "create from the template"; step 1 and the hand-offs say whether a mixed page may move; step 6: the last agent moves the page, both directions; Never: create a spec |
| `.github/agents/architect.agent.md` | step 6 of "Legacy page": the page stays when the migrator's hand-off says so (candidate spec or context without a spec pending) |
| `scripts/migration-status.py` | `Candidates` read from each spec's Open questions, the `**Shaping - candidate spec**` line with the next free number, `shaping` in the summary; architecture pages listed once outside the contexts and excluded from their runs; regenerate `migration/all.md` after copying |
| `.github/skills/spec-lifecycle/SKILL.md` | "Which run am I in?": the candidate-spec and architecture-page cases; Planning and "Ready for the analyst" paragraphs |
| `.github/skills/spec-lifecycle/references/run-checklist.md` | Run 2: no spec created (candidate line), `_done/` only without a pending candidate, the architect hand-off item; Run 3: page cited and moved when the auditor is last, screen rules handed to the migrator |

### 43.2 Docs repository: single rows to merge

| File | Where | What |
|---|---|---|
| `.github/agents/migration-lead.agent.md` | procedure step 2, after the unassigned-pages bullet | new bullet: for every candidate spec the proposed ID and title, spec of its own or part of an existing one, the developer who confirms it; the confirmed row goes to the board before its Run 1 |
| `CONCEPT.md` | lifecycle item 2; the "ready for the analyst" sentence | "The migrator never creates a spec: a capability no spec covers becomes a `candidate spec:` open question, the lead and a developer confirm it, Run 1 writes it from the code and the page is rerun."; readiness adds "and no candidate spec is pending (architecture pages belong to `architect`, not to a context)" |
| `confluence-import/README.md` | Triage, part 3 "Target", after "a wrong guess sends facts into the less suitable spec" | "A page about a screen or modal that no spec covers yet gets no target and no new spec from the migrator: it leaves a `candidate spec:` open question, the board lists it as a shaping decision, and the spec is written from the code (Run 1) before the page is rerun." |
| `confluence-import/README.md` | Triage, part 1, the "Product or process?" paragraph | "...hands the formula part to the calc-auditor (or the architecture part to the architect); the last agent that takes the page moves it to `_done/`." |
| `CONCEPT.md` | agents table, row `calc-auditor`, "Hands off to" | add "`confluence-migrator` for the screen rules of a mixed legacy page" |

### 43.3 Playbook (read only)

Section 10, "Run 2, legacy pages" (last sentences) and "Architecture pages" (listed once, outside the contexts).
`MIGRATION-RUNBOOK.md` Step 5 has the candidate bullet.
