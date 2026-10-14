---
type: Document
title: "Kafka events (BE)"
description: "Generated map: Kafka events (BE), derived from @KafkaListener / KafkaTemplate.send scan; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-14
status: stable
---
# Kafka events (BE)

> Generated from `@KafkaListener / KafkaTemplate.send scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
5 topic(s). Payload schema: open the event class named in the handler signature.

| Topic | Producers (this repo) | Consumers (this repo) |
|---|---|---|
| `harbor.imports.movements-loaded` | `MovementsLoadedPublisher` (core/src/main/kotlin/harbor/event/MovementsLoadedPublisher.kt:35) | `onMovementsLoaded` (core/src/main/kotlin/harbor/event/Product1ProjectionRefreshListener.kt:24, group harbor-product1)<br>`onMovementsLoaded` (core/src/main/kotlin/harbor/event/Product2ProjectionRefreshListener.kt:24, group harbor-product2) |
| `harbor.market.prices-updated` | _external_ | `onPricesUpdated` (core/src/main/kotlin/harbor/event/MarketPricesListener.kt:23, group harbor-market) |
| `harbor.meetings.session-closed` | `SessionEventsPublisher` (core/src/main/kotlin/harbor/event/SessionEventsPublisher.kt:27) | `onSessionClosed` (core/src/main/kotlin/harbor/event/ClientRoleSessionClosedListener.kt:23, group harbor-clients)<br>`onSessionClosed` (core/src/main/kotlin/harbor/event/ReportSessionClosedListener.kt:19, group harbor-reports) |
| `harbor.reports.render-requested` | `ReportRenderRequester` (core/src/main/kotlin/harbor/event/ReportRenderRequester.kt:29) | _external_ |
| `harbor.reports.rendered` | _external_ | `onReportRendered` (core/src/main/kotlin/harbor/event/ReportRenderedListener.kt:13, group harbor-reports) |
