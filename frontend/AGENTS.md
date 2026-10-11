# AGENTS.md - harbor-frontend (React 18 / TypeScript / react-router / openapi-fetch)

Read by Copilot Chat (VS Code, JetBrains), Copilot CLI, the Copilot coding agent and other agent tools.
Copilot-specific extras are in `.github/copilot-instructions.md`; path-scoped rules in `.github/instructions/`.

## What this repository is
Web client of the Harbor platform. Account representatives search clients, start a **meeting session**, work through the
product overview pages (projection tables, cover charts, movement and peer-simulation modals), market scenarios and the
stress test, and download the meeting report. One feature folder per bounded context, named like the context in the docs repo `contexts.yml` (BE classes carry the matching name prefix):
`clients`, `meetings`, `product1`, `product2`, `cover`, `market`, `stress`, `reports`, `admin`.
`presentation` (FE-only, `PRS-001`) is the client-facing window `/present/:sessionId`; all cross-window sync goes through
the single `BroadcastChannel` module `src/features/presentation/channel.ts` (`route` / `view` / `session-closed` messages).

## Read in this order (cheapest first) - never walk `src/`
1. `docs/_generated/index.md`, then the map that answers the question: `codebase-map.md` (features, exports, API calls),
   `routes.md` (URL -> component), `types-index.md` (exported types), `docs-tags.md` (spec ID -> code).
2. The feature barrel `src/features/<name>/index.ts` and `src/features/<name>/<name>.types.ts`.
3. One component or hook named there. Max 3 source files per question.
4. For "which backend endpoint / which screens are affected" use the docs repo `generated/graph/<feature>.md`.

## Contracts (source of truth)
- The backend `core/src/main/resources/openapi/harbor-api.yaml` is the REST contract. `src/api/generated/schema.d.ts` is **generated** from it
  (`npm run generate:api`); never edit it by hand. `src/api/client.ts` exports the typed `api` client (base URL `/api/v1`).
- Hooks call `api.GET('/clients/{clientId}/overview', { params: { path: { clientId } } })` with the literal contract path -
  the maps and the graph join on that string, so never build paths with template literals.
- Every `/session/**` call needs the header `X-Harbor-Session`; the contract declares it required, so the generated types
  demand it. Hooks pass `params: { header: sessionHeader(), ... }` with `sessionHeader()` from `src/api/client.ts`, which
  reads the id from `sessionStore`. Components never set the header; there is no middleware.

## Conventions the generators rely on
- Feature folder: `src/features/<name>/{index.ts, <name>.types.ts, api/use*.ts, ui/*.tsx}`; cross-feature imports only via the barrel.
- `index.ts` starts with a JSDoc block `/** @module <name> ... @docs <ID> */` (e.g. `@module product1`, `@docs P1-001`) - `codebase-map.md` reads it.
- `<name>.types.ts` holds the feature's exported types (mirrors of contract schemas), tagged `@docs <ID>` -> `types-index.md`.
- Routes are object routes in `src/app/routes.tsx` / `src/app/AdminRoutes.tsx` written as `{ path: '...', element: <Page /> }`
  with `path:` before `element:` -> `routes.md`.
- Data fetching only in `api/use*.ts` hooks (react-query); components receive props. Charts: pure `compute*.ts` + rendering component.
- Files <= 300 lines, components <= 150 lines, one component per file (`scripts/check-file-size.ps1 -MaxLines 300`).
- No real client data in fixtures or mocks; synthetic values only.

## Commands
- `pwsh scripts/docs/gen-all.ps1` regenerates `docs/_generated/*`; `-Check` fails if stale (CI gate). Run after changing routes,
  barrels, types or `@docs` tags and commit the maps.
- `pwsh scripts/check-file-size.ps1 -Root . -MaxLines 300 -Include *.ts,*.tsx -Baseline .filesize-baseline.txt`
- `npm run generate:api` (regenerate the client from the backend contract), `npm test`, `npm run build`.

## Where business rules live
Not here. Feature specs are in the docs repo (`harbor-docs/features/<context>/<ID>.md`, e.g. `P1-001`, `STR-001`), formulas in
`harbor-docs/domain/calculations/<id>.md` (e.g. `monthly_projection`). The frontend displays backend results; it never recomputes
them. Resolve an ID via `docs/_generated/docs-tags.md` and cite it in answers, JSDoc and commit messages.
