# Work items (Jira)

Two shapes, same `epic` -> `stories[]` -> `subtasks[]` structure; schema with both examples in `_schema.yml`:

| Shape | File(s) | When |
|---|---|---|
| **Feature epic** | `<FEATURE-ID>.yml` (e.g. `P1-001.yml`) | the work is one spec: `/jira-from-spec <ID>` |
| **Request epic** | `<slug>.yml` + `<slug>.md` (the analysis, template `_analysis-template.md`) | a request from an analyst in free text that spans several contexts, mixes existing and new behaviour, or follows a flow; `specs: [...]` lists every spec its stories cite |

Push with `scripts/jira-push.py work-items/<file>.yml` (Jira REST v3; writes back `jira_key`). Import alternative
without API access: `scripts/jira-csv.py` → CSV for Jira's bulk importer.

Conventions:
- A feature epic's `feature` must exist under `features/`; a request epic's `request` is lowercase kebab-case (never
  a spec ID) and every `specs[]` entry must exist. `project` is the Jira project key of Harbor (`HRB`).
- Every acceptance criterion cites exactly one business rule `BR-<ID>-<n>` of a spec the file names (the feature, or
  one of `specs[]`); a story may cite rules of several specs. A story without a rule to cite means the spec is
  incomplete — add the rule first (`spec-writer`, as a draft, label the story `needs-spec-review`), then the story.
  New behaviour in a context without a spec gets its first draft spec (`<PREFIX>-001`) before any story.
- Subtask prefixes: `[DB]`, `[BE]`, `[FE]`, `[INT]`, `[TEST]`, `[DOC]`; each ≤ 8 h. Across contexts the story that
  creates the contract / table / topic comes first and the others `depends_on` it.
- The analysis document (`<slug>.md`) is written before the YAML and holds the reading of the request the analyst
  confirmed, the parts with their state (unchanged / changed / new), the evidence, the contract and data changes,
  the gaps; it is the record of why the epic looks the way it does. `status: confirmed` once the analyst agreed.
- `questions[]` collects what the analyst could not resolve from the specs; they are mirrored into the specs'
  "Open questions" sections.
- `validate-work-items.py` checks both shapes; `coverage-matrix.py` counts a request epic's stories for every spec
  they cite.

Rules: `.github/instructions/work-items.instructions.md` · Skill: `.github/skills/jira-work-items/SKILL.md`
· Agent: `analyst`.
