---
type: Document
title: "REST API index (BE)"
description: "Generated map: REST API index (BE), derived from harbor-core/src/main/resources/openapi/openapi_harbor.yaml (contract) + handler method named like the operationId (rest.handler_pattern) in @RestController classes; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# REST API index (BE)

> Generated from `harbor-core/src/main/resources/openapi/openapi_harbor.yaml (contract) + handler method named like the operationId (rest.handler_pattern) in @RestController classes` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
34 operation(s) from the contract; 34 implemented. Request/response schemas: open the contract `components/schemas`, not the DTO files. 1 request mapping(s) outside the contract are tagged `(no contract)`.

| Method | Path | operationId | Tag | Handler | Params | Location |
|---|---|---|---|---|---|---|
| GET | `/api/v1/admin/imports` | `listImportBatches` | admin | `AdminController.listImportBatches` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/AdminController.kt:25` |
| POST | `/api/v1/admin/imports/run` | `triggerImport` | admin | `AdminController.triggerImport` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/AdminController.kt:28` |
| GET | `/api/v1/admin/parameters` | `listParameters` | admin | `AdminController.listParameters` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/AdminController.kt:19` |
| PUT | `/api/v1/admin/parameters/{key}` | `upsertParameter` | admin | `AdminController.upsertParameter` | key | `harbor-core/src/main/kotlin/com/acme/harbor/api/AdminController.kt:22` |
| GET | `/api/v1/clients` | `searchClients` | clients | `ClientController.searchClients` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ClientController.kt:22` |
| GET | `/api/v1/clients/{clientId}` | `getClient` | clients | `ClientController.getClient` | clientId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ClientController.kt:25` |
| GET | `/api/v1/clients/{clientId}/cover-policies` | `listCoverPolicies` | cover | `CoverController.listCoverPolicies` | clientId | `harbor-core/src/main/kotlin/com/acme/harbor/api/CoverController.kt:31` |
| GET | `/api/v1/clients/{clientId}/overview` | `getClientOverview` | clients | `ClientController.getClientOverview` | clientId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ClientController.kt:28` |
| GET | `/api/v1/clients/{clientId}/role` | `getClientRole` | clients | `ClientController.getClientRole` | clientId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ClientController.kt:31` |
| POST | `/api/v1/clients/{clientId}/sessions` | `createSession` | meetings | `SessionController.createSession` | clientId | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:24` |
| POST | `/api/v1/session/cover/quotes` | `requestCoverQuote` | cover | `CoverController.requestCoverQuote` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/CoverController.kt:26` |
| GET | `/api/v1/session/cover/summary` | `getCoverSummary` | cover | `CoverController.getCoverSummary` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/CoverController.kt:23` |
| GET | `/api/v1/session/market/baseline` | `getBaselinePrices` | market | `ScenarioController.getBaselinePrices` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:41` |
| PUT | `/api/v1/session/product1/movements` | `putProduct1Movements` | product1 | `Product1Controller.putProduct1Movements` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:29` |
| GET | `/api/v1/session/product1/overview` | `getProduct1Overview` | product1 | `Product1Controller.getProduct1Overview` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:24` |
| POST | `/api/v1/session/product1/peer-simulation` | `postProduct1PeerSimulation` | product1 | `Product1Controller.postProduct1PeerSimulation` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:35` |
| GET | `/api/v1/session/product1/projection` | `getProduct1Projection` | product1 | `Product1Controller.getProduct1Projection` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:41` |
| PUT | `/api/v1/session/product2/movements` | `putProduct2Movements` | product2 | `Product2Controller.putProduct2Movements` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product2Controller.kt:30` |
| GET | `/api/v1/session/product2/overview` | `getProduct2Overview` | product2 | `Product2Controller.getProduct2Overview` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product2Controller.kt:24` |
| POST | `/api/v1/session/product2/peer-simulation` | `postProduct2PeerSimulation` | product2 | `Product2Controller.postProduct2PeerSimulation` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product2Controller.kt:36` |
| GET | `/api/v1/session/product2/projection` | `getProduct2Projection` | product2 | `Product2Controller.getProduct2Projection` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/Product2Controller.kt:42` |
| GET | `/api/v1/session/scenarios` | `listScenarios` | market | `ScenarioController.listScenarios` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:23` |
| POST | `/api/v1/session/scenarios` | `createScenario` | market | `ScenarioController.createScenario` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:26` |
| DELETE | `/api/v1/session/scenarios/{scenarioId}` | `deleteScenario` | market | `ScenarioController.deleteScenario` | scenarioId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:36` |
| PUT | `/api/v1/session/scenarios/{scenarioId}` | `updateScenario` | market | `ScenarioController.updateScenario` | scenarioId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ScenarioController.kt:31` |
| GET | `/api/v1/session/stress-test` | `getStressTest` | stress | `StressTestController.getStressTest` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/StressTestController.kt:23` |
| POST | `/api/v1/session/stress-test` | `runStressTest` | stress | `StressTestController.runStressTest` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/StressTestController.kt:20` |
| GET | `/api/v1/sessions` | `listSessions` | meetings | `SessionController.listSessions` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:34` |
| GET | `/api/v1/sessions/{sessionId}` | `getSession` | meetings | `SessionController.getSession` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:37` |
| POST | `/api/v1/sessions/{sessionId}/close` | `closeSession` | meetings | `SessionController.closeSession` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:40` |
| GET | `/api/v1/sessions/{sessionId}/report` | `getReport` | reports | `ReportController.getReport` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ReportController.kt:21` |
| POST | `/api/v1/sessions/{sessionId}/report` | `regenerateReport` | reports | `ReportController.regenerateReport` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ReportController.kt:24` |
| GET | `/api/v1/sessions/{sessionId}/report.pdf` | `downloadReportPdf` | reports | `ReportController.downloadReportPdf` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/ReportController.kt:27` |
| PUT | `/api/v1/sessions/{sessionId}/role` | `setRoleOverride` | meetings | `SessionController.setRoleOverride` | sessionId | `harbor-core/src/main/kotlin/com/acme/harbor/api/SessionController.kt:43` |
| GET | `/api/v1/technical/version` | `version` | (no contract) | `TechnicalController.version` |  | `harbor-core/src/main/kotlin/com/acme/harbor/api/technical/TechnicalController.kt:20` |
