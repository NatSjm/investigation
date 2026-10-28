# AGENTS.md - Harbor documentation repository

This repository is the **single source of truth** for functional and technical documentation of the Harbor
platform (client meetings, Product 1 / Product 2 movements and projections, cover, market scenarios, stress tests,
reports, administration). Confluence is a *publish target*; the code repositories `harbor-backend` (Kotlin/Spring,
`be/`) and `harbor-frontend` (React/TypeScript, `fe/`) are *inputs*; Jira and the tests repository are *outputs*.

The repository is one **Open Knowledge Format v0.2 bundle**: every document is a concept with YAML frontmatter and
every folder has a generated `index.md`. Agents orient through indexes, never through directory listings.

## Work task-scoped: build the context pack first

For any task about a feature, calculation, change or ticket:

```bash
python3 scripts/context-pack.py --task P1-001          # spec ID, calculation name, graph node or free text
```

It writes `.context/<task>.md` (git-ignored; sized by its subjects, roughly 1000 lines for one spec with its
calculations and neighbourhood, more with several subjects, `--budget N` to cap it): the spec with its trust badge, linked calculations
(formula + worked examples), the flows it takes part in, the depth-2 graph neighbourhood (endpoints, classes, tables, topics, FE routes with
`file:line`), the OpenAPI operations and tables involved, existing work items / tests, and legacy pages that mention
the subject. **Read the pack first.** It is the recorded slice the task starts from: a change request takes the full
pack top to bottom; a question takes the narrowest subject (calculation, spec or flow, never a context) with
`--budget 200` and reads the Subject and the section it names, the rest stays a pointer. After it the analyst opens or
searches the documentation folders freely (never `raw-html/` or `_attachments/`); other agents open the documentation
files their procedure names; code only at the `file:line` the pack names, the analyst also under its steps 9 and 10.
Skill: `.github/skills/task-context/SKILL.md`.

A request in free text ("when imports change, do the stress numbers refresh?", "dashboard with the cover ratio trend
and a new churn score") names no ID and often spans several contexts: read `generated/catalogue.md` first (one line
per context, flow, spec, calculation, endpoint, topic, table, external service and glossary alias), pick the subjects
yourself and build one pack with a `--task` per subject (spec ID, calculation, `flows/<name>.md`, `context:<name>`);
what matches no line is new work: add the context it belongs to as a subject, its overview shows what is already there.

## Read order when there is no pack (cheapest first)

1. `generated/catalogue.md` (everything on one page, one line each) or `index.md` -> the area's `index.md` (one line + trust badge per concept)
2. `features/<context>/<ID>.md` - functional spec; business rules are `BR-<ID>-<n>`
3. `domain/calculations/<name>.md` - formulas and worked examples (never re-derive from Kotlin)
4. `contexts.yml` (context -> BE class-name prefixes, FE feature, spec prefix), then `generated/graph/REPO_MAP.md` ->
   `generated/graph/<context>.md` - architectural graph (`context:`, `class:` nodes, `depends-on` / `persists-to` edges) with `file:line`
5. `generated/be/*.md`, `generated/fe/*.md` - code maps (admin parameters in `parameters.md`, named datasets in `datasets.md`, BE layers in `codebase-map.md`, one row per class in `components.md`,
   API index with `Tag` = context, events, schema, jobs, routes, types, `@docs` tags)
6. `generated/openapi/backend.yaml`, `generated/openapi/external/*.yaml`, `generated/asyncapi/backend.yaml` - contracts the
   code implements; `contracts/proposed/<ID>.*.yaml` - contracts still being designed (proposals, see `contracts/conventions.md`)
7. Only then source code in `../backend` / `../frontend`, smallest possible range, located via the graph, `components.md` or
   `docs-tags.md`. The backend is layered (`harbor-core/src/main/kotlin/com/acme/harbor/<layer>/`): start at the context's `manager/<Ctx>Manager.kt`.

## Hard rules

- Never hand-edit `generated/**`; it is published by the code repositories' CI. Fix the generator or the code.
- Every concept under `architecture/`, `domain/`, `features/`, `flows/` (cross-context behaviour, `type: Flow`), `generated/` has frontmatter with `type`; folders use
  `index.md` (built by `scripts/build-index.py`), never `README.md`.
- Provenance: set `generated: { by: copilot/<agent>, at: <ISO> }` on anything you write; cite `sources[]` with
  `[^id]`; never write `verified.by: human:<id>` yourself; `status: draft` until a person verifies. A business rule
  you write ends with its source marker, `(source: code <sources-id>#<symbol>)` or the legacy / contract / person /
  spec form (`features/conventions.md`, "Provenance per rule"); so does every Formula step and the Conventions
  paragraph of a calculation (`calculations.instructions.md`, "Provenance per step"); a spec's `api[]` lists only the
  operations its own context handles ("Owned versus called operations").
- Traceability IDs are mandatory: specs `<CTX>-<NNN>` (`CLI SES IMP P1 P2 COV MKT STR RPT ADM`), rules
  `BR-<ID>-<n>`, calculations `snake_case`. Work items and test scenarios cite them.
- Terminology from `domain/glossary.md`; English only in files (answer in the user's language in chat).
- Synthetic data only: no real client names, identifiers or contract values in docs, fixtures or examples.
- A contract designed before code lives under `contracts/proposed/` (`x-status: proposed`), is cited as **proposed**
  and never as current behaviour; it reaches `generated/` only through a code repository and the collector.
- Keep outputs in files; chat summaries <= 15 lines. Specs <= 300 lines; diagrams <= 25 nodes.

## Commands (Python 3.11+, no other dependencies)

| Purpose | Command |
|---|---|
| Task context pack | `python3 scripts/context-pack.py --task <ID|calculation|flows/<name>.md|context:<name>|node|text> [--task ...] [--budget N]` (several `--task` = one merged pack; no cap unless `--budget`) |
| Catalogue (free-text requests start here) | `python3 scripts/gen-catalogue.py` -> `generated/catalogue.md` (`--check` in CI) |
| Validate (see Checks) | `python3 scripts/okf-validate.py --strict` (the whole bundle; `--path <folder or file>` lets only that part fail); `python3 scripts/validate-frontmatter.py [<file>]`; `python3 scripts/validate-work-items.py [<file>]` |
| Rebuild indexes | `python3 scripts/build-index.py` (`--check` in CI) |
| Graph | `python3 scripts/gen-graph.py [--check]`; `python3 scripts/graph-query.py --node spec:P1-001 --depth 2` / `--files <paths>` / `--find <text>` |
| Changed code -> specs | `git -C ../backend diff --name-only main | sed 's#^#be/#' | python3 scripts/map-paths.py` |
| Processed legacy page -> `_done/` | `python3 scripts/legacy-done.py <page> --into <concept> [--into ...]` (or `--status obsolete --reason "<why>"`); never move the file by hand |
| Analytics | `python3 scripts/coverage-matrix.py` (BR <-> story <-> scenario matrix into `generated/analytics/`) |

## Checks: once, at the end of a task, for what it changed

Never after each edit; the `agentStop` hook runs the full set again when you stop.

- Changed no file by hand (a question, a pack, a graph query, analytics - generators write valid files): run nothing.
- Changed a concept (a `.md` of the bundle: `features/`, `domain/`, `architecture/`, `flows/`, `contracts/`, root
  pages): `build-index.py`, then `okf-validate.py --strict` over the whole bundle (quick; it runs no git command).
  The hook and CI keep the bundle at zero warnings, so what it reports normally comes from your edit, a link your
  rename or deletion broke in another file included; an older problem in a file your task did not touch is reported,
  not fixed. A spec or a calculation also gets `validate-frontmatter.py <file>`.
- Changed a work-item file: `validate-work-items.py <file>`.
- A dated entry in `log.md` for lifecycle events only (created / deprecated / verified / regenerated).
- A `stale` line is freshness, not a failure: never move `stale_after` or write `verified` to clear it.

## Agents, prompts, skills

Custom agents live in `.github/agents/` (`analyst`, `spec-writer`, `doc-sync`, `calc-auditor`, `test-designer`,
`architect`, `impact-analyst`, `confluence-migrator`, `migration-lead`), one-shot prompts in `.github/prompts/`,
procedures in `.github/skills/`. A spec is written run by run (skeleton -> legacy merge -> calculation audit ->
owner decision; skill `spec-lifecycle`); `python3 scripts/migration-status.py --scope all` lists the runs still due per
context in `migration/all.md` (agent `migration-lead` / prompt `migration-plan`). A request in free text goes through
`analyst` / prompt `analyse-request`: catalogue -> one pack -> analysis document (`work-items/<slug>.md`, reading
confirmed by the analyst) -> request epic (`work-items/<slug>.yml`); nothing new without a draft rule first.
Copilot-specific notes are in `.github/copilot-instructions.md`. Layout table: `README.md`.
