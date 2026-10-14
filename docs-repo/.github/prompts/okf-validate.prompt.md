---
name: okf-validate
description: Validate the OKF documentation bundle and fix conformance errors.
argument-hint: "[path] [--strict]"
agent: agent
tools: ['read', 'edit', 'execute']
---
Path: ${input:path:.}
Strictness: ${input:strict:--strict}

1. Run `python3 scripts/okf-validate.py --path ${input:path} ${input:strict}` (fallback: the Python checker in
   `.github/skills/okf-validate/scripts/`). Also run `python3 scripts/validate-frontmatter.py` and `python3 scripts/validate-work-items.py`.
2. For every ERROR, fix the file (add frontmatter with `type`, rename stray `README.md` to `index.md`).
3. For warnings, fix the cheap ones (missing `description`, actor casing, broken internal link).
4. Re-run until clean; `python3 scripts/build-index.py`. Report: counts before/after, files changed (<= 10 lines).
