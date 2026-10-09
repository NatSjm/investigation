# Copilot instructions - Harbor documentation repository

The rules for working in this repository are in [`AGENTS.md`](../AGENTS.md) (read by Copilot Chat, Copilot CLI,
the coding agent and other tools). This file adds only what is Copilot-specific.

## Start every task with a context pack
`./scripts/context-pack.ps1 -Task <spec ID | calculation | node | text>` then attach `.context/<task>.md` with `#file`.
Do not use `@workspace` over this repository or over `../backend` / `../frontend`; the pack and the graph already
contain the relevant `file:line` references.

## Which agent / prompt for which job

| Job | Agent (`@name`) | Prompt (`/name`) | Reads |
|---|---|---|---|
| Stories, subtasks, estimates, questions for Jira | `analyst` | `/jira-from-spec`, `/coverage-report` | context pack only |
| New or refreshed feature spec | `spec-writer` | `/spec-skeleton-from-graph`, `/spec-from-code` | graph neighbourhood + one manager file |
| Keep specs in sync with a code change / generated PR | `doc-sync` | - | `map-paths.ps1` output, generated maps, contracts |
| Check a formula doc or legacy page against the code | `calc-auditor` | `/audit-calculation` | calculation doc, `docs-tags.md`, one class + its test |
| Gherkin + fixtures for the tests repo | `test-designer` | `/tests-from-spec` | spec BRs + worked examples |
| HLD / ADR / integration map | `architect` | `/hld-from-spec` | architecture/, contracts |
| Blast radius of a change | `impact-analyst` | `/impact-from-graph` | `generated/graph/` only |
| Legacy Confluence page -> concept | `confluence-migrator` | - | the page + generated maps |
| OKF conformance | - | `/okf-validate`, `/okf-produce` | validators |

Agents hand off in the natural order: `spec-writer` -> `analyst` -> `test-designer`; `calc-auditor` findings go
back to `spec-writer` / `doc-sync`.

## Tools available in VS Code (in-house extension, no MCP)
`#docsLookup <ID|keywords>` (concept + trust badge), `#codeMap <query>` (rows from the code maps),
`#specToCode <ID>` (`@docs` locations), `#impact <node|file>` (graph neighbourhood), chat participant `@docs`.
JetBrains / CLI: run `scripts/graph-query.ps1` and paste the output.

## Guard rails (hooks in `.github/hooks/`)
`docs-quality.json` rebuilds indexes and runs `okf-validate.ps1 -Strict` when an agent stops, and blocks edits
under `generated/**`. If a hook fails, fix the reported file; do not disable the hook.

## Output discipline
Files first, chat second (<= 15 lines). Quote `file:line` and spec IDs, never paste source code or long
tables into chat. When a fact is uncertain, write it into the concept's **Open questions**, not into prose.
