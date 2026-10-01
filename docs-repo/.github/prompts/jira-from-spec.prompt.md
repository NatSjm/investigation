---
description: Generate Jira epic/stories/subtasks YAML from a feature spec.
agent: analyst
---

Feature ID: ${input:featureId}
Team mode: ${input:mode:vertical|component}
Sprint capacity hint (optional): ${input:capacity}

Produce `work-items/${input:featureId}.yml` following `work-items/_schema.yml`. Then print story summaries and
open questions only.
