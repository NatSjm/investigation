---
type: Flow                      # cross-context behaviour: more than one bounded context or more than one window / process
title: <Flow title>
description: <One sentence - becomes the index.md line.>
tags: [flow, <context1>, <context2>]
status: draft
generated: { by: copilot/<agent>, at: 2026-01-01T00:00:00Z }
# verified: { by: human:<id>, at: <ISO> }
# stale_after: <ISO>
sources: []
# --- repo extensions ---
id: FLOW-<slug>
contexts: [<context1>, <context2>]      # from /contexts.yml
specs: [<CTX>-001, <CTX>-002]           # specs whose rules this flow composes
code_refs: []                           # entry points only, from the graph (file:line)
channels: []                            # BroadcastChannel / Kafka topics / external calls crossed
---

# <Flow title>

## Purpose
Why this behaviour exists and who triggers it. One paragraph.

## Questions this document answers
- …
- …

## Trigger
What starts the flow (user action, job, event) and its precondition.

## Participants
| Participant | Kind | Role in the flow |
|---|---|---|
| `feature:<x>` / `class:<Y>` / `channel:<name>` | FE feature / BE class / channel | |

## Steps
Numbered; each step names the node and `file:line` from the graph. Mermaid `sequenceDiagram` if > 5 steps (<= 25 nodes).

## Data and state changes
Which tables, caches or window state change, and when.

## Failure behaviour
What the user sees and what is retried / rolled back when a step fails or a window closes.

## Invariants and assumptions
- The flow MUST … (cite `BR-<ID>-<n>` where a spec owns the rule)

## Security and privacy notes
What must never cross this boundary (e.g. internal indicators never reach the client window).

## Source map
| Concern | Location |
|---|---|

## Open questions
- [ ] …

## Change log
| Date | Change | Ref |
|---|---|---|
