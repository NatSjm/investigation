---
applyTo: "**/harbor/event/**/*.kt,kafka_client/**/*.kt"
description: "Kafka listeners/publishers (event/) and topics/payloads (kafka_client): Topics constants, groupId, immutable events, harbor-events.yaml in sync."
---
# Kafka messaging

- Topic names only via `Topics.<CONST>` from `kafka_client/src/main/kotlin/harbor/kafka/Topics.kt` (`harbor.imports.movements-loaded`,
  `harbor.market.prices-updated`, `harbor.meetings.session-closed`, `harbor.reports.render-requested`, `harbor.reports.rendered`).
  `gen-events.py` resolves the constants; string literals break `docs/_generated/events.md`.
- Listeners live in `core/src/main/kotlin/harbor/event/`: `@KafkaListener(topics = [Topics.X], groupId = "harbor-<context>")`;
  the handler parameter type is the event class (it is used as the payload reference in the docs).
- Producers call `kafkaTemplate.send(Topics.X, key, payload)` from a `*Publisher` / `*Requester` class in `event/`.
- Event classes are immutable `data class`es in `kafka_client/.../kafka/events/` (`MovementsLoadedEvent`, `PricesUpdatedEvent`,
  `SessionClosedEvent`, ...). Breaking payload changes = new topic with a version suffix (`.v2`), never a silent field change.
- `core/src/main/resources/openapi/harbor-events.yaml` must describe every topic produced or consumed; update it in the same change.
- Topics produced or consumed by external services (`market-data`, `document-service`) are listed in
  `harbor-docs/architecture/integrations.md`; check it before adding a producer or consumer.
- For "who consumes X" questions answer from `docs/_generated/events.md` - do not search the repository.
