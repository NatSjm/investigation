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
Copilot is the only harness, no MCP servers, no third-party agent frameworks, standard-library Python for scripts, English in
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
4. **Agents start from a pack, not from a search.** For each task a script assembles a context pack: the subject
   whole, the graph neighbourhood, the contracts, the tables, related work, and pointers to its calculations, flows
   and imported pages. Every agent then walks the same six steps (2.6): the pack and its pointers, the documentation
   folders and the graph freely, code last - through the maps and then freely for the analyst, at a named line for
   the others - and whatever code says is evidence, never a rule.

Everything else in the workspace serves one of those four parts.

---

## 2. Core concepts

### 2.1 Docs as code
Documentation lives in Git as Markdown, reviewed in pull requests, validated by scripts in CI, published outward.
Benefits that matter here: diffs and blame tell you what changed and when; validators enforce structure; agents can
read and write it with the same tools as code; Confluence pages cannot drift silently because they are rendered from
Git.

### 2.2 Generated maps
Each code repository has `scripts/docs/gen-*.py`, regex scanners that need no build. They produce
`docs/_generated/*.md`: one row per class, operation, topic, table, job, route, type, or `@docs` tag, each with
`file:line`. They exist so that an agent reads a 100-line table instead of 150 source files, and so that the docs
repo can be verified against the code mechanically. The maps are checked for freshness on every PR.

### 2.3 Bounded contexts by name prefix (`contexts.yml`)
The backend is layered (`api/`, `manager/`, `service/`, `dao/` ...), so a folder holds every business area. The
business area of a class is therefore its **name prefix**: `Product1Manager`, `ProjectionService`, `ProjectionRepository`
belong to `product1`. `docs-repo/contexts.yml` maps each context to its spec prefix (`P1`), its frontend feature
folder (`src/features/product1`) and its backend prefixes. Longest prefix wins (an entry with `*` matches anywhere in
the name: `"*StressTest"` for `Product1StressTestUtils`); unmatched classes are `shared`. The
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
  forbidden inside the bundle so that there is exactly one entry file per folder. The context pack (2.6) keeps the
  principle: a change request reads the whole slice, a question reads one section of the narrowest subject.
- **A lifecycle log** (`log.md`): created, verified, deprecated, regenerated.
- **A validator** (`okf-validate.py`, plus the reference Python checker in CI) that fails the build when any of the
  above is missing.
- **Attested Computation**, a concept type for formulas: parameters, an executor (the unit test), worked examples,
  and the sanctioned code shape. Agents bind parameters; they never re-derive a formula.

What we would lose without it: no machine-readable trust, so the analyst could not tell a verified rule from a draft;
no provenance, so imported claims and verified facts would look the same; no indexes, so agents would list and grep
directories; no standard validator, so every rule would be a code review comment. The cost is the frontmatter block,
which agents never see (the pack strips it) and people can fold. Our repository-specific keys (`id`, `context`,
`code_refs`, `api`, `events`, `tables`, `calculations`, `jira`, `tests`) are allowed extensions.

### 2.6 Context packs
`scripts/context-pack.py --task <x>` writes `.context/<task>.md`, the recorded slice of one task: a Contents with the
line range of every section; the subject whole with its badge (spec body, calculation concept, flow with the rules it
cites, or the overview of a context); the computed sections no file shows (graph neighbourhood with `file:line`,
contract operations and payloads, table pages with their datasets, work items and tests, the merged slice of several
subjects); and pointers - one line with path and badge - to the calculations the spec uses, the flows it takes part in
and the imported pages that mention it. Nothing is truncated (`--budget N` exists for a tool with a hard limit and no
procedure uses it). Around the pack every agent walks the same **six steps**, for a question and a change request
alike (`.github/skills/task-context/SKILL.md`): resolve the subjects through the catalogue; build one pack; check the
badges; read what the task needs by the Contents and follow the pointers through the indexes; search the
documentation folders and the graph freely, rebuilding once with a neighbour when the record should carry it; read
code last - through the generated maps, then freely for a question that still blocks. How far each agent goes is one
table in the skill: the analyst all six, the spec-writer, doc-sync and calc-auditor to a named file, the others no code. Code gives evidence, never
a rule: `code-read <file:line>`, unverified, an Open question in the spec that the coverage matrix counts.

### 2.7 The architectural graph
`gen-graph.py` turns the maps into nodes (`context:`, `class:`, `endpoint:`, `topic:`, `table:`, `feature:`,
`route:`, `component:` (feature components and, in community `shared-ui`, the shared component library), `hook:`, `channel:` (browser `BroadcastChannel`, the frontend counterpart of a topic), `spec:`) and edges (`depends-on` from constructor injection, `persists-to` from
tables, `handles`, `publishes`, `consumes`, `calls`, `documents`). Communities are the contexts. A small PageRank
ranks nodes so that `REPO_MAP.md` fits a budget; each context gets its own `<context>.md`; `graph.json` serves the
query script and the VS Code tool. Optional precise exports (a Spring-context test, a TypeScript-compiler script)
override the regex edges when present.

### 2.8 Copilot customisation primer
GitHub Copilot reads, per repository: `AGENTS.md` (cross-tool, read by Chat, CLI, JetBrains and the cloud coding
agent), `.github/copilot-instructions.md` (Copilot-only supplement), `.github/instructions/*.instructions.md`
(rules applied to files matching `applyTo` globs), `.github/agents/*.agent.md` (custom agents with a tool list and
`handoffs`), `.github/prompts/*.prompt.md` (slash commands in the IDE chat that pick an agent and carry arguments; the CLI does
not load them, there you ask the agent to follow the file),
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
    glossary.md               canonical terms; Aliases column for imported / source-language wording
    context-map.md            the contexts, prefixes, entry points, relationships
    calculations/             one Attested Computation per calculation: formula, parameters, worked examples, audit
      _template.md
  architecture/
    overview.md, integrations.md, adr/NNNN-*.md, adr/template.md, (hld/<ID>.md)
  flows/                      cross-context behaviour (`type: Flow`): trigger, participants, steps with file:line, invariants, source map
    _template.md, client-presentation.md
  confluence-import/          quarantine for exported imported pages; README with rules + inventory; raw-html/<section>/ the HTML export as received,
                              <SPACE>/<section>/<slug>.md the imported pages (scripts/confluence-import.py), <SPACE>/_attachments/<slug>/ their images, <SPACE>/_done/
  generated/                  collected from the code repos by scripts/collect-evidence.py (manifest.yml names the source commits); never edited by hand
    be/, fe/                  the maps; openapi/, asyncapi/ the contracts; graph/ the graph; analytics/ the coverage matrix
  migration/                  migration board(s) written by migration-status.py / migration-lead
  work-items/                 analyst output: <ID>.yml per feature, _schema.yml, README
  test-design/                test-designer output: features/<ID>.feature, fixtures/, README with the step vocabulary
  scripts/                    Python 3.11+ scripts (section 4) + hooks/guard-generated.py + README
  ci-examples/                CI fragments for the code repos
  third-party/                vendored OKF skills (MIT) and licences
  .github/                    Copilot customisation: agents, skills, prompts, instructions, hooks, workflows
  .context/                   context packs (git-ignored)
```

Key files worth reading once: `AGENTS.md` (the contract between people and agents), `features/_template.md`
(every field explained), `features/conventions.md` (how a spec is written run by run), `contexts.yml`.

---

## 4. Scripts (`docs-repo/scripts/`, Python 3.11+, standard library only)

| Script | What it does | Input | Output | When |
|---|---|---|---|---|
| `context-pack.py --task <x> [--budget N] [--print]` | builds the task-scoped pack (2.6) | spec ID, calculation, graph node or free text | `.context/<task>.md` | start of every agent task |
| `graph-viewer.py [--community <id>]` | draws the graph in a self-contained HTML page (`.context/graph-viewer.html`, open in a browser): one community at a time, text filter, direct neighbours, node details with `file:line` | `generated/graph/graph.json` | HTML | looking at a community before writing its spec; showing the graph to a colleague |
| `graph-query.py --node <id> --depth n` / `--files <paths>` / `--find <text>` | queries the graph: neighbourhood, impacted specs for changed files, text search | `generated/graph/graph.json` | text (or `--json`) | impact questions, CI PR comment, IntelliJ users |
| `gen-graph.py [--check]` | joins BE/FE maps + `@docs` tags + `docs-map.yml` rows (+ precise exports) into the graph; a mapping row gives the same `implemented-by` edges as a tag, so tags are optional at the start | `generated/be`, `generated/fe`, `contexts.yml` | `generated/graph/REPO_MAP.md`, `<context>.md`, `graph.json`; prunes orphan community files | after publish; `--check` in CI |
| `build-index.py [--check]` | regenerates every `index.md` with trust badges | frontmatter of all concepts | `index.md` per folder | after any edit; hook; CI |
| `okf-validate.py [--path <folder or file>] [--strict]` | OKF conformance: frontmatter, types, actors, provenance warnings; a past `stale_after` is listed as `stale` and never fails | the bundle (with `--path` only those files can fail) | errors/warnings | hook; CI; agents once at the end of a task |
| `validate-frontmatter.py` | repo-specific keys: ID format, BR numbering, calculation and flow links on specs and calculations; `parameter_set` keys vs `generated/be/parameters.md` | `features/`, `domain/calculations/` | OK / errors | hook; CI |
| `validate-work-items.py` | work-item YAML against `_schema.yml`: BRs exist, estimates Fibonacci, subtasks <= 8 h | `work-items/*.yml` | OK / errors | after analyst runs; CI |
| `coverage-matrix.py` | BR -> story -> scenario coverage, badges, calculation audits | specs, work items, feature files | `generated/analytics/coverage-matrix.md|json` | analytics questions; CI check |
| `map-paths.py` | changed code paths -> affected specs | stdin paths + `docs-map.yml` | spec list | doc-sync, CI |
| `check-freshness.py` | CI gate in the code repos: mapped path changed but `last_verified` not bumped and no `docs-not-affected` label | PR diff, specs | pass/fail | code-repo PRs |
| `collect-evidence.py [--generate] [--graph] [--dry-run]` | the single evidence collector: stages maps, contracts and the Kafka payload schemas (Avro / JSON Schema files under the backend's `kafka.schema_dirs` -> `generated/asyncapi/schemas/`) from the code checkouts, validates the candidate (frontmatter, OpenAPI/AsyncAPI headers, schema files parse, unresolved `$ref`), replaces the collector-owned sets under `generated/` (deletions included), writes `generated/manifest.yml` (source commits, dirty flag, sha256 per file); no-op when nothing changed | the code repos' `docs/_generated` and contracts | `generated/be|fe|openapi|asyncapi/**`, `manifest.yml` | local loop; CI `ci-examples/collect-evidence.yml` (manual + nightly, one PR per snapshot) |
| `publish-local.py` | deprecated name of `collect-evidence.py`, forwards to it | - | - | - |
| `migration-status.py --scope <ctx|all>` | which lifecycle runs are still due per context, with commands | `contexts.yml`, specs, calculations, docs-tags, REPO_MAP, pending pages | `migration/<scope>.md` | planning; migration-lead |
| `hooks/guard-generated.py` | Copilot `preToolUse` hook: denies edits under `generated/**` and of `index.md` | hook payload | permission decision | every agent edit |
| `confluence-export.py`, `confluence-publish.py`, `jira-push.py`, `push-to-tests-repo.py` | **stubs** describing the intended integrations (export/import of imported pages, publish back, Jira REST, tests repo PR) | - | - | to be implemented per environment |

All validators return a non-zero exit code on failure so the same commands run in hooks and CI.

---

## 5. Agents (`docs-repo/.github/agents/`)

Each file is YAML frontmatter (`name`, `description`, `tools`, optional `handoffs`) plus the procedure in prose.
`tools: ['read','edit','search','execute']` are Copilot's tool aliases. Handoffs appear as buttons after a run.

| Agent | Role | Reads | Writes | Hands off to |
|---|---|---|---|---|
| `analyst` | business/system analyst: epic, stories, subtasks with Gherkin criteria; analytics mode for coverage/freshness questions | the six context steps of `task-context`, all of them: the pack and its pointers, the documentation folders and the graph, then code last - through the maps, freely for a question that still blocks; everything read from code is recorded as evidence and open questions | `work-items/<ID>.yml`, open questions in the spec | `test-designer`, `spec-writer` |
| `spec-writer` | writes or refreshes a feature spec from the graph and one manager file; marks everything unsourced as unverified | pack, `generated/graph/<ctx>.md`, contracts, `manager/<Ctx>Manager.kt` | `features/<ctx>/<ID>.md`, `docs-map.yml`, `log.md` | `analyst`, `calc-auditor` |
| `doc-sync` | keeps specs in sync with code changes from the generated diffs with minimal source reading | `map-paths`, `graph-query --files`, contracts, maps | folder `log.md` lines, `last_verified`, stubs for unmapped contexts | `calc-auditor` for utils changes |
| `calc-auditor` | verifies a calculation concept or an imported formula page against the calculator and its unit test; never changes numbers | two source files only | `## Audit <date>` table, status, open questions | `spec-writer`, `confluence-migrator` for the screen rules of a mixed imported page |
| `confluence-migrator` | converts one imported page into the right concept: merge new facts, mark conflicts, extract glossary terms, cite the page | the page, the pack, `generated/` | merged concept, glossary, page moved to `_done/` | `calc-auditor` for formula pages, `architect` for architecture, decision and process pages |
| `test-designer` | Gherkin scenarios and synthetic fixtures from the spec's BRs and worked examples | pack | `test-design/features/<ID>.feature`, fixtures | - |
| `architect` | HLD (C4/arc42 Mermaid), ADRs, integration map refresh; migrates imported architecture, decision and process pages | `architecture/`, graph, contracts, spec frontmatter only, the imported page | `architecture/hld/<ID>.md`, `adr/NNNN-*.md`, `overview.md` / `integrations.md` prose, page moved to `_done/` | `confluence-migrator`, `calc-auditor` for a page's feature or formula part |
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
| `task-context` | the six context steps every agent walks - catalogue, one pack, badges, pointers, documentation, code last - with the table of how far each agent goes; pack anatomy | everyone |
| `spec-lifecycle` | the four runs of one spec, owner, inputs, outputs, exit state; per-run review checklist | writers, lead, reviewers |
| `write-feature-spec` | spec structure, numbering, `source-priority.md` (cheapest source first) | spec-writer, doc-sync |
| `calculation-spec` | Attested Computation: formula, parameters, worked examples from the test, conventions | calc-auditor, spec-writer |
| `imported-page-audit` | claims table with MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED; two files only | calc-auditor, migrator |
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

**Hooks** (`.github/hooks/docs-quality.json`): `preToolUse` runs `guard-generated.py` (blocks edits under
`generated/**` and of `index.md`); `agentStop` runs `build-index`, `okf-validate --strict`, `validate-frontmatter`,
`validate-work-items`. An agent cannot finish with an invalid bundle.

**CI** (`.github/workflows/docs-quality.yml`): markdownlint, frontmatter and work-item validation, both OKF
validators, index and graph and coverage-matrix freshness checks, impacted specs for the PR, the OKF graph artifact,
link check, Mermaid syntax, OpenAPI/AsyncAPI lint; on main, publish changed concepts to Confluence (stub).
`copilot-setup-steps.yml` prepares the cloud coding agent's environment.

---

## 9. The code-repo kit (`code-repo-kit/`)

`apply-kit.py --flavour be|fe --target <repo>` copies the flavour into a code repository. The kit is the source of
truth; existing files are overwritten.

| Part | Backend (`be/`) | Frontend (`fe/`) | Why |
|---|---|---|---|
| `AGENTS.md` | <= 60 lines: purpose, read order (map -> manager -> one range), contracts, conventions, commands | same for feature folders (map -> barrel -> one range) | the first thing every Copilot surface reads |
| `.github/copilot-instructions.md` | never-open list, output discipline, agents/prompts/tools | same | Copilot-specific supplement |
| `.github/instructions/` | `api` (contract-first), `calculations` (utils), `kafka`, `migrations`, `tests`, `layers` (allowed dependencies between layers, prefix rule) | `api-client`, `features` | path-scoped rules, loaded only when editing matching files |
| `.github/agents/` | `code-reader` (read-only navigator, max 3 files), `impact-analyst` | `code-reader` | cheap answers before any implementation agent |
| `.github/prompts/` | `/explain-module`, `/find-spec-code`, `/add-endpoint` | `/explain-feature` | repeatable questions |
| `.github/hooks/docs-maps.json` | `agentStop` -> `gen-all.py --check` | same | an agent cannot leave stale maps |
| `.github/workflows/copilot-setup-steps.yml` | JDK 21 + `mvn generate-sources` | Node 24 | cloud coding agent environment |
| `scripts/docs/gen-*.py`, `gen-all.py` | codebase-map (modules, layers), components (one row per class), api-index (contract-first), events, db-schema, jobs, docs-tags | codebase-map (features + Channels column for `BroadcastChannel`s), components (shared library: props, used by), routes, types-index, docs-tags, `gen-graph-fe.ts` | the maps (2.2) |
| `templates/GraphExportTest.kt` | precise graph export from the Spring context (test scope) | - | optional precision over regex |
| `shared/` | `check-file-size.py` (line cap with baseline), `copilot-content-exclusion.yml`, `workspaces/product1.code-workspace` (per-context multi-root workspace), `ide-setup.md` | same | token hygiene, less noise |
| `ci/docs-maps.yml` | PR: maps fresh + size budget, nothing else | same | the code repo keeps describing itself; publication belongs to the docs repo's collector, so no docs-repo credentials here |
| `vscode-extension/` | `#docsLookup`, `#codeMap`, `#specToCode`, `#impact`, chat participant `@docs` | same | retrieval tools without MCP |

---

## 10. The flows end to end

### A. A code change reaches the documentation
1. Developer changes `ProjectionService.kt`, opens a PR. CI runs `gen-all.py --check` (maps must be regenerated in
   the PR) and the file-size gate. `check-freshness.py` (when enabled) requires `last_verified` of P1-001 to be
   bumped or the label `docs-not-affected`.
2. Nightly, or on demand, the docs repo's collector (`collect-evidence.yml` -> `collect-evidence.py`) checks out
   backend and frontend read-only, runs their generators, validates the snapshot, replaces `generated/`, records the
   source commits in `generated/manifest.yml`, rebuilds the graph and opens ONE PR labelled `generated`; the body lists
   the source paths changed since the previous manifest, mapped to specs through `docs-map.yml`. A second run against
   unchanged sources opens nothing. Lower latency, when needed, is a `repository_dispatch` from the code repos' CI.
3. In the docs repo, `doc-sync` runs on that PR: `map-paths` and `graph-query --files` name the specs in the blast
   radius; it compares their API/Events/Data sections with the new contracts and maps, updates them, adds a
   line to the context folder's `log.md`, sets `last_verified`, flags calculations for `calc-auditor` if `utils/` changed, and stubs any
   context that has no spec. Hooks validate; a person reviews and merges.

### B. A spec is written (the four runs, see `spec-lifecycle`)
Run 1 skeleton from the graph and the manager (`spec-writer`), Run 2 imported pages merged one per run
(`confluence-migrator`), Run 3 calculation audit (`calc-auditor`), Run 4 owner decision (a person adds
`verified.by`). One run, one review, one commit. `migration-status.py` says what is still due.

### C. Confluence migration
Space export to HTML under `confluence-import/raw-html/<section>/`, imported by `scripts/confluence-import.py` into
`confluence-import/<SPACE>/<section>/<slug>.md` with a header block, the images a page shows under
`<SPACE>/_attachments/<slug>/` (spec in [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md)), triaged in the generated
inventory table (the **Known state** column), then flow B. Pages are evidence, never copied; numbers always go through
Run 3. A page that changes after its migration comes back from the next export as a fresh page (`supersedes_done`
naming the migrated copy) and goes through flow B again; `import-done.py` replaces the copy.

### D. An analyst task
`/context-pack <task>` resolves the task to a spec, builds the pack. `@analyst /jira-from-spec <ID>` reads it, checks
the badge, slices stories per `jira-work-items`, derives subtasks per graph node kind, writes `work-items/<ID>.yml`,
validates it. Gaps become `questions[]` and, if blocking, open questions in the spec. Handoff buttons: test design,
spec refresh.

### E. Tests and Jira
`test-designer` writes `test-design/features/<ID>.feature` with `@BR` tags and synthetic fixtures using the shared
step vocabulary; `push-to-tests-repo.py` (stub) hands them to the tests repository. `jira-push.py` (stub) creates
the epic and stories and writes back keys.

### F. Analytics
`coverage-matrix.py` computes BR coverage by stories and scenarios, badges and staleness. `/coverage-report`
answers from it and from the index badges, including `code only` contexts from REPO_MAP. `/impact-from-graph`
answers change questions from the graph alone.

### G. Measuring whether it works
From the pilot onward: Copilot premium requests per user per week, share of `@workspace` versus `#file`/pack
usage, PR review time, number of `_not implemented_` rows in the API index, number of open questions per spec,
and the human analyst's assessment of agent-written stories (the baseline recorded in the pilot).

---

## 11. Design decisions as questions and answers

**Why standard-library Python and regex instead of a parser or a library?** No packages to approve (only an interpreter),
runs on Windows, macOS and CI runners unchanged, and a regex over Kotlin declarations is enough for maps that carry `file:line`; precision
comes from the optional compiler-based exports when needed.

**Why no MCP?** Not permitted in the environment. The VS Code extension provides the same retrieval through the
public API; scripts cover JetBrains and CLI.

**Why business contexts by class-name prefix?** Because the real backend is layered and we did not want to
restructure it. One file, `contexts.yml`, turns the layered code into contexts for the graph and the docs.

**Why is the frontmatter so long?** Only six fields are OKF requirements. The rest are traceability fields that make
packs, badges, the freshness gate and the matrix possible. Agents never see them (the pack strips them); people fold
them; Confluence readers never see them. They can be script-generated from the graph later.

**Why packs instead of letting the agent search?** The folders are open from step 4 on; the pack is for what search
cannot give: a recorded starting point (two runs start from the same slice, the PR carries it), the computed sections
(graph neighbourhood, merged slice, contracts and tables resolved from the frontmatter), trust in view before anything
is read, and one read instead of twenty tool calls for the part every task needs. A searching agent reads whatever
matched, in whatever order, and leaves no record of where it started.

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
- **Context pack**: the recorded per-task slice in `.context/<task>.md` - subject whole, computed sections, pointers.
- **Bounded context**: a business area; in code a set of class-name prefixes plus one FE feature; in docs one spec folder and one spec prefix.
- **Map**: a generated table about the code (`generated/be|fe/*.md`).
- **Graph**: nodes and edges joined from the maps; `REPO_MAP.md`, `<context>.md`, `graph.json`.
- **Run**: one agent execution of one lifecycle step, followed by one human review and one commit.
- **Attested Computation**: the OKF type for a calculation with parameters, executor, worked examples.
- **Code only**: a context or calculation present in the code but without a concept; the backlog list in REPO_MAP.
- **Freshness gate**: the CI check that a PR touching a mapped path must bump `last_verified` or declare `docs-not-affected`.
- **Quarantine**: `confluence-import/`, where imported pages wait as evidence until migrated.
