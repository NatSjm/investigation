---
type: Decision
title: "ADR-0001: Documentation as code in a dedicated repository"
description: Keep all functional/technical docs of Harbor as an OKF bundle in a separate Git repo (harbor-docs) fed by backend/frontend CI artifacts, consumed by Copilot agents, published one-way to Confluence.
tags: [adr, docs]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# ADR-0001: Documentation as code in a dedicated repository

- **Status**: Accepted
- **Date**: 2026-10-09
- **Deciders**: harbor-platform-team
- **Related**: [ADR-0002](/architecture/adr/0002-openapi-first-contracts.md), `features/conventions.md`

## Context
Documentation of Harbor lives in Confluence and drifts from the code: the legacy pages under
`confluence-import/HARBOR/` describe thresholds and flows that the code no longer implements. We need docs that
(a) stay in sync with `harbor-backend` and `harbor-frontend`, (b) feed analysis, Jira work items and automated
tests, (c) are consumable by GitHub Copilot with low token cost. MCP servers and third-party agent frameworks are
not permitted; Copilot custom instructions, agents, prompts and skills are.

## Decision
Create a separate `harbor-docs` repository as the single source of truth (Markdown + Mermaid + YAML), structured
as an **Open Knowledge Format v0.2 bundle** (typed concepts, trust/provenance/lifecycle frontmatter, `index.md`
progressive disclosure), with: generated artifacts published by backend/frontend CI into `generated/`,
Copilot agents/skills/prompts for downstream artefacts, quality gates in CI (`okf-validate.py --strict`,
`build-index.py --check`, `check-freshness.py` against `docs-map.yml`), one-way publishing to Confluence via REST
scripts.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Keep Confluence as source | no migration | no diff/review, no CI, poor for Copilot, drift continues |
| Docs inside the backend repo | close to code | frontend docs split; huge context for Copilot; access coupling |
| Docs repo (chosen) | reviewable, CI-checkable, small context, tool-agnostic | requires CI wiring + migration effort |
| Wiki (GitHub/GitLab wiki) | simple | weak CI/PR flow, no folder structure conventions |

## Consequences
+ Traceability spec → Jira → tests via IDs (`<CTX>-<NNN>`, `BR-<ID>-<n>`). + Cheap Copilot context via `generated/`
  and `scripts/context-pack.py --task <ID>`.
− Initial migration effort; discipline to keep `docs-map.yml` updated (enforced by the CI freshness gate).
