# Implementation plan - from this prototype workspace to the real repositories

Reference workspace: `C:\projects/investigation` (this folder; open `harbor.code-workspace`). Everything below points to a
file here that you copy, rename or run. The three simulated repositories stand in for the real ones; rename with one
search/replace (`harbor-*` -> your repo names, `Harbor` -> your platform name):

| Prototype folder | Stands in for | Stack | Gets |
|---|---|---|---|
| `backend/` (`harbor-backend`) | the real BE repo | Kotlin / Spring Boot / Maven / PostgreSQL / Kafka, OpenAPI-generated `*Api` interfaces | `code-repo-kit/be/**`, `shared/check-file-size.py`, `ci/docs-maps.yml` (via `apply-kit.py --flavour be`) |
| `frontend/` (`harbor-frontend`) | the real FE repo | React / TypeScript, OpenAPI-generated client | `code-repo-kit/fe/**`, same shared files (`apply-kit.py --flavour fe`) |
| `docs-repo/` (`harbor-docs`) | new docs repo | Markdown, OKF v0.2 bundle, Python scripts, Copilot customisation | `docs-repo/**` |
| - | existing tests repo | your test framework | receives `test-design/**` via `scripts/push-to-tests-repo.py` |
| - | internal VSIX feed | - | `code-repo-kit/vscode-extension` packaged |

Constraints honoured: no third-party libraries or frameworks in the code repos (only standard-library Python, the existing Spring test
classpath, the existing `typescript` devDependency), no MCP, GitHub Copilot only (VS Code + JetBrains), confidentiality in a
regulated enterprise (synthetic data, content exclusion, read-only tooling). Confluence stays the legacy source and the
publish target; Jira and the tests repo are outputs.

---

## Step 0 - Prerequisites to verify (half a day)

| # | Check | Where | If false |
|---|---|---|---|
| 0.1 | `harbor-core/src/main/resources/openapi/openapi_harbor.yaml` is the BE contract and controllers implement generated `*Api` interfaces with `override fun <operationId>` | BE repo | `gen-api-index.py` falls back to annotation scan; the join to operations is lost |
| 0.2 | External service contracts exist as OpenAPI files (`harbor-core/src/main/resources/api/`); Kafka topics are constants in one `Topics` object (`kafka-client`) | BE repo | add the files / constants before Step 3 (`events.md` cannot resolve literals) |
| 0.2a | Class-name prefixes cover the business contexts (layered `core`: `Product1*`, `Projection*`, `Stress*`, ...; one `<Ctx>Manager` per context) | BE repo, `components.md` | fill `docs-repo/contexts.yml` (context -> BE prefixes, FE feature, spec prefix); unmatched classes show as `shared` in the graph - rename or add a prefix line |
| 0.3 | `spring-boot-starter-test` on the BE test classpath | BE `pom.xml` | skip `GraphExportTest.kt`; regex joiner alone (edges "approximate") |
| 0.4 | `typescript` in FE `devDependencies`; API calls go through one generated client (`api.GET('<path>')` literals) | FE `package.json`, `src/api/` | skip `gen-graph-fe.ts`; FE regex maps alone |
| 0.5 | Python 3.11+ on CI runners (`python3`) | GitHub-hosted: yes; self-hosted: install | standard library only; Windows runners also work (`python`) |
| 0.6 | Git platform (GitHub / GitLab / Azure DevOps) | - | port `ci/docs-maps.yml` and `docs-quality.yml`; hooks and scripts do not change |
| 0.7 | Copilot surfaces: VS Code with custom agents, skills and hooks; JetBrains plugin from 2026-03 (reads `AGENTS.md`; hooks/skills preview); `chat.useAgentsMdFile` allowed by org policy | IDE admins | fall back to `copilot-instructions.md` carrying the full rules; CI enforces what hooks would |
| 0.8 | Repo/org admin can set **Copilot content exclusion** | GitHub settings | "never open" lists in `copilot-instructions.md` (weaker) |
| 0.9 | Jira / Confluence REST reachable from CI | network team | CSV fallback for Jira; Confluence publish optional |
| 0.10 | Security review slot for the VS Code extension (~250 lines, read-only, no network) and for the vendored OKF Python | security team | JetBrains-only path still works via `graph-query.py` + prompts; `okf-validate.py` is the gate without Python |
| 0.11 | Language policy agreed: English bundle, source language at the edges (INVESTIGATION §3.14); a native-speaking reviewer per context | owners | without a reviewer, migrated specs stay `draft` |

Decide and record: owners per bounded context (frontmatter `owners`), pilot context (one with calculations **and** a legacy
page to audit), repo names.

---

## Step 1 - Create the docs repo from the prototype (1-2 days)

1. Copy `docs-repo/**` into the new repo, excluding build outputs: `generated/be`, `generated/fe`, `generated/openapi`,
   `generated/asyncapi`, `generated/graph`, `generated/analytics`, `.context/`.
2. Search/replace `Harbor` / `harbor-*`; set `owners` in `features/_template.md`, `domain/calculations/_template.md`;
   adapt the context prefixes in `features/conventions.md` and `AGENTS.md`; keep `lang`, `source_lang`, `aliases`.
3. Keep: `index.md`, `log.md`, `architecture/`, `domain/glossary.md` (with its `Aliases` column), `domain/context-map.md`,
   `features/conventions.md`, `work-items/_schema.yml`, `test-design/README.md`, `docs-map.yml`, `.github/**`, `scripts/**`,
   `third-party/**` (licences), `.gitignore` (`.context/`, `.publish/`).
4. Sample content (`features/*/CLI-001|SES-001|P1-001|STR-001|MKT-001|RPT-001.md`, `domain/calculations/*.md`,
   `work-items/P1-001.yml`, `test-design/features/STR-001.feature`, `confluence-import/HARBOR/*`): keep until your pilot
   spec, work items and audit exist (they are the worked examples the agents and skills quote), then delete.
5. Run locally: `scripts/okf-validate.py --strict`, `scripts/build-index.py`, `scripts/validate-frontmatter.py`,
   `scripts/validate-work-items.py`.
6. Enable CI `.github/workflows/docs-quality.yml` (warn-only for two weeks: `continue-on-error: true` on the graph and
   coverage steps until Step 3 publishes maps) and `copilot-setup-steps.yml`.

**Done when:** CI green on an empty-ish bundle; `index.md` lists sections; in VS Code `AGENTS.md` is picked up, agents and
`/context-pack` appear in the pickers and the `preToolUse` hook refuses an edit under `generated/`; `AGENTS.md` + instructions load in JetBrains.

---

## Step 2 - Code-repo hygiene (BE and FE, 1 day each, no behaviour change)

1. `code-repo-kit/apply-kit.py --flavour be --target <be-repo> --what-if`, review, drop `--what-if`; same with `fe`. Copies
   `AGENTS.md`, `.github/` (copilot-instructions, instructions, agents, prompts, hooks, `copilot-setup-steps.yml`),
   `scripts/docs/**`, `scripts/check-file-size.py`, `.github/workflows/docs-maps.yml`.
2. Adjust in the copied files: base package (`harbor`), Maven modules (`core`, `kafka-client`), layer names, `applyTo` globs, feature folder root (`src/features`), the HTTP client wrapper name,
   header name (`X-Harbor-Session` -> yours), JDK / Node versions in `copilot-setup-steps.yml`.
3. **Content exclusion**: apply `code-repo-kit/shared/copilot-content-exclusion.yml` in repo settings (`target/` incl.
   `generated-sources`, `build/`, `node_modules/`, lockfiles, generated clients and `schema.d.ts`, snapshots, fixtures, env configs).
4. Legacy baseline once: `python3 scripts/check-file-size.py --root . --max-lines 400 --write-baseline .filesize-baseline.txt` (FE: 300).
5. Distribute `code-repo-kit/shared/ide-setup.md` and one `*.code-workspace` per bounded context from
   `shared/workspaces/product1.code-workspace` (BE `core` sources + resources + FE feature + docs repo; IntelliJ scopes by
   class-name prefix, e.g. `file:harbor-core/src/main/kotlin/com/acme/harbor//Product1*.kt||file:harbor-core/src/main/kotlin/com/acme/harbor//Projection*.kt`).

**Done when:** Copilot in both IDEs shows `AGENTS.md`-driven answers; `@workspace` no longer indexes `target/` / `node_modules/`;
the `agentStop` hook `docs-maps.json` runs `gen-all.py --check` at the end of a session.

---

## Step 3 - Lib-free generated maps and contract publish (BE and FE, 1-2 days each)

1. Run `python3 scripts/docs/gen-all.py --root .` and inspect `docs/_generated/*.md`:
   - BE: `codebase-map` (modules from `pom.xml` -> layers -> classes + resource folders), `components` (one row per class:
     layer, stereotype, injected deps, tables, `@docs`, `file:line`), `api-index` (operations from `openapi/openapi_harbor.yaml`
     joined to `override fun <operationId>`, `Tag` = context; rows `_not implemented_` are a real backlog), `events`,
     `db-schema` ("Used in:" lists classes), `jobs`, `docs-tags`.
   - FE: `codebase-map` (feature barrels), `routes`, `types-index`, `docs-tags`.
2. Expect gaps where code deviates from the conventions the regexes assume; fix by **convention**, not by regex growth:
   `Topics` constants, one `manager/<Ctx>Manager.kt` per context, business-prefix class names, constructor injection,
   `@Scheduled` with a one-line KDoc, Flyway `V*.sql` one column per line;
   FE `src/features/<name>/index.ts` barrel with `/** @module ... */`, `<name>.types.ts`, object routes.
3. Add `@docs <ID>` KDoc/JSDoc tags on managers, calculators, event classes, FE barrels/types (pilot context).
4. Commit `docs/_generated/**`; `docs-maps.yml` runs the freshness + size gate on PR and, on `main`, publishes maps **and
   contracts** (`harbor-core/src/main/resources/openapi/openapi_harbor.yaml` -> `generated/openapi/backend.yaml`,
   `.../openapi/harbor-events.yaml` -> `generated/asyncapi/backend.yaml`, `.../resources/api/*.yaml` -> `generated/openapi/external/`)
   as a PR into the docs repo.
5. In the docs repo the PRs land in `generated/be`, `generated/fe`, `generated/openapi`, `generated/asyncapi`; agent
   `doc-sync` reviews them (`map-paths.py` -> affected specs). The docs repo's collector (`scripts/collect-evidence.py`, CI `ci-examples/collect-evidence.yml`) does the copy, validation and manifest; the code repos keep only the PR freshness check.

**Done when:** a PR that adds an operation to `openapi_harbor.yaml` without regenerating fails CI; `generated/be/api-index.md` and
`generated/openapi/backend.yaml` exist in the docs repo; `jobs.md` lists the import jobs.

---

## Step 4 - Architectural graph (1-2 days + 1 day BE export)

1. Docs repo: `python3 scripts/gen-graph.py` (reads `generated/be` incl. `components.md`, `generated/fe`, `contexts.yml`), then
   `python3 scripts/build-index.py`. Review `generated/graph/REPO_MAP.md`: communities = bounded contexts of `contexts.yml`
   (`context:<name>` node at its manager + BE classes by name prefix + the FE feature; `class:` nodes with `depends-on` /
   `persists-to` edges); the `shared` bucket lists classes without a known prefix; the
   **Spec coverage** list is your documentation backlog (`code only` -> `/spec-skeleton-from-graph`; `spec only` -> tag code).
2. BE precise export (if 0.3 true): copy `code-repo-kit/be/templates/GraphExportTest.kt` into `harbor-core/src/test/kotlin/com/acme/harbor/docs/`;
   create a `graph-export` Spring profile with embedded/mocked infra (or `init_docker_compose`). Run
   `mvn -pl harbor-core -am -Dtest=GraphExportTest -Ddocs.graph=true test` -> `docs/_generated/graph-export-be.json`; add the
   command to the code repo's CI as an artifact-producing step; the docs repo's collector downloads the artifact (comment block in `docs-maps.yml` / `collect-evidence.yml`).
3. FE precise export (if 0.4 true): `npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js src
   docs/_generated/graph-export-fe.json`; adjust the client-wrapper regex in `gen-graph-fe.ts`.
4. Re-run `gen-graph.py`; edges from the exports show `(exact)`. The CI step "Architectural graph is up to date" is in
   `docs-quality.yml`; the PR step prints impacted specs via `graph-query.py --files`.
5. Build a pack: `python3 scripts/context-pack.py --task <pilot-ID> --print` - the graph section must be present (else the graph is missing or stale).

**Done when:** `#impact spec:<pilot-ID>` (VS Code) or `graph-query.py --node spec:<pilot-ID>` returns endpoints, classes,
tables, topics, FE hooks/routes with `file:line`; `REPO_MAP.md` shows the pilot spec as `spec + code`; the pack has all sections.

---

## Step 5 - VS Code extension (2 days incl. review)

1. `cd code-repo-kit/vscode-extension && npm install && npm run compile && npx @vscode/vsce package --no-dependencies`.
2. Security review checklist in its `README.md` (read-only `.md`/`.json` under configured paths, no network, no runtime deps).
   If dev dependencies are also disallowed, vendor `vscode.d.ts` (MIT) instead of `@types/vscode`.
3. Publish the `.vsix` to the internal gallery; add it to the per-context workspace recommendations.
4. Settings per workspace (see `harbor.code-workspace`): `harborDocs.docsRepoPath`, `harborDocs.generatedPaths`,
   `harborDocs.graphPath`, plus `chat.useAgentsMdFile` and `chat.useHooks`.

**Done when:** in agent mode Copilot calls `#docsLookup` / `#codeMap` / `#specToCode` / `#impact` on its own for
"where / which / what breaks" questions; `@docs /impact topic:<x>` answers with citations and no source files opened.

---

## Step 6 - Pilot: one bounded context end-to-end (1-2 weeks, in parallel with 3-5)

| Order | Action | Asset | Output |
|---|---|---|---|
| 6.1 | Context pack | `/context-pack <ID>` or `scripts/context-pack.py --task <ID>` (skill `task-context`) | `.context/<ID>.md`; every later step starts from it |
| 6.2 | Skeleton spec from graph | `/spec-skeleton-from-graph <context> <ID>` (agent `spec-writer`) | `features/<ctx>/<ID>.md` draft with Interfaces (from `openapi_harbor.yaml`), Events, Data prefilled |
| 6.3 | Fill business rules | `spec-writer` reads graph neighbourhood + one manager file (`context:` node); legacy pages via `confluence-migrator` (translates via glossary `Aliases`, sets `source_lang`, `aliases`) | spec `status: draft`, open questions listed |
| 6.4 | Calculations + audit | skill `calculation-spec` (worked examples copied from the unit test); `/audit-calculation <name>` (agent `calc-auditor`, skill `legacy-page-audit`) against the calculator + its test | `domain/calculations/<name>.md` with `## Audit <date>` table; legacy page `migrated | obsolete` |
| 6.5 | Human review | owner adds `verified[].by: human:<id>` | index badge `human-reviewed` |
| 6.6 | Jira | `@analyst /jira-from-spec <ID>` (pack only; subtasks per graph node kind) -> `work-items/<ID>.yml` -> `validate-work-items.py` -> `jira-push.py` (or CSV) | epic/stories/subtasks |
| 6.7 | Tests | `@test-designer /tests-from-spec <ID>` -> `test-design/features/<ID>.feature` + fixtures -> `push-to-tests-repo.py` | PR in the tests repo |
| 6.8 | HLD | `/hld-from-spec` (agent `architect`, contracts + graph) | `architecture/` C4/Mermaid |
| 6.9 | Status | `/coverage-report <prefix>` (skill `docs-analytics`) | <= 25-line report from `coverage-matrix.md` + badges + REPO_MAP coverage |
| 6.10 | Publish | `scripts/confluence-publish.py` (English mirror + banner; `--lang <code>` for a machine-translated page via `translate-for-publish`) | Confluence page points to Git |

Measure during the pilot (Step 8) and adjust `AGENTS.md`, the pack budget and the agents before scaling to the other contexts.

---

## Step 7 - Scale out and harden (weeks 3-8)

1. One bounded context per sprint: tag code (`@docs`), pack, skeleton from graph, migrate + audit legacy pages, review, Jira, tests.
2. Flip gates to blocking: `gen-all.py --check`, `check-file-size.py`, `gen-graph.py --check`, `coverage-matrix.py --check`,
   `okf-validate.py --strict`; keep the IDE hooks identical to CI.
3. `stale_after` discipline: specs older than 90 days without re-verification get the `STALE` badge; packs show it; agents mark
   downstream outputs `needs-spec-review`.
4. Implement the stub scripts for your platform: `jira-push.py`, `confluence-export.py`, `confluence-publish.py`,
   `push-to-tests-repo.py` (REST calls; CSV fallback kept).
5. Optional (only if build plugins get approved): richer generators in `docs-repo/ci-examples/` (springdoc, springwolf, Dokka)
   feed the same `generated/` folders; the graph joiner and the packs do not change.

---

## Step 8 - Measurement protocol (run from the pilot onwards)

For 10 representative tasks per role (dev BE, dev FE, analyst, QA), record before/after:

| Metric | How |
|---|---|
| Tokens per task **with vs without the context pack** | same task twice (pack attached via `#file` vs. free navigation); Copilot usage metrics API (premium requests) or request count in the chat panel |
| Files opened by the agent | ask for "list the files you read" at the end; **target <= 2 besides the pack** |
| Answer correctness | spot-check `file:line` citations exist; spec IDs and `BR-*` resolve; audit tables match the unit test |
| Doc freshness | % specs `human-reviewed` and < 90 days; `REPO_MAP` spec coverage `spec + code` ratio; `_not implemented_` rows in `api-index.md` |
| CI / hooks / analytics | % PRs failing the freshness gate (near 0 after two sprints); hook failures per week; `/coverage-report` answers a sprint-status question without a human opening files |

Targets after the pilot: >= 60 % fewer files opened per question, `code only` items trending to zero for the pilot context,
Jira subtasks produced in < 10 minutes per story with no source files read, every formula concept audited once.

---

## Reusable assets catalogue

### Copilot customisation - docs repo (`docs-repo/`)

| Type | Name | Use it for |
|---|---|---|
| canonical rules | `AGENTS.md` | purpose, context-pack rule, read order, hard rules, commands (cross-tool) |
| instructions | `.github/copilot-instructions.md` | Copilot-specific: agent/prompt matrix, extension tools, hooks, output discipline |
| instructions | `.github/instructions/{features,calculations,generated,test-design,work-items,confluence-import}.instructions.md` | path-scoped rules (`applyTo`, `description`) |
| agent | `agents/analyst.agent.md` | pack -> Jira YAML + analytics mode; handoffs to `test-designer`, `spec-writer` |
| agent | `agents/spec-writer.agent.md` | spec from graph + contracts + one manager file; handoffs to `analyst`, `calc-auditor` |
| agent | `agents/calc-auditor.agent.md` | formula doc / legacy page vs. calculator + unit test (two files) |
| agent | `agents/doc-sync.agent.md` | review `generated/` PRs, propose spec updates |
| agent | `agents/test-designer.agent.md` | spec -> Gherkin + fixtures (graph-driven scope) |
| agent | `agents/architect.agent.md` | HLD / ADR from contracts and graph |
| agent | `agents/impact-analyst.agent.md` | blast radius from the graph, checklist output |
| agent | `agents/confluence-migrator.agent.md` | classify/merge legacy pages; formula pages -> `calc-auditor` |
| skill | `skills/task-context` (+ `references/pack-anatomy.md`) | build and consume context packs |
| skill | `skills/write-feature-spec` (+ `source-priority.md`), `calculation-spec` (+ `conventions.md`), `legacy-page-audit` | authoring; claims list, two-file comparison, audit table, status rules |
| skill | `skills/jira-work-items` (+ `slicing-heuristics.md`), `gherkin-test-design` (+ `coverage-checklist.md`) | downstream outputs |
| skill | `skills/code-graph` (+ `subtask-mapping.md`, `graph-schema.md`) | reading/querying the graph; node -> subtask / test layer |
| skill | `skills/docs-analytics` | coverage / trust / staleness answers from generated files |
| skill | `skills/okf`, `okf-validate`, `okf-visualize` | OKF bundle rules, vendored checkers (MIT) |
| prompt | `prompts/context-pack`, `spec-skeleton-from-graph`, `spec-from-code`, `audit-calculation`, `jira-from-spec`, `tests-from-spec`, `hld-from-spec`, `impact-from-graph`, `coverage-report`, `translate-for-publish`, `okf-produce`, `okf-validate` | one-click flows (`agent`, `argument-hint`) |
| hooks | `.github/hooks/docs-quality.json` + `scripts/hooks/guard-generated.py` | `preToolUse` guard on `generated/**`, `agentStop` validators |
| scripts | `context-pack.py`, `graph-query.py`, `gen-graph.py`, `coverage-matrix.py`, `build-index.py`, `okf-validate.py`, `validate-frontmatter.py`, `validate-work-items.py`, `map-paths.py`, `check-freshness.py`, `collect-evidence.py` (`publish-local.py` deprecated wrapper) | generation + gates (lib-free) |
| scripts (stubs) | `jira-push.py`, `confluence-export.py`, `confluence-publish.py`, `push-to-tests-repo.py` | fill in REST calls for your platform |
| CI | `.github/workflows/docs-quality.yml`, `copilot-setup-steps.yml` | all gates + impacted-specs output; coding-agent environment |
| templates | `features/_template.md`, `domain/calculations/_template.md`, `architecture/adr/template.md`, `work-items/_schema.yml` | content shape |

### Copilot customisation - code repos (`code-repo-kit/`)

| Type | Name | Use it for |
|---|---|---|
| installer | `apply-kit.py --flavour be|fe --target <repo> [--what-if]` | copies the flavour into a repo (kit is the source of truth) |
| canonical rules | `be/AGENTS.md`, `fe/AGENTS.md` (<= 60 lines) | read order (maps -> manager (+ `components.md` deps) / barrel -> one range), contracts as truth, conventions the generators rely on |
| instructions | `be/.github/copilot-instructions.md`, `fe/.github/copilot-instructions.md` | never-open list, output discipline, agents/prompts/tools |
| instructions | `be/.github/instructions/{api,calculations,kafka,migrations,tests}.instructions.md`, `fe/.github/instructions/{features,api-client}.instructions.md` | scoped conventions |
| agent | `be/.github/agents/code-reader.agent.md`, `fe/.github/agents/code-reader.agent.md` | <= 3 files Q&A |
| agent | `be/.github/agents/impact-analyst.agent.md` | blast radius across backend / frontend / docs |
| prompt | `be/.github/prompts/{explain-module,find-spec-code,add-endpoint}`, `fe/.github/prompts/explain-feature` | bounded explanations (`/explain-module` explains a context: manager + its deps), contract-first endpoint checklist |
| hooks / setup | `be|fe/.github/hooks/docs-maps.json`, `be|fe/.github/workflows/copilot-setup-steps.yml` | `agentStop` -> `gen-all.py --check`; JDK 21 / Node 24 for the coding agent |
| scripts | `be/scripts/docs/gen-{codebase-map,components,api-index,events,db-schema,jobs,docs-tags}.py`, `fe/scripts/docs/gen-{codebase-map,routes,types-index,docs-tags}.py`, `gen-all.py --check` | regex/contract maps + freshness gate |
| export | `be/templates/GraphExportTest.kt` | precise BE graph from the Spring context (test scope only) |
| export | `fe/scripts/docs/gen-graph-fe.ts` + `tsconfig.gen.json` (+ `README.md`) | precise FE graph via the TypeScript compiler API |
| shared | `shared/check-file-size.py`, `copilot-content-exclusion.yml`, `workspaces/product1.code-workspace`, `ide-setup.md` | hygiene + IDE scope |
| CI | `ci/docs-maps.yml` | freshness/size gate; publish maps, contracts and exports to the docs repo |
| extension | `vscode-extension/` (`#docsLookup`, `#codeMap`, `#specToCode`, `#impact`, `@docs`) | MCP-free retrieval in VS Code |

### Fixtures to test against before touching the real repos
The simulated repos `backend/` and `frontend/` (naming contract `BLUEPRINT.md`): layered BE (`core` + `kafka-client` in `pom.xml`, 10 contexts by class-name prefix in `contexts.yml`),
34 operations in `harbor-core/src/main/resources/openapi/openapi_harbor.yaml`, 5 topics, 5 external contracts, 9 FE feature folders; specs `CLI-001` / `SES-001` / `P1-001`
stable, `STR-001` draft with a deliberately outdated legacy page, `MKT-001` / `RPT-001` skeletons, `P2-001` / `COV-001` /
`IMP-001` / `ADM-001` deliberately missing. Run every generator, the publish, the graph joiner, the packs and the coverage
matrix here (`README.md` "Try it"); counts and spec coverage: see `docs-repo/generated/graph/REPO_MAP.md`. Then exercise the agents on
the gaps: `/spec-skeleton-from-graph product2 P2-001`, `/audit-calculation stress_test_monthly`, `@analyst /jira-from-spec STR-001`, `/coverage-report`.

---

## Order of execution (summary)

```
Step 0 verify prerequisites (contract, topics, test classpath, Copilot surfaces)
Step 1 docs repo (AGENTS.md, agents, skills, hooks, CI)  --+
Step 2 hygiene BE/FE (apply-kit, exclusion, baseline)        +- week 1
Step 3 maps + contracts publish BE/FE                       --+
Step 4 graph + packs                                        --+
Step 5 extension                                              +- week 2 (parallel with pilot 6.1-6.4)
Step 6 pilot context (pack -> spec -> audit -> Jira -> tests) -+  weeks 2-3
Step 7 scale + harden                                            weeks 3-8
Step 8 measure (tokens with/without pack, files opened)          continuous
```
