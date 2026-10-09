---
name: tests-from-spec
description: Generate Gherkin test cases and synthetic fixtures for a feature from its context pack.
argument-hint: "featureId [layers]"
agent: test-designer
---
Feature ID: ${input:featureId:STR-001}
Layers to cover: ${input:layers:api,ui,calc,kafka}

Build the context pack; produce `test-design/features/${input:featureId}.feature` and fixtures; update the spec's
`tests:` list; run `./scripts/coverage-matrix.ps1`. Print the rule -> scenario coverage matrix only.
