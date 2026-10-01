---
mode: agent
description: Draft a feature spec skeleton for a module/feature from its graph neighbourhood, then fill prose from the facade only
---
Target community: ${input:community:BE module or FE feature name, e.g. hedges}. Spec ID to create: ${input:id:e.g. HEDGE-002}.

1. Read `generated/graph/${input:community}.md` only. Build the skeleton of `features/<ctx>/${input:id}.md` from
   `features/_template.md`:
   - **Interfaces** <- `endpoints` (method, path, handler `file:line`) and `routes`.
   - **Events** <- `topics` with produced/consumed direction.
   - **Data** <- `tables` with column lists.
   - **Calculations** <- `spec:*` nodes of kind calculation linked to this community.
   - **Code refs** frontmatter <- node locations (file only, no line, to stay stable).
2. For the Summary and Business rules, open **only** the facade file named on the `module:` node (`file`, whole file,
   it is small by convention) - no controllers, calculators or repositories.
3. Mark every rule you could not source as `❓ UNVERIFIED`; put gaps in **Open questions**.
4. Set frontmatter `generated.by: copilot/write-feature-spec`, `status: draft`; run `scripts/okf-validate.ps1 -Strict`
   and `scripts/build-index.ps1`.
Report in chat: sections filled from graph vs. from facade vs. left open (<= 10 lines).
