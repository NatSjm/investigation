# code-repo-kit - token-efficient Copilot setup for harbor-backend and harbor-frontend

Companion to `docs-repo/` (the OKF docs bundle, simulated repo `harbor-docs`). Everything here is **library-free**
(PowerShell 7 / regex, plain VS Code API) so it can be adopted without new third-party dependencies.
`apply-kit.ps1` copies the relevant part into each code repository.

```
code-repo-kit/
  apply-kit.ps1           -Flavour be|fe -Target <repo> [-WhatIf]: copies .github/**, AGENTS.md, scripts/docs/**, check-file-size.ps1, docs-maps.yml
  be/                     -> harbor-backend (Kotlin / Spring Boot / Maven core + kafka_client / PostgreSQL / Kafka; package-by-layer)
    AGENTS.md                               <= 60 lines: repo purpose, read order, contracts, conventions, commands, where rules live
    .github/copilot-instructions.md         Copilot-only supplement (never-open list, output discipline, agents/prompts/tools)
    .github/instructions/*.instructions.md  applyTo-scoped: api (contract-first), calculations (utils/), kafka, migrations, tests, layers
    .github/agents/code-reader.agent.md     read-only navigator (maps + manager + components.md, max 3 files)
    .github/agents/impact-analyst.agent.md  blast-radius checklist across backend / frontend / docs
    .github/agents/docs-tagger.agent.md     adds missing @docs tags from contexts.yml (comment lines only, one PR per context)
    .github/prompts/*.prompt.md             /explain-module (a context), /find-spec-code, /add-endpoint, /tag-docs
    scripts/docs/tag-candidates.ps1         inventory for docs-tagger: manager / calculation -> current tag, proposed tag, status
    .github/hooks/docs-maps.json            agentStop hook: gen-all.ps1 -Check
    .github/workflows/copilot-setup-steps.yml  JDK 21 + mvn -pl core -am generate-sources for the coding agent
    scripts/docs/gen-*.ps1, gen-all.ps1     generators -> docs/_generated/*.md (+ -Check gate)
    templates/GraphExportTest.kt            precise graph export from the Spring context (test scope; template)
  fe/                     -> harbor-frontend (React / TypeScript / openapi-fetch)
    AGENTS.md, .github/...                  same pattern for feature folders (+ api-client instructions, Node 24 setup steps)
    scripts/docs/gen-*.ps1                  codebase-map (features), routes, types-index, docs-tags
    scripts/docs/tag-candidates.ps1         inventory for docs-tagger: barrel / types / hooks -> current tag, proposed tag, status
    scripts/docs/gen-graph-fe.ts            precise graph export via the TypeScript compiler API (existing devDependency)
  shared/
    check-file-size.ps1                     line-cap gate with baseline (token hygiene)
    copilot-content-exclusion.yml           what Copilot must never see (GitHub repo setting, every surface)
    workspaces/product1.code-workspace      per-context multi-root workspace (BE core sources + resources + FE feature + docs)
    ide-setup.md                            IntelliJ / VS Code settings
  ci/docs-maps.yml                          freshness + size gate on PR; publish maps and contracts to harbor-docs on main
  vscode-extension/                         MCP-free retrieval tools (#docsLookup, #codeMap, #specToCode, #impact, @docs)
```

## The idea in one paragraph
Copilot spends tokens on *finding* and *reading*. We remove finding by giving every repo a few generated,
always-fresh maps (`docs/_generated/`: layers, components, operations, topics, tables, jobs, routes, types, `@docs` tags)
and an `AGENTS.md` that says "read the map, then the manager or barrel, then one range". We shrink reading by capping file
size, excluding noise at the GitHub level, opening per-context workspaces instead of whole repos, keeping the REST
contract (`core/src/main/resources/openapi/harbor-api.yaml`) as the single thing to read instead of generated interfaces
and clients, and - in VS Code - replacing `@workspace` with four retrieval tools that return a few hundred tokens with `file:line`.

**Layered backend.** `harbor-backend` is package-by-layer (`core/src/main/kotlin/harbor/<layer>/`: `api`, `manager`,
`service`, `dao`, `event`, `job`, `utils`, `client`, ...; topics and payloads in the `kafka_client` module), so a folder
holds every business area. The business context of a class is its **name prefix** (`Product1*`, `Projection*` ->
`product1`), mapped once in the docs repo `contexts.yml`. `components.md` (one row per class: layer, stereotype, injected
dependencies, tables, `@docs`, `file:line`) replaces "open the module folder": an agent goes map -> the context's
`<Ctx>Manager.kt` -> its dependencies in `components.md` -> one range.

## Generated maps (what an agent reads instead of source)

| Map | BE source | FE source | Typical size |
|---|---|---|---|
| `codebase-map.md` | root `pom.xml` modules -> layers (package segment after `harbor`) -> classes, plus resource folders (`api`, `openapi`, `db/migration`, `pdf`) | `src/features/*` barrels (`@module` JSDoc, exports, `api.GET('<path>')` calls) | 1 line / module and layer, or 1 row / feature |
| `components.md` | every top-level class: layer, Spring stereotype, constructor-injected deps, tables (`@Table`, SQL, `JpaRepository<Entity>`), `@docs`, `file:line` | - | 1 row / class |
| `api-index.md` | **contract-first**: operations from `openapi/harbor-api.yaml` joined to `override fun <operationId>` in controllers (`_not implemented_` when missing); column `Tag` = context; annotation scan as fallback | - | 1 row / operation |
| `events.md` | `@KafkaListener` + `KafkaTemplate.send` in `event/`, `Topics.<CONST>` resolved from `kafka_client` | - | 1 row / topic |
| `db-schema.md` | Flyway `V*.sql` (CREATE/ALTER, inline `REFERENCES`), Mermaid ER; "Used in:" lists classes | - | 1 section / table |
| `jobs.md` | `@Scheduled` methods: trigger (cron / fixedDelay), first KDoc line, `file:line` | - | 1 row / job |
| `routes.md` | - | react-router object routes (`path:` then `element:`) / `<Route>` | 1 row / route |
| `types-index.md` | - | `export interface/type` from `*.types.ts` verbatim | types only |
| `docs-tags.md` | `@docs <ID>` in KDoc (`P1-001`, `monthly_projection`) | `@docs <ID>` in JSDoc | 1 row / tag |

All maps carry OKF-style frontmatter (`type: Document`, `generated.by: process:gen-docs`) so CI can copy them into the
docs bundle's `generated/<be|fe>/` unchanged. CI also publishes the contracts:
`core/src/main/resources/openapi/harbor-api.yaml` -> `generated/openapi/backend.yaml`,
`core/src/main/resources/openapi/harbor-events.yaml` -> `generated/asyncapi/backend.yaml`,
`core/src/main/resources/api/*.yaml` -> `generated/openapi/external/`.

## Architectural graph (docs repo joins the maps)
The docs repo's `scripts/gen-graph.ps1` turns these maps (+ `@docs` tags, + optional precise exports
`graph-export-be.json` / `graph-export-fe.json`) into `generated/graph/`: `REPO_MAP.md` (ranked, budgeted),
one `<context>.md` neighbourhood each, and `graph.json` for `#impact` / `scripts/graph-query.ps1`.
Communities are the bounded contexts of `contexts.yml`: BE classes grouped by name prefix (node `context:<name>`,
located at its manager) plus the FE feature of the same name (`product1`, `stress`, ...); `class:` nodes carry
`depends-on` (constructor injection) and `persists-to` (tables) edges, and spec IDs (`P1-001`) link both sides to the docs.
See `INVESTIGATION.md` section 3.9 and `IMPLEMENTATION-PLAN.md` Step 4.

## Verified locally
Run from `code-repo-kit/` against the sibling simulated repos:
```
.\be\scripts\docs\gen-all.ps1 -Root ..\backend            # codebase-map (core + kafka_client, layers), components, api-index from openapi/harbor-api.yaml, events, db-schema, jobs, docs-tags
.\be\scripts\docs\gen-all.ps1 -Root ..\backend -Check     # exit 1 when a map is stale (what CI and the agentStop hook run)
.\fe\scripts\docs\gen-all.ps1 -Root ..\frontend           # 3 features, 12 routes, 31 types, 18 tags (state of the simulated frontend at the time of writing)
.\fe\scripts\docs\gen-all.ps1 -Root ..\frontend -Check
.\apply-kit.ps1 -Flavour be -Target ..\backend -WhatIf     # lists the files it would copy; drop -WhatIf to apply
cd vscode-extension; npm install; npm run compile          # tsc OK -> out/extension.js, out/knowledge.js
cd ..\..\docs-repo; .\scripts\gen-graph.ps1 -BeMaps ..\backend\docs\_generated -FeMaps ..\frontend\docs\_generated
                    .\scripts\graph-query.ps1 -Node spec:P1-001 -Depth 2
cd ..\frontend;     npx tsc -p scripts/docs/tsconfig.gen.json; node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json
```
The generated outputs belong to the code repos (`backend/docs/_generated`, `frontend/docs/_generated`), not to the kit.

## Rollout order
1. `apply-kit.ps1` per repo, content exclusion, `check-file-size.ps1 -WriteBaseline` (day 1, zero risk).
2. Generators + `docs-maps.yml` freshness gate (warn-only for two sprints, then blocking); `copilot-setup-steps.yml` so the
   coding agent can run `gen-all.ps1 -Check` in its own environment.
3. `@docs` tagging of managers, barrels and calculations during normal work; `docs-tags.md` fills up; contract changes go
   through `openapi/harbor-api.yaml` first (`/add-endpoint`); new class-name prefixes go into `contexts.yml`.
4. Per-context workspaces + VS Code extension for frontend / QA / analyst roles; `graph-query.ps1` for IntelliJ users.
5. Measure: Copilot usage metrics API (premium requests / user / week), share of `@workspace` vs `#file` references in prompts
   (survey), PR review time, number of `_not implemented_` rows in `api-index.md`.

## Copilot customisation files and where each surface reads them

| File | VS Code Copilot Chat | JetBrains Copilot | Copilot CLI | Coding agent (github.com) | Notes |
|---|---|---|---|---|---|
| `AGENTS.md` (repo root) | yes | yes (since 2026-03) | yes | yes | cross-tool; also read by other agent CLIs. Keep <= 60 lines |
| `.github/copilot-instructions.md` | yes | yes | yes | yes | Copilot-only supplement; points at `AGENTS.md` |
| `.github/instructions/*.instructions.md` | yes (`applyTo`) | yes | yes | yes | path-scoped rules; `description` shown in pickers |
| `.github/agents/*.agent.md` | yes (custom agents) | yes | yes | yes (assignable) | `tools: ['read', 'search', 'edit', 'execute']` aliases; `handoffs` is VS Code-only |
| `.github/prompts/*.prompt.md` | yes (`/name`) | yes | yes | - | `agent:` picks the custom agent, `argument-hint` shown in the picker |
| `.github/skills/<name>/SKILL.md` | yes | preview | yes | yes | not used in the code repos; the docs repo ships skills |
| `.github/hooks/*.json` | yes | preview | yes | yes | `docs-maps.json`: `agentStop` -> `gen-all.ps1 -Check` |
| `.github/workflows/copilot-setup-steps.yml` | - | - | - | yes | job name must be `copilot-setup-steps`; preinstalls JDK 21 / Node 24 |
| Content exclusion (repo settings) | yes | yes | yes | yes | from `shared/copilot-content-exclusion.yml` |
| `vscode-extension/` tools + `@docs` | yes | - | - | - | JetBrains users run `harbor-docs/scripts/graph-query.ps1` instead |
