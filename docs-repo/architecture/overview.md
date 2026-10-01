---
type: Architecture View
title: Architecture overview (arc42-lite, C4 context)
description: How architecture documentation is organised (context, containers, components, runtime, deployment, ADRs, HLDs) plus the C4 context diagram.
tags: [architecture]
status: stable
generated: { by: human:platform-team, at: 2026-09-30T19:00:00Z }
---

# Architecture

arc42-lite structure. Diagrams are Mermaid (renders in GitHub/GitLab/IDE; no binary files).

| File | Content |
|---|---|
| `01-context.md` | C4 level 1: system, users, external systems |
| `02-containers.md` | C4 level 2: FE, BE, PostgreSQL, Kafka, external services |
| `03-components.md` | C4 level 3 per bounded context (generated skeleton from `codebase-map.md`) |
| `04-runtime.md` | key sequences: proposal creation, monthly run, stress test |
| `05-deployment.md` | environments, topology |
| [integrations.md](/architecture/integrations.md) | table of REST/Kafka integrations (partly generated from AsyncAPI/OpenAPI) |
| `hld/<ID>.md` | high-level designs per feature/epic (agent `architect`) |
| `adr/` | Architecture Decision Records, e.g. [ADR-0001](/architecture/adr/0001-docs-as-code.md) |

## C4 Context (example)

```mermaid
C4Context
  title Financial Advisory Platform — context
  Person(advisor, "Advisor")
  Person(admin, "Risk admin")
  System(fap, "Advisory Platform", "React + Kotlin Spring + PostgreSQL")
  System_Ext(core, "Core banking", "loans master data")
  System_Ext(market, "Market data", "rates, fixings")
  System_Ext(crm, "CRM", "clients, meetings")
  SystemQueue_Ext(kafka, "Kafka", "events")
  Rel(advisor, fap, "prepares proposals")
  Rel(admin, fap, "configures limits, scenarios")
  Rel(fap, core, "reads loans")
  Rel(fap, market, "reads rates")
  Rel(fap, crm, "reads clients")
  Rel(fap, kafka, "publishes/consumes events")
```
