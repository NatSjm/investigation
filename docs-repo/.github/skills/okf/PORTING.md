# Porting notes: okf-skills (Claude Code) → GitHub Copilot

Source: https://github.com/scaccogatto/okf-skills (MIT) · Spec: GoogleCloudPlatform/open-knowledge-format (Apache-2.0).

| Claude Code construct | What we did |
|---|---|
| `skills/okf/SKILL.md` | Rewritten as `.github/skills/okf/SKILL.md`; repo-specific type vocabulary, actor names, default bundle = repo root (not `.okf/`) |
| `skills/validate`, `skills/visualize` | `.github/skills/okf-validate/`, `okf-visualize/`; Python scripts vendored unchanged for CI; **standard-library port** of the validator core in `scripts/okf-validate.py` for machines without pip packages (no pyyaml) |
| `${CLAUDE_SKILL_DIR}`, `$ARGUMENTS`, `/okf:<skill>` | Fixed repo paths; prompt files `.github/prompts/okf-*.prompt.md` with `${input:…}` |
| `user-invocable`, `argument-hint`, `allowed-tools` frontmatter | Dropped (Copilot only reads `name`, `description`) |
| `agents/event-analyzer`, `agents/bundle-weaver` (backfill map/reduce) | Not ported — git-history/transcript backfill is low value here; `confluence-migrator` agent covers legacy import |
| `hooks/` Stop hook (`upkeep: enforced`) | No IDE hook in Copilot → enforced in CI: `docs-quality.yml` runs the validator; code repos run `check-freshness.py` |
| `servers/okf_mcp.py`, `.mcp.json` | Not ported (MCP not permitted; Copilot reads files directly) |
| `templates/CLAUDE-okf.md` | Merged into `.github/copilot-instructions.md` ("OKF bundle" section) |
| `action.yml` (composite GitHub Action) | Not vendored; equivalent step inline in `.github/workflows/docs-quality.yml` |
| `.claude-plugin/`, `benchmark/`, `.okf/` self-bundle | Not needed |

Known gaps of the standard-library port vs `okf_validate.py`: no `--migrate` (v0.1→v0.2), no `usage_window`
checks, no JSON output. Use the Python checker in CI for full §11 + warnings coverage.
Additions of the port: `--path <folder or file>` chooses which files can fail while the whole bundle is still read
(links resolve from the root `index.md` that carries `okf_version`); a past `stale_after` is listed as `stale` and
never fails a run (the reference checker does not report it). A repo rule of this bundle, not of the OKF spec: in a draft `Feature Spec` no person has
verified, a business rule without a `(source: ...)` marker, a marker naming no `sources[].id`, or a code marker without a
`#symbol` is a warning (`features/conventions.md`, "Provenance per rule").
