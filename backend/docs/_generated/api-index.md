---
type: Document
title: "REST API index (BE)"
description: "Generated map: REST API index (BE), derived from core/src/main/resources/openapi/harbor-api.yaml (contract) + override fun <operationId> lookup in @RestController classes; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-11
status: stable
---
# REST API index (BE)

> Generated from `core/src/main/resources/openapi/harbor-api.yaml (contract) + override fun <operationId> lookup in @RestController classes` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
34 operation(s) from the contract; 34 implemented. Request/response schemas: open the contract `components/schemas`, not the DTO files.

| Method | Path | operationId | Tag | Handler | Params | Location |
|---|---|---|---|---|---|---|
| GET | `/api/v1/admin/imports` | `listImportBatches` | admin | `AdminController.listImportBatches` |  | `core/src/main/kotlin/harbor/api/AdminController.kt:26` |
| POST | `/api/v1/admin/imports/run` | `triggerImport` | admin | `AdminController.triggerImport` |  | `core/src/main/kotlin/harbor/api/AdminController.kt:29` |
| GET | `/api/v1/admin/parameters` | `listParameters` | admin | `AdminController.listParameters` |  | `core/src/main/kotlin/harbor/api/AdminController.kt:20` |
| PUT | `/api/v1/admin/parameters/{key}` | `upsertParameter` | admin | `AdminController.upsertParameter` | key | `core/src/main/kotlin/harbor/api/AdminController.kt:23` |
| GET | `/api/v1/clients` | `searchClients` | clients | `ClientController.searchClients` |  | `core/src/main/kotlin/harbor/api/ClientController.kt:23` |
| GET | `/api/v1/clients/{clientId}` | `getClient` | clients | `ClientController.getClient` | clientId | `core/src/main/kotlin/harbor/api/ClientController.kt:26` |
| GET | `/api/v1/clients/{clientId}/cover-policies` | `listCoverPolicies` | cover | `CoverController.listCoverPolicies` | clientId | `core/src/main/kotlin/harbor/api/CoverController.kt:31` |
| GET | `/api/v1/clients/{clientId}/overview` | `getClientOverview` | clients | `ClientController.getClientOverview` | clientId | `core/src/main/kotlin/harbor/api/ClientController.kt:29` |
| GET | `/api/v1/clients/{clientId}/role` | `getClientRole` | clients | `ClientController.getClientRole` | clientId | `core/src/main/kotlin/harbor/api/ClientController.kt:32` |
| POST | `/api/v1/clients/{clientId}/sessions` | `createSession` | meetings | `SessionController.createSession` | clientId | `core/src/main/kotlin/harbor/api/SessionController.kt:25` |
| POST | `/api/v1/session/cover/quotes` | `requestCoverQuote` | cover | `CoverController.requestCoverQuote` |  | `core/src/main/kotlin/harbor/api/CoverController.kt:26` |
| GET | `/api/v1/session/cover/summary` | `getCoverSummary` | cover | `CoverController.getCoverSummary` |  | `core/src/main/kotlin/harbor/api/CoverController.kt:23` |
| GET | `/api/v1/session/market/baseline` | `getBaselinePrices` | market | `ScenarioController.getBaselinePrices` |  | `core/src/main/kotlin/harbor/api/ScenarioController.kt:41` |
| PUT | `/api/v1/session/product1/movements` | `putProduct1Movements` | product1 | `Product1Controller.putProduct1Movements` |  | `core/src/main/kotlin/harbor/api/Product1Controller.kt:29` |
| GET | `/api/v1/session/product1/overview` | `getProduct1Overview` | product1 | `Product1Controller.getProduct1Overview` |  | `core/src/main/kotlin/harbor/api/Product1Controller.kt:24` |
| POST | `/api/v1/session/product1/peer-simulation` | `postProduct1PeerSimulation` | product1 | `Product1Controller.postProduct1PeerSimulation` |  | `core/src/main/kotlin/harbor/api/Product1Controller.kt:35` |
| GET | `/api/v1/session/product1/projection` | `getProduct1Projection` | product1 | `Product1Controller.getProduct1Projection` |  | `core/src/main/kotlin/harbor/api/Product1Controller.kt:41` |
| PUT | `/api/v1/session/product2/movements` | `putProduct2Movements` | product2 | `Product2Controller.putProduct2Movements` |  | `core/src/main/kotlin/harbor/api/Product2Controller.kt:31` |
| GET | `/api/v1/session/product2/overview` | `getProduct2Overview` | product2 | `Product2Controller.getProduct2Overview` |  | `core/src/main/kotlin/harbor/api/Product2Controller.kt:25` |
| POST | `/api/v1/session/product2/peer-simulation` | `postProduct2PeerSimulation` | product2 | `Product2Controller.postProduct2PeerSimulation` |  | `core/src/main/kotlin/harbor/api/Product2Controller.kt:37` |
| GET | `/api/v1/session/product2/projection` | `getProduct2Projection` | product2 | `Product2Controller.getProduct2Projection` |  | `core/src/main/kotlin/harbor/api/Product2Controller.kt:43` |
| GET | `/api/v1/session/scenarios` | `listScenarios` | market | `ScenarioController.listScenarios` |  | `core/src/main/kotlin/harbor/api/ScenarioController.kt:23` |
| POST | `/api/v1/session/scenarios` | `createScenario` | market | `ScenarioController.createScenario` |  | `core/src/main/kotlin/harbor/api/ScenarioController.kt:26` |
| DELETE | `/api/v1/session/scenarios/{scenarioId}` | `deleteScenario` | market | `ScenarioController.deleteScenario` | scenarioId | `core/src/main/kotlin/harbor/api/ScenarioController.kt:36` |
| PUT | `/api/v1/session/scenarios/{scenarioId}` | `updateScenario` | market | `ScenarioController.updateScenario` | scenarioId | `core/src/main/kotlin/harbor/api/ScenarioController.kt:31` |
| GET | `/api/v1/session/stress-test` | `getStressTest` | stress | `StressTestController.getStressTest` |  | `core/src/main/kotlin/harbor/api/StressTestController.kt:24` |
| POST | `/api/v1/session/stress-test` | `runStressTest` | stress | `StressTestController.runStressTest` |  | `core/src/main/kotlin/harbor/api/StressTestController.kt:21` |
| GET | `/api/v1/sessions` | `listSessions` | meetings | `SessionController.listSessions` |  | `core/src/main/kotlin/harbor/api/SessionController.kt:35` |
| GET | `/api/v1/sessions/{sessionId}` | `getSession` | meetings | `SessionController.getSession` | sessionId | `core/src/main/kotlin/harbor/api/SessionController.kt:38` |
| POST | `/api/v1/sessions/{sessionId}/close` | `closeSession` | meetings | `SessionController.closeSession` | sessionId | `core/src/main/kotlin/harbor/api/SessionController.kt:41` |
| GET | `/api/v1/sessions/{sessionId}/report` | `getReport` | reports | `ReportController.getReport` | sessionId | `core/src/main/kotlin/harbor/api/ReportController.kt:24` |
| POST | `/api/v1/sessions/{sessionId}/report` | `regenerateReport` | reports | `ReportController.regenerateReport` | sessionId | `core/src/main/kotlin/harbor/api/ReportController.kt:27` |
| GET | `/api/v1/sessions/{sessionId}/report.pdf` | `downloadReportPdf` | reports | `ReportController.downloadReportPdf` | sessionId | `core/src/main/kotlin/harbor/api/ReportController.kt:30` |
| PUT | `/api/v1/sessions/{sessionId}/role` | `setRoleOverride` | meetings | `SessionController.setRoleOverride` | sessionId | `core/src/main/kotlin/harbor/api/SessionController.kt:44` |
