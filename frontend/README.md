# harbor-frontend

React 18 / TypeScript single-page application for Harbor account representatives: find a client, open a
meeting session for a product group, review the monthly projection tables and cover position, define market
scenarios, run the stress test and close the meeting with a PDF report. Administration (parameters, import
batches) lives outside meetings. The backend contract is `backend/harbor-core/src/main/resources/openapi/harbor-api.yaml` (served under `/api/v1`).

## Scripts

| Script | Purpose |
|---|---|
| `npm run dev` | Vite dev server on :5173, proxies `/api` to the backend on :8080 |
| `npm run build` | Type-check and production build |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run test` | Vitest (unit tests next to the code: `*.test.ts(x)`) |
| `npm run generate:api` | Regenerate `src/services/openapi/schema.d.ts` from the backend OpenAPI contract |
| `python3 scripts/docs/gen-all.py [--check]` | Regenerate (or verify) the code maps in `docs/_generated/`; layout in `scripts/docs/docs-gen.json` |

## Source layout (`src/`)

| Folder | Holds |
|---|---|
| `pages/<Page>/` | one folder per routed page: `<Page>.tsx` (JSDoc with the route, one sentence of purpose and `@docs <SPEC-ID>`), `hook/use*.ts` (TanStack Query hooks, the only place that calls the API), `components/<Name>/{index.ts, <Name>.tsx, <Name>.test.tsx}` |
| `pages/shared/` | `components/` and `hook/` used by several pages (projection tables, modals, cover panel, report preview, session and baseline hooks) |
| `components/` | generic UI (`DataTable`, `Modal`, `LineChart`, `StackedBars`), `layout/` (root, session and presentation layouts), `broadcast/` (the one `BroadcastChannel` module) and `hook/` (its publisher / subscriber hooks) |
| `routing/` | `Routing.tsx` (`useRoutes`), `SessionRoutes.tsx` (meeting steps under `/session/:sessionId`), `AdminRoutesGuard.tsx` |
| `constants/routes.ts` | `ROUTES` and `SESSION_STEPS` path constants used by the routing files |
| `services/api/` | `client.ts` (typed openapi-fetch client, `sessionHeader()`), `sessionStore.ts` (zustand) |
| `services/openapi/` | generated client types (`schema.d.ts`), never edited, never read by the generators |
| `types/<context>.ts` | view-model types mirroring the backend DTOs (derived from `components['schemas']`), tagged `@docs` |
| `utils/` | formatting and month-grid helpers |

Hooks always call the API with the literal path string (`api.GET('/clients/{clientId}/overview', ...)`) so the generated
docs and the graph can join on it; components receive data via props and never fetch. Which pages belong to which bounded
context is declared in the docs repo `contexts.yml` (`fe` list): `clients`, `meetings`, `product1`, `product2`, `market`,
`stress`, `admin`, `presentation`; `cover` and `reports` have no page of their own (their pieces live under `pages/shared/`).
`Product2OverviewPage` deliberately reuses the projection tables, chart and modals from `pages/shared/`.

## API client and session header

`src/services/api/client.ts` exports `api = createClient<paths>({ baseUrl: '/api/v1' })` (openapi-fetch) and `sessionHeader()`,
which returns `{ 'X-Harbor-Session': <sessionId> }` from `src/services/api/sessionStore.ts` (zustand). The contract marks the header
as required on every `/session/**` operation, so each session-scoped hook passes `params: { header: sessionHeader(), ... }`
and the typecheck fails if one forgets. `SessionLayout` writes the session from `/session/:sessionId/*` into the store and
clears it on leave. Only the PDF download (`/sessions/{sessionId}/report.pdf`) uses plain `fetch` and sets the header itself.

## Routes (`src/routing/Routing.tsx`, meeting steps in `src/routing/SessionRoutes.tsx`)

| Path | Page | Context |
|---|---|---|
| `/clients` | `ClientSearchPage` | clients |
| `/clients/:clientId` | `ClientOverviewPage` | clients |
| `/meetings` | redirect to `/meetings/client` | meetings |
| `/meetings/client` | `ClientMeetingsPage` (kind CLIENT, shared `MeetingsListPage`) | meetings |
| `/meetings/preparation` | `PreparationSessionsPage` (kind PREPARATION, shared `MeetingsListPage`) | meetings |
| `/session/:sessionId/product1` | `Product1OverviewPage` (relative child `product1` of `SessionLayout`) | product1 |
| `/session/:sessionId/product2` | `Product2OverviewPage` | product2 |
| `/session/:sessionId/scenarios` | `ScenariosPage` | market |
| `/session/:sessionId/stress-test` | `StressTestPage` | stress |
| `/session/:sessionId/summary` | `SessionSummaryPage` | meetings |
| `/admin/parameters` | `ParametersPage` (under `AdminRoutesGuard`) | admin |
| `/admin/imports` | `ImportsPage` (under `AdminRoutesGuard`) | admin |
| `/present/:sessionId` | `PresentationPage` under `PresentationLayout` (outside `RootLayout`) | presentation |

## Presentation window and session channel (`src/components/broadcast`, `src/components/hook`)

During a CLIENT session the representative clicks "Open client screen" in `SessionLayout`; it opens
`/present/<sessionId>` in a second window (`noopener`). That window renders `PresentationLayout` (header with client
name and product group, no navigation, no admin links) and `PresentationPage`, a read-only mirror of the current step
built from the same presentational components and query hooks (`ProjectionTables`, `CoverRatioChart`, scenario list,
`TransportPriceChart`, `StressTable`). It never shows modals, the cover quote panel, role override, close session or
"Run stress test"; routes without a client counterpart (summary, client search) show "Waiting for the representative".

Both windows talk over a `BroadcastChannel` named `harbor.session.<sessionId>`. The channel itself is opened only in
`src/components/broadcast/sessionChannel.ts` (`sessionChannelName`, `openSessionChannel`, the `PresentationMessage` union);
the hooks `usePresentationPublisher` and `usePresentationSubscriber` in `src/components/hook/` are the only callers.
Messages: `route` (published by `SessionLayout` on every navigation inside `/session/:sessionId/*`), `view` (city from
`Product1OverviewPage`, transport mode from `Product2OverviewPage`, stress dimension from `StressTestPage`),
`session-closed` (from `useCloseSession`), and `hello` (sent by a new subscriber; publishers replay their last messages so
a late-opened window catches up). The presentation window has its own session store, initialised from the route param via `useSession`.
