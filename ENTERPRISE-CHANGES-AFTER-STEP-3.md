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
