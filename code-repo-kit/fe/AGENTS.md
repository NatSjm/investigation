# AGENTS.md - harbor-frontend (React 18 / TypeScript / react-router / openapi-fetch)

Read by Copilot Chat (VS Code, JetBrains), Copilot CLI, the Copilot coding agent and other agent tools.
Copilot-specific extras are in `.github/copilot-instructions.md`; path-scoped rules in `.github/instructions/`.

## What this repository is
Web client of the Harbor platform. Account representatives search clients, start a **meeting session**, work through the
product overview pages (projection tables, cover charts, movement and peer-simulation modals), market scenarios and the
stress test, and download the meeting report. One folder per routed page under `src/pages/<Page>/`; the docs repo
`contexts.yml` lists which pages belong to which bounded context (`fe` list) and which BE class-name prefixes do:
`clients`, `meetings`, `product1`, `product2`, `cover`, `market`, `stress`, `reports`, `admin`.
`presentation` (FE-only, `PRS-001`) is the client-facing window `/present/:sessionId`; all cross-window sync goes through
the single `BroadcastChannel` module `src/components/broadcast/sessionChannel.ts` and the hooks in `src/components/hook/`
(`route` / `view` / `session-closed` messages).

## Read in this order (cheapest first) - never walk `src/`
1. `docs/_generated/index.md`, then the map that answers the question: `codebase-map.md` (pages, hooks, components, API calls),
   `routes.md` (URL -> page), `components.md` (shared UI), `types-index.md` (exported types), `docs-tags.md` (spec ID -> code).
2. The page component `src/pages/<Page>/<Page>.tsx` (its JSDoc names the route and the spec) and `src/types/<context>.ts`.
3. One hook under `src/pages/<Page>/hook/` or one component. Max 3 source files per question.
4. For "which backend endpoint / which screens are affected" use the docs repo `generated/graph/<context>.md`.

## Contracts (source of truth)
- The backend `core/src/main/resources/openapi/harbor-api.yaml` is the REST contract. `src/services/openapi/schema.d.ts` is **generated** from it
  (`npm run generate:api`); never edit it, never read it. `src/services/api/client.ts` exports the typed `api` client (base URL `/api/v1`).
- Hooks call `api.GET('/clients/{clientId}/overview', { params: { path: { clientId } } })` with the literal contract path -
  the maps and the graph join on that string, so never build paths with template literals.
- Every `/session/**` call needs the header `X-Harbor-Session`; the contract declares it required, so the generated types
  demand it. Hooks pass `params: { header: sessionHeader(), ... }` with `sessionHeader()` from `src/services/api/client.ts`, which
  reads the id from `sessionStore`. Components never set the header; there is no middleware.

## Conventions the generators rely on (layout in `scripts/docs/docs-gen.json`)
- Page folder: `src/pages/<Page>/{<Page>.tsx, hook/use*.ts, components/<Name>/{index.ts, <Name>.tsx, <Name>.test.tsx}}`;
  pieces shared by pages in `src/pages/shared/{components,hook}/`; generic UI in `src/components/<Name>/`.
- `<Page>.tsx` carries a JSDoc block whose first sentence is the purpose and which ends with `@docs <ID>` (e.g. `@docs P1-001`)
  - `codebase-map.md` and `docs-tags.md` read it. Hooks and types files carry `@docs <ID>` too.
- Types in `src/types/<context>.ts` (mirrors of contract schemas) and `<Page>/types.ts` -> `types-index.md`.
- Routes are object routes in `src/routing/Routing.tsx` / `SessionRoutes.tsx` (`useRoutes`) written as
  `{ path: ROUTES.X, Component: XPage }` or `{ path: ROUTES.X, element: <X /> }`, constants in `src/constants/routes.ts`,
  nested `children` with relative paths -> `routes.md` (joined paths, layouts).
- Data fetching only in `hook/use*.ts` (react-query); components receive props. Charts: pure `compute*.ts` + rendering component.
- Files <= 300 lines, components <= 150 lines, one component per file (`scripts/check-file-size.py --max-lines 300`).
- No real client data in fixtures or mocks; synthetic values only.

## Commands
- `python3 scripts/docs/gen-all.py` regenerates `docs/_generated/*`; `--check` fails if stale (CI gate). Run after changing routes,
  pages, hooks, types or `@docs` tags and commit the maps.
- `python3 scripts/check-file-size.py --root . --max-lines 300 --include *.ts,*.tsx --baseline .filesize-baseline.txt`
- `npm run generate:api` (regenerate the client from the backend contract), `npm test`, `npm run build`.

## Where business rules live
Not here. Feature specs are in the docs repo (`harbor-docs/features/<context>/<ID>.md`, e.g. `P1-001`, `STR-001`), formulas in
`harbor-docs/domain/calculations/<id>.md` (e.g. `monthly_projection`). The frontend displays backend results; it never recomputes
them. Resolve an ID via `docs/_generated/docs-tags.md` and cite it in answers, JSDoc and commit messages.
