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

It writes `.context/<task>.md` (git-ignored, ~300-500 lines): the spec with its trust badge, linked calculations
(formula + worked examples), the flows it takes part in, the depth-2 graph neighbourhood (endpoints, classes, tables, topics, FE routes with
`file:line`), the OpenAPI operations and tables involved, existing work items / tests, and legacy pages that mention
the subject. **Read the pack, not the repository.** Open anything else only to answer a question the pack leaves
open, and then only the `file:line` it names. Skill: `.github/skills/task-context/SKILL.md`.

## Read order when there is no pack (cheapest first)

1. `index.md` -> the area's `index.md` (one line + trust badge per concept)
2. `features/<context>/<ID>.md` - functional spec; business rules are `BR-<ID>-<n>`
3. `domain/calculations/<name>.md` - formulas and worked examples (never re-derive from Kotlin)
4. `contexts.yml` (context -> BE class-name prefixes, FE feature, spec prefix), then `generated/graph/REPO_MAP.md` ->
   `generated/graph/<context>.md` - architectural graph (`context:`, `class:` nodes, `depends-on` / `persists-to` edges) with `file:line`
5. `generated/be/*.md`, `generated/fe/*.md` - code maps (admin parameters in `parameters.md`, named datasets in `datasets.md`, BE layers in `codebase-map.md`, one row per class in `components.md`,
   API index with `Tag` = context, events, schema, jobs, routes, types, `@docs` tags)
6. `generated/openapi/backend.yaml`, `generated/openapi/external/*.yaml`, `generated/asyncapi/backend.yaml` - contracts the
   code implements; `contracts/proposed/<ID>.*.yaml` - contracts still being designed (proposals, see `contracts/conventions.md`)
7. Only then source code in `../backend` / `../frontend`, smallest possible range, located via the graph, `components.md` or
   `docs-tags.md`. The backend is layered (`core/src/main/kotlin/harbor/<layer>/`): start at the context's `manager/<Ctx>Manager.kt`.

## Hard rules

- Never hand-edit `generated/**`; it is published by the code repositories' CI. Fix the generator or the code.
- Every concept under `architecture/`, `domain/`, `features/`, `flows/` (cross-context behaviour, `type: Flow`), `generated/` has frontmatter with `type`; folders use
  `index.md` (built by `scripts/build-index.py`), never `README.md`.
- Provenance: set `generated: { by: copilot/<agent>, at: <ISO> }` on anything you write; cite `sources[]` with
  `[^id]`; never write `verified.by: human:<id>` yourself; `status: draft` until a person verifies.
- Traceability IDs are mandatory: specs `<CTX>-<NNN>` (`CLI MTG IMP P1 P2 COV MKT STR RPT ADM`), rules
  `BR-<ID>-<n>`, calculations `snake_case`. Work items and test scenarios cite them.
- Terminology from `domain/glossary.md`; English only in files (answer in the user's language in chat).
- Synthetic data only: no real client names, identifiers or contract values in docs, fixtures or examples.
- A contract designed before code lives under `contracts/proposed/` (`x-status: proposed`), is cited as **proposed**
  and never as current behaviour; it reaches `generated/` only through a code repository and the collector.
- Keep outputs in files; chat summaries <= 15 lines. Specs <= 300 lines; diagrams <= 25 nodes.

## Commands (Python 3.11+, no other dependencies)

| Purpose | Command |
|---|---|
| Task context pack | `python3 scripts/context-pack.py --task <ID|name|text> [--budget 500]` |
| Validate bundle | `python3 scripts/okf-validate.py --strict`; `python3 scripts/validate-frontmatter.py`; `python3 scripts/validate-work-items.py` |
| Rebuild indexes | `python3 scripts/build-index.py` (`--check` in CI) |
| Graph | `python3 scripts/gen-graph.py [--check]`; `python3 scripts/graph-query.py --node spec:P1-001 --depth 2` / `--files <paths>` / `--find <text>` |
| Changed code -> specs | `git -C ../backend diff --name-only main | sed 's#^#be/#' | python3 scripts/map-paths.py` |
| Analytics | `python3 scripts/coverage-matrix.py` (BR <-> story <-> scenario matrix into `generated/analytics/`) |

Before finishing any edit: `okf-validate.py --strict`, `build-index.py`, and a dated entry in `log.md` for
lifecycle events (created / deprecated / verified / regenerated).

## Agents, prompts, skills

Custom agents live in `.github/agents/` (`analyst`, `spec-writer`, `doc-sync`, `calc-auditor`, `test-designer`,
`architect`, `impact-analyst`, `confluence-migrator`, `migration-lead`), one-shot prompts in `.github/prompts/`,
procedures in `.github/skills/`. A spec is written run by run (skeleton -> legacy merge -> calculation audit ->
owner decision; skill `spec-lifecycle`); `python3 scripts/migration-status.py --scope all` lists the runs still due per
context in `migration/all.md` (agent `migration-lead` / prompt `migration-plan`). Copilot-specific notes are in `.github/copilot-instructions.md`. Layout table: `README.md`.
