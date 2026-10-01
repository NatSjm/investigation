---
description: Validate the OKF documentation bundle and fix conformance errors.
agent: agent
---

Path: ${input:path:.}
Strictness: ${input:strict:-Strict}

1. Run `scripts/okf-validate.ps1 -Path ${input:path} ${input:strict}` (fallback: the Python checker in
   `.github/skills/okf-validate/scripts/`).
2. For every ERROR, fix the file (add frontmatter with `type`, rename stray `README.md` to `index.md`).
3. For warnings, fix the cheap ones (missing `description`, actor casing, broken internal link).
4. Re-run until clean. Report: counts before/after, files changed (≤ 10 lines).
