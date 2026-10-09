---
name: task-context
description: Build and consume a task-scoped context pack (scripts/context-pack.ps1) so that an analyst, writer or tester agent reads only what the current task needs - spec, calculations, graph neighbourhood, contracts, tables, related work items and legacy pages - instead of the repository or the code. Use at the start of every feature, calculation, change or ticket task.
---

# Task-scoped context packs

The bundle is bigger than any task. The pack is the **budgeted slice** of it for one task, assembled
deterministically by a script, so every agent starts from the same ~300-500 lines and can tell what it did not get.

## Build
```powershell
./scripts/context-pack.ps1 -Task P1-001                       # spec ID
./scripts/context-pack.ps1 -Task stress_test_monthly          # calculation
./scripts/context-pack.ps1 -Task "topic:harbor.meetings.session-closed"   # graph node
./scripts/context-pack.ps1 -Task "transport mode toggle on the stress table" # free text -> candidates
./scripts/context-pack.ps1 -Task P1-001 -Budget 250 -Print    # smaller, to stdout
```
Output: `.context/<slug>.md` (git-ignored). Attach it with `#file` (VS Code) or paste it (JetBrains / CLI).

## Anatomy (in priority order; lower sections are truncated first when over budget)
1. **Header** - subject, resolution (spec / calculation / node / candidates), trust badge
   (`status`, `human-reviewed | machine-confirmed | unverified`, `STALE`), `last_verified`, `stale_after`.
2. **Spec** - whole body when <= 200 lines, otherwise Summary, Business rules, API / Events, Data, Open questions.
3. **Calculations** linked from the spec - Purpose, Formula, Conventions, Worked examples (never the Kotlin block).
4. **Graph neighbourhood** - `graph-query.ps1 -Node spec:<ID> -Depth 2`: nodes by kind with `file:line`, edges,
   cross-community edges, heuristic marks.
5. **Contracts** - the `paths` blocks of `generated/openapi/backend.yaml` for the spec's `api[]` entries; channel
   names from `asyncapi/backend.yaml` for `events[]`.
6. **Data** - the `db-schema.md` sections for `tables[]`.
7. **Related** - `work-items/<ID>.yml` story summaries, `test-design/features/<ID>.feature` scenario names.
8. **Legacy** - `confluence-import/**` pages mentioning the ID or title keywords (listed, first lines only, marked unverified).
9. **Footer** - sources used, sections truncated, and the rule: *open nothing else unless a question below is
   unanswered; then only the `file:line` named above*.

See `references/pack-anatomy.md` for the exact section markers the agents rely on.

## Consume
- Read the pack once, top to bottom. Quote `BR-*`, node ids and `file:line` from it.
- Treat the trust badge as part of the answer: `draft` / `unverified` / `STALE` -> say it, label outputs `needs-spec-review`.
- `candidates:` in the header means the free text matched several specs - choose or ask; do not merge them.
- A truncated section (`... (truncated: see <path>)`) tells you exactly which file to open if you need more.
- If the pack has no graph section, the graph is missing or stale: run `./scripts/gen-graph.ps1` or say so.

## Why a script and not "just search"
Deterministic, budgeted, reviewable (the pack can be attached to the PR), cheap (one read instead of 10-20 tool
calls), and it carries provenance (which files, which generated-at dates) into the agent's reasoning.
