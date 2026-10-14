---
name: coverage-report
description: Documentation analytics - which business rules have stories and scenarios, which specs are stale or unverified, which code has no spec.
argument-hint: "[context prefix, e.g. P1]"
agent: analyst
---
Scope: ${input:scope:all}

1. Run `python3 scripts/coverage-matrix.py` and read `generated/analytics/coverage-matrix.md`.
2. Read the trust badges in `features/index.md` and each `features/<ctx>/index.md`, and the **Spec coverage**
   section of `generated/graph/REPO_MAP.md`.
3. Report (<= 25 lines): per spec in scope - rules total / with story / with scenario, badge, stale_after;
   `code only` communities without a spec; `spec only` specs without code tags; the three most valuable gaps to close next.
Do not open source code.
