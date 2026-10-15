# Enterprise playbook: build the documentation flow for the analyst agent, step by step

What you are building: a documentation repository that GitHub Copilot can read instead of your code, fed by small
generated maps from the frontend and backend, by the OpenAPI and Kafka contracts you already have, and by the
Confluence pages you will export. The target state is "an analyst agent reads one context pack per task and
produces stories, test designs and analytics with trust labels", with a person verifying every document once. The order of work is documentation first (phase 1, sections 1 to 11
and 13), then the analyst (phase 2, section 12); section 16 has the plan and the gate between the two.

This playbook is written for your situation: IntelliJ plus the Copilot CLI (no VS Code required, no MCP, no
third-party agent frameworks), standard-library Python 3.11+ scripts only, OpenAPI documents for the frontend API and for the other
services already stored in the docs repository, a Kafka schema, Confluence pages still to be exported. Every file
named below exists in this investigation repository; copy it, then adapt where the text says "adapt".

Companion documents: [HANDBOOK.md](HANDBOOK.md) explains every piece and why; [MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md)
is the meeting checklist; [GUIDE.md](GUIDE.md) is the tour of this prototype. This playbook is the order of work.

Contents: 0 Ground rules and safety · 1 Decisions before you start · 2 Docs repository skeleton · 3 AGENTS.md and the
Copilot files · 4 Contexts and the mapping file · 5 Contracts you already have · 6 Code repositories · 7 Collector ·
8 Graph and indexes · 9 Confluence import · 10 Specs, run by run · 11 Calculations and flows · 12 The analyst ·
13 Maintenance · 14 Scripts catalogue · 15 Agents catalogue · 16 Plan: documentation first, analyst second · 17 Lessons from the first trial · 18 Human-owned documents an agent may draft · 19 Several repositories in IntelliJ · 20 Workstations: Windows and macOS

---

## 0. Ground rules and safety

Read this section first; it is what you will be asked about.

**What agents may and may not do** (enforced by files, hooks and CI, not by goodwill):

| Rule | Where it is enforced |
|---|---|
| Agents never edit `generated/**` or any `index.md` | `scripts/hooks/guard-generated.py` as a `preToolUse` hook; CI `gen-graph.py --check`, `build-index.py --check` |
| Agents never write `verified.by: human:*` | `AGENTS.md` hard rule; `okf-validate.py` rejects a `verified` whose actor is not `human:`; review of every PR |
| Every agent-written document is `status: draft` with `generated: { by: copilot/<agent>, at }` | templates, `validate-frontmatter.py`, index badges |
| The analyst never opens application source; other agents open at most the files their procedure names | agent files (`.github/agents/*.agent.md`), context pack footer rule |
| An agent cannot finish with an invalid bundle | `agentStop` hook runs the validators (`.github/hooks/docs-quality.json`) |
| One run, one human review, one commit | process; branch protection on the docs repo |
| Synthetic data only in docs, fixtures, packs, work items | `AGENTS.md` hard rule; reviewers; Confluence attachments are not imported |

**What the scripts do and do not do.** Every `scripts/*.py` and `scripts/docs/gen-*.py` is plain Python 3.11+ with
no third-party packages. The generators read source files with regular expressions and write Markdown under `docs/_generated/`;
they do not compile, run or load application code, and they make no network calls. The only script that talks to
anything outside the working tree is the collector, and it only runs `git` against checkouts you give it. The stubs
(`confluence-export.py`, `confluence-publish.py`, `jira-push.py`, `push-to-tests-repo.py`) do nothing until you
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
2. **Scope: a slice, not the product.** Write down the first tasks the analyst should get, and list the bounded
   contexts they touch, usually one to three. That list is the scope of phase 1; everything else stays "code only"
   on the migration board with an owner and a date. Two kinds of work behave differently here:
   - **generated, whole product for free:** code maps, graph, contracts, parameter and dataset catalogues, indexes.
     The generators scan the entire repository; there is no cheaper partial run and the full result is what makes
     "what else touches this table" answerable.
   - **written and reviewed, per context:** specs (Runs 1 to 4), calculations, flows, glossary rows, Confluence
     pages, test designs. Done only for the contexts in scope; the board shows the rest as due.
   The first context in scope is the pilot: one backend entry point, one frontend feature, at least one
   calculation. Everything below is done for it first, then for the other contexts in scope.
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
index.md                       edit the `# <Product> documentation bundle` heading once, keep the "Start here" block; the section list is regenerated
log.md                         empty it except the header
contexts.yml                   rewrite (section 4)
docs-map.yml                   rewrite (section 4)
.markdownlint-cli2.yaml, .gitignore, .gitattributes   (line-ending normalisation, section 20)
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
.github/skills/*/references/   keep the pointer files too (17.6): every reference a skill names is reachable from that skill
ci-examples/                   collect-evidence.yml, code-repo-freshness-gate.yml
third-party/                   the vendored OKF skills and licences
.github/                       agents, instructions, hooks, prompts, skills, workflows (section 3)
```

Delete the Harbor specs, calculations, flows, ADRs, work items, test fixtures (`test-design/fixtures/*.json`) and the
legacy pages under `confluence-import/HARBOR/`; they are examples, not content. Rewrite `architecture/overview.md`,
`architecture/integrations.md` and `domain/context-map.md` before validating: their links point at the deleted examples
and `--strict` turns broken links into failures. Run once:

```bash
python3 scripts/build-index.py; python3 scripts/okf-validate.py --strict; python3 scripts/validate-frontmatter.py
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
2. **Work task-scoped: build the context pack first.** The command `python3 scripts/context-pack.py --task <ID|name|text>`,
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
   legacy merge, calculation audit, owner decision), and the pointer to `migration-status.py`.

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
their area); if not, extend `Context-Of` in `gen-graph.py` and `migration-status.py` to match on the package path.
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

It is read by `map-paths.py` (changed paths to specs), `check-freshness.py` (CI gate), the collector's PR body, and
`gen-graph.py`, which turns every row into `implemented-by` edges. That last point means you do not have to put
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

The API index generator (`gen-api-index.py`) is contract-first: it lists every operation of the OpenAPI document
and finds the handler method by `operationId`. If your controllers are not generated from the contract, adapt the
lookup to your annotations (`@GetMapping("/path")`); the output table stays the same.

---

## 6. Code repositories (one afternoon per repository)

Copy the kit flavour into each repository. `code-repo-kit/apply-kit.py --flavour be --target <backend>` copies
everything at once; for the enterprise rollout copy selectively in this order and review each file:

1. **`scripts/docs/`** with `gen-all.py`, `_common.py` and the generators (section 14 lists each). Run
   `python3 scripts/docs/gen-all.py --root .` and read every table in `docs/_generated/`. Where your code differs from the
   simulated one (annotation names, package root, Flyway folder, router style), adjust the regular expression in
   the generator; the tables carry `file:line`, so a wrong row is visible immediately. Target: every endpoint,
   topic, table, scheduled job, route and hook of the pilot context appears once.
2. **`AGENTS.md`** under 60 lines: purpose of the repo, read order (map, then the context's manager or barrel, then
   one named range), the contracts and where they live, conventions, the commands. Adapt from `code-repo-kit/be/AGENTS.md`
   and `fe/AGENTS.md`.
3. **`.github/copilot-instructions.md`** with the never-open list (generated clients, build output, lock files).
4. **`.github/instructions/`**: backend `api`, `calculations`, `kafka`, `migrations`, `tests`, `layers`; frontend
   `api-client`, `features`. Short path-scoped rules; keep the ones that match your stack.
5. **`.github/hooks/docs-maps.json`**: `agentStop` runs `gen-all.py --check`, so an agent cannot leave stale maps.
6. **`.github/workflows/docs-maps.yml`** from `code-repo-kit/ci/docs-maps.yml`: on pull requests, maps fresh and file
   size budget. Nothing on main; publication belongs to the docs repo (section 7). Start warn-only, make it blocking
   after two sprints.
7. **Content exclusion** in the repository settings from `code-repo-kit/shared/copilot-content-exclusion.yml`.
8. **`@docs` tags**, selectively: `@docs <SPEC-ID>` on the context's entry point (manager or orchestration service)
   and on the frontend barrel, `@docs <calculation_name>` on every business calculator. Not on every class. The
   `docs-tagger` agent and `scripts/docs/tag-candidates.py` list candidates per context when you get there.
9. Commit `docs/_generated/` with the code. It is cheap, it gives the PR-time freshness check, and Copilot in the
   code repo reads the maps without running anything.

**Acceptance:** `gen-all.py --check` passes on a clean checkout and fails when you rename an endpoint without
regenerating; a Copilot question "where is the billing entry point" in the code repo is answered from the map.

---

## 7. Collector (half a day, platform engineer)

One workflow in the docs repository pulls the evidence; the code repositories push nothing.

1. Locally first, from the docs repo, against checkouts of the code repos:
   ```bash
   ./scripts/collect-evidence.py --backend ../backend --frontend ../frontend --generate --graph
   ./scripts/collect-evidence.py --backend ../backend --frontend ../frontend          # second run: "no change"
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

```bash
python3 scripts/gen-graph.py; python3 scripts/build-index.py
```

Read `generated/graph/REPO_MAP.md`: communities (your contexts), the ranked nodes, the cross-repo flows (route, feature,
endpoint, class, topic or table) and the **spec coverage** list, where every context and every `@docs` calculation
without a document appears as "code only". That list is your backlog. Then:

- `python3 scripts/graph-query.py --node context:billing --depth 2` must show the classes, endpoints, tables and topics you
  expect. Iterate `contexts.yml` until it does.
- `python3 scripts/migration-status.py --scope all` writes `migration/all.md`: per context the runs due with the command.

**Acceptance:** `gen-graph.py --check` and `build-index.py --check` pass twice in a row; the pilot context's community
file names its entry point.

---

## 9. Confluence import (half a day per space)

Export the space to HTML (the standard space export, no API needed) and run the importer: the specification is in
[MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md) step 3 and the stub `scripts/confluence-export.py`. It writes one Markdown
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
`migration-status.py` lists exactly what is still due; "ready for the analyst" is: spec stable and verified, every
linked calculation audited, no pending page, pack within budget.

After every run: `python3 scripts/okf-validate.py --strict; python3 scripts/build-index.py`, a line in `log.md`, a PR, a review.
The `agentStop` hook runs the validators anyway.

---

## 11. Calculations and flows

**Calculations** are `type: Attested Computation` documents: inputs with units, parameters with defaults and where
they are read from, outputs with rounding, the formula, a step list with footnotes to the source, the sanctioned code
shape, conventions, worked examples copied from the test with the test method named, an audit table, open questions.
Agents bind parameters; they never re-derive a formula. `calculation-spec` and `legacy-page-audit` are the skills.
The `## Parameters` table names keys exactly as in `generated/be/parameters.md`; the admin spec maps each key to the
calculation that owns its meaning, and `validate-frontmatter.py` checks both directions (17.7). Worked examples come
from unit tests; scenario setups cite named datasets from `generated/be/datasets.md` (17.7).

**Flows** (`flows/<name>.md`, `type: Flow`) exist only for behaviour that crosses contexts or windows: trigger,
participants, steps with `file:line`, invariants, source map. The spec-writer creates one during Run 1 when the graph
neighbourhood crosses communities; the architect writes larger ones on request. They follow the lifecycle of the spec
that spawned them.

**Glossary** rows are added by the migrator (Run 2) and the spec-writer; the Aliases column keeps legacy and
source-language wording so searches still find the concept.

---

## 12. The analyst

Phase 2 of the plan (section 16): run the analyst on real tasks only after the "documentation ready" gate is passed
for the contexts those tasks touch (the scope of section 1). A task that crosses into an out-of-scope context is
the signal to bring that context through Runs 1 to 4 next, not to let the analyst guess.

What the analyst agent is told (`.github/agents/analyst.agent.md`), in short: build the pack, read it top to bottom (spec, calculations, flows,
graph, contracts, tables, related work), check the badge, slice stories per the `jira-work-items` skill with Gherkin criteria citing rule IDs, derive subtasks
per graph node kind, write `work-items/<ID>.yml`, validate it, put gaps into `questions[]` and, when blocking, into the
spec's Open questions. Never read source; only when the pack leaves a question and names a `file:line`, open that
range and record the fact as an open question (decision and setup: 17.2 and section 19). On a finished feature the
input is a change request and the output is delta stories only (17.1).

The everyday sequence:

```bash
python3 scripts/context-pack.py --task BIL-001            # or in the CLI: /context-pack BIL-001
# in the Copilot CLI:
@analyst /jira-from-spec BIL-001
python3 scripts/validate-work-items.py work-items/BIL-001.yml
python3 scripts/coverage-matrix.py                        # BR -> story -> scenario matrix, badges, staleness
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
  context. A person reviews and merges. The freshness gate in the code repos (`check-freshness.py`,
  `ci-examples/code-repo-freshness-gate.yml`) requires a PR touching a mapped path to bump `last_verified` or carry
  the label `docs-not-affected`.
- **Confluence changes.** Re-export, re-import; the inventory shows pages newer than their `_done/` copy; Run 2 again.
- **Drift found by a reader.** Open question in the spec, status back to draft, owner decides; never a silent edit.
- **The board.** `migration-status.py --scope all` weekly; the `migration-lead` agent annotates order and blockers.

---

## 14. Scripts catalogue (what each one reads and writes)

Docs repository, `scripts/` (Python 3.11+, standard library only, no network unless stated):

| Script | Reads | Writes | Safe to run any time |
|---|---|---|---|
| `context-pack.py --task <x> [--budget N] [--print]` | specs, calculations, `graph.json`, contracts, db schema, work items | `.context/<task>.md` (git-ignored) | yes |
| `graph-query.py --node <id> --depth n` / `--files <paths>` / `--find <text>` | `generated/graph/graph.json` | stdout | yes |
| `gen-graph.py [--check]` | `generated/be|fe/*.md`, `contexts.yml`, `docs-map.yml`, optional precise exports | `generated/graph/REPO_MAP.md`, `<context>.md`, `graph.json` | yes; `--check` writes nothing |
| `build-index.py [--check]` | frontmatter of every concept | every `index.md` | yes |
| `okf-validate.py [--strict]` | the bundle | stdout, exit code | yes |
| `validate-frontmatter.py` | `features/`, `domain/calculations/`, `flows/`, `generated/be/parameters.md` | stdout, exit code | yes |
| `validate-work-items.py [file]` | `work-items/*.yml`, `_schema.yml`, specs (rule IDs) | stdout, exit code | yes |
| `coverage-matrix.py` | specs, work items, feature files | `generated/analytics/coverage-matrix.md|json` | yes |
| `map-paths.py` (stdin paths) | `docs-map.yml` | stdout | yes |
| `check-freshness.py` | PR diff, specs | exit code | CI |
| `collect-evidence.py [--generate] [--graph] [--dry-run]` | the code checkouts (`git`, `docs/_generated`, contracts) | `generated/be|fe|openapi|asyncapi/**`, `generated/manifest.yml`; with `--graph` also graph and indexes | yes; `--dry-run` writes nothing; the only script that runs `git` |
| `migration-status.py --scope <ctx|all>` | `contexts.yml`, specs, calculations, docs tags, REPO_MAP, pending pages | `migration/<scope>.md` | yes |
| `hooks/guard-generated.py` | the hook payload | permission decision | hook |
| `confluence-export.py`, `confluence-publish.py`, `jira-push.py`, `push-to-tests-repo.py` | - | - | stubs; implement per environment |

Code repositories, `scripts/docs/` (regex scanners, no build, no execution of application code):

| Generator | Backend output | Frontend output |
|---|---|---|
| `gen-codebase-map.py` | modules and layers with class counts | feature folders with routes, hooks, components, BroadcastChannels |
| `gen-components.py` | one row per class: layer, annotations, injected dependencies, `file:line` | the shared component library: props, used-by features |
| `gen-api-index.py` | every OpenAPI operation with its handler method | - |
| `gen-events.py` | topics with producers, consumers, payload classes | - |
| `gen-db-schema.py` | tables and columns from the migrations | - |
| `gen-jobs.py` | scheduled jobs with cron and class | - |
| `gen-parameters.py` | admin parameter catalogue: key, seeded defaults per scope, readers, validator (cross-checked against the calculations by `validate-frontmatter.py`) | - |
| `gen-datasets.py` | named synthetic datasets (seed scripts, integration fixtures): purpose, tables and row counts, loaders, one sample row - analysts cite setups by name instead of describing rows | - |
| `gen-routes.py` | - | routes to screens |
| `gen-types-index.py` | - | exported types per feature |
| `gen-docs-tags.py` | `@docs <ID>` tags with `file:line` | same |
| `tag-candidates.py` | candidates for tags per context, with proposed IDs | same |
| `gen-all.py [--check]` | runs all of the above; `--check` fails when a map is stale | same |
| `shared/check-file-size.py` | line-count budget with a baseline (token hygiene) | same |

---

## 15. Agents catalogue

| Agent | Input | May read | Writes | Start with it in |
|---|---|---|---|---|
| `analyst` | spec ID, calculation, graph node, free text, analytics question | the pack; a named `file:line` only when blocked | `work-items/<ID>.yml`, open questions in the spec, `generated/analytics/*` | week 1 |
| `spec-writer` | context + ID | pack, `generated/graph/<ctx>.md`, contracts, the entry-point class | `features/<ctx>/<ID>.md`, `docs-map.yml`, `log.md` | week 1 |
| `calc-auditor` | calculation name, spec ID or formula page | the calculator and its unit test, nothing else | `domain/calculations/<name>.md` with audit table | week 1 |
| `confluence-migrator` | one page path | the page, the pack, `generated/` | merged concept, glossary rows, page moved to `_done/` | week 2 |
| `doc-sync` | the collector's PR | `map-paths`, `graph-query --files`, contracts, maps | change-log rows, `last_verified`, stubs | week 3 |
| `migration-lead` | scope | `migration-status` output, REPO_MAP, index badges | `migration/<scope>.md` notes | week 2 |
| `test-designer` | spec ID | the pack | `test-design/features/<ID>.feature`, fixtures | week 3 |
| `architect` | spec or epic | `architecture/`, graph, contracts, spec frontmatter | `architecture/hld/<ID>.md`, ADR drafts | week 4 |
| `impact-analyst` | node or file | `generated/graph/` | checklist | week 3 |

Common contract of all agents, written in every agent file: build the pack first; files first, chat under 15 lines;
set `generated.by: copilot/<agent>`; never write `verified.by: human:*`; never edit `generated/**`; finish with the
validators, the indexes and a log line.

---

## 16. Plan: documentation first, analyst second

The work has two phases with a gate between them. Phase 1 builds the documentation and proves it on readers who
are not agents. Phase 2 puts the analyst agent on it. Nothing in phase 1 depends on the analyst, and starting the
analyst on documentation that is not ready produces exactly the result of the first trial (section 17): valid files
about the wrong thing.

### Phase 1 - documentation ready (weeks 1 to 4)

| Week | Work | Done when |
|---|---|---|
| 1 | Sections 1 to 4; section 6 for the pilot repositories; section 8. Run 1 for the pilot context. | validators green; maps correct for the pilot; `REPO_MAP.md` shows the pilot community; one draft spec exists |
| 2 | Section 5 (contracts in place); section 9 (first Confluence space imported); Run 2 and Run 3 for the pilot; Run 4 by the owner. Parameter and dataset headers in the pilot repositories (17.7). | pilot spec human-reviewed, calculations audited; the two catalogues collected; `validate-frontmatter.py` green with the parameter cross-check |
| 3 | Section 7 (collector in CI); section 13 (doc-sync on the first collector PR); Run 1 for the other contexts in scope (and, if cheap, skeletons for the rest); section 6 for the remaining repositories. | one collector PR merged; every context in scope has at least a draft spec; the freshness gate is warn-only |
| 4 | Run 2 and 3 for the other contexts in scope; the Confluence spaces those contexts need; glossary and flows; freshness gate blocking; the reader test of 17.3. | every context in scope human-reviewed; the board shows the rest with owners and dates; one designer's five questions on github.com answered with rule IDs and badges |

**Gate: documentation ready.** All of these, checked by the documentation maintainer and one context owner:

- `okf-validate.py --strict`, `validate-frontmatter.py`, `gen-graph.py --check`, `build-index.py --check` green on `main`,
  and the code repositories' `gen-all.py --check` green on their `main`.
- The collector runs on schedule and its PRs are reviewed and merged; the manifest names the commits it collected.
- Every context **in scope** has a human-reviewed spec (`verified`, `stale_after` set) and every calculation it links
  is audited (status not `draft`) or carries an open question with an owner. Contexts out of scope have a Run 1
  skeleton at most and appear on the board as due; a spec the first tasks will cite must not be out of scope.
- The migration board (`migration/all.md`) has an owner and a date for every remaining run.
- `generated/be/parameters.md` and `generated/be/datasets.md` exist and the two-way parameter check passes.
- A reader who is not an analyst (designer, owner) gets correct answers with rule IDs and badges from Copilot chat on
  github.com, and the Confluence publish of the human-reviewed specs is in place.
- Costs of phase 1 are known: premium requests per run per agent (spec-writer, migrator, auditor, doc-sync).

Until the gate is passed, the analyst agent is not run on real tasks. It may be run once, in week 4, on the pilot
context with a change request, only to calibrate the pack budget and the step vocabulary, and its output is discarded.

### Phase 2 - the analyst (weeks 5 and 6)

| Week | Work | Done when |
|---|---|---|
| 5 | Section 12 and 17.1, 17.2: the analyst on change requests for the human-reviewed contexts, interactively in the IDE or CLI (section 19). A human analyst reviews every file. Test designs for the same stories (`test-designer`). | stories accepted unchanged by the human analyst above an agreed share; every story cites existing rule IDs; `needs-spec-review` appears only on draft specs |
| 6 | Coverage report to the team (`/coverage-report`); headless runs only in CI (17.4); API design skill and Spectral ruleset if proposals are being written (17.8); decide the analyst's standing tasks. | the coverage matrix is read in the sprint review; premium requests per story are known; the next contexts for Run 2 and 3 are chosen from the analyst's gaps |

Read section 17 before week 5; the acceptance of week 5 is one analyst run on a change request producing delta
stories only, judged by a human analyst.

The success criterion is not the number of files or agents. It is: an analyst question answered from the docs with
rule IDs and a trust badge, and a code change that correctly triggers a documentation review.

---

## 17. Lessons from the first trial (read before phase 2)

The first headless analyst run on a finished spec (ADM-001, Copilot CLI, 67 seconds, about 7.5 premium requests)
produced a valid file and four honest open questions, and taught the following. Each item is a rule in the
repository now; this section says why, so you keep it when you adapt the files.

**17.1 Brownfield: the analyst produces delta stories.** `jira-from-spec` on a spec whose graph neighbourhood is already
implemented produced stories to build what exists. The analyst agent now checks the pack's graph section first: when
the endpoints, hooks and components of the spec are present, the input must be a change request and the stories
describe only the delta; without a change request the agent says "implemented, nothing to build" and stops. Give
the analyst tasks like "ADM-001: warn when a parameter an open session has snapshotted is edited", not bare IDs,
unless the feature is new. Example of a delta story: `work-items/ADM-001.yml`, story S4.

**17.2 Code access for the analyst: allowed locally, absent on the web.** Decision: the analyst may open exactly the
`file:line` a pack names in `../backend` or `../frontend`, when a question blocks the task, and must record what it
learned as an open question in the spec. The code repositories are sibling checkouts (section 19). Where they are
not available, for example Copilot chat on github.com or a machine with the docs repo only, the agent records the
question and stops; nothing else in the procedure depends on code access, so the web experience is not broken.
Headless runs that should have this access pass `--add-dir ../backend --add-dir ../frontend`; runs that should not,
simply omit the flags and the CLI refuses the path.

**17.3 Readers who are not analysts.** Product designers, owners and support read on github.com. There, nothing runs:
no pack, no hooks, no validators. Copilot chat on the repository reads the files and applies
`.github/copilot-instructions.md` (start at `index.md`, cite spec and rule IDs, name the badge, never present a draft
as verified); prompt files and custom agents are not available there. For a curated entry point use Copilot Spaces
(Business and Enterprise): one space per product with `features/`, `domain/`, `flows/`, `architecture/`,
`generated/graph/REPO_MAP.md` and the contracts, shared with designers. Keep the Confluence publish
(`translate-for-publish`) as the fallback reading surface. Before the first demo, have one designer ask five real
questions on github.com and keep the transcript; a thin answer is almost always a missing description, alias or badge.

**17.4 Headless runs and cost.** A headless agent run is for CI and acceptance tests, not everyday work: about a
minute and 7 to 8 premium requests per analyst run. Everyday use is the IDE (section 19) or the CLI interactively,
where the user approves tool calls and the pack is reused across questions. Budget premium requests per agent per
week and show them in the coverage report.

**17.5 Links.** Specs link with root-relative paths (`/features/<ctx>/<ID>.md`). GitHub resolves them against the
repository root, so they are clickable only when the docs repo is its own repository. Never nest it in a monorepo.
`file:line` references and `#/paths/...` anchors are search keys for agents, not links; leave them as code.

**17.6 Where the skill references live.** The subtask mapping used by the analyst lives under the `code-graph` skill;
the model looked for it under `jira-work-items` and gave up. A one-line pointer file now sits in
`.github/skills/jira-work-items/references/subtask-mapping.md`. Rule: every reference a skill names is either in that
skill's `references/` folder or has a pointer there.

**17.7 Parameters and datasets, adoption steps.** Two catalogues came out of the question "how does an admin value
reach a calculation on the screen". Both are generated in the backend and collected like every other map:
- `parameters.md`: keep the parameter keys in one enum and the defaults in the migrations; the generator reads both.
  Every calculation that reads a key fills its `## Parameters` table with the key exactly as in the catalogue; the
  admin spec maps each key to the document that owns its meaning (`features/admin/ADM-001.md` is the model).
  `validate-frontmatter.py` fails on a key the catalogue lacks and on a catalogue key no document explains, so
  expect red CI until the mapping is complete. The rule in one sentence: the calculation owns the meaning, the admin
  spec owns scope, versioning and validation, the key string is the join.
- `datasets.md`: add the five header lines (`-- dataset:`, `-- purpose:`, `-- tables:`, `-- depends:`,
  `-- synthetic:`) to every existing seed and integration-fixture SQL file; the generator counts inserted rows per
  table, finds who loads the dataset and takes the first row of each table as a sample, values only when the header
  says `synthetic: yes`. The pack lists the datasets that touch a spec's tables; analysts and test designers write
  `Given dataset "<name>" is loaded` and describe rows only for values a scenario asserts on. Loaders that are not
  SQL (CSV, DbUnit XML) need one more reader in `gen-datasets.py`. Check what your seeds contain before the first
  run: if they hold production or UAT extracts, mark them `synthetic: no` so no value is ever copied.

**17.8 API design rules.** Reserved: `.github/skills/api-design/` for your enterprise API conventions and a Spectral
ruleset under `contracts/`, linted by `docs-quality.yml` for both `generated/openapi/` and `contracts/proposed/`.
Until it exists, proposals are reviewed by a human against the written conventions.

---

## 18. Human-owned documents an agent may draft

Several documents are owned by humans because they encode decisions, not code: the context map, the mapping file,
the glossary seed, the architecture pages, ADRs, conventions. Nothing stops you from asking an agent for the first
draft. The rule that keeps this safe is the same as for specs: the draft carries `status: draft` and
`generated: { by: copilot/<agent>, at }`, a human edits and adds `verified`, and the validators treat it as
unverified until then. Point the model at the reference copy in this investigation repository and at the evidence
it may use; forbid invention explicitly.

| Document | Reference in this repository | Give the model | Human confirms |
|---|---|---|---|
| `contexts.yml` (bounded contexts, class prefixes, FE features) | `docs-repo/contexts.yml` | `generated/be/codebase-map.md`, `generated/fe/codebase-map.md`, the team's own context names | the list is complete and the prefixes do not overlap |
| `docs-map.yml` (code paths to spec IDs) | `docs-repo/docs-map.yml` | `contexts.yml`, `generated/be/components.md`, `generated/fe/codebase-map.md` | every path pattern matches at least one file; `map-paths.py` agrees |
| `domain/context-map.md` | `docs-repo/domain/context-map.md` | `contexts.yml`, `generated/graph/REPO_MAP.md` (cross-community edges), `generated/be/events.md` | the relationships are the real ones; direction of each dependency |
| `domain/glossary.md` seed | `docs-repo/domain/glossary.md` | `generated/be/db-schema.md`, enum files named in `components.md`, the Confluence inventory | definitions; aliases in the source language |
| `architecture/overview.md`, `integrations.md` | `docs-repo/architecture/overview.md`, `integrations.md` | `generated/be/codebase-map.md`, `api-index.md`, `events.md`, `generated/openapi/external/*.yaml` | boundaries, ownership, anything the maps cannot show (hosting, auth) |
| `architecture/adr/*.md` | `docs-repo/architecture/adr/template.md`, `0002-openapi-first-contracts.md` | the decision as you would say it in one paragraph, plus the alternatives considered | the decision itself; an ADR is never generated from code |
| `flows/*.md` | `docs-repo/flows/client-presentation.md` | the pack of each spec involved, `generated/graph/<community>.md` | steps and invariants; participants |
| `features/conventions.md`, `contracts/conventions.md` | the files of the same name | your existing team rules (naming, ID scheme, review) | they match how the team works, not how the model thinks it should |
| `confluence-import/README.md` inventory | `docs-repo/confluence-import/README.md` | the export folder listing | which pages are in scope and who owns them |
| `test-design/README.md` step vocabulary | `docs-repo/test-design/README.md` | the step definitions of the tests repository | one meaning per step; no synonyms |
| `work-items/_schema.yml` | `docs-repo/work-items/_schema.yml` | your Jira field names and story template | field names match Jira |
| `AGENTS.md`, `.github/copilot-instructions.md`, agent files | `docs-repo/AGENTS.md`, `docs-repo/.github/**` | the rendered versions here, your product name and context list | every hard rule; the never-open list; the safety section |
| `migration/` owners and dates | `docs-repo/migration/all.md` (generated board) | the board, the team list | owner per context and the Run 4 dates |

How to ask, in the CLI or the IDE, from the docs repo root:

```text
Draft domain/context-map.md for <product>. Evidence: contexts.yml, generated/graph/REPO_MAP.md, generated/be/events.md.
Follow the structure of this file exactly: <paste or attach docs-repo/domain/context-map.md from the investigation repo>.
Frontmatter status: draft, generated.by: copilot/architect. Where the evidence does not show a relationship, write
"unknown" and add an open question; do not infer from names. Finish with python3 scripts/okf-validate.py --strict.
```

Two documents must not be drafted by an agent: the safety section of `AGENTS.md` (section 0) and the content
exclusion list. Write those yourself.

---

## 19. Several repositories in IntelliJ with the Copilot CLI agent

The analyst's exception (17.2), the spec-writer's `file:line` reads and `doc-sync` all assume the code repositories are
reachable from the docs repo as `../backend` and `../frontend`. Set it up once per machine.

1. **Layout.** Clone side by side: `C:/work/<product>-docs`, `C:/work/<product>-backend`,
   `C:/work/<product>-frontend`. The scripts use relative paths from the docs repo root; the collector takes the
   paths as parameters, so other layouts work for the collector but not for the agents' conventions.
2. **IntelliJ project.** Open the docs repo as the project. Attach the code repositories so they are visible in the
   same window: `File > Open`, choose the backend folder, answer **Attach** in the dialog (not New Window); repeat
   for the frontend. They appear as separate modules in the Project view and in Copilot's workspace. Do the same in
   reverse for developers: code repo as project, docs repo attached.
3. **Copilot plugin, CLI agent.** In the Copilot tool window select the CLI agent (preview; it must be enabled by a
   Copilot Business or Enterprise administrator under editor preview features). Choose **workspace isolation** so the
   agent writes into the checkout you see, not into a separate worktree; the hooks in `.github/hooks` then run on the
   files you commit.
4. **Directory access.** The CLI trusts the project folder. For the attached repositories either answer the trust
   prompt when the agent first reaches `../backend`, or grant access up front in the chat with the slash commands:

   ```text
   /add-dir ../backend
   /add-dir ../frontend
   /list-dirs
   ```

   `/add-dir` also loads that repository's `.github/skills` and `.github/agents`, which is what you want: the
   backend's `code-reader` and `docs-tagger` agents become available from the docs repo session. The equivalent for a
   terminal or headless run is `--add-dir ../backend --add-dir ../frontend`; `/cwd` changes the working directory
   inside a session when a prompt must run from a code repo root.
5. **Verify** with one question that needs both sides: "which backend class implements spec <ID> and which frontend
   hook calls its endpoint" should be answered from `generated/graph/<community>.md` without a permission prompt;
   then "show me the file:line the pack names for open question 1" should open the range in the attached repo.
6. **What to expect to change.** The CLI agent in JetBrains is a public preview; the plugin manages the working
   directory and the isolation mode, and the plugin release notes are the place to confirm whether `/add-dir` and
   trust prompts behave as in the terminal. Keep step 4 as the fallback: it is documented for the CLI itself and the
   plugin runs the same CLI.

Sources: GitHub changelog, "Introducing Copilot CLI agent and unified sessions view in GitHub Copilot for JetBrains
IDEs" (2026-05-13); GitHub Docs, Copilot CLI command reference (`/add-dir`, `/list-dirs`, `/cwd`, `--add-dir`).

---

## 20. Workstations: Windows and macOS

The scripts are Python 3.11+ using only the standard library; they run unchanged on Windows, macOS and Linux, and the
CI examples already run on `ubuntu-latest`. What differs between a Windows and a Mac workstation, and what the
repository does about it:

| Topic | Windows | macOS | Rule in the repository |
|---|---|---|---|
| Interpreter | `python` (python.org installer or `winget install Python.Python.3.12`) | `python3` (`brew install python`, or the Xcode command-line tools) | every script starts with `#!/usr/bin/env python3` and needs no package; hook files carry a `python` command for PowerShell and a `python3` command for bash; CI calls `python3` |
| Paths | `\` or `/` | `/` only | scripts build paths with `os.path` and print them with `/`; documentation examples use `/` |
| Sort order | - | - | every sorted table and index uses one rule, case-insensitive alphabetical with the exact string as tie-break, implemented in the scripts themselves (`sort_key`); no locale or ICU is involved, so the output is identical on every machine |
| Line endings | checkout CRLF with `core.autocrlf=true` | checkout LF | `.gitattributes` with `* text=auto` in every repository; the scripts read files without translating line endings, write LF, and the `--check` comparisons ignore CR |
| File-name case | NTFS case-insensitive | APFS case-insensitive by default | Linux CI is case-sensitive: links and `code_refs` must match the file name exactly; the validators report the mismatch before CI does |
| Containers | Docker Desktop | Docker Desktop | the seed runner uses `docker compose exec`, no local `psql` needed |
| Toolchain | JDK 21, Node, Maven paths as in `LOCAL-TESTING.md` | the same via Homebrew; Maven path differs | nothing in the docs repo depends on the toolchain; only the code repos do |
| IDE | IntelliJ with the Copilot plugin | the same | section 19 applies unchanged |

First day on a Mac: clone the three repositories side by side, open a terminal in the docs repo and run the full chain
with `--check` against files generated on Windows:

```bash
python3 scripts/okf-validate.py --strict; python3 scripts/validate-frontmatter.py; python3 scripts/gen-graph.py --check; python3 scripts/build-index.py --check
python3 ../backend/scripts/docs/gen-all.py --root ../backend --check; python3 ../frontend/scripts/docs/gen-all.py --root ../frontend --check
```

All green means the two platforms generate byte-identical maps. A `STALE` here is a platform difference, not a content
change: open the two files, and the cause is a line ending or a path separator (the sort order cannot differ any more).
