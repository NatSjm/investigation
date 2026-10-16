---
type: Document
title: "Kafka events (BE)"
description: "Generated map: Kafka events (BE), derived from @KafkaListener / producer-call scan (kafka.producer_pattern in docs-gen.json); read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-16
status: stable
---
# Kafka events (BE)

> Generated from `@KafkaListener / producer-call scan (kafka.producer_pattern in docs-gen.json)` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
5 topic(s). Payload schema: open the event class named in the handler signature.

| Topic | Producers (this repo) | Consumers (this repo) |
|---|---|---|
| `harbor.imports.movements-loaded` | `MovementsLoadedPublisher` (harbor-core/src/main/kotlin/com/acme/harbor/event/MovementsLoadedPublisher.kt:35) | `onMovementsLoaded` (harbor-core/src/main/kotlin/com/acme/harbor/event/Product1ProjectionRefreshListener.kt:24, group harbor-product1)<br>`onMovementsLoaded` (harbor-core/src/main/kotlin/com/acme/harbor/event/Product2ProjectionRefreshListener.kt:24, group harbor-product2) |
| `harbor.market.prices-updated` | _external_ | `onPricesUpdated` (harbor-core/src/main/kotlin/com/acme/harbor/event/MarketPricesListener.kt:23, group harbor-market) |
| `harbor.meetings.session-closed` | `SessionEventsPublisher` (harbor-core/src/main/kotlin/com/acme/harbor/event/SessionEventsPublisher.kt:27) | `onSessionClosed` (harbor-core/src/main/kotlin/com/acme/harbor/event/ClientRoleSessionClosedListener.kt:23, group harbor-clients)<br>`onSessionClosed` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportSessionClosedListener.kt:19, group harbor-reports) |
| `harbor.reports.render-requested` | `ReportRenderRequester` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderRequester.kt:29) | _external_ |
| `harbor.reports.rendered` | _external_ | `onReportRendered` (harbor-core/src/main/kotlin/com/acme/harbor/event/ReportRenderedListener.kt:13, group harbor-reports) |

Producer wrappers whose topic is a parameter (the callers above name the topic): `EventProducer` (harbor-core/src/main/kotlin/com/acme/harbor/client/kafka/EventProducer.kt:15)
