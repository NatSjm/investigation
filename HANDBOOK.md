# Handbook: how the agent-ready documentation system works, file by file

This is the reference. [GUIDE.md](GUIDE.md) is the tour and the from-zero checklist; this document explains every
piece and why it exists, so you can explain it to others and rebuild it in the real project.

Contents: 1 Problem and idea · 2 Core concepts (incl. why OKF) · 3 The docs repository, folder by folder ·
4 Scripts · 5 Agents · 6 Skills · 7 Prompts · 8 Instructions, hooks, CI · 9 The code-repo kit ·
10 The flows end to end · 11 Design decisions as questions and answers · 12 Vocabulary

---

## 1. The problem and the idea

Two repositories (a large layered Kotlin/Spring backend and a React frontend) and a Confluence space of pages that
are partly outdated. You want an analyst agent (GitHub Copilot) that produces Jira stories, test designs, HLDs and
status analytics from documentation alone, and only goes to the code when a fact must be verified. Constraints:
Copilot is the only harness, no MCP servers, no third-party agent frameworks, PowerShell for scripts, English in
files, synthetic data only.

The idea has four parts:

1. **The code repositories describe themselves.** Small scripts generate maps of the code (classes, endpoints,
   topics, tables, jobs, routes, types, documentation tags); the docs repo collects them and the contracts as one
   validated snapshot with a manifest of source commits (one collector, one pull request, no publishers in the code repos).
2. **The docs repository is the single source of truth** for functional knowledge: specs, calculations, glossary,
   architecture decisions. Confluence becomes a publish target. Every document carries metadata that says who wrote
   it, when it was verified, and when it goes stale.
3. **A graph joins both**: generated maps plus documentation tags become an architectural graph whose communities are
   the business contexts. "What is affected", "where is it", "what talks to what" are answered without opening code.
4. **Agents never search; they read a pack.** For each task a script assembles a budgeted context pack: the spec,
   its calculations, the graph neighbourhood, the contracts, the tables, related work. The analyst reads that and
   nothing else.

Everything else in the workspace serves one of those four parts.

---

## 2. Core concepts

### 2.1 Docs as code
Documentation lives in Git as Markdown, reviewed in pull requests, validated by scripts in CI, published outward.
Benefits that matter here: diffs and blame tell you what changed and when; validators enforce structure; agents can
read and write it with the same tools as code; Confluence pages cannot drift silently because they are rendered from
Git.

### 2.2 Generated maps
Each code repository has `scripts/docs/gen-*.ps1`, regex scanners that need no build. They produce
`docs/_generated/*.md`: one row per class, operation, topic, table, job, route, type, or `@docs` tag, each with
`file:line`. They exist so that an agent reads a 100-line table instead of 150 source files, and so that the docs
repo can be verified against the code mechanically. The maps are checked for freshness on every PR.

### 2.3 Bounded contexts by name prefix (`contexts.yml`)
The backend is layered (`api/`, `manager/`, `service/`, `dao/` ...), so a folder holds every business area. The
business area of a class is therefore its **name prefix**: `Product1Manager`, `ProjectionService`, `ProjectionDao`
belong to `product1`. `docs-repo/contexts.yml` maps each context to its spec prefix (`P1`), its frontend feature
folder (`src/features/product1`) and its backend prefixes. Longest prefix wins; unmatched classes are `shared`. The
graph, the context pack, the migration board and the traceability globs all read this one file.

### 2.4 Traceability IDs
Specs are `<CTX>-<NNN>` (`P1-001`), business rules `BR-<ID>-<n>`, calculations `snake_case`
(`stress_test_monthly`). The code carries the same IDs as `@docs <ID>` KDoc/JSDoc tags on managers, barrels and
calculators. Work items cite BR-IDs in acceptance criteria; Gherkin scenarios carry `@BR-...` tags. This is what
makes "which rules have a story and a test" a script, not an opinion.

### 2.5 OKF: the Open Knowledge Format, and why we use it
OKF v0.2 is a small convention for a folder of Markdown meant to be consumed by agents. We adopted it instead of
inventing our own metadata because it already defines the things we would have had to define anyway:

- **Every document is a concept with YAML frontmatter**: `type`, `description`, `status`, `generated: {by, at}`,
  `verified: {by, at}`, `stale_after`, `sources[]`. A document without a type is a validation error.
- **Actors are typed**: `copilot/<agent>`, `human:<id>`, `process:<ci-job>`. Only `human:` counts as review. From
  this, the index derives a **trust badge** for every concept: *human-reviewed*, *machine-confirmed*, *unverified*,
  *STALE* (past `stale_after`). The analyst reads the badge and labels its stories accordingly.
- **Provenance**: `sources[]` with per-claim footnotes `[^id]`. A migrated Confluence page is always a source. A
  reader can trace any sentence to where it came from.
- **Progressive disclosure**: every folder has a generated `index.md`, one line per concept with description and
  badge. Agents navigate index to index and open only what they need; they never list directories. `README.md` is
  forbidden inside the bundle so that there is exactly one entry file per folder.
- **A lifecycle log** (`log.md`): created, verified, deprecated, regenerated.
- **A validator** (`okf-validate.ps1`, plus the reference Python checker in CI) that fails the build when any of the
  above is missing.
- **Attested Computation**, a concept type for formulas: parameters, an executor (the unit test), worked examples,
  and the sanctioned code shape. Agents bind parameters; they never re-derive a formula.

What we would lose without it: no machine-readable trust, so the analyst could not tell a verified rule from a draft;
no provenance, so legacy claims and verified facts would look the same; no indexes, so agents would list and grep
directories; no standard validator, so every rule would be a code review comment. The cost is the frontmatter block,
which agents never see (the pack strips it) and people can fold. Our repository-specific keys (`id`, `context`,
`code_refs`, `api`, `events`, `tables`, `calculations`, `jira`, `tests`) are allowed extensions.

### 2.6 Context packs
`scripts/context-pack.ps1 -Task <x>` writes `.context/<task>.md`: a ranked, budgeted (default 500 lines) selection
for one task. Sections in priority order: subject and badge, spec body, calculations, graph neighbourhood,
contracts, tables, related work items and tests, legacy pages, and a footer naming what was truncated. Lower
sections are cut first. The pack is deterministic, attachable to a PR, and cheap: one read instead of twenty tool
calls. When it is not enough, the escalation order is fixed (wider budget, follow the pointer, deeper graph, a second
pack, one named line range, then it is a documentation gap).

### 2.7 The architectural graph
`gen-graph.ps1` turns the maps into nodes (`context:`, `class:`, `endpoint:`, `topic:`, `table:`, `feature:`,
`route:`, `component:` (feature components and, in community `shared-ui`, the shared component library), `hook:`, `channel:` (browser `BroadcastChannel`, the frontend counterpart of a topic), `spec:`) and edges (`depends-on` from constructor injection, `persists-to` from
tables, `handles`, `publishes`, `consumes`, `calls`, `documents`). Communities are the contexts. A small PageRank
ranks nodes so that `REPO_MAP.md` fits a budget; each context gets its own `<context>.md`; `graph.json` serves the
query script and the VS Code tool. Optional precise exports (a Spring-context test, a TypeScript-compiler script)
override the regex edges when present.

### 2.8 Copilot customisation primer
GitHub Copilot reads, per repository: `AGENTS.md` (cross-tool, read by Chat, CLI, JetBrains and the cloud coding
agent), `.github/copilot-instructions.md` (Copilot-only supplement), `.github/instructions/*.instructions.md`
(rules applied to files matching `applyTo` globs), `.github/agents/*.agent.md` (custom agents with a tool list and
`handoffs`), `.github/prompts/*.prompt.md` (slash commands that pick an agent and carry arguments),
`.github/skills/<name>/SKILL.md` (procedures loaded when their description matches the task),
`.github/hooks/*.json` (commands run before a tool call or when an agent stops), and
`.github/workflows/copilot-setup-steps.yml` (environment for the cloud coding agent). Content exclusion is a
repository setting. No MCP, no plugins, no frameworks are needed for any of this.

### 2.9 The token strategy
Finding is removed by maps, graph and packs. Reading is shrunk by file-size caps, content exclusion, per-context
workspaces, the contract as the single thing to read instead of generated clients, and a VS Code extension that
replaces `@workspace` with four retrieval tools returning a few hundred tokens with `file:line`. Every agent
procedure says what it may open and how much.

---

## 3. The docs repository, folder by folder

```
docs-repo/
  index.md                    root index (okf_version, "Start here" block, generated section list)
  log.md                      lifecycle log, append-only
  AGENTS.md                   the rules every agent reads: read order, hard rules, commands, agents list
  README.md                   entry point for people: quick start, layout, local checks
  contexts.yml                context -> spec prefix, FE feature, BE class-name prefixes
  docs-map.yml                code path globs -> specs (freshness gate, impact of PRs)
  .markdownlint-cli2.yaml     Markdown lint config
  .gitignore                  .context/ (packs), .publish/ (translations), confluence _raw/
  features/                   feature specs, one folder per context
    _template.md              the spec template with every frontmatter key explained
    conventions.md            ID scheme, BR numbering, size caps, section order, lifecycle of one spec
    <ctx>/<CTX>-NNN.md        the specs; <ctx>/index.md generated
  domain/
    glossary.md               canonical terms; Aliases column for legacy / source-language wording
    context-map.md            the contexts, prefixes, entry points, relationships
    calculations/             one Attested Computation per calculation: formula, parameters, worked examples, audit
      _template.md
  architecture/
    overview.md, integrations.md, adr/NNNN-*.md, adr/template.md, (hld/<ID>.md)
  flows/                      cross-context behaviour (`type: Flow`): trigger, participants, steps with file:line, invariants, source map
    _template.md, client-presentation.md
  confluence-import/          quarantine for exported legacy pages; README with rules + inventory; <SPACE>/_done/
  generated/                  collected from the code repos by scripts/collect-evidence.ps1 (manifest.yml names the source commits); never edited by hand
    be/, fe/                  the maps; openapi/, asyncapi/ the contracts; graph/ the graph; analytics/ the coverage matrix
  migration/                  migration board(s) written by migration-status.ps1 / migration-lead
  work-items/                 analyst output: <ID>.yml per feature, _schema.yml, README
  test-design/                test-designer output: features/<ID>.feature, fixtures/, README with the step vocabulary
  scripts/                    PowerShell 7 scripts (section 4) + hooks/guard-generated.ps1 + README
  ci-examples/                CI fragments for the code repos
  third-party/                vendored OKF skills (MIT) and licences
  .github/                    Copilot customisation: agents, skills, prompts, instructions, hooks, workflows
  .context/                   context packs (git-ignored)
```

Key files worth reading once: `AGENTS.md` (the contract between people and agents), `features/_template.md`
(every field explained), `features/conventions.md` (how a spec is written run by run), `contexts.yml`.

---

## 4. Scripts (`docs-repo/scripts/`, PowerShell 7, no modules)

| Script | What it does | Input | Output | When |
|---|---|---|---|---|
| `context-pack.ps1 -Task <x> [-Budget N] [-Print]` | builds the task-scoped pack (2.6) | spec ID, calculation, graph node or free text | `.context/<task>.md` | start of every agent task |
| `graph-query.ps1 -Node <id> -Depth n` / `-Files <paths>` / `-Find <text>` | queries the graph: neighbourhood, impacted specs for changed files, text search | `generated/graph/graph.json` | text (or `-Json`) | impact questions, CI PR comment, IntelliJ users |
| `gen-graph.ps1 [-Check]` | joins BE/FE maps + `@docs` tags + `docs-map.yml` rows (+ precise exports) into the graph; a mapping row gives the same `implemented-by` edges as a tag, so tags are optional at the start | `generated/be`, `generated/fe`, `contexts.yml` | `generated/graph/REPO_MAP.md`, `<context>.md`, `graph.json`; prunes orphan community files | after publish; `-Check` in CI |
| `build-index.ps1 [-Check]` | regenerates every `index.md` with trust badges | frontmatter of all concepts | `index.md` per folder | after any edit; hook; CI |
| `okf-validate.ps1 [-Strict]` | OKF conformance: frontmatter, types, actors, staleness, provenance warnings | the bundle | errors/warnings | hook; CI; before commit |
| `validate-frontmatter.ps1` | repo-specific keys: ID format, BR numbering, calculation links on specs and calculations | `features/`, `domain/calculations/` | OK / errors | hook; CI |
| `validate-work-items.ps1` | work-item YAML against `_schema.yml`: BRs exist, estimates Fibonacci, subtasks <= 8 h | `work-items/*.yml` | OK / errors | after analyst runs; CI |
| `coverage-matrix.ps1` | BR -> story -> scenario coverage, badges, calculation audits | specs, work items, feature files | `generated/analytics/coverage-matrix.md|json` | analytics questions; CI check |
| `map-paths.ps1` | changed code paths -> affected specs | stdin paths + `docs-map.yml` | spec list | doc-sync, CI |
| `check-freshness.ps1` | CI gate in the code repos: mapped path changed but `last_verified` not bumped and no `docs-not-affected` label | PR diff, specs | pass/fail | code-repo PRs |
| `collect-evidence.ps1 [-Generate] [-Graph] [-DryRun]` | the single evidence collector: stages maps + contracts from the code checkouts, validates the candidate (frontmatter, OpenAPI/AsyncAPI headers, unresolved `$ref`), replaces the collector-owned sets under `generated/` (deletions included), writes `generated/manifest.yml` (source commits, dirty flag, sha256 per file); no-op when nothing changed | the code repos' `docs/_generated` and contracts | `generated/be|fe|openapi|asyncapi/**`, `manifest.yml` | local loop; CI `ci-examples/collect-evidence.yml` (manual + nightly, one PR per snapshot) |
| `publish-local.ps1` | deprecated name of `collect-evidence.ps1`, forwards to it | - | - | - |
| `migration-status.ps1 -Scope <ctx|all>` | which lifecycle runs are still due per context, with commands | `contexts.yml`, specs, calculations, docs-tags, REPO_MAP, pending pages | `migration/<scope>.md` | planning; migration-lead |
| `hooks/guard-generated.ps1` | Copilot `preToolUse` hook: denies edits under `generated/**` and of `index.md` | hook payload | permission decision | every agent edit |
| `confluence-export.ps1`, `confluence-publish.ps1`, `jira-push.ps1`, `push-to-tests-repo.ps1` | **stubs** describing the intended integrations (export/import of legacy pages, publish back, Jira REST, tests repo PR) | - | - | to be implemented per environment |

All validators return a non-zero exit code on failure so the same commands run in hooks and CI.

---

## 5. Agents (`docs-repo/.github/agents/`)

Each file is YAML frontmatter (`name`, `description`, `tools`, optional `handoffs`) plus the procedure in prose.
`tools: ['read','edit','search','execute']` are Copilot's tool aliases. Handoffs appear as buttons after a run.

| Agent | Role | Reads | Writes | Hands off to |
|---|---|---|---|---|
| `analyst` | business/system analyst: epic, stories, subtasks with Gherkin criteria; analytics mode for coverage/freshness questions | the pack only; source only at a `file:line` the pack names and only when blocked | `work-items/<ID>.yml`, open questions in the spec | `test-designer`, `spec-writer` |
| `spec-writer` | writes or refreshes a feature spec from the graph and one manager file; marks everything unsourced as unverified | pack, `generated/graph/<ctx>.md`, contracts, `manager/<Ctx>Manager.kt` | `features/<ctx>/<ID>.md`, `docs-map.yml`, `log.md` | `analyst`, `calc-auditor` |
| `doc-sync` | keeps specs in sync with code changes from the generated diffs with minimal source reading | `map-paths`, `graph-query -Files`, contracts, maps | change-log rows, `last_verified`, stubs for unmapped contexts | `calc-auditor` for utils changes |
| `calc-auditor` | verifies a calculation concept or a legacy formula page against the calculator and its unit test; never changes numbers | two source files only | `## Audit <date>` table, status, open questions | `spec-writer` |
| `confluence-migrator` | converts one legacy page into the right concept: merge new facts, mark conflicts, extract glossary terms, cite the page | the page, the pack, `generated/` | merged concept, glossary, page moved to `_done/` | `calc-auditor` for formula pages |
| `test-designer` | Gherkin scenarios and synthetic fixtures from the spec's BRs and worked examples | pack | `test-design/features/<ID>.feature`, fixtures | - |
| `architect` | HLD (C4/arc42 Mermaid), ADRs, integration map refresh | `architecture/`, graph, contracts, spec frontmatter only | `architecture/hld/<ID>.md`, `adr/NNNN-*.md` | - |
| `impact-analyst` | blast radius of a change from the graph, as a checklist | `generated/graph/` | checklist in chat/file | - |
| `migration-lead` | plans and tracks the migration: runs due per context, order, blockers; proposes, never edits concepts | `migration-status` output, REPO_MAP, index badges | `migration/<scope>.md` lead notes | `spec-writer`, `confluence-migrator`, `calc-auditor` |

Common contract of all agents: build the pack first; files first, chat under 15 lines; set
`generated.by: copilot/<agent>`; never write `verified.by: human:*`; never edit `generated/**`; finish with
validate, build-index, log.

---

## 6. Skills (`docs-repo/.github/skills/<name>/SKILL.md`)

A skill is a procedure Copilot loads when the task matches its description, shared by all agents. References live
beside it under `references/`.

| Skill | Teaches | Used by |
|---|---|---|
| `task-context` | build and consume a pack; section anatomy; the escalation when it is not enough | everyone |
| `spec-lifecycle` | the four runs of one spec, owner, inputs, outputs, exit state; per-run review checklist | writers, lead, reviewers |
| `write-feature-spec` | spec structure, numbering, `source-priority.md` (cheapest source first) | spec-writer, doc-sync |
| `calculation-spec` | Attested Computation: formula, parameters, worked examples from the test, conventions | calc-auditor, spec-writer |
| `legacy-page-audit` | claims table with MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED; two files only | calc-auditor, migrator |
| `code-graph` | answer where/what-talks-to-what from the graph; `graph-schema.md`; `subtask-mapping.md` (node kind -> subtask type) | analyst, impact-analyst, test-designer |
| `jira-work-items` | slicing heuristics, estimates, acceptance-criteria conventions | analyst |
| `gherkin-test-design` | step vocabulary, coverage checklist | test-designer |
| `docs-analytics` | answer coverage/freshness/status questions from the matrix and badges | analyst |
| `okf`, `okf-validate`, `okf-visualize` | author/maintain/consume the bundle; run the validators; render the knowledge graph | everyone; CI |

---

## 7. Prompts (`docs-repo/.github/prompts/*.prompt.md`, typed as `/name`)

| Prompt | Agent | Does |
|---|---|---|
| `/context-pack <x>` | - | builds the pack and summarises what it contains and lacks |
| `/jira-from-spec <ID>` | analyst | work items YAML |
| `/coverage-report` | analyst | analytics answer from the matrix and badges |
| `/tests-from-spec <ID>` | test-designer | Gherkin + fixtures |
| `/hld-from-spec <ID>` | architect | HLD |
| `/impact-from-graph <node|file>` | impact-analyst | blast radius checklist |
| `/spec-skeleton-from-graph <ctx> <ID>` | spec-writer | Run 1: new spec from graph + manager |
| `/spec-from-code <ID>` | spec-writer | refresh an existing spec against contracts and maps |
| `/audit-calculation <name|ID|page>` | calc-auditor | Run 3: audit table |
| `/migration-plan <ctx|all>` | migration-lead | migration board with lead notes |
| `/okf-produce`, `/okf-validate` | - | capture knowledge as concepts; validate and fix conformance |
| `/translate-for-publish <path> <lang>` | - | glossary-controlled rendering for Confluence readers, not committed |

---

## 8. Instructions, hooks, CI

**Instructions** (`.github/instructions/*.instructions.md`, applied by `applyTo` glob): `features` (spec rules),
`calculations` (Attested Computation rules), `confluence-import` (quarantine rules), `generated` (read-only),
`test-design`, `work-items`. They are short because the detailed procedures are in skills.

**Hooks** (`.github/hooks/docs-quality.json`): `preToolUse` runs `guard-generated.ps1` (blocks edits under
`generated/**` and of `index.md`); `agentStop` runs `build-index`, `okf-validate -Strict`, `validate-frontmatter`,
`validate-work-items`. An agent cannot finish with an invalid bundle.

**CI** (`.github/workflows/docs-quality.yml`): markdownlint, frontmatter and work-item validation, both OKF
validators, index and graph and coverage-matrix freshness checks, impacted specs for the PR, the OKF graph artifact,
link check, Mermaid syntax, OpenAPI/AsyncAPI lint; on main, publish changed concepts to Confluence (stub).
`copilot-setup-steps.yml` prepares the cloud coding agent's environment.

---

## 9. The code-repo kit (`code-repo-kit/`)

`apply-kit.ps1 -Flavour be|fe -Target <repo>` copies the flavour into a code repository. The kit is the source of
truth; existing files are overwritten.

| Part | Backend (`be/`) | Frontend (`fe/`) | Why |
|---|---|---|---|
| `AGENTS.md` | <= 60 lines: purpose, read order (map -> manager -> one range), contracts, conventions, commands | same for feature folders (map -> barrel -> one range) | the first thing every Copilot surface reads |
| `.github/copilot-instructions.md` | never-open list, output discipline, agents/prompts/tools | same | Copilot-specific supplement |
| `.github/instructions/` | `api` (contract-first), `calculations` (utils), `kafka`, `migrations`, `tests`, `layers` (allowed dependencies between layers, prefix rule) | `api-client`, `features` | path-scoped rules, loaded only when editing matching files |
| `.github/agents/` | `code-reader` (read-only navigator, max 3 files), `impact-analyst` | `code-reader` | cheap answers before any implementation agent |
| `.github/prompts/` | `/explain-module`, `/find-spec-code`, `/add-endpoint` | `/explain-feature` | repeatable questions |
| `.github/hooks/docs-maps.json` | `agentStop` -> `gen-all.ps1 -Check` | same | an agent cannot leave stale maps |
| `.github/workflows/copilot-setup-steps.yml` | JDK 21 + `mvn generate-sources` | Node 24 | cloud coding agent environment |
| `scripts/docs/gen-*.ps1`, `gen-all.ps1` | codebase-map (modules, layers), components (one row per class), api-index (contract-first), events, db-schema, jobs, docs-tags | codebase-map (features + Channels column for `BroadcastChannel`s), components (shared library: props, used by), routes, types-index, docs-tags, `gen-graph-fe.ts` | the maps (2.2) |
| `templates/GraphExportTest.kt` | precise graph export from the Spring context (test scope) | - | optional precision over regex |
| `shared/` | `check-file-size.ps1` (line cap with baseline), `copilot-content-exclusion.yml`, `workspaces/product1.code-workspace` (per-context multi-root workspace), `ide-setup.md` | same | token hygiene, less noise |
| `ci/docs-maps.yml` | PR: maps fresh + size budget, nothing else | same | the code repo keeps describing itself; publication belongs to the docs repo's collector, so no docs-repo credentials here |
| `vscode-extension/` | `#docsLookup`, `#codeMap`, `#specToCode`, `#impact`, chat participant `@docs` | same | retrieval tools without MCP |

---

## 10. The flows end to end

### A. A code change reaches the documentation
1. Developer changes `ProjectionService.kt`, opens a PR. CI runs `gen-all.ps1 -Check` (maps must be regenerated in
   the PR) and the file-size gate. `check-freshness.ps1` (when enabled) requires `last_verified` of P1-001 to be
   bumped or the label `docs-not-affected`.
2. Nightly, or on demand, the docs repo's collector (`collect-evidence.yml` -> `collect-evidence.ps1`) checks out
   backend and frontend read-only, runs their generators, validates the snapshot, replaces `generated/`, records the
   source commits in `generated/manifest.yml`, rebuilds the graph and opens ONE PR labelled `generated`; the body lists
   the source paths changed since the previous manifest, mapped to specs through `docs-map.yml`. A second run against
   unchanged sources opens nothing. Lower latency, when needed, is a `repository_dispatch` from the code repos' CI.
3. In the docs repo, `doc-sync` runs on that PR: `map-paths` and `graph-query -Files` name the specs in the blast
   radius; it compares their API/Events/Data sections with the new contracts and maps, updates them, appends a
   change-log row, sets `last_verified`, flags calculations for `calc-auditor` if `utils/` changed, and stubs any
   context that has no spec. Hooks validate; a person reviews and merges.

### B. A spec is written (the four runs, see `spec-lifecycle`)
Run 1 skeleton from the graph and the manager (`spec-writer`), Run 2 legacy pages merged one per run
(`confluence-migrator`), Run 3 calculation audit (`calc-auditor`), Run 4 owner decision (a person adds
`verified.by`). One run, one review, one commit. `migration-status.ps1` says what is still due.

### C. Confluence migration
Space export to HTML, imported into `confluence-import/<SPACE>/` with a header block by the importer script
(spec in [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md)), triaged in the inventory table, then flow B. Pages are
evidence, never copied; numbers always go through Run 3.

### D. An analyst task
`/context-pack <task>` resolves the task to a spec, builds the pack. `@analyst /jira-from-spec <ID>` reads it, checks
the badge, slices stories per `jira-work-items`, derives subtasks per graph node kind, writes `work-items/<ID>.yml`,
validates it. Gaps become `questions[]` and, if blocking, open questions in the spec. Handoff buttons: test design,
spec refresh.

### E. Tests and Jira
`test-designer` writes `test-design/features/<ID>.feature` with `@BR` tags and synthetic fixtures using the shared
step vocabulary; `push-to-tests-repo.ps1` (stub) hands them to the tests repository. `jira-push.ps1` (stub) creates
the epic and stories and writes back keys.

### F. Analytics
`coverage-matrix.ps1` computes BR coverage by stories and scenarios, badges and staleness. `/coverage-report`
answers from it and from the index badges, including `code only` contexts from REPO_MAP. `/impact-from-graph`
answers change questions from the graph alone.

### G. Measuring whether it works
From the pilot onward: Copilot premium requests per user per week, share of `@workspace` versus `#file`/pack
usage, PR review time, number of `_not implemented_` rows in the API index, number of open questions per spec,
and the human analyst's assessment of agent-written stories (the baseline recorded in the pilot).

---

## 11. Design decisions as questions and answers

**Why PowerShell and regex instead of a parser or a library?** No dependencies to approve, runs on Windows, macOS and
CI runners unchanged, and a regex over Kotlin declarations is enough for maps that carry `file:line`; precision
comes from the optional compiler-based exports when needed.

**Why no MCP?** Not permitted in the environment. The VS Code extension provides the same retrieval through the
public API; scripts cover JetBrains and CLI.

**Why business contexts by class-name prefix?** Because the real backend is layered and we did not want to
restructure it. One file, `contexts.yml`, turns the layered code into contexts for the graph and the docs.

**Why is the frontmatter so long?** Only six fields are OKF requirements. The rest are traceability fields that make
packs, badges, the freshness gate and the matrix possible. Agents never see them (the pack strips them); people fold
them; Confluence readers never see them. They can be script-generated from the graph later.

**Why packs instead of letting the agent search?** Deterministic, budgeted, reviewable, cheap, and they carry
provenance. A searching agent reads whatever matched, in whatever order, and spends its context on the wrong files.

**Why one Confluence page per run?** Reviewable diffs and a per-page audit trail in `sources[]` and `log.md`. A
page is evidence; a person has to judge every conflict.

**Why may calc-auditor open only two files?** The calculator and its test are the truth about a formula; anything
else is noise and tokens. The test also supplies the worked examples, so numbers are copied, never re-derived.

**Why English in files when the source language is different?** One language for IDs, search and agents; the
glossary's Aliases column keeps the source-language terms findable, and `translate-for-publish` renders the other
language for Confluence readers.

**Why synthetic data only?** Docs, fixtures and packs are read by agents and may be attached to PRs. No client
identifiers or contract values may ever be in them.

**Why is Confluence not the source?** It has no diffs, no validation, no provenance and no machine-readable trust.
It stays the reading surface, rendered from Git with a banner.

**Why a separate docs repository instead of docs in each code repo?** Specs span both repositories, the analyst must
not need the code checkouts, access can differ, and one collector in it can pull from every code repo with a
read token, instead of every code repo needing write access to it.

---

## 12. Vocabulary of this system

- **Concept**: one Markdown file with OKF frontmatter; the unit of documentation.
- **Bundle**: the whole docs repository as one OKF unit, with a root `index.md`.
- **Trust badge**: human-reviewed / machine-confirmed / unverified / STALE, derived from `verified`, `generated`, `stale_after`.
- **Context pack**: the budgeted per-task selection in `.context/<task>.md`.
- **Bounded context**: a business area; in code a set of class-name prefixes plus one FE feature; in docs one spec folder and one spec prefix.
- **Map**: a generated table about the code (`generated/be|fe/*.md`).
- **Graph**: nodes and edges joined from the maps; `REPO_MAP.md`, `<context>.md`, `graph.json`.
- **Run**: one agent execution of one lifecycle step, followed by one human review and one commit.
- **Attested Computation**: the OKF type for a calculation with parameters, executor, worked examples.
- **Code only**: a context or calculation present in the code but without a concept; the backlog list in REPO_MAP.
- **Freshness gate**: the CI check that a PR touching a mapped path must bump `last_verified` or declare `docs-not-affected`.
- **Quarantine**: `confluence-import/`, where legacy pages wait as evidence until migrated.
