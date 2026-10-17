---
applyTo: "**/src/main/kotlin/**/event/**/*.kt,**/src/main/kotlin/**/client/kafka/**/*.kt,kafka-client/**/*.kt"
description: "Kafka listeners/publishers (event/) and topics/payloads (kafka-client): Topics constants, groupId, immutable events, harbor-events.yaml in sync."
---
# Kafka messaging

- Topic names only via the `TOPIC` constant of the listener or publisher class declared as `const val TOPIC` in the companion object of that class in `event/` (never a literal in the annotation; `harbor.imports.movements-loaded`,
  `harbor.market.prices-updated`, `harbor.meetings.session-closed`, `harbor.reports.render-requested`, `harbor.reports.rendered`).
  `gen-events.py` resolves the constants; string literals break `docs/_generated/events.md`.
- Listeners live in `harbor-core/src/main/kotlin/com/acme/harbor/event/`: `@KafkaListener(topics = [TOPIC], groupId = "${harbor.kafka.groups.<context>}")`;
  the handler parameter type is the generated event class (it is the payload reference in the docs); `groupId` and `autoStartup` are `${...}` properties.
- Producers call `producer.send(TOPIC, key, payload)` from a `*Publisher` / `*Requester` class in `event/`;
  `client/kafka/EventProducer` is the only class that touches the `KafkaTemplate` and never knows a topic name.
- Payload schemas live in `kafka-client/src/main/resources`: Avro (`avro/*.avsc`) for the events Harbor publishes, JSON Schema
  (`json_<service>/*.json`) for the events of external services; the classes are generated at build into
  `com.acme.harbor.kafka.events[.<service>]` and never hand-written. A listener's parameter type names the schema (`events.md` links it: the generated class and the schema file share the simple name). The generated classes under `target/` are never read or cited: open the schema file. Breaking payload changes = new topic with a version suffix (`.v2`), never a silent field change.
- `harbor-core/src/main/resources/openapi/harbor-events.yaml` (the AsyncAPI document, when the backend keeps one: `asyncapi` in `scripts/docs/docs-gen.json`) must describe every topic produced or consumed; update it in the same change. Without one, the schema files plus `docs/_generated/events.md` are the Kafka contract.
- Topics produced or consumed by external services (`market-data`, `document-service`) are listed in
  `harbor-docs/architecture/integrations.md`; check it before adding a producer or consumer.
- For "who consumes X" questions answer from `docs/_generated/events.md` - do not search the repository.
