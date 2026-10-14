---
agent: docs-tagger
description: Add the missing @docs tags to the managers and calculations of one context (or all), comment lines only, one PR per context.
argument-hint: "context name from contexts.yml, e.g. product1, or all"
---
Tag the managers and calculations of `${input:context:all}` with `@docs <ID>`.

Follow the `docs-tagger` procedure: `scripts/docs/tag-candidates.py` is the only inventory you use; edit KDoc comment
lines only; calculation IDs are `snake_case` names of the quantity computed, not of the class; regenerate
`docs/_generated/*` and rerun the candidates script until no `PROPOSE` row remains for the context. Report the
`class | tag | reason` table and the blockers (prefixes missing in `contexts.yml`), nothing else.
