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

Contents: Pilot track (read first) · 0 Ground rules and safety · 1 Decisions before you start · 2 Docs repository skeleton · 3 AGENTS.md and the
Copilot files · 4 Contexts and the mapping file · 5 Contracts you already have · 6 Code repositories · 7 Collector ·
8 Graph and indexes · 9 Confluence import · 10 Specs, run by run · 11 Calculations and flows · 12 The analyst ·
13 Maintenance · 14 Scripts catalogue · 15 Agents catalogue · 16 Plan: documentation first, analyst second · 17 Lessons from the first trial · 18 Human-owned documents an agent may draft · 19 Several repositories in IntelliJ · 20 Workstations: Windows and macOS

---

## Pilot track: the minimum for the first spec (read first)

The playbook describes the full system. For the first spec of one pilot context you need five pieces; everything
else is added when its absence hurts. Each section from 2 to 13 is marked **Pilot** or **Later** under its heading.

| # | Piece | Section | Done when |
|---|---|---|---|
| 1 | Docs repo skeleton, `AGENTS.md`, three agents (`analyst`, `spec-writer`, `calc-auditor`), the instructions and skills; prompt files are optional in the CLI (section 1, item 6) | 2, 3 | validators green on the empty repo; `/agent` lists the three agents |
| 2 | Contracts copied by hand into `generated/openapi/` (own API, external services) with a line each in `generated/manifest.yml` | 5 | `okf-validate.py --strict` accepts them; `architecture/integrations.md` cites them |
| 3 | Backend and frontend generators run once by hand in the pilot repositories (`docs-gen.json` through `/adapt-docs-scripts`, then `gen-all.py`), `docs/_generated/` committed; the database documentation folder (`docs/db`, from your tool or from the kit) next to it | 6, items 1 and 9 | every endpoint, topic, table, job, route and hook of the pilot context appears once; every table page carries its comment |
| 4 | `contexts.yml`, a `docs-map.yml` with one row per context, the maps copied into `generated/be` and `generated/fe` (by hand or by one local collector run; by hand, copy the backend `scripts/docs/docs-gen.json` to `generated/be/docs-gen.json` too, the graph reads the layer names from it), then `gen-graph.py` and `build-index.py` | 4, 7 (local run only), 8 | `REPO_MAP.md` shows the pilot community; its spec is listed as "code only" |
| 5 | One context pack per task and Runs 1 to 4 for the pilot spec, with the calculations it links | 10, 11 | a spec with `file:line` citations, reviewed by its owner |

Deferred until the trigger named:

- Hooks, CI workflows, the freshness gate and the migration board (section 6 items 5 to 7, section 7 in CI,
  section 13): when a second person writes specs, or the first time a map goes stale unnoticed.
- `confluence-migrator` and section 9: when the first exported space arrives, or earlier when another team hands you a
  generated knowledge base (next paragraph).
- `doc-sync`: with the first collector pull request. `impact-analyst`, `architect`, `test-designer`,
  `migration-lead`: with the first task of that kind.
- `@docs` tags and `tag-docs` (section 6, item 8): when a calculation without a spec appears on the board.
- Parameter and dataset headers (17.7): when `gen-parameters.py` and `gen-datasets.py` leave `skip_generators`.
  The parameter generator expects one key enum and one key-value table. A backend whose administrator edits values
  in several typed tables (one table per parameter family, each with its own columns) keeps `gen-parameters.py` in
  `skip_generators`: without `generated/be/parameters.md` the parameter check of `validate-frontmatter.py` is
  skipped and nothing else reads the file. The tables are documented anyway: a `COMMENT ON` per table and column in
  the migrations (the table pages and the graph notes come from them), the admin spec's Data section listing the
  columns each screen writes with the rule that governs the write, and every calculation naming the value it reads
  as `table.column` in its Inputs table (its `## Parameters` section says "none"). Name the context `admin` even
  so: the validator exempts exactly that name from the parameter check, and the catalogue for typed tables is a
  later kit addition that will need it. The admin spec's title can still read "Administration".
- Confluence publish, the reader test of 17.3 and a human-facing rendering of the repository: after the first
  analytics tasks.
- The analyst agent (section 12) and the gate of section 16 stay as written; the pilot track is week 1 of phase 1,
  not a shortcut around the gate.

**A knowledge base another team already generated** (a tester's "RAG knowledge base" for the frontend and backend,
an onboarding page written by an agent from the code) is an imported legacy page, not a source of truth: it is a
snapshot of one day without `file:line`, and nothing regenerates it. Put it under `confluence-import/<SPACE>/` as
`<name>.md` (for example `confluence-import/<SPACE>/rag.md`) with the header block of that folder's README (`source`,
`last_modified`, `author`, `status: imported`) and a row in its "Current pages" table - **never under
`confluence-import/raw-html/`**, which holds only the Confluence HTML export: the importer reads only `.html` files
there and agents never open that folder, so a Markdown file placed there is never seen. Then let `confluence-migrator` take it
section by section (`/agent confluence-migrator`, then "Migrate section <n> of confluence-import/<SPACE>/<file>.md").
Migrate only what the generators cannot produce: the step-by-step user flows (one `flows/` document), business rules
stated in prose ("starting a meeting reuses the matching active session"), the purposes of broadcast message types
(`channels:` of the flow), enumerations with business meaning and the glossary (into `domain/`), architectural notes
("technical routes are defined outside the OpenAPI file"), known limitations (into `work-items/` or the open questions
of the affected spec) and the page-to-test-file table (into `test-design/`). The tech stack, folder schemas, route map,
endpoint, entity, enumeration, job and integration tables are **cross-checks only**: diff them against
`generated/fe/routes.md`, `generated/be/api-index.md`, `generated/be/jobs.md` and `architecture/integrations.md`; a
mismatch is a generator gap to fix now or a stale line in the import. Test-framework internals (locator and keyword
conventions) stay in the tests repository. Once the flow, the glossary rows and the first spec exist, the other
team's agent reads the docs repository or a context pack instead, and the import moves to `_done/`.

The pilot track is an afternoon after section 3 once `docs-gen.json` is right. The two places where it stalls are
the generator regexes against your conventions (`/adapt-docs-scripts`, section 6) and the bounded-context cut in
`contexts.yml` (section 4), which no tool decides for you.

---

## 0. Ground rules and safety

Read this section first; it is what you will be asked about.

**What agents may and may not do** (enforced by files, hooks and CI, not by goodwill):

| Rule | Where it is enforced |
|---|---|
| Agents never edit `generated/**` or any `index.md` | `scripts/hooks/guard-generated.py` as a `preToolUse` hook; CI `gen-graph.py --check`, `build-index.py --check` |
| Agents never write `verified.by: human:*` | `AGENTS.md` hard rule; `okf-validate.py` rejects a `verified` whose actor is not `human:`; review of every PR |
| Every agent-written document is `status: draft` with `generated: { by: copilot/<agent>, at }` | templates, `validate-frontmatter.py`, index badges |
| The analyst reads at most five code ranges per task, located through the generated maps, and takes one free reading pass over both repositories only for a question that still blocks its answer; other agents open at most the files their procedure names | agent files (`.github/agents/*.agent.md`), context pack footer rule |
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
named source range only when a procedure says so; the analyst at most five ranges per task, plus a free reading pass for a
question that still blocks its answer. That is less exposure than a developer's
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
   The first context in scope is the pilot: one backend entry point, one frontend page, at least one
   calculation. Everything below is done for it first, then for the other contexts in scope.
3. **IDs.** Spec IDs `<CTX>-<NNN>` (for example `P1-001`), rules `BR-<ID>-<n>`, calculations `snake_case`. If the
   enterprise already has feature IDs, keep them; the scripts only need the pattern in `features/conventions.md`.
4. **Context list.** The business areas and, per area, the backend class-name prefixes or packages, the frontend
   page folders, the spec prefix. This becomes `contexts.yml` (section 4).
5. **Roles.** Documentation maintainer (runs the agents, reviews diffs), context owners (Run 4 verification), one
   analyst to evaluate the output, a platform engineer for CI and tokens.
6. **Copilot client.** Copilot CLI for every agent run (hooks and skills work there; the JetBrains plugin has them in
   preview), IntelliJ for reading and reviewing. The CLI loads `AGENTS.md`, `.github/agents/*.agent.md` (`/agent`)
   and `.github/skills/`; it does **not** load `.github/prompts/*.prompt.md` as slash commands (github/copilot-cli
   issue 618, still a feature request in 2026). Prompt files are slash commands in the JetBrains plugin and VS Code
   only. Wherever this playbook writes `/name`, in the CLI type
   `Follow .github/prompts/<name>.prompt.md with <input> = <value>, ...`, after selecting the agent named in the
   prompt's `agent:` line with `/agent` when it is not the default one. Verify once that hooks fire in `-p` mode.
7. **Language.** English in files; glossary aliases keep the source-language terms findable.

---

## 2. Docs repository skeleton (half a day)

**Pilot.**

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

**Pilot** (the agents `analyst`, `spec-writer`, `calc-auditor`, the instructions and skills; hooks and workflows later).

`AGENTS.md` is the contract between people and agents. Every Copilot surface reads it first. Keep it under 80 lines.
Write these sections, in this order, adapted from `docs-repo/AGENTS.md`:

1. **What this repository is.** One paragraph: single source of truth for functional and technical documentation of
   `<product>`; Confluence is a publish target; the code repositories are inputs; Jira and the tests repository are
   outputs. One OKF v0.2 bundle: every document has frontmatter with `type`, every folder a generated `index.md`.
2. **Work task-scoped: build the context pack first.** The command `python3 scripts/context-pack.py --task <ID|name|text>`,
   what the pack contains, and the sentence "Read the pack first. A change request takes the full pack top to bottom;
   a question takes the narrowest subject with `--budget 200` and reads the Subject and the section it names. After
   it the analyst opens or searches the documentation folders freely; other agents open the documentation files
   their procedure names; code only at the `file:line` the pack names."
3. **Read order when there is no pack**, cheapest first: `index.md` of the area, the spec, the calculation, `contexts.yml`
   and `generated/graph/REPO_MAP.md`, the maps under `generated/be|fe`, the contracts under `generated/openapi|asyncapi`,
   and only then source code in the sibling checkouts, smallest range, located through the graph or `docs-tags.md`.
4. **Hard rules.** Never hand-edit `generated/**`. Every concept has frontmatter with `type`; folders use `index.md`,
   never `README.md`. Provenance: `generated: { by: copilot/<agent>, at }` on anything an agent writes, `sources[]`
   cited with `[^id]`, never `verified.by: human:*`, `status: draft` until a person verifies. Traceability IDs
   mandatory. Terminology from the glossary; English only. Synthetic data only. Outputs in files; chat under 15 lines;
   specs under 300 lines; diagrams under 25 nodes.
5. **Commands table and Checks.** Context pack, validators, indexes, graph and graph query, changed paths to
   specs, analytics, collector, migration board; then the Checks: an agent runs the validators once, after the
   last edit of a task, for what it changed (`okf-validate.py --strict`), never after each edit, and a
   task that changed no file runs none. Copy both from `docs-repo/AGENTS.md`.
6. **Agents, prompts, skills.** The list of agent names with one line each, the lifecycle sentence (skeleton,
   legacy merge, calculation audit, owner decision), and the pointer to `migration-status.py`.

Then copy `.github/` as it is and adapt only names:

| Folder | What to keep | What to adapt |
|---|---|---|
| `.github/copilot-instructions.md` | the pointer to `AGENTS.md`, the never-open list | product name |
| `.github/instructions/*.instructions.md` | all seven (features, calculations, contracts, confluence-import, generated, test-design, work-items); they are short path-scoped rules | nothing |
| `.github/agents/*.agent.md` | for the pilot three agents are enough: `analyst`, `spec-writer`, `calc-auditor`; add `confluence-migrator` when the first pages arrive, `doc-sync` when the collector runs, `migration-lead`, `test-designer`, `architect`, `impact-analyst` later | the domain sentence in each description |
| `.github/prompts/*.prompt.md` | all; they are the slash commands | nothing |
| `.github/skills/*/SKILL.md` | all; procedures shared by agents | `write-feature-spec/references/source-priority.md` if your source layout differs |
| `.github/hooks/docs-quality.json` | `preToolUse` guard and `agentStop` validators | nothing |
| `.github/workflows/docs-quality.yml` | markdownlint, validators, index and graph checks, link check | runner OS, Python availability for the reference OKF checker (optional) |
| `.github/workflows/copilot-setup-steps.yml` | only if you use the cloud coding agent | - |

**Acceptance:** in the Copilot CLI, opened in the docs repo, `/agent` lists `analyst`, and
`python3 scripts/context-pack.py --task <any text> --print` runs; in the JetBrains plugin or VS Code `/context-pack`
and `/spec-skeleton-from-graph` appear as commands (not in the CLI, section 1 item 6).

**With an agent.** One file of this step is written from your code rather than copied: the code rows of
`.github/skills/write-feature-spec/references/source-priority.md`. Steps: 1. open the Copilot CLI in the docs repo with
`--add-dir` for both code checkouts (section 19); 2. `/source-priority-from-code <product>` (agent `architect`, no scripts);
3. check that every path pattern in the new rows matches a file you know, that the manager row comes before the unit-test
row, and that the rules of thumb stay at seven or fewer; 4. commit. Rerun it whenever a repository moves folders.

---

## 4. Contexts and the mapping file (one hour with a developer who knows the code)

**Pilot.**

**`contexts.yml`** turns code into bounded contexts without moving code. One entry per business area:

```yaml
contexts:
  billing:
    spec: BIL                          # spec prefix -> features/billing/BIL-001.md
    fe: [BillingPage, InvoicePage]     # page folders under src/pages/ (wildcards allowed: "*BillingPage"); [] when the context has no page
    be: [Billing, Invoice, Tariff]     # backend class-name prefixes (longest prefix wins; "*Tariff" = wildcard over the whole name); unmatched classes -> shared
```

If your backend is organised by package rather than by layer, prefixes still work (most classes are named after
their area); if not, extend `Context-Of` in `gen-graph.py` and `migration-status.py` to match on the package path.
Iterate until `generated/graph/REPO_MAP.md` shows a `shared` community that holds only true helpers (section 8).
Context names are free (lowercase, digits, hyphens; `data-imports` is as good as `imports`), chosen once with the
prefix, with three exceptions: `shared` and `fe-shared` are the communities of unmatched classes and pages, and the
administration context is `admin`, the one name `validate-frontmatter.py` exempts from the parameter check (pilot
track, deferred list). The word people see in titles and the catalogue is free text.

**`docs-map.yml`** is the manual mapping the other analyses recommended: code path globs to the documents they affect.
Write one row per context now, even before any spec exists (`specs: []` is allowed and shows as backlog):

```yaml
mappings:
  - paths: ["be/<module>/src/main/kotlin/<root>/**/Billing*.kt", "fe/src/pages/BillingPage/**", "fe/src/pages/InvoicePage/**", "fe/src/types/billing.ts"]
    specs: ["features/billing/BIL-001.md"]
  - paths: ["be/<module>/src/main/kotlin/<root>/utils/**"]
    specs: ["domain/calculations/**"]
ignore: ["**/*Test.kt", "**/src/test/**", "**/*.test.ts*", "fe/src/services/openapi/**"]
```

**With an agent.** Both files are drafted from the source, then confirmed by the developer:
1. `/context-map-from-code <product>` (agent `architect`, reads both checkouts, no scripts) writes `domain/context-map.md`
   and proposes `contexts.yml` in chat: one line per context with `spec`, the `fe` list of page folders and the `be` prefixes.
2. Review together: prefixes must not overlap ambiguously (longest match wins), every page folder named must exist,
   `fe: []` where a context has no page of its own (its pieces sit under the shared folder and are reached by `@docs`
   tags and `docs-map.yml`). Paste the result into `contexts.yml`.
3. `/docs-map-from-contexts` (agent `architect`) drafts the `mappings` rows from `contexts.yml` and the file trees: one
   row per context with a glob per class prefix, per page folder, the types file and the shared pieces the page imports,
   then the cross-cutting rows (calculators, messaging, contracts); every glob verified against at least one file.
4. Check: `python3 scripts/map-paths.py <one real path per context>`, each path prefixed `be/` or `fe/` and relative to
   its repository root (for example the context's manager file and its page component), prints the spec of that context,
   or `BACKLOG` for a context whose row still has `specs: []`; `UNMAPPED` means no row matched the path, so a glob is
   wrong. Commit both files. The graph (section 8) is where wrong prefixes become visible.

It is read by `map-paths.py` (changed paths to specs), `check-freshness.py` (CI gate), the collector's PR body, and
`gen-graph.py`, which turns every row into `implemented-by` edges. That last point means you do not have to put
`@docs` tags into application source before documentation can begin; add tags later on managers and calculators,
where precision matters.

---

## 5. Contracts you already have (one hour)

**Pilot** (contracts copied by hand; the collector later).

You already keep the OpenAPI documents in the docs repository. Put them where the scripts and agents look:

| Contract | Location in the docs repo | Who owns the file |
|---|---|---|
| The API the frontend calls | `generated/openapi/backend.yaml` | the collector (copied from the backend repo) |
| APIs of the other services your backend calls | `generated/openapi/external/<service>.yaml` (or `.json`) | the collector if they live in the backend repo (`src/main/resources/api/<service>/`, yaml or json; folder from the backend `docs-gen.json`), otherwise hand-placed with a note in `generated/manifest.yml` |
| Kafka: AsyncAPI document | `generated/asyncapi/backend.yaml` | the collector |
| Kafka: payload schemas (Avro `.avsc`, JSON Schema `.json`) | `generated/asyncapi/schemas/<path relative to the schema folder>` (Harbor: `avro/*.avsc`, `json_<service>/*.json`) | the collector, from the folders in `kafka.schema_dirs` of the backend `docs-gen.json`; `generated/be/events.md` names the file of each topic's payload (re-pointed to the copy) and tables its fields |
| Database documentation (`schema.json`, one page per table with the column comments and relations, ER diagram, index) | `generated/be/db/` | the collector, from the backend folder named by `db_docs.dir` (default `docs/db`); written there either by your database documentation tool (SchemaSpy with its converter script under `docs/db/scripts/`, tbls: set `db_docs.generate: false`; the collector copies pages, `schema.json` and diagrams, never the scripts) or by the kit's `gen-db-docs.py` from the migrations and their `COMMENT ON TABLE\|COLUMN` statements. Keep the comments in the migrations: they are the data dictionary agents cite |
| Kafka: Avro or JSON schemas only (a `kafka-client` module with `avro/*.avsc` and `json_<service>/*.json`, no AsyncAPI document) | the schema files go to `generated/asyncapi/schemas/` as in the row above; `generated/be/events.md` lists every topic with producer, consumer, payload type and the path of its schema file, and the fields of every schema (`kafka.schema_dirs` in the backend `docs-gen.json`); set `asyncapi: ""` in `docs-gen.json`, the collector then copies no AsyncAPI document and the agent texts fall back to `events.md` and the schema copies | `events.md` by the generator, the schema copies by the collector; add an AsyncAPI document later only if you want the collector to publish one |

Rules: keep the complete document and the files it references; an external `$ref` that does not resolve inside
`generated/` is rejected by the collector. Record the version and retrieval time of a provider specification in the
manifest when there is no source commit. The frontend's generated client and the backend's generated interfaces are
never read by agents; the contract is the single thing to read (`api.instructions.md`, `services.instructions.md`).

**Contracts designed before code.** Your analysts design APIs during analysis, so a contract may exist in the docs
repo before any code. That is a proposal, not evidence, and it has its own folder: `contracts/proposed/<SPEC-ID>.openapi.yaml`
(or `.asyncapi.yaml`), started from `_template.openapi.yaml`, with `x-spec`, `x-status: proposed` and `x-generated-by`
in the `info` block. The spec's API table links to it and says **proposed**; stories cite its `operationId`s and carry
`needs-contract`. The handover is a copy into the code repository that will generate code from it; the collector then
brings the implemented version back under `generated/`, and `doc-sync` switches the spec's links and closes the
proposal. Nothing is ever copied from `contracts/proposed/` into `generated/` by hand. Rules: `contracts/conventions.md`,
`.github/instructions/contracts.instructions.md`; CI lints both folders with the same linters.

**With an agent.** None for placing the contracts; this is platform work and the collector's validation is the test.
Once they are in place, `/integrations-from-contracts <product>` (agent `architect`; in the CLI "Follow
.github/prompts/integrations-from-contracts.prompt.md with product = <name>") rewrites the tables of
`architecture/integrations.md` (Kafka, outbound REST per external contract, inbound REST per tag, jobs) and the C4
context diagram plus the "Contexts at a glance" table of `architecture/overview.md` from `generated/`; the prose of
both pages stays yours, and a contract no client class references is listed as held but not called. While your
overview still carries the Harbor text, `scope = overview-draft` rewrites the whole page as `status: draft` from the
codebase maps, the contracts and the graph, leaving `> ❓ TODO (human)` lines for hosting, authentication and the
other rules the evidence cannot show (section 18); you edit and add `verified`.
Two agent uses come later: `@architect` starts a proposed contract from `contracts/_template.openapi.yaml` when a spec
needs an API before code exists (section 17.8), and `doc-sync` switches a spec from the proposal to the implemented
contract once the collector brings it in (section 13).

The API index generator (`gen-api-index.py`) is contract-first: it lists every operation of the OpenAPI document
and finds the handler method by `operationId` (`rest.handler_match: operationId`, controllers implementing the generated
interfaces with `override fun`). If your controllers are hand-written, set `rest.handler_match: mapping` and the handler
is matched by verb and path of its `@GetMapping`; routes outside the contract are listed as `(no contract)` either way.

---

## 6. Code repositories (one afternoon per repository)

**Pilot:** items 1 and 9 for the pilot repositories, items 2 to 4 with them when cheap; items 5 to 8 later.

**Shortest path (pilot).** Yes, the whole kit flavour can be copied at once; the generators are configuration-driven
and nothing in them is Harbor-specific. Run `python3 code-repo-kit/apply-kit.py --flavour be --target <backend> --pilot`
with one `--replace OLD=NEW` per Harbor name (`harbor-core`, `com/acme/harbor`, `com.acme.harbor`, `openapi_harbor.yaml`,
`harbor-backend`, `harbor-frontend`, `harbor-docs`, `Harbor`, `harbor`; the script applies the longest first), the same
for `--flavour fe`. `--pilot` leaves out the hooks and workflows (items 5 and 6), `--replace` rewrites the names in
the copied `.md`, `.yml`, `.json` and `.kt` files, never in the scripts, and the script ends with the list of copied
text files that still mention Harbor: those sentences (topic names, class names, module purposes in `AGENTS.md`,
the instructions and the agents) you reword by hand or with the agent of item 1 below. Then fill
`scripts/docs/docs-gen.json` (the values you already know are in the change list, section 4), run `gen-all.py`, and
read the tables. The ordered list below is the same work, file by file, for a rollout with review per file.

**Pilot checklist, by hand (no workflows, no hooks).** What to copy from `code-repo-kit/` and where, then what to
do, in order. "Reword" means: open the file, replace the Harbor names (module, package, contract file, topic and
class names) by yours, delete sentences about things you do not have.

Backend repository:

| From `code-repo-kit/be/` | To `<backend>/` | Then |
|---|---|---|
| `scripts/docs/*.py`, `scripts/docs/README.md` | `scripts/docs/` | nothing to edit; the scripts read the config below |
| `scripts/docs/docs-gen.json` | `scripts/docs/docs-gen.json` | fill every key for your repository (`README.md` next to it explains each; your known values: change list sections 4 and 7.3); when your layer folders are not Harbor's, set `layers`, `graph_layers`, `graph_exclude_layers` to your names and rename the folders in the `applyTo` lines of the instruction files; when your SQL views live outside the migrations folder, list that folder in `migrations.view_dirs` (`["/db/statistical-views/"]`, change list section 9) |
| `AGENTS.md` | `AGENTS.md` | reword; keep it under 60 lines; the read order names your entry layer (`service/<Ctx>Service.kt`) |
| `.github/copilot-instructions.md` | `.github/copilot-instructions.md` | reword the never-open list (your generated client folders, build output) |
| `.github/instructions/*.instructions.md` | `.github/instructions/` | keep `api`, `calculations`, `kafka`, `migrations`, `tests`, `layers`; reword paths; delete a file whose stack you do not have |
| `.github/agents/*.agent.md` | `.github/agents/` | `code-reader`, `docs-tagger`, `impact-analyst`: reword the file names they cite |
| `.github/prompts/*.prompt.md` | `.github/prompts/` | `adapt-docs-scripts`, `tag-docs`, `explain-module`, `find-spec-code`, `add-endpoint`: reword; the CLI reaches them with "Follow .github/prompts/<name>.prompt.md ..." |
| `../shared/check-file-size.py` | `scripts/check-file-size.py` | optional in the pilot |
| not copied | | `.github/hooks/`, `.github/workflows/`, `../ci/docs-maps.yml` (items 5 and 6, later); `templates/GraphExportTest.kt` (optional precise graph, later); `scripts/db/` (Harbor's seed loader) |

Frontend repository:

| From `code-repo-kit/fe/` | To `<frontend>/` | Then |
|---|---|---|
| `scripts/docs/*.py`, `scripts/docs/README.md` | `scripts/docs/` | nothing to edit |
| `scripts/docs/docs-gen.json` | `scripts/docs/docs-gen.json` | fill: `pages_dir`, `not_pages`, `page_entry`, `hook_dirs`, `components_dir`, `shared_dir`, `app_dirs`, `route_files` (your `src/routing`), `route_constants`, `types`, `exclude_paths` (the generated client), `test_pattern`, `api_call_pattern`, `generated_client.dirs` (the same generated client folders: hooks calling Orval functions then get their `METHOD /path` in the `API calls` column) |
| `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/pages|services.instructions.md`, `.github/agents/*`, `.github/prompts/*` | same paths | reword as for the backend |
| not copied | | `.github/hooks/`, `.github/workflows/`; `scripts/docs/gen-graph-fe.ts`, `tsconfig*.json`, `out/` (precise graph through the TypeScript compiler, later) |

Then, per repository:

1. `python3 scripts/docs/gen-all.py` (backend: with `db_docs.generate: false` it leaves your `docs/db` alone). Read every
   table under `docs/_generated/`: `codebase-map.md` (every layer with a role; business classes under `(root)` mean a
   wrong base package), `components.md` (your services, managers and calculators present, `Depends on` filled),
   `api-index.md` (no `_not implemented_` for an operation that exists), `events.md` (no `<expr>` topic, a schema path
   next to every payload), `jobs.md`, frontend `routes.md` (every page with a route and a purpose).
2. A wrong or missing row: paste the declaration the generator missed and the regex from the generator to the agent
   of item 2 of "With an agent" below, apply the smallest change, rerun. Or run `/adapt-docs-scripts` first (item 1
   below): it proposes the whole `docs-gen.json` with one evidence path per key and never runs anything.
3. Commit `scripts/`, `.github/`, `AGENTS.md` and `docs/_generated/` together (item 9).
4. Back in the docs repository: the collector or the hand copy of the maps (pilot piece 4), then `gen-graph.py` and
   `build-index.py`. `@docs` tags (`/tag-docs`, item 8) wait until a calculation without a spec shows on the board.

Copy the kit flavour into each repository. `code-repo-kit/apply-kit.py --flavour be --target <backend>` copies
everything at once; for the enterprise rollout copy selectively in this order and review each file:

1. **`scripts/docs/`** with `gen-all.py`, `_common.py` and the generators (section 14 lists each). Run
   `python3 scripts/docs/gen-all.py --root .` and read every table in `docs/_generated/`. Both flavours read the
   repository layout from `scripts/docs/docs-gen.json`: fill that file first, it is the whole adaptation.
   Two keys decide where agents start reading and are not about folder names: `entry_layer` is the layer of the one
   class per context the controller hands the request to (in Harbor the manager; in a controller -> service -> manager
   flow the service), and `calculation_layer` is the layer of the pure calculators with their unit tests (`utils` in
   Harbor and in most layered backends). Layers between the two (a manager holding the business logic the service
   delegates to) are ordinary rows of the source priority, read after the entry point and before the calculators. The
   read order in `AGENTS.md`, the source priority rows, the `@docs` candidates and the context map's entry-point
   column all follow these two values.
   Backend keys (`code-repo-kit/be/scripts/docs/README.md` lists every key): the Maven modules, the base package,
   the layer list with the sub-packages that count as layers of their own (`dao/model`, `dao/repository`,
   `dao/service`, `client/rest`, `api/technical`, ...; your folder names, which may differ from Harbor's: the keys
   of `layers` are what the maps print, `graph_layers` and `graph_exclude_layers` tell the docs repository's graph
   which of them are behaviour and which are data, and the `applyTo` globs of the instruction files name the same
   folders), the OpenAPI, AsyncAPI and external-contract paths, how
   controllers relate to the contract (`override fun <operationId>` on a generated interface, or hand-written
   `@GetMapping` routes matched by verb and path), the Kafka listener annotation and the property files that resolve
   `${...}` topic names, the migrations folder, the parameter-key enum and its table, the seed and fixture folders,
   and `db_docs` (the database documentation folder and whether the kit generates it or your database tool does).
   Frontend keys (`code-repo-kit/fe/scripts/docs/README.md`): pages folder, hook and component folder names, shared
   component library, routing files and route constants, type globs, generated client to exclude. Where your code
   still differs from the simulated one (a Liquibase changelog, a Quartz scheduler, a router that is neither object
   routes nor `<Route>`), adjust the regular expression in the generator; the tables carry `file:line`, so a wrong
   row is visible immediately. Target: every endpoint, topic, table, scheduled job, route and hook of the pilot
   context appears once.
2. **`AGENTS.md`** under 60 lines: purpose of the repo, read order (map, then the context's manager or page component, then
   one named range), the contracts and where they live, conventions, the commands. Adapt from `code-repo-kit/be/AGENTS.md`
   and `fe/AGENTS.md`.
3. **`.github/copilot-instructions.md`** with the never-open list (generated clients, build output, lock files).
4. **`.github/instructions/`**: backend `api`, `calculations`, `kafka`, `migrations`, `tests`, `layers`; frontend
   `services`, `pages`. Short path-scoped rules; keep the ones that match your stack.
5. **`.github/hooks/docs-maps.json`**: `agentStop` runs `gen-all.py --check`, so an agent cannot leave stale maps.
6. **`.github/workflows/docs-maps.yml`** from `code-repo-kit/ci/docs-maps.yml`: on pull requests, maps fresh and file
   size budget. Nothing on main; publication belongs to the docs repo (section 7). Start warn-only, make it blocking
   after two sprints.
7. **Content exclusion** in the repository settings from `code-repo-kit/shared/copilot-content-exclusion.yml`.
8. **`@docs` tags**, selectively: `@docs <SPEC-ID>` on the context's entry point (manager or orchestration service)
   and on the frontend page component (the JSDoc above `export function <Page>`), `@docs <calculation_name>` on every
   business calculator. Not on every class. The
   `docs-tagger` agent and `scripts/docs/tag-candidates.py` list candidates per context when you get there.
9. Commit `docs/_generated/` with the code. It is cheap, it gives the PR-time freshness check, and Copilot in the
   code repo reads the maps without running anything.

**With an agent** (Copilot in the code repository, after the kit files are copied):
1. `/adapt-docs-scripts` (prompt in both kit flavours, agent `agent`; give it the strongest reasoning model you have). The
   agent reads `scripts/docs/*` and the repository and answers **without running anything**: a security table per script
   (what it reads, writes, starts, downloads; imports outside the standard library), the `docs-gen.json` with one
   evidence path per key, the smallest regex diff for what the config cannot express, and what every table must show
   for this repository. A person checks the security table against the scripts (the only process start is `gen-all.py`
   calling its sibling generators; writes go under `docs/_generated` or `--out`, plus `db_docs.dir` when the kit generates it, where `gen-db-docs.py` removes pages of dropped tables file by file; `--check` works in a system temp folder it creates and removes), pastes the config, applies the
   diffs it agrees with, then runs `gen-all.py` and compares `codebase-map.md` (every layer with a role; business classes
   under `(root)` mean a wrong base package), `api-index.md` (no `_not implemented_` row for an operation that exists;
   hand-written routes tagged `(no contract)`), `events.md` (no `<expr>` topic, a schema next to every payload),
   `jobs.md` (every job with its lock) and `routes.md` (no relative route, a purpose and hooks per page) with the expected
   outcome the agent wrote. Generators that do not apply (no parameter enum, no SQL datasets) go into `skip_generators`.
2. Generator regexes (both repositories): when a table misses a row, paste the declaration it missed (the controller
   annotation, the listener, the route object) together with the regex from the generator and ask for the smallest
   change that matches it; rerun `gen-all.py` and diff the table. Never let the agent widen a regex to match everything.
3. `/tag-docs <Page|all>` in the frontend and `/tag-docs <context|all>` in the backend (agent `docs-tagger`): it runs
   `tag-candidates.py --contexts <docs repo>/contexts.yml`, adds `@docs <ID>` to comment lines only, one PR per page or
   context; `BLOCKED` rows mean a page or prefix missing in `contexts.yml`, `SHARED` rows (frontend shared folder) are
   yours to decide. Review the diff: comments only, IDs from the right context.
4. The acceptance question below is asked to `@code-reader`; if it opens more than the map and one file, `AGENTS.md`
   or the map is wrong, not the agent.

**Acceptance:** `gen-all.py --check` passes on a clean checkout and fails when you rename an endpoint without
regenerating; a Copilot question "where is the billing entry point" in the code repo is answered from the map.

---

## 7. Collector (half a day, platform engineer)

**Later** (one local run in the pilot to copy the maps, or copy `docs/_generated/` by hand; CI when a second person writes specs).

One workflow in the docs repository pulls the evidence; the code repositories push nothing.

1. Locally first, from the docs repo, against checkouts of the code repos:
   ```bash
   ./scripts/collect-evidence.py --backend ../backend --frontend ../frontend --generate --graph
   ./scripts/collect-evidence.py --backend ../backend --frontend ../frontend          # second run: "no change"
   ```
   It stages maps, contracts, the Kafka payload schemas (as `generated/asyncapi/schemas/`, the paths in `events.md`
   re-pointed there) and the database documentation folder (as `generated/be/db/`, frontmatter added to its
   pages), validates the candidate (frontmatter on every map, OpenAPI and AsyncAPI headers, every schema file parses,
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

**With an agent.** None for the setup; the two local runs are the test. Copilot can adapt `ci-examples/collect-evidence.yml`
to your runner, token and artifact policy when you paste it with the constraints, nothing more. The first agent that
touches a collector PR is `doc-sync` (section 13).

**Acceptance:** an added, a changed and a deleted contract are reflected correctly; a failed validation publishes
nothing; an unchanged run opens no PR.

---

## 8. Graph and indexes (one hour, then iterate)

**Pilot.**

```bash
python3 scripts/gen-graph.py; python3 scripts/build-index.py
```

Read `generated/graph/REPO_MAP.md`: communities (your contexts), the ranked nodes, the cross-repo flows (route, feature,
endpoint, class, topic or table) and the **spec coverage** list, where every context and every `@docs` calculation
without a document appears as "code only". That list is your backlog. Then:

- `python3 scripts/graph-query.py --node context:billing --depth 2` must show the classes, endpoints, tables and topics you
  expect. Iterate `contexts.yml` until it does. To look at a community instead of reading it:
  `python3 scripts/graph-viewer.py --community billing` writes `.context/graph-viewer.html`; open the file in a browser
  (Python and a browser, nothing else). `--all` opens the page on `(all communities)`, the whole graph coloured by
  community with a legend: the view for spotting a page or class that landed in the wrong context.
- `python3 scripts/migration-status.py --scope all` writes `migration/all.md`: per context the runs due with the command.

**With an agent.** 1. `/migration-plan all` (agent `migration-lead`) runs `migration-status.py`, reads `REPO_MAP.md` and
appends `## Lead notes <date>` to `migration/all.md`: processing order, blockers, targets; that is the first version of
the board. 2. `/impact-from-graph context:<name>` (agent `impact-analyst`, graph only) as the sanity check of a
community: the checklist must name the classes, endpoints, tables and topics you expect; a missing or foreign node is a
prefix or page to fix in `contexts.yml`, not a document to write. 3. `/context-pack <PREFIX>-001` for the pilot even
before the spec exists: the pack's "missing" list is what Run 1 will have to produce.

**Acceptance:** `gen-graph.py --check` and `build-index.py --check` pass twice in a row; the pilot context's community
file names its entry point.

---

## 9. Confluence import (half a day per space)

**Later** (with the first exported space).

Export the space to HTML (the standard space export, no API needed), put each page tree you migrate under
`confluence-import/raw-html/<section>/` and run `scripts/confluence-import.py --src confluence-import/raw-html --space
<KEY> --lang <code> --base-url <url>` ([MIGRATION-RUNBOOK.md](MIGRATION-RUNBOOK.md) step 3; the REST stub
`scripts/confluence-export.py` is the alternative route). It writes one Markdown file per page under
`confluence-import/<SPACE>/<section>/` with a header block (`source`, `title`, `section`, `confluence_id`, `url`,
`author`, `last_modified`, `path`, `parent`, `status`), copies the images a page shows to
`confluence-import/<SPACE>/_attachments/<slug>/`, rewrites the links between pages, and fills the inventory table in
`confluence-import/README.md` (the analysts write only its **Known state** column). It is idempotent and has `--check`.
Rules, all enforced by `confluence-import.instructions.md` and the quarantine README: nothing in that folder is
authoritative; `raw-html/` and the generated pages are never edited by hand; pages are migrated one per run; processed
pages move to `_done/<section>/` through `scripts/legacy-done.py`, which writes `status: migrated|obsolete`, the date
and `superseded_by` (every concept the page went into) and re-points the links; only the images a page shows are imported, and anything with
customer data is deleted before the import; the folder is excluded from the validators.

Triage the inventory with the analysts: for each page the target context and a known state (current, partly outdated,
obsolete, formula page). Formula pages are routed to the calculation audit, never merged by hand. The vocabulary and
examples for the Known state column are in the "Triage" section of `confluence-import/README.md`. No agent reads that
column, so quote a page's note in the request that starts its run.

**With an agent.** The export and the import script are not agent work. The triage is: 1. `/migration-plan <SPACE>`
(agent `migration-lead`) lists the imported pages per target context and the unassigned ones, and proposes a target from
the title, the context map and the glossary; the analyst confirms or corrects in the inventory table. 2. A page the lead
marks as a formula page goes to `/audit-calculation <path of the page>` (agent `calc-auditor` accepts a legacy page as
input) instead of Run 2. 3. An architecture, decision or process page goes to `@architect <path of the page>`
(section 10, "Architecture pages"); the board lists it under "Architecture pages". 4. Everything else waits for Run 2
(`@confluence-migrator`, section 10), one page per run.

---

## 10. Specs, run by run (the core of the work)

**Pilot** (one context, four runs).

One spec is written in four runs; one Copilot run, one human review of the diff, one commit each. The lifecycle skill
(`.github/skills/spec-lifecycle/SKILL.md`) and its review checklist (`references/run-checklist.md`) are the reference.
All commands are typed in the Copilot CLI opened in the docs repo (`/name` is a prompt file; in the CLI invoke it
as in section 1, item 6).

**Before Run 1, shape the spec list of the context** (migration lead with a developer, one hour per context;
the rules are in `features/conventions.md`, section "Shaping specs"). Contexts follow the code seams, never the
menu or the Confluence tree. The first spec of a context is its main screen; every modal or sub-capability with
rules of its own gets the next number (`P1-001` screen, `P1-002` movement modal, `P1-003` peer modal). A
component shared by two screens is described once, in the UI flow of the screen that renders it, and each half of
its behaviour is a rule of the context that owns it, cited by ID. A product type is a dimension inside a
capability spec (`STR-001` BR-5), unless the code has a class family for that product only; then the product is a
context and a mirrored spec restates nothing (`P2-002` reads "as BR-P1-002-1, with transport mode as dimension").
Behaviour across contexts is a flow (`flows/meeting-journey.md`, `flows/session-inputs-recalculation.md`), and every
table column or chart series names a calculation document instead of carrying a formula. Write the list down as the
first rows of the migration board; it is cheaper to split a spec on paper than after stories cite its rule IDs.

**With an agent, the shaping step.** Ask `@architect`: "From `generated/graph/<ctx>.md`, `generated/fe/routes.md`,
the rows of the context's pages in `generated/fe/codebase-map.md` (components, hooks, API calls),
`generated/fe/components.md` (the library and the Page components table: where each page component is rendered, which
hooks it calls) and the rules in `features/conventions.md` 'Shaping specs', propose the spec list of context <ctx>.
You may open the entry file of each page named in `codebase-map.md`, nothing else. One row per screen and per modal or
sub-capability with rules of its own, with ID, title, the page or component that renders it (`file:line`), the backend
operations it owns, and the behaviour that belongs to another context (cite that context); what only a developer can
answer (how a surface opens, which validation it has) as questions. Evidence only, no rules written." The architect
never opens code unless asked, hence the one named file per page. The lead and the developer confirm the list and
answer the questions; the rows go to the board. The four runs below are agent runs with a human review each; Run 4 is
the only human-written step.

**Run 1, skeleton from the code.** `/spec-skeleton-from-graph billing BIL-001`. The `spec-writer` reads the context's
graph file, the contracts and the components map, plus exactly one source file, the context's entry point, and writes
`features/billing/BIL-001.md`: API, events, data and UI flow from the graph with exact names; summary, actors and
business rules from the entry point's documentation, each rule one MUST sentence with an ID; everything unsourced
under Open questions; `status: draft`, no `verified`. Two rules of `features/conventions.md` shape the result: `api[]`
holds only the operations this context handles, and what the screen calls elsewhere stays in the API table with its
owner (consumers read `api[]` as scope: pack contracts, coverage, API tests); and every rule ends with a source marker
naming the symbol it came from, `(source: code manager#<method>)`, never a line range, so the owner at Run 4 opens one
method per rule instead of the file (`okf-validate.py --strict` warns on a draft rule without one). Do this for every
context in one sitting; it is mechanical. One case needs a third argument: a context whose entry layer holds one class
per screen and no orchestrator above them (a hedge service and a scenario service, two pages, no `<Prefix>Service`).
The graph names one of them as the context's entry point, the shortest name, so the first skeleton reads the right
file and the second would read the first screen's. Pass the file of this screen's class as the entry file,
`/spec-skeleton-from-graph product1 P1-002 service/ScenarioService.kt`; the agent reads it instead of the node's file,
still exactly one source file. Nothing after the skeleton needs it: the spec's own `code_refs` and markers name the
right class from then on.

**Run 2, legacy pages.** `@confluence-migrator confluence-import/<SPACE>/<page>.md`, one page per run. The migrator
names every spec the page touches from `generated/catalogue.md` - a legacy page often describes several contexts,
and a context you name in the message is the primary target, not a filter - and merges each fact into the spec of
the context that owns that behaviour; a sequence across contexts goes to a flow, or to an Open question when none
exists; a context the page describes that has no skeleton yet keeps the page out of `_done/` until its Run 1 (the
board keeps listing it). New facts are merged into the skeleton, contradictions become `> ⚠️ CONFLICT (legacy: <page>)` callouts, unverifiable claims
`> ❓ UNVERIFIED`, domain terms go to the glossary, the page is cited in `sources[]` and moved to `_done/`. No number,
threshold or formula is copied from a page. The migrator never creates a spec: a page about a modal or screen that no
spec of the context covers leaves a `candidate spec:` line under the primary spec's Open questions, the board lists
it as a shaping decision with the next free number, the lead and a developer confirm it (or fold it into an existing
spec), Run 1 writes it from the code, and the page is rerun. A new spec has two origins only: the code (Run 1) and a
request the analyst takes to a context without a spec (section 12); a Confluence page is never one.

**Architecture pages.** `@architect confluence-import/<SPACE>/<page>.md` (task "Legacy page"), one page per run, for
a page about what the application is, its parts, integrations or deployment, a decision, or a procedure that still
matters. They are not part of a spec's runs and wait for one thing only: `/integrations-from-contracts` (section 5)
must have refreshed `architecture/integrations.md`, and `scope = overview-draft` rewritten the overview while it
still carried the reference text, so the page is merged into evidence and checked against it. The architect writes
the page's prose into `overview.md`, the `manual` rows and prose of `integrations.md`, a draft ADR or a document under
`architecture/`; a claim that differs from a `gen` row or from existing prose becomes a `> ⚠️ CONFLICT` callout,
never an edit; the page moves to `_done/`. A page with a feature part goes to the migrator first, which merges that
part and hands the rest to the architect. The board lists these pages once, by title (integration, deployment,
decision, architecture, also the Czech stems), outside the contexts' runs and without blocking a context's readiness;
a page the title does not give away is classified in the triage note and handed over by the migrator.

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
The `agentStop` hook runs the validators anyway. Agents run them once, after the last edit of a run, for what they
changed (`okf-validate.py --strict`), never after each edit. A `stale` line (past `stale_after`) is
freshness, not conformance, and never fails a run: the owner re-verifies, nobody moves the date by hand.

---

## 11. Calculations and flows

**Pilot** for the calculations the pilot spec links; flows later.

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

**With an agent.** Calculations: `/audit-calculation <name>` per calculation named by a spec (Run 3); the auditor reports
a calculator without a unit test as a finding and stops, a developer writes the test, then the audit is rerun. Flows: ask
`@architect` (or `@spec-writer` during Run 1 when the graph neighbourhood crosses communities): "Write `flows/<name>.md`
(`type: Flow`) for <behaviour> from `generated/graph/*.md` and the specs <IDs>: trigger, participants per community, steps
with `file:line`, invariants, source map; cite rules by ID, restate none." Glossary: `@spec-writer` adds a row or an alias
when a search term misses; `@confluence-migrator` adds the legacy wording during Run 2. Every result goes through
`validate-frontmatter.py` (parameter cross-check) before the review.

---

## 12. The analyst

**Later** (after the gate of section 16).

Phase 2 of the plan (section 16): run the analyst on real tasks only after the "documentation ready" gate is passed
for the contexts those tasks touch (the scope of section 1). A task that crosses into an out-of-scope context is
the signal to bring that context through Runs 1 to 4 next, not to let the analyst guess.

What the analyst agent is told (`.github/agents/analyst.agent.md`), in short: build the pack and, for a change request, read it top to bottom (spec, calculations, flows,
graph, contracts, tables, related work) - a question takes the narrowest subject with `--budget 200` and reads only the section it names (17.9) -, check the badge, slice stories per the `jira-work-items` skill with Gherkin criteria citing rule IDs, derive subtasks
per graph node kind, write `work-items/<ID>.yml`, validate it, put gaps into `questions[]` and, when blocking, into the
spec's Open questions. Read source only when the pack leaves a question open: at most five ranges, located through
the maps, then a free reading pass for a question that still blocks, each finding recorded as `code-read` evidence and
an open question (decision and setup: 17.2 and section 19). On a finished feature the
input is a change request and the output is delta stories only (17.1).

The everyday sequence:

```bash
python3 scripts/context-pack.py --task BIL-001            # or, in the CLI: Follow .github/prompts/context-pack.prompt.md with task = BIL-001
# in the Copilot CLI (/agent analyst, then):
#   Follow .github/prompts/jira-from-spec.prompt.md with featureId = BIL-001, mode = vertical
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

**Later.**

- **Code changes.** The collector's PR names the specs in the blast radius (manifest diff through `docs-map.yml`).
  `doc-sync` runs on that PR: compares API, events and data sections with the new contracts and maps, updates them,
  appends a change-log row, flags calculations for `calc-auditor` when calculator files changed, stubs any new
  context. A person reviews and merges. The freshness gate in the code repos (`check-freshness.py`,
  `ci-examples/code-repo-freshness-gate.yml`) requires a PR touching a mapped path to bump `last_verified` or carry
  the label `docs-not-affected`.
- **Confluence changes.** Re-export, run `confluence-import.py` again; it skips pages already under `_done/` and the
  inventory flags those whose export is newer than the migrated copy; Run 2 again.
- **Drift found by a reader.** Open question in the spec, status back to draft, owner decides; never a silent edit.
- **The board.** `migration-status.py --scope all` weekly; the `migration-lead` agent annotates order and blockers.

**With an agent.** 1. On every collector PR: `@doc-sync` with the PR body (changed paths mapped to specs); it compares the
API, events and data sections with the new contracts and maps, updates them, appends change-log rows and flags calculations
whose calculator files changed for `/audit-calculation`; a person reviews and merges. 2. Before a risky code change:
`/impact-from-graph` with the pasted `git diff --name-only` (agent `impact-analyst`) for the blast-radius checklist.
3. Weekly: `/migration-plan all` (board notes) and `/coverage-report` (agent `analyst`) for the sprint review.
4. A reader's drift report: a person adds the open question and sets `status: draft`; `/spec-from-code <ID>` (agent
`spec-writer`) then refreshes the spec against the current contracts, maps and graph, opening source only for the rule in question.

---

## 14. Scripts catalogue (what each one reads and writes)

Docs repository, `scripts/` (Python 3.11+, standard library only, no network unless stated):

| Script | Reads | Writes | Safe to run any time |
|---|---|---|---|
| `context-pack.py --task <x> [--budget N] [--print]` | specs, calculations, `graph.json`, contracts, db schema, work items | `.context/<task>.md` (git-ignored) | yes |
| `graph-query.py --node <id> --depth n` / `--files <paths>` / `--find <text>` | `generated/graph/graph.json` | stdout | yes |
| `graph-viewer.py [--all] [--community <id>] [--out <file>]` | `generated/graph/graph.json` | `.context/graph-viewer.html` (git-ignored), a self-contained page to open in any browser: the whole graph coloured by community (`--all`) or one community at a time, filter, neighbours, node details | - |
| `gen-graph.py [--check]` | `generated/be|fe/*.md`, `contexts.yml`, `docs-map.yml`, optional precise exports | `generated/graph/REPO_MAP.md`, `<context>.md`, `graph.json` | yes; `--check` writes nothing |
| `build-index.py [--check]` | frontmatter of every concept | every `index.md` | yes |
| `okf-validate.py [--path <folder or file>] [--strict]` | the bundle (with `--path` only those files can fail) | stdout, exit code | yes |
| `validate-frontmatter.py` | `features/`, `domain/calculations/`, `flows/`, `generated/be/parameters.md` | stdout, exit code | yes |
| `validate-work-items.py [file]` | `work-items/*.yml`, `_schema.yml`, specs (rule IDs) | stdout, exit code | yes |
| `coverage-matrix.py` | specs, work items, feature files | `generated/analytics/coverage-matrix.md|json` | yes |
| `map-paths.py` (stdin paths) | `docs-map.yml` | stdout | yes |
| `check-freshness.py` | PR diff, specs | exit code | CI |
| `collect-evidence.py [--generate] [--graph] [--dry-run]` | the code checkouts (`git`, `docs/_generated`, contracts) | `generated/be|fe|openapi|asyncapi/**`, `generated/manifest.yml`; with `--graph` also graph and indexes | yes; `--dry-run` writes nothing; the only script that runs `git` |
| `migration-status.py --scope <ctx|all>` | `contexts.yml`, specs, calculations, docs tags, REPO_MAP, pending pages | `migration/<scope>.md` | yes |
| `confluence-import.py --src <export> --space <KEY> [--section <tree>] [--lang <code>] [--base-url <url>] [--no-images] [--body md\|html] [--check]` | a Confluence HTML export under `confluence-import/raw-html/<section>/`, `contexts.yml` (guessed context), `<KEY>/_done/` (pages already migrated) | `confluence-import/<KEY>/<section>/<slug>.md`, `<KEY>/_attachments/<slug>/`, the inventory in `confluence-import/README.md`; removes the generated files of pages gone from the export | yes; `--check` writes nothing |
| `hooks/guard-generated.py` | the hook payload | permission decision | hook |
| `confluence-export.py`, `confluence-publish.py`, `jira-push.py`, `push-to-tests-repo.py` | - | - | stubs; implement per environment |

Code repositories, `scripts/docs/` (regex scanners, no build, no execution of application code):

| Generator | Backend output | Frontend output |
|---|---|---|
| `gen-codebase-map.py` | modules and layers with class counts, sub-packages such as `dao/model` as layers of their own (layout from `docs-gen.json`) | page folders with purpose, hooks, components, API calls (literal paths, and `METHOD /path` for calls to a generated client named in `generated_client`), BroadcastChannels (layout from `docs-gen.json`) |
| `gen-components.py` | one row per class: layer or sub-layer, annotations, injected dependencies, tables, `file:line` | the shared component library (props, used-by pages), then the page components (page, props, where each is rendered as `file:line`, hooks it calls) |
| `gen-routes.py` | - | URL -> page component, nested routes joined, route constants resolved, enclosing layout |
| `gen-api-index.py` | every OpenAPI operation with its handler (matched by operationId or by verb + path), plus hand-written routes outside the contract | - |
| `gen-events.py` | topics with producers, consumers, payload type linked to its schema file (`TOPIC` constants of the declaring class, literals and `${property}` names resolved) | - |
| `gen-db-schema.py` | tables and columns from the migrations (read by `_migrations.py`, shared with `gen-db-docs.py`: `CREATE TABLE`, `ALTER TABLE` add / drop / rename / alter column and add / drop constraint, `DROP TABLE`, schema-qualified and quoted names), plus the views defined next to them | - |
| `gen-db-docs.py` (via `gen-all.py`, off with `db_docs.generate: false`) | the database documentation folder: `schema.json`, one page per table (comment, columns with comments, relations, constraints), ER diagram, index; from the migrations and their `COMMENT ON` statements; a foreign key added by `ALTER TABLE ... ADD CONSTRAINT` is a relation like an inline `REFERENCES`, a composite key one relation | - |
| `gen-jobs.py` | scheduled jobs with cron, class and distributed-lock name (ShedLock) | - |
| `gen-parameters.py` | admin parameter catalogue: key, seeded defaults per scope, readers, validator (cross-checked against the calculations by `validate-frontmatter.py`) | - |
| `gen-datasets.py` | named synthetic datasets (seed scripts, integration fixtures): purpose, tables and row counts, loaders, one sample row - analysts cite setups by name instead of describing rows | - |
| `gen-types-index.py` | - | exported types per types file (`types` globs of `docs-gen.json`) |
| `gen-docs-tags.py` | `@docs <ID>` tags with `file:line` | same |
| `tag-candidates.py` | candidates for tags per context, with proposed IDs | same |
| `gen-all.py [--check]` | runs all of the above; `--check` fails when a map is stale | same |
| `shared/check-file-size.py` | line-count budget with a baseline (token hygiene) | same |

---

## 15. Agents catalogue

| Agent | Input | May read | Writes | Start with it in |
|---|---|---|---|---|
| `analyst` | spec ID, calculation, graph node, free text, analytics question | the pack; up to five code ranges located through the maps when it leaves a question open, then a free reading pass for a question that still blocks | `work-items/<ID>.yml`, open questions in the spec, `generated/analytics/*` | week 1 |
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

**17.2 Code access for the analyst: allowed locally, absent on the web.** Decision (revised 2026-10-20): when the
pack, a rebuilt pack and the graph leave a question open that the answer or the analysis needs, the analyst may read at
most five ranges of 40-120 lines per task in `../backend` or `../frontend`. It locates them through the generated
maps - a `file:line` the pack names, `graph-query.py --find`, `components.md`, `codebase-map.md`, the `@docs` tags -
never by searching code or walking folders. A finding is cited as `code-read <file:line>` in the analysis document and
appended to the spec's Open questions; a story resting on it is `needs-spec-review`, and its acceptance criteria still
cite a (draft) rule. The earlier rule - only a `file:line` the pack itself names, only when the task is blocked - left
the analyst with nothing to do but stop while the specs of a context are thin drafts, which is the normal state in the
pilot. When a context's specs are verified this access goes mostly unused; an analyst that still reads code often for
a mature context points at a spec that misses something. The code repositories are sibling checkouts (section 19). Where they are
not available, for example Copilot chat on github.com or a machine with the docs repo only, the agent records the
question and stops; nothing else in the procedure depends on code access, so the web experience is not broken.

Revised again 2026-10-24: five ranges were still a stop for the analyst when the documentation of a context had not
caught up, and a stopped analyst delivers nothing. A question that still blocks the answer or the analysis after the
five ranges now earns one **free reading pass** over both repositories (search, whole files, call chains; analyst
agent step 10). The pass is for blocking questions only, never for "is this intended", which code cannot answer. Its
findings keep the step 9 discipline (`code-read` evidence, unverified, `needs-spec-review`, an Open question in the
spec), the files read are listed in the analysis document, and `coverage-matrix.py` counts the open questions
answered from code per spec in an **answered from code** column: the gaps that cost analyst time, which the
migration lead uses to order the next spec runs. The spec-writer and the calculation auditor keep their narrower
reading on purpose.

Revised once more the same day, for the documentation itself: the pack was also the only way into `features/`,
`domain/` and the other documentation folders, so an analyst that wanted a neighbour spec had to rebuild the pack
with another `--task`. That rule was written against code browsing and swept the documentation along. The analyst
now opens or searches the documentation folders freely after the pack (never the raw Confluence HTML or the
attachments); the pack stays mandatory as the recorded slice a task starts from and as the only source of the
graph neighbourhood and of a merged slice over several subjects. Other agents keep opening the documentation files
their procedure names; code access is unchanged.
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
  Parameters kept in several typed tables instead of one key-value table are outside the generator's shape: skip it
  and document the tables as the pilot track's deferred list says (migration comments, admin Data section,
  `table.column` inputs in the calculations); a table mode of the generator is the kit change that would bring
  them into the two-way check.
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

**17.9 Progressive disclosure inside the pack (2026-10-26).** The bundle discloses progressively, index to index, but
the analyst's procedure said "build one pack, read it top to bottom" for every input, so a small question ("how do we
know a client is an exporter?") was answered after reading a 500-line pack of the spec that links the calculation,
with five table pages and the graph neighbourhood in between, while the answer sits in twenty lines of the
calculation concept. Two causes: subject resolution had no rule for the narrowest kind, so the spec won over the
calculation the glossary alias pointed at; and question mode reused the change-request pack. Now a question takes
the narrowest subject that answers it (calculation for "how is it computed or classified", spec for "what does the
screen show or allow", flow for "in which order across contexts", never `context:<name>`), is built with
`--budget 200` (the ranked truncation keeps the Subject, the spec or calculation body and the linked calculations
whole and turns the graph, contracts, tables, related items and legacy pages into pointers) and the analyst reads
the Subject and the section the question names; a pointer is followed only when the answer needs it, and dropping
the budget is escalation step 1 as before. A change request keeps the full pack read top to bottom: the epic uses
every section and the analysis document cites the pack. Measured: the CLI-001 pack goes from 521 to about 215 lines
at budget 200, the calculation pack is 131 lines with nothing truncated. When the section does not answer, the
question's first escalation is a search of the documentation folders and one opened document, cited; the pack is
rebuilt only when the question turns out structural (the graph section) or spans several subjects. The free search was
permitted since 17.2's third revision but was not a numbered step, and an agent takes the numbered steps.

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
| `architecture/overview.md`, `integrations.md` | `docs-repo/architecture/overview.md`, `integrations.md` | `generated/be/codebase-map.md`, `api-index.md`, `events.md`, `generated/openapi/external/*.yaml`; the tables and the context diagram through `/integrations-from-contracts`, the whole overview once through its `scope = overview-draft`, the prose by hand afterwards | boundaries, ownership, anything the maps cannot show (hosting, auth) |
| `architecture/adr/*.md` | `docs-repo/architecture/adr/template.md`, `0002-openapi-first-contracts.md` | the decision as you would say it in one paragraph, plus the alternatives considered | the decision itself; an ADR is never generated from code |
| `flows/*.md` | `docs-repo/flows/client-presentation.md` | the pack of each spec involved, `generated/graph/<community>.md` | steps and invariants; participants |
| `features/conventions.md`, `contracts/conventions.md` | the files of the same name | your existing team rules (naming, ID scheme, review) | they match how the team works, not how the model thinks it should |
| `confluence-import/README.md` inventory | `docs-repo/confluence-import/README.md` | the table `confluence-import.py` generates (page, id, date, author, images, guessed context) | the **Known state** column: which pages are in scope, their class and target, who owns them |
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
