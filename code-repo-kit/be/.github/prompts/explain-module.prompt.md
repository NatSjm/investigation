---
agent: code-reader
description: Explain a module from its facade and the generated map, in <= 20 lines.
---
Explain module `${input:module:hedges}` for a developer who is new to it.

Use only `#file:docs/_generated/codebase-map.md` and the facade file it lists for that module.
Cover: responsibility, entry points (endpoints/topics/jobs from the maps), main collaborators, spec IDs (`@docs`).
Finish with "Open next:" and at most 3 `file:line` suggestions.
