# Copilot instructions - advisory frontend (React / TypeScript)

## Read in this order (cheapest first)
1. `docs/_generated/index.md` -> `codebase-map.md` (features, public exports, API calls), `routes.md`, `types-index.md`, `docs-tags.md`.
   For "which BE endpoint / which screens are affected" questions: docs repo `generated/graph/<feature>.md` or VS Code `#impact <node|file>`.
2. The feature barrel `src/features/<name>/index.ts` and `<name>.types.ts`.
3. Only then a specific component/hook named there. Never walk `src/` or open `node_modules`.
4. BE contract: the BE repo `docs/_generated/api-index.md` (or docs repo `generated/openapi`) - not BE source.
5. Business rules / acceptance criteria: docs repo `features/**/<ID>.md`; cite the ID.

## Never open
`node_modules/`, `dist/`, `coverage/`, lockfiles, `*.snap`, `*.stories.tsx` (unless asked about Storybook),
generated API clients (`src/api/generated/**`), i18n JSON bundles, large mock JSON > 100 lines.

## Conventions
- Feature folders: `src/features/<name>/{index.ts, <name>.types.ts, api/, ui/, hooks/}`; cross-feature imports only via the barrel.
- `index.ts` starts with a JSDoc `@module <name>` block: one sentence purpose + `@docs <ID>`; keep it current.
- Types mirror BE DTOs 1:1 in `<name>.types.ts`; tag with `@docs <ID>`.
- Files <= 300 lines; components <= 150 lines; one component per file.
- Data fetching via hooks in `api/` (react-query); no `fetch` inside components.
- Charts/graphs: computation in a pure `compute*.ts` function (unit-tested), rendering separate.
- No real client data in fixtures/mocks; synthetic only.

## Output discipline
- Return diffs, not full files. Explanations <= 15 lines with `file:line`.
- After changing routes, barrels, types or `@docs` tags, run `scripts/docs/gen-all.ps1` and include regenerated `docs/_generated/*`.

## Context hygiene
Prefer `#file`/`#sym`/`#selection` over `@workspace`; open `workspaces/<feature>.code-workspace`, not the repo root.
