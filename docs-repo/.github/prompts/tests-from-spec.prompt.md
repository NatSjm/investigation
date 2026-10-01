---
description: Generate Gherkin test cases and synthetic fixtures from a feature spec.
agent: test-designer
---

Feature ID: ${input:featureId}
Layers to cover: ${input:layers:api,ui,calc,kafka}

Produce `test-design/features/${input:featureId}.feature` and fixtures. Print the rule → scenario coverage
matrix only.
