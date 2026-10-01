---
type: Decision
title: "ADR-0001: Documentation as code in a dedicated repository"
description: Keep all functional/technical docs as an OKF bundle in a separate Git repo fed by FE/BE CI artifacts, consumed by Copilot agents, published one-way to Confluence.
tags: [adr, docs]
status: draft
generated: { by: human:platform-team, at: 2026-09-30T19:00:00Z }
---

# ADR-0001: Documentation as code in a dedicated repository

- **Status**: Proposed
- **Date**: 2026-09-30
- **Deciders**: platform team
- **Related**: `INVESTIGATION.md`

## Context
Documentation lives in Confluence and drifts from the code. We need docs that (a) stay in sync with FE/BE,
(b) feed analytics, Jira work items and automated tests, (c) are consumable by GitHub Copilot with low token
cost. MCP servers and third-party agent frameworks are not permitted; Copilot custom instructions/agents/skills are.

## Decision
Create a separate `docs` repository as the single source of truth (Markdown + Mermaid + YAML), structured as an
**Open Knowledge Format v0.2 bundle** (typed concepts, trust/provenance/lifecycle frontmatter, `index.md`
progressive disclosure), with: generated artifacts published by FE/BE CI, Copilot agents/skills/prompts for
downstream artefacts, quality gates in CI, one-way publishing to Confluence via REST scripts.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Keep Confluence as source | no migration | no diff/review, no CI, poor for Copilot, drift continues |
| Docs inside BE monorepo | close to code | FE docs split; huge context for Copilot; access/permission coupling |
| Docs repo (chosen) | reviewable, CI-checkable, small context, tool-agnostic | requires CI wiring + migration effort |
| Wiki (GitHub/GitLab wiki) | simple | weak CI/PR flow, no folder structure conventions |

## Consequences
+ Traceability spec → Jira → tests via IDs. + Cheap Copilot context via `generated/`.
− Initial migration effort; discipline to keep `docs-map.yml` updated (enforced by CI check).
