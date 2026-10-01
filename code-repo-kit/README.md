# code-repo-kit - token-efficient Copilot setup for the FE and BE repos

Companion to `docs-repo/` (the OKF docs bundle). Everything here is **library-free** (PowerShell 7 / regex,
plain VS Code API) so it can be adopted in the bank without new third-party dependencies. Copy the relevant
folder into each code repository.

```
code-repo-kit/
  be/                     -> advisory-be (Kotlin / Spring / Maven)
    .github/copilot-instructions.md       <= 60 lines: read order, never-open list, conventions, output discipline
    .github/instructions/*.instructions.md  applyTo-scoped: calc/, messaging/, tests
    .github/agents/code-reader.agent.md     read-only navigator (maps + facade, max 3 files)
    .github/agents/impact-analyst.agent.md  blast-radius checklist across BE/FE/docs
    .github/prompts/*.prompt.md             explain-module, find-spec-code
    scripts/docs/gen-*.ps1, gen-all.ps1     generators -> docs/_generated/*.md (+ -Check gate)
    templates/GraphExportTest.kt            precise graph export from the Spring context (test scope; template)
  fe/                     -> advisory-fe (React / TypeScript)
    .github/...                             same pattern for feature folders
    scripts/docs/gen-*.ps1                  codebase-map (features), routes, types-index, docs-tags
    scripts/docs/gen-graph-fe.ts            precise graph export via the TypeScript compiler API (existing devDependency)
  shared/
    check-file-size.ps1                     line-cap gate with baseline (token hygiene)
    copilot-content-exclusion.yml           what Copilot must never see (GitHub repo setting, both IDEs)
    workspaces/hedges.code-workspace        per-context multi-root workspace (BE module + FE feature + docs)
    ide-setup.md                            IntelliJ / VS Code settings
  ci/docs-maps.yml                          freshness + size gate on PR; publish maps to docs repo on main
  vscode-extension/                         MCP-free retrieval tools (#docsLookup, #codeMap, #specToCode, #impact, @docs)
  samples/be-mini, samples/fe-mini          fixtures used to verify the generators
```

## The idea in one paragraph
Copilot spends tokens on *finding* and *reading*. We remove finding by giving every repo a few generated,
always-fresh maps (`docs/_generated/`: modules, endpoints, topics, tables, routes, types, `@docs` tags) and an
instruction file that says "read the map, then the facade, then one range". We shrink reading by capping file
size, excluding noise at the GitHub level, opening per-context workspaces instead of whole repos, and - in VS
Code - replacing `@workspace` with three retrieval tools that return a few hundred tokens with `file:line`.

## Generated maps (what an agent reads instead of source)

| Map | BE source | FE source | Typical size |
|---|---|---|---|
| `codebase-map.md` | `pom.xml` modules + `@RestController/@KafkaListener/@Scheduled` + facade files | `src/features/*` barrels (`@module` JSDoc, exports, fetch URLs) | 1 row / module or feature |
| `api-index.md` | `@*Mapping` scan: method, path, handler, params, `file:line` | - | 1 row / endpoint |
| `events.md` | `@KafkaListener` + `KafkaTemplate.send`, constants resolved | - | 1 row / topic |
| `db-schema.md` | Flyway `V*.sql` (CREATE/ALTER), Mermaid ER | - | 1 section / table |
| `routes.md` | - | react-router objects / `<Route>` | 1 row / route |
| `types-index.md` | - | `export interface/type` from `*.types.ts` verbatim | types only |
| `docs-tags.md` | `@docs <ID>` in KDoc | `@docs <ID>` in JSDoc | 1 row / tag |

All maps carry OKF-style frontmatter (`type: Document`, `generated.by: process:gen-docs`) so they can be
copied into the docs bundle's `generated/<repo>/` by CI unchanged.

## Architectural graph (docs repo joins the maps)
The docs repo's `scripts/gen-graph.ps1` turns these maps (+ `@docs` tags, + optional precise exports
`graph-export-be.json` / `graph-export-fe.json`) into `generated/graph/`: `REPO_MAP.md` (ranked, budgeted),
one `<module-or-feature>.md` neighbourhood each, and `graph.json` for `#impact` / `scripts/graph-query.ps1`.
Communities are Maven modules / FE features; FE and BE with the same name form one bounded context.
See `INVESTIGATION.md` §3.9 and `IMPLEMENTATION-PLAN.md` Step 4.

## Verified locally
```
cd samples/be-mini;  ..\..\be\scripts\docs\gen-all.ps1 -Root .          # 2 modules, 6 endpoints, 3 topics, 2 tables, 5 tags
                     ..\..\be\scripts\docs\gen-all.ps1 -Root . -Check   # up to date; detects an added endpoint
cd samples/fe-mini;  ..\..\fe\scripts\docs\gen-all.ps1 -Root .          # 2 features, 5 routes, 4 types, 2 tags
cd vscode-extension; npm install; npm run compile                       # tsc OK; knowledge.ts tested against docs-repo bundle + graph.json
cd ..\docs-repo;     .\scripts\gen-graph.ps1 -BeMaps ..\code-repo-kit\samples\be-mini\docs\_generated -FeMaps ..\code-repo-kit\samples\fe-mini\docs\_generated
                     .\scripts\graph-query.ps1 -Node spec:HEDGE-001 -Depth 2                       # 36 nodes, 44 edges, 3 communities
cd samples\fe-mini;  node <compiled gen-graph-fe.js> src docs\_generated\graph-export-fe.json       # 11 nodes, 9 edges, exact URLs + methods
```

## Rollout order
1. Content exclusion + `copilot-instructions.md` + `check-file-size.ps1 -WriteBaseline` (day 1, zero risk).
2. Generators + `docs-maps.yml` freshness gate (warn-only for two sprints, then blocking).
3. `@docs` tagging of facades/calculations during normal work; `docs-tags.md` fills up.
4. Per-context workspaces + VS Code extension for FE/QA/analyst roles.
5. Measure: Copilot usage metrics API (premium requests / user / week), count of `@workspace` vs `#file` references in prompts (survey), PR review time.
