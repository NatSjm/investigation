---
type: Document
title: Codebase map (FE)
description: Generated map: Codebase map (FE), derived from src/features/* + index.ts barrels; read instead of source files.
generated:
  by: process:gen-docs
  at: 2026-10-09
status: stable
---
# Codebase map (FE)

> Generated from `src/features/* + index.ts barrels` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Read the feature `index.ts` (public surface) and `*.types.ts` first; open components only for UI-level questions.

| Feature | Purpose | Entry | Files | Components | Hooks | Public exports | API calls |
|---|---|---|---|---|---|---|---|
| `admin` | Administration outside meetings: parameter sets with inline editing and the daily import batch monitor. | `src/features/admin/index.ts` | 7 | 3 | 2 | ParametersPage, ParameterRow, ImportsPage, useParameters, useUpsertParameter, useImportBatches, useTriggerImport, Parameter, ParameterUpsertRequest, ImportBatch, ImportStatus | /admin/imports<br>/admin/imports/run<br>/admin/parameters<br>/admin/parameters/{key} |
| `clients` | Client search, client overview with product group cards (key indicators, sparklines, Start meeting / Prepare) and role classification. | `src/features/clients/index.ts` | 9 | 4 | 3 | ClientSearchPage, ClientOverviewPage, ProductGroupCard, ClientInfoPanel, useClientSearch, useClientOverview, useClientRole, ClientSummary, ClientOverview, ProductGroupIndicators, ClientRoleInfo, ClientRole | /clients<br>/clients/{clientId}<br>/clients/{clientId}/overview<br>/clients/{clientId}/role |
| `cover` | Cover position of a session: cover ratio per month and sub-product, and quotes for the uncovered part. | `src/features/cover/index.ts` | 5 | 1 | 2 | CoverQuotePanel, useCoverSummary, useCoverPolicies, useCoverQuote, CoverSummary, CoverSummaryRow, CoverQuote, CoverQuoteRequest, CoverPolicy, uncoveredValue | /clients/{clientId}/cover-policies<br>/session/cover/quotes<br>/session/cover/summary |
| `market` | Market scenarios of a session: price and transport price shocks on top of the baseline curve, with live path preview. | `src/features/market/index.ts` | 7 | 3 | 2 | ScenariosPage, ScenarioEditor, ShockRow, useScenarios, useScenarioMutations, useBaselinePrices, Scenario, ScenarioRequest, ScenarioKind, Shock, BaselinePrices, BaselinePoint, scenarioPricePath | /session/market/baseline<br>/session/scenarios<br>/session/scenarios/{scenarioId} |
| `meetings` | Meeting session lifecycle: create CLIENT or PREPARATION sessions, list and close them, override the client role, show the session summary. | `src/features/meetings/index.ts` | 9 | 3 | 4 | MeetingsListPage, SessionSummaryPage, RoleOverrideDialog, useSessions, useSession, useCreateSession, useCloseSession, useRoleOverride, Session, SessionKind, SessionStatus, CreateSessionRequest, RoleOverrideRequest, SessionFilter | /clients/{clientId}/sessions<br>/sessions<br>/sessions/{sessionId}<br>/sessions/{sessionId}/close<br>/sessions/{sessionId}/role |
| `product1` | Product 1 overview per city hub: the four cumulative projection tables, cover ratio chart, movement input and peer simulation modals. | `src/features/product1/index.ts` | 11 | 6 | 3 | Product1OverviewPage, ProjectionTables, CoverRatioChart, MovementInputModal, PeerSimulationModal, CitySelector, useProduct1Overview, useProduct1Projection, useProduct1Movements, usePeerSimulation1, ProductOverview, ProjectionTables, ProjectionRow, ProjectionSummaryRow, MovementInput, MovementDimension, PeerSimulationRequest, PeerSimulationResult, CoverSeries, P1_CITIES, P1_SUB_PRODUCTS | /session/product1/movements<br>/session/product1/overview<br>/session/product1/peer-simulation<br>/session/product1/projection |
| `product2` | Product 2 overview per transport mode, reusing the projection tables, cover chart and modals of product1. | `src/features/product2/index.ts` | 7 | 2 | 3 | Product2OverviewPage, TransportModeSelector, useProduct2Overview, useProduct2Projection, useProduct2Movements, usePeerSimulation2, Product2Overview, TransportMode, P2_TRANSPORT_MODES, P2_SUB_PRODUCTS, P2_CITIES | /session/product2/movements<br>/session/product2/overview<br>/session/product2/peer-simulation<br>/session/product2/projection |
| `reports` | Meeting report of a closed session: payload preview, PDF download and regeneration. | `src/features/reports/index.ts` | 6 | 2 | 2 | DownloadPdfButton, ReportPreview, useReport, useRegenerateReport, useDownloadReportPdf, Report, ReportStatus | /api/v1/sessions/{*}/report.pdf<br>/sessions/{sessionId}/report |
| `stress` | Stress test per scenario: monthly exposure table by city or transport mode plus the transport price chart. | `src/features/stress/index.ts` | 8 | 4 | 2 | StressTestPage, StressTable, TransportPriceChart, DimensionToggle, useStressTest, useRunStressTest, Dimension, StressRow, StressScenarioResult, StressTestResult, defaultDimension, DIMENSION_LABEL | /session/stress-test |
