# Update Log

## 2026-10-29
* **Six context steps.** The two code steps of the task-context skill (through the maps, then freely) merged into one
  step 6 "Read code, last" with the maps-first order and the free search as its sub-rules; same evidence rules, same
  Open question, same coverage-matrix column. Analyst, prompt, template, AGENTS, CONCEPT, instructions and the guides
  say six steps; the other agents' "steps 1-5 / 1-6" references are unchanged.
* **A changed Confluence page that is already migrated is re-imported.** The importer only flagged a page whose
  export was newer than its copy under `_done/` (`EXPORT NEWER`), so the new text had no readable copy and the
  migrator could not rerun on it. `confluence-import.py` now writes such a page again as a fresh page in its section
  folder (`status: imported`, `supersedes_done:` naming the migrated copy, `supersedes_done_modified:` its date; the
  copy untouched; inventory state and console `re-imported, migrated copy <path>`; a second run changes nothing; an
  unparsed date never counts as newer). `legacy-done.py` moves the fresh page over the copy it supersedes: the old
  file removed, the new one in its place under `_done/<section>/` (a changed title changes the path and the pages
  under `_done/` that linked the old copy are re-pointed), the copy's `superseded_by` entries carried forward and
  merged with `--into` (optional then), `earlier_migration:` with the copy's dates; one copy per page, git keeps the
  replaced one. Tested on the admin parameters page (migrated, re-exported with a later date, re-imported, moved
  with and without `--into`, re-exported with a new title, moved again; tree restored). Import README, scripts
  README (a `legacy-done.py` row added), runbook steps 3 and 5, import instructions, migrator input, CONCEPT rows.
* **One context procedure in the task-context skill; the pack points instead of copying.** The analyst had two
  procedures (a budgeted pack for a question, a full pack for a change request) and the code-reading rules as its
  steps 9 and 10; the pack copied every linked calculation and flow, so a request over several subjects ran to 1900
  lines, and a rebuilt pack had no map of what was new. `context-pack.py` now writes a `## Contents` with the line
  range of every section and part, keeps the subject whole and the computed sections (graph, contracts, tables,
  merged slice), turns linked calculations, flows and legacy pages into pointers (path, badge, description; a flow's
  steps that name the subject), demotes embedded headings so `## ` is always a pack section, and records what it
  pointed at in the footer (P1-001: 979 to 531 lines). The procedure moved into `.github/skills/task-context/SKILL.md`
  as seven steps, the same for a question and a change request - catalogue, one pack, badges, the pack and its
  pointers, the documentation and the graph freely, code through the maps, code freely - with a table of how far each
  agent goes; the agents reference the skill and keep their own procedure. `CONCEPT.md` describes the pack as it is
  now and why a pack and not a search.
* **A request that changes before the code has it.** The analyst had no step for a request whose text changed after
  the proposed rules were written (a re-imported Confluence page, a changed ask), and the conventions named `doc-sync`
  as the one who withdraws a proposed rule without saying when. Now: the same request, rerun under the same slug
  (analyst step 4, `analyse-request` step 4) - pack rebuilt, `work-items/<slug>.md` rewritten in place, Reading
  confirmed again, `spec-writer` adjusts the proposed rules of the same spec (changed: same ID and marker; new: next
  number; no longer asked for: **withdrawn** (request `<slug>`), text kept, never deleted or renumbered), the stories
  that cited them re-cut; a request dropped altogether sets the analysis to `status: superseded` and `doc-sync` (step
  4) or the owner withdraws its rules. "Proposed rules" in `features/conventions.md`; import README (a page that
  changes while still in place is rewritten by the next import; rerun the step it is in); runbook step 5 and playbook
  section 12 (a code change needs nothing by hand: `doc-sync` on the next snapshot).
* **A candidate spec not yet in code, and no renumbering.** The migrator's candidate path assumed the capability a
  legacy page describes exists in code and will get a Run 1; a page describing a screen still to be built (written in
  Confluence first) had no path, and the board pointed at `/spec-skeleton-from-graph`, which has no graph nodes for
  it. The candidate line now says `in code | not in code` (from the catalogue and the generated maps); `in code`
  keeps Run 1, `not in code` is a request: `/analyse-request` with the page as the request text, `spec-writer`
  drafts the spec with every rule **proposed** and the legacy citation, then the page is rerun. Either way the spec
  takes the **next free number**: the existing specs of the context are never renumbered (IDs never reused, rule IDs
  cited by flows, calculations, stories and Gherkin outside the repo); a main screen that arrives late is marked by
  `aliases`, `tags` and the manual block of `index.md`, not by `-001`. Written as "Shaping specs" point 9 in
  `features/conventions.md`; migrator step 2 and Never list, analyst step 6, Run 2 checklist, import README,
  CONCEPT; `migration-status.py` reads the marker and prints the matching run (tested on two temporary candidate
  lines in `P1-001`, restored), board regenerated.

## 2026-10-28
* **A processed legacy page is moved by a script.** `confluence-migrator`, `architect` and `calc-auditor` each moved
  a page to a flat `_done/` by hand, set `status` themselves, wrote `superseded_by` only for a contradicting page
  (one page had it) and left the image links to break one level up. `scripts/legacy-done.py <page> --into <concept>
  [--into ...]` now does the move: `_done/<section>/` from the page header (the REST export's root pages stay at
  `_done/`), `status`, `migrated` or `obsolete` with `reason`, `superseded_by` naming every concept the page went into
  (the backward link; `sources[]` is the forward one), every relative link re-pointed (`../_attachments/` one level
  deeper, a link to a page already under `_done/` follows it, pages under `_done/` that linked the moved page are
  re-pointed too), no git call. Tested on two Harbor pages and restored. The migrator also puts the page title into
  the `aliases` of every spec it touched. Agents' move steps, Run 2 and Run 3 checklists, import README (layout,
  rule 3, after migration), import instructions, AGENTS commands, CONCEPT scripts table.
* **The Kafka payload schemas reach the docs repo.** The collector copied the AsyncAPI document but never the Avro
  and JSON Schema files of `kafka-client/src/main/resources`; `generated/be/events.md` linked them by their backend
  path, which exists nowhere here, and a backend without an AsyncAPI document had the payload fields nowhere.
  `gen-events.py` (backend kit) now ends with a "Payload schemas" section: every Avro record and JSON Schema under
  `kafka.schema_dirs` with its fields (name, type, required, doc) as the file declares them. `collect-evidence.py`
  copies these files to `generated/asyncapi/schemas/<path relative to the folder>` (`avro/`, `json_<service>/`),
  rejects a file that is not JSON, re-points the schema paths of `events.md` to the copies; `gen-catalogue.py`
  reads only the topic table of `events.md` (the field tables counted as topics); the context pack lists each
  topic of the subject with its payload type, schema file and field table. Agent texts, instructions, skills and
  the integrations prompt name `generated/asyncapi/schemas/` next to the AsyncAPI document.

## 2026-10-27
* **Legacy architecture pages reach the architect.** The triage table and the runbook sent architecture, decision
  and process pages to `architect`, but the architect had no procedure for a legacy page, the migrator handed off
  only formula pages, the runbook also listed these pages under the migrator, and the board offered
  `@confluence-migrator` for every page without a context. The architect has a "Legacy page" task (target by
  content: overview prose, `manual` rows of the integration map, a draft ADR or a document; `gen` rows never edited,
  differences as conflicts; run after the integration map refresh, not after the specs), the migrator hands these
  pages off, and `migration-status.py` lists pages whose title reads as architecture under "Architecture pages" with
  the `@architect` command (Harbor: `deployment-notes`, `kafka-topics`). Same day, two corrections: an
  architecture page is listed once, outside the contexts' runs, and no longer counts as a context's Run 2 or
  blocks its readiness; and the page is moved by the last agent that takes it in either hand-off direction.
* **The migrator never creates a spec.** Step 2 still said "no target -> create from the template (or hand to
  `spec-writer`)", against the lifecycle rule that a spec starts from the code and never from a legacy page, and
  against the shaping decision the lead takes with a developer. A page about a capability no spec covers now
  leaves `- [ ] candidate spec: <title> (legacy conf-<slug>; owner: migration lead) - ...` under the primary spec's
  Open questions; `migration-status.py` lists it as a shaping decision with the next free number, the lead confirms
  it, Run 1 writes it from the code, the page is rerun. Run 2 checklist, lifecycle skill ("Which run am I in?",
  "Ready for the analyst"), migration-lead step 2, CONCEPT, import README triage. A mixed page
  (`feature-spec + architecture`) whose feature part left a candidate stays out of `_done/`: the migrator's
  hand-off says whether the page may move, the architect's step 6 respects it. The same for a
  `feature-spec + calculation` page: the migrator merges the screen rules (a threshold links the concept, never
  the value) and hands the formula part on; `calc-auditor` cites the page in the concept, moves it when it is the
  last agent, and hands the screen rules of a page that reached it first to the migrator. Step 1 of the migrator
  says the classification comes from the content, one class or two joined by `+`, and what counts as a formula
  part (how a number is computed, not a value the screen shows).

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
