# Investigation: agent-ready documentation for a large two-repo application

This repository is a **working prototype** of a way of working, not a product. It answers two questions:

1. How to keep a **separate documentation repository** that is prepared for an AI agent (GitHub Copilot) so that an
   analyst agent produces Jira work items, test designs, HLDs and status analytics from the documentation alone,
   going to the code only when something must be verified.
2. How to make **large frontend and backend repositories cheap for agents** (generated code maps, an architectural
   graph, contract-first API index, short instructions, content exclusion) without third-party agent frameworks or MCP.

The business case is simulated and deliberately generic (**Harbor**: client meetings, two product groups moving
between country pairs, cover, market scenarios, stress tests, reports). See [BLUEPRINT.md](BLUEPRINT.md) for the
naming contract every file follows.

## Layout - three "repositories" in one workspace

| Folder | Plays the role of | What is inside |
|---|---|---|
| [`backend/`](backend/) | `harbor-backend` (Kotlin / Spring Boot / Maven / PostgreSQL / Kafka) | layered `core` (package-by-layer `harbor/<layer>/`: api, manager, service, dao, event, job, utils, ...; business context = class-name prefix per `docs-repo/contexts.yml`) + `kafka_client` (topics, payloads) + `init_docker_compose/` (local env); OpenAPI-first contract (`core/src/main/resources/openapi/harbor-api.yaml`), AsyncAPI (`openapi/harbor-events.yaml`), Flyway migrations, calculations in `utils/` with unit tests, external-service contracts in `core/src/main/resources/api/`; the applied kit (`AGENTS.md`, `.github/`, `scripts/docs/`, `docs/_generated/`) |
| [`frontend/`](frontend/) | `harbor-frontend` (React / TypeScript) | feature folders mirroring the bounded contexts, generated `openapi-fetch` client with the session header, routes; the applied kit |
| [`docs-repo/`](docs-repo/) | `harbor-docs` (OKF v0.2 bundle) | specs, calculations, glossary, architecture, generated maps + graph + contracts, work items, test design, legacy pages; **Copilot customisation** (`AGENTS.md`, agents, prompts, skills, hooks) and PowerShell scripts (context packs, validators, graph, analytics) |
| [`code-repo-kit/`](code-repo-kit/) | reusable kit | what gets copied into each code repo (`apply-kit.ps1`), CI, VS Code retrieval extension (MCP substitute), shared hygiene files |
| [`harbor.code-workspace`](harbor.code-workspace) | the workspace | opens all of the above side by side with the extension settings |

Documents: [INVESTIGATION.md](INVESTIGATION.md) (problem, options, decisions, token strategy),
[IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) (rollout to the real repositories), [BLUEPRINT.md](BLUEPRINT.md) (simulated domain).

## The loop in one picture

```mermaid
flowchart LR
  BE[backend<br/>scripts/docs/gen-all.ps1] -- CI publishes maps + contracts --> GEN[docs-repo/generated/be, fe, openapi, asyncapi]
  FE[frontend<br/>scripts/docs/gen-all.ps1] -- CI --> GEN
  GEN -- gen-graph.ps1 --> GRAPH[generated/graph]
  GRAPH & SPEC[features · domain · architecture] -- context-pack.ps1 --> PACK[.context/task.md]
  PACK --> ANALYST[@analyst] --> WI[work-items -> Jira]
  PACK --> TD[@test-designer] --> TESTS[test-design -> tests repo]
  PACK --> SW[@spec-writer / @calc-auditor / @doc-sync] --> SPEC
  LEGACY[confluence-import] -. verified, never copied .-> SW
```

## Try it (PowerShell 7, nothing else to install)

```powershell
# 1. regenerate the code maps in both "repos" (regex scanners, no build)
.\code-repo-kit\be\scripts\docs\gen-all.ps1 -Root .\backend
.\code-repo-kit\fe\scripts\docs\gen-all.ps1 -Root .\frontend

# 2. publish them into the docs repo the way CI would, then build the graph and indexes
.\docs-repo\scripts\collect-evidence.ps1       # single collector: maps + contracts -> docs-repo/generated, with manifest.yml (source commits, hashes)
.\docs-repo\scripts\gen-graph.ps1
.\docs-repo\scripts\build-index.ps1
.\docs-repo\scripts\okf-validate.ps1 -Strict

# 3. what an agent reads for a task
.\docs-repo\scripts\context-pack.ps1 -Task P1-001 -Print
.\docs-repo\scripts\graph-query.ps1 -Node spec:STR-001 -Depth 2
.\docs-repo\scripts\coverage-matrix.ps1
```

Then open `harbor.code-workspace` in VS Code with Copilot and, in the `harbor-docs` folder, try
`/context-pack P1-001`, `@analyst /jira-from-spec STR-001`, `/spec-skeleton-from-graph product2 P2-001`,
`/audit-calculation stress_test_monthly` (the legacy page is deliberately outdated), `/coverage-report`.

## Deliberate gaps (the backlog the agents work on)

Specs `P2-001`, `COV-001`, `IMP-001`, `ADM-001` and the calculation `peer_benchmark_simulation` do not exist yet
(they show as `code only` in `docs-repo/generated/graph/REPO_MAP.md`); `MKT-001` and `RPT-001` are skeletons;
`STR-001` is a draft whose legacy page contradicts the code. Those are the exercises.
