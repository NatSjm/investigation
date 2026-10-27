# Migration runbook: from Confluence pages to agent-ready documentation

Audience: the team that will prepare the documentation bundle before the analyst agent is allowed to work from it.
Everything below is already set up and rehearsed in `docs-repo/` (three sample legacy pages under
`confluence-import/HARBOR/`). Paths are relative to `docs-repo/` unless stated otherwise.

## 0. Principle

The code is the truth, Confluence is evidence. We therefore build the skeleton of every document **from the code
maps first** and only then merge the Confluence pages into it, page by page, with every claim verified or marked.
A page is never copied; it is cited (`sources[]`) and the facts it adds are either confirmed against `generated/`
or flagged `❓ UNVERIFIED` / `⚠️ CONFLICT`.

## 1. Target structure of the docs repository

| Folder | Content | Who writes it |
|---|---|---|
| `features/<context>/<CTX>-<NNN>.md` | functional specs (OKF Feature Spec), business rules `BR-<ID>-<n>` | `spec-writer`, `confluence-migrator`, humans verify |
| `domain/calculations/<name>.md` | one concept per calculation: formula, parameters, worked examples, audit table | `calc-auditor`, `spec-writer` |
| `domain/glossary.md`, `domain/context-map.md` | terminology (with `Aliases` for legacy / source-language terms), bounded contexts | humans + `confluence-migrator` |
| `architecture/` | overview, integration map, ADRs, HLDs | `architect` |
| `confluence-import/<SPACE>/` | raw exported pages (quarantine): `<section>/<slug>.md` per page tree, `_attachments/<slug>/` images, `_done/` after migration; `raw-html/` the HTML export as received | `scripts/confluence-import.py` (HTML export), `scripts/confluence-export.py` (REST, stub) |
| `generated/be`, `generated/fe`, `generated/openapi`, `generated/asyncapi` | code maps and contracts collected from the code repos as one validated snapshot (`generated/manifest.yml` names the source commits); never edited by hand | the docs repo's collector `scripts/collect-evidence.py` (CI: `ci-examples/collect-evidence.yml`, one PR per snapshot) |
| `generated/graph/` | architectural graph: `REPO_MAP.md`, one `<context>.md` per bounded context, `graph.json` | `scripts/gen-graph.py` |
| `generated/analytics/` | coverage matrix (BR -> story -> scenario) | `scripts/coverage-matrix.py` |
| `work-items/`, `test-design/` | outputs of the analyst and test-designer agents (after the migration) | `analyst`, `test-designer` |
| `contexts.yml`, `docs-map.yml` | context -> BE class-name prefixes / FE feature / spec prefix; code path globs -> specs | humans (once), then maintained |
| `index.md` per folder, `log.md` | generated indexes with trust badges, lifecycle log | `scripts/build-index.py`, agents |

## 2. Steps

### Step 1: make the code repositories readable (dev lead, once per repo)

1. Apply `code-repo-kit/be` and `code-repo-kit/fe` (`apply-kit.py`): `AGENTS.md`, `.github/instructions`,
   `scripts/docs/gen-*.py`, the CI job that publishes `docs/_generated` + contracts to the docs repo.
2. Add `@docs <SPEC-ID>` KDoc tags to every `manager/<Ctx>Manager.kt` and `@docs <calculation_name>` to every
   calculation in `utils/`. These tags are how agents jump from a document to `file:line` without searching.
3. Run `scripts/docs/gen-all.py` in both repos; check `docs/_generated/*.md` reads correctly
   (components, api-index with no unimplemented operations, events, db-schema, jobs, routes, types).

### Step 2: bootstrap the docs repository (dev lead + one analyst, one day)

1. Fill `contexts.yml`: one line per bounded context with spec prefix, FE feature folder and BE class-name prefixes.
   Unmatched classes show up as `shared` in the graph; iterate until `shared` holds only true helpers.
2. `python3 scripts/collect-evidence.py --generate --graph` (or merge the collector's PR): runs both generators, validates the snapshot, writes `generated/manifest.yml`, then `gen-graph.py` and `build-index.py`.
3. Read `generated/graph/REPO_MAP.md`: every community is a future spec; the "code only" list is the backlog.
4. Seed `domain/glossary.md` with the terms that appear in the contracts and the entity names (code vocabulary),
   leaving the `Aliases` column for the Confluence wording.
5. Fill `docs-map.yml` with one mapping per context (prefix globs), even when the spec does not exist yet (`specs: []`).

### Step 3: export and triage Confluence (analysts, half a day per space)

1. Export the space to HTML (Confluence "Export space to HTML", no API needed) and put each page tree you migrate
   under `confluence-import/raw-html/<section>/` (one folder per page `<Title>_<pageId>/<pageId>.html` with its images
   next to it, or the standard export files `<Title>_<pageId>.html` + `attachments/<pageId>/`). Then
   `python3 scripts/confluence-import.py --src confluence-import/raw-html --space <KEY> --lang <code> --base-url <url>`:
   one file per page under `confluence-import/<KEY>/<section>/<slug>.md` with the header block `source`, `title`,
   `section`, `confluence_id`, `url`, `author`, `last_modified`, `path`, `parent`, `source_lang`, `status: imported`,
   `attachments`, `imported_from`; the body converted to Markdown (`--body html` keeps it as HTML: Copilot reads both).
   The REST route (`scripts/confluence-export.py`, a stub) remains for a space you cannot export as HTML.
2. Images the pages show are copied to `confluence-import/<KEY>/_attachments/<slug>/`; nothing else is. Delete every
   screenshot or table containing client data from `raw-html/` before the import (synthetic data rule); the importer
   is idempotent, so re-run it after every such deletion and keep `--check` clean.
3. The importer writes the inventory table into `confluence-import/README.md` (page, `confluence_id`,
   `last_modified`, author, images, guessed context from the title and the spec IDs the page cites); the analysts fill
   the **Known state** column: guessed class (`feature-spec | calculation | architecture | decision | glossary |
   process | obsolete`), condition and target concept (vocabulary and examples: the "Triage" section of
   `confluence-import/README.md`). Sort the work by business value and age; pages older than the last major
   release are suspects by default. A later export is imported the same way: pages already under `_done/` are not
   rewritten, and the inventory flags those whose export is newer than their migrated copy (Run 2 again).

### Step 4: skeletons from the code (one agent run per context)

For every community in `REPO_MAP.md` without a spec, run the prompt `spec-skeleton-from-graph` with
`<community> <CTX>-001` (agent `spec-writer`). It fills API / Events / Data / UI flow / Calculations from the graph
and contracts, and Summary / Actors / Business rules from the manager KDoc only. Result: `status: draft`, open
questions listed, `docs-map.yml` updated. For every `@docs <calculation>` tag without a concept, create one from
`domain/calculations/_template.md` with the worked examples copied from the unit test (`calc-auditor` does this).

### Step 5: merge Confluence pages, one page per run

- `@confluence-migrator confluence-import/<SPACE>/<page>.md` for feature, glossary and obsolete pages. It names
  every spec the page touches from `generated/catalogue.md`, merges only new facts, marks conflicts and unverifiable
  claims, extracts terms into the glossary, adds the `sources[]` entry, moves the page to `_done/`, validates, logs.
- The migrator never creates a spec. A page about a capability no spec covers leaves a `candidate spec:` open
  question in the primary spec; the board lists it as a shaping decision with the next free number; the lead and a
  developer confirm it, Run 1 (step 4) writes it from the code, the page is rerun.
- Formula pages are handed to `calc-auditor` (`audit-calculation` prompt). It opens exactly two files (calculator and
  its unit test), writes the `## Audit <date>` table with `MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED`, and never
  changes numbers itself. Non-MATCH rows become open questions naming an owner.
- Architecture, decision and still-relevant process pages go to `@architect confluence-import/<SPACE>/<page>.md`
  (task "Legacy page"; the board lists them, and the migrator hands one off when it is given one). Run them after
  `/integrations-from-contracts` has refreshed `architecture/integrations.md` (and `scope = overview-draft` while the
  overview still carries the reference text), not after the skeletons: the architect merges the page's prose into
  `overview.md`, the `manual` rows of `integrations.md`, an ADR from `architecture/adr/template.md` or a document under
  `architecture/`, marks claims that differ from a `gen` row as conflicts, and moves the page to `_done/`. A page with a
  feature part goes to the migrator first, which merges that part and hands the rest on.
- Pages in another language are translated during normalisation through the glossary `Aliases` column; the original
  title and key terms go into `aliases:` so searches in the source language still work.

The run-by-run lifecycle of one spec (skeleton -> legacy merge -> calculation audit -> owner decision), with what
each run reads and writes, is documented in `docs-repo/features/conventions.md`, section "Lifecycle of one spec".

Review rhythm: one agent run, then a 10-15 minute human review of the diff (the hook `agentStop` already ran
`build-index`, `okf-validate --strict`, `validate-frontmatter`, `validate-work-items`). Commit per page.

### Step 6: owners verify (domain owners, continuous)

A spec or calculation becomes `status: stable` only when an owner adds `verified: { by: human:<id>, at }` and
`stale_after` (+90 days). Open questions are decided by the owner, recorded in the concept's Change log, and the
legacy page keeps `superseded_by:` for the audit trail. Index badges (`build-index.py`) show the state per concept.

### Step 7: close the loop

1. `python3 scripts/coverage-matrix.py` and `python3 scripts/okf-validate.py --strict` clean; `gen-graph.py --check` and
   `build-index.py --check` pass in CI (`.github/workflows/docs-quality.yml`).
2. Enable the freshness gate in the code repos (`code-repo-kit/ci/docs-maps.yml` + `check-freshness.py`): a PR that
   touches a mapped path must bump `last_verified` or carry `docs-not-affected`. From then on `doc-sync` keeps specs
   current from the generated diffs.
3. Replace each migrated Confluence page by a banner + link to the published copy (`confluence-publish.py`, stub
   today; `translate-for-publish` renders the source-language view).

## 3. Definition of "ready for the analyst agent"

- No "code only" community in `generated/graph/REPO_MAP.md`; every context has at least `<CTX>-001`.
- Every `@docs <calculation>` tag has a concept with worked examples copied from its test and an audit table.
- Every page in `confluence-import/` is in `_done/` with `status: migrated | obsolete`.
- Glossary covers every term used in the specs; `okf-validate --strict` reports 0 errors.
- `python3 scripts/context-pack.py --task <ID> --print` for each spec fits the budget and contains spec, calculations,
  graph neighbourhood, contracts and tables.
- At least the high-value specs are `stable` (human-verified); the analyst labels stories from `draft` specs
  `needs-spec-review` automatically.

## 3a. Tracking the work

`python3 scripts/migration-status.py --scope all` (or `@migration-lead` / `/migration-plan all` in Copilot) writes
`docs-repo/migration/all.md`: per context the runs still due with the exact command to type, pending legacy pages,
calculations without concept or audit, and specs waiting for an owner. The lead agent appends processing order,
targets for unclassified pages, batch-vs-interactive advice and blockers; it never edits specs itself.
Lifecycle and per-run review checklist: `docs-repo/.github/skills/spec-lifecycle/`.

## 4. Who does what

| Role | Steps | Tools |
|---|---|---|
| Dev lead | 1, 2, 7.2 | kit scripts, CI, `contexts.yml` |
| Migration lead (one analyst) | 3a | `migration-lead` agent, `migration-status.py`, `migration/all.md` as the team board |
| Analysts (2) | 3, 4, 5 | Copilot agents `spec-writer`, `confluence-migrator`, `calc-auditor`, `architect`; prompts in `.github/prompts/` |
| Domain owners | 6 | review diffs, add `verified.by` |
| Everyone | - | `AGENTS.md` read order, `context-pack.py` before any question |
