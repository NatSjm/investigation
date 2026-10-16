---
type: Document
title: "Codebase map (FE)"
description: "Generated map: Codebase map (FE), derived from src/pages/<Page>/ + src/routing, src/components/layout; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Codebase map (FE)

> Generated from `src/pages/<Page>/ + src/routing, src/components/layout` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
One row per page folder: read the page component (entry) and its hooks first; open components only for UI-level questions. `shared` hold pieces shared by several pages; `fe-app` is the app shell.
Channels = browser `BroadcastChannel`s (`defines` / `pub` / `sub`), the FE counterpart of Kafka topics; the shared component library is in `components.md`.

| Page | Purpose | Entry | Files | Components | Hooks | API calls | Channels |
|---|---|---|---|---|---|---|---|
| `ClientMeetingsPage` | `/meetings/client` - sessions of kind `CLIENT` (real meetings), with status filter and PDF download for closed ones. | `src/pages/ClientMeetingsPage/ClientMeetingsPage.tsx` | 1 |  |  |  |  |
| `ClientOverviewPage` | `/clients/:clientId` - client info panel plus one card per product group. | `src/pages/ClientOverviewPage/ClientOverviewPage.tsx` | 8 | ClientInfoPanel, ProductGroupCard | useClientOverview, useClientRole, useCreateSession | /clients/{clientId}/overview<br>/clients/{clientId}/role<br>/clients/{clientId}/sessions |  |
| `ClientSearchPage` | `/clients` - search box backed by the client registry; results link to the overview page. | `src/pages/ClientSearchPage/ClientSearchPage.tsx` | 2 |  | useClientSearch | /clients<br>/clients/{clientId} |  |
| `ImportsPage` | `/admin/imports` - monitor of the daily XLS movement imports with a manual trigger. | `src/pages/ImportsPage/ImportsPage.tsx` | 2 |  | useImportBatches | /admin/imports<br>/admin/imports/run |  |
| `ParametersPage` | `/admin/parameters` - parameter sets with product group filter and inline editing. | `src/pages/ParametersPage/ParametersPage.tsx` | 4 | ParameterRow | useParameters | /admin/parameters<br>/admin/parameters/{key} |  |
| `PreparationSessionsPage` | `/meetings/preparation` - sessions of kind `PREPARATION` (dry runs by the representative), same list and actions. | `src/pages/PreparationSessionsPage/PreparationSessionsPage.tsx` | 1 |  |  |  |  |
| `PresentationPage` | `/present/:sessionId` - what the client sees on the second screen. | `src/pages/PresentationPage/PresentationPage.tsx` | 7 | ProductMirror, ScenariosMirror, StressMirror |  |  | sub harbor.session.{*} |
| `Product1OverviewPage` | `/session/:sessionId/product1` - first meeting step for Product 1: city filter, the four projection tables, cover ratio chart, cover quote panel and the two input modals. | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx` | 6 | CitySelector | usePeerSimulation1, useProduct1Movements, useProduct1Overview | /session/product1/movements<br>/session/product1/overview<br>/session/product1/peer-simulation<br>/session/product1/projection | pub harbor.session.{*} |
| `Product2OverviewPage` | `/session/:sessionId/product2` - first meeting step for Product 2: transport mode filter, the four projection tables, cover ratio chart, cover quote panel and the two input modals. | `src/pages/Product2OverviewPage/Product2OverviewPage.tsx` | 6 | TransportModeSelector | usePeerSimulation2, useProduct2Movements, useProduct2Overview | /session/product2/movements<br>/session/product2/overview<br>/session/product2/peer-simulation<br>/session/product2/projection | pub harbor.session.{*} |
| `ScenariosPage` | `/session/:sessionId/scenarios` - second meeting step: list of scenarios of the session, baseline curve info and the editor to add / change / remove scenarios. | `src/pages/ScenariosPage/ScenariosPage.tsx` | 6 | ScenarioEditor, ShockRow | useScenarios | /session/scenarios<br>/session/scenarios/{scenarioId} |  |
| `SessionSummaryPage` | `/session/:sessionId/summary` - last meeting step: role override, close the session, preview the report payload and download the rendered PDF. | `src/pages/SessionSummaryPage/SessionSummaryPage.tsx` | 5 | RoleOverrideDialog | useCloseSession, useRoleOverride | /sessions/{sessionId}/close<br>/sessions/{sessionId}/role | pub harbor.session.{*} |
| `shared` | pieces shared by several pages | `src/pages/shared` | 22 | CoverQuotePanel, CoverRatioChart, DownloadPdfButton, MeetingsListPage, MovementInputModal, PeerSimulationModal, ProjectionTables, ReportPreview | useBaselinePrices, useCoverQuote, useCoverSummary, useDownloadReportPdf, useReport, useSessions | /api/v1/sessions/{*}/report.pdf<br>/clients/{clientId}/cover-policies<br>/session/cover/quotes<br>/session/cover/summary<br>/session/market/baseline<br>/sessions<br>/sessions/{sessionId}<br>/sessions/{sessionId}/report |  |
| `StressTestPage` | `/session/:sessionId/stress-test` - third meeting step: one monthly table per scenario, transport price chart per scenario and the dimension toggle (city / transport mode). | `src/pages/StressTestPage/StressTestPage.tsx` | 9 | DimensionToggle, StressTable, TransportPriceChart | useRunStressTest, useStressTest | /session/stress-test | pub harbor.session.{*} |
| `fe-app` | app shell: routing, layouts, providers, channel modules | `src/App.tsx` | 13 | AdminRoutesGuard, App, PresentationLayout, RootLayout, Routing, SessionLayout, SessionRoutes | usePresentationPublisher, usePresentationSubscriber |  | pub harbor.session.{*}<br>defines harbor.session.{*} (src/components/broadcast/sessionChannel.ts) |
