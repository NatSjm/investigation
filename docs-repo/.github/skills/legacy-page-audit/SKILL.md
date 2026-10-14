---
name: legacy-page-audit
description: Compare a legacy (Confluence) page or an existing calculation concept with the current implementation using the generated maps and at most two source files (calculator + unit test); classify each claim as MATCH, DOC-STALE, CODE-SUSPECT or UNDOCUMENTED and record the result in the concept. Use when documentation may be outdated and must be validated against the real state of the project.
---

# Legacy page / calculation audit

Legacy pages describe how things *were meant* to work; the unit test next to the calculator describes how they
*do* work today. Auditing means putting the two side by side without rewriting either from memory.

## Procedure
1. **Pack**: `python3 scripts/context-pack.py --task <calculation | spec ID | page path>`.
2. **Claims list**: extract from the page / concept every checkable claim: formula terms, thresholds, defaults,
   rounding, units, sign conventions, flow steps, field names. One row each.
3. **Locate code** through `generated/be/docs-tags.md` (`@docs <name>` -> `file:line`) or the graph node
   `class:<Calculator>`. Open exactly two files: the class and `<Class>Test.kt`. For flow steps use
   `generated/fe/routes.md` and `generated/be/api-index.md` instead of UI code.
4. **Compare** each claim; parameters with defaults live in `V9__parameters.sql` seeds (`generated/be/db-schema.md`
   names the table; the seed values are in the pack's Data section when present).
5. **Record** under `## Audit <date>` in the concept:

   | # | Item | Documentation says | Code/test says | Severity | Action |
   |---|---|---|---|---|---|

   Severities: `MATCH` · `DOC-STALE` · `CODE-SUSPECT` · `UNDOCUMENTED`.
6. **Status**: any non-`MATCH` -> concept `status: draft`, open question naming who decides; legacy page header
   `status: obsolete | migrated`. Worked examples may only be replaced by values copied from the test (cite the
   test method).
7. Validate, rebuild indexes, `log.md`.

## Rules
- Never "fix" the code or decide which side is right; that is an owner's decision recorded as an open question.
- Never paste the calculator source into the concept; the `# Computation` block holds only the sanctioned shape.
- If the test does not cover a claim, severity is `UNDOCUMENTED` with action "add test case" - not `MATCH`.
