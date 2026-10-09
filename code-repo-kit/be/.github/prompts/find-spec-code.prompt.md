---
agent: code-reader
description: Jump from a spec or calculation ID to the code and summarise the implementation without reading unrelated files.
argument-hint: "spec or calculation ID, e.g. P1-001 or monthly_projection"
---
Where is `${input:specId:P1-001}` implemented?

1. Look it up in `#file:docs/_generated/docs-tags.md`.
2. Open only the listed locations (narrow ranges).
3. Reply: declaration list with `file:line`, one-sentence behaviour each, and any mismatch you notice between the KDoc
   formula and the code. For a calculation ID also name the unit test that holds the worked examples.
Do not search the repository. If the ID is not tagged, say so and suggest which manager or `utils` class should carry `@docs`.
