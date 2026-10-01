---
applyTo: "work-items/**/*.yml"
---

# Work item (Jira) rules

- One YAML file per feature ID; structure per `work-items/_schema.yml`.
- Hierarchy: `epic` → `stories[]` → `subtasks[]`. Stories are vertical slices (FE + BE + test) unless the team
  works component-wise; then tag `component: fe|be|db|integration`.
- Every story has: `summary` (≤ 80 chars, imperative), `description`, `acceptance_criteria` (Gherkin
  `Given/When/Then`, each citing a `BR-*` rule), `estimate` (story points, Fibonacci), `labels`, `depends_on`.
- Subtasks are technical and ≤ 1 day: e.g. "Add Liquibase changeset for hedge_limit", "Expose GET /hedges/{id}/limits".
- Do not invent IDs for Jira; leave `jira_key: null` — `scripts/jira-push.ps1` fills it after creation.
- Never include client or production data.
