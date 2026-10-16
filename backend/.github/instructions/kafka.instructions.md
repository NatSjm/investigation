---
applyTo: "**/src/main/kotlin/**/event/**/*.kt,**/src/main/kotlin/**/client/kafka/**/*.kt,kafka-client/**/*.kt"
description: "Kafka listeners/publishers (event/) and topics/payloads (kafka-client): Topics constants, groupId, immutable events, harbor-events.yaml in sync."
---
# Kafka messaging

- Topic names only via `Topics.<CONST>` from `kafka-client/src/main/kotlin/com/acme/harbor/kafka/Topics.kt` (`harbor.imports.movements-loaded`,
  `harbor.market.prices-updated`, `harbor.meetings.session-closed`, `harbor.reports.render-requested`, `harbor.reports.rendered`).
  `gen-events.py` resolves the constants; string literals break `docs/_generated/events.md`.
- Listeners live in `harbor-core/src/main/kotlin/com/acme/harbor/event/`: `@KafkaListener(topics = [Topics.X], groupId = "harbor-<context>")`;
  the handler parameter type is the event class (it is used as the payload reference in the docs).
- Producers call `producer.send(Topics.X, key, payload)` from a `*Publisher` / `*Requester` class in `event/`;
  `client/kafka/EventProducer` is the only class that touches the `KafkaTemplate` and never knows a topic name.
- Event classes are immutable `data class`es in `kafka-client/.../kafka/events/` (`MovementsLoadedEvent`, `PricesUpdatedEvent`,
  `SessionClosedEvent`, ...). Breaking payload changes = new topic with a version suffix (`.v2`), never a silent field change.
- `harbor-core/src/main/resources/openapi/harbor-events.yaml` must describe every topic produced or consumed; update it in the same change.
- Topics produced or consumed by external services (`market-data`, `document-service`) are listed in
  `harbor-docs/architecture/integrations.md`; check it before adding a producer or consumer.
- For "who consumes X" questions answer from `docs/_generated/events.md` - do not search the repository.
