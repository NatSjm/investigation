# Investigation: Docs-as-Code repository for a large two-repository enterprise application

**Date**: 2026-10-09 · **Status**: proposal · **Prototype**: `docs-repo/` + simulated code repos `backend/`, `frontend/` + `code-repo-kit/`
(open `harbor.code-workspace`; naming contract in `BLUEPRINT.md`; the business case is synthetic - see §8)

## 1. Problem

| Fact | Consequence |
|---|---|
| A large two-year-old platform in a regulated enterprise (React FE, Kotlin/Spring/Maven BE, PostgreSQL, Kafka, five external services) | Large, heterogeneous codebase; reading it with an LLM is expensive |
| FE and BE are generated from one OpenAPI contract; external services have their own contracts | The contracts are the cheapest truth about FE<->BE and BE<->external; agents must be pointed at them, not at generated code |
| Heavy domain: meeting sessions, monthly projections over a planning horizon (four cumulative result tables), cover ratios, market scenarios, stress tests, PDF reports, admin parameters; large monthly calculations live in Kotlin utilities, not SQL | Business rules and formulas are the most valuable and most drift-prone knowledge; they are testable but buried |
| Client data arrives as XLS files parsed by scheduled jobs; a meeting is a session in the DB created when a product is selected, and every request then carries a session header | Behaviour depends on jobs and request context that no controller shows; agents guess unless maps say so |
| Legacy docs in Confluence, drifting; several pages contradict the code | Must be validated against the real state before anything is derived from them; no review, no CI, not machine-consumable |
| Downstream needs: analytics, Jira epics/stories/subtasks, test cases + data for an existing tests repo, HLD | Docs must be structured enough to be *inputs* for automation |
| Constraints: GitHub Copilot only (VS Code + JetBrains); **no MCP, no third-party agent frameworks or libraries in the code repos**; confidentiality | Everything lives in the docs repo as Copilot-native customisation (AGENTS.md / instructions / agents / skills / prompts / hooks) + plain Python (standard library); synthetic data only |

## 2. Options considered

| Option | Verdict | Why |
|---|---|---|
| A. Keep Confluence as source, generate from it | ✗ | No diff/review/CI; Copilot cannot use it as context; drift continues |
| B. Docs inside BE repo (`/docs`) | ✗ | FE docs split off; huge context for Copilot; access/ownership coupling; can't add agents/skills there |
| **C. Dedicated docs repo, docs-as-code (chosen)** | ✓ | Reviewable, CI-checkable, small focused context, Copilot customisation allowed, tool-agnostic (Markdown/Mermaid/YAML) |
| D. Wiki (GitHub/GitLab wiki) | ✗ | Weak PR flow, no CI, no folder conventions, no Copilot customisation |
| E. Full DocOps platform (Backstage TechDocs, Docusaurus site) | later | Nice rendering, but adds infra; can be layered on C later |

## 3. Recommended architecture (Option C)

```mermaid
flowchart LR
  BE[BE repo<br/>gen-all.py + contracts] -- CI publishes --> GEN[generated/be, fe, openapi, asyncapi]
  FE[FE repo<br/>gen-all.py] -- CI publishes --> GEN
  CONF[Confluence legacy] -- export --> IMP[confluence-import/]
  GEN -- gen-graph.py --> GRAPH[generated/graph]
  GRAPH & SPEC[features · domain · architecture] -- context-pack.py --> PACK[.context/task.md]
  PACK --> AN[@analyst] --> WI[work-items -> Jira]
  PACK --> TD[@test-designer] --> TESTS[test-design -> tests repo]
  PACK --> SW[@spec-writer / @calc-auditor / @doc-sync] --> SPEC
  IMP -. audited, never copied .-> SW
  SPEC -- publish --> CONFRO[Confluence read-only mirror]
  SPEC -. freshness gate .-> BE & FE
```

### 3.1 Content model
- **`features/<ctx>/<ID>.md`** - functional spec with YAML frontmatter (id, context, status, `code_refs`, api, events,
  tables, calculations, jira, tests, `last_verified`, `stale_after`, `lang`, `source_lang`, `aliases`). Numbered business
  rules `BR-<ID>-n` are the traceability atoms cited by stories and test scenarios. Prefixes: `CLI SES IMP P1 P2 COV MKT STR RPT ADM`.
- **`domain/calculations/*.md`** - formula + conventions (month grid, rounding `HALF_EVEN`, scale, sign conventions) +
  **worked examples copied from the BE unit tests**. The key asset for a computation-heavy app: once written, analysts,
  testers and agents never open Kotlin; the `calc-auditor` keeps it true (§3.7).
- **`domain/glossary.md`** - canonical English terms; an `Aliases` column holds synonyms and source-language terms.
- **`architecture/`** - arc42-lite, C4 in Mermaid, ADRs, integration/Kafka map (partly generated).
- **`generated/`** - CI-produced, read-only: `be/` and `fe/` code maps (BE layers, **components** (one row per class with
  injected dependencies and tables), API index, events, DB schema, **jobs**, routes, types, `@docs` tags), **`openapi/backend.yaml`**, **`openapi/external/*.yaml`**, **`asyncapi/backend.yaml`** (copies of the
  contracts - the analyst sees FE<->BE and BE<->external without any client code), `graph/` (§3.13), `analytics/` (§3.8).
- **`work-items/*.yml`** - epic/stories/subtasks with Gherkin acceptance criteria -> Jira via REST or CSV.
- **`test-design/`** - Gherkin `.feature` + synthetic fixtures + shared **step vocabulary** (contract with the tests repo).
- **`confluence-import/`** - legacy pages as evidence, never as rules; each ends `migrated` or `obsolete`.
- **`docs-map.yml`** - code path globs -> specs; drives PR-to-spec mapping and the freshness gate.

### 3.2 Keeping docs and code in sync
1. The docs repo's collector (nightly or on demand) checks out FE/BE read-only, regenerates the maps, validates the snapshot,
   replaces `generated/` with a manifest of source commits and opens ONE PR labelled `generated`
   (`docs-repo/ci-examples/collect-evidence.yml` -> `scripts/collect-evidence.py`; the code repos' `docs-maps.yml` is the PR
   freshness check only).
2. The `doc-sync` agent (or a human) processes that PR: `map-paths.py` changed paths -> specs, diffs against contracts,
   updates specs, bumps `last_verified`, flags tests to review.
3. FE/BE PRs run a **freshness gate** (`ci-examples/code-repo-freshness-gate.yml` -> `scripts/check-freshness.py`):
   touching a mapped path requires a recent `last_verified` or the label `docs-not-affected`.
4. Inside the IDE the same gates run as **hooks**: `preToolUse` denies edits under `generated/**` and of `index.md`,
   `agentStop` rebuilds indexes and validates the bundle (`.github/hooks/docs-quality.json`).
5. Confluence becomes a **read-only mirror** published on merge (banner: "managed in Git").

### 3.3 Copilot customisation - 2026 conventions (no MCP / frameworks)
All files are native Copilot customisation, in the docs repo and (a smaller set) in the code repos:

| Artefact | Files | Role | Read by |
|---|---|---|---|
| Canonical rules | `AGENTS.md` (<= 60 lines) | purpose, read order, hard rules, commands | VS Code, JetBrains (since 2026-03), Copilot CLI, coding agent, other agent CLIs |
| Copilot supplement | `.github/copilot-instructions.md` (short) | what is Copilot-specific: which agent for which job, tools, hooks | all Copilot surfaces |
| Scoped instructions | `.github/instructions/*.instructions.md` with `applyTo` + `description` | rules load only when editing specs / calculations / work items / tests / generated / legacy pages | all |
| Custom agents | `.github/agents/*.agent.md` with `tools` aliases and `handoffs` | one persona per downstream artefact, strict "what to read" lists | all (`handoffs` VS Code) |
| Agent Skills | `.github/skills/<name>/SKILL.md` + `references/` (agentskills.io layout) | reusable procedures with progressive disclosure | VS Code, CLI, coding agent, JetBrains (preview) |
| Prompt files | `.github/prompts/*.prompt.md` with `agent` + `argument-hint` | one-shot parametrised tasks (`/jira-from-spec`, `/coverage-report`, ...) | VS Code, JetBrains, CLI |
| Hooks | `.github/hooks/*.json` (`preToolUse`, `agentStop`) | guard rails and validators inside the session | VS Code, CLI, coding agent, JetBrains (preview) |
| Setup steps | `.github/workflows/copilot-setup-steps.yml` | environment for the coding agent (Python 3.12, pyyaml only for the OKF reference tools; JDK / Node in the code repos) | coding agent |

The spec -> work-items -> tests chain corresponds to the community **Spec Kit** pattern (spec -> plan -> tasks); we keep the
pattern and the file discipline but do not adopt its CLI (no third-party tooling, our artefacts are OKF concepts and YAML).

### 3.4 Token-saving strategy (the core design driver)
| Technique | Effect |
|---|---|
| **Task-scoped context pack** (§3.5) | one ~300-500-line read replaces 10-20 tool calls; the agent opens <= 2 files besides the pack |
| **Contracts instead of generated code** (§3.6) | `openapi/harbor-api.yaml` is read once; `*Api` interfaces, generated clients and `schema.d.ts` are never opened |
| **Lib-free code maps in the code repos** (`code-repo-kit/`, §3.12) | 1 row per layer/class/operation/topic/table/job/route with `file:line` instead of directory walks |
| **Layered backend mapped by name prefix** (§3.12) | `contexts.yml` turns `Product1*` / `Projection*` classes spread over `api/`, `manager/`, `service/`, `dao/` into one bounded context; `components.md` gives the injection chain, so nobody walks layer folders |
| **Architectural graph** (§3.13) | context -> endpoint -> manager -> service / dao -> calculator -> table (`depends-on`, `persists-to`), topic -> consumer, FE route -> endpoint; a few hundred nodes |
| **Calculations as formula + worked examples** | tests/analytics derived from ~50 lines of Markdown instead of thousands of lines of Kotlin |
| **Source priority ladder** in every agent (pack -> indexes -> spec -> calculations -> graph -> maps -> contracts -> one range) | agents stop at the cheapest sufficient source |
| `applyTo`-scoped instructions, short `SKILL.md` + `references/` | only relevant rules enter context |
| Content exclusion + per-context workspaces + "never open" lists | `target/`, `node_modules`, generated clients, fixtures never enter context or the index |
| Prefer BE unit tests over services when edge cases are needed | tests are dense in facts, cheap in tokens; two files per audit |
| Output discipline ("files only, <= 15 lines in chat") | prevents echoing large content back |
| Spec size cap (~300 lines) and diagram cap (<= 25 nodes) | keeps any single read bounded |

### 3.5 Task-scoped context packs (lever a)
`scripts/context-pack.py --task <spec ID | calculation | graph node | free text> [--budget 500] [--print]` writes
`.context/<task>.md` (git-ignored). Sections in priority order, lower ones truncated when over budget: header with trust
badge (`human-reviewed | machine-confirmed | unverified`, `STALE`), spec body or its key sections, linked calculations
(formula + worked examples, never the Kotlin), depth-2 graph neighbourhood with `file:line`, the OpenAPI `paths` of the
spec's `api[]` and the AsyncAPI channels of its `events[]`, `db-schema.md` sections for `tables[]`, existing work items and
scenarios, legacy pages mentioning the subject (marked unverified), footer with sources and truncations. Skill `task-context`:
read once, quote `BR-*` and `file:line`, treat the badge as part of the answer, open nothing else unless an open question names
a `file:line`; free text matching several specs yields `candidates:`. Why a script: deterministic, budgeted, reviewable, carries provenance.

### 3.6 Contract-led API index and jobs map (lever b)
Because the real FE and BE are generated from the OpenAPI document, the controllers carry no mapping annotations.
`gen-api-index.py` therefore reads `core/src/main/resources/openapi/harbor-api.yaml` (operations, parameters, the shared session-header parameter) and
joins each `operationId` to `override fun <operationId>(` in a `@RestController`; operations without an implementation are
listed `_not implemented_` (a useful backlog signal). Annotation scan remains the fallback for non-contract repos.
`gen-jobs.py` lists every `@Scheduled` method with its trigger and one KDoc line, so the XLS import and monthly snapshot
jobs are visible to analysts. `events.md` resolves `Topics.<CONST>`; `db-schema.md` is parsed from Flyway migrations, so the
four cumulative projection tables and the `parameter_set` table appear with columns. CI copies `openapi/harbor-api.yaml`,
`openapi/harbor-events.yaml` and `core/src/main/resources/api/*.yaml` next to the maps.

### 3.7 Calculation and legacy-page audit (lever c)
Agent `calc-auditor` + skill `legacy-page-audit`: given a calculation name, a spec ID or a legacy page, build the pack,
extract every checkable claim (terms, thresholds, defaults, rounding, sign conventions, flow steps), locate the code
through `docs-tags.md`, open **exactly two files** (the calculator class and its unit test), classify each claim
`MATCH | DOC-STALE | CODE-SUSPECT | UNDOCUMENTED`, record an `## Audit <date>` table in the concept, downgrade to `draft`
when anything differs, mark the legacy page `obsolete | migrated`. Worked examples may only be replaced by values copied
from the test. `confluence-migrator` hands every formula page to this agent instead of migrating it.

### 3.8 Docs analytics (lever d)
`scripts/coverage-matrix.py` -> `generated/analytics/coverage-matrix.md|json`: per spec BRs / with story / with scenario /
open questions / badge / `stale_after`; per calculation `used_by`, worked examples, audited. Skill `docs-analytics` and prompt
`/coverage-report` (agent `analyst`) answer status questions from this file, the index badges and the **Spec coverage**
section of `generated/graph/REPO_MAP.md` (`spec + code` / `code only` / `spec only`) - counts come from scripts, source code
is never opened, `machine-confirmed` is not treated as verified.

### 3.9 Downstream automation
| Output | Agent | Transport (no MCP) |
|---|---|---|
| Jira epic/stories/subtasks | `analyst` -> `work-items/*.yml` (subtasks per graph node kind) | `scripts/jira-push.py` (REST v3) or CSV bulk import |
| Test cases + data | `test-designer` -> `test-design/` | `scripts/push-to-tests-repo.py` (git + PR API); tests repo CI reports unimplemented steps |
| HLD / ADR | `architect` -> `architecture/hld`, `adr` | in-repo |
| Analytics / reports | `coverage-matrix.py`, index badges, REPO_MAP coverage | in-repo, CI-generated |
| Confluence | `confluence-publish.py` | Confluence REST (one-way) |

### 3.10 Quality gates (docs repo CI + hooks)
`.github/workflows/docs-quality.yml`: markdownlint · frontmatter/ID validation · work-items schema · OKF §11 conformance
(`okf-validate.py --strict` + reference Python checker) · `build-index.py --check` · `gen-graph.py --check` ·
`coverage-matrix.py --check` · impacted specs per PR · OKF graph artifact · link check · Mermaid compile · Spectral lint of the
published contracts · freshness gate (in the code repos). The `agentStop` hook runs the validators locally before CI does.

### 3.11 Knowledge format: Google Open Knowledge Format (OKF v0.2)

**Decision:** the docs repo *is* one OKF bundle (root `index.md` with `okf_version: "0.2"`); repo-specific keys (`id`,
`code_refs`, `jira`, `tests`, ...) are extensions.

| Need | OKF construct | Effect for us |
|---|---|---|
| Agents must find the right doc cheaply | reserved `index.md` per folder, one line + description per concept (§8) | progressive disclosure: root -> area -> concept; ~2-3k tokens to orient |
| Trust: which docs can an analyst rely on? | `generated.by`, `verified[].by` with actors `human:<id>` / `copilot/<agent>` / `process:<ci>` | index badges `unverified · machine-confirmed · human-reviewed · STALE`; packs carry the badge |
| Formulas that must match code | `Attested Computation` (`runtime`, `parameters`, `# Computation`, attester) | `domain/calculations/*.md` are executable-by-contract specs, auditable against the unit test |
| Provenance for migrated legacy content | `sources[]` + `[^id]` footnotes | each claim traceable to page/author/date |
| Ageing | `stale_after`, `status` enum | validator flags STALE; freshness becomes machine-checkable |
| Interop | Apache-2.0 spec, plain Markdown+YAML, deterministic checker | no lock-in |

**Toolkit:** `scaccogatto/okf-skills` (MIT, Claude Code) ported to Copilot: skills `okf` (+ `PORTING.md`, vendored `SPEC.md`,
templates), `okf-validate` (reference checker + standard-library twin `scripts/okf-validate.py`), `okf-visualize` (CI artifact); MCP server, backfill
subagents and `action.yml` not ported. `scripts/build-index.py` is new. Licences under `third-party/`; vendored Python needs a security review and pinning.

### 3.12 Token efficiency inside the FE/BE repos (`code-repo-kit/`)

Constraint: no third-party libraries in the code repos; standard-library Python, Copilot customisation files and an in-house VS Code
extension are allowed. `apply-kit.py --flavour be|fe --target <repo>` copies the flavour into a repo.
The backend is **package-by-layer** (`core/src/main/kotlin/harbor/<layer>/` + `kafka_client`), so no folder names a
business area: the kit and the graph derive the bounded context from the class-name prefix (`docs-repo/contexts.yml`).

| Lever | What ships | Effect |
|---|---|---|
| **Layered backend -> contexts by prefix** | `contexts.yml` (context -> BE prefixes, FE feature, spec prefix), `components.md` (layer, stereotype, injected deps, tables, `@docs`, `file:line` per class), `layers.instructions.md` (allowed layer dependencies, prefix naming) | "where is product1" = prefix filter + manager + injection chain, not a walk through 18 layer folders |
| **Content exclusion** (GitHub setting; VS Code and JetBrains) | `shared/copilot-content-exclusion.yml`: `target/` incl. `generated-sources`, `node_modules`, lockfiles, generated clients, fixtures, env configs | noise never enters context or the index; secrets guard |
| **Generated maps, lib-free** | `scripts/docs/gen-*.py` -> `docs/_generated/`: `codebase-map` (modules -> layers -> classes), `components` (class, layer, injected deps, tables), `api-index` (contract-first, `Tag` = context), `events`, `db-schema`, `jobs`, `routes`, `types-index`, `docs-tags` (+ `index.md`); `gen-all.py --check` | 1 row per thing with `file:line` instead of opening controllers |
| **Spec-to-code tags** `@docs <ID>` in KDoc/JSDoc | `docs-tags.md` + prompt `/find-spec-code` | `P1-001` -> exact declarations; no repo-wide search |
| **`AGENTS.md` + short `copilot-instructions.md`** | read order (map -> context manager -> `components.md` deps -> one range), contracts as source of truth, conventions the generators rely on, "never open" list | bounds every answer in both IDEs and the CLI |
| **Scoped rules** | `*.instructions.md` with `applyTo`: `api` (contract change before code), `calculations` (`utils/`), `kafka`, `migrations`, `tests`, `layers` (allowed layer dependencies, prefix naming); FE `features`, `api-client` | rules load only when relevant |
| **Read-only agents + prompts** | `code-reader` (max 3 files), `impact-analyst`; `/explain-module`, `/find-spec-code`, `/add-endpoint`, `/explain-feature` | cheap Q&A before any implementation agent |
| **Hooks + setup steps** | `.github/hooks/docs-maps.json` (`agentStop` -> `gen-all.py --check`), `copilot-setup-steps.yml` (JDK 21 / Node 24) | maps cannot go stale inside an agent session; coding agent can run the gate |
| **Code shape** | one `<Ctx>Manager` per context (KDoc + `@docs`), business-prefix class names, feature barrels + `*.types.ts`, file cap 400/300 lines via `check-file-size.py` with baseline | smaller files, cheaper reads |
| **IDE scope** | IntelliJ scopes by class-name prefix (`Product1*||Projection*`); `shared/workspaces/product1.code-workspace` (BE `core` sources + resources + FE feature + docs) | the model sees one bounded context |
| **MCP-free retrieval** | VS Code extension: `#docsLookup`, `#codeMap`, `#specToCode`, `#impact` + `@docs` participant (`vscode.lm.registerTool`, no runtime deps); JetBrains: `graph-query.py` + prompts | a few hundred tokens with badge + `file:line` instead of `@workspace` |
| **CI** | `ci/docs-maps.yml`: freshness + size gate on PR; on `main` publishes maps and contracts to the docs repo | maps stay true; docs repo consumes them unchanged |

Exercised against the simulated `backend/` and `frontend/` (§8). The springdoc/Dokka path in `ci-examples/` remains the richer
option *if* build plugins are later allowed; with a contract-first BE the regex generators cover where/which/who-calls questions without them.

### 3.13 Architectural knowledge graph (graphify / codegraph / tree-sitter assessed; in-house hybrid chosen)

| Tool family | How it works | Why not as-is |
|---|---|---|
| graphify | tree-sitter AST + LLM-extracted edges -> Leiden communities -> report | Python deps, non-deterministic edges, Claude-Code hooks, knows nothing of Spring/Kafka/Flyway |
| codegraph-style MCP servers | tree-sitter -> symbol graph -> graph DB -> MCP tools | **requires MCP** + a DB; tens of thousands of symbol nodes, unusable without the tool JetBrains cannot host |
| aider repo-map | tags -> PageRank -> top symbols within a token budget | tree-sitter lib; but *rank + budget* is library-free and the best single idea |

**Key insight.** Docs, Jira analytics and test design reason about *architectural* nodes (context, endpoint, manager / service / dao class, calculator,
table, topic, FE route/hook, spec ID). That graph has a few hundred nodes and is extractable with zero new libraries:

| Layer | Mechanism (lib-free) | Shipped |
|---|---|---|
| Nodes + approximate edges | `scripts/gen-graph.py` joins `generated/be/*` (incl. `components.md`: `class:` nodes, `depends-on` / `persists-to` edges) + `generated/fe/*` + `@docs` tags; `docs-repo/contexts.yml` groups BE classes by name prefix into `context:<name>` nodes, which with the FE feature of the same name form one community | `graph.json`, `graph/<community>.md`, `REPO_MAP.md` (PageRank + `--budget`) |
| Precise BE edges | the running Spring context (`spring-boot-starter-test` already present): bean dependencies, handler mappings, Kafka listener registry, JPA metamodel | template `be/templates/GraphExportTest.kt` (verify on the real repo) |
| Precise FE edges | TypeScript compiler API (`typescript` already a devDependency): `uses`/`renders`, `api.GET('<path>')` literals resolved to operations | `fe/scripts/docs/gen-graph-fe.ts` |
| Query | BFS over `graph.json` | `#impact` (VS Code), `scripts/graph-query.py --node / --files / --find` (CLI, CI) |
| Freshness | `gen-graph.py --check` in docs CI; code CI publishes `graph-export-*.json` | wired |

Skipped on purpose: LLM-extracted edges (audit, cost, determinism) and Leiden (overkill at ten contexts). Decision: **build the
hybrid, port none of the tools.** Revisit tree-sitter (WASM) only if the Spring context cannot boot in CI.

### 3.14 Language: source language at the edges, English in the repository

Legacy pages are written in the organisation's source language; the repository is English (cheaper tokens, English-centric
Gherkin/YAML/Jira tooling, one glossary). The source language lives only at the edges:

| Edge | Mechanism | Asset |
|---|---|---|
| Import | `confluence-migrator` translates while normalising; domain terms only via the glossary `Aliases` column; `source_lang` set, original title/terms into `aliases`; translated rules stay `draft` until a native-speaking owner verifies | `domain/glossary.md`, `features/_template.md` (`lang`, `source_lang`, `aliases`) |
| Search | `#docsLookup`, index scoring and `context-pack.py` free text match `aliases` | `vscode-extension/src/knowledge.ts`, `scripts/context-pack.py` |
| Chat | answer in the user's language, write files in English | `AGENTS.md` |
| Publish | `confluence-publish.py --lang <code>` -> prompt `translate-for-publish` renders a glossary-controlled page into `.publish/` (git-ignored) with a "machine-translated, English is authoritative" banner | `scripts/confluence-publish.py`, `.gitignore` |
| Jira / tests | work-item summaries may be rendered in the source language at push time; Gherkin stays English | - |

Risks: LLM translation of business rules -> human verification before `stable`; terminology drift -> the glossary is the only
allowed term source; regulators wanting the source language as the record -> publish that rendering with page history, Git/English stays authoritative.

## 4. Migration from Confluence
1. Export space(s) -> `confluence-import/<space>/` (REST + pandoc; `scripts/confluence-export.py`).
2. Triage list: keep / merge / obsolete (cheap, human, 1-2 days).
3. `confluence-migrator` per page: classify, merge into spec/ADR/glossary, verify claims against `generated/`; formula pages go
   to `calc-auditor`, which validates them against the calculator and its unit test (the prototype ships a deliberately
   outdated page for this exercise).
4. Replace Confluence pages with the published mirror + banner.

## 5. Roadmap

| Phase | Weeks | Deliverables |
|---|---|---|
| 0. Pilot | 1-2 | docs repo from the prototype (OKF bundle, validators, hooks, index builder in CI); code repos: `apply-kit.py`, content exclusion, file-size baseline, lib-free maps + contract publish + freshness gate (warn-only); one bounded context documented end-to-end with context packs: 2-3 specs, 2 calculations audited, work items, tests |
| 1. Generators + graph | 2-3 | `@docs` tagging of managers/calculators/barrels; `contexts.yml` complete; per-context workspaces; VS Code retrieval extension; architectural graph (`gen-graph.py` in docs CI, `GraphExportTest.kt`, `gen-graph-fe.ts`); coverage matrix in CI |
| 2. Migration | 3-6 | Confluence export + migration per context; every formula page audited; glossary complete; gates blocking |
| 3. Automation | 6-8 | Jira push, tests-repo PR flow, Confluence publish; `/coverage-report` as sprint input |
| 4. Hardening | ongoing | ADRs, HLD template use, metrics (§Step 8 of the plan): tokens per task, files opened, % specs verified, BR coverage |

## 6. Risks & mitigations
| Risk | Mitigation |
|---|---|
| Teams don't update docs | freshness gate + `agentStop` hooks + `doc-sync` agent does most of the work from generated diffs |
| Agents read the whole repo anyway | context pack is the mandated entry point; `AGENTS.md` forbids `@workspace`; measure files opened per task |
| Generated artifacts too large for context | per-context graph files, one row per class in `components.md`; packs budgeted; `REPO_MAP --budget`; `okf-validate` warns on size |
| Formula docs wrong, legacy pages trusted | worked examples copied from BE unit tests; `calc-auditor` audit table per concept; legacy pages marked unverified in packs |
| Confidential data leaks into docs/fixtures | synthetic-data rule in `AGENTS.md`; content exclusion; secret/PII scanning in CI |
| Jira/Confluence API access blocked | CSV fallback for Jira; Confluence publish optional (Git renders Markdown+Mermaid) |
| Copilot customisation formats change | plain Markdown/JSON files; `AGENTS.md` is cross-tool; hooks/skills are preview in JetBrains - CI enforces the same gates |
| OKF spec still young (v0.2); vendored Python | only `type` is mandatory; extension keys are ours; checkers vendored, licensed (`third-party/`) and pinned; the standard-library validator works without pyyaml |
| Regex generators miss unusual code shapes | contract-first index does not depend on annotations; `_not implemented_` rows surface gaps; conventions enforced via instructions |
| Spring context cannot boot in CI for `GraphExportTest` | `graph-export` profile with embedded/mocked infra; regex joiner alone still yields the graph (`approximate` edges) |
| Graph or maps become a second source of truth | derived only (`--check` gates, `generated.by: process:*`, hook denies hand edits) |
| Agents over-trust structural edges for behaviour | skill `code-graph`: structure here, formulas in `domain/calculations/`; `impact-analyst` outputs a "Verify" section |

## 7. Decisions requested
1. Approve Option C and the pilot on one bounded context (recommended: the context with the richest calculations and a
   contradicting legacy page, as in the prototype's `stress` / `product1`).
2. Confirm Git platform (GitHub / GitLab / Azure DevOps) to finalise CI YAML, hooks support and PR-creation scripts.
3. Confirm Jira & Confluence REST access from CI (or CSV/manual fallback).
4. Nominate owners per bounded context (frontmatter `owners`) and a native-speaking reviewer for migrated rules.
5. Approve OKF v0.2 as the bundle/frontmatter convention (§3.11) and the vendored okf-skills tooling.
6. Approve the code-repo kit (§3.12): `apply-kit.py`, GitHub content exclusion, lib-free generators + contract publish + CI
   gate, hooks, file-size cap, and the in-house VS Code extension (one internal security review) as the MCP substitute.
7. Approve the architectural graph (§3.13) and the two precise exporters; confirm `spring-boot-starter-test` and `typescript`
   exist in the real repos.
8. Approve the working model of §3.5-3.8: context pack as the mandatory entry point, `calc-auditor` sign-off before a
   calculation becomes `stable`, `/coverage-report` as the status source.
9. Approve the language policy (§3.14): English-only bundle; source language only at the edges.

See `IMPLEMENTATION-PLAN.md` for the step-by-step rollout and the list of reusable assets.

## 8. Prototype contents
The business case is synthetic (`BLUEPRINT.md`: a goods-trading company, two product groups, meetings, cover, scenarios,
stress tests, reports); it mirrors the real application's *shape* (contract-generated FE/BE, XLS imports by jobs, session
header, Kotlin calculations, four cumulative tables, admin parameters, PDF via Kafka, outdated legacy pages) with no real
names, values or identifiers. Everything is standard-library Python 3.11+; nothing to install beyond Python.

### 8.1 Simulated code repositories (`backend/`, `frontend/`)
| Item | State |
|---|---|
| BE layout | `backend/pom.xml` modules `core` (package-by-layer `core/src/main/kotlin/harbor/<layer>/`, 18 layers, one `<Ctx>Manager` per bounded context) and `kafka_client`, plus `init_docker_compose/`; 10 bounded contexts by class-name prefix (`docs-repo/contexts.yml`); calculators in `utils/`, unit tests in `core/src/test/kotlin/harbor/utils/` |
| REST contract | `backend/core/src/main/resources/openapi/harbor-api.yaml`: 34 operations, shared session-header parameter; `openapi/harbor-events.yaml`: 5 topics (`kafka_client/.../harbor/kafka/Topics.kt`) |
| External contracts | `backend/core/src/main/resources/api/`: client-registry, market-data, cover-provider, document-service, file-exchange |
| DB | 9 Flyway migrations `V1__..V9__` per the blueprint (four projection tables, `parameter_set`); counts: see `generated/be/db-schema.md` after `gen-all.py` |
| FE | 9 feature folders mirroring the bounded contexts, `openapi-fetch` client with the session-header middleware, object routes; routes/types/tags counts: see `generated/fe/*.md` |
| Kit applied | `AGENTS.md`, `.github/` (instructions, agents, prompts, hooks, setup steps), `scripts/docs/`; maps in `docs/_generated/` are build outputs (`gen-all.py`) |

### 8.2 Docs repo (`docs-repo/`)
| Item | State |
|---|---|
| Specs | `CLI-001`, `SES-001`, `P1-001` stable (human-reviewed); `STR-001` draft whose legacy page contradicts the code; `MKT-001`, `RPT-001` skeletons; `P2-001`, `COV-001`, `IMP-001`, `ADM-001` **deliberately missing** (`code only` in `REPO_MAP.md`) |
| Calculations | `client_role_classification`, `monthly_projection`, `stress_test_monthly` with worked examples; `cover_ratio`, `scenario_price_path` draft; `peer_benchmark_simulation` missing on purpose |
| Legacy pages | `confluence-import/HARBOR/stress-test-calculation.md` **deliberately outdated** (threshold, missing transport delta); two partly correct pages |
| Worked examples | `work-items/P1-001.yml`, `test-design/features/STR-001.feature` + fixture; `generated/analytics/coverage-matrix.md` |
| Customisation | `AGENTS.md`, short `copilot-instructions.md`, 6 scoped instructions, 8 agents (`analyst`, `spec-writer`, `doc-sync`, `calc-auditor`, `test-designer`, `architect`, `impact-analyst`, `confluence-migrator`), 12 prompts, 11 skills (`write-feature-spec`, `calculation-spec`, `jira-work-items`, `gherkin-test-design`, `code-graph`, `task-context`, `legacy-page-audit`, `docs-analytics`, `okf`, `okf-validate`, `okf-visualize`), hooks `docs-quality.json`, `copilot-setup-steps.yml`, CI `docs-quality.yml` |
| Scripts | `context-pack`, `graph-query`, `gen-graph`, `coverage-matrix`, `build-index`, `okf-validate`, `validate-frontmatter`, `validate-work-items`, `map-paths`, `check-freshness`, `collect-evidence` (`publish-local` deprecated), `hooks/guard-generated`; stubs `jira-push`, `confluence-export`, `confluence-publish`, `push-to-tests-repo` |

### 8.3 How to verify locally (nothing here is claimed as run)
```bash
python3 code-repo-kit/be/scripts/docs/gen-all.py --root ./backend;  ./code-repo-kit/fe/scripts/docs/gen-all.py --root ./frontend
python3 docs-repo/scripts/collect-evidence.py --graph     # collect + manifest, then gen-graph.py and build-index.py
python3 docs-repo/scripts/okf-validate.py --strict; python3 docs-repo/scripts/validate-frontmatter.py; python3 docs-repo/scripts/validate-work-items.py
python3 docs-repo/scripts/context-pack.py --task P1-001 --print;  ./docs-repo/scripts/graph-query.py --node spec:STR-001 --depth 2
python3 docs-repo/scripts/coverage-matrix.py;  ./code-repo-kit/apply-kit.py --flavour be --target ./backend --what-if
```
Expected: counts and spec coverage in `docs-repo/generated/graph/REPO_MAP.md`; `--check` variants exit 1 after adding an
operation to `openapi.yaml` without regenerating. In VS Code (`harbor.code-workspace`, folder `harbor-docs`): `/context-pack P1-001`,
`@analyst /jira-from-spec STR-001`, `/spec-skeleton-from-graph product2 P2-001`, `/audit-calculation stress_test_monthly`, `/coverage-report`.
