# Work items (Jira)

One YAML per feature ID; schema in `_schema.yml`. Push with `scripts/jira-push.ps1 work-items/<ID>.yml`
(Jira REST v3; writes back `jira_key`). Import alternative without API access: `scripts/jira-csv.ps1` → CSV
for Jira's bulk importer.

Conventions:
- `feature` must exist under `features/`; `project` is the Jira project key of Harbor (`HRB`).
- Every acceptance criterion cites exactly one business rule `BR-<ID>-<n>` of that spec; a story without a rule
  to cite means the spec is incomplete — add the rule first, then the story.
- Subtask prefixes: `[DB]`, `[BE]`, `[FE]`, `[INT]`, `[TEST]`; each ≤ 8 h.
- `questions[]` collects what the analyst could not resolve from the spec; they are mirrored into the spec's
  "Open questions" section.

Rules: `.github/instructions/work-items.instructions.md` · Skill: `.github/skills/jira-work-items/SKILL.md`
· Agent: `analyst`.
