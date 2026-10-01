# graph.json schema (produced by scripts/gen-graph.ps1)

```json
{
  "generated": { "by": "process:gen-graph", "at": "YYYY-MM-DD" },
  "communities": [ { "id": "hedges", "repo": "be+fe", "nodes": 17 } ],
  "nodes": [ { "id": "endpoint:GET /api/v1/hedges/{clientId}/proposals", "kind": "endpoint", "label": "...",
               "community": "hedges", "repo": "be", "location": "hedges/src/.../HedgeController.kt:13",
               "note": "handler HedgeController.listProposals; params clientId: String",
               "component": 1, "rank": 28.61, "degree": 3 } ],
  "edges": [ { "from": "feature:hedges", "to": "endpoint:GET /api/v1/hedges/{clientId}/proposals",
               "rel": "calls", "source": "regex-map | export | name-heuristic" } ]
}
```

- `community` = BE Maven module or FE feature folder; FE feature and BE module with the same name share one
  community on purpose (one bounded context across repos). `docs` = spec nodes, `external` = topics with no
  producer/consumer in our repos.
- `component` = connected component id (flows that never touch each other).
- `rank` = PageRank x 1000 on the undirected graph; drives `REPO_MAP.md` ordering under the line budget.
- `source`: `export` edges come from `graph-export-be.json` (Spring context test) / `graph-export-fe.json`
  (TypeScript compiler API) and override regex edges with the same from/rel/to.

Inputs the joiner expects in the docs repo:
`generated/be/{codebase-map,api-index,events,db-schema,docs-tags}.md`, `generated/fe/{codebase-map,routes,docs-tags}.md`,
optional `generated/be/graph-export-be.json`, `generated/fe/graph-export-fe.json`, and `features/**`, `domain/calculations/**`
for spec status/path.
