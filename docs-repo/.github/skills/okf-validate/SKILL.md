---
name: okf-validate
description: Check the docs bundle for Open Knowledge Format v0.2 conformance (§11) with a deterministic checker — once at the end of a task that changed concepts (--changed), when asked to validate/lint the bundle, or to migrate v0.1 frontmatter with --migrate. Never after each edit; never eyeball conformance.
---

# Validate the OKF bundle

`okf_validate.py` is vendored unchanged from `scaccogatto/okf-skills` (MIT, `third-party/okf-skills/LICENSE`);
`scripts/okf-validate.py` is our standard-library port of its core (no pyyaml needed) (attribution in its header). This SKILL.md is rewritten for Copilot.

Pick the checker by environment:

| Where | Command |
|---|---|
| Dev machine (no pyyaml) | `scripts/okf-validate.py [--changed [BASE]] [--path <folder or file>] [--strict] [--max-warnings N]` |
| CI / full checker | `python3 .github/skills/okf-validate/scripts/okf_validate.py <bundle> --strict` (needs `pyyaml`; `--json` for machine output). It has **no exclude list**, so point it at a staged copy of `index.md log.md README.md architecture domain features generated` (see `.github/workflows/docs-quality.yml`), not at the repo root. |

An agent runs it once, after the last edit of a task that changed concepts, as `--changed --strict`; a task that
only read runs nothing, and the `agentStop` hook runs the whole bundle again (`AGENTS.md`, Checks).
`--changed` takes the files changed since BASE (default `HEAD`) plus untracked ones, `--path` a folder or a file; both
only choose which files can fail. The whole bundle is always read, so links resolve from its root (the folder whose
`index.md` carries `okf_version`), a link broken by a renamed or deleted file counts against the change, and the other
files' problems are one count line.

Template files (`_template.md`, `template.md`) are checked for §11 only; placeholder values do not raise warnings.

Interpret the result:
- **ERROR** — hard §11 failure: no parseable frontmatter, missing/empty `type`, unreadable file. A `README.md`
  inside the bundle is an ERROR — rename to `index.md` or add `type: Document`. Fix all.
- **warn** — soft: missing `title`/`description`, broken cross-link (spec-tolerated), non-ISO date, actor not
  matching §7 shapes, `Attested Computation` without `runtime`, frontmatter in a reserved file, root `index.md`
  with unexpected keys. Fix when cheap; `--strict` turns them into failures.
- **stale** — past `stale_after` (§5.5): freshness, not conformance. Listed, never counted as a warning, never fails
  a run (the reference checker does not report it). A person re-verifies a spec, its generator refreshes a generated
  page; never move `stale_after` or write `verified` to clear it.
- Fix on sight: `Human:jdoe` / `human/jdoe` — trust tier silently drops to machine-confirmed.

`--migrate` (Python only) **rewrites files in place** (`timestamp` → `generated.at`, `# Citations` → `sources`);
tell the user before running it on content they did not ask to migrate.

Exit code non-zero on any ERROR in the checked files, or when their warnings exceed the gate (`--strict` = 0,
`--max-warnings N`); stale lines never count.
