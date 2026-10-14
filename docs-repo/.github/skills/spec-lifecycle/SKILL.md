---
name: spec-lifecycle
description: The run-by-run lifecycle of one feature spec in this repo (Run 1 skeleton from the graph, Run 2 legacy page merge, Run 3 calculation audit, Run 4 owner decision, ongoing doc-sync) - which agent owns which run, what each run may read and write, how to tell which run you are in, and how the migration-lead plans them. Use when planning or executing documentation migration work, or when unsure whether a spec is ready for the analyst.
---

# Spec lifecycle

One spec is written **part by part**: one Copilot agent run per part, a human review of the diff after each run,
one commit per run. Runs are chained by agent handoffs (buttons), never by an agent calling another agent. The
code is the truth: the skeleton comes from the code maps first; Confluence pages are merged into it afterwards.

| Run | Owner | May read | Writes | Exit state |
|---|---|---|---|---|
| 1 Skeleton | `spec-writer` via `/spec-skeleton-from-graph <ctx> <ID>` | context pack: `generated/graph/<ctx>.md`, contracts, `generated/be/components.md`; one source file: `manager/<Ctx>Manager.kt` | `features/<ctx>/<ID>.md`, `docs-map.yml`, `log.md` | `status: draft`, open questions listed |
| 2 Legacy merge | `confluence-migrator <page>` (one page per run) | the page, the pack | merged facts, `⚠️ CONFLICT` / `❓ UNVERIFIED` callouts, `sources[]`, glossary terms, page -> `_done/` | `draft`; every legacy claim cited |
| 3 Calculation | `calc-auditor` via handoff or `/audit-calculation <name>` | calculator class + its unit test only | `domain/calculations/<name>.md` (`## Audit <date>` table, open questions) | calculation `stable` only when all rows `MATCH` |
| 4 Owner decision | human | open questions | Change log rows, `verified: { by: human:<id>, at }`, `stale_after` | `status: stable`, badge *human-reviewed* |
| ongoing | `doc-sync` per generated-diff PR | generated diff, pack | Change log row, `last_verified` | stays `stable`, or back to `draft` if a BR changed |

## Which run am I in?
- No `features/<ctx>/<ID>.md` exists -> Run 1. Never start from a legacy page.
- Spec exists and a page under `confluence-import/` is not in `_done/` -> Run 2 for that page.
- A `@docs <calculation>` tag in `generated/be/docs-tags.md` has no concept, or the concept has no `## Audit` -> Run 3.
- Spec is `draft` with open questions and no `verified` -> Run 4 (a person, not an agent).
- `scripts/migration-status.py --scope <ctx> --print` answers this deterministically.

## Rules shared by every run
- Build the context pack first (`scripts/context-pack.py --task <ID|name|page>`); read the pack, not the repo.
- Never copy numbers from a legacy page; link the calculation and let Run 3 verify.
- Never write `verified.by: human:*`; never edit `generated/**`.
- Finish with `okf-validate.py --strict`, `build-index.py`, a `log.md` line. The `agentStop` hook repeats the checks.

## Planning (migration-lead)
`scripts/migration-status.py --scope all` writes `migration/all.md`: per context the runs still due with the exact
command, pending legacy pages, calculations without concept or audit, specs waiting for an owner. Order of work:
all Run 1 first (may be batched through the Copilot coding agent, one issue per context), then Run 2 page by page
interactively, Run 3 as the handoff after each spec, Run 4 by the owner. See `references/run-checklist.md`.

## Ready for the analyst
No "code only" entry for the context in `generated/graph/REPO_MAP.md`; spec `stable` + `verified`; every linked
calculation audited; no pending page; the context pack for the ID fits its budget.
