---
name: spec-skeleton-from-graph
description: Draft a feature spec for a bounded-context community from its graph neighbourhood, then fill prose from the manager file only.
argument-hint: "community spec-id [entry file] (e.g. product2 P2-001; product1 P1-002 manager/ScenarioManager.kt)"
agent: spec-writer
---
Target community: ${input:community:product2} (bounded context from `contexts.yml`: BE class-name prefixes + FE feature). Spec ID to create: ${input:id:P2-001}.
Entry file (optional): ${input:entry:none} - the source file to read instead of the one named on the `context:` node,
for a context whose entry layer holds several peer classes (one per screen) and no `<Prefix>Manager`: the graph then
names one of them for the whole context, right for the first spec only; name the class of this spec's screen here.

Build the pack for the community, create `features/<ctx>/${input:id}.md` from `features/_template.md`:
API / Events / Data / UI flow / Calculations and frontmatter from `generated/graph/${input:community}.md`;
Summary, Actors and Business rules from the manager file named on the `context:` node (layer `manager/`) only, or
from the entry file when one is given (it replaces that file; still exactly one source file). Mark unsourced rules
`❓ UNVERIFIED`; collect gaps under Open questions; `status: draft`. Add the `docs-map.yml` mapping, validate, rebuild
indexes, log. Report which sections came from the graph, the manager, legacy pages, and what is open (<= 10 lines).
