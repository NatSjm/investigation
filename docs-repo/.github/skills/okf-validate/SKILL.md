---
name: okf-validate
description: Check the docs bundle for Open Knowledge Format v0.2 conformance (§11) with a deterministic checker — use before committing any doc change, when asked to validate/lint the bundle, or to migrate v0.1 frontmatter with --migrate. Never eyeball conformance.
---

# Validate the OKF bundle

`okf_validate.py` is vendored unchanged from `scaccogatto/okf-skills` (MIT, `third-party/okf-skills/LICENSE`);
`scripts/okf-validate.ps1` is our PowerShell port of its core (attribution in its header). This SKILL.md is rewritten for Copilot.

Pick the checker by environment:

| Where | Command |
|---|---|
| Windows dev machine (no Python) | `scripts/okf-validate.ps1 [-Path .] [-Strict] [-MaxWarnings N]` |
| CI / full checker | `python .github/skills/okf-validate/scripts/okf_validate.py <bundle> --strict` (needs `pyyaml`; `--json` for machine output). It has **no exclude list**, so point it at a staged copy of `index.md log.md README.md architecture domain features generated` (see `.github/workflows/docs-quality.yml`), not at the repo root. |

Template files (`_template.md`, `template.md`) are checked for §11 only; placeholder values do not raise warnings.

Interpret the result:
- **ERROR** — hard §11 failure: no parseable frontmatter, missing/empty `type`, unreadable file. A `README.md`
  inside the bundle is an ERROR — rename to `index.md` or add `type: Document`. Fix all.
- **warn** — soft: missing `title`/`description`, broken cross-link (spec-tolerated), non-ISO date, actor not
  matching §7 shapes, `Attested Computation` without `runtime`, frontmatter in a reserved file, root `index.md`
  with unexpected keys. Fix when cheap; `-Strict` turns them into failures.
- Fix on sight: `Human:jdoe` / `human/jdoe` — trust tier silently drops to machine-confirmed.

`--migrate` (Python only) **rewrites files in place** (`timestamp` → `generated.at`, `# Citations` → `sources`);
tell the user before running it on content they did not ask to migrate.

Exit code non-zero on any ERROR, or when warnings exceed the gate (`-Strict` = 0, `-MaxWarnings N`).
