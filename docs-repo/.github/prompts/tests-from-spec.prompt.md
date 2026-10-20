---
name: tests-from-spec
description: Generate Gherkin test cases and synthetic fixtures for a feature from its context pack.
argument-hint: "featureId | request slug [layers]"
agent: test-designer
---
Feature ID (or request slug of `work-items/<slug>.yml`; then one feature file per spec it names): ${input:featureId:STR-001}
Layers to cover: ${input:layers:api,ui,calc,kafka}

Build the context pack; produce `test-design/features/${input:featureId}.feature` and fixtures; update the spec's
`tests:` list; run `python3 scripts/coverage-matrix.py`. Print the rule -> scenario coverage matrix only.
