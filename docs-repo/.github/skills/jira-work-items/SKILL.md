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
7. Validate: `python3 scripts/validate-work-items.py work-items/<ID>.yml`.

## Request epics (a request that spans several specs)

A request from an analyst in free text usually touches several contexts, follows a flow, or mixes existing and new
behaviour ("quarterly view on both products carried into the stress test", "dashboard from two existing calculations
and a new score"). Then:

1. Subjects come from `generated/catalogue.md`, the pack is one pack with a `--task` per subject (`task-context`
   skill), and the **analysis document** `work-items/<slug>.md` (template `work-items/_analysis-template.md`) is
   written first: the Reading the analyst confirms, the parts with their state (unchanged / changed / new), the
   evidence, contracts, data, flows, calculations, gaps, and the stories outline.
2. The epic is `work-items/<slug>.yml` with `request: <slug>`, `analysis:`, `specs: [...]` (every spec a story cites),
   optional `flows:` and `contexts:`; the same story shape, a story may cite rules of several specs.
3. **Nothing new without a rule.** A new behaviour in an existing spec gets its rule drafted there first
   (`spec-writer`, `status: draft`, label `needs-spec-review` on the stories); a new behaviour in a context without a
   spec gets its first draft spec (`<PREFIX>-001`) first; a new operation gets `contracts/proposed/<ID>.openapi.yaml`
   (label `needs-contract`); a new calculation gets a draft concept under `domain/calculations/` (inputs and outputs
   named, formula open if unknown). Only then the stories.
4. Order across contexts: the story that creates the contract, table, topic or calculation comes first; the stories
   of the other contexts `depends_on` it. One epic, not one per context.
5. `python3 scripts/validate-work-items.py work-items/<slug>.yml`; `coverage-matrix.py` counts the stories for every
   spec they cite.
