---
type: Feature Spec              # OKF: required
title: <Feature title>
description: <One sentence — becomes the index.md line.>
tags: [<context>]
status: draft                   # draft | stable | deprecated
generated: { by: copilot/doc-sync, at: 2026-01-01T00:00:00Z }
# verified: { by: human:<id>, at: <ISO> }     # added by a human reviewer only
# stale_after: <ISO>                          # verified + 90 days
sources: []                     # Confluence pages / code URLs actually read; cite claims with [^id]
# --- repo extensions ---
id: CTX-000
lang: en                       # repo language is always English
source_lang: cs                # language of the Confluence/original source, if different
aliases: []                    # Czech (or other) terms people search for, e.g. [zajištění, úrokový swap]
context: hedges | loans | stress-test | monthly-calc | graphs | admin | integration
owners: [team-or-person]
last_verified: null            # ISO date, set only after check vs generated/ (mirrors latest verified.at)
code_refs:                     # relative to FE/BE repo roots, from generated/codebase-map.md
  - be/src/main/kotlin/...
  - fe/src/features/...
api: []                        # e.g. "GET /hedges/{id}"
events: []                     # Kafka topics
tables: []                     # DB tables
calculations: []               # /domain/calculations/<name>.md
jira: { epic: null }
tests: []                      # test-design/features/<ID>.feature
---

# <ID> — <Feature title>

## Summary
One paragraph: who, what, why (business value).

## Actors
| Actor | Role in this feature |
|---|---|

## Business rules
- **BR-<ID>-1** — The system MUST …
- **BR-<ID>-2** — The system MUST NOT …

## UI flow
Screens/steps; Mermaid `flowchart` if > 3 steps.

## API / Events
| Kind | Name | Purpose | Contract |
|---|---|---|---|
| REST | `GET /…` | | `generated/openapi/be.yaml#/paths/…` |
| Kafka | `topic.name` | | `generated/asyncapi/be.yaml#/channels/…` |

## Data
Tables/columns touched; link `generated/db/schema.md#table`.

## Calculations
Links to `domain/calculations/*.md` and which BRs they satisfy.

## Edge cases
- …

## Open questions
- [ ] …

## Change log
| Date | Change | Ref |
|---|---|---|
