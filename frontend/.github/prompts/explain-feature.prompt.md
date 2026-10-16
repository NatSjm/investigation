---
agent: code-reader
description: Explain a frontend page from its component, hooks and the generated maps, in <= 20 lines.
argument-hint: "page folder, e.g. StressTestPage, Product1OverviewPage, SessionSummaryPage"
---
Explain page `${input:page:StressTestPage}` for a new developer.

Use only `#file:docs/_generated/codebase-map.md`, `#file:docs/_generated/routes.md` and the page component
`src/pages/${input:page:StressTestPage}/${input:page:StressTestPage}.tsx` (its JSDoc and the hooks it imports).
Cover: purpose (from the JSDoc), route and layout, components and hooks, backend operations called (literal contract
paths), spec IDs from `@docs` (e.g. `STR-001`).
Finish with "Open next:" and at most 3 file suggestions. Do not open components unless asked.
