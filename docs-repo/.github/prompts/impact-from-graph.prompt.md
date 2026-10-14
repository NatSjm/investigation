---
name: impact-from-graph
description: Impact analysis of a change from the architectural graph (no source reading).
argument-hint: "spec ID | node id | changed file paths"
agent: impact-analyst
---
Subject: ${input:subject:spec ID, node id (topic:..., table:..., endpoint:..., class:...), or paste `git diff --name-only`}

Resolve the node, read `generated/graph/<community>.md` for its community (or run
`python3 scripts/graph-query.py --node "<id>" --depth 2`), and produce the checklist (BE / FE / Contracts / Docs / Tests /
Cross-context / Verify). Cite node ids and `file:line` only from the graph. If the subject is not in the graph, say so
and suggest the closest ids from `generated/graph/REPO_MAP.md`.
