# Implementation plan - from this investigation repo to the real Advisory Platform

Reference workspace: `d:\investigation` (this folder). Everything below points to a file here that you copy,
rename or run. Target repositories (names assumed - rename everywhere with one search/replace):

| Repo | Stack | Gets |
|---|---|---|
| `advisory-be` | Kotlin / Spring Boot / Maven / PostgreSQL / Kafka | `code-repo-kit/be/**`, `code-repo-kit/shared/**`, `code-repo-kit/ci/docs-maps.yml` |
| `advisory-fe` | React / TypeScript | `code-repo-kit/fe/**`, `code-repo-kit/shared/**`, `code-repo-kit/ci/docs-maps.yml` |
| `advisory-docs` (new) | Markdown, OKF v0.2 bundle, PowerShell scripts | `docs-repo/**` |
| `advisory-tests` (exists) | your test framework | receives `test-design/**` via `scripts/push-to-tests-repo.ps1` |
| internal VSIX feed | - | `code-repo-kit/vscode-extension` packaged |

Constraints honoured: no third-party libraries or frameworks in the code repos (only PowerShell, the existing
Spring test classpath, the existing `typescript` devDependency), no MCP, GitHub Copilot only (VS Code + JetBrains),
bank confidentiality (synthetic data, content exclusion, read-only tooling).

---

## Step 0 - Prerequisites to verify (half a day)

| # | Check | Where | If false |
|---|---|---|---|
| 0.1 | `spring-boot-starter-test` on the BE test classpath | `advisory-be/*/pom.xml` | skip `GraphExportTest.kt`; regex joiner alone (edges "approximate") |
| 0.2 | `typescript` in FE `devDependencies` | `advisory-fe/package.json` | skip `gen-graph-fe.ts`; FE regex maps alone |
| 0.3 | PowerShell 7 available on CI runners (`pwsh`) | GitHub-hosted: yes; self-hosted: install | all generators are PS 5.1-compatible, so Windows runners also work |
| 0.4 | Git platform (GitHub / GitLab / Azure DevOps) | - | port `ci/docs-maps.yml` and `.github/workflows/docs-quality.yml`; the scripts do not change |
| 0.5 | Repo/org admin can set **Copilot content exclusion** | GitHub settings | fall back to `.copilotignore`-style instructions in `copilot-instructions.md` (weaker) |
| 0.6 | Jira / Confluence REST reachable from CI | network team | CSV fallback for Jira; Confluence publish optional |
| 0.7 | Internal security review slot for the VS Code extension (~250 lines, read-only, no network) | security team | JetBrains-only path still works via `graph-query.ps1` + prompts |
| 0.8 | Python 3 on docs CI (only for the vendored OKF reference checker/visualiser) | - | `okf-validate.ps1` is the gate; Python steps are `|| true` |
| 0.9 | Language policy agreed: English bundle, Czech at the edges (INVESTIGATION §3.10); Czech-speaking reviewer per context for translated rules | owners | without a reviewer, migrated specs stay `draft` |

Decide and record: owners per bounded context (frontmatter `owners`), pilot context (**Hedges** recommended), repo names.

---

## Step 1 - Create `advisory-docs` from the prototype (1-2 days)

1. Copy `docs-repo/**` (excluding `generated/graph/*`, `generated/codebase-map.md` sample content) into the new repo.
2. Search/replace `ORG/advisory-*` names; set `owners` in `features/_template.md`, `domain/calculations/_template.md`.
3. Keep: `index.md`, `log.md`, `architecture/`, `domain/glossary.md`, `domain/context-map.md`, `features/conventions.md`,
   `work-items/_schema.yml`, `test-design/README.md`, `.github/**`, `scripts/**`, `third-party/**` (licences).
4. Replace sample content: `features/hedges/HEDGE-001.md`, `domain/calculations/hedge_monthly_cashflow.md`,
   `work-items/HEDGE-001.yml`, `test-design/features/HEDGE-001.feature` - keep them until your first real spec exists
   (they are the worked example for the agents), then delete.
5. Run locally: `scripts/okf-validate.ps1 -Strict`, `scripts/build-index.ps1`, `scripts/validate-frontmatter.ps1`.
6. Enable CI `.github/workflows/docs-quality.yml` (warn-only for the first two weeks: make the gen-graph / index
   steps `continue-on-error: true`, then flip).

**Done when:** CI green on an empty-ish bundle; `index.md` lists sections; `.github/copilot-instructions.md` loads in VS Code / IntelliJ.

---

## Step 2 - Code-repo hygiene (BE and FE, 1 day each, no behaviour change)

1. **Content exclusion**: apply `code-repo-kit/shared/copilot-content-exclusion.yml` in repo settings (paths:
   `target/`, `build/`, `node_modules/`, lockfiles, generated clients, snapshots, big fixtures, old migrations, env configs).
2. Copy `code-repo-kit/be/.github/**` -> `advisory-be/.github/`; `code-repo-kit/fe/.github/**` -> `advisory-fe/.github/`.
   Adjust package root (`com.bank.adv`) and feature folder (`src/features`) names in the instructions if they differ.
3. Copy `code-repo-kit/shared/check-file-size.ps1` -> `scripts/`; create the legacy baseline once:
   `./scripts/check-file-size.ps1 -Root . -MaxLines 400 -WriteBaseline .filesize-baseline.txt` (FE: 300).
4. Copy `code-repo-kit/shared/ide-setup.md` into the repo wiki/README; distribute
   `code-repo-kit/shared/workspaces/hedges.code-workspace` (one per bounded context: BE module + FE feature + `_generated` + docs).

**Done when:** Copilot in both IDEs shows the instructions; `@workspace` no longer indexes `target/` / `node_modules/`.

---

## Step 3 - Lib-free generated maps (BE and FE, 1-2 days each)

1. Copy `code-repo-kit/be/scripts/docs/*.ps1` -> `advisory-be/scripts/docs/`; `code-repo-kit/fe/scripts/docs/*.ps1` -> `advisory-fe/scripts/docs/`.
2. Run `./scripts/docs/gen-all.ps1 -Root .` and inspect `docs/_generated/*.md`. Expect gaps where code deviates from
   the conventions the regexes assume; fix by **convention**, not by regex growth:
   - BE: `Topics` constants for Kafka names, annotation-based routing (`@GetMapping` etc.), one `*Facade.kt` per module,
     Flyway `V*.sql` migrations.
   - FE: `src/features/<name>/index.ts` barrel with `/** @module ... */`, `<name>.types.ts`, react-router objects or `<Route>`.
3. Add `@docs <ID>` KDoc/JSDoc tags on facades, calculators, event classes, FE barrels/types (pilot context first).
4. Commit `docs/_generated/**`; add `code-repo-kit/ci/docs-maps.yml` -> `.github/workflows/docs-maps.yml`
   (freshness gate `gen-all.ps1 -Check` + file-size gate on PR; publish job on `main` -> PR into `advisory-docs/generated/<repo>/`).
5. In `advisory-docs`, the publish job's PRs land in `generated/be/`, `generated/fe/`; agent `doc-sync` reviews them.

**Done when:** a PR that adds an endpoint without regenerating fails CI; `advisory-docs/generated/be/api-index.md` exists.

---

## Step 4 - Architectural graph (1-2 days + 1 day BE export)

1. Docs repo: `scripts/gen-graph.ps1` is already in place. Run `./scripts/gen-graph.ps1` (defaults read
   `generated/be`, `generated/fe`), then `./scripts/build-index.ps1`. Review `generated/graph/REPO_MAP.md`:
   - communities = Maven modules / FE features; FE and BE with the same name merge into one bounded context on purpose;
   - **Spec coverage** at the bottom is your documentation backlog (`code only` -> write spec; `spec only` -> tag code).
2. BE precise export (if 0.1 true): copy `code-repo-kit/be/templates/GraphExportTest.kt` to
   `<app-module>/src/test/kotlin/com/bank/adv/docs/`; create a `graph-export` Spring profile with embedded/mocked
   infra (H2 or Testcontainers already in use, `spring.kafka.*` pointed at a mock or `@MockBean` the templates).
   Run `mvn -pl <app-module> -Dtest=GraphExportTest -Ddocs.graph=true test` -> `docs/_generated/graph-export-be.json`.
   Add that command to the publish job in `docs-maps.yml` (comment block already there).
3. FE precise export (if 0.2 true): copy `code-repo-kit/fe/scripts/docs/gen-graph-fe.ts` + `tsconfig.gen.json`;
   `npx tsc -p scripts/docs/tsconfig.gen.json && node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json`.
   Adjust the HTTP-client regex in `gen-graph-fe.ts` (`fetch|axios|api|apiClient|http`) to your client wrapper name.
4. Re-run `gen-graph.ps1`; edges from the exports show `(exact)`. CI step "Architectural graph is up to date" is already
   in `docs-quality.yml`; the PR step prints impacted specs via `graph-query.ps1 -Files`.
5. IntelliJ users: `scripts/graph-query.ps1 -Node <id> | clip` then paste into Copilot chat with prompt
   `impact-from-graph`.

**Done when:** `#impact spec:<pilot-ID>` (VS Code) or `graph-query.ps1 -Node spec:<pilot-ID>` returns endpoints, classes,
tables, topics, FE hooks/routes with `file:line`, and `REPO_MAP.md` shows the pilot spec as `spec + code`.

---

## Step 5 - VS Code extension (2 days incl. review)

1. `cd code-repo-kit/vscode-extension && npm install && npm run compile && npx @vscode/vsce package --no-dependencies`.
2. Security review checklist is in its `README.md` (read-only `.md`/`.json` access under configured paths, no network,
   no runtime deps). If dev dependencies are also disallowed, vendor `vscode.d.ts` (MIT) instead of `@types/vscode`.
3. Publish the `.vsix` to the internal gallery / share drive; add to `hedges.code-workspace` recommendations.
4. Settings per workspace: `bankDocs.docsRepoPath`, `bankDocs.generatedPaths`, `bankDocs.graphPath` (empty = docs repo default).

**Done when:** in agent mode Copilot calls `#docsLookup` / `#codeMap` / `#specToCode` / `#impact` on its own for
"where / which / what breaks" questions; `@docs /impact topic:<x>` answers with citations and no source files opened.

---

## Step 6 - Pilot: Hedges end-to-end (1-2 weeks, in parallel with 3-5)

| Order | Action | Asset | Output |
|---|---|---|---|
| 6.1 | Skeleton spec from graph | prompt `spec-skeleton-from-graph` (community `hedges`) | `features/hedges/HEDGE-00x.md` draft with Interfaces/Events/Data prefilled |
| 6.2 | Fill business rules | agent `architect`/`write-feature-spec` skill reads only the facade; Czech Confluence pages via `confluence-migrator` (translates via glossary `cs` column, sets `source_lang`, `aliases`) into `confluence-import/` | spec `status: draft`, open questions listed |
| 6.3 | Calculations | skill `calculation-spec`; worked examples copied from BE unit tests | `domain/calculations/<id>.md` |
| 6.4 | Human review | owner adds `verified[].by: human:<id>` | index badge `human-reviewed` |
| 6.5 | Jira | agent `analyst` (graph-driven subtasks) -> `work-items/<ID>.yml` -> `scripts/jira-push.ps1` (or CSV) | epic/stories/subtasks |
| 6.6 | Tests | agent `test-designer` (graph-driven scope) -> `test-design/features/<ID>.feature` + fixtures -> `scripts/push-to-tests-repo.ps1` | PR in `advisory-tests` |
| 6.7 | HLD | prompt `hld-from-spec` | `architecture/` C4/Mermaid |
| 6.8 | Publish | `scripts/confluence-publish.ps1` (English mirror + banner; `-Lang cs` for a machine-translated Czech page via prompt `translate-for-publish`) | Confluence page points to Git |

Measure during the pilot (see Step 8) and adjust instructions before scaling to Loans, Stress tests, Admin, Integrations.

---

## Step 7 - Scale out and harden (weeks 3-8)

1. One bounded context per sprint: tag code (`@docs`), skeleton from graph, migrate Confluence, review, Jira, tests.
2. Flip gates to blocking: `gen-all.ps1 -Check`, `check-file-size.ps1`, `gen-graph.ps1 -Check`, `okf-validate.ps1 -Strict`.
3. Add `stale_after` discipline: specs older than 90 days without re-verification get the `STALE` badge; agents mark
   downstream outputs `@needs-review`.
4. Implement the stub scripts in `docs-repo/scripts/` for your platform: `jira-push.ps1`, `confluence-export.ps1`,
   `confluence-publish.ps1`, `push-to-tests-repo.ps1` (REST calls; CSV fallback kept).
5. Optional (only if build plugins get approved): richer generators in `docs-repo/ci-examples/` (springdoc OpenAPI,
   springwolf AsyncAPI, Dokka) feed the same `generated/` folders; the graph joiner does not change.

---

## Step 8 - Measurement protocol (run from the pilot onwards)

For 10 representative tasks per role (dev BE, dev FE, analyst, QA), record before/after:

| Metric | How |
|---|---|
| Tokens per task | Copilot usage metrics API (org) or the request count in the chat panel; proxy = number of files opened by Copilot in the session |
| Files opened by Copilot | ask for "list the files you read" at the end; target <= 3 per answer |
| Answer correctness | spot-check `file:line` citations exist; spec IDs resolve |
| Doc freshness | % specs `human-reviewed` and < 90 days; `REPO_MAP` spec coverage `spec + code` ratio |
| CI | % PRs failing the freshness gate (should fall to near 0 after two sprints) |

Targets after the pilot: >= 60 % fewer files opened per question, `code only` items in spec coverage trending to zero
for the pilot context, Jira subtasks produced in < 10 minutes per story with no source files read.

---

## Reusable assets catalogue

### Copilot customisation - docs repo (`docs-repo/.github/`)

| Type | Name | Use it for |
|---|---|---|
| instructions | `copilot-instructions.md` | golden rules, read order (indexes -> spec -> calculations -> graph -> maps), OKF rules, token discipline |
| instructions | `instructions/features.instructions.md`, `generated.instructions.md`, `test-design.instructions.md`, `work-items.instructions.md` | path-scoped rules (`applyTo`) |
| agent | `agents/architect.agent.md` | spec/HLD writing from maps + facade |
| agent | `agents/analyst.agent.md` | spec -> Jira YAML (graph-driven subtasks) |
| agent | `agents/test-designer.agent.md` | spec -> Gherkin + fixtures (graph-driven scope) |
| agent | `agents/impact-analyst.agent.md` | blast radius from the graph, checklist output |
| agent | `agents/doc-sync.agent.md` | review `generated/` PRs, propose spec updates |
| agent | `agents/confluence-migrator.agent.md` | classify/merge imported Confluence pages |
| skill | `skills/write-feature-spec` | spec authoring + source priority |
| skill | `skills/calculation-spec` | formula docs with worked examples |
| skill | `skills/jira-work-items` | slicing heuristics, YAML schema |
| skill | `skills/gherkin-test-design` | coverage checklist |
| skill | `skills/code-graph` (+ `references/subtask-mapping.md`, `graph-schema.md`) | reading/querying the graph; node -> subtask / test-layer mapping |
| skill | `skills/okf`, `okf-validate`, `okf-visualize` | OKF bundle rules, vendored checkers (MIT) |
| prompt | `prompts/spec-from-code`, `spec-skeleton-from-graph`, `hld-from-spec`, `jira-from-spec`, `tests-from-spec`, `impact-from-graph`, `translate-for-publish`, `okf-produce`, `okf-validate` | one-click flows |
| scripts | `scripts/gen-graph.ps1`, `graph-query.ps1`, `build-index.ps1`, `okf-validate.ps1`, `validate-frontmatter.ps1`, `check-freshness.ps1`, `map-paths.ps1` | generation + gates (lib-free) |
| scripts (stubs) | `scripts/jira-push.ps1`, `confluence-export.ps1`, `confluence-publish.ps1`, `push-to-tests-repo.ps1` | fill in REST calls for your platform |
| CI | `.github/workflows/docs-quality.yml` | all gates + impacted-specs output on PR |
| templates | `features/_template.md`, `domain/calculations/_template.md`, `architecture/adr/template.md`, `work-items/_schema.yml` | content shape |

### Copilot customisation - code repos (`code-repo-kit/`)

| Type | Name | Use it for |
|---|---|---|
| instructions | `be/.github/copilot-instructions.md`, `fe/.github/copilot-instructions.md` | read order (maps/graph -> facade -> range), never-open list, output discipline |
| instructions | `be/.github/instructions/{calculations,kafka,tests}.instructions.md`, `fe/.github/instructions/features.instructions.md` | scoped conventions the generators rely on |
| agent | `be/.github/agents/code-reader.agent.md` | <= 3 files Q&A |
| agent | `be/.github/agents/impact-analyst.agent.md` | blast radius inside the BE repo (graph when available) |
| prompt | `be/.github/prompts/explain-module`, `find-spec-code`; `fe/.github/prompts/explain-feature` | bounded explanations |
| scripts | `be/scripts/docs/gen-*.ps1`, `fe/scripts/docs/gen-*.ps1`, `gen-all.ps1 -Check` | regex maps + freshness gate |
| export | `be/templates/GraphExportTest.kt` | precise BE graph from the Spring context (test scope only) |
| export | `fe/scripts/docs/gen-graph-fe.ts` + `tsconfig.gen.json` (+ `README.md` on IDE errors outside the real repo) | precise FE graph via the TypeScript compiler API |
| shared | `shared/check-file-size.ps1`, `copilot-content-exclusion.yml`, `workspaces/hedges.code-workspace`, `ide-setup.md` | hygiene + IDE scope |
| CI | `ci/docs-maps.yml` | freshness/size gate; publish maps + exports to the docs repo |
| extension | `vscode-extension/` (`#docsLookup`, `#codeMap`, `#specToCode`, `#impact`, `@docs`) | MCP-free retrieval in VS Code |

### Fixtures to test against before touching the real repos
`code-repo-kit/samples/be-mini`, `samples/fe-mini` - run every generator and the graph joiner here first; expected
numbers are in `INVESTIGATION.md` §8.1-8.2.

---

## Order of execution (summary)

```
Step 0 verify prerequisites
Step 1 docs repo  ──┐
Step 2 hygiene BE/FE ├─ week 1
Step 3 maps BE/FE  ──┘
Step 4 graph       ──┐
Step 5 extension    ├─ week 2 (parallel with pilot 6.1-6.3)
Step 6 pilot Hedges ─┘  weeks 2-3
Step 7 scale + harden   weeks 3-8
Step 8 measure          continuous
```
