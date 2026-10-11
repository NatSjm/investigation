---
type: Document
title: "Component library (FE)"
description: "One row per shared UI component: props, purpose, which features render it, file:line; name these in stories instead of inventing new components."
generated:
  by: process:gen-docs
  at: 2026-10-11
status: stable
---
# Component library (FE)

> Generated from `src/shared/** exported components` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
4 component(s) under `src/shared/`. Features must compose these; a new shared component is a change to this library, not to a feature.

| Component | Group | Purpose | Props | Used by | Location |
|---|---|---|---|---|---|
| `LineChart` | charts | Thin recharts wrapper: multi-series line chart over a month axis. | `data`, `series`, `xKey?`, `height?`, `yFormatter?`, `xFormatter?` | `clients`, `market`, `product1`, `stress` | `src/shared/charts/LineChart.tsx:33` |
| `StackedBars` | charts | Thin recharts wrapper: stacked bars per month (one stack segment per series). | `data`, `series`, `xKey?`, `height?`, `yFormatter?`, `xFormatter?` | _unused_ | `src/shared/charts/StackedBars.tsx:22` |
| `DataTable` | ui | Plain semantic table used for projection tables, stress rows, parameter lists and import batches. | `columns`, `rows`, `rowKey`, `caption?`, `emptyMessage?`, `footer?`, `dense?` | `admin`, `clients`, `meetings`, `product1`, `stress` | `src/shared/ui/DataTable.tsx:24` |
| `Modal` | ui | Minimal accessible dialog: closes on Escape and backdrop click, traps nothing fancy. | `open`, `title`, `onClose`, `children`, `footer?`, `width?` | `meetings`, `product1` | `src/shared/ui/Modal.tsx:14` |
