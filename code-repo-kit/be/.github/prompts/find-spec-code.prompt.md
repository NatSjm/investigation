---
agent: code-reader
description: Jump from a spec / calculation ID to code and summarise the implementation without reading unrelated files.
---
Where is `${input:specId:HEDGE-001}` implemented?

1. Look it up in `#file:docs/_generated/docs-tags.md`.
2. Open only the listed locations (narrow ranges).
3. Reply: declaration list with `file:line`, one-sentence behaviour each, and any mismatch you notice between the KDoc formula and the code.
Do not search the repository.
