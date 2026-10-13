# Setting up an agent-ready docs repository for the analyst agent - step by step

This is the hands-on recipe for repeating the `docs-repo/` flow of this investigation in a real enterprise project:
which folders to create, which files to copy, what to put into `AGENTS.md`, which agents and scripts you need, what
each script does, and whether it is safe. Governance (owners, branch protection, review policy, evaluation) is in
[`ENTERPRISE-ADOPTION.md`](ENTERPRISE-ADOPTION.md); read its steps 1-3 once before you start.

Assumptions (adjust the names, keep the shape):

| Placeholder | Meaning |
|---|---|
| `<docs>` | your docs repository (already has the FE-facing Swagger, other services' Swagger and the Kafka schema) |
| `<be>`, `<fe>` | backend (Kotlin/Spring, layered `core/src/main/kotlin/<project>/<layer>/`) and frontend repositories |
| `<project>` | the Kotlin root package |
| `<CTX>` | spec ID prefix of one bounded context (e.g. `P1`, `CLI`) |
| `C:\src\` | the folder where `<docs>`, `<be>`, `<fe>` are checked out side by side |

Tooling: GitHub Copilot (VS Code / JetBrains / CLI), PowerShell 7 (`pwsh`), git. No MCP, no Python, no npm needed for
the core flow.

---

## 0. The flow in one picture

```text
 <be> / <fe> source
     |  scripts/docs/gen-all.ps1  (regex scan, no build)          -> <repo>/docs/_generated/*.md   (code maps)
     v
 <docs>/scripts/collect-evidence.ps1                               -> generated/be, generated/fe, generated/openapi,
     |                                                                generated/asyncapi, generated/manifest.yml
     v
 gen-graph.ps1 (contexts.yml + docs-map.yml + maps)                -> generated/graph/REPO_MAP.md, <context>.md, graph.json
     v
 Run 1  spec-writer       skeleton spec per context from graph      -> features/<ctx>/<CTX>-001.md  (draft)
 Run 2  confluence-migrator  one exported page per run, merged      -> same spec + glossary, page -> _done/
 Run 3  calc-auditor      formula vs calculator + its unit test     -> domain/calculations/<name>.md (Audit table)
 Run 4  human owner       answers open questions, marks verified    -> status: stable
     v
 analyst agent: context-pack.ps1 -Task <ID>  ->  .context/<ID>.md  ->  answers / work items / analytics
```

The principle that makes the analyst trustworthy: **the code is the truth, Confluence is evidence.** The skeleton of
every spec is built from code maps and contracts first; Confluence pages are merged into it afterwards, claim by claim,
each claim either confirmed against `generated/` or marked `❓ UNVERIFIED` / `⚠️ CONFLICT`.

---

## Phase A - Prepare the docs repository (day 1)

### Step 1. Decide where your existing contracts go

You already have Swagger files and a Kafka schema in `<docs>`. The collector script **deletes and rewrites every file**
under `generated/be`, `generated/fe`, `generated/openapi`, `generated/asyncapi` on each run. So sort the contracts
into two groups first:

| Contract | Where it really comes from | Put it in `<docs>` at |
|---|---|---|
| Own REST contract (the one FE and BE are generated from) | `<be>/core/src/main/resources/openapi/<name>.yaml` | `generated/openapi/backend.yaml` - **collector-owned**, do not keep a hand copy |
| External services consumed by BE | `<be>/core/src/main/resources/api/*.yaml` | `generated/openapi/external/*.yaml` - **collector-owned** |
| Kafka schema, if it is AsyncAPI and lives in `<be>` | `<be>/core/src/main/resources/openapi/<events>.yaml` | `generated/asyncapi/backend.yaml` - **collector-owned** |
| Anything that is **not** in `<be>` (other teams' Swagger, Avro/JSON schemas from a registry, Swagger 2.0 you cannot convert) | uploaded by hand | `contracts/openapi/`, `contracts/kafka/` - **hand-maintained**, never under `generated/` |

Checks before you move anything:

- The collector rejects `generated/openapi/backend.yaml` unless it starts with `openapi: 3` and rejects any contract with
  a relative `$ref` to another file. Multi-file specs must be bundled into one file first.
- If the Kafka schema is Avro (`.avsc`) or JSON Schema, it is not AsyncAPI: keep it in `contracts/kafka/` and tell the
  agents where it is (Step 4), or extend the collector (Step 3).

### Step 2. Create the folder layout

```text
<docs>/
  AGENTS.md                      rules for every agent (Step 4)
  index.md                       root index; only the block between <!-- manual:start/end --> is hand-written
  log.md                         lifecycle log (created / migrated / audited / verified)
  contexts.yml                   bounded contexts -> BE class-name prefixes, FE feature folder, spec prefix (Step 7)
  docs-map.yml                   code path globs -> specs (Step 9)
  .gitignore                     .context/  .publish/  okf-graph.html
  .github/
    copilot-instructions.md      Copilot-only supplement (Step 4)
    agents/  prompts/  skills/  instructions/  hooks/  workflows/
  domain/glossary.md  domain/context-map.md  domain/calculations/_template.md
  features/_template.md  features/conventions.md  features/<ctx>/
  flows/_template.md
  architecture/adr/template.md
  confluence-import/README.md    inventory of exported pages; pages go to confluence-import/<SPACE>/
  contracts/                     hand-maintained contracts (Step 1)
  generated/                     collector-owned evidence + graph + analytics (never hand-edited)
  migration/                     migration board written by migration-status.ps1
  work-items/_schema.yml         analyst output schema
  test-design/                   test-designer output
  scripts/                       PowerShell tooling (Step 3)
```

### Step 3. Copy files from this repository

Copy from `docs-repo/` of this investigation into `<docs>`, then do the edits in the right-hand column.
Everything named "Harbor", `harbor`, `HARBOR`, `P1`, `CLI`, ... is sample vocabulary and must be replaced.

**Copy and edit (required for the analyst flow):**

| File(s) | Edit after copying |
|---|---|
| `scripts/context-pack.ps1`, `graph-query.ps1`, `gen-graph.ps1`, `build-index.ps1`, `okf-validate.ps1`, `validate-frontmatter.ps1`, `validate-work-items.ps1`, `map-paths.ps1`, `coverage-matrix.ps1`, `migration-status.ps1`, `hooks/guard-generated.ps1` | `build-index.ps1` line ~78: bundle title. `context-pack.ps1` lines ~163-177: if you keep hand-maintained contracts in `contracts/`, add them to the "Contracts" section (it only reads `generated/openapi/backend.yaml` today). `validate-frontmatter.ps1` checks the generic ID pattern `^[A-Z][A-Z0-9]*-\d{3}$` and the required keys (line 17); change only if your IDs look different. |
| `scripts/collect-evidence.ps1` | Lines 99-101: replace `openapi/harbor-api.yaml` and `openapi/harbor-events.yaml` with your file names. Remove the `asyncapi` line if your events contract is not AsyncAPI. Line 76: temp folder prefix. |
| `.github/agents/analyst.agent.md` | Replace with the version in Step 14 (adds a question-answering mode). |
| `.github/agents/spec-writer.agent.md`, `confluence-migrator.agent.md`, `calc-auditor.agent.md`, `doc-sync.agent.md`, `migration-lead.agent.md` | Replace `harbor` paths with `<project>`. In `calc-auditor` replace `V9__parameters.sql` / `parameter_set` / `.../calc/<Class>Test.kt` with where your parameters and calculator tests really live. In `doc-sync` step 5 replace `core/src/main/kotlin/harbor/utils/**` with your calculation package. |
| `.github/prompts/*.prompt.md` | Replace sample defaults in `${input:...:default}` (e.g. `product2 P2-001`). |
| `.github/skills/spec-lifecycle`, `task-context`, `write-feature-spec`, `calculation-spec`, `legacy-page-audit`, `jira-work-items`, `gherkin-test-design`, `docs-analytics`, `code-graph` | Replace sample names and paths. |
| `.github/instructions/*.instructions.md` | Keep `applyTo` globs; replace sample names. |
| `.github/hooks/docs-quality.json` | None (runs local scripts only). |
| `features/_template.md`, `features/conventions.md`, `domain/calculations/_template.md`, `flows/_template.md`, `architecture/adr/template.md`, `work-items/_schema.yml` | `context:` list and `owners:` in the templates; spec prefixes in `conventions.md`. |
| `confluence-import/README.md` | Empty the inventory table; keep the header format description. |

**Copy later (not needed before the analyst works):** `test-designer`, `architect`, `impact-analyst` agents;
`scripts/check-freshness.ps1`, `ci-examples/collect-evidence.yml`, `.github/workflows/docs-quality.yml` (Phase F).

**Do not copy:** `confluence-export.ps1`, `confluence-publish.ps1`, `jira-push.ps1`, `push-to-tests-repo.ps1` (they are
stubs that only print what they would do), `publish-local.ps1` (deprecated wrapper), `third-party/`, the OKF Python
scripts (optional duplicates of the PowerShell validators), `code-repo-kit/vscode-extension/` (separate project).
Do not copy any sample content (`features/*/*.md`, `domain/calculations/*.md`, `generated/**`, `confluence-import/HARBOR/`).

### Step 4. Write `AGENTS.md` and `.github/copilot-instructions.md`

`AGENTS.md` is read automatically by Copilot Chat, CLI and the coding agent. Keep it under ~70 lines: anything longer
is paid for in tokens on every request. Paste and fill in:

````markdown
# AGENTS.md - <Product> documentation repository

Single source of truth for functional and technical documentation of <Product>. Code repositories `<be>`
(Kotlin/Spring) and `<fe>` are *inputs*; Confluence is a *legacy source* (`confluence-import/`); Jira and the tests
repository are *outputs*. Every document is a concept with YAML frontmatter; every folder has a generated `index.md`.
Agents orient through indexes, never through directory listings.

## Work task-scoped: build the context pack first
For any task about a feature, calculation, change or ticket run
`./scripts/context-pack.ps1 -Task <spec ID | calculation | graph node | free text>` and read `.context/<task>.md`.
Read the pack, not the repository. Open anything else only to answer a question the pack leaves open, and then only
the `file:line` it names.

## Read order when there is no pack (cheapest first)
1. `index.md` -> the area's `index.md` (one line + trust badge per concept)
2. `features/<context>/<ID>.md` - functional spec; business rules are `BR-<ID>-<n>`
3. `domain/calculations/<name>.md` - formulas and worked examples (never re-derive from code)
4. `contexts.yml`, then `generated/graph/REPO_MAP.md` -> `generated/graph/<context>.md`
5. `generated/be/*.md`, `generated/fe/*.md` - code maps (components, api-index, events, db-schema, jobs, routes, types, docs-tags)
6. Contracts: `generated/openapi/backend.yaml`, `generated/openapi/external/*.yaml`, `generated/asyncapi/backend.yaml`,
   hand-maintained `contracts/**` (<list what is there: other teams' APIs, Kafka schemas>)
7. Only then source code in `../<be>` / `../<fe>`, smallest range, located via the graph or `docs-tags.md`.

## Hard rules
- Never hand-edit `generated/**` or any `index.md`; run the scripts that own them.
- Provenance: set `generated: { by: copilot/<agent>, at: <ISO> }` on anything you write; cite `sources[]` with
  `[^id]`; never write `verified.by: human:<id>`; `status: draft` until a person verifies.
- IDs: specs `<CTX>-<NNN>` (<list your prefixes>), rules `BR-<ID>-<n>`, calculations `snake_case`.
  Work items and test scenarios cite them.
- Confluence pages are evidence, not rules. Never copy numbers or thresholds from them; link the calculation.
- Unknown = open question in the concept, never a guess in prose.
- Terminology from `domain/glossary.md`; English in files; answer in the user's language in chat.
- No real customer data, personal data or secrets in any file.
- Outputs go to files; chat summaries <= 15 lines. Specs <= 300 lines; diagrams <= 25 nodes.

## Commands (PowerShell 7)
| Purpose | Command |
|---|---|
| Context pack | `./scripts/context-pack.ps1 -Task <ID|name|text> [-Budget 500]` |
| Validate | `./scripts/okf-validate.ps1 -Strict`; `./scripts/validate-frontmatter.ps1`; `./scripts/validate-work-items.ps1` |
| Indexes | `./scripts/build-index.ps1` |
| Graph | `./scripts/graph-query.ps1 -Node spec:<ID> -Depth 2` / `-Files <paths>` / `-Find <text>` |
| Migration board | `./scripts/migration-status.ps1 -Scope all` |
| Analytics | `./scripts/coverage-matrix.ps1` |

Before finishing any edit: `okf-validate.ps1 -Strict`, `build-index.ps1`, and a dated line in `log.md`.

## Agents
`.github/agents/`: `analyst`, `spec-writer`, `confluence-migrator`, `calc-auditor`, `doc-sync`, `migration-lead`.
A spec is written run by run (skeleton -> legacy merge -> calculation audit -> owner decision); see
`.github/skills/spec-lifecycle/SKILL.md`.
````

`.github/copilot-instructions.md` - copy from this repo and keep only: "Start every task with a context pack", the
"which agent for which job" table (rows for the agents you copied), "Guard rails" and "Output discipline". Delete the
"Tools available in VS Code (in-house extension)" section unless you also build that extension.

**Client check (once):** in VS Code and JetBrains confirm that your organisation's Copilot policy allows custom
instructions, `AGENTS.md`, custom agents, prompt files, skills and hooks (some are preview or disabled by policy on
some surfaces). Settings: `code-repo-kit/shared/ide-setup.md`.

---

## Phase B - Make the code readable (day 2-3, dev lead)

### Step 5. Install the generators in `<be>` and `<fe>`

From `code-repo-kit/` copy into each code repository (review first with `apply-kit.ps1 -WhatIf`, or copy by hand):

| `<be>` | `<fe>` |
|---|---|
| `scripts/docs/_common.ps1`, `gen-all.ps1`, `gen-codebase-map.ps1`, `gen-components.ps1`, `gen-api-index.ps1`, `gen-events.ps1`, `gen-db-schema.ps1`, `gen-jobs.ps1`, `gen-docs-tags.ps1`, `tag-candidates.ps1` | `scripts/docs/_common.ps1`, `gen-all.ps1`, `gen-codebase-map.ps1`, `gen-components.ps1`, `gen-routes.ps1`, `gen-types-index.ps1`, `gen-docs-tags.ps1`, `tag-candidates.ps1` |
| `.github/agents/docs-tagger.agent.md`, `.github/prompts/tag-docs.prompt.md` | same |
| `AGENTS.md` (rewrite for your repo, keep the structure) | same |

Edits: `gen-api-index.ps1` line 78 adds a sample-specific header name (`X-Harbor-Session`) - change it to your
header or delete the line; `gen-all.ps1` lines 32-33 contract file names in the index text; `tag-candidates.ps1` (BE line 29, FE line 24)
default path to `contexts.yml` (`../<docs>/contexts.yml`).

Run and inspect:

```powershell
cd C:\src\<be>; pwsh scripts/docs/gen-all.ps1
cd C:\src\<fe>; pwsh scripts/docs/gen-all.ps1
```

Open every file in `docs/_generated/` and check it against reality. The generators are regex scanners with
assumptions; an empty or wrong map means the generator must be adapted, never the map edited:

| Map | Assumes | If your code differs |
|---|---|---|
| `components.md` | Spring stereotypes, constructor injection, `JpaRepository<Entity>` / `@Table` | adapt the regex in `gen-components.ps1` |
| `api-index.md` | contract-first: `operationId` implemented as `override fun <operationId>(` in a `@RestController` | otherwise it falls back to `@*Mapping` annotations; check `_not implemented_` rows |
| `events.md` | `@KafkaListener` + `KafkaTemplate.send(Topics.X, ...)`, constants in `kafka_client` | adapt `gen-events.ps1` |
| `db-schema.md` | Flyway `db/migration/V*.sql` | Liquibase -> rewrite `gen-db-schema.ps1` |
$1$2| `parameters.md` | enum `ParameterKey(val key)` + `INSERT INTO parameter_set` seeds in Flyway migrations | other names via `-EnumName` / `-Table`; otherwise adapt `gen-parameters.ps1` |$2| `routes.md` (FE) | react-router object routes or `<Route>` | adapt `gen-routes.ps1` |

Commit `scripts/docs/**` and `docs/_generated/**` in each code repo through a normal PR. The generators only read
source and write `docs/_generated/`.

### Step 6. Define the bounded contexts - `contexts.yml` in `<docs>`

The layered backend has no business folders, so the business area of a class is its **class-name prefix**. One line per
context:

```yaml
contexts:
  <context>: { spec: <CTX>, fe: <fe feature folder or "">, be: [<Prefix1>, <Prefix2>] }
```

Iterate: run Step 8, open `generated/graph/shared.md`; every class there that is not a true helper means a prefix is
missing. Repeat until `shared` holds only helpers.

### Step 7. Tag the entry points with `@docs` (in `<be>` / `<fe>`, one PR per context)

`@docs <ID>` in a KDoc/JSDoc is the only link from a spec to `file:line`. In `<be>`:

```powershell
pwsh scripts/docs/tag-candidates.ps1      # read-only table: manager/calculation -> current tag, proposed tag, PROPOSE/REVIEW/BLOCKED
```

Then in Copilot Chat (agent `docs-tagger`, or prompt `/tag-docs <context>`). The agent edits **comment lines only**
(adds `@docs <CTX>-001` to `manager/<Ctx>Manager.kt`, `@docs <calculation_name>` to calculation classes), reruns
`gen-all.ps1`, and reports. Review the diff like any code PR; build and tests must pass.

### Step 8. Collect the evidence into `<docs>` and build the graph

```powershell
cd C:\src\<docs>
git status                                                         # clean tree first
./scripts/collect-evidence.ps1 -Backend C:\src\<be> -Frontend C:\src\<fe> -DryRun
./scripts/collect-evidence.ps1 -Backend C:\src\<be> -Frontend C:\src\<fe> -Graph
git diff --stat
```

`-DryRun` lists `+` added / `~` changed / `-` removed files and writes nothing - read the `-` lines carefully the first
time (they are files that will be deleted from `generated/`). The real run writes `generated/manifest.yml` with the
source commits and hashes, then `gen-graph.ps1` and `build-index.ps1`. Commit as one PR ("evidence snapshot <be sha>/<fe sha>").

Read `generated/graph/REPO_MAP.md`: every community is a future spec; the "code only" list is your backlog.

---

## Phase C - Seed the knowledge (day 3-4)

### Step 9. Glossary and `docs-map.yml`

- `domain/glossary.md`: one line per term taken from the contracts and entity names (code vocabulary). Leave the
  `Aliases` column for Confluence wording and other languages - `confluence-migrator` fills it.
- `docs-map.yml`: one mapping per context, even before the spec exists (`specs: []  # TODO: <CTX>-001`). BE globs select
  by prefix: `be/core/src/main/kotlin/<project>/**/<Prefix>*.kt`. Add calculations
  (`be/core/src/main/kotlin/<project>/utils/**` -> `domain/calculations/**`) and messaging paths.

### Step 10. Bring in the Confluence export

You export the pages yourself (no script needed). For each page create
`confluence-import/<SPACE>/<slug>.md` with this header, then the body (Markdown or the storage HTML - Copilot reads both):

```markdown
---
source: Confluence <SPACE>/<page title>
confluence_id: <page id>
url: <page url>
author: <author id or "legacy">
last_modified: <YYYY-MM-DD>
status: imported
---
```

Before committing:

1. Remove attachments, screenshots and any table with real customer data or personal data. Search the export for
   e-mail addresses, IBAN/account-like numbers, phone numbers and client names before `git add`; git history keeps
   whatever you commit.
2. Fill the inventory table in `confluence-import/README.md`: page, `last_modified`, guessed class
   (`feature-spec | calculation | architecture | decision | glossary | process | obsolete`), target concept.
   Pages older than the last major release are suspect by default.

---

## Phase D - Write the specs, run by run (the bulk of the work)

### Step 11. Plan with the migration board

```powershell
./scripts/migration-status.ps1 -Scope all      # writes migration/all.md: per context the runs due + exact command
```

Optionally ask the `migration-lead` agent (prompt `/migration-plan all`) to add the processing order, targets for
unassigned pages and blockers. It never edits specs.

### Step 12. Execute the runs - one Copilot run, one human review, one commit

| Run | In Copilot Chat | Reads | Writes | Your review (10-15 min) |
|---|---|---|---|---|
| 1 Skeleton | agent `spec-writer`, prompt `/spec-skeleton-from-graph <context> <CTX>-001` | graph neighbourhood, contracts, **one** manager file | `features/<ctx>/<CTX>-001.md` (`draft`), `docs-map.yml`, `log.md` | API/Events/Data match the contracts; rules are single MUST statements; gaps are in Open questions |
| 2 Legacy merge | agent `confluence-migrator`, message `confluence-import/<SPACE>/<page>.md` | the page + context pack | merged new facts, `⚠️ CONFLICT` / `❓ UNVERIFIED` callouts, `sources[]`, glossary terms; page moved to `_done/` | every legacy claim is cited; no numbers copied; conflicts are visible |
| 3 Calculation | agent `calc-auditor`, prompt `/audit-calculation <name>` (or the handoff button) | the calculator class + its unit test only | `domain/calculations/<name>.md` with `## Audit <date>` (`MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED`) | worked examples come from the test, with test method names |
| 4 Owner decision | a person, no agent | open questions | answers in the Change log, `verified: { by: human:<id>, at }`, `stale_after` (+90 days), `status: stable` | - |

Order: all Run 1 first (they can be batched - one Copilot coding-agent issue per context with the same prompt), then
Run 2 interactively page by page, Run 3 after each spec, Run 4 by the owner. Rerun `migration-status.ps1` after each
batch. When a run fails validation the `agentStop` hook prints the error; fix the file, do not disable the hook.

---

## Phase E - Switch on the analyst agent

### Step 13. Readiness check per context

A context is ready for the analyst when all of these hold (`migration-status.ps1 -Scope <ctx> -Print` shows most of them):

- no "code only" entry for the context in `generated/graph/REPO_MAP.md`;
- the spec exists, high-value specs are `stable` + human-verified;
- every linked calculation has a concept with worked examples from its test and an `## Audit` table;
- no page for the context remains outside `confluence-import/<SPACE>/_done/`;
- `./scripts/okf-validate.ps1 -Strict` reports 0 errors;
- `./scripts/context-pack.ps1 -Task <CTX>-001 -Print` contains spec, calculations, graph neighbourhood, contracts and
  tables within the budget.

Then test it: write 10-15 questions with answers your domain owner agrees with (including one the docs cannot answer)
and check that the analyst answers with rule IDs and admits the gap on the unanswerable one.

### Step 14. The analyst agent file

`.github/agents/analyst.agent.md` (this repo's version + a question mode with evidence requests):

````markdown
---
name: analyst
description: Business/system analyst. Answers questions about features with rule IDs and citations, turns a spec into Jira-ready work items with Gherkin acceptance criteria, and reports documentation coverage. Works from a task-scoped context pack only.
tools: ['read', 'edit', 'search', 'execute']
handoffs:
  - label: Design tests for these stories
    agent: test-designer
    prompt: Derive Gherkin scenarios and fixtures for the stories in work-items/${input:featureId}.yml.
  - label: Spec has gaps - refresh it
    agent: spec-writer
    prompt: The analyst found gaps in ${input:featureId}; resolve the Open questions from the graph neighbourhood and the manager file only.
---

You are a senior business/system analyst for <Product>. You do not read application source code; the documentation
bundle is prepared so that you do not have to.

## Input
A spec ID (`<CTX>-001`), a calculation name, a graph node, a free-text question or task, or an analytics question.

## Procedure
1. Build the pack: `./scripts/context-pack.ps1 -Task "<input>"`; read `.context/<task>.md` top to bottom. If it lists
   `candidates:`, pick one and rebuild, or ask the user.
2. Trust check: `draft`, `unverified` or `STALE` concepts are unreliable - say so. Legacy pages are evidence, not rules.
3. Question mode: answer from the pack. Every statement cites `BR-<ID>-<n>`, a calculation or a contract operation.
   Separate **facts** (stable specs), **unverified** (draft / legacy) and **unknown**. For an unknown that matters,
   append an evidence request to the spec's **Open questions**: question, documents checked, missing fact, likely
   source location if known, why it matters. Never guess.
4. Work-item mode: slice per `.github/skills/jira-work-items/SKILL.md` (1 epic, 2-8 stories, subtasks <= 1 day per
   graph node kind). Every acceptance criterion is Gherkin and cites a `BR-` that exists in the pack. Stories derived
   from non-stable specs get the label `needs-spec-review`. Write `work-items/<ID>.yml`; run
   `./scripts/validate-work-items.ps1 work-items/<ID>.yml`.
5. Analytics mode: `./scripts/coverage-matrix.ps1`; answer from `generated/analytics/coverage-matrix.md` and index badges.
6. Only if the pack leaves a blocking question AND names a `file:line`, open exactly that range in `../<be>` or
   `../<fe>`, and record what you learned as an open question, not as a silent assumption.

## Output
Files for work items and open questions. Chat <= 15 lines: answer with citations, trust badge of each spec used,
open questions raised.
````

How analysts use it daily: open **only** `<docs>` (or a multi-root workspace with `<docs>` plus read-only code repos),
choose agent `analyst`, ask the question or type `/jira-from-spec <ID>`. Never use `@workspace` over the code repos.

---

## Phase F - Keep it current (after the first contexts are ready)

### Step 15. Guard rails and CI

| What | Where | Effect |
|---|---|---|
| `.github/hooks/docs-quality.json` | `<docs>` | `preToolUse`: blocks agent edits to `generated/**` and `index.md`; `agentStop`: rebuilds indexes and validates |
| `CODEOWNERS` | `<docs>` | `generated/**` and `scripts/**` owned by platform; `features/<ctx>/**` by the context owner |
| Branch protection | `<docs>` | PR + green checks + code-owner approval on the default branch |
| CI job `docs-quality` | `<docs>` | PowerShell steps from `.github/workflows/docs-quality.yml`: `validate-frontmatter`, `validate-work-items`, `okf-validate -Strict`, `build-index -Check`, `gen-graph -Check`. The markdownlint / lychee / mermaid / spectral / Python steps pull third-party actions and packages - include them only if your platform approves them |
| Collector job | `<docs>` | `ci-examples/collect-evidence.yml` adapted to your CI: scheduled or manual, checks out `<be>`/`<fe>` into separate folders, runs `collect-evidence.ps1 -Graph`, opens one PR per changed snapshot |
| `gen-all.ps1 -Check` | `<be>`, `<fe>` PRs | fails when `docs/_generated` is stale |
| Freshness gate | `<be>`, `<fe>` PRs | `code-repo-kit/ci/docs-maps.yml` + `check-freshness.ps1`: a PR touching a mapped path must update the spec's `last_verified` or carry the label `docs-not-affected`. Start warn-only |
| `doc-sync` agent | `<docs>` | on each collector PR: maps changed paths to specs (`map-paths.ps1`, `graph-query.ps1 -Files`), updates API/Data sections, flags calculations to `calc-auditor`, removes a human verification when the section it covered changed |

---

## Agents - what to create

| Agent | Repo | Needed for analyst go-live | Job | Can edit |
|---|---|---|---|---|
| `analyst` | `<docs>` | yes | answers, work items, analytics | `work-items/`, Open questions in specs |
| `spec-writer` | `<docs>` | yes | Run 1 skeletons, refresh drafts | `features/`, `docs-map.yml`, `log.md` |
| `confluence-migrator` | `<docs>` | yes | Run 2, one page per run | specs, glossary, `confluence-import/` (move to `_done/`) |
| `calc-auditor` | `<docs>` | yes, if you have calculations | Run 3 | `domain/calculations/` |
| `migration-lead` | `<docs>` | recommended | plans runs | `migration/` only |
| `doc-sync` | `<docs>` | after go-live | keeps specs current | specs, `docs-map.yml` |
| `docs-tagger` | `<be>`, `<fe>` | yes (once per context) | adds `@docs` tags | comment lines in source |
| `test-designer`, `architect`, `impact-analyst` | `<docs>` | later | Gherkin, HLD/ADR, blast radius | their own folders |

Agents never call each other; handoffs are buttons a person clicks after reviewing the previous run.

## Scripts - what each does and whether it is safe

None of the copied scripts makes a network call or needs credentials. All are plain PowerShell 7 with no modules.

| Script | Reads | Writes | Risk and how to handle it |
|---|---|---|---|
| `be|fe/scripts/docs/gen-all.ps1` (+ `gen-*.ps1`) | source files of that repo | only `docs/_generated/` (`-Check` writes to a temp folder) | Safe. Output reveals class names and table names to whoever can read `<docs>` - same audience as the code, normally fine |
| `tag-candidates.ps1` | `docs/_generated/components.md`, `contexts.yml` | nothing (or `-Out` file) | Safe, read-only |
| `collect-evidence.ps1` | `<be>`, `<fe>` checkouts (runs `git rev-parse/status`; with `-Generate` runs their `gen-all.ps1`) | **deletes and rewrites** all files in `generated/be`, `generated/fe`, `generated/openapi`, `generated/asyncapi`; writes `generated/manifest.yml` | The only destructive script. By design it removes files the sources no longer produce. Never keep hand-made files in those four folders; start from a clean git tree; run `-DryRun` first; a failed validation publishes nothing |
| `gen-graph.ps1` | `generated/be|fe`, `contexts.yml`, `docs-map.yml` | `generated/graph/**` | Safe; overwrites its own output |
| `build-index.ps1` | frontmatter of all concepts | **every `index.md`** outside excluded folders; root `index.md` keeps the `manual:start/end` block | Do not keep hand-written content in `index.md` files (put it in `README.md` or a concept) |
| `context-pack.ps1` | specs, calculations, graph, contracts, `confluence-import/` | `.context/<task>.md` (git-ignored) | Safe. Packs may quote legacy pages - keep `.context/` ignored |
| `graph-query.ps1`, `map-paths.ps1` | `graph.json`, `docs-map.yml` | nothing (stdout) | Safe, read-only |
| `okf-validate.ps1`, `validate-frontmatter.ps1`, `validate-work-items.ps1` | the bundle | nothing | Safe, read-only; exit code 1 on errors |
| `coverage-matrix.ps1` | specs, work items, test design | `generated/analytics/coverage-matrix.md|json` | Safe |
| `migration-status.ps1` | specs, calculations, `confluence-import/`, graph | `migration/<scope>.md` | Safe |
| `check-freshness.ps1` | changed paths, `docs-map.yml`, spec frontmatter | nothing; exit 1 when stale | Safe; it is a gate, start it warn-only |
| `hooks/guard-generated.ps1` | hook payload on stdin | permission decision on stdout | Best effort (regex over the payload). It reduces accidents; it is not a security boundary - CODEOWNERS and branch protection are |

## Safety rules for the agents themselves

1. **`execute` tool = terminal access.** Agents with `tools: [..., 'execute']` can run commands. Keep terminal
   auto-approval off, or allow-list only `pwsh ./scripts/*.ps1` and `pwsh scripts/docs/*.ps1`. Do not run agent
   sessions in a shell that has production tokens in its environment.
2. **Agents write drafts only.** They set `status: draft` and `generated.by: copilot/<agent>`; only a person adds
   `verified.by: human:<id>`. Approval is the PR review, not a field the agent can write.
3. **One run, one review, one commit.** Never merge a batch of agent output you have not read.
4. **Data.** Everything in `<docs>` becomes Copilot context for everyone with access. Strip personal and customer data
   from Confluence exports before the first commit; use synthetic values in examples and fixtures; configure Copilot
   content exclusion (`code-repo-kit/shared/copilot-content-exclusion.yml`) for anything sensitive in the code repos.
5. **Code repos.** The only source edit any agent makes in this flow is `docs-tagger` adding comment lines. It goes
   through a normal code PR with build and tests.
6. **Execution policy.** If your machines enforce signed PowerShell scripts (`AllSigned`), the scripts must be signed by
   your platform team before use; do not bypass the policy.
7. **CI dependencies.** The PowerShell checks need nothing external. Third-party CI actions, npm and pip packages in the
   sample workflow need the usual enterprise approval or can be dropped.

## Minimal path (if you need the analyst quickly)

Steps 1-4, 5-8 for the backend only, 9, 10, then Run 1 + Run 2 + Run 3 for **one** context, Run 4 by its owner, Step 14,
and the 10-15 question test from Step 13. Expand context by context; switch on Phase F once two or three contexts are
`stable`.
