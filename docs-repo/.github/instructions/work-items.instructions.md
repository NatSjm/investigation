---
applyTo: "work-items/**/*.yml"
description: Rules for Jira work-item YAML (epic / stories / subtasks with Gherkin acceptance criteria), feature epics and request epics.
---

# Work item (Jira) rules

- One YAML file per feature ID (`<ID>.yml`, feature epic) or per analyst request (`<slug>.yml` with the analysis
  `<slug>.md` beside it, request epic, `specs: [...]`); structure per `work-items/_schema.yml`; validate with
  `scripts/validate-work-items.py`.
- Hierarchy: `epic` -> `stories[]` -> `subtasks[]`. Stories are vertical slices (FE + BE + test) unless the team
  works component-wise; then tag `component: fe|be|db|integration`.
- Every story has: `summary` (<= 80 chars, imperative), `description`, `acceptance_criteria` (Gherkin
  `Given/When/Then`, each citing an existing `BR-<ID>-<n>` of the feature or of a spec in `specs[]`), `estimate`
  (story points, Fibonacci), `labels`, `depends_on`.
- Subtasks are technical and <= 1 day, derived from the graph neighbourhood of the spec
  (`.github/skills/code-graph/references/subtask-mapping.md`): e.g. "[DB] migration V10__stress_test_result_dimension.sql",
  "[BE] Product1Controller.getProduct1Overview: add city filter", "[FE] stress: DimensionToggle for TRANSPORT_MODE".
- Cross-community edges in the graph become `depends_on`, not subtasks; in a request epic the story that creates a
  contract, table or topic comes first and the stories of the other contexts depend on it.
- Unknowns go to `questions[]`; never guess a rule that is not in the spec. New behaviour gets a draft rule or draft
  spec from `spec-writer` first (stories citing it carry `needs-spec-review`); a new operation gets a proposal under
  `contracts/proposed/` cited as proposed (`needs-contract`).
- A request epic is written after its analysis document (`_analysis-template.md`) and only once the analyst confirmed
  the Reading in it.
- Do not invent Jira keys; leave `jira_key: null` - `scripts/jira-push.py` fills it after creation.
- Never include client or production data.
