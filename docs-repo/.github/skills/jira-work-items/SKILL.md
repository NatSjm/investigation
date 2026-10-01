---
name: jira-work-items
description: Slice a feature spec into a Jira epic, stories and subtasks as YAML; estimation, dependency and acceptance-criteria conventions. Use when producing files under work-items/.
---

# Jira work items from a spec

1. Epic = the feature. `summary` = spec title; `description` = spec Summary + link to spec.
2. Stories = **vertical slices** by actor goal or by business-rule cluster (3–6 BRs per story). Check
   `references/slicing-heuristics.md` when unsure.
3. Each story: acceptance criteria in Gherkin, each citing `BR-*`; `estimate` in SP (1,2,3,5,8); >8 → split.
4. Subtasks by layer using `generated/codebase-map.md` to name the module: `[BE] ...`, `[FE] ...`, `[DB] ...`,
   `[INT] ...`, `[TEST] ...`. Each ≤ 1 day.
5. `depends_on` between stories only when a contract (endpoint/topic/table) must exist first.
6. Unknowns → `questions[]`, never assumptions.
7. Validate: `scripts/validate-work-items.ps1 work-items/<ID>.yml`.
