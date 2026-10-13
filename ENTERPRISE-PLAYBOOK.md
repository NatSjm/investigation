# Enterprise playbook: build the documentation flow for the analyst agent, step by step

What you are building: a documentation repository that GitHub Copilot can read instead of your code, fed by small
generated maps from the frontend and backend, by the OpenAPI and Kafka contracts you already have, and by the
Confluence pages you will export. The target state is "an analyst agent reads one context pack per task and
produces stories, test designs and analytics with trust labels", with a person verifying every document once.

This playbook is written for your situation: IntelliJ plus the Copilot CLI (no VS Code required, no MCP, no
third-party agent frameworks), PowerShell 7 scripts only, OpenAPI documents for the frontend API and for the other
services already stored in the docs repository, a Kafka schema, Confluence pages still to be exported. Every file
named below exists in this investigation repository; copy it, then adapt where the text says "adapt".

Companion documents: [HANDBOOK.md](HANDBOOK.md) explains every piece and why; [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md)
is the meeting checklist; [GUIDE.md](GUIDE.md) is the tour of this prototype. This playbook is the order of work.

Contents: 0 Ground rules and safety · 1 Decisions before you start · 2 Docs repository skeleton · 3 AGENTS.md and the
Copilot files · 4 Contexts and the mapping file · 5 Contracts you already have · 6 Code repositories · 7 Collector ·
8 Graph and indexes · 9 Confluence import · 10 Specs, run by run · 11 Calculations and flows · 12 The analyst ·
13 Maintenance · 14 Scripts catalogue · 15 Agents catalogue · 16 Four-week plan and acceptance

---

## 0. Ground rules and safety

Read this section first; it is what you will be asked about.

**What agents may and may not do** (enforced by files, hooks and CI, not by goodwill):

| Rule | Where it is enforced |
|---|---|
| Agents never edit `generated/**` or any `index.md` | `scripts/hooks/guard-generated.ps1` as a `preToolUse` hook; CI `gen-graph.ps1 -Check`, `build-index.ps1 -Check` |
| Agents never write `verified.by: human:*` | `AGENTS.md` hard rule; `okf-validate.ps1` rejects a `verified` whose actor is not `human:`; review of every PR |
| Every agent-written document is `status: draft` with `generated: { by: copilot/<agent>, at }` | templates, `validate-frontmatter.ps1`, index badges |
| The analyst never opens application source; other agents open at most the files their procedure names | agent files (`.github/agents/*.agent.md`), context pack footer rule |
| An agent cannot finish with an invalid bundle | `agentStop` hook runs the validators (`.github/hooks/docs-quality.json`) |
| One run, one human review, one commit | process; branch protection on the docs repo |
| Synthetic data only in docs, fixtures, packs, work items | `AGENTS.md` hard rule; reviewers; Confluence attachments are not imported |

**What the scripts do and do not do.** Every `scripts/*.ps1` and `scripts/docs/gen-*.ps1` is plain PowerShell 7 with
no modules. The generators read source files with regular expressions and write Markdown under `docs/_generated/`;
they do not compile, run or load application code, and they make no network calls. The only script that talks to
anything outside the working tree is the collector, and it only runs `git` against checkouts you give it. The stubs
(`confluence-export.ps1`, `confluence-publish.ps1`, `jira-push.ps1`, `push-to-tests-repo.ps1`) do nothing until you
implement them. Section 14 lists each script with what it reads and writes.

**Secrets and sensitive content.** Nothing in the docs repository should ever need a secret: contracts, maps and
specs are not secret by construction. Keep configuration files with credentials, customer data and anything legally
sensitive out of Copilot's reach with the repository content-exclusion setting (`code-repo-kit/shared/copilot-content-exclusion.yml`
is the template). The collector needs one read token for the code repositories and PR rights on the docs repository;
store it in the CI secret store, never in a file.

**Headless Copilot runs** (`copilot -p "..."` in CI or scripts): allow only the tools and scripts the agent needs,
keep the `preToolUse` guard on, and never auto-merge an agent's PR. Interactive runs from the terminal follow the same
rules; the hooks apply to both.

**Is it safe to let Copilot read the code at all?** The documentation agents read maps and contracts first and open a
named source range only when a procedure says so; the analyst never does. That is less exposure than a developer's
normal Copilot session. The real controls are the same as for any Copilot use: content exclusion, repository
permissions, and review of what gets committed.

---

## 1. Decisions before you start (one meeting)

1. **Repositories.** Frontend, backend, tests, and a new docs repository. Decide its name and who owns it.
2. **Pilot context.** One business area with one backend entry point, one frontend feature and at least one
   calculation. Everything below is done for this context first, then repeated.
3. **IDs.** Spec IDs `<CTX>-<NNN>` (for example `P1-001`), rules `BR-<ID>-<n>`, calculations `snake_case`. If the
   enterprise already has feature IDs, keep them; the scripts only need the pattern in `features/conventions.md`.
4. **Context list.** The business areas and, per area, the backend class-name prefixes or packages, the frontend
   feature folder, the spec prefix. This becomes `contexts.yml` (section 4).
5. **Roles.** Documentation maintainer (runs the agents, reviews diffs), context owners (Run 4 verification), one
   analyst to evaluate the output, a platform engineer for CI and tokens.
6. **Copilot client.** Copilot CLI for every agent run (hooks and skills work there; the JetBrains plugin has them in
   preview), IntelliJ for reading and reviewing. Verify once on your CLI version that prompt files appear as slash
   commands and that hooks fire in `-p` mode.
7. **Language.** English in files; glossary aliases keep the source-language terms findable.

---

## 2. Docs repository skeleton (half a day)

Create the repository and copy these from `docs-repo/` of this investigation repository, unchanged unless noted:

```
AGENTS.md                      adapt: product name, context list, agent list (section 3)
README.md                      adapt: names
index.md                       keep the "Start here" block; the section list is regenerated
log.md                         empty it except the header
contexts.yml                   rewrite (section 4)
docs-map.yml                   rewrite (section 4)
.markdownlint-cli2.yaml, .gitignore
features/_template.md, features/conventions.md
domain/glossary.md             empty table, keep the columns
domain/context-map.md          rewrite from your context list
domain/calculations/_template.md
architecture/overview.md, integrations.md, adr/template.md     rewrite the prose, keep the frontmatter
flows/_template.md
contracts/conventions.md, contracts/proposed/_template.openapi.yaml   contracts designed before code (proposals)
confluence-import/README.md    keep the quarantine rules; empty the inventory table
generated/                     empty except the folders be/, fe/, openapi/, asyncapi/, graph/, analytics/
migration/, work-items/_schema.yml, work-items/README.md, test-design/README.md
scripts/                       all of it, including scripts/hooks/
ci-examples/                   collect-evidence.yml, code-repo-freshness-gate.yml
third-party/                   the vendored OKF skills and licences
.github/                       agents, instructions, hooks, prompts, skills, workflows (section 3)
```

Delete the Harbor specs, calculations, flows, ADRs and work items; they are examples, not content. Run once:

```powershell
.\scripts\build-index.ps1; .\scripts\okf-validate.ps1 -Strict; .\scripts\validate-frontmatter.ps1
```

All three must pass on the empty skeleton. Protect `main`: PRs only, one approval, CI required.

**Acceptance:** validators green on an empty bundle; `index.md` lists the folders with zero concepts.

---

## 3. AGENTS.md and the Copilot files

`AGENTS.md` is the contract between people and agents. Every Copilot surface reads it first. Keep it under 80 lines.
Write these sections, in this order, adapted from `docs-repo/AGENTS.md`:

1. **What this repository is.** One paragraph: single source of truth for functional and technical documentation of
   `<product>`; Confluence is a publish target; the code repositories are inputs; Jira and the tests repository are
   outputs. One OKF v0.2 bundle: every document has frontmatter with `type`, every folder a generated `index.md`.
2. **Work task-scoped: build the context pack first.** The command `./scripts/context-pack.ps1 -Task <ID|name|text>`,
   what the pack contains, and the sentence "Read the pack, not the repository. Open anything else only to answer a
   question the pack leaves open, and then only the `file:line` it names."
3. **Read order when there is no pack**, cheapest first: `index.md` of the area, the spec, the calculation, `contexts.yml`
   and `generated/graph/REPO_MAP.md`, the maps under `generated/be|fe`, the contracts under `generated/openapi|asyncapi`,
   and only then source code in the sibling checkouts, smallest range, located through the graph or `docs-tags.md`.
4. **Hard rules.** Never hand-edit `generated/**`. Every concept has frontmatter with `type`; folders use `index.md`,
   never `README.md`. Provenance: `generated: { by: copilot/<agent>, at }` on anything an agent writes, `sources[]`
   cited with `[^id]`, never `verified.by: human:*`, `status: draft` until a person verifies. Traceability IDs
   mandatory. Terminology from the glossary; English only. Synthetic data only. Outputs in files; chat under 15 lines;
   specs under 300 lines; diagrams under 25 nodes.
5. **Commands table.** Context pack, validators, indexes, graph and graph query, changed paths to specs, analytics,
   collector, migration board. Copy the table from `docs-repo/AGENTS.md`.
6. **Agents, prompts, skills.** The list of agent names with one line each, the lifecycle sentence (skeleton,
   legacy merge, calculation audit, owner decision), and the pointer to `migration-status.ps1`.

Then copy `.github/` as it is and adapt only names:

| Folder | What to keep | What to adapt |
|---|---|---|
| `.github/copilot-instructions.md` | the pointer to `AGENTS.md`, the never-open list | product name |
| `.github/instructions/*.instructions.md` | all six (features, calculations, confluence-import, generated, test-design, work-items); they are short path-scoped rules | nothing |
| `.github/agents/*.agent.md` | for the pilot three agents are enough: `analyst`, `spec-writer`, `calc-auditor`; add `confluence-migrator` when the first pages arrive, `doc-sync` when the collector runs, `migration-lead`, `test-designer`, `architect`, `impact-analyst` later | the domain sentence in each description |
| `.github/prompts/*.prompt.md` | all; they are the slash commands | nothing |
| `.github/skills/*/SKILL.md` | all; procedures shared by agents | `write-feature-spec/references/source-priority.md` if your source layout differs |
| `.github/hooks/docs-quality.json` | `preToolUse` guard and `agentStop` validators | nothing |
| `.github/workflows/docs-quality.yml` | markdownlint, validators, index and graph checks, link check | runner OS, Python availability for the reference OKF checker (optional) |
| `.github/workflows/copilot-setup-steps.yml` | only if you use the cloud coding agent | - |

**Acceptance:** in the Copilot CLI, opened in the docs repo, `/context-pack` and `/spec-skeleton-from-graph` appear
as commands and `@analyst` is selectable.

---

## 4. Contexts and the mapping file (one hour with a developer who knows the code)

**`contexts.yml`** turns code into bounded contexts without moving code. One entry per business area:

```yaml
contexts:
  billing:
    spec: BIL                          # spec prefix -> features/billing/BIL-001.md
    fe: billing                        # src/features/billing in the frontend
    be: [Billing, Invoice, Tariff]     # backend class-name prefixes (longest prefix wins); unmatched classes -> shared
```

If your backend is organised by package rather than by layer, prefixes still work (most classes are named after
their area); if not, extend `Context-Of` in `gen-graph.ps1` and `migration-status.ps1` to match on the package path.
Iterate until `generated/graph/REPO_MAP.md` shows a `shared` community that holds only true helpers (section 8).

**`docs-map.yml`** is the manual mapping the other analyses recommended: code path globs to the documents they affect.
Write one row per context now, even before any spec exists (`specs: []` is allowed and shows as backlog):

```yaml
mappings:
  - paths: ["be/src/main/kotlin/<root>/**/Billing*.kt", "fe/src/features/billing/**"]
    specs: ["features/billing/BIL-001.md"]
  - paths: ["be/src/main/kotlin/<root>/calc/**"]
    specs: ["domain/calculations/**"]
ignore: ["**/*Test.kt", "**/src/test/**", "**/*.test.ts*", "fe/src/api/generated/**"]
```

It is read by `map-paths.ps1` (changed paths to specs), `check-freshness.ps1` (CI gate), the collector's PR body, and
`gen-graph.ps1`, which turns every row into `implemented-by` edges. That last point means you do not have to put
`@docs` tags into application source before documentation can begin; add tags later on managers and calculators,
where precision matters.

---

## 5. Contracts you already have (one hour)

You already keep the OpenAPI documents in the docs repository. Put them where the scripts and agents look:

| Contract | Location in the docs repo | Who owns the file |
|---|---|---|
| The API the frontend calls | `generated/openapi/backend.yaml` | the collector (copied from the backend repo) |
| APIs of the other services your backend calls | `generated/openapi/external/<service>.yaml` | the collector if they live in the backend repo (`src/main/resources/api/`), otherwise hand-placed with a note in `generated/manifest.yml` |
| Kafka: AsyncAPI document | `generated/asyncapi/backend.yaml` | the collector |
| Kafka: Avro or JSON schemas only | `generated/asyncapi/schemas/<topic>.json`, plus the generated `events.md` map (topic, producer, consumer, payload class with `file:line`) | schemas hand-placed; `events.md` by the generator |

Rules: keep the complete document and the files it references; an external `$ref` that does not resolve inside
`generated/` is rejected by the collector. Record the version and retrieval time of a provider specification in the
manifest when there is no source commit. The frontend's generated client and the backend's generated interfaces are
never read by agents; the contract is the single thing to read (`api.instructions.md`, `api-client.instructions.md`).

**Contracts designed before code.** Your analysts design APIs during analysis, so a contract may exist in the docs
repo before any code. That is a proposal, not evidence, and it has its own folder: `contracts/proposed/<SPEC-ID>.openapi.yaml`
(or `.asyncapi.yaml`), started from `_template.openapi.yaml`, with `x-spec`, `x-status: proposed` and `x-generated-by`
in the `info` block. The spec's API table links to it and says **proposed**; stories cite its `operationId`s and carry
`needs-contract`. The handover is a copy into the code repository that will generate code from it; the collector then
brings the implemented version back under `generated/`, and `doc-sync` switches the spec's links and closes the
proposal. Nothing is ever copied from `contracts/proposed/` into `generated/` by hand. Rules: `contracts/conventions.md`,
`.github/instructions/contracts.instructions.md`; CI lints both folders with the same linters.

The API index generator (`gen-api-index.ps1`) is contract-first: it lists every operation of the OpenAPI document
and finds the handler method by `operationId`. If your controllers are not generated from the contract, adapt the
lookup to your annotations (`@GetMapping("/path")`); the output table stays the same.

---

## 6. Code repositories (one afternoon per repository)

Copy the kit flavour into each repository. `code-repo-kit/apply-kit.ps1 -Flavour be -Target <backend>` copies
everything at once; for the enterprise rollout copy selectively in this order and review each file:

1. **`scripts/docs/`** with `gen-all.ps1`, `_common.ps1` and the generators (section 14 lists each). Run
   `./scripts/docs/gen-all.ps1 -Root .` and read every table in `docs/_generated/`. Where your code differs from the
   simulated one (annotation names, package root, Flyway folder, router style), adjust the regular expression in
   the generator; the tables carry `file:line`, so a wrong row is visible immediately. Target: every endpoint,
   topic, table, scheduled job, route and hook of the pilot context appears once.
2. **`AGENTS.md`** under 60 lines: purpose of the repo, read order (map, then the context's manager or barrel, then
   one named range), the contracts and where they live, conventions, the commands. Adapt from `code-repo-kit/be/AGENTS.md`
   and `fe/AGENTS.md`.
3. **`.github/copilot-instructions.md`** with the never-open list (generated clients, build output, lock files).
4. **`.github/instructions/`**: backend `api`, `calculations`, `kafka`, `migrations`, `tests`, `layers`; frontend
   `api-client`, `features`. Short path-scoped rules; keep the ones that match your stack.
5. **`.github/hooks/docs-maps.json`**: `agentStop` runs `gen-all.ps1 -Check`, so an agent cannot leave stale maps.
6. **`.github/workflows/docs-maps.yml`** from `code-repo-kit/ci/docs-maps.yml`: on pull requests, maps fresh and file
   size budget. Nothing on main; publication belongs to the docs repo (section 7). Start warn-only, make it blocking
   after two sprints.
7. **Content exclusion** in the repository settings from `code-repo-kit/shared/copilot-content-exclusion.yml`.
8. **`@docs` tags**, selectively: `@docs <SPEC-ID>` on the context's entry point (manager or orchestration service)
   and on the frontend barrel, `@docs <calculation_name>` on every business calculator. Not on every class. The
   `docs-tagger` agent and `scripts/docs/tag-candidates.ps1` list candidates per context when you get there.
9. Commit `docs/_generated/` with the code. It is cheap, it gives the PR-time freshness check, and Copilot in the
   code repo reads the maps without running anything.

**Acceptance:** `gen-all.ps1 -Check` passes on a clean checkout and fails when you rename an endpoint without
regenerating; a Copilot question "where is the billing entry point" in the code repo is answered from the map.

---

## 7. Collector (half a day, platform engineer)

One workflow in the docs repository pulls the evidence; the code repositories push nothing.

1. Locally first, from the docs repo, against checkouts of the code repos:
   ```powershell
   .\scripts\collect-evidence.ps1 -Backend ..\backend -Frontend ..\frontend -Generate -Graph
   .\scripts\collect-evidence.ps1 -Backend ..\backend -Frontend ..\frontend          # second run: "no change"
   ```
   It stages maps and contracts, validates the candidate (frontmatter on every map, OpenAPI and AsyncAPI headers,
   no unresolved external `$ref`), replaces the collector-owned sets under `generated/` including deletions, writes
   `generated/manifest.yml` with the source commits and a hash per file, then rebuilds graph and indexes. Nothing
   outside `generated/be|fe|openapi|asyncapi` and `manifest.yml` is touched.
2. CI: `ci-examples/collect-evidence.yml` as `.github/workflows/collect-evidence.yml` in the docs repo. Manual and
   nightly. It needs a GitHub App or bot token with read access to the code repositories and contents plus
   pull-request rights on the docs repository. It opens one PR per snapshot whose body lists the source paths changed
   since the previous manifest, mapped to specs through `docs-map.yml`.
3. If policy forbids cross-repository read access, let each code repo's CI upload `docs/_generated` and the contracts
   as build artifacts and have the collector download them; the script's inputs are directories, so nothing else
   changes.
4. Precise graph exports (`be/templates/GraphExportTest.kt`, `fe/scripts/docs/gen-graph-fe.ts`) are optional; when you
   enable them, the code repo's CI produces the JSON as an artifact and the collector picks it up.

**Acceptance:** an added, a changed and a deleted contract are reflected correctly; a failed validation publishes
nothing; an unchanged run opens no PR.

---

## 8. Graph and indexes (one hour, then iterate)

```powershell
.\scripts\gen-graph.ps1; .\scripts\build-index.ps1
```

Read `generated/graph/REPO_MAP.md`: communities (your contexts), the ranked nodes, the cross-repo flows (route, feature,
endpoint, class, topic or table) and the **spec coverage** list, where every context and every `@docs` calculation
without a document appears as "code only". That list is your backlog. Then:

- `./scripts/graph-query.ps1 -Node context:billing -Depth 2` must show the classes, endpoints, tables and topics you
  expect. Iterate `contexts.yml` until it does.
- `./scripts/migration-status.ps1 -Scope all` writes `migration/all.md`: per context the runs due with the command.

**Acceptance:** `gen-graph.ps1 -Check` and `build-index.ps1 -Check` pass twice in a row; the pilot context's community
file names its entry point.

---

## 9. Confluence import (half a day per space)

Export the space to HTML (the standard space export, no API needed) and run the importer: the specification is in
[MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md) step 3 and the stub `scripts/confluence-export.ps1`. It writes one Markdown
file per page under `confluence-import/<SPACE>/` with a header block (`source`, `last_modified`, `author`,
`confluence_id`, `url`) and an inventory table in `confluence-import/README.md`. Rules, all enforced by
`confluence-import.instructions.md` and the quarantine README: nothing in that folder is authoritative; pages are
migrated one per run; processed pages move to `_done/` with `status: migrated|obsolete`; attachments and anything with
customer data are not imported; the folder is excluded from the validators.

Triage the inventory with the analysts: for each page the target context and a known state (current, partly outdated,
obsolete, formula page). Formula pages are routed to the calculation audit, never merged by hand.

---

## 10. Specs, run by run (the core of the work)

One spec is written in four runs; one Copilot run, one human review of the diff, one commit each. The lifecycle skill
(`.github/skills/spec-lifecycle/SKILL.md`) and its review checklist (`references/run-checklist.md`) are the reference.
All commands are typed in the Copilot CLI opened in the docs repo.

**Run 1, skeleton from the code.** `/spec-skeleton-from-graph billing BIL-001`. The `spec-writer` reads the context's
graph file, the contracts and the components map, plus exactly one source file, the context's entry point, and writes
`features/billing/BIL-001.md`: API, events, data and UI flow from the graph with exact names; summary, actors and
business rules from the entry point's documentation, each rule one MUST sentence with an ID; everything unsourced
under Open questions; `status: draft`, no `verified`. Do this for every context in one sitting; it is mechanical.

**Run 2, legacy pages.** `@confluence-migrator confluence-import/<SPACE>/<page>.md`, one page per run. New facts are
merged into the skeleton, contradictions become `> ⚠️ CONFLICT (legacy: <page>)` callouts, unverifiable claims
`> ❓ UNVERIFIED`, domain terms go to the glossary, the page is cited in `sources[]` and moved to `_done/`. No number,
threshold or formula is copied from a page.

**Run 3, calculations.** `/audit-calculation <name>` for every calculation the context uses. The `calc-auditor`
opens the calculator and its unit test, nothing else, and writes or audits `domain/calculations/<name>.md`: formula,
parameters, worked examples copied from the test, an `## Audit <date>` table with MATCH, DOC-STALE, CODE-SUSPECT or
UNDOCUMENTED per item, open questions naming the owner. A calculator without a unit test gets one first; the test is
the executor of the concept.

**Run 4, owner decision.** A person reads the spec and its calculations, answers the open questions in the change
log, sets `status: stable`, adds `verified: { by: human:<id>, at }` and `stale_after`. The badge turns human-reviewed.
`migration-status.ps1` lists exactly what is still due; "ready for the analyst" is: spec stable and verified, every
linked calculation audited, no pending page, pack within budget.

After every run: `./scripts/okf-validate.ps1 -Strict; ./scripts/build-index.ps1`, a line in `log.md`, a PR, a review.
The `agentStop` hook runs the validators anyway.

---

## 11. Calculations and flows

**Calculations** are `type: Attested Computation` documents: inputs with units, parameters with defaults and where
they are read from, outputs with rounding, the formula, a step list with footnotes to the source, the sanctioned code
shape, conventions, worked examples copied from the test with the test method named, an audit table, open questions.
Agents bind parameters; they never re-derive a formula. `calculation-spec` and `legacy-page-audit` are the skills.

**Flows** (`flows/<name>.md`, `type: Flow`) exist only for behaviour that crosses contexts or windows: trigger,
participants, steps with `file:line`, invariants, source map. The spec-writer creates one during Run 1 when the graph
neighbourhood crosses communities; the architect writes larger ones on request. They follow the lifecycle of the spec
that spawned them.

**Glossary** rows are added by the migrator (Run 2) and the spec-writer; the Aliases column keeps legacy and
source-language wording so searches still find the concept.

---

## 12. The analyst

What the analyst agent is told (`.github/agents/analyst.agent.md`), in short: build the pack, read it top to bottom,
check the badge, slice stories per the `jira-work-items` skill with Gherkin criteria citing rule IDs, derive subtasks
per graph node kind, write `work-items/<ID>.yml`, validate it, put gaps into `questions[]` and, when blocking, into the
spec's Open questions. Never read source; only when the pack leaves a question and names a `file:line`, open that
range and record the fact as an open question.

The everyday sequence:

```powershell
./scripts/context-pack.ps1 -Task BIL-001            # or in the CLI: /context-pack BIL-001
# in the Copilot CLI:
@analyst /jira-from-spec BIL-001
./scripts/validate-work-items.ps1 work-items/BIL-001.yml
./scripts/coverage-matrix.ps1                        # BR -> story -> scenario matrix, badges, staleness
```

Handoffs: `test-designer` (`/tests-from-spec BIL-001`) for Gherkin scenarios and synthetic fixtures, `architect`
(`/hld-from-spec`) for a design, `impact-analyst` (`/impact-from-graph <node|file>`) for blast radius,
`/coverage-report` for analytics questions. Stories from a draft spec carry `needs-spec-review`; that label is the
analyst's honesty, not a defect.

Measure from the first week: analyst time per story, share of stories a human analyst accepts unchanged, open
questions per spec, Copilot premium requests per run.

---

## 13. Maintenance

- **Code changes.** The collector's PR names the specs in the blast radius (manifest diff through `docs-map.yml`).
  `doc-sync` runs on that PR: compares API, events and data sections with the new contracts and maps, updates them,
  appends a change-log row, flags calculations for `calc-auditor` when calculator files changed, stubs any new
  context. A person reviews and merges. The freshness gate in the code repos (`check-freshness.ps1`,
  `ci-examples/code-repo-freshness-gate.yml`) requires a PR touching a mapped path to bump `last_verified` or carry
  the label `docs-not-affected`.
- **Confluence changes.** Re-export, re-import; the inventory shows pages newer than their `_done/` copy; Run 2 again.
- **Drift found by a reader.** Open question in the spec, status back to draft, owner decides; never a silent edit.
- **The board.** `migration-status.ps1 -Scope all` weekly; the `migration-lead` agent annotates order and blockers.

---

## 14. Scripts catalogue (what each one reads and writes)

Docs repository, `scripts/` (PowerShell 7, no modules, no network unless stated):

| Script | Reads | Writes | Safe to run any time |
|---|---|---|---|
| `context-pack.ps1 -Task <x> [-Budget N] [-Print]` | specs, calculations, `graph.json`, contracts, db schema, work items | `.context/<task>.md` (git-ignored) | yes |
| `graph-query.ps1 -Node <id> -Depth n` / `-Files <paths>` / `-Find <text>` | `generated/graph/graph.json` | stdout | yes |
| `gen-graph.ps1 [-Check]` | `generated/be|fe/*.md`, `contexts.yml`, `docs-map.yml`, optional precise exports | `generated/graph/REPO_MAP.md`, `<context>.md`, `graph.json` | yes; `-Check` writes nothing |
| `build-index.ps1 [-Check]` | frontmatter of every concept | every `index.md` | yes |
| `okf-validate.ps1 [-Strict]` | the bundle | stdout, exit code | yes |
| `validate-frontmatter.ps1` | `features/`, `domain/calculations/` | stdout, exit code | yes |
| `validate-work-items.ps1 [file]` | `work-items/*.yml`, `_schema.yml`, specs (rule IDs) | stdout, exit code | yes |
| `coverage-matrix.ps1` | specs, work items, feature files | `generated/analytics/coverage-matrix.md|json` | yes |
| `map-paths.ps1` (stdin paths) | `docs-map.yml` | stdout | yes |
| `check-freshness.ps1` | PR diff, specs | exit code | CI |
| `collect-evidence.ps1 [-Generate] [-Graph] [-DryRun]` | the code checkouts (`git`, `docs/_generated`, contracts) | `generated/be|fe|openapi|asyncapi/**`, `generated/manifest.yml`; with `-Graph` also graph and indexes | yes; `-DryRun` writes nothing; the only script that runs `git` |
| `migration-status.ps1 -Scope <ctx|all>` | `contexts.yml`, specs, calculations, docs tags, REPO_MAP, pending pages | `migration/<scope>.md` | yes |
| `hooks/guard-generated.ps1` | the hook payload | permission decision | hook |
| `confluence-export.ps1`, `confluence-publish.ps1`, `jira-push.ps1`, `push-to-tests-repo.ps1` | - | - | stubs; implement per environment |

Code repositories, `scripts/docs/` (regex scanners, no build, no execution of application code):

| Generator | Backend output | Frontend output |
|---|---|---|
| `gen-codebase-map.ps1` | modules and layers with class counts | feature folders with routes, hooks, components, BroadcastChannels |
| `gen-components.ps1` | one row per class: layer, annotations, injected dependencies, `file:line` | the shared component library: props, used-by features |
| `gen-api-index.ps1` | every OpenAPI operation with its handler method | - |
| `gen-events.ps1` | topics with producers, consumers, payload classes | - |
| `gen-db-schema.ps1` | tables and columns from the migrations | - |
| `gen-jobs.ps1` | scheduled jobs with cron and class | - |
| `gen-routes.ps1` | - | routes to screens |
| `gen-types-index.ps1` | - | exported types per feature |
| `gen-docs-tags.ps1` | `@docs <ID>` tags with `file:line` | same |
| `tag-candidates.ps1` | candidates for tags per context, with proposed IDs | same |
| `gen-all.ps1 [-Check]` | runs all of the above; `-Check` fails when a map is stale | same |
| `shared/check-file-size.ps1` | line-count budget with a baseline (token hygiene) | same |

---

## 15. Agents catalogue

| Agent | Input | May read | Writes | Start with it in |
|---|---|---|---|---|
| `analyst` | spec ID, calculation, graph node, free text, analytics question | the pack; a named `file:line` only when blocked | `work-items/<ID>.yml`, open questions in the spec, `generated/analytics/*` | week 1 |
| `spec-writer` | context + ID | pack, `generated/graph/<ctx>.md`, contracts, the entry-point class | `features/<ctx>/<ID>.md`, `docs-map.yml`, `log.md` | week 1 |
| `calc-auditor` | calculation name, spec ID or formula page | the calculator and its unit test, nothing else | `domain/calculations/<name>.md` with audit table | week 1 |
| `confluence-migrator` | one page path | the page, the pack, `generated/` | merged concept, glossary rows, page moved to `_done/` | week 2 |
| `doc-sync` | the collector's PR | `map-paths`, `graph-query -Files`, contracts, maps | change-log rows, `last_verified`, stubs | week 3 |
| `migration-lead` | scope | `migration-status` output, REPO_MAP, index badges | `migration/<scope>.md` notes | week 2 |
| `test-designer` | spec ID | the pack | `test-design/features/<ID>.feature`, fixtures | week 3 |
| `architect` | spec or epic | `architecture/`, graph, contracts, spec frontmatter | `architecture/hld/<ID>.md`, ADR drafts | week 4 |
| `impact-analyst` | node or file | `generated/graph/` | checklist | week 3 |

Common contract of all agents, written in every agent file: build the pack first; files first, chat under 15 lines;
set `generated.by: copilot/<agent>`; never write `verified.by: human:*`; never edit `generated/**`; finish with the
validators, the indexes and a log line.

---

## 16. Four-week plan and acceptance

| Week | Work | Done when |
|---|---|---|
| 1 | Sections 1 to 4, 6 for the pilot repos, 8. Run 1 for the pilot context. | validators green; maps correct for the pilot; `REPO_MAP.md` shows the pilot community; one draft spec exists |
| 2 | Section 5 (contracts in place), 9 (first space imported), Run 2 and Run 3 for the pilot, Run 4 by the owner. First analyst run. | pilot spec human-reviewed, calculations audited; `work-items/<ID>.yml` validated; a human analyst has judged the stories |
| 3 | Section 7 (collector in CI), 13 (doc-sync on the first collector PR), Run 1 for all remaining contexts. | one collector PR merged; every context has at least a draft spec; the freshness gate is warn-only |
| 4 | Run 2 and 3 for two more contexts, test designs, coverage report to the team, freshness gate blocking. | three contexts ready for the analyst; the board shows the rest with owners and dates |

The success criterion is not the number of files or agents. It is: an analyst question answered from the docs with
rule IDs and a trust badge, and a code change that correctly triggers a documentation review.
