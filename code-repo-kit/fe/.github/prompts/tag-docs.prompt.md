---
agent: docs-tagger
description: Add the missing @module / @docs tags to the barrel, types file and hooks of one feature (or all), comment lines only, one PR per feature.
argument-hint: "feature folder under src/features, e.g. stress, or all"
---
Tag the files of feature `${input:feature:all}` with `@module` / `@docs <ID>`.

Follow the `docs-tagger` procedure: `scripts/docs/tag-candidates.py` is the only inventory you use; edit JSDoc comment
lines only; every file of a feature carries the barrel's ID; regenerate `docs/_generated/*` and rerun the candidates
script until no `PROPOSE` row remains for the feature. Report the `file | tag | reason` table and the blockers (folders
missing in `contexts.yml`), nothing else.
