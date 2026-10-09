---
name: okf-validate
description: Validate the OKF documentation bundle and fix conformance errors.
argument-hint: "[path] [-Strict]"
agent: agent
tools: ['read', 'edit', 'execute']
---
Path: ${input:path:.}
Strictness: ${input:strict:-Strict}

1. Run `./scripts/okf-validate.ps1 -Path ${input:path} ${input:strict}` (fallback: the Python checker in
   `.github/skills/okf-validate/scripts/`). Also run `./scripts/validate-frontmatter.ps1` and `./scripts/validate-work-items.ps1`.
2. For every ERROR, fix the file (add frontmatter with `type`, rename stray `README.md` to `index.md`).
3. For warnings, fix the cheap ones (missing `description`, actor casing, broken internal link).
4. Re-run until clean; `./scripts/build-index.ps1`. Report: counts before/after, files changed (<= 10 lines).
