---
name: spec-from-code
description: Refresh an existing feature spec against the current contracts, maps and graph; open source only for rules the artifacts cannot explain.
argument-hint: "featureId [hint]"
agent: spec-writer
---
Feature ID: ${input:featureId:STR-001}
Context hint (optional): ${input:hint:context name, endpoint, operationId or screen}

Steps:
1. Build the context pack; compare the spec's API / Events / Data sections with the contracts and maps in the pack.
2. Correct drift; append a Change log row; keep `BR-*` numbering stable (deprecate, never renumber).
3. For a rule that no artifact explains, open **only** the `file:line` the graph names for the handler or manager,
   a narrow range; cite it in `code_refs` and `sources[]`.
4. Set `last_verified` only for sections you actually checked; keep `status: draft` if open questions remain.
5. Validate, rebuild indexes, log.
