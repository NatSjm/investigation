---
type: Feature Spec              # OKF: required
title: <Feature title>
description: <One sentence — becomes the index.md line.>
tags: [<context>]
status: draft                   # draft | stable | deprecated
generated: { by: copilot/doc-sync, at: 2026-01-01T00:00:00Z }
# verified: { by: human:<id>, at: <ISO> }     # added by a human reviewer only
# stale_after: <ISO>                          # verified + 90 days
sources: []                     # imported pages / code URLs actually read; cite claims with [^id]
# --- repo extensions ---
id: CTX-000
lang: en                       # repo language is always English
source_lang: en                # language of the imported/original source, if different
aliases: []                    # synonyms or source-language terms people search for
context: clients | meetings | imports | product1 | product2 | cover | market | stress | reports | admin
owners: [harbor-platform-team]
last_verified: null            # ISO date, set only after check vs generated/ (mirrors latest verified.at)
code_refs:                     # relative to the code repo roots, from generated/be/components.md and fe/codebase-map.md
  - be/harbor-core/src/main/kotlin/com/acme/harbor/manager/<Ctx>Manager.kt     # context entry point; other classes from generated/be/components.md
  - fe/src/pages/<Page>/<Page>.tsx                               # the page(s) of the context (contexts.yml fe list); hooks and shared pieces from fe/codebase-map.md
api: []                        # e.g. "GET /session/product1/overview"
events: []                     # Kafka topics, e.g. harbor.imports.movements-loaded
tables: []                     # DB tables
calculations: []               # /domain/calculations/<name>.md
flows: []                      # /flows/<name>.md this feature takes part in; the flow lists its specs in specs[] (both checked)
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
Screens/steps; Mermaid `flowchart` if > 3 steps. Routes from `generated/fe/routes.md`.

## API / Events
| Kind | Name | Purpose | Contract |
|---|---|---|---|
| REST | `GET /…` | | `generated/openapi/backend.yaml#/paths/~1…` |
| Kafka | `harbor.<context>.<event>` | | `generated/asyncapi/backend.yaml#/channels/harbor.<context>.<event>` |
| REST | `POST /…` | **proposed** - designed with this spec, not implemented yet | `contracts/proposed/<ID>.openapi.yaml#/paths/~1…` |

## Data
Tables/columns touched; see `generated/be/db-schema.md`.

## Calculations
Links to `domain/calculations/*.md` and which BRs they satisfy.

## Edge cases
- …

## Open questions
- [ ] …
