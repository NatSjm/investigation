---
type: Document
title: "Component library (FE)"
description: "One row per shared UI component: props, purpose, which pages render it, file:line; name these in stories instead of inventing new components."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Component library (FE)

> Generated from `src/components/** exported components` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
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
