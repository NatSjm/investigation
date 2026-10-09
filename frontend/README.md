# harbor-frontend

React 18 / TypeScript single-page application for Harbor account representatives: find a client, open a
meeting session for a product group, review the monthly projection tables and cover position, define market
scenarios, run the stress test and close the meeting with a PDF report. Administration (parameters, import
batches) lives outside meetings. The backend contract is `backend/core/src/main/resources/openapi/harbor-api.yaml` (served under `/api/v1`).

## Scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Vite dev server on :5173, proxies `/api` to the backend on :8080 |
| `npm run build` | Type-check and production build |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run test` | Vitest (unit tests next to the code: `*.test.ts(x)`) |
| `npm run generate:api` | Regenerate `src/api/generated/schema.d.ts` from the backend OpenAPI contract |

## Feature folder convention (`src/features/<feature>/`)

- `index.ts` - the barrel and only public surface; starts with `/** @module <feature> ... @docs <SPEC-ID> */`.
- `<feature>.types.ts` - view-model types mirroring the backend DTOs (derived from `components['schemas']`).
- `api/use*.ts` - TanStack Query hooks; the only place that calls the API, always with the literal path string
  (`api.GET('/clients/{clientId}/overview', ...)`) so the generated docs and the graph can join on it.
- `ui/*.tsx` - components and pages; they receive data via props or the feature's hooks, never fetch themselves.

Features map 1:1 to backend modules: `clients`, `meetings`, `product1`, `product2`, `market`, `stress`,
`reports`, `admin`, `cover`. `product2` deliberately imports the projection tables, chart and modals from `product1`.

## API client and session header

`src/api/client.ts` exports `api = createClient<paths>({ baseUrl: '/api/v1' })` (openapi-fetch). A middleware adds
`X-Harbor-Session: <sessionId>` from `src/api/sessionStore.ts` (zustand) to every request whose URL contains
`/session/`. `SessionLayout` writes the session from `/session/:sessionId/*` into the store and clears it on leave.
Only the PDF download (`/sessions/{sessionId}/report.pdf`) uses plain `fetch` and sets the header itself.

## Routes (`src/app/routes.tsx`, admin in `src/app/AdminRoutes.tsx`)

| Path | Page | Feature |
|---|---|---|
| `/clients` | `ClientSearchPage` | clients |
| `/clients/:clientId` | `ClientOverviewPage` | clients |
| `/meetings` | `MeetingsListPage` | meetings |
| `/session/:sessionId/product1` | `Product1OverviewPage` | product1 |
| `/session/:sessionId/product2` | `Product2OverviewPage` | product2 |
| `/session/:sessionId/scenarios` | `ScenariosPage` | market |
| `/session/:sessionId/stress-test` | `StressTestPage` | stress |
| `/session/:sessionId/summary` | `SessionSummaryPage` | meetings |
| `/admin/parameters` | `ParametersPage` | admin |
| `/admin/imports` | `ImportsPage` | admin |
