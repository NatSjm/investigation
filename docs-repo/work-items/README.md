# Work items (Jira)

One YAML per feature ID; schema in `_schema.yml`. Push with `scripts/jira-push.ps1 work-items/<ID>.yml`
(Jira REST v3; writes back `jira_key`). Import alternative without API access: `scripts/jira-csv.ps1` → CSV
for Jira's bulk importer.

Rules: `.github/instructions/work-items.instructions.md` · Skill: `.github/skills/jira-work-items/SKILL.md`
· Agent: `analyst`.
