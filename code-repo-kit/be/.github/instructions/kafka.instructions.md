---
applyTo: "**/messaging/**/*.kt"
---
# Kafka messaging

- Topic names only via `Topics.<CONST>`; `gen-events.ps1` resolves constants - literals break the catalogue.
- `@KafkaListener` must set `groupId`; handler signature names the event class (used as the payload reference in docs).
- Event classes are immutable `data class`es with a `version: Int`; breaking changes = new topic suffix (`.v2`).
- Cross-service contracts live in `advisory-docs/architecture/integrations.md`; check it before adding a producer.
- For "who consumes X" questions, answer from `docs/_generated/events.md` - do not grep the repo.
