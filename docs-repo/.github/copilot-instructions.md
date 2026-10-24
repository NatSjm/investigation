# Copilot instructions - Harbor documentation repository

The rules for working in this repository are in [`AGENTS.md`](../AGENTS.md) (read by Copilot Chat, Copilot CLI,
the coding agent and other tools). This file adds only what is Copilot-specific.

## Start every task with a context pack
`python3 scripts/context-pack.py --task <spec ID | calculation | node | text>` then attach `.context/<task>.md` with `#file`.
Free text (no ID, often several contexts): read `generated/catalogue.md` first, pick the subjects, one pack with a `--task` per subject
(spec ID, calculation, `flows/<name>.md`, `context:<name>` for the context a new piece belongs to).
Do not use `@workspace` over this repository or over `../backend` / `../frontend`; the pack and the graph already
contain the relevant `file:line` references.

## Which agent / prompt for which job

| Job | Agent (`@name`) | Prompt (`/name`) | Reads |
|---|---|---|---|
| Stories, subtasks, estimates, questions for Jira | `analyst` | `/jira-from-spec`, `/coverage-report` | context pack, then the documentation folders freely; up to five code ranges located through the maps when a question stays open, then a free reading pass for one that still blocks |
| A request in free text: a question, or a change spanning contexts with existing and new behaviour -> analysis document, confirmed reading, request epic | `analyst` | `/analyse-request` | `generated/catalogue.md` + one merged context pack |
| New or refreshed feature spec | `spec-writer` | `/spec-skeleton-from-graph`, `/spec-from-code` | graph neighbourhood + one manager file |
| Keep specs in sync with a code change / generated PR | `doc-sync` | - | `map-paths.py` output, generated maps, contracts |
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
JetBrains / CLI: run `scripts/graph-query.py` and paste the output.

## Guard rails (hooks in `.github/hooks/`)
`docs-quality.json` rebuilds indexes and runs `okf-validate.py --strict` and the other validators when an agent stops,
and blocks edits under `generated/**`; so run the checks yourself only once, after the last edit of a task that changed
files (`AGENTS.md`, Checks). If a hook fails, fix the reported file; do not disable the hook. `stale` lines
never fail it.

## Output discipline
Files first, chat second (<= 15 lines). Quote `file:line` and spec IDs, never paste source code or long
tables into chat. When a fact is uncertain, write it into the concept's **Open questions**, not into prose.
