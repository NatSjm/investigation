---
agent: code-reader
description: Explain a frontend feature from its barrel, types and the generated maps, in <= 20 lines.
argument-hint: "feature name, e.g. stress, product1, meetings"
---
Explain feature `${input:feature:stress}` for a new developer.

Use only `#file:docs/_generated/codebase-map.md`, `#file:docs/_generated/routes.md` and the feature's `index.ts` / `<feature>.types.ts`.
Cover: purpose (from `@module`), routes, public components and hooks, backend operations called (literal contract paths),
spec IDs from `@docs` (e.g. `STR-001`).
Finish with "Open next:" and at most 3 file suggestions. Do not open components unless asked.
