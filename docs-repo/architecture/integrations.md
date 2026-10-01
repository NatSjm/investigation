---
type: Integration Map
title: Integrations map
description: Kafka topics and REST integrations (inbound/outbound) with producers, consumers, schemas and owning features; generated rows refreshed from AsyncAPI/OpenAPI.
tags: [architecture, integration, kafka]
status: draft
generated: { by: process:be-ci, at: 2026-09-30T19:00:00Z }
stale_after: 2026-10-30T00:00:00Z
sources:
  - { id: asyncapi, resource: /generated/asyncapi/be.yaml, title: AsyncAPI (springwolf) }
  - { id: openapi, resource: /generated/openapi/be.yaml, title: OpenAPI (springdoc) }
---

# Integrations map

Rows marked `gen` are refreshed by `scripts/build-integrations.ps1` from `generated/asyncapi` and
`generated/openapi`; rows marked `manual` are maintained by hand.

## Kafka topics
| Topic | Direction | Producer | Consumer | Schema | Feature | Src |
|---|---|---|---|---|---|---|
| `advisory.hedge.proposal.created` | out | BE hedge module | Reporting, CRM sync | `generated/asyncapi/be.yaml#HedgeProposalCreated` | HEDGE-001 | gen |
| `core.loan.updated` | in | Core banking | BE loans module | external | LOAN-0xx | gen |

## REST (outbound)
| System | Endpoint | Purpose | Auth | Feature | Src |
|---|---|---|---|---|---|
| Market data | `GET /rates/{ccy}` | fixings for calculations | mTLS | CALC-0xx | manual |
| CRM | `GET /clients/{id}` | client master data | OAuth2 | — | manual |

## REST (inbound, own API)
See `generated/openapi/be.yaml` — grouped by tag = bounded context.
