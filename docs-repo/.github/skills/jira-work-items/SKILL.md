---
name: jira-work-items
description: Slice a feature spec into a Jira epic, stories and subtasks as YAML from its context pack; estimation, dependency and acceptance-criteria conventions; subtasks derived from the graph neighbourhood. Use when producing files under work-items/.
---

# Jira work items from a spec

0. Implemented already (the pack's graph lists the spec's endpoints, hooks, components)? Then slice only the change
   request you were given; without one, answer "implemented - nothing to build".
1. Work from the context pack (`task-context` skill). Epic = the feature: `summary` = spec title,
   `description` = spec Summary + link.
2. Stories = **vertical slices** by actor goal or by business-rule cluster (3-6 BRs per story). See
   `references/slicing-heuristics.md`.
3. Each story: acceptance criteria in Gherkin, each citing a `BR-*` present in the pack; `estimate` in SP
   (1,2,3,5,8); > 8 -> split.
4. Subtasks from the **graph neighbourhood** section of the pack, one per node kind
   (`.github/skills/code-graph/references/subtask-mapping.md`): `[BE]` endpoint / manager / calculator,
   `[DB]` table (migration), `[INT]` topic (producer / consumer idempotency) or external contract, `[FE]` hook /
   component / route, `[TEST]`, `[DOC]`. Each <= 1 day; name the class / operationId / table / route.
5. `depends_on` between stories only when a contract (endpoint / topic / table) must exist first, or when the graph
   shows a cross-community edge.
6. Unknowns -> `questions[]`, never assumptions. Spec badge `draft` / `unverified` / `STALE` -> label
   `needs-spec-review` on the epic.
7. Validate: `./scripts/validate-work-items.ps1 work-items/<ID>.yml`.
