# graph.json schema (produced by scripts/gen-graph.py)

```json
{
  "generated": { "by": "process:gen-graph", "at": "YYYY-MM-DD" },
  "communities": [ { "id": "product1", "repo": "be+fe", "nodes": 24 } ],
  "nodes": [ { "id": "endpoint:GET /api/v1/session/product1/overview", "kind": "endpoint", "label": "...",
               "community": "product1", "repo": "be", "location": "harbor-core/src/main/kotlin/com/acme/harbor/api/Product1Controller.kt:21",
               "note": "handler Product1Controller.getProduct1Overview; params city?, X-Harbor-Session",
               "component": 1, "rank": 28.61, "degree": 3 } ],
  "edges": [ { "from": "feature:product1", "to": "endpoint:GET /api/v1/session/product1/overview",
               "rel": "calls", "source": "regex-map | export | name-heuristic" } ]
}
```

- Node kinds: `context` (BE side of a bounded context, located at its `manager/<Ctx>Manager.kt`), `feature`,
  `endpoint`, `route`, `class` (one per architectural class; `note` = layer + stereotype), `hook`, `component`,
  `topic`, `channel` (browser `BroadcastChannel`, the FE counterpart of a topic: `defines` / `produces` / `consumed-by` edges to features), `table`, `spec`. Shared library components (`generated/fe/components.md`) are `component` nodes in community `shared-ui` with `renders` edges from the features that use them. `depends-on` edges (class -> class) come from constructor injection, `persists-to`
  edges (class -> table) from `components.md` / `db-schema.md` "Used in:".
- `community` = bounded context from `contexts.yml` (BE class-name prefixes + FE feature): one community spans both
  repos on purpose (`clients`, `meetings`, `product1`, `product2`, `cover`, `market`, `stress`, `reports`, `admin`;
  `imports` is BE-only). BE classes matching no prefix are `shared`. `docs` = spec nodes, `external` = topics with
  no producer/consumer in our repos.
- `component` = connected component id (flows that never touch each other).
- `rank` = PageRank x 1000 on the undirected graph; drives `REPO_MAP.md` ordering under the line budget.
- `source`: `export` edges come from `graph-export-be.json` (Spring context test) / `graph-export-fe.json`
  (TypeScript compiler API) and override regex edges with the same from/rel/to.

Inputs the joiner expects in the docs repo:
`contexts.yml`, `generated/be/{codebase-map,components,api-index,events,db-schema,jobs,docs-tags}.md`,
`generated/fe/{codebase-map,routes,docs-tags}.md`, optional `generated/be/graph-export-be.json`,
`generated/fe/graph-export-fe.json`, and `features/**`, `domain/calculations/**` for spec status/path.
