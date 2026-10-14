---
name: migration-plan
description: Plan the documentation migration for a context, a Confluence space or the whole repo - which lifecycle runs are due, in which order, with the command for each.
argument-hint: "context | space key | all"
agent: migration-lead
---
Scope: ${input:scope:all}

Run `python3 scripts/migration-status.py --scope <scope>`, read `migration/<scope>.md` and `generated/graph/REPO_MAP.md`,
append `## Lead notes <date>` (processing order, targets for unassigned pages, batch vs interactive runs, blockers),
rebuild indexes, log. Report runs due by type, contexts ready for the analyst and the first three commands (<= 10 lines).
