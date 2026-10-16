---
type: Document
title: "Routes (FE)"
description: "Generated map: Routes (FE), derived from react-router route objects / <Route> elements; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Routes (FE)

> Generated from `react-router route objects / <Route> elements` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
15 route(s). Child paths are joined to their parent; `Layout` is the nearest enclosing pathless or parent element. Component -> page: the page folder of the same name in codebase-map.md.

| Path | Component | Layout | Location |
|---|---|---|---|
| `/` | `Navigate` | `RootLayout` | `src/routing/Routing.tsx:26` |
| `/admin/imports` | `ImportsPage` | `AdminRoutesGuard` | `src/routing/Routing.tsx:37` |
| `/admin/parameters` | `ParametersPage` | `AdminRoutesGuard` | `src/routing/Routing.tsx:36` |
| `/clients` | `ClientSearchPage` | `RootLayout` | `src/routing/Routing.tsx:27` |
| `/clients/:clientId` | `ClientOverviewPage` | `RootLayout` | `src/routing/Routing.tsx:28` |
| `/meetings` | `Navigate` | `RootLayout` | `src/routing/Routing.tsx:29` |
| `/meetings/client` | `ClientMeetingsPage` | `RootLayout` | `src/routing/Routing.tsx:30` |
| `/meetings/preparation` | `PreparationSessionsPage` | `RootLayout` | `src/routing/Routing.tsx:31` |
| `/present/:sessionId` | `PresentationPage` | `PresentationLayout` | `src/routing/Routing.tsx:44` |
| `/session/:sessionId` | `SessionLayout` | `RootLayout` | `src/routing/SessionRoutes.tsx:15` |
| `/session/:sessionId/product1` | `Product1OverviewPage` | `SessionLayout` | `src/routing/SessionRoutes.tsx:19` |
| `/session/:sessionId/product2` | `Product2OverviewPage` | `SessionLayout` | `src/routing/SessionRoutes.tsx:20` |
| `/session/:sessionId/scenarios` | `ScenariosPage` | `SessionLayout` | `src/routing/SessionRoutes.tsx:21` |
| `/session/:sessionId/stress-test` | `StressTestPage` | `SessionLayout` | `src/routing/SessionRoutes.tsx:22` |
| `/session/:sessionId/summary` | `SessionSummaryPage` | `SessionLayout` | `src/routing/SessionRoutes.tsx:23` |
