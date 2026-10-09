---
name: spec-skeleton-from-graph
description: Draft a feature spec for a bounded-context community from its graph neighbourhood, then fill prose from the manager file only.
argument-hint: "community spec-id (e.g. product2 P2-001)"
agent: spec-writer
---
Target community: ${input:community:product2} (bounded context from `contexts.yml`: BE class-name prefixes + FE feature). Spec ID to create: ${input:id:P2-001}.

Build the pack for the community, create `features/<ctx>/${input:id}.md` from `features/_template.md`:
API / Events / Data / UI flow / Calculations and frontmatter from `generated/graph/${input:community}.md`;
Summary, Actors and Business rules from the manager file named on the `context:` node (layer `manager/`) only. Mark unsourced rules
`❓ UNVERIFIED`; collect gaps under Open questions; `status: draft`. Add the `docs-map.yml` mapping, validate, rebuild
indexes, log. Report which sections came from the graph, the manager, legacy pages, and what is open (<= 10 lines).
