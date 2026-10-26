# Update Log

## 2026-10-26
* **Context pack: the UI flow survives the spec reduction.** A spec body above 200 lines or 60 % of the budget is
  reduced to key sections; the keep list lacked `UI flow`, so with the question budget of 200 a spec over 120 lines
  (P1-001, ADM-001) reached the analyst without the section a "what does the screen show or allow" question reads.
  `UI flow` is in the keep list; the skill and `pack-anatomy.md` name the sections kept.
* **Confluence migrator: targets from the catalogue, a page may touch several specs.** Step 2 found the target
  spec through the pack script's keyword matcher on the page title, so a page describing two contexts was merged
  into one spec (or into a new duplicate), and a context given in the message could act as a filter that dropped
  the other context's facts while the page moved to `_done/`. The migrator now reads `generated/catalogue.md`,
  names every spec the page touches, merges each fact into the spec of the context that owns the behaviour, sends
  a cross-context sequence to a flow or an Open question, cites the page in every spec touched, and moves the page
  once, only when every context it describes has a spec. Run 2 checklist, lifecycle row, CONCEPT, routing table.
* **Analyst: progressive disclosure inside the pack.** The procedure said "build one pack, read it top to bottom"
  for every input, so a question was answered after reading the change-request pack of the spec (CLI-001: 521
  lines) when the answer sat in one section of the calculation the glossary alias pointed at. A question now takes
  the narrowest subject (calculation, spec or flow; never a context), `--budget 200`, and the analyst reads the
  Subject and the section the question names, the truncated sections being pointers; a change request keeps the
  full pack. Analyst agent steps 1 and 2, `analyse-request` prompt, `task-context` skill, `AGENTS.md`,
  `CONCEPT.md`, routing table. Same day: when the section does not answer, the question's first escalation is a
  search of the documentation folders and one opened document, cited; the pack is rebuilt only for a structural
  or multi-subject question (analyst step 4, prompt step 2, the skill's escalation step 1).

## 2026-10-25
* **Context pack: the sanctioned code shape of a calculation is in the pack, by rule.** The `task-context` skill said
  a linked calculation comes "never with the Kotlin block", while `context-pack.py` carried the `# Computation` block
  inside Formula for a calculation linked from a spec and replaced it with a pointer when the calculation was the
  subject. Decision: keep the block (short, and the most precise statement of rounding and inclusive thresholds).
  Both branches now include it, demoted under the pack's headings; the skill, `pack-anatomy.md` and the
  investigation notes say so.
* **Database documentation: the ER diagram parses and `ALTER TABLE` foreign keys are relations.** The kit's
  `gen-db-docs.py` wrote a primary-and-foreign key column as `PK FK` (Mermaid wants `PK, FK`) and its migration
  reader knew only an inline `REFERENCES` and a `FOREIGN KEY` inside the `CREATE TABLE` body with plain names, so a
  key added by `ALTER TABLE ... ADD CONSTRAINT`, a schema-qualified or quoted name, a second `ADD COLUMN` in one
  statement and a composite key were missing from `schema.json`, the table pages and the diagram. The reader is now
  `scripts/docs/_migrations.py` (backend kit), shared with `gen-db-schema.py`; `generated/be/db/` and
  `generated/be/db-schema.md` re-collected (Harbor: same 21 tables and 18 relations, the two `PK, FK` lines the only
  diagram change); the `gen-graph.py` diagram fallback accepts a quoted composite label.

## 2026-10-24
* **Analyst: the documentation folders are free after the pack.** The pack was the only way into `features/`,
  `domain/` and the other documentation folders, so a neighbour spec meant a rebuilt pack. The analyst now opens or
  searches `features/`, `domain/`, `flows/`, `architecture/`, `contracts/`, `work-items/`, `test-design/`,
  `generated/` and the imported Confluence pages freely after the pack (never `raw-html/` or `_attachments/`); the
  pack stays mandatory as the recorded slice and as the only source of the graph neighbourhood and a merged slice.
  Other agents open the documentation files their procedure names; code access unchanged (steps 9 and 10).
  Analyst agent step 2, `task-context` skill, pack footer rule, `AGENTS.md`, `CONCEPT.md`, routing table.
* **Analyst: a free reading pass when a question still blocks.** The five map-located ranges of step 9 stopped the
  analyst wherever a context's documentation had not caught up. A question that still blocks the answer or the
  analysis after them now earns one free reading pass over `../backend` and `../frontend` (search, whole files, call
  chains; analyst agent step 10), for blocking questions only, never for "is this intended". Findings keep the step 9
  discipline (`code-read` evidence, unverified, `needs-spec-review`, an Open question in the spec), the files read
  are listed in the analysis document, and `coverage-matrix.py` gained the **answered from code** column (open
  question items citing `code-read`, `openQuestionsFromCode` in the JSON): the documentation gaps that cost analyst
  time. Prompt `analyse-request`, the `task-context` and `docs-analytics` skills, the analysis template, the pack
  footer rule and the routing table updated; spec-writer and calc-auditor unchanged.
* **Graph viewer: the `docs` community is selectable.** `graph.json` lists the code communities only; the spec and
  calculation nodes carry the community `docs`, which the viewer drew in the legend but left out of the dropdown, so
  the legend click did nothing and `--community docs` fell back to the whole graph. The dropdown now adds every
  community found on nodes; `.context/graph-viewer.html` regenerated.
* **Calculations: a source marker per Formula step and on the Conventions paragraph.** Pattern F applied to
  calculations: until a person verifies the document, every numbered step of the Formula step list and the
  Conventions paragraph end with `(source: code <sources-id>#<symbol>)` naming the function, property or constant
  that implements them (or the legacy / person / spec form); `okf-validate.py --strict` warns on a draft step or
  paragraph without one, with an unknown `sources[].id` or a code marker without symbol; a calculation tagged
  `proposed` is exempt. Applied to the five draft calculations (24 markers, symbols read from the calculator files:
  `coveredShare`, `build`, `totals`, `totalsOf`, `divideAsRatio`, `aggregate`, `valueRow`, `group`, `money`,
  `median`, `simulate`, `factorAt`, `apply`); the two verified ones and the proposed roll-up untouched. Template,
  calculations instructions, `calc-auditor` step 2 and the `calculation-spec` skill updated.
* **Calculations: `code_refs` are files, never line ranges.** The calculation template (`#L10-L80`, `URL#Lx-Ly`) and
  `calculations.instructions.md` ("optional `#Lx-Ly`") still allowed line ranges, so `calc-auditor` wrote them while
  the spec rule (conventions, "Provenance per rule") says a symbol, never a line. Template, instructions,
  `calc-auditor` step 2 and the `calculation-spec` skill now say: file only in `code_refs` and `sources[]`, the test
  method in a worked-example row, the function in an audit row; the `file:line` of the tags map is where to read.
* **Skeleton prompt: optional entry file.** `/spec-skeleton-from-graph <ctx> <ID> [entry file]`: a context whose
  entry layer holds one class per screen and no `<Prefix>Manager` gets one entry point on its `context:` node, right
  for the first spec only; the call now names the file of this spec's screen and the spec-writer reads it instead (one
  source file either way). Prompt, `spec-writer` step 3, `spec-lifecycle` table and Run 1 checklist updated; no
  script or spec changed.

## 2026-10-23
* **Spec prefix: 3 to 5 characters.** `.github/prompts/context-map-from-code.prompt.md` told the architect "2-3
  uppercase letters"; the validators accept `[A-Z][A-Z0-9]*` before the dash, so the prompt now says 3-5 uppercase
  letters or digits, one token (`TARIF`, never `TA-RIF`). No validator or spec changed.
* **Two spec rules: owned operations in `api[]`, a source marker per rule.** `features/conventions.md` gains
  "Owned versus called operations" (`api[]` lists only the operations the spec's context handles; a called operation
  of another context stays in the API / Events table with `owned by <SPEC-ID>`; consumers read `api[]` as scope) and
  "Provenance per rule" (until a person verifies the spec every rule ends with `(source: code <sources-id>#<symbol>)`,
  or the legacy / contract / person / spec form - a symbol, never a line range). `okf-validate.py --strict` warns on a
  draft rule without a marker. Applied: the 11 draft specs carry 68 markers (verified CLI-001 and SES-001 exempt);
  [PRS-001](/features/presentation/PRS-001.md) `api[]` emptied (frontend-only, every call owned elsewhere), its API
  table names the owners, BR-10 cites `PresentationLayout`; MKT-001 BR-3 cites the listener, STR-001 BR-7 the
  calculator, BR-8 defers to SES-001 BR-5. Agents and skills updated (spec-writer, confluence-migrator, doc-sync,
  write-feature-spec, run checklist, features instructions, AGENTS.md); catalogue and coverage matrix regenerated.
* **Frontmatter block lists no longer read across keys.** `scripts/_common.py` `get_list()`: the block form
  (`api:` followed by indented `- ` lines) used a DOTALL regex and returned every indented item of the keys below as
  well, so a spec with block-list `api`, `tables` and `calculations` had its calculation links inside `api[]` (packs
  listed them under Contracts as not found). One item per line now; the next top-level key ends the list. Harbor
  specs write these lists inline and were never affected; catalogue, graph and indexes unchanged.

## 2026-10-21
* **Checks once, at the end of a task, for what it changed.** Agents no longer validate after each edit: `AGENTS.md`
  (section Checks), the `okf` and `okf-validate` skills and the `analyst` agent (its Checks table) run the validators
  once, after the last edit, for the kind of file the task changed; a question, a pack or analytics runs none.
  `scripts/okf-validate.py` keeps checking the whole bundle and runs no git command; `--path` resolves links from the
  bundle root, and a past `stale_after` is listed as `stale` without failing a run (freshness, not conformance).
* **Page components; renders and uses edges (regenerated).** [generated/fe/components.md](/generated/fe/components.md)
  gains a Page components table: one row per component in a page folder with its page, props, purpose, where it is
  rendered (`file:line` of the JSX tag) and which of the frontend's hooks it calls. The frontend exporter
  (`gen-graph-fe.ts`) builds its TypeScript program from the repository's `tsconfig.json`, so `@/` imports resolve: the
  graph has 53 `renders` (was 3) and 62 `uses` (was 0) edges from the export, 852 edges in all (was 740), e.g. which
  modals each overview page renders and which hooks it uses.
* **Frontend exporter on TypeScript 7 (export regenerated, graph unchanged).** `gen-graph-fe.ts` now runs on
  TypeScript 7, the native compiler: the `typescript` package no longer exports `ts.createProgram`, so the script talks
  to the bundled compiler process through `typescript/unstable/sync` and reads nodes through `typescript/unstable/ast`.
  The process picks each file's project the way the language server does (the nearest `tsconfig.json` that includes
  it, references followed), so `@/` aliases resolve as before; the console line names the config(s) used. Harbor: the
  same 129 nodes and 267 edges (53 `renders`, 62 `uses`), written in sorted file order; `tsconfig.gen.json` compiles
  with `moduleResolution: bundler`, the frontend's `tsconfig.json` lost `baseUrl` (removed in TypeScript 7).

## 2026-10-20
* **Catalogue for free-text requests.** `scripts/gen-catalogue.py` writes [generated/catalogue.md](/generated/catalogue.md):
  one line per context (also code-only ones), flow, spec with aliases, calculation with parameters, API endpoint
  (also code-only ones), Kafka topic, table with owner, external service and glossary alias. An agent given a request
  that names no ID reads it first, picks the subjects itself and builds one pack per subject (analyst agent step 1,
  skill `task-context`); `collect-evidence.py --graph` rebuilds it, CI checks it with `--check`.
* **One context pack for several subjects; flows and contexts as subjects.** `scripts/context-pack.py --task` may
  be repeated (one pack, shared sections merged and deduplicated, budget +300 per extra subject); a flow
  (`flows/<name>.md`: body, the rules it cites per spec, graph impact of its code_refs) and a context
  (`context:<name>`: specs, endpoints, tables, calculations, topics, classes by layer, pages, integrations, proposed
  contracts - the overview for placing new work) are subjects; the free-text fallback applies glossary aliases and
  scores flows. Section markers: `.github/skills/task-context/references/pack-anatomy.md`. No budget by default
  (every item bounded on its own); `--budget N` caps a pack.
* **Request epics.** A request spanning several specs gets `work-items/<slug>.yml` (`request:`, `specs: [...]`, a
  story may cite rules of several specs) and the analysis document `work-items/<slug>.md` written first from
  `work-items/_analysis-template.md`; `validate-work-items.py` checks both shapes, `coverage-matrix.py` counts the
  stories for every spec they cite. Rule kept: nothing new without a (draft) rule.
* **Analyst procedure for free-text requests.** `analyst` works resolve (catalogue) -> gather (one pack) -> analyse
  (analysis document, reading confirmed by the analyst) -> produce (feature or request epic); question mode with
  citations; nothing new without a draft rule, contract proposal or calculation concept first. New prompt
  `analyse-request`; `test-designer`, `architect`, `tests-from-spec` and `hld-from-spec` accept a request slug.
* **Proposed rules; first request epics.** `features/conventions.md`: a rule for behaviour asked for but not built
  continues the numbering with the marker **proposed** (request `<slug>`). Acceptance run of the request flow:
  [quarterly-view-across-products](/work-items/quarterly-view-across-products.md) (analysis confirmed, epic of four
  stories, proposed rules BR-P1-001-12, BR-P2-001-10, BR-STR-001-9, BR-PRS-001-11, draft calculation
  [quarterly_rollup](/domain/calculations/quarterly_rollup.md), proposal `contracts/proposed/quarterly-view-across-products.openapi.yaml`);
  [premium-estimate-on-cover-chart](/work-items/premium-estimate-on-cover-chart.md) (analysis, stopped: COV-001 first).

## 2026-10-19
* **Confluence HTML export importer; four legacy pages imported.** `scripts/confluence-import.py` (standard library)
  turns a Confluence HTML space export kept under `confluence-import/raw-html/<section>/` into
  `confluence-import/<SPACE>/<section>/<slug>.md` pages with the quarantine header block, copies the images a page
  shows to `<SPACE>/_attachments/<slug>/`, rewrites the links between pages and regenerates the inventory of
  `confluence-import/README.md`; pages already under `_done/` are skipped, `--check` for CI. Imported (synthetic
  fixture, two page trees): `HARBOR/business/admin-parameters-page.md`, `HARBOR/business/cover-quote-rules.md`,
  `HARBOR/technical/kafka-topics.md`, `HARBOR/technical/deployment-notes.md` (`status: imported`, Run 2 due; listed
  in `migration/all.md`).

## 2026-10-15
* **Meetings prefix renamed `MTG` → `SES`.** [SES-001](/features/meetings/SES-001.md) (was `MTG-001`), rule IDs `BR-SES-001-n`, dataset `ses-session-snapshot`, `contexts.yml`, `docs-map.yml`, every citation in specs, flows, work items and the `@docs` tags of the meetings classes and hooks; generated maps, graph and boards regenerated.
* **Specs cut by screen and modal; product mirrors; two flows.** `features/conventions.md` gains the section
  "Shaping specs" (contexts follow the code, first spec = screen, modals with own rules = own spec, ownership by
  rule, product types as a dimension or a mirrored context, flows for cross-context behaviour, formulas as
  calculations, optional screenshots). [P1-001](/features/product1/P1-001.md) is now the screen only; its modal
  rules moved to [P1-002](/features/product1/P1-002.md) (modelled movements, former BR-5/6 withdrawn with pointers)
  and [P1-003](/features/product1/P1-003.md) (peer simulation, former BR-7; the 0.1-5.0 factor range became an
  open question because neither the contract nor the code enforces it). Product 2 documented as mirrors
  [P2-001](/features/product2/P2-001.md), [P2-002](/features/product2/P2-002.md), [P2-003](/features/product2/P2-003.md).
  New flows [meeting-journey](/flows/meeting-journey.md) and
  [session-inputs-recalculation](/flows/session-inputs-recalculation.md) (the stress test is not rerun
  automatically). Work items split accordingly (`P1-002.yml`, `P1-003.yml`); `docs-map.yml`, the context map,
  the glossary references, the calculations' `used_by` and the `@docs` tags of the validator, the peer service and
  the four modal hooks updated; generated maps, graph, indexes, coverage matrix and migration boards regenerated.

## 2026-10-14
* **Scripts ported from PowerShell to Python (standard library, 3.11+).** Every `scripts/*.py`, `scripts/hooks/guard-generated.py`
  and the code-repo generators (`scripts/docs/*.py`, `check-file-size.py`, `seed-local.py`, `apply-kit.py`) replace the former
  `.ps1` files one to one; flags are long options (`--check`, `--strict`, `--task`). Hooks, CI workflows and all documentation
  updated; `python3` in CI and on macOS, `python` on Windows. Generated maps, graph, indexes and analytics regenerated with the
  new scripts (same content; tables now sort case-insensitively by a rule inside the scripts, no locale involved).

## 2026-10-12
* **audited horizon_totals: 13 findings.** Re-audit of [horizon_totals](/domain/calculations/horizon_totals.md) against `ProjectionAggregator` and `ProjectionAggregatorTest`: 7 MATCH, 4 DOC-STALE, 2 UNDOCUMENTED, 0 CODE-SUSPECT. Corrects the Run 3 audit, which reported 6 MATCH: worked example 2 had a hand-computed share (0.3354) that the test does not assert, and the rows lacked test method names. Both are fixed by keeping only values the test asserts. Still open: share rounding (per key, no remainder correction), the `UNKNOWN` key, and the city-filter wording (Q1-Q3). Status stays draft. Inherited by [P1-001](/features/product1/P1-001.md) (BR-P1-001-11).
* **product1: Run 2 and Run 3 done, Run 4 due.** Legacy page "Product 1 overview tables" merged into [P1-001](/features/product1/P1-001.md) (4 confirmations, 2 conflicts → open questions; page moved to `_done/`). Audits: [monthly_projection](/domain/calculations/monthly_projection.md) 11 items (6 MATCH, 3 DOC-STALE corrected, 1 UNDOCUMENTED, 1 CODE-SUSPECT → status draft, Q1-Q2), [horizon_totals](/domain/calculations/horizon_totals.md) 6 MATCH. New concept [peer_benchmark_simulation](/domain/calculations/peer_benchmark_simulation.md) (draft) with executor `PeerBenchmarkTest` added to the backend (was code only). P1-001 and `monthly_projection` are drafts until the owner answers the open questions and re-verifies.
* **Horizon totals added.** New calculation [horizon_totals](/domain/calculations/horizon_totals.md) (draft, Run 1 from the aggregator and its test): each projection table summed over the horizon per key with share of value, returned as `tables.totals` and shown as three separate tables under the monthly ones ([P1-001](/features/product1/P1-001.md) BR-P1-001-11, mirrored by [PRS-001](/features/presentation/PRS-001.md)); glossary entry *Projection* extended.
* **Presentation context added (FE-only).** [PRS-001](/features/presentation/PRS-001.md) (draft, Run 1 from `feature:presentation` and the channel module) and the first flow document [client-presentation](/flows/client-presentation.md) (`type: Flow`, new folder `flows/`); `contexts.yml` gained `presentation`, the FE maps a `components.md` (shared component library) and a Channels column (BroadcastChannel), the graph `channel:` and `shared-ui` `component:` nodes. [SES-001](/features/meetings/SES-001.md): meetings list split into client / preparation pages (change log).

## 2026-10-09
* **Spec lifecycle and migration planning added.** Skill `spec-lifecycle` (run-by-run lifecycle + review checklist),
  agent `migration-lead` with prompt `migration-plan`, script `scripts/migration-status.py`; first plan
  [migration/all.md](/migration/all.md): 16 runs due, 1 of 10 contexts ready for the analyst.
* **Bundle rebuilt for the Harbor simulated domain.** Concepts: [CLI-001](/features/clients/CLI-001.md),
  [SES-001](/features/meetings/SES-001.md), [P1-001](/features/product1/P1-001.md),
  [STR-001](/features/stress/STR-001.md), [MKT-001](/features/market/MKT-001.md), [RPT-001](/features/reports/RPT-001.md);
  calculations [client_role_classification](/domain/calculations/client_role_classification.md),
  [monthly_projection](/domain/calculations/monthly_projection.md),
  [stress_test_monthly](/domain/calculations/stress_test_monthly.md),
  [cover_ratio](/domain/calculations/cover_ratio.md) (draft), [scenario_price_path](/domain/calculations/scenario_price_path.md) (draft);
  [Glossary](/domain/glossary.md), [Context map](/domain/context-map.md), [Architecture overview](/architecture/overview.md),
  [Integrations map](/architecture/integrations.md), ADR-0001..0003. Legacy pages quarantined under
  `confluence-import/HARBOR/`; work items `P1-001.yml`; test design `STR-001.feature` + fixture.
* **Backend restructured to layered layout; docs paths and graph contexts updated.** `harbor-backend` is now
  `core` (package-by-layer) + `kafka-client` + `init_docker_compose`; specs, calculations, `docs-map.yml`, agents and
  skills point at `harbor-core/src/main/kotlin/com/acme/harbor/<layer>/` paths, contexts come from `contexts.yml`
  ([ADR-0004](/architecture/adr/0004-layered-backend-and-context-prefixes.md)), the BE map `components.md` was added
  and the per-module graph nodes became `context:<x>` nodes.
