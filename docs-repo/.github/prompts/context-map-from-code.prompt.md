---
name: context-map-from-code
description: Draft domain/context-map.md (bounded contexts, prefixes, relationships) and a proposed contexts.yml from the backend and frontend source, before the collector has run. Evidence only; the human verifies.
argument-hint: "product name; optional: backend path, frontend path, reference context map"
agent: architect
---
Product: ${input:product:Harbor}
Backend repository: ${input:backend:../harbor-backend}
Frontend repository: ${input:frontend:../harbor-frontend}
Reference format: ${input:reference:domain/context-map.md of the investigation repository}

## Role
Draft one document for this repository: `domain/context-map.md`, the map of bounded contexts of the product.
The document is human-owned; you produce a draft a human will verify. Think thoroughly before writing, but write
only what the evidence shows.

## Inputs (read-only)
- This repository: `AGENTS.md`, `features/conventions.md`, `contexts.yml` (may be a placeholder), `docs-map.yml`,
  `domain/glossary.md`, `architecture/overview.md`, `architecture/integrations.md`.
- Backend repository: Kotlin/Spring, layered packages (`api`, `manager`, `service`, `dao`, `event`, `job`, `utils`,
  `client`, `config`, `enums`, `model`, ...). The business area of a class is in its NAME PREFIX, not its folder.
- Frontend repository: React/TypeScript, one folder per routed page (`src/pages/<Page>/` with `hook/` and `components/`), routes in `src/routing/`, shared pieces in `src/pages/shared/` and `src/components/`.
- Optional: a Confluence export folder, for page titles only, never as a source of rules.
- Reference format: copy the STRUCTURE of the reference file exactly (frontmatter keys, the intro bullets, the table
  columns, the "shared" paragraph, the Mermaid flowchart, the "Relationship notes" list). Replace all content with
  the product's own. Keep none of the reference's names.

## Investigation (all of it, before writing)
1. **Backend inventory.** Every class under the layered packages with simple name, layer and file path. Group
   classes by shared name prefix (longest meaningful prefix). Per group: the manager or service that is its entry
   point, controllers and their routes, DAOs and the tables they touch, Kafka topics produced or consumed (event
   package, kafka client module, `resources/openapi` or asyncapi files), external clients.
2. **Frontend inventory.** Every page folder under `src/pages/`, the JSDoc of its page component, the routes that
   render it (`src/routing/*.tsx`, route constants in `src/constants/`), the API hooks it owns (`hook/use*.ts`) and the backend routes they call, BroadcastChannel
   or other cross-window channels if any.
3. **Cross-context evidence.** Constructor injections across prefix groups (A depends on B), tables read by several
   groups, topics published by one group and consumed by another, session or request headers that scope several
   groups, parameters copied or snapshotted.
4. **Product types.** If the product has several product types chosen per session, treat a product type as a
   DIMENSION inside a capability context, not as a context, unless the code has a class family that exists for one
   product type only. State for every context which product types it serves and on what evidence (enum, prefix,
   folder, route).
5. **Candidate contexts.** One per prefix group that has an entry point and user-facing behaviour (routes, pages,
   jobs or topics). Classes matching no group are `shared` (configuration, enums, utils helpers, generic clients,
   libraries). A shared service used by several contexts stays shared; say who uses it in the relationship notes.

## Output
**A. `domain/context-map.md`**, in English:
- frontmatter: `type: Document`, `title`, `description` (one sentence naming every context),
  `tags: [domain, architecture]`, `status: draft`, `generated: { by: copilot/architect, at: <ISO timestamp> }`.
  No other keys.
- the table: Context | Spec prefix | BE class-name prefixes | Backend entry point | FE feature / routes | Specs.
  Spec prefix: 2-3 uppercase letters, unique. Specs column: `missing (<PREFIX>-001 backlog)` for every context
  without a spec. Backend entry point and FE feature cells are real file paths or route paths you saw.
- the `shared` paragraph listing the actual unprefixed classes.
- the Mermaid flowchart: one node per context, one edge per relationship you have evidence for, the edge label
  naming the evidence (topic, table, header, injected class). Group session-scoped contexts in a subgraph if a
  session or request scope exists. External systems as dotted edges. Under 25 nodes.
- Relationship notes: one bullet per edge with the DDD relationship kind (customer/supplier, published language,
  shared kernel, conformist, anti-corruption layer) and the `file:line` that proves it.
- a final `## Open questions` list: every place where the evidence was missing or ambiguous, as a checkbox item
  naming what a human must decide (for example: "cover: own context or part of product1? `Cover*` classes are used
  by `Product1*` and `Stress*`; no manager of their own").

**B. A proposed `contexts.yml`** in the format of this repository's current file: one line per context with `spec`,
`fe` folder and the list of `be` prefixes. Prefixes must not overlap ambiguously; where two groups share a prefix
start, list the longer one so that longest-match wins. Present it as a proposal for section 4 of the playbook; do
not overwrite the existing file.

**C. A report in chat (under 25 lines):** contexts found, product-type handling per context, the five most
important open questions, and anything in the code that contradicts the Confluence page structure.

## Rules
- Evidence only. Where the code does not show a relationship, write "unknown" in the notes and add an open
  question. Never infer a dependency from a name, a comment or the Confluence tree.
- Every path and route you cite must exist in the repositories as read. Quote `file:line` for relationships.
- Do not edit any other file. Do not create specs, calculations or flows. Do not run scripts; the human runs
  `okf-validate` on the draft.
- No client data, credentials or environment URLs in the document.
- One table row per context.
