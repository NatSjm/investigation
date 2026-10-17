---
type: Document
title: "Kafka events (BE)"
description: "Generated map: Kafka events (BE), derived from @KafkaListener / producer-call scan (kafka.producer_pattern in docs-gen.json); read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-17
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
