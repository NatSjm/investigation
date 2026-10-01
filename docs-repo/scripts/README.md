# Scripts

All scripts are PowerShell (works on Windows dev machines and `pwsh` in CI). No MCP or third-party agent
frameworks; only REST calls with tokens from environment variables.

| Script | Purpose | Env |
|---|---|---|
| `validate-frontmatter.ps1` | check repo-specific keys on `Feature Spec` / `Attested Computation` concepts (ID format, BR rules, calc links) | — |
| `okf-validate.ps1` | OKF v0.2 §11 conformance + provenance/trust warnings for the whole bundle (`-Strict`, `-MaxWarnings N`) | — |
| `build-index.ps1` | regenerate every `index.md` (reserved OKF file) from concept frontmatter; `-Check` for CI | — |
| `validate-work-items.ps1` | check YAML against `work-items/_schema.yml` rules | — |
| `map-paths.ps1` | changed code paths → affected specs (uses `docs-map.yml`) | — |
| `check-freshness.ps1` | CI gate: mapped code changed but `last_verified` not bumped | — |
| `gen-graph.ps1` | join `generated/be`, `generated/fe` maps + `@docs` tags (+ optional `graph-export-*.json`) into `generated/graph/` (`graph.json`, `<community>.md`, `REPO_MAP.md`); `-Check` for CI; `-Budget N` lines for REPO_MAP | — |
| `graph-query.ps1` | query `graph.json`: `-Node <id|substring> -Depth n`, `-Files <changed paths>` (impacted specs), `-Find <text>`, `-Json`; CLI twin of the VS Code `#impact` tool for IntelliJ and CI | — |
| `jira-push.ps1` | create/update epic/stories/subtasks via Jira REST v3, write back keys | `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN` |
| `jira-csv.ps1` | fallback: export work items to Jira bulk-import CSV | — |
| `confluence-export.ps1` | Confluence REST → Markdown into `confluence-import/` | `CONFLUENCE_URL`, `CONFLUENCE_TOKEN` |
| `confluence-publish.ps1` | Markdown → Confluence page (one-way), keeps page id map in `.confluence-map.json` | same |
| `push-to-tests-repo.ps1` | copy `test-design/**` into tests repo branch + open PR | `TESTS_REPO_URL`, `GIT_TOKEN` |

Only `validate-frontmatter.ps1`, `okf-validate.ps1`, `build-index.ps1`, `map-paths.ps1`, `check-freshness.ps1`,
`gen-graph.ps1` and `graph-query.ps1` are implemented in this prototype; the others are stubs describing the intended API calls.

Python equivalents of the OKF checker/visualiser (vendored from `scaccogatto/okf-skills`, MIT) live under
`.github/skills/okf-validate/scripts/` and `.github/skills/okf-visualize/scripts/`; CI runs both flavours.
