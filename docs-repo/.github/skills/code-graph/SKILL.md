---
name: code-graph
description: Answer "what is affected / where is it / what talks to what" from the generated architectural graph (generated/graph) instead of reading source. Use for impact analysis, Jira subtask scoping, test-case scoping and spec skeletons.
---

# Code graph (REPO_MAP + graph/<community>.md + graph.json)

The graph is built by `scripts/gen-graph.py` from the BE/FE generated maps, `contexts.yml` and `@docs` tags. Nodes
are *architectural* (context, feature, endpoint, route, class, hook, component, topic, table, spec); there are a few
hundred, not thousands, so one neighbourhood file fits in ~1-2k tokens.

## Read order (stop as soon as you can answer)
1. The **Graph neighbourhood** section of your context pack (already depth 2 around the task).
2. `generated/graph/REPO_MAP.md` - communities, top nodes, cross-repo flows, spec coverage (~4k tokens).
3. `generated/graph/<community>.md` - one bounded-context neighbourhood (BE classes + FE feature): nodes with `file:line`, edges, specs.
4. A query: VS Code `#impact <node|file>` (extension) or
   `scripts/graph-query.py --node <id> --depth 2` / `--files <paths>` / `--find <text>` (JetBrains, CLI, CI).
5. Class-level detail the graph omits (validators, mappers, injected deps, tables): `generated/be/components.md`.
6. Only then a source range (`file:line` from the node) - never a whole file or layer.

## Node id grammar
`context:<name>` `feature:<name>` `endpoint:<METHOD> <path>` `route:<path>` `class:<Simple>` `hook:<name>`
`component:<Name>` `topic:<name>` `table:<name>` `spec:<ID>` (spec = `CTX-NNN`, calculation = `snake_case`).
Examples: `spec:P1-001`, `context:product1`, `feature:stress`, `endpoint:GET /api/v1/session/stress-test`,
`topic:harbor.meetings.session-closed`, `table:projection_summary`, `class:Product1Manager`, `class:StressTestCalculator`.
`context:` = BE side of a bounded context from `contexts.yml`, located at its `manager/<Ctx>Manager.kt`.
Edges: `contains exposes handled-by depends-on calls renders uses produces consumed-by persists-to owns fk-* implemented-by`
(`depends-on` = class -> class: constructor injection, or a static call on a Kotlin object such as `Rounding.money(v)`; `persists-to` = class -> table).
Edge marks: `(exact)` = from Spring-context / TS-compiler export; `(heuristic)` = name match - verify before relying on it.

## Recipes
| Question | Do |
|---|---|
| Blast radius of a change | `#impact <node>` depth 2 -> list by kind; specs in radius = docs to update |
| Which specs does this PR touch | `graph-query.py --files (git diff --name-only)` -> `specs in blast radius` |
| Jira subtasks for a story | neighbourhood of `spec:<ID>` -> one `[BE]` per class along `depends-on`, `[FE]` per feature/hook, `[DB]` per table, `[INT]` per topic; see `references/subtask-mapping.md` |
| Test scope for a spec | depth-2 from `spec:<ID>`: endpoints -> `@api`, routes -> `@ui`, calculators -> `@calc`, topics -> `@kafka`, tables -> fixtures |
| Doc skeleton for a context | `<community>.md` sections become the spec's API / Events / Data headings; prose is the only thing left to write |
| Untagged code / unspecified features | `REPO_MAP.md` **Spec coverage**: `code only` -> write spec; `spec only` -> add `@docs` tag |

## Rules
- Quote node ids and `file:line` from the graph; do not invent edges.
- If a node is missing, say "not in graph (maps stale or not architectural)" and point to `gen-all.py` / `gen-graph.py`.
- `url:` nodes mean an FE call that matched no BE endpoint - external service or stale map; flag it.
- Graph edges are structural, not behavioural: formulas live in `domain/calculations/`, not here.
