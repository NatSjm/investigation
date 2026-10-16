---
agent: docs-tagger
description: Add the missing @docs tags to the page component, types file and hooks of one page (or all), comment lines only, one PR per page.
argument-hint: "page folder under src/pages, e.g. StressTestPage, or all"
---
Tag the files of page `${input:page:all}` with `@docs <ID>`.

Follow the `docs-tagger` procedure: `scripts/docs/tag-candidates.py` is the only inventory you use; edit JSDoc comment
lines only; every file of a page carries the page's ID unless it serves a modal with its own spec; regenerate
`docs/_generated/*` and rerun the candidates script until no `PROPOSE` row remains for the page. Report the
`file | tag | reason` table, the `SHARED` rows left for the owner and the blockers (pages missing in `contexts.yml`),
nothing else.
