---
name: code-graph
description: Answer "what is affected / where is it / what talks to what" from the generated architectural graph (generated/graph) instead of reading source. Use for impact analysis, Jira subtask scoping, test-case scoping and doc skeletons.
---

# Code graph (REPO_MAP + graph/<community>.md + graph.json)

The graph is built by `scripts/gen-graph.ps1` from the BE/FE generated maps and `@docs` tags. Nodes are
*architectural* (module, feature, endpoint, route, class, hook, component, topic, table, spec); there are a few
hundred, not thousands, so one neighbourhood file fits in ~1-2k tokens.

## Read order (stop as soon as you can answer)
1. `generated/graph/REPO_MAP.md` - communities, top nodes, cross-repo flows, spec coverage (~4k tokens).
2. `generated/graph/<community>.md` - one module/feature neighbourhood: nodes with `file:line`, edges, specs.
3. A query: VS Code `#impact <node|file>` (extension) or
   `scripts/graph-query.ps1 -Node <id> -Depth 2` / `-Files <paths>` / `-Find <text>` (IntelliJ, CI).
4. Only then a source range (`file:line` from the node) - never a whole module.

## Node id grammar
`module:<name>` `feature:<name>` `endpoint:<METHOD> <path>` `route:<path>` `class:<Simple>` `hook:<name>`
`component:<Name>` `topic:<name>` `table:<name>` `spec:<ID>` (spec = `CTX-NNN`, calculation = `snake_case`).
Edges: `contains exposes handled-by depends-on calls renders uses produces consumed-by persists-to owns fk-* implemented-by`.
Edge marks: `(exact)` = from Spring-context / TS-compiler export; `(heuristic)` = name match - verify before relying on it.

## Recipes
| Question | Do |
|---|---|
| Blast radius of a change | `#impact <node>` depth 2 -> list by kind; specs in radius = docs to update |
| Which specs does this PR touch | `graph-query.ps1 -Files (git diff --name-only)` -> `specs in blast radius` |
| Jira subtasks for a story | neighbourhood of `spec:<ID>` -> one `[BE]` per class, `[FE]` per feature/hook, `[DB]` per table, `[INT]` per topic; see `references/subtask-mapping.md` |
| Test scope for a spec | depth-2 from `spec:<ID>`: endpoints -> `@api`, routes -> `@ui`, calculators -> `@calc`, topics -> `@kafka`, tables -> fixtures |
| Doc skeleton for a module | `<community>.md` sections become the spec's Interfaces / Events / Data headings; prose is the only thing left to write |
| Untagged code / unspecified features | `REPO_MAP.md` **Spec coverage**: `code only` -> write spec; `spec only` -> add `@docs` tag |

## Rules
- Quote node ids and `file:line` from the graph; do not invent edges.
- If a node is missing, say "not in graph (maps stale or not architectural)" and point to `gen-all.ps1` / `gen-graph.ps1`.
- `url:` nodes mean an FE call that matched no BE endpoint - external service or stale map; flag it.
- Graph edges are structural, not behavioural: formulas live in `domain/calculations/`, not here.
