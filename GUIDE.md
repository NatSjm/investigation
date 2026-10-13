# Guide: what this workspace is, how to run it, how the agents work, and how to build it for your real project

Read this first. It links to the deeper documents instead of repeating them:
[README.md](README.md) (layout), [BLUEPRINT.md](BLUEPRINT.md) (names of the simulated domain),
[INVESTIGATION.md](INVESTIGATION.md) (why these choices), [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) (rollout steps
with estimates), [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md) (Confluence -> docs), [EXTERNAL-PATTERNS.md](EXTERNAL-PATTERNS.md).

---

## Part 1 - What this is

A rehearsal of a way of working, built on a simulated business ("Harbor": client meetings, Product 1 and Product 2
moving between country pairs, cover, market scenarios, stress tests, reports, admin). It contains three simulated
repositories and a kit:

| Folder | Plays | Contains |
|---|---|---|
| `backend/` | the real Kotlin/Spring backend | layered `core` (`harbor/<layer>/`), `kafka_client`, OpenAPI contract, migrations, calculations in `utils/` with tests, and the applied kit |
| `frontend/` | the real React frontend | one folder per feature, a shared component library (`src/shared`), the client presentation window synchronised over `BroadcastChannel`, generated API client, routes, and the applied kit |
| `docs-repo/` | the documentation repository agents work from | specs, calculations, glossary, architecture, generated maps and graph, Copilot agents / skills / prompts / hooks, PowerShell scripts |
| `code-repo-kit/` | what gets copied into each code repository | `AGENTS.md`, instructions, map generators, CI, `apply-kit.ps1` |

Both applications also run locally (Step 0 below); the documentation pipeline (Steps 1-9) needs neither to be running.

The idea in three sentences. The code repositories generate small maps of themselves (classes, endpoints, topics,
tables, routes); the docs repo collects them, together with the contracts, as one versioned snapshot (one collector,
one pull request, a manifest of source commits). The docs repo joins the maps into an architectural graph and holds
the human-owned specs, calculations and glossary with trust metadata. For any task a script builds a **context pack**
(the spec, its calculations, the graph neighbourhood, the contracts, the tables) and the analyst agent reads only that.

---

## Part 2 - Run it in 20 minutes

Prerequisites: PowerShell 7 (`pwsh`), Git, VS Code with GitHub Copilot (agent mode). Nothing else. Open
`harbor.code-workspace` in VS Code, then a PowerShell terminal at `C:\projects\investigation`.

**Step 0 - Run the applications (optional, needs JDK 21, Docker, Node; Maven unpacked under `C:projects	ools`, no system install):**

```powershell
docker compose -f backendinit_docker_composedocker-compose.yml up -d        # Postgres, Kafka, WireMock (external services)
cd backend; C:projects	oolspache-maven-3.9.9inmvn -B -DskipTests package   # 27 unit tests with `mvn test`
$env:HARBOR_CLIENT_REGISTRY_URL='http://localhost:8089'; $env:HARBOR_MARKET_DATA_URL='http://localhost:8089'
$env:HARBOR_COVER_PROVIDER_URL='http://localhost:8089'; $env:HARBOR_DOCUMENT_SERVICE_URL='http://localhost:8089'; $env:HARBOR_FILE_EXCHANGE_URL='http://localhost:8089'
java -jar core	argetre-1.0.0-SNAPSHOT.jar                                     # http://localhost:8080/api/v1, Flyway applies V1..V9
cd ..rontend; npm install; npm run generate:api; npm run dev                      # http://localhost:5173, proxies /api to 8080
```
Search a client, open its overview, create a session; `/meetings/client` and `/meetings/preparation` list the sessions; inside a
session "Open client screen" opens `/present/<id>`, the client-facing window synchronised over `BroadcastChannel`.

**Step 1 - Generate the backend maps** (regex scanners, no build):

```powershell
.\code-repo-kit\be\scripts\docs\gen-all.ps1 -Root .\backend
```
Look at `backend\docs\_generated\`: `codebase-map.md` (modules, layers), `components.md` (one row per class with
dependencies and tables), `api-index.md` (34 operations from the contract joined to controllers), `events.md`,
`db-schema.md`, `jobs.md`, `docs-tags.md` (`@docs` tags -> file:line). Add `-Check` to see the CI freshness gate.

**Step 2 - Generate the frontend maps**:

```powershell
.\code-repo-kit\fe\scripts\docs\gen-all.ps1 -Root .\frontend
```
Look at `frontend\docs\_generated\`: features, routes, types, tags.

**Step 3 - Collect into the docs repo** (locally against the sibling checkouts; in reality the docs repo's own
workflow `collect-evidence.yml` does this nightly or on demand and opens one pull request per snapshot):

```powershell
.\docs-repo\scripts\collect-evidence.ps1          # add -Generate to run both gen-all first, -Graph to rebuild graph + indexes
```
Look at `docs-repo\generated\be`, `fe`, `openapi\backend.yaml`, `openapi\external\`, `asyncapi\backend.yaml`, and
`generated\manifest.yml`: which backend and frontend commits the snapshot describes, with a hash per file. The collector
validates the candidate before writing (frontmatter on every map, OpenAPI/AsyncAPI headers, no unresolved external
`$ref`), deletes files the code no longer produces, and writes nothing when nothing changed. Run it twice: the second
run reports "no change". `publish-local.ps1` is the old name and still works.

**Step 4 - Build the architectural graph**:

```powershell
.\docs-repo\scripts\gen-graph.ps1
```
Look at `docs-repo\generated\graph\REPO_MAP.md` (ranked map, one community per bounded context, the
"Spec coverage" list at the end with `code only` entries) and one `generated\graph\product1.md`.
Communities come from `docs-repo\contexts.yml`: a backend class belongs to the context of its name prefix.

**Step 5 - Indexes and validation**:

```powershell
.\docs-repo\scripts\build-index.ps1
.\docs-repo\scripts\okf-validate.ps1 -Strict
.\docs-repo\scripts\validate-frontmatter.ps1
```
Look at `docs-repo\index.md` and `docs-repo\features\index.md`: one line per concept with a trust badge
(human-reviewed / machine-confirmed / unverified / STALE). Every concept has YAML frontmatter; folders use `index.md`.

**Step 6 - Build a context pack** (what an agent reads for a task):

```powershell
.\docs-repo\scripts\context-pack.ps1 -Task P1-001
code .\docs-repo\.context\p1-001.md
```
Up to 500 lines: subject and badge, the spec body, its calculations with worked examples, the graph neighbourhood with
`file:line`, the contract operations, the tables, related work items and tests, legacy pages. Try a free-text task:
`-Task "transport mode toggle on the stress table"`.

**Step 7 - Ask the graph a question**:

```powershell
.\docs-repo\scripts\graph-query.ps1 -Node spec:STR-001 -Depth 2
.\docs-repo\scripts\graph-query.ps1 -Files be/core/src/main/kotlin/harbor/utils/StressTestCalculator.kt
```
The second form answers "which specs are affected if this file changes".

**Step 8 - Analytics and the migration board**:

```powershell
.\docs-repo\scripts\coverage-matrix.ps1        # business rule -> story -> test scenario coverage
.\docs-repo\scripts\migration-status.ps1 -Scope all
```
Look at `generated\analytics\coverage-matrix.md` and `docs-repo\migration\all.md` (which documentation runs are still
due per context, with the command for each).

**Step 9 - Now with Copilot.** In VS Code, Copilot Chat, agent mode, with the `harbor-docs` folder as the workspace
root. Try, in this order:

| Type | What happens |
|---|---|
| `/context-pack P1-001` | builds the pack and summarises it |
| `@analyst /jira-from-spec STR-001` | analyst reads the pack, writes `work-items/STR-001.yml` (epic, stories, subtasks, Gherkin criteria citing BR-IDs), warns that STR-001 is a draft |
| `/spec-skeleton-from-graph product2 P2-001` | spec-writer creates `features/product2/P2-001.md` from the graph and the manager file, status draft |
| `/audit-calculation stress_test_monthly` | calc-auditor compares the concept and the legacy Confluence page with the calculator and its unit test; the legacy page is deliberately outdated |
| `/coverage-report` | analyst answers from the coverage matrix and index badges |
| `/migration-plan all` | migration-lead refreshes the board and adds order and blockers |

After each run the `agentStop` hook validates the bundle. Edits under `generated/` are blocked by a `preToolUse` hook.

---

## Part 3 - The cast

### Agents (`docs-repo/.github/agents/`)

| Agent | Job | Input | Output | Opens source code? |
|---|---|---|---|---|
| `analyst` | Jira-ready epic / stories / subtasks with Gherkin criteria; documentation analytics | spec ID, calculation, graph node, free text, analytics question | `work-items/<ID>.yml`, answers from the coverage matrix | only a `file:line` the pack names, when blocked |
| `spec-writer` | create or refresh a feature spec | spec ID + context | `features/<ctx>/<ID>.md`, `docs-map.yml` | the context's manager file only |
| `confluence-migrator` | merge one legacy page into the right concept | `confluence-import/<SPACE>/<page>.md` | merged spec, glossary terms, page moved to `_done/` | no |
| `calc-auditor` | verify a calculation concept or formula page against code | calculation name, spec ID or page | `## Audit <date>` table, open questions | calculator class + its unit test, nothing else |
| `doc-sync` | keep specs in sync with code changes | changed paths or a generated diff | spec change-log rows, `last_verified` | narrow ranges only when the contract diff cannot explain behaviour |
| `test-designer` | Gherkin scenarios and synthetic fixtures | spec ID or work items | `test-design/features/<ID>.feature`, fixtures | no |
| `architect` | HLD, ADRs, integration map | spec ID or decision | `architecture/hld/<ID>.md`, `adr/NNNN-*.md` | never |
| `impact-analyst` | blast radius of a change | file paths or a node | checklist across BE / FE / docs | no (graph only) |
| `migration-lead` | plan and track the documentation migration | context, space key or `all` | `migration/<scope>.md` | no |

### Skills (`docs-repo/.github/skills/`, loaded by description when relevant)

| Skill | Teaches |
|---|---|
| `task-context` | build and consume a context pack; what to do when it is not enough |
| `spec-lifecycle` | the four runs of writing one spec, who owns which, review checklist |
| `write-feature-spec` | structure, numbering, source priority (cheapest source first) |
| `calculation-spec` | formula + parameters + worked examples + sanctioned code shape |
| `legacy-page-audit` | claims table: MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED |
| `code-graph` | answer "what is affected / where is it" from the graph; subtask mapping per node kind |
| `jira-work-items` | slicing heuristics, estimates, acceptance criteria conventions |
| `gherkin-test-design` | step vocabulary, coverage checklist |
| `docs-analytics` | answer coverage / freshness / status questions from the bundle |
| `okf`, `okf-validate`, `okf-visualize` | the knowledge format: frontmatter, provenance, trust, indexes |

### Prompts (`/name` in Copilot Chat)

`context-pack`, `jira-from-spec`, `tests-from-spec`, `hld-from-spec`, `impact-from-graph`, `spec-from-code`,
`spec-skeleton-from-graph`, `audit-calculation`, `coverage-report`, `migration-plan`, `okf-produce`, `okf-validate`,
`translate-for-publish`.

### Scripts (`docs-repo/scripts/`, PowerShell 7, no modules)

`context-pack`, `graph-query`, `gen-graph`, `build-index`, `okf-validate`, `validate-frontmatter`,
`validate-work-items`, `coverage-matrix`, `map-paths`, `check-freshness`, `collect-evidence` (`publish-local` is its old name), `migration-status`,
`hooks/guard-generated`. Stubs that describe the intended integration: `jira-push`, `confluence-export`,
`confluence-publish`, `push-to-tests-repo`. Table with purposes: `docs-repo/scripts/README.md`.

### Code repositories (`code-repo-kit/be`, `fe`)

`AGENTS.md` (read order: map -> manager or barrel -> one range), `.github/instructions/*.instructions.md`
(path-scoped rules: contract-first API, calculations, Kafka, migrations, tests, layers), agents `code-reader`,
`impact-analyst` and `docs-tagger`, prompts `/explain-module`, `/find-spec-code`, `/add-endpoint`, `/tag-docs`, the generators
and `tag-candidates.ps1` under `scripts/docs/`, an `agentStop` hook that runs `gen-all.ps1 -Check`, CI `docs-maps.yml` (freshness gate on PR
only; publication is the docs repo's collector), `copilot-setup-steps.yml` for the cloud coding agent.

---

## Part 4 - The flows

### 4.1 Preparing a code repository (once)

1. `apply-kit.ps1 -Flavour be -Target <repo>` (and `fe`).
2. Add `@docs <SPEC-ID>` to every manager KDoc and `@docs <calculation_name>` to every calculation in `utils/` (FE: `@module` +
   `@docs` on the barrel, types file and hooks). By hand, or with the `docs-tagger` agent: `scripts/docs/tag-candidates.ps1`
   lists every candidate with its current tag, the proposed ID from `contexts.yml` and a status (`tagged / PROPOSE / REVIEW /
   BLOCKED`); `/tag-docs <context|all>` then writes the comment lines, one PR per context, and a person reviews the table.
   Only `contexts.yml` must exist first; the spec files come later.
3. Run `gen-all.ps1`; read the maps; fix the generator where the real code differs from the simulated one.
4. Enable the CI workflow: on PR, `gen-all.ps1 -Check` + file-size cap. Nothing on main: the docs repo pulls the maps and
   contracts with its collector, so the code repo needs no docs-repo credentials.
5. Content exclusion in the GitHub repo settings from `shared/copilot-content-exclusion.yml`.

### 4.2 Writing documentation (per spec, run by run)

| Run | Who | Command | Result |
|---|---|---|---|
| 1 Skeleton | `spec-writer` | `/spec-skeleton-from-graph <ctx> <ID>` | draft spec from graph + manager, open questions listed |
| 2 Legacy merge | `confluence-migrator` | `@confluence-migrator confluence-import/<SPACE>/<page>.md` | new facts merged, conflicts marked, page moved to `_done/` |
| 3 Calculation | `calc-auditor` | handoff or `/audit-calculation <name>` | audit table, open questions |
| 4 Owner decision | a person | edit | `verified.by`, `stale_after`, status stable |
| ongoing | `doc-sync` | on generated-diff PRs | change-log rows, `last_verified` |

One run, one human review of the diff, one commit. `migration/all.md` lists what is still due. Details:
[MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md) and `docs-repo/features/conventions.md`, "Lifecycle of one spec".

### 4.3 Analytics (what the analyst agent does, from the pack only)

Example task: "add a transport-mode toggle to the stress table".

1. `context-pack.ps1 -Task "transport mode toggle on the stress table"` resolves to STR-001 and builds the pack
   (spec with badge *draft*, `stress_test_monthly` with worked examples, graph: `StressController`, `StressManager`,
   `StressTestCalculator`, table `stress_test_result`, FE `StressTestPage`, contract `POST /session/stress-test`).
2. `@analyst /jira-from-spec STR-001`: one epic, 2-8 vertical stories citing `BR-STR-001-n`, subtasks per graph node
   kind (`[BE]` endpoint, `[DB]` table, `[FE]` component, `[INT]` topic, calculator + unit test), estimates, questions.
   Because the spec is a draft, stories are labelled `needs-spec-review`. Output `work-items/STR-001.yml`, validated.
3. Handoff to `test-designer`: `test-design/features/STR-001.feature` + synthetic fixture, scenario names aligned to stories.
4. Handoff to `architect` for an HLD if the change crosses contexts; `impact-analyst` for the blast radius.
5. `coverage-matrix.ps1` shows BR -> story -> scenario coverage; `/coverage-report` answers status questions.
6. Stubs `jira-push.ps1` and `push-to-tests-repo.ps1` describe the hand-over to Jira and the tests repository.

The analyst never searches the repository. If the pack is not enough it escalates in a fixed order (task-context
skill, "When the pack is not enough") and ends with an open question in the spec instead of a guess.

---

## Part 5 - Building the docs repo from zero for your real project

Order matters: code maps first, because every document is verified against them. Estimates are per person.
The full plan with risks is [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md); this is the checklist.

### Day 0 - Decide (one meeting)
- The **bounded contexts** of your application and, for each, the spec prefix, the FE feature folder and the BE
  class-name prefixes. This becomes `contexts.yml` and is the single most important decision.
- Who **owns** each context (the person who will verify specs).
- The **first pilot context**: medium size, has a calculation, has a Confluence page that is probably outdated.
- Repository names and the branch policy for the docs repo (PRs, draft PRs from automation, no auto-merge).

### Day 1 - Create the docs repository (half a day)
1. New repository; copy from `docs-repo/` everything **except** the simulated content: keep `AGENTS.md`, `README.md`,
   `.github/**`, `scripts/**`, `features/_template.md`, `features/conventions.md`, `domain/calculations/_template.md`,
   `architecture/adr/template.md`, `architecture/adr/0001-docs-as-code.md`, `architecture/adr/0002-openapi-first-contracts.md`
   (adapt), `work-items/_schema.yml`, `work-items/README.md`, `test-design/README.md`, `confluence-import/README.md`,
   `third-party/**`, `.markdownlint-cli2.yaml`, `.gitignore`.
   Delete: `features/<ctx>/*.md`, `domain/calculations/*.md` except the template, `domain/glossary.md` content (keep the
   header and table head), `architecture/overview.md`, `integrations.md`, ADR-0003/0004 (write your own), `generated/**`,
   `confluence-import/HARBOR/`, `work-items/*.yml`, `test-design/features/*`, `test-design/fixtures/*`, `migration/`, `.context/`.
2. Replace the simulated names. Search the copied files for `harbor`, `Harbor`, the context names, the spec prefixes, the
   header name `X-Harbor-Session`, the topic prefix `harbor.`, the external service names, and the paths
   `core/src/main/kotlin/harbor/`; replace with yours. [BLUEPRINT.md](BLUEPRINT.md) lists every name that was chosen.
3. Write `contexts.yml` from Day 0. Write `docs-map.yml` with one mapping per context (`specs: []` for now).
4. Commit. Run `okf-validate.ps1 -Strict` and `build-index.ps1`: the empty bundle must validate.

### Day 2-3 - Prepare the code repositories (one day each, no behaviour change)
1. `apply-kit.ps1 -Flavour be -Target <backend>`; same for `fe`. Review the copied `AGENTS.md` and instructions, replace
   the simulated names and paths, delete rules that do not apply.
2. Run `scripts/docs/gen-all.ps1`. Expect the generators to miss things the simulated code did not have (other
   annotations, Java files, a second base package, non-Flyway migrations). Fix the regexes in the generators; they are
   short and documented. The acceptance test: `components.md` lists every manager, `api-index.md` has no
   `_not implemented_` row that is actually implemented, `db-schema.md` has every table.
3. Add `@docs <SPEC-ID>` to every manager and `@docs <calculation_name>` to every calculation. Use the prefixes from
   `contexts.yml`; the IDs do not need a spec yet.
4. Enable `docs-maps.yml` in CI as warn-only; switch to blocking after two sprints. There is no publish job in the code
   repos: the docs repo's `collect-evidence.yml` (one read token for the code repos) pulls maps and contracts and opens
   one PR per snapshot. Until it runs, use `collect-evidence.ps1 -Backend <path> -Frontend <path>` from the docs repo.
5. Content exclusion in GitHub settings; `check-file-size.ps1 -WriteBaseline`.

### Day 4 - First graph (half a day)
1. In the docs repo: `collect-evidence.ps1 -Generate -Graph` (or merge the first collector PR); it runs the generators,
   validates the snapshot, writes `generated/manifest.yml`, then `gen-graph.ps1` and `build-index.ps1`.
2. Read `generated/graph/REPO_MAP.md`. Iterate `contexts.yml` until the `shared` community holds only true helpers
   and every context has a manager as entry point. Every community is a future spec; `code only` is your backlog.
3. Seed `domain/glossary.md` with the vocabulary of the contracts and entities; leave the Aliases column for the
   Confluence wording.

### Week 2 - Pilot context end to end
1. `/spec-skeleton-from-graph <ctx> <PFX>-001` (Run 1). Review the draft with the owner for 15 minutes.
2. Export the Confluence pages of the context (space export to HTML; importer per [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md)),
   triage them in the inventory table, then `@confluence-migrator <page>` one page per run (Run 2).
3. `/audit-calculation <name>` for each calculation of the context (Run 3). Expect findings; that is the value.
4. Owner decides the open questions, adds `verified.by` (Run 4). The index badge turns *human-reviewed*.
5. `context-pack.ps1 -Task <PFX>-001`: the pack must fit the budget and contain spec, calculations, graph,
   contracts, tables. Then `@analyst /jira-from-spec <PFX>-001` and `/tests-from-spec`. Compare the stories with what a
   human analyst would have written; record the differences, that is your measurement baseline.
6. Enable the hooks (`.github/hooks/docs-quality.json`) and the docs CI (`.github/workflows/docs-quality.yml`).

### Weeks 3-8 - Scale out
1. `/migration-plan all`; process contexts in the order the lead proposes. Run 1 for all remaining contexts can be
   batched through the Copilot coding agent, one issue per context. Runs 2-4 stay interactive.
2. Flip the freshness gate to blocking. From now on a PR that touches a mapped path must bump `last_verified` or carry
   `docs-not-affected`; `doc-sync` handles the generated-diff PRs.
3. Add flow documents for cross-context behaviour and `questions:` to specs (see [EXTERNAL-PATTERNS.md](EXTERNAL-PATTERNS.md)).
4. Replace migrated Confluence pages with a banner and link.
5. Later: the distilled per-context instructions for developers' Copilot in the code repositories.

### Definition of "ready for the analyst"
No `code only` community in `REPO_MAP.md`; every `@docs` calculation tag has a concept with test-derived worked
examples and an audit table; every imported page is in `_done/`; `okf-validate -Strict` clean; a context pack per spec
fits its budget; the high-value specs are human-verified.

### What to keep from this workspace, verbatim
`docs-repo/.github/**` (agents, skills, prompts, hooks, workflows), `docs-repo/scripts/**`, the templates, the
conventions, `code-repo-kit/**`. These are domain-neutral apart from names and paths.

### What is simulation only
The three repositories' content, the Harbor names, the external service contracts, the legacy pages, the work items and
test designs, and the stubs for Jira, Confluence and the tests repository.
