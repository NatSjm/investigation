---
type: Document
title: Feature spec conventions
description: Bounded-context prefixes, ID scheme, business-rule numbering, size caps, section order and folder layout for feature specs under features/.
tags: [conventions]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# Features

Functional specs, one per feature ID (`type: Feature Spec`), grouped by bounded context. One folder per context,
named exactly like the context in `/contexts.yml` and the frontend feature; backend classes of the context carry
the class-name prefixes listed there (the backend is layered, so there is no backend folder per context).

## ID scheme

`<CTX>-<NNN>` — context prefix, dash, three digits (`P1-001`, `STR-014`). A sub-feature split out of a spec that
grew past the size cap gets a letter suffix (`P1-001a`). File name = `<ID>.md`. IDs are never reused.

| Context | Prefix | Folder | BE class-name prefixes (`contexts.yml`) / FE feature |
|---|---|---|---|
| Clients | `CLI` | `clients/` | `Client*` / `clients` |
| Meetings | `MTG` | `meetings/` | `Session*`, `Meeting*`, `RoleOverride*` / `meetings` |
| Imports | `IMP` | `imports/` | `Import*`, `Movement*`, `GoodsMovement*`, `Xls*`, `Workbook*`, `DailyMovement*`, `MonthlySnapshot*` / — |
| Product 1 | `P1` | `product1/` | `Product1*`, `Projection*`, `Peer*`, `MovementInput*` / `product1` |
| Product 2 | `P2` | `product2/` | `Product2*` / `product2` |
| Cover | `COV` | `cover/` | `Cover*` / `cover` |
| Market | `MKT` | `market/` | `Market*`, `Scenario*`, `BaselinePrice*` / `market` |
| Stress test | `STR` | `stress/` | `Stress*` / `stress` |
| Reports | `RPT` | `reports/` | `Report*` / `reports` |
| Admin | `ADM` | `admin/` | `Admin*`, `Parameter*` / `admin` |

## Business rules

- Numbered `BR-<ID>-<n>` starting at 1, never renumbered; a withdrawn rule stays with the text "withdrawn, see …".
- Each rule is **one testable MUST / MUST NOT statement**; work items (`acceptance_criteria[].rule`) and Gherkin
  tags (`@BR-<ID>-<n>`) cite the rule, so a rule must not contain two independent assertions.
- Claims are backed by `sources[]` entries and footnotes whose label equals a `sources[].id` (manager file,
  controller, legacy page).

## Size caps

- ≤ 300 lines per spec (CI warns at 250); split into `<ID>a`, `<ID>b` beyond that.
- ≤ 12 business rules per spec; ≤ 1 Mermaid diagram per section.
- Worked numbers live in `domain/calculations/`, never in a spec.

## Sections (fixed order)

Summary → Actors → Business rules → UI flow → API / Events → Data → Calculations → Edge cases →
Open questions → Change log. Keep empty sections with "none".

## References inside a spec

- Endpoints: `METHOD /path` exactly as in `generated/openapi/backend.yaml`, contract anchor
  `generated/openapi/backend.yaml#/paths/~1session~1product1~1overview`.
- Topics: exact names from `generated/asyncapi/backend.yaml#/channels/<topic>`.
- Operations or topics that exist only as a design: contract column `contracts/proposed/<ID>.openapi.yaml#/paths/...`
  and the word **proposed** in the Purpose column; switched to the `generated/` anchor by `doc-sync` once implemented
  (`contracts/conventions.md`).
- Tables: names from `generated/be/db-schema.md`.
- Code: `code_refs` relative to the repo roots with prefix `be/` (harbor-backend) or `fe/` (harbor-frontend).

## Lifecycle of one spec (run by run)

A spec is written part by part: one Copilot agent run per part, a short human review of the diff after each run,
one commit per run. Runs are chained by the handoff buttons of the agents, not by an automated pipeline.

| Run | Who / how | Reads | Writes | Spec state after |
|---|---|---|---|---|
| 1 Skeleton | `/spec-skeleton-from-graph <context> <ID>` (agent `spec-writer`) | context pack: `generated/graph/<context>.md`, contracts, the manager KDoc only | `features/<ctx>/<ID>.md` (API / Events / Data / UI flow / Calculations from the graph; Summary / Actors / BRs from the manager), `docs-map.yml`, `log.md` | `status: draft`, open questions listed, badge *draft* |
| 2 Legacy merge | `@confluence-migrator confluence-import/<SPACE>/<page>.md`, one page per run | the page, the pack | new facts merged, `⚠️ CONFLICT` / `❓ UNVERIFIED` callouts, `sources[]` entry, glossary terms, page moved to `_done/` | still `draft`; legacy claims traceable |
| 3 Calculations | handoff "Audit the linked calculations" (agent `calc-auditor`) | calculator class + its unit test, nothing else | `## Audit <date>` table in `domain/calculations/<name>.md`, open questions with an owner | calculation `draft` until all rows `MATCH` |
| 4 Owner decision | human | open questions | decisions in the Change log, `verified: { by: human:<id>, at }`, `stale_after` | `status: stable`, badge *human-reviewed* |
| ongoing | `doc-sync` on each generated-diff PR; `analyst` consumes via `context-pack.ps1` | generated diff, pack | Change log row, `last_verified` | stays `stable` or back to `draft` if a BR changed |

Skill: `.github/skills/spec-lifecycle/SKILL.md` (with a per-run review checklist). Which runs are still due per
context: `./scripts/migration-status.ps1 -Scope all` -> `migration/all.md` (agent `migration-lead`).

Run 1 may be done in batch for all "code only" contexts (`generated/graph/REPO_MAP.md`) by assigning one issue per
context to the Copilot coding agent, which opens one PR each. Runs 2 to 4 stay interactive: every legacy page needs
a human judgement on conflicts. The agentStop hook validates the bundle after every run
(`build-index`, `okf-validate -Strict`, `validate-frontmatter`, `validate-work-items`).

Template: `_template.md`. Rules: `.github/instructions/features.instructions.md`.
Index of all specs is generated by `scripts/build-index.ps1` into each folder's `index.md`.
