---
type: Document
title: Feature spec conventions
description: Bounded-context prefixes, ID scheme, how a context is cut into specs (screens, modals, product types), business-rule numbering, size caps, section order and folder layout for feature specs under features/.
tags: [conventions]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# Features

Functional specs (`type: Feature Spec`), one per user capability, grouped by bounded context: one folder per
context, named exactly like the context in `/contexts.yml` and the frontend feature folder; backend classes of
the context carry the class-name prefixes listed there (the backend is layered, so there is no backend folder per
context). A context usually holds several specs: its main screen and the capabilities carved out of it
(section "Shaping specs").

## ID scheme

`<CTX>-<NNN>` — context prefix, dash, three digits (`P1-001`, `STR-014`). File name = `<ID>.md`. IDs are never
reused. A capability carved out of an existing spec gets the next free number of the context, never a letter
suffix (`validate-frontmatter.py` accepts digits only); the rules that move get new IDs in the new spec and the
old rule keeps its number with the text "withdrawn, moved to BR-<new>".

| Context | Prefix | Folder | BE class-name prefixes (`contexts.yml`) / FE feature |
|---|---|---|---|
| Clients | `CLI` | `clients/` | `Client*` / `clients` |
| Meetings | `SES` | `meetings/` | `Session*`, `Meeting*`, `RoleOverride*` / `meetings` |
| Imports | `IMP` | `imports/` | `Import*`, `Movement*`, `GoodsMovement*`, `Xls*`, `Workbook*`, `DailyMovement*`, `MonthlySnapshot*` / — |
| Product 1 | `P1` | `product1/` | `Product1*`, `Projection*`, `Peer*`, `MovementInput*` / `product1` |
| Product 2 | `P2` | `product2/` | `Product2*` / `product2` |
| Cover | `COV` | `cover/` | `Cover*` / `cover` |
| Market | `MKT` | `market/` | `Market*`, `Scenario*`, `BaselinePrice*` / `market` |
| Stress test | `STR` | `stress/` | `Stress*` / `stress` |
| Reports | `RPT` | `reports/` | `Report*` / `reports` |
| Admin | `ADM` | `admin/` | `Admin*`, `Parameter*` / `admin` |

Choose a prefix once, from the word the code and the business both use for the context; it ends up in file
names, rule IDs, `@docs` tags, Jira keys and test names, and renaming it later touches all of them.

## Shaping specs

Decisions taken before Run 1 of a context, by the migration lead with a developer who knows the code:

1. **Contexts follow the code, not the menu.** A context is a class-name prefix family plus a frontend feature
   folder. The navigation menu and the Confluence page tree are presentation; they are reproduced with `tags`,
   `aliases`, the manual block of `index.md` and the publish map, never by folders under `features/`.
2. **The first spec of a context is its main screen** (`<CTX>-001`): what the screen shows (tables, charts,
   inputs, filters), which button opens which modal, what each action calls. The UI flow diagram is the
   screen; the business rules are what must hold for what is shown.
3. **A modal or sub-capability gets its own spec** (`<CTX>-002`, ...) as soon as it has rules of its own, or
   when the screen spec would exceed the size caps. The screen spec keeps the modal in its UI flow diagram and
   cites the rules of the modal spec by ID; it never restates them. Example: `P1-001` (overview screen),
   `P1-002` (movement modal), `P1-003` (peer simulation modal).
4. **Ownership is by rule, not by component.** A component shared by several screens or contexts (one modal
   that changes the client and the positions, a table reused by two products) is documented once in the UI
   flow of the screen that renders it; each half of its behaviour is a rule of the context that owns that
   behaviour, cited by ID. The component file is listed in the `code_refs` of the screen spec only.
5. **Product types are a dimension, not a context**, unless the code has a class family that exists for one
   product only. Then (a) one screen serving both products is one spec with a dimension rule (`STR-001`
   BR-5: city for Product 1, transport mode for Product 2); (b) a product-specific class family is its own
   context and the product's screens and modals are specs in it (`product1/`, `product2/`); (c) a mirrored
   spec restates nothing: a rule identical to the other product's reads "as BR-P1-002-1, with transport mode
   as dimension" and keeps its own ID so tests and stories can cite it (`P2-002`).
6. **Behaviour across contexts is a flow**, never a rule repeated in several specs: the session journey
   across the product, scenario and stress screens, or the recalculation chain that one input change triggers
   (`/flows/`). Each spec keeps its local rule; the flow composes them and lists the specs in `specs[]`.
7. **Formulas are calculation documents.** A table column or chart series names the quantity it shows; the
   quantity is a file under `domain/calculations/` with inputs, parameters, formula, worked examples from the
   unit test and an audit table. One document per output quantity, not per table.
8. **Screenshots are optional illustrations.** If used: under the Mermaid diagram of the UI flow, file in
   `/assets/<ID>/`, synthetic data only, caption with dataset and capture date, refreshed by the human
   reviewer at Run 4. Agents do not read them; the rules stay authoritative.

## Business rules

- Numbered `BR-<ID>-<n>` starting at 1, never renumbered; a withdrawn rule stays with the text "withdrawn, see …"
  or "withdrawn, moved to BR-<new>".
- Each rule is **one testable MUST / MUST NOT statement**; work items (`acceptance_criteria[].rule`) and Gherkin
  tags (`@BR-<ID>-<n>`) cite the rule, so a rule must not contain two independent assertions.
- Claims are backed by `sources[]` entries and footnotes whose label equals a `sources[].id` (manager file,
  controller, legacy page).

## Size caps

- ≤ 300 lines per spec (CI warns at 250); carve a capability out into the next free ID beyond that.
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
- Other specs: a rule of another spec is cited by ID (`BR-CLI-001-3`) and the spec by root-relative link
  (`/features/clients/CLI-001.md`); never copy its text.
- Flows: `flows: [/flows/<name>.md]` lists the cross-context flows the feature takes part in; the flow lists the same
  specs in its `specs:`. `validate-frontmatter.py` checks both directions and the context pack includes the flow's
  Purpose, Trigger, Participants, Steps and Invariants.
- Parameters: a feature that reads an admin parameter names the key in a business rule (for example `peer.scaling_default`);
  the calculation that uses it owns the meaning in its `## Parameters` table; `ADM-001` owns scope, versioning and
  validation and maps keys to owners. Keys must exist in `generated/be/parameters.md` (`validate-frontmatter.py`).
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
| ongoing | `doc-sync` on each generated-diff PR; `analyst` consumes via `context-pack.py` | generated diff, pack | Change log row, `last_verified` | stays `stable` or back to `draft` if a BR changed |

Skill: `.github/skills/spec-lifecycle/SKILL.md` (with a per-run review checklist). Which runs are still due per
context: `python3 scripts/migration-status.py --scope all` -> `migration/all.md` (agent `migration-lead`).

Run 1 may be done in batch for all "code only" contexts (`generated/graph/REPO_MAP.md`) by assigning one issue per
context to the Copilot coding agent, which opens one PR each. Runs 2 to 4 stay interactive: every legacy page needs
a human judgement on conflicts. The agentStop hook validates the bundle after every run
(`build-index`, `okf-validate --strict`, `validate-frontmatter`, `validate-work-items`).

Template: `_template.md`. Rules: `.github/instructions/features.instructions.md`.
Index of all specs is generated by `scripts/build-index.py` into each folder's `index.md`.
