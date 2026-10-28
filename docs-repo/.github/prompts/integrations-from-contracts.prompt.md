---
name: integrations-from-contracts
description: Refresh architecture/integrations.md (Kafka, outbound REST, inbound REST, jobs) and the integration-facing parts of architecture/overview.md (C4 context diagram, "Contexts at a glance") from the contracts under generated/ and the generated maps; with scope overview-draft, a complete first draft of overview.md as status draft. Prose and decisions stay human-owned.
argument-hint: "product name; optional: scope = integrations | overview | both (default both) | overview-draft (whole overview page as a draft, for a repository whose overview is still the Harbor text)"
agent: architect
---
Product: ${input:product:Harbor}
Scope: ${input:scope:both}

## Role
Maintain the two architecture pages whose facts come from evidence: `architecture/integrations.md` and the
integration-facing parts of `architecture/overview.md`. You rewrite tables and diagrams from `generated/`; the prose
paragraphs, the ADR links and anything the maps cannot show (hosting, authentication, environments) are human-owned
text that you keep word for word unless a row you rewrite makes a sentence false, in which case you mark the sentence
with `> ⚠️ REVIEW (integrations refresh, <date>)` instead of rewriting it.

Scope `overview-draft` is the exception to the prose rule: it rewrites the whole `architecture/overview.md` as a first
draft (playbook section 18: human-owned documents an agent may draft) for a repository whose overview still carries the
reference text of another product. Everything the evidence cannot show is left as a marked gap, never invented. Run it in a run of its own, after a run with `scope = integrations`: the draft takes the Kafka, outbound REST and jobs rows from the refreshed `architecture/integrations.md` instead of repeating steps 1 to 4, and reads nothing else from that page.

## Inputs (read-only, in this order)
1. The two pages as they are (read them first; note which rows are `gen` and which `manual`).
2. `generated/openapi/external/*.yaml` or `*.json`: one file per external service the backend calls. Title, version,
   `servers`, every operation (`operationId`, method, path, one-line summary).
3. `generated/openapi/backend.yaml`: tags and `operationId`s of the own API (inbound table).
4. `generated/asyncapi/backend.yaml` when present, and `generated/be/events.md` always (topic, producer, consumers,
   payload type, the path of its schema file under `generated/asyncapi/schemas/` and, in the Payload schemas
   section, the fields of every schema). A producer or consumer shown as `_external_` is another system.
5. `generated/be/components.md`: the `client/*` rows (which class wraps which external contract: the `Depends on`
   column and the class name) and the `event/*` rows.
6. `generated/be/jobs.md`: scheduled jobs, cron, lock.
7. `generated/graph/REPO_MAP.md`: communities, for the "Contexts at a glance" table (entry point, tables, topics).
8. `contexts.yml` and `features/**` frontmatter only (`id`, `context`, `api`, `events`) via `search`: the owning
   feature of a row is the spec whose `api[]` or `events[]` names the operation or topic; `-` when none yet.
9. `generated/manifest.yml`: the collector run that produced the files (date for the `generated:` line) and the
   `sources:` remotes (repository names).
10. For `overview-draft` only: `generated/be/codebase-map.md` (modules with purpose and base package; layers with role,
    file count and classes), `generated/fe/codebase-map.md` (pages with route and purpose, hooks, channels),
    `generated/be/db-schema.md` or `generated/be/db/schema/index.md` (table count, first and last table name), the
    files present under `architecture/` (for the file table) and `architecture/adr/*.md` titles.
Source code: never.

## Procedure
1. **Kafka table** (`## Kafka topics`): one row per topic of `events.md` / the AsyncAPI document: schema file
   (its path relative to `generated/asyncapi/schemas/`, as `events.md` names it), topic, producer (`event/<Class>`
   or `external (<system>)`), consumers, payload (type and its fields from the Payload schemas section of
   `events.md`; the type alone when no schema file is listed), contract anchor (the AsyncAPI channel, else the schema path),
   owning feature, `gen`. A topic that is in the page but no longer in the evidence is removed and named in chat.
2. **Outbound REST table** (`## REST (outbound, external services)`): one row per file under
   `generated/openapi/external/`: system (file name), client class from `components.md` (`client/` layer; `-` and a
   chat note when no class references the contract), the operations (method and path, grouped), purpose (from the
   contract's `info.description` or the operation summaries, one phrase), contract path, owning feature, `gen`.
   A contract with no client class is still listed: it is a contract the backend holds but does not call yet.
3. **Inbound table** (`## REST (inbound, own API)`): one row per tag of `generated/openapi/backend.yaml` with its
   `operationId`s; the tag maps to a context through `contexts.yml` (name the mismatch in chat when a tag matches no
   context).
4. **Jobs table**: from `generated/be/jobs.md`; keep the `manual` effect column text when the job already has a row,
   add new jobs with the effect left as `-` for a human.
5. **Overview** (scope `overview` or `both`): in the `C4Context` diagram one `System_Ext` per external system of the
   outbound table and of the external Kafka parties, and one `Rel` per direction with the operations or topic names
   as the label (keep the people and the main system as they are); in "Contexts at a glance" refresh the entry point,
   tables and produces / consumes columns from `REPO_MAP.md` and the Kafka table. Keep the diagram under 25 nodes;
   when the external systems exceed that, group them by purpose and say so in chat.
5b. **Whole overview** (scope `overview-draft` only; replaces steps 1 to 5, the tables come from `integrations.md`): rewrite `architecture/overview.md` section by
   section, keeping its heading structure: the file table (one row per file that exists under `architecture/`, the
   `hld/` and `adr/` rows always); the repositories paragraph (names from `manifest.yml`, modules and technology from
   the two codebase maps: module purposes verbatim, frontend stack from the FE map header); the `C4Context` diagram
   (people: keep the current ones when they exist, else one `Person` per role named in `features/**` frontmatter
   or, when none, a single `Person(user, "User")` with a TODO; external systems and relations as in step 5); the
   `C4Container` diagram (one `Container` per backend module with its purpose, one for the frontend, `ContainerDb`
   with the table count, `ContainerQueue` with the topic count and topic prefixes, one `System_Ext` for the external
   systems; relations from the layers that exist: `dao` -> database, `event` / `client/kafka` -> queue, `client/rest`
   -> external systems); the layers table (one row per layer of the BE codebase map with its role column verbatim
   and up to two class names as examples; merge sub-layers of one parent into one row); "Contexts at a glance" as
   in step 5; "Cross-cutting rules": keep only the rules the evidence supports (contract-first when a contract
   exists and controllers carry the `*Api` kind in `components.md`; layers and prefixes from `contexts.yml`; pure
   calculations when a `utils` layer exists), each linked to an ADR only when that ADR file exists; every other
   rule of the old text becomes one line `> ❓ TODO (human): <topic>` (hosting, authentication, session scoping,
   environments). Set `status: draft`, `title` and `description` for this product, `tags` kept; remove every
   reference to the reference product's names, IDs and files.
6. **Frontmatter**: `generated: { by: copilot/architect, at: <now> }`, `sources[]` listing every file you read with
   its `generated/manifest.yml` entry when it has one; keep `status` as it is unless rows changed, then `status: draft`
   until a human re-verifies. Do not touch `verified`.
7. Finish with `python3 scripts/okf-validate.py --strict` and `python3 scripts/build-index.py`;
   add one `log.md` line.

## Output
**A.** The edited page(s). **B. In chat, under 15 lines:** rows added, removed or changed per table; contracts
without a client class; topics with an external party; tags matching no context; sentences marked REVIEW; for
`overview-draft` the list of TODO gaps a human must fill.

## Rules
- Every row cites evidence under `generated/`; nothing comes from memory or from source code.
- Numbers, paths and names verbatim from the files; no product names other than this product's; no client data.
- Do not edit any other file; do not edit `generated/**`; do not run the generators or the collector.
