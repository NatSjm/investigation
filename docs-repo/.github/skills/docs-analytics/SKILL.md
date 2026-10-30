---
name: docs-analytics
description: Answer analytics questions about the documentation and delivery state from the bundle itself - BR coverage by stories and test scenarios, trust and staleness of specs, code without specs, open questions - using scripts/coverage-matrix.py, the index badges and REPO_MAP spec coverage. Use for status reports, backlog grooming and release readiness questions.
---

# Documentation analytics

Everything an analyst needs for a status answer is machine-readable: frontmatter (`status`, `verified`,
`stale_after`, `last_verified`), `BR-*` identifiers in specs, `rule:` citations in work items, `@BR-*` tags in
Gherkin, and the graph's spec coverage.

## Sources (all generated, no source code)
| Question | Source | Command |
|---|---|---|
| Which rules have stories / scenarios? | `generated/analytics/coverage-matrix.md` | `python3 scripts/coverage-matrix.py` |
| Which specs are trustworthy? | badges in `features/index.md`, `features/<ctx>/index.md` (`human-reviewed`, `machine-confirmed`, `unverified`, `STALE`, `draft`) | `python3 scripts/build-index.py` |
| Which code has no spec / which spec has no code? | `generated/graph/REPO_MAP.md` -> **Spec coverage** (`spec + code`, `code only`, `spec only`) | `python3 scripts/gen-graph.py` |
| What is open? | `## Open questions` sections; `questions[]` in `work-items/*.yml` | `search` for `- [ ]` under features/ |
| Where did the documentation run out? | `generated/analytics/coverage-matrix.md`, column **answered from code**: open questions the analyst settled from source (`code-read` items) | `python3 scripts/coverage-matrix.py` |
| What changed recently? | root `log.md` (lifecycle events); `features/<ctx>/log.md`, `domain/calculations/log.md`, `flows/log.md`, `architecture/log.md` (one line per change, newest first) | - |
| Which specs does a code change hit? | `scripts/map-paths.py`, `graph-query.py --files` | - |

## Report shape (<= 25 lines)
1. Scope and date; number of specs by status/badge.
2. Table: spec | BRs | with story | with scenario | answered from code | badge | stale_after.
3. Gaps: `code only` communities (write spec), `spec only` (tag code), rules without scenarios, drafts older than 30 days,
   specs with the most questions answered from code (the analyst had to read source: refresh them first).
4. Top 3 actions with the prompt to run (`/spec-skeleton-from-graph`, `/tests-from-spec`, `/audit-calculation`).

## Rules
- Counts come from the scripts, not from reading files by hand; if a script fails, say so.
- Do not treat a `machine-confirmed` badge as verified; only `human-reviewed` is.
- Never open `../backend` / `../frontend` for analytics questions.
