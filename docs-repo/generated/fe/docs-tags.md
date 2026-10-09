---
type: Document
title: Spec-to-code traceability (@docs tags)
description: Generated map: Spec-to-code traceability (@docs tags), derived from @docs <ID> tags in KDoc/JSDoc; read instead of source files.
generated:
  by: process:gen-docs
  at: 2026-10-09
status: stable
---
# Spec-to-code traceability (@docs tags)

> Generated from `@docs <ID> tags in KDoc/JSDoc` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
50 tag(s). Resolve a spec/calculation ID here, then open only the listed location.

| Spec ID | Declaration | Summary | Location |
|---|---|---|---|
| `ADM-001` | `export interface Parameter` | View-model types for administration. Mirror `Parameter` and `ImportBatch` from the contract | `src/features/admin/admin.types.ts:11` |
| `ADM-001` | `export function useImportBatches()` | Import batch monitor (`listImportBatches`): daily XLS runs of the file-exchange import. | `src/features/admin/api/useImportBatches.ts:10` |
| `ADM-001` | `export function useTriggerImport()` | Starts an import run outside the nightly schedule (`triggerImport`). | `src/features/admin/api/useImportBatches.ts:22` |
| `ADM-001` | `export function useUpsertParameter()` | Creates or updates one parameter by key (`upsertParameter`); scope fields select the row. | `src/features/admin/api/useParameters.ts:20` |
| `ADM-001` | `export function useParameters(productGroup?: ProductGroup)` | Parameter sets (`listParameters`), optionally filtered by product group. | `src/features/admin/api/useParameters.ts:9` |
| `ADM-001` | `(module) index.ts` | Administration outside meetings: parameter sets with inline editing and the daily import batch monitor. | `src/features/admin/index.ts:6` |
| `CLI-001` | `export function useClientOverview(clientId: string)` | Client overview (`getClientOverview`): per product group the last-12-month volume and value, | `src/features/clients/api/useClientOverview.ts:10` |
| `CLI-001` | `export function useClientRole(clientId: string, productGroup: ProductGroup)` | Role classification (`getClientRole`): algorithm result (`client_role_classification`, | `src/features/clients/api/useClientRole.ts:10` |
| `CLI-001` | `export function useClientSearch(q: string)` | Client search (`searchClients`): proxies the client registry and merges the local profile. | `src/features/clients/api/useClientSearch.ts:10` |
| `CLI-001` | `export function useClient(clientId: string)` | Single client profile (`getClient`). | `src/features/clients/api/useClientSearch.ts:24` |
| `CLI-001` | `export const PRODUCT_GROUP_LABEL: Record<ProductGroup, string>` | View-model types for the clients feature. Mirror the backend DTOs (`getClient`, `getClientOverview`, | `src/features/clients/clients.types.ts:56` |
| `CLI-001` | `(module) index.ts` | Client search, client overview with product group cards (key indicators, sparklines, Start meeting / Prepare) and role classification. | `src/features/clients/index.ts:6` |
| `COV-001` | `export function useCoverQuote()` | Requests a quote for the uncovered value from the external cover provider (`requestCoverQuote`); | `src/features/cover/api/useCoverQuote.ts:11` |
| `COV-001` | `export function useCoverSummary()` | Cover ratio per month per sub-product for the current session (`getCoverSummary`). | `src/features/cover/api/useCoverSummary.ts:10` |
| `COV-001` | `export function useCoverPolicies(clientId: string)` | Cover policies of a client across product groups (`listCoverPolicies`). | `src/features/cover/api/useCoverSummary.ts:23` |
| `COV-001` | `export interface CoverSummaryRow` | View-model types for cover. Mirror `CoverSummary`, `CoverQuoteRequest`, `CoverQuote`, `CoverPolicy` | `src/features/cover/cover.types.ts:13` |
| `COV-001` | `(module) index.ts` | Cover position of a session: cover ratio per month and sub-product, and quotes for the uncovered part. | `src/features/cover/index.ts:6` |
| `MKT-001` | `export function useBaselinePrices()` | Baseline price and transport price curve for the session's corridor (`getBaselinePrices`), | `src/features/market/api/useBaselinePrices.ts:11` |
| `MKT-001` | `export function useScenarios()` | Scenarios of the current session (`listScenarios`). | `src/features/market/api/useScenarios.ts:10` |
| `MKT-001` | `export function useScenarioMutations()` | Create / update / delete scenarios (`createScenario`, `updateScenario`, `deleteScenario`). | `src/features/market/api/useScenarios.ts:24` |
| `MKT-001` | `(module) index.ts` | Market scenarios of a session: price and transport price shocks on top of the baseline curve, with live path preview. | `src/features/market/index.ts:6` |
| `MKT-001` | `export interface Shock` | View-model types for market scenarios. Mirror `Scenario`, `Shock` and `BaselinePrices` | `src/features/market/market.types.ts:13` |
| `MTG-001` | `export function useCloseSession(sessionId: string)` | Closes a meeting session (`closeSession`). The backend stores the report payload and emits | `src/features/meetings/api/useCloseSession.ts:10` |
| `MTG-001` | `export function useCreateSession(clientId: string)` | Creates a meeting session for a client and product group (`createSession`). | `src/features/meetings/api/useCreateSession.ts:11` |
| `MTG-001` | `export function useRoleOverride(sessionId: string)` | Manual role override during a meeting (`setRoleOverride`): replaces the algorithm result | `src/features/meetings/api/useRoleOverride.ts:10` |
| `MTG-001` | `export function useSession(sessionId: string)` | One session by id (`getSession`); used by `SessionLayout` to populate the session store. | `src/features/meetings/api/useSessions.ts:20` |
| `MTG-001` | `export function useSessions(filter: SessionFilter` | Session list for the Meetings page (`listSessions`), filterable by client, status and kind. | `src/features/meetings/api/useSessions.ts:9` |
| `MTG-001` | `(module) index.ts` | Meeting session lifecycle: create CLIENT or PREPARATION sessions, list and close them, override the client role, show the session summary. | `src/features/meetings/index.ts:6` |
| `MTG-001` | `export interface SessionFilter` | View-model types for meeting sessions. Mirror `Session`, `CreateSessionRequest` and | `src/features/meetings/meetings.types.ts:47` |
| `P1-001` | `export function usePeerSimulation1()` | Peer simulation for Product 1 (`postProduct1PeerSimulation`, modal 2): monthly series of | `src/features/product1/api/usePeerSimulation1.ts:11` |
| `P1-001` | `export function useProduct1Movements()` | Modelled movements per month for Product 1 (`putProduct1Movements`, modal 1). | `src/features/product1/api/useProduct1Movements.ts:11` |
| `P1-001` | `export function useProduct1Overview(city?: string)` | Product 1 overview (`getProduct1Overview`): the four projection tables filtered by city hub | `src/features/product1/api/useProduct1Overview.ts:11` |
| `P1-001` | `export function useProduct1Projection()` | Product 1 projection only (`getProduct1Projection`): the four tables without chart series, | `src/features/product1/api/useProduct1Overview.ts:25` |
| `P1-001` | `(module) index.ts` | Product 1 overview per city hub: the four cumulative projection tables, cover ratio chart, movement input and peer simulation modals. | `src/features/product1/index.ts:6` |
| `P1-001` | `export interface ProjectionRow` | View-model types for Product 1 (also consumed by `product2`, which shares the projection shape). | `src/features/product1/product1.types.ts:17` |
| `P2-001` | `export function usePeerSimulation2()` | Peer simulation for Product 2 (`postProduct2PeerSimulation`, modal 2). | `src/features/product2/api/usePeerSimulation2.ts:10` |
| `P2-001` | `export function useProduct2Movements()` | Modelled movements per month for Product 2 (`putProduct2Movements`, modal 1). | `src/features/product2/api/useProduct2Movements.ts:11` |
| `P2-001` | `export function useProduct2Overview(transportMode?: TransportMode)` | Product 2 overview (`getProduct2Overview`): four projection tables filtered by transport mode | `src/features/product2/api/useProduct2Overview.ts:12` |
| `P2-001` | `export function useProduct2Projection()` | Product 2 projection only (`getProduct2Projection`). | `src/features/product2/api/useProduct2Overview.ts:26` |
| `P2-001` | `(module) index.ts` | Product 2 overview per transport mode, reusing the projection tables, cover chart and modals of product1. | `src/features/product2/index.ts:6` |
| `P2-001` | `export interface Product2Overview extends ProductOverview` | View-model types for Product 2. The projection shape is identical to Product 1 | `src/features/product2/product2.types.ts:12` |
| `RPT-001` | `export function useDownloadReportPdf()` | Downloads the rendered PDF (`downloadReportPdf`, `application/pdf`). Uses plain `fetch` because the | `src/features/reports/api/useDownloadReportPdf.ts:10` |
| `RPT-001` | `export function useRegenerateReport(sessionId: string)` | Requests a fresh render of the report (`regenerateReport`), e.g. after a failed document-service run. | `src/features/reports/api/useReport.ts:22` |
| `RPT-001` | `export function useReport(sessionId: string, enabled` | Report payload of a closed session (`getReport`). Polls while the PDF is still being rendered. | `src/features/reports/api/useReport.ts:9` |
| `RPT-001` | `(module) index.ts` | Meeting report of a closed session: payload preview, PDF download and regeneration. | `src/features/reports/index.ts:6` |
| `RPT-001` | `export type ReportStatus` | View-model types for meeting reports. Mirror `Report` from the contract | `src/features/reports/reports.types.ts:7` |
| `STR-001` | `export function useRunStressTest()` | Recomputes the stress test for all scenarios of the session (`runStressTest`, calculation | `src/features/stress/api/useRunStressTest.ts:11` |
| `STR-001` | `export function useStressTest(dimension: Dimension)` | Stress test results of the session (`getStressTest`) for one dimension (`CITY` \| `TRANSPORT_MODE`). | `src/features/stress/api/useStressTest.ts:11` |
| `STR-001` | `(module) index.ts` | Stress test per scenario: monthly exposure table by city or transport mode plus the transport price chart. | `src/features/stress/index.ts:6` |
| `STR-001` | `export type Dimension` | View-model types for the stress test. Mirror `StressTestResult`, `StressRow` from the contract | `src/features/stress/stress.types.ts:11` |
