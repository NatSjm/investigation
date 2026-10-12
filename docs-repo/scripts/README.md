# Scripts

All scripts are PowerShell 7 (Windows dev machines and `pwsh` in CI). No MCP, no third-party agent frameworks, no
modules; external systems are reached with plain REST calls and tokens from environment variables.

| Script | Purpose | Env |
|---|---|---|
| `context-pack.ps1` | **task-scoped context** for an agent: spec + badge, calculations, graph neighbourhood, contract operations, tables, related work items / tests, legacy pages -> `.context/<task>.md` (`-Budget N`, `-Print`) | - |
| `graph-query.ps1` | query `generated/graph/graph.json`: `-Node <id|substring> -Depth n`, `-Files <changed paths>` (impacted specs), `-Find <text>`, `-Json`; CLI twin of the VS Code `#impact` tool | - |
| `gen-graph.ps1` | join `generated/be`, `generated/fe` maps + `@docs` tags (+ optional `graph-export-*.json`) into `generated/graph/` (`graph.json`, `<community>.md`, `REPO_MAP.md`); `-Check` for CI | - |
| `coverage-matrix.ps1` | analytics: BR -> story -> scenario coverage, badges, calculations' worked examples / audits -> `generated/analytics/coverage-matrix.md|json` | - |
| `build-index.ps1` | regenerate every `index.md` (reserved OKF file) from concept frontmatter with trust badges; `-Check` for CI | - |
| `okf-validate.ps1` | OKF v0.2 §11 conformance + provenance/trust warnings for the whole bundle (`-Strict`, `-MaxWarnings N`) | - |
| `validate-frontmatter.ps1` | repo-specific keys on `Feature Spec` / `Attested Computation` concepts (ID format, BR numbering, calculation links) | - |
| `validate-work-items.ps1` | `work-items/*.yml` against `_schema.yml` rules (BR citations exist in the spec, estimates, subtasks <= 8 h) | - |
| `migration-status.ps1` | migration plan: per context the lifecycle runs still due (skeleton, legacy merge, calculation audit, owner decision) with their commands, pending legacy pages, unaudited calculations -> `migration/<scope>.md` (`-Scope all|<ctx>`, `-Print`) | - |
| `map-paths.ps1` | changed code paths -> affected specs (uses `docs-map.yml`) | - |
| `check-freshness.ps1` | CI gate in the code repos: mapped code changed but `last_verified` not bumped | - |
| `collect-evidence.ps1 [-Generate] [-Graph] [-DryRun]` | the single evidence collector: stages maps + contracts from `../backend`, `../frontend`, validates the candidate, replaces the collector-owned sets under `generated/` (deletions included), writes `generated/manifest.yml` (source commits, hashes); idempotent when nothing changed; `-Graph` also rebuilds graph + indexes. CI: `ci-examples/collect-evidence.yml` opens one PR per snapshot | - |
| `publish-local.ps1` | deprecated name of `collect-evidence.ps1` (kept as a wrapper) | - |
| `hooks/guard-generated.ps1` | Copilot `preToolUse` hook: denies edits under `generated/**` and of `index.md` files | - |
| `jira-push.ps1` | create/update epic/stories/subtasks via Jira REST v3, write back keys | `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN` |
| `confluence-export.ps1` | Confluence REST -> Markdown into `confluence-import/` | `CONFLUENCE_URL`, `CONFLUENCE_TOKEN` |
| `confluence-publish.ps1` | Markdown -> Confluence page (one-way), keeps page id map in `.confluence-map.json` | same |
| `push-to-tests-repo.ps1` | copy `test-design/**` into the tests repo branch + open PR | `TESTS_REPO_URL`, `GIT_TOKEN` |

`jira-push.ps1`, `confluence-export.ps1`, `confluence-publish.ps1` and `push-to-tests-repo.ps1` are stubs that
describe the intended API calls; everything else is implemented and exercised against the simulated repositories.

Python equivalents of the OKF checker/visualiser (vendored from `scaccogatto/okf-skills`, MIT) live under
`.github/skills/okf-validate/scripts/` and `.github/skills/okf-visualize/scripts/`; CI runs both flavours.

Typical local loop:
```powershell
..\code-repo-kit\be\scripts\docs\gen-all.ps1 -Root ..\backend
..\code-repo-kit\fe\scripts\docs\gen-all.ps1 -Root ..\frontend
.\collect-evidence.ps1 -Graph; .\okf-validate.ps1 -Strict; .\coverage-matrix.ps1
.\context-pack.ps1 -Task P1-001 -Print
```
