# Copilot instructions - harbor-frontend

The repository rules (read order, contracts, conventions, commands, where business rules live) are in
[`AGENTS.md`](../AGENTS.md). This file adds only what is specific to GitHub Copilot.

## Never open (also enforced by content exclusion in the GitHub repo settings)
`node_modules/`, `dist/`, `coverage/`, lockfiles, `*.snap`, `src/api/generated/**`, `public/locales/**`,
`*.stories.tsx` (unless asked about Storybook), mock JSON over 100 lines.

## Output discipline
- Return diffs, not full files. Explanations <= 15 lines with `file:line` and the spec ID.
- After changing routes, barrels, types or `@docs` tags: run `scripts/docs/gen-all.py` and include `docs/_generated/*`.
- A new or changed backend field starts in the backend `core/src/main/resources/openapi/harbor-api.yaml`; here only `npm run generate:api` and the
  feature types/hooks change.

## Context references
Prefer `#file`, `#sym`, `#selection` over `@workspace` / `#codebase`. Start from `#file:docs/_generated/index.md`;
for backend endpoints use the backend `docs/_generated/api-index.md` or `#codeMap`, not backend source.

## Custom agents and prompts in this repo
- Agents (`.github/agents/`): `code-reader` (read-only navigator, max 3 files), `docs-tagger` (adds missing `@module` / `@docs`
  JSDoc tags from `contexts.yml`, comment lines only, one PR per feature).
- Prompts (`.github/prompts/`): `/explain-feature` (default `stress`), `/tag-docs <feature|all>` (inventory from `scripts/docs/tag-candidates.py`, then the tags).
- Hook `.github/hooks/docs-maps.json` runs `gen-all.py --check` when an agent session stops.

## Docs-repo tools
- VS Code with the "Harbor Docs for Copilot" extension: `#docsLookup:P1-001`, `#codeMap`, `#specToCode`, `#impact <node|file>`,
  participant `@docs /spec | /where | /impact`.
- JetBrains: `python3 ../harbor-docs/scripts/graph-query.py --node feature:stress --depth 2` and attach `docs/_generated/<map>.md`.
