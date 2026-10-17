---
name: integrations-from-contracts
description: Refresh architecture/integrations.md (Kafka, outbound REST, inbound REST, jobs) and the integration-facing parts of architecture/overview.md (C4 context diagram, "Contexts at a glance") from the contracts under generated/ and the generated maps; prose and decisions stay human-owned.
argument-hint: "product name; optional: scope = integrations | overview | both (default both)"
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

## Inputs (read-only, in this order)
1. The two pages as they are (read them first; note which rows are `gen` and which `manual`).
2. `generated/openapi/external/*.yaml` or `*.json`: one file per external service the backend calls. Title, version,
   `servers`, every operation (`operationId`, method, path, one-line summary).
3. `generated/openapi/backend.yaml`: tags and `operationId`s of the own API (inbound table).
4. `generated/asyncapi/backend.yaml` when present; else `generated/be/events.md` (topic, producer, consumers, payload
   type and the path of its schema file). A producer or consumer shown as `_external_` is another system.
5. `generated/be/components.md`: the `client/*` rows (which class wraps which external contract: the `Depends on`
   column and the class name) and the `event/*` rows.
6. `generated/be/jobs.md`: scheduled jobs, cron, lock.
7. `generated/graph/REPO_MAP.md`: communities, for the "Contexts at a glance" table (entry point, tables, topics).
8. `contexts.yml` and `features/**` frontmatter only (`id`, `context`, `api`, `events`) via `search`: the owning
   feature of a row is the spec whose `api[]` or `events[]` names the operation or topic; `-` when none yet.
9. `generated/manifest.yml`: the collector run that produced the files (date for the `generated:` line).
Source code: never.

## Procedure
1. **Kafka table** (`## Kafka topics`): one row per topic of `events.md` / the AsyncAPI document: schema file,
   topic, producer (`event/<Class>` or `external (<system>)`), consumers, payload (type and its fields when the
   schema file is listed; otherwise the type alone), contract anchor (the AsyncAPI channel, else the schema path),
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
6. **Frontmatter**: `generated: { by: copilot/architect, at: <now> }`, `sources[]` listing every file you read with
   its `generated/manifest.yml` entry when it has one; keep `status` as it is unless rows changed, then `status: draft`
   until a human re-verifies. Do not touch `verified`.
7. Finish with `python3 scripts/okf-validate.py --strict` and `python3 scripts/build-index.py`; add one `log.md` line.

## Output
**A.** The edited page(s). **B. In chat, under 15 lines:** rows added, removed or changed per table; contracts
without a client class; topics with an external party; tags matching no context; sentences marked REVIEW.

## Rules
- Every row cites evidence under `generated/`; nothing comes from memory or from source code.
- Numbers, paths and names verbatim from the files; no product names other than this product's; no client data.
- Do not edit any other file; do not edit `generated/**`; do not run the generators or the collector.
