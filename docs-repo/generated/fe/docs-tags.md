---
type: Document
title: "Spec-to-code traceability (@docs tags)"
description: "Generated map: Spec-to-code traceability (@docs tags), derived from @docs <ID> tags in KDoc/JSDoc; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Spec-to-code traceability (@docs tags)

> Generated from `@docs <ID> tags in KDoc/JSDoc` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
71 tag(s). Resolve a spec/calculation ID here, then open only the listed location.

| Spec ID | Declaration | Summary | Location |
|---|---|---|---|
| `ADM-001` | `export function useImportBatches()` | Import batch monitor (`listImportBatches`): daily XLS runs of the file-exchange import. | `src/pages/ImportsPage/hook/useImportBatches.ts:10` |
| `ADM-001` | `export function useTriggerImport()` | Starts an import run outside the nightly schedule (`triggerImport`). | `src/pages/ImportsPage/hook/useImportBatches.ts:22` |
| `ADM-001` | `export function ImportsPage()` | `/admin/imports` - monitor of the daily XLS movement imports with a manual trigger. | `src/pages/ImportsPage/ImportsPage.tsx:22` |
| `ADM-001` | `export function useUpsertParameter()` | Creates or updates one parameter by key (`upsertParameter`); scope fields select the row. | `src/pages/ParametersPage/hook/useParameters.ts:20` |
| `ADM-001` | `export function useParameters(productGroup?: ProductGroup)` | Parameter sets (`listParameters`), optionally filtered by product group. | `src/pages/ParametersPage/hook/useParameters.ts:9` |
| `ADM-001` | `export function ParametersPage()` | `/admin/parameters` - parameter sets with product group filter and inline editing. | `src/pages/ParametersPage/ParametersPage.tsx:9` |
| `ADM-001` | `export function AdminRoutesGuard()` | Set by the deployment (window-level flag) until roles arrive with the session; admin pages stay hidden otherwise. */ | `src/routing/AdminRoutesGuard.tsx:16` |
| `ADM-001` | `export type Parameter` | View-model types for administration. Aliases of `Parameter`, `ParameterUpsert` and `ImportBatch` from the contract | `src/types/admin.ts:11` |
| `CLI-001` | `export function ClientOverviewPage()` | `/clients/:clientId` - client info panel plus one card per product group. | `src/pages/ClientOverviewPage/ClientOverviewPage.tsx:18` |
| `CLI-001` | `export function useClientOverview(clientId: string)` | Client overview (`getClientOverview`): per product group the last-12-month volume and value, | `src/pages/ClientOverviewPage/hook/useClientOverview.ts:10` |
| `CLI-001` | `export function useClientRole(clientId: string, productGroup: ProductGroup)` | Role classification (`getClientRole`): algorithm result (`client_role_classification`, | `src/pages/ClientOverviewPage/hook/useClientRole.ts:10` |
| `CLI-001` | `export function ClientSearchPage()` | `/clients` - search box backed by the client registry; results link to the overview page. | `src/pages/ClientSearchPage/ClientSearchPage.tsx:17` |
| `CLI-001` | `export function useClientSearch(q: string)` | Client search (`searchClients`): proxies the client registry and merges the local profile. | `src/pages/ClientSearchPage/hook/useClientSearch.ts:10` |
| `CLI-001` | `export function useClient(clientId: string)` | Single client profile (`getClient`). | `src/pages/ClientSearchPage/hook/useClientSearch.ts:24` |
| `CLI-001` | `export type Client` | View-model types for the clients feature. Aliases of the contract schemas behind `searchClients`, `getClient`, | `src/types/clients.ts:17` |
| `COV-001` | `export function CoverQuotePanel(` | Suffix for monetary values; omitted while the contract does not provide a price basis. */ | `src/pages/shared/components/CoverQuotePanel/CoverQuotePanel.tsx:19` |
| `COV-001` | `export function useCoverQuote()` | Requests a quote for the uncovered value from the external cover provider (`requestCoverQuote`); | `src/pages/shared/hook/useCoverQuote.ts:11` |
| `COV-001` | `export function useCoverSummary()` | Cover ratio per month per sub-product for the current session (`getCoverSummary`). | `src/pages/shared/hook/useCoverSummary.ts:10` |
| `COV-001` | `export function useCoverPolicies(clientId: string)` | Cover policies of a client across product groups (`listCoverPolicies`). | `src/pages/shared/hook/useCoverSummary.ts:23` |
| `COV-001` | `export type CoverSummaryRow` | View-model types for cover. Aliases of `CoverSummary`, `CoverMonth`, `CoverQuoteRequest`, `CoverQuote`, `CoverPolicy` | `src/types/cover.ts:13` |
| `MKT-001` | `export function useScenarios()` | Scenarios of the current session (`listScenarios`). | `src/pages/ScenariosPage/hook/useScenarios.ts:10` |
| `MKT-001` | `export function useScenarioMutations()` | Create / update / delete scenarios (`createScenario`, `updateScenario`, `deleteScenario`). | `src/pages/ScenariosPage/hook/useScenarios.ts:24` |
| `MKT-001` | `export function ScenariosPage()` | `/session/:sessionId/scenarios` - second meeting step: list of scenarios of the session, | `src/pages/ScenariosPage/ScenariosPage.tsx:17` |
| `MKT-001` | `export function useBaselinePrices()` | Baseline price and transport price curve for the session's corridor (`getBaselinePrices`), | `src/pages/shared/hook/useBaselinePrices.ts:11` |
| `MKT-001` | `export type Shock` | View-model types for market scenarios. Aliases of `Scenario`, `ScenarioInput`, `Shock` and `BaselinePrices` | `src/types/market.ts:11` |
| `P1-001` | `export function useProduct1Overview(city?: string)` | Product 1 overview (`getProduct1Overview`): the four projection tables filtered by city hub | `src/pages/Product1OverviewPage/hook/useProduct1Overview.ts:11` |
| `P1-001` | `export function useProduct1Projection()` | Product 1 projection only (`getProduct1Projection`): the four tables without chart series, | `src/pages/Product1OverviewPage/hook/useProduct1Overview.ts:26` |
| `P1-001` | `export function Product1OverviewPage()` | `/session/:sessionId/product1` - first meeting step for Product 1: city filter, the four | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx:25` |
| `P1-001` | `export function CoverRatioChart(` | Flat `CoverSeriesPoint[]` from the overview (one point per period x sub-product). */ | `src/pages/shared/components/CoverRatioChart/CoverRatioChart.tsx:18` |
| `P1-001` | `export function ProjectionTables(` | The four cumulative tables of the monthly projection: by sub-product, by dimension | `src/pages/shared/components/ProjectionTables/ProjectionTables.tsx:70` |
| `P1-001` | `export type ProjectionRow` | View-model types for Product 1 (also consumed by `product2`, which shares the projection shape). | `src/types/product1.ts:18` |
| `P1-002` | `export function useProduct1Movements()` | Modelled movements per month for Product 1 (`putProduct1Movements`, modal 1). | `src/pages/Product1OverviewPage/hook/useProduct1Movements.ts:11` |
| `P1-002` | `export function MovementInputModal(` | Projection grid of the session (`projectionGrid(horizon)`): the months the backend accepts. */ | `src/pages/shared/components/MovementInputModal/MovementInputModal.tsx:30` |
| `P1-003` | `export function usePeerSimulation1()` | Peer simulation for Product 1 (`postProduct1PeerSimulation`, modal 2): monthly series of | `src/pages/Product1OverviewPage/hook/usePeerSimulation1.ts:11` |
| `P1-003` | `export function PeerSimulationModal(` | Modal 2: movements of similar products at peer firms. Picks a peer segment and a scaling | `src/pages/shared/components/PeerSimulationModal/PeerSimulationModal.tsx:22` |
| `P2-001` | `export function useProduct2Overview(transportMode?: TransportMode)` | Product 2 overview (`getProduct2Overview`): four projection tables filtered by transport mode | `src/pages/Product2OverviewPage/hook/useProduct2Overview.ts:12` |
| `P2-001` | `export function useProduct2Projection()` | Product 2 projection only (`getProduct2Projection`). | `src/pages/Product2OverviewPage/hook/useProduct2Overview.ts:30` |
| `P2-001` | `export function Product2OverviewPage()` | `/session/:sessionId/product2` - first meeting step for Product 2: transport mode filter, | `src/pages/Product2OverviewPage/Product2OverviewPage.tsx:25` |
| `P2-001` | `export type Product2Overview` | View-model types for Product 2. The projection shape is identical to Product 1 | `src/types/product2.ts:15` |
| `P2-002` | `export function useProduct2Movements()` | Modelled movements per month for Product 2 (`putProduct2Movements`, modal 1). | `src/pages/Product2OverviewPage/hook/useProduct2Movements.ts:11` |
| `P2-003` | `export function usePeerSimulation2()` | Peer simulation for Product 2 (`postProduct2PeerSimulation`, modal 2). | `src/pages/Product2OverviewPage/hook/usePeerSimulation2.ts:10` |
| `PRS-001` | `export const SESSION_CHANNEL_PREFIX` | Cross-window synchronisation between the representative's session window and the client-facing | `src/components/broadcast/sessionChannel.ts:12` |
| `PRS-001` | `export function usePresentationPublisher(sessionId: string): (message: PresentationMessage)` | Representative side of the session channel. Returns `publish(message)`; the channel is opened once per | `src/components/hook/usePresentationPublisher.ts:15` |
| `PRS-001` | `export function usePresentationSubscriber(sessionId: string, onMessage: (message: PresentationMessage)` | Client-screen side of the session channel. Subscribes, announces itself with `hello` and hands every | `src/components/hook/usePresentationSubscriber.ts:9` |
| `PRS-001` | `export function PresentationLayout()` | Minimal layout for the client-facing window `/present/:sessionId`: no main navigation, no admin links, | `src/components/layout/PresentationLayout.tsx:13` |
| `PRS-001` | `export function ProductMirror(` | City (Product 1) or transport mode (Product 2) as published by the representative; unknown values mean "all". */ | `src/pages/PresentationPage/components/ProductMirror/ProductMirror.tsx:24` |
| `PRS-001` | `export function ScenariosMirror()` | Read-only mirror of the scenarios step: baseline info and the scenario list with their shocks. | `src/pages/PresentationPage/components/ScenariosMirror/ScenariosMirror.tsx:10` |
| `PRS-001` | `export function StressMirror(` | Read-only mirror of the stress test step for the dimension the representative selected: | `src/pages/PresentationPage/components/StressMirror/StressMirror.tsx:17` |
| `PRS-001` | `export function PresentationPage()` | `/present/:sessionId` - what the client sees on the second screen. Follows the representative's | `src/pages/PresentationPage/PresentationPage.tsx:21` |
| `PRS-001` | `export type PresentationStep` | View-model types for the client-facing presentation window. FE-only: the screen mirrors the | `src/types/presentation.ts:9` |
| `RPT-001` | `export function DownloadPdfButton(` | "Download PDF" button for a closed session (Meetings list, session summary). | `src/pages/shared/components/DownloadPdfButton/DownloadPdfButton.tsx:12` |
| `RPT-001` | `export function ReportPreview(` | Read-only view of the report payload grouped by known sections, with a regenerate action. | `src/pages/shared/components/ReportPreview/ReportPreview.tsx:19` |
| `RPT-001` | `export function useDownloadReportPdf()` | Downloads the rendered PDF (`downloadReportPdf`, `application/pdf`). Uses plain `fetch` because the | `src/pages/shared/hook/useDownloadReportPdf.ts:10` |
| `RPT-001` | `export function useReport(sessionId: string, enabled` | Report payload of a closed session (`getReport`). Polls while the PDF is still being rendered | `src/pages/shared/hook/useReport.ts:12` |
| `RPT-001` | `export function useRegenerateReport(sessionId: string)` | Requests a fresh render of the report (`regenerateReport`), e.g. after a failed document-service run. | `src/pages/shared/hook/useReport.ts:28` |
| `RPT-001` | `export type Report` | View-model types for meeting reports. Alias of `Report` from the contract | `src/types/reports.ts:9` |
| `SES-001` | `export function ClientMeetingsPage()` | `/meetings/client` - sessions of kind `CLIENT` (real meetings), with status filter and PDF download for closed ones. | `src/pages/ClientMeetingsPage/ClientMeetingsPage.tsx:7` |
| `SES-001` | `export function useCreateSession(clientId: string)` | Creates a meeting session for a client and product group (`createSession`). | `src/pages/ClientOverviewPage/hook/useCreateSession.ts:11` |
| `SES-001` | `export function PreparationSessionsPage()` | `/meetings/preparation` - sessions of kind `PREPARATION` (dry runs by the representative), same list and actions. | `src/pages/PreparationSessionsPage/PreparationSessionsPage.tsx:7` |
| `SES-001` | `export function useCloseSession(sessionId: string)` | Closes a meeting session (`closeSession`). The backend stores the report payload and emits | `src/pages/SessionSummaryPage/hook/useCloseSession.ts:12` |
| `SES-001` | `export function useRoleOverride(sessionId: string)` | Manual role override during a meeting (`setRoleOverride`): replaces the algorithm result | `src/pages/SessionSummaryPage/hook/useRoleOverride.ts:10` |
| `SES-001` | `export function SessionSummaryPage()` | `/session/:sessionId/summary` - last meeting step: role override, close the session, | `src/pages/SessionSummaryPage/SessionSummaryPage.tsx:16` |
| `SES-001` | `export function MeetingsListPage(` | Fixed session kind of the page (`ClientMeetingsPage`, `PreparationSessionsPage`); the kind filter is hidden then. */ | `src/pages/shared/components/MeetingsListPage/MeetingsListPage.tsx:44` |
| `SES-001` | `export function useSession(sessionId: string)` | One session by id (`getSession`); used by `SessionLayout` to populate the session store. | `src/pages/shared/hook/useSessions.ts:20` |
| `SES-001` | `export function useSessions(filter: SessionFilter` | Session list for the Meetings page (`listSessions`), filterable by client, status and kind. | `src/pages/shared/hook/useSessions.ts:9` |
| `SES-001` | `export const sessionRoutes: RouteObject` | Meeting steps under `/session/:sessionId`: `SessionLayout` syncs `:sessionId` into the session store and renders the | `src/routing/SessionRoutes.tsx:15` |
| `SES-001` | `export interface SessionFilter` | View-model types for meeting sessions. Aliases of `Session`, `CreateSessionRequest`, `SessionCreated` and | `src/types/meetings.ts:25` |
| `STR-001` | `export function useRunStressTest()` | Recomputes the stress test for all scenarios of the session (`runStressTest`, calculation | `src/pages/StressTestPage/hook/useRunStressTest.ts:11` |
| `STR-001` | `export function useStressTest(dimension: Dimension)` | Stress test results of the session (`getStressTest`) for one dimension (`CITY` \| `TRANSPORT_MODE`). | `src/pages/StressTestPage/hook/useStressTest.ts:11` |
| `STR-001` | `export function StressTestPage()` | `/session/:sessionId/stress-test` - third meeting step: one monthly table per scenario, | `src/pages/StressTestPage/StressTestPage.tsx:21` |
| `STR-001` | `export type Dimension` | View-model types for the stress test. Aliases of `StressTestResult`, `StressTestScenarioResult`, `StressTestRow` | `src/types/stress.ts:11` |
