# Porting notes: okf-skills (Claude Code) → GitHub Copilot

Source: https://github.com/scaccogatto/okf-skills (MIT) · Spec: GoogleCloudPlatform/open-knowledge-format (Apache-2.0).

| Claude Code construct | What we did |
|---|---|
| `skills/okf/SKILL.md` | Rewritten as `.github/skills/okf/SKILL.md`; repo-specific type vocabulary, actor names, default bundle = repo root (not `.okf/`) |
| `skills/validate`, `skills/visualize` | `.github/skills/okf-validate/`, `okf-visualize/`; Python scripts vendored unchanged for CI; **PowerShell port** of the validator core in `scripts/okf-validate.ps1` for Windows dev machines without Python |
| `${CLAUDE_SKILL_DIR}`, `$ARGUMENTS`, `/okf:<skill>` | Fixed repo paths; prompt files `.github/prompts/okf-*.prompt.md` with `${input:…}` |
| `user-invocable`, `argument-hint`, `allowed-tools` frontmatter | Dropped (Copilot only reads `name`, `description`) |
| `agents/event-analyzer`, `agents/bundle-weaver` (backfill map/reduce) | Not ported — git-history/transcript backfill is low value here; `confluence-migrator` agent covers legacy import |
| `hooks/` Stop hook (`upkeep: enforced`) | No IDE hook in Copilot → enforced in CI: `docs-quality.yml` runs the validator; code repos run `check-freshness.ps1` |
| `servers/okf_mcp.py`, `.mcp.json` | Not ported (MCP not permitted; Copilot reads files directly) |
| `templates/CLAUDE-okf.md` | Merged into `.github/copilot-instructions.md` ("OKF bundle" section) |
| `action.yml` (composite GitHub Action) | Not vendored; equivalent step inline in `.github/workflows/docs-quality.yml` |
| `.claude-plugin/`, `benchmark/`, `.okf/` self-bundle | Not needed |

Known gaps of the PowerShell port vs `okf_validate.py`: no `--migrate` (v0.1→v0.2), no `usage_window`
checks, no JSON output. Use the Python checker in CI for full §11 + warnings coverage.
