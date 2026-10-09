---
name: jira-from-spec
description: Generate the Jira epic / stories / subtasks YAML for a feature from its context pack.
argument-hint: "featureId [vertical|component]"
agent: analyst
---
Feature ID: ${input:featureId:P1-001}
Team mode: ${input:mode:vertical|component}
Sprint capacity hint (optional): ${input:capacity}

Build the context pack for the feature, then produce `work-items/${input:featureId}.yml` following
`work-items/_schema.yml` with subtasks derived per graph node kind. Validate with
`./scripts/validate-work-items.ps1`. Print story summaries, estimates, `depends_on` and open questions only.
