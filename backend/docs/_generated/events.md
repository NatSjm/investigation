---
type: Document
title: "Kafka events (BE)"
description: "Generated map: Kafka events (BE), derived from @KafkaListener / producer-call scan (kafka.producer_pattern in docs-gen.json); read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-28
status: stable
---
# Kafka events (BE)

> Generated from `@KafkaListener / producer-call scan (kafka.producer_pattern in docs-gen.json)` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
5 topic(s). Payload = the listener parameter type, with its schema file when one exists under the configured schema folders.

| Topic | Producers (this repo) | Consumers (this repo) | Payload |
|---|---|---|---|
| `harbor.imports.movements-loaded` | `MovementsLoadedPublisher` (harbor-core/src/main/kotlin/com/acme/harbor/event/MovementsLoadedPublisher.kt:34) | `onMovementsLoaded` (harbor-core/src/main/kotlin/com/acme/harbor/event/Product1ProjectionRefreshListener.kt:24, group harbor-product1)<br>`onMovementsLoaded` (harbor-core/src/main/kotlin/com/acme/harbor/event/Product2ProjectionRefreshListener.kt:24, group harbor-product2) | `MovementsLoaded` (kafka-client/src/main/resources/avro/MovementsLoaded.avsc) |
| `harbor.market.prices-updated` | _external_ | `onPricesUpdated` (harbor-core/src/main/kotlin/com/acme/harbor/event/MarketPricesListener.kt:22, group harbor-market) | `PricesUpdated` (kafka-client/src/main/resources/json_market-data/PricesUpdated.json) |
| `harbor.meetings.session-closed` | `SessionEventsPublisher` (harbor-core/src/main/kotlin/com/acme/harbor/event/SessionEventsPublisher.kt:26) | `onSessionClosed` (harbor-core/src/main/kotlin/com/acme/harbor/event/ClientRoleSessionClosedListener.kt:23, group harbor-clients)<br>`onSessionClosed` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportSessionClosedListener.kt:19, group harbor-reports) | `SessionClosed` (kafka-client/src/main/resources/avro/SessionClosed.avsc) |
| `harbor.reports.render-requested` | `ReportRenderRequester` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderRequester.kt:28) | _external_ |  |
| `harbor.reports.rendered` | _external_ | `onReportRendered` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderedListener.kt:12, group harbor-reports) | `ReportRendered` (kafka-client/src/main/resources/json_document-service/ReportRendered.json) |

Producer wrappers whose topic is a parameter (the callers above name the topic): `EventProducer` (harbor-core/src/main/kotlin/com/acme/harbor/client/kafka/EventProducer.kt:15)

## Payload schemas

5 schema file(s) under the schema folders (`kafka-client/src/main/resources`); fields as the files declare them, the payload classes generated at build are not read.

### `MovementsLoaded` - Avro record, kafka-client/src/main/resources/avro/MovementsLoaded.avsc
Topic harbor.imports.movements-loaded, key = batchId: a daily import batch has been stored in goods_movement; the projections of the listed clients are stale. Produced by MovementsLoadedPublisher.

| Field | Type | Required | Doc |
|---|---|---|---|
| `batchId` | string | yes | import batch id (UUID) |
| `clientIds` | array<string> | yes | clients (UUID) with accepted rows in the batch |
| `periodFrom` | string | yes | first month of the batch, ISO date (first day of month) |
| `periodTo` | string | yes | last month of the batch, ISO date |

### `ReportRenderRequested` - Avro record, kafka-client/src/main/resources/avro/ReportRenderRequested.avsc
Topic harbor.reports.render-requested, key = sessionId: asks document-service to render the report payload as PDF. Produced by ReportRenderRequester.

| Field | Type | Required | Doc |
|---|---|---|---|
| `sessionId` | string | yes | session id (UUID) |
| `payloadRef` | string | yes | URL under which document-service fetches the JSON report payload (getReport) |
| `template` | string | yes | HTML template of the meeting report (pdf/meeting-report.html with pdf/report.css inlined) |

### `SessionClosed` - Avro record, kafka-client/src/main/resources/avro/SessionClosed.avsc
Topic harbor.meetings.session-closed, key = sessionId: a meeting session was closed. Produced by SessionEventsPublisher; consumed by the report and client-role listeners.

| Field | Type | Required | Doc |
|---|---|---|---|
| `sessionId` | string | yes | session id (UUID) |
| `clientId` | string | yes | client id (UUID) |
| `productGroup` | string | yes | wire value of the product group (product1 / product2) |
| `kind` | string | yes | CLIENT (real meeting) or PREPARATION (dry run) |
| `roleOverride` | string | no | IMPORTER / EXPORTER / MIXED when a manual override was set in the session |

### `ReportRendered` - JSON Schema, kafka-client/src/main/resources/json_document-service/ReportRendered.json
Topic harbor.reports.rendered, published by the external document-service (key = sessionId): the PDF of a meeting report is available. Consumed by ReportRenderedListener.

| Field | Type | Required | Doc |
|---|---|---|---|
| `sessionId` | string (uuid) | yes | session id |
| `pdfPath` | string | yes | location of the rendered PDF in the document store |

### `PricesUpdated` - JSON Schema, kafka-client/src/main/resources/json_market-data/PricesUpdated.json
Topic harbor.market.prices-updated, published by the external market-data service (key = productGroup): the baseline price curve of a product group changed. Consumed by MarketPricesListener.

| Field | Type | Required | Doc |
|---|---|---|---|
| `productGroup` | string | yes | wire value of the product group (product1 / product2) |
| `corridor` | string | yes | corridor code (VLD-NRL / CST-MRD) |
| `asOf` | string (date-time) | yes | instant the curve was published |
