---
type: Document
title: Kafka events (BE)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# Kafka events (BE)

> Generated from `@KafkaListener / KafkaTemplate.send scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
3 topic(s). Payload schema: open the event class named in the handler signature.

| Topic | Producers (this repo) | Consumers (this repo) |
|---|---|---|
| `client.kyc.changed` | _external_ | `onKyc` (hedges/src/main/kotlin/com/bank/adv/hedges/messaging/HedgeEvents.kt:22, group hedges) |
| `hedge.proposal.created` | `HedgeEventPublisher` (hedges/src/main/kotlin/com/bank/adv/hedges/messaging/HedgeEvents.kt:14) | _external_ |
| `market.rates.updated` | _external_ | `onRates` (hedges/src/main/kotlin/com/bank/adv/hedges/messaging/HedgeEvents.kt:19, group hedges) |
