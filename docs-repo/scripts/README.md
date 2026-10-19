# Scripts

All scripts are Python 3.11+ using only the standard library (`python3` on macOS/Linux and CI, `python` on Windows). No MCP,
no third-party agent frameworks, no pip packages; external systems are reached with plain REST calls and tokens from
environment variables. Flags are long options (`--check`, `--task P1-001`); `python3 scripts/<name>.py --help` lists them.

| Script | Purpose | Env |
|---|---|---|
| `context-pack.py` | **task-scoped context** for an agent: spec + badge, calculations, graph neighbourhood, contract operations, tables, related work items / tests, legacy pages -> `.context/<task>.md` (`--budget N`, `--print`) | - |
| `graph-viewer.py` | `--all`, `--community <id>`, `--out <file>`: writes a self-contained HTML page of `generated/graph/graph.json` (default `.context/graph-viewer.html`, git-ignored) to open in any browser: the first dropdown entry `(all communities)` draws the whole graph coloured by community (legend, clusters on a circle, filter dims non-matching nodes; `--all` opens on it), the others one community at a time with the filter hiding non-matching nodes and optional direct neighbours from other communities; click a node for location, note and edges | - |
| `graph-query.py` | query `generated/graph/graph.json`: `--node <id|substring> --depth n`, `--files <changed paths>` (impacted specs), `--find <text>`, `--json`; CLI twin of the VS Code `#impact` tool | - |
| `gen-graph.py` | join `generated/be`, `generated/fe` maps + `@docs` tags (+ optional `graph-export-*.json`) into `generated/graph/` (`graph.json`, `<community>.md`, `REPO_MAP.md`); `--check` for CI | - |
| `coverage-matrix.py` | analytics: BR -> story -> scenario coverage, badges, calculations' worked examples / audits -> `generated/analytics/coverage-matrix.md|json` | - |
| `build-index.py` | regenerate every `index.md` (reserved OKF file) from concept frontmatter with trust badges; `--check` for CI | - |
| `okf-validate.py` | OKF v0.2 §11 conformance + provenance/trust warnings for the whole bundle (`--strict`, `--max-warnings N`) | - |
| `validate-frontmatter.py` | repo-specific keys on `Feature Spec` / `Attested Computation` concepts (ID format, BR numbering, calculation and flow links both ways, `parameter_set` keys in `## Parameters` tables vs `generated/be/parameters.md` in both directions) | - |
| `validate-work-items.py` | `work-items/*.yml` against `_schema.yml` rules (BR citations exist in the spec, estimates, subtasks <= 8 h) | - |
| `migration-status.py` | migration plan: per context the lifecycle runs still due (skeleton, legacy merge, calculation audit, owner decision) with their commands, pending legacy pages, unaudited calculations -> `migration/<scope>.md` (`--scope all|<ctx>`, `--print`) | - |
| `map-paths.py` | changed code paths -> affected specs (uses `docs-map.yml`) | - |
| `check-freshness.py` | CI gate in the code repos: mapped code changed but `last_verified` not bumped | - |
| `collect-evidence.py [--generate] [--graph] [--dry-run]` | the single evidence collector: stages maps + contracts from `../backend`, `../frontend`, validates the candidate, replaces the collector-owned sets under `generated/` (deletions included), writes `generated/manifest.yml` (source commits, hashes); idempotent when nothing changed; `--graph` also rebuilds graph + indexes. CI: `ci-examples/collect-evidence.yml` opens one PR per snapshot | - |
| `publish-local.py` | deprecated name of `collect-evidence.py` (kept as a wrapper) | - |
| `hooks/guard-generated.py` | Copilot `preToolUse` hook: denies edits under `generated/**` and of `index.md` files | - |
| `jira-push.py` | create/update epic/stories/subtasks via Jira REST v3, write back keys | `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN` |
| `confluence-export.py` | Confluence REST -> Markdown into `confluence-import/` | `CONFLUENCE_URL`, `CONFLUENCE_TOKEN` |
| `confluence-publish.py` | Markdown -> Confluence page (one-way), keeps page id map in `.confluence-map.json` | same |
| `push-to-tests-repo.py` | copy `test-design/**` into the tests repo branch + open PR | `TESTS_REPO_URL`, `GIT_TOKEN` |

`jira-push.py`, `confluence-export.py`, `confluence-publish.py` and `push-to-tests-repo.py` are stubs that
describe the intended API calls; everything else is implemented and exercised against the simulated repositories.

Python equivalents of the OKF checker/visualiser (vendored from `scaccogatto/okf-skills`, MIT) live under
`.github/skills/okf-validate/scripts/` and `.github/skills/okf-visualize/scripts/`; CI runs both flavours.

Typical local loop (from the docs repository root):
```bash
python3 ../code-repo-kit/be/scripts/docs/gen-all.py --root ../backend
python3 ../code-repo-kit/fe/scripts/docs/gen-all.py --root ../frontend
python3 scripts/collect-evidence.py --graph; python3 scripts/okf-validate.py --strict; python3 scripts/coverage-matrix.py
python3 scripts/context-pack.py --task P1-001 --print
```
