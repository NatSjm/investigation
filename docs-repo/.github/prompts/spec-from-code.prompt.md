---
description: Create or refresh a feature spec for a given feature ID using generated artifacts (cheap) before code (expensive).
agent: doc-sync
---

Feature ID: ${input:featureId:e.g. HEDGE-012}
Context hint (optional): ${input:hint:module name, endpoint, or screen}

Steps:
1. Locate entry points in `generated/codebase-map.md` using the ID/hint.
2. Collect contract facts from `generated/openapi`, `generated/asyncapi`, `generated/db/schema.md`,
   `generated/api-surface`.
3. Fill `features/<ctx>/${input:featureId}.md` from `features/_template.md`. Number business rules.
4. If any business rule cannot be derived from artifacts, open **only** the function named in the codebase map,
   narrow range, and derive it. Note the file:line in `code_refs`.
5. Add mapping to `docs-map.yml`.
