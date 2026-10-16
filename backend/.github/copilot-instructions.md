# Copilot instructions - harbor-backend

The repository rules (read order, contracts, conventions, commands, where business rules live) are in
[`AGENTS.md`](../AGENTS.md). This file adds only what is specific to GitHub Copilot.

## Never open (also enforced by content exclusion in the GitHub repo settings)
`target/` (incl. `generated-sources`), `build/`, `*.iml`, lockfiles, `src/test/resources/**/*.json|*.csv` fixtures,
`application-*.yml`, keystores. Migrations only when the task is a DDL change.

## Output discipline
- Return diffs / edited files, never whole-file dumps in chat.
- "How does X work" answers: map + manager (+ its row in `components.md`), <= 15 lines, `file:line` links and the spec ID; expand only on request.
- After touching an endpoint, topic, table, job or `@docs` tag: run `scripts/docs/gen-all.py` and include `docs/_generated/*` (incl. `components.md`).

## Context references
Prefer `#file`, `#sym`, `#selection` over `@workspace` / `#codebase`. Start from `#file:docs/_generated/index.md`.

## Custom agents and prompts in this repo
- Agents (`.github/agents/`): `code-reader` (read-only navigator, max 3 files), `impact-analyst` (blast-radius checklist),
  `docs-tagger` (adds missing `@docs` KDoc tags from `contexts.yml`, comment lines only, one PR per context).
- Prompts (`.github/prompts/`): `/explain-module` (explains a context: manager + its dependencies; default `product1`), `/find-spec-code` (default `P1-001`),
  `/add-endpoint` (contract-first checklist), `/tag-docs <context|all>` (inventory from `scripts/docs/tag-candidates.py`, then the tags),
  `/adapt-docs-scripts` (security review of `scripts/docs/*` and the `docs-gen.json` for this repository; never runs anything, a person runs after review).
- Hook `.github/hooks/docs-maps.json` runs `gen-all.py --check` when an agent session stops.

## Docs-repo tools
- VS Code with the "Harbor Docs for Copilot" extension: `#docsLookup:P1-001`, `#codeMap`, `#specToCode`, `#impact <node|file>`,
  participant `@docs /spec | /where | /impact`.
- JetBrains: `python3 ../harbor-docs/scripts/graph-query.py --node spec:P1-001 --depth 2` and attach `docs/_generated/<map>.md` to the chat.
