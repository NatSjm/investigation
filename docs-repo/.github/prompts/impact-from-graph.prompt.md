---
mode: agent
description: Impact analysis of a change from the architectural graph (no source reading)
---
Use agent `impact-analyst`. Subject: ${input:subject:spec ID, node id (topic:..., table:..., endpoint:...), or paste `git diff --name-only`}.

Steps: resolve the node, read `generated/graph/<community>.md` for its community (or run
`scripts/graph-query.ps1 -Node "<id>" -Depth 2`), and produce the checklist (BE / FE / Docs / Tests / Cross-context / Verify).
Cite node ids and `file:line` only from the graph. If the subject is not in the graph, say so and suggest the
closest ids from `generated/graph/REPO_MAP.md`.
