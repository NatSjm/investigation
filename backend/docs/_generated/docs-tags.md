---
type: Document
title: "Spec-to-code traceability (@docs tags)"
description: "Generated map: Spec-to-code traceability (@docs tags), derived from @docs <ID> tags in KDoc/JSDoc; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-14
status: stable
---
# Spec-to-code traceability (@docs tags)

> Generated from `@docs <ID> tags in KDoc/JSDoc` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
18 tag(s). Resolve a spec/calculation ID here, then open only the listed location.

| Spec ID | Declaration | Summary | Location |
|---|---|---|---|
| `ADM-001` | `class AdminManager(` | Administration outside meetings: the parameter sets (tariff rates, handling and transport costs, role | `core/src/main/kotlin/harbor/manager/AdminManager.kt:25` |
| `CLI-001` | `class ClientManager(` | Client search, profile, overview indicators and role classification. | `core/src/main/kotlin/harbor/manager/ClientManager.kt:26` |
| `client_role_classification` | `object RoleClassifier` | Client role classification for one product group from the last 12 full months of actual movements. | `core/src/main/kotlin/harbor/utils/RoleClassifier.kt:24` |
| `COV-001` | `class CoverManager(` | Cover of the current session: cover ratio per month and sub-product (`cover_ratio` on top of the | `core/src/main/kotlin/harbor/manager/CoverManager.kt:26` |
| `cover_ratio` | `object CoverRatioCalculator` | Cover ratio per month: which share of the projected value is covered by the client's policies. | `core/src/main/kotlin/harbor/utils/CoverRatioCalculator.kt:23` |
| `horizon_totals` | `fun totals(tables: Tables): Totals` | Horizon totals: each monthly table summed over the whole horizon per key, plus the overall line from the summary | `core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt:166` |
| `horizon_totals` | `object ProjectionAggregator` | Monthly projection: values every movement row of a session over the planning horizon and groups the | `core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt:36` |
| `IMP-001` | `class ImportManager(` | Daily XLS movement import and monthly snapshot (entry point of `DailyMovementImportJob` and `MonthlySnapshotJob`). | `core/src/main/kotlin/harbor/manager/ImportManager.kt:19` |
| `MKT-001` | `class MarketManager(` | Market scenarios of the current session (create / update / delete, with shocks validated against the | `core/src/main/kotlin/harbor/manager/MarketManager.kt:22` |
| `monthly_projection` | `object ProjectionAggregator` | Monthly projection: values every movement row of a session over the planning horizon and groups the | `core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt:36` |
| `MTG-001` | `class MeetingManager(` | Meeting session lifecycle: create (CLIENT or PREPARATION), list, read, manual role override and close. | `core/src/main/kotlin/harbor/manager/MeetingManager.kt:38` |
| `P1-001` | `class Product1Manager(` | Product 1 overview page of the current session: the four cumulative projection tables (by sub-product, | `core/src/main/kotlin/harbor/manager/Product1Manager.kt:27` |
| `P2-001` | `class Product2Manager(` | Product 2 overview page of the current session: the four cumulative projection tables with transport mode | `core/src/main/kotlin/harbor/manager/Product2Manager.kt:27` |
| `peer_benchmark_simulation` | `object PeerBenchmark` | Peer benchmark simulation (modal 2 on the product pages): models the movements of similar products | `core/src/main/kotlin/harbor/utils/PeerBenchmark.kt:19` |
| `RPT-001` | `class ReportManager(` | Meeting report: builds the JSON payload from the projection tables, `stress_test_result` and the scenarios | `core/src/main/kotlin/harbor/manager/ReportManager.kt:27` |
| `scenario_price_path` | `object ScenarioPricePath` | Scenario price path: applies the shocks of a market scenario to a baseline curve. | `core/src/main/kotlin/harbor/utils/ScenarioPricePath.kt:19` |
| `STR-001` | `class StressManager(` | Stress test of the current session: runs calculation `stress_test_monthly` for every scenario of the | `core/src/main/kotlin/harbor/manager/StressManager.kt:31` |
| `stress_test_monthly` | `object StressTestCalculator` | Monthly stress test per scenario and dimension value (city for Product 1, transport mode for Product 2). | `core/src/main/kotlin/harbor/utils/StressTestCalculator.kt:23` |
