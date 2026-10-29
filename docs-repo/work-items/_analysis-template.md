---
request: <slug>                      # lowercase kebab-case; file name of this document and of <slug>.yml
title: "<the request in one line>"
status: draft                        # draft (agent's reading) | confirmed (the analyst agreed with the Reading) | superseded
generated: { by: copilot/analyst, at: <ISO> }
contexts: [<context>, <context>]     # from generated/catalogue.md
specs: [<ID>, <ID>]                  # every spec the request touches; new ones appear here once spec-writer drafted them
flows: [/flows/<name>.md]            # flows the request follows or changes; a new flow is a gap below until written
pack: .context/<slug>.md             # the pack this analysis was written from (rebuild: the command in Sources)
---

# <title>

## Request
> The request as it was given, verbatim (or the question, for a question).

## Reading
One paragraph: what the request means in the vocabulary of `domain/glossary.md`, which contexts it spans and why.
End with the line the analyst confirms: **I read this as: <subject 1> + <subject 2> + new <piece> in <context> - right?**

## Parts
One row per distinct piece of the request. `State`: `unchanged` (already behaves so - cite the rule), `changed`
(an existing rule or screen changes), `new` (nothing in the bundle does it). Evidence from the pack: rule IDs,
calculation names, flow steps, graph node ids with `file:line`; or `code-read <file:line>` for a range read under
steps 6 and 7 of the task-context skill (unverified: it is also an Open question in the spec until a rule says the
same).

| # | Part of the request | State | Context | Owner (spec / calculation / flow) | Evidence |
|---|---|---|---|---|---|
| 1 | | | | | |

## Trust
Badges of every spec, calculation and flow used (`human-reviewed`, `draft`, `unverified`, `STALE`). Anything not
`human-reviewed` makes the stories derived from it `needs-spec-review`.

## What is reused, what changes, what is built
- **Reused as is**: calculations, endpoints, tables, components the request can take unchanged (name them).
- **Changed**: the rule / endpoint / table / component and what changes in it (one line each).
- **Built**: new calculation (inputs from which tables and existing outputs), new endpoint (in which existing
  controller, or a new service and why), new table, new screen or component, new topic.

## Contracts
Changed operations (operationId), new operations in existing controllers, new services; each new operation gets a
proposal under `contracts/proposed/` (`contracts/conventions.md`) cited as **proposed**.

## Data
Tables read, tables changed (columns, migrations), new tables; datasets touching them.

## Flows
Flows affected (which step changes) and whether a new cross-context flow is needed (then it is a gap: `flows/_template.md`).

## Calculations
Existing used as is / changed (which rule of the concept) / new (a draft concept under `domain/calculations/` from
`_template.md`, status draft, inputs and outputs named, formula open if unknown).

## Gaps and questions
What the bundle does not say and the analyst must decide or find out; what is forwarded to `spec-writer`
(draft spec / new rules), `architect` (new service), `calc-auditor` (changed formula). Never filled from memory.

## Stories outline
The epic and the stories of `<slug>.yml` in one line each with the rules they cite and `depends_on` across contexts;
the YAML is the source, this list is the summary the analyst reads first.

## Sources
- pack: `python3 scripts/context-pack.py --task <subject> --task <subject> ...` (built <ISO>)
- catalogue: `generated/catalogue.md` (generated <date>)
- documents opened after the pack (task-context steps 4 and 5): the calculations, flows, legacy pages and other files the pack pointed at or a search found, each with the fact it gave
- code ranges read through the maps (task-context step 6): each `file:line`, how it was located (pack, `graph-query.py --find`, `components.md`, `codebase-map.md`, `docs-tags.md`), the commit from `generated/manifest.yml`, and the question it answered
- free code search (task-context step 7, only for a question that still blocked): the files read, the question each answered, the commit from `generated/manifest.yml`
