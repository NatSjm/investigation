---
type: Document
title: "Components (FE)"
description: "One row per shared UI component (props, purpose, which pages render it, file:line), then one row per page component (where it is rendered, which hooks it calls); name these in stories instead of inventing new components."
generated:
  by: process:gen-docs
  at: 2026-10-21
status: stable
---
# Components (FE)

> Generated from `src/components/** and src/pages/*/components/** exported components` by `scripts/docs` (regex scan, no build required). Do not edit by hand.

## Library

7 component(s) under `src/components/`. Pages must compose these; a new shared component is a change to this library, not to a page.

| Component | Group | Purpose | Props | Used by | Location |
|---|---|---|---|---|---|
| `DataTable` | - | Plain semantic table used for projection tables, stress rows, parameter lists and import batches. | `columns`, `rows`, `rowKey`, `caption?`, `emptyMessage?`, `footer?`, `dense?` | `ClientSearchPage`, `ImportsPage`, `shared`, `StressTestPage` | `src/components/DataTable/DataTable.tsx:24` |
| `LineChart` | - | Thin recharts wrapper: multi-series line chart over a month axis. | `data`, `series`, `xKey?`, `height?`, `yFormatter?`, `xFormatter?` | `ClientOverviewPage`, `ScenariosPage`, `shared`, `StressTestPage` | `src/components/LineChart/LineChart.tsx:33` |
| `Modal` | - | Minimal accessible dialog: closes on Escape and backdrop click, traps nothing fancy. | `open`, `title`, `onClose`, `children`, `footer?`, `width?` | `SessionSummaryPage`, `shared` | `src/components/Modal/Modal.tsx:14` |
| `StackedBars` | - | Thin recharts wrapper: stacked bars per month (one stack segment per series). | `data`, `series`, `xKey?`, `height?`, `yFormatter?`, `xFormatter?` | _unused_ | `src/components/StackedBars/StackedBars.tsx:22` |
| `PresentationLayout` | layout | Minimal layout for the client-facing window `/present/:sessionId`: no main navigation, no admin links, |  | `fe-app` | `src/components/layout/PresentationLayout.tsx:13` |
| `RootLayout` | layout | Top navigation + current session badge; every page renders inside the outlet. |  | `fe-app` | `src/components/layout/RootLayout.tsx:13` |
| `SessionLayout` | layout | Layout for `/session/:sessionId/*`. Loads the session, mirrors it into the session store |  | `fe-app` | `src/components/layout/SessionLayout.tsx:14` |

## Page components

22 component(s) in page folders (`src/pages/<Page>/components/`, shared folders included). Each belongs to its page. Rendered by: the file:line of the JSX tag that renders it, first per file, its own definition excluded; Hooks: the hooks of this repository it calls.

| Page component | Page | Purpose | Props | Rendered by | Hooks | Location |
|---|---|---|---|---|---|---|
| `ClientInfoPanel` | `ClientOverviewPage` | Static client information (registry data) and the list of currently open sessions. | `client`, `openSessions` | `src/pages/ClientOverviewPage/ClientOverviewPage.tsx:42` |  | `src/pages/ClientOverviewPage/components/ClientInfoPanel/ClientInfoPanel.tsx:13` |
| `ProductGroupCard` | `ClientOverviewPage` | Key indicators for one product group + sparkline (last 12 months) + session start buttons. | `indicators`, `busy?`, `onStartMeeting`, `onPrepare` | `src/pages/ClientOverviewPage/ClientOverviewPage.tsx:45` |  | `src/pages/ClientOverviewPage/components/ProductGroupCard/ProductGroupCard.tsx:23` |
| `ParameterRow` | `ParametersPage` | One parameter row with inline value editing (value + valid-from). | `parameter`, `pending?`, `onSave` | `src/pages/ParametersPage/ParametersPage.tsx:45` |  | `src/pages/ParametersPage/components/ParameterRow/ParameterRow.tsx:14` |
| `ProductMirror` | `PresentationPage` | Read-only mirror of the product overview: the four projection tables and the cover ratio chart for the | `productGroup`, `dimensionValue?` | `src/pages/PresentationPage/PresentationPage.tsx:55` | `useProduct1Overview`, `useProduct2Overview` | `src/pages/PresentationPage/components/ProductMirror/ProductMirror.tsx:24` |
| `ScenariosMirror` | `PresentationPage` | Read-only mirror of the scenarios step: baseline info and the scenario list with their shocks. |  | `src/pages/PresentationPage/PresentationPage.tsx:59` | `useBaselinePrices`, `useScenarios` | `src/pages/PresentationPage/components/ScenariosMirror/ScenariosMirror.tsx:10` |
| `StressMirror` | `PresentationPage` | Read-only mirror of the stress test step for the dimension the representative selected: | `dimension` | `src/pages/PresentationPage/PresentationPage.tsx:61` | `useBaselinePrices`, `useStressTest` | `src/pages/PresentationPage/components/StressMirror/StressMirror.tsx:17` |
| `CitySelector` | `Product1OverviewPage` | City hub filter for Product 1 tables (Aldmoor, Brightwater, Carrow, Dunmere or all). | `value`, `options`, `onChange` | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx:50` |  | `src/pages/Product1OverviewPage/components/CitySelector/CitySelector.tsx:8` |
| `TransportModeSelector` | `Product2OverviewPage` | Transport mode filter for Product 2 tables (ROAD, RAIL, SEA, AIR or all). | `value`, `options`, `onChange` | `src/pages/Product2OverviewPage/Product2OverviewPage.tsx:50` |  | `src/pages/Product2OverviewPage/components/TransportModeSelector/TransportModeSelector.tsx:10` |
| `ScenarioEditor` | `ScenariosPage` | Form for one scenario (name, kind, shocks) with a live preview of the resulting price paths. | `scenario?`, `baseline`, `horizonMonths`, `pending?`, `onSave`, `onCancel` | `src/pages/ScenariosPage/ScenariosPage.tsx:78` |  | `src/pages/ScenariosPage/components/ScenarioEditor/ScenarioEditor.tsx:22` |
| `ShockRow` | `ScenariosPage` | One editable shock: month it starts, price change and transport price change (entered in %). | `index`, `shock`, `horizonMonths`, `onChange`, `onRemove` | `src/pages/ScenariosPage/components/ScenarioEditor/ScenarioEditor.tsx:78` |  | `src/pages/ScenariosPage/components/ShockRow/ShockRow.tsx:12` |
| `RoleOverrideDialog` | `SessionSummaryPage` | Manual role override with mandatory reason (replaces the algorithm result for this session). | `open`, `sessionId`, `currentRole?`, `onClose` | `src/pages/SessionSummaryPage/SessionSummaryPage.tsx:65` | `useRoleOverride` | `src/pages/SessionSummaryPage/components/RoleOverrideDialog/RoleOverrideDialog.tsx:20` |
| `CoverQuotePanel` | `shared` | Embedded in the product overview pages: current cover position over the horizon and a | `priceBasis?`, `subProducts` | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx:65`<br>`src/pages/Product2OverviewPage/Product2OverviewPage.tsx:65` | `useCoverQuote`, `useCoverSummary` | `src/pages/shared/components/CoverQuotePanel/CoverQuotePanel.tsx:19` |
| `CoverRatioChart` | `shared` | Cover ratio per month, one line per sub-product (calculation `cover_ratio`). | `series`, `height?` | `src/pages/PresentationPage/components/ProductMirror/ProductMirror.tsx:45`<br>`src/pages/Product1OverviewPage/Product1OverviewPage.tsx:64`<br>`src/pages/Product2OverviewPage/Product2OverviewPage.tsx:64` |  | `src/pages/shared/components/CoverRatioChart/CoverRatioChart.tsx:18` |
| `DownloadPdfButton` | `shared` | "Download PDF" button for a closed session (Meetings list, session summary). | `sessionId`, `disabled?`, `label?` | `src/pages/SessionSummaryPage/SessionSummaryPage.tsx:61`<br>`src/pages/shared/components/MeetingsListPage/MeetingsListPage.tsx:27` | `useDownloadReportPdf` | `src/pages/shared/components/DownloadPdfButton/DownloadPdfButton.tsx:12` |
| `MeetingsListPage` | `shared` | Shared session list with filters; closed sessions expose the report PDF download. | `kind?`, `title?` | `src/pages/ClientMeetingsPage/ClientMeetingsPage.tsx:8`<br>`src/pages/PreparationSessionsPage/PreparationSessionsPage.tsx:8` | `useSessions` | `src/pages/shared/components/MeetingsListPage/MeetingsListPage.tsx:44` |
| `MovementInputModal` | `shared` | Modal 1: modelled movements per month. One row per month with IN and OUT quantity / unit price | `open`, `onClose`, `periods`, `subProducts`, `dimension`, `dimensionValues`, `initial?`, `pending?`, `onSubmit` | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx:70`<br>`src/pages/Product2OverviewPage/Product2OverviewPage.tsx:70` |  | `src/pages/shared/components/MovementInputModal/MovementInputModal.tsx:30` |
| `PeerSimulationModal` | `shared` | Modal 2: movements of similar products at peer firms. Picks a peer segment and a scaling | `open`, `onClose`, `segments`, `result?`, `pending?`, `onSubmit` | `src/pages/Product1OverviewPage/Product1OverviewPage.tsx:81`<br>`src/pages/Product2OverviewPage/Product2OverviewPage.tsx:81` |  | `src/pages/shared/components/PeerSimulationModal/PeerSimulationModal.tsx:22` |
| `ProjectionTables` | `shared` | The four cumulative tables of the monthly projection: by sub-product, by dimension | `tables`, `priceBasis?`, `dimensionLabel` | `src/pages/PresentationPage/components/ProductMirror/ProductMirror.tsx:43`<br>`src/pages/Product1OverviewPage/Product1OverviewPage.tsx:62`<br>`src/pages/Product2OverviewPage/Product2OverviewPage.tsx:62` |  | `src/pages/shared/components/ProjectionTables/ProjectionTables.tsx:70` |
| `ReportPreview` | `shared` | Read-only view of the report payload grouped by known sections, with a regenerate action. | `report` | `src/pages/SessionSummaryPage/SessionSummaryPage.tsx:60` | `useRegenerateReport` | `src/pages/shared/components/ReportPreview/ReportPreview.tsx:19` |
| `DimensionToggle` | `StressTestPage` | Segmented control switching the stress table between city and transport mode breakdown. | `value`, `onChange`, `disabled?` | `src/pages/StressTestPage/StressTestPage.tsx:46` |  | `src/pages/StressTestPage/components/DimensionToggle/DimensionToggle.tsx:12` |
| `StressTable` | `StressTestPage` | Monthly stress table of one scenario (`stress_test_monthly`): exposure, transport cost delta | `scenario`, `dimension`, `priceBasis?` | `src/pages/PresentationPage/components/StressMirror/StressMirror.tsx:33`<br>`src/pages/StressTestPage/StressTestPage.tsx:62` |  | `src/pages/StressTestPage/components/StressTable/StressTable.tsx:17` |
| `TransportPriceChart` | `StressTestPage` | Transport price over time, one line per scenario (plus the dashed baseline when provided). | `scenarios`, `baseline?`, `height?` | `src/pages/PresentationPage/components/StressMirror/StressMirror.tsx:31`<br>`src/pages/StressTestPage/StressTestPage.tsx:59` |  | `src/pages/StressTestPage/components/TransportPriceChart/TransportPriceChart.tsx:18` |
