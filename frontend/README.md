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
`presentation` is FE-only (spec `PRS-001`): the client-facing second window, see below.

## API client and session header

`src/api/client.ts` exports `api = createClient<paths>({ baseUrl: '/api/v1' })` (openapi-fetch) and `sessionHeader()`,
which returns `{ 'X-Harbor-Session': <sessionId> }` from `src/api/sessionStore.ts` (zustand). The contract marks the header
as required on every `/session/**` operation, so each session-scoped hook passes `params: { header: sessionHeader(), ... }`
and the typecheck fails if one forgets. `SessionLayout` writes the session from `/session/:sessionId/*` into the store and
clears it on leave. Only the PDF download (`/sessions/{sessionId}/report.pdf`) uses plain `fetch` and sets the header itself.

## Routes (`src/app/routes.tsx`, admin in `src/app/AdminRoutes.tsx`)

| Path | Page | Feature |
|---|---|---|
| `/clients` | `ClientSearchPage` | clients |
| `/clients/:clientId` | `ClientOverviewPage` | clients |
| `/meetings` | redirect to `/meetings/client` | meetings |
| `/meetings/client` | `ClientMeetingsPage` (kind CLIENT, shared `MeetingsListPage`) | meetings |
| `/meetings/preparation` | `PreparationSessionsPage` (kind PREPARATION, shared `MeetingsListPage`) | meetings |
| `/session/:sessionId/product1` | `Product1OverviewPage` | product1 |
| `/session/:sessionId/product2` | `Product2OverviewPage` | product2 |
| `/session/:sessionId/scenarios` | `ScenariosPage` | market |
| `/session/:sessionId/stress-test` | `StressTestPage` | stress |
| `/session/:sessionId/summary` | `SessionSummaryPage` | meetings |
| `/admin/parameters` | `ParametersPage` | admin |
| `/admin/imports` | `ImportsPage` | admin |
| `/present/:sessionId` | `PresentationPage` under `PresentationLayout` (outside `RootLayout`) | presentation |

## Presentation window and session channel (`src/features/presentation`)

During a CLIENT session the representative clicks "Open client screen" in `SessionLayout`; it opens
`/present/<sessionId>` in a second window (`noopener`). That window renders `PresentationLayout` (header with client
name and product group, no navigation, no admin links) and `PresentationPage`, a read-only mirror of the current step
built from the same presentational components and query hooks (`ProjectionTables`, `CoverRatioChart`, scenario list,
`TransportPriceChart`, `StressTable`). It never shows modals, the cover quote panel, role override, close session or
"Run stress test"; routes without a client counterpart (summary, client search) show "Waiting for the representative".

Both windows talk over a `BroadcastChannel` named `harbor.session.<sessionId>`. All channel code is in
`src/features/presentation/channel.ts` (`sessionChannelName`, `usePresentationPublisher`, `usePresentationSubscriber`);
no other module may open a channel. Messages (`PresentationMessage`): `route` (published by `SessionLayout` on every
navigation inside `/session/:sessionId/*`), `view` (city from `Product1OverviewPage`, transport mode from
`Product2OverviewPage`, stress dimension from `StressTestPage`), `session-closed` (from `useCloseSession`), and `hello`
(sent by a new subscriber; publishers replay their last messages so a late-opened window catches up).
The presentation window has its own session store, initialised from the route param via `useSession`.
