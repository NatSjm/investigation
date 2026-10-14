---
name: docs-tagger
description: Adds the missing `@docs <ID>` KDoc tags to manager and calculation classes from the docs repo contexts.yml, one PR per context, editing comment lines only. Use once when a repository joins the documentation pipeline and whenever `tag-candidates.py` reports untagged classes.
tools: ['read', 'search', 'edit', 'execute']
---
# docs-tagger

Input: a context name from `contexts.yml` (e.g. `product1`) or `all`.

The tags are the only link between this code and the docs repo (`harbor-docs/features/<ctx>/<ID>.md`,
`harbor-docs/domain/calculations/<id>.md`). The spec files do not have to exist yet: the ID is reserved from the
context's `spec` prefix and the spec is written later from the graph (`spec-skeleton-from-graph` in the docs repo).

1. Run `python3 scripts/docs/gen-all.py` (fresh maps), then `python3 scripts/docs/tag-candidates.py` and read its table.
   Do not search the repository: the table lists every manager and calculation with `file:line`.
2. For every row with status `PROPOSE` in the requested context(s):
   - **Manager** (`manager/<Ctx>Manager.kt`): open the listed location. If the class already has a KDoc block, add
     ` * @docs <Proposed>` as its last line. If it has none, write a KDoc of 1-3 lines that summarises what the manager
     does *from its public functions only* (no business rules, no numbers), ending with `@docs <Proposed>`. Place the
     block directly above the annotations (`@Service`), never between them and `class`.
   - **Calculation** (`utils/`): same, but choose the ID yourself: a `snake_case` name of the business quantity the class
     computes, taken from the KDoc or the main function name (`monthly_projection`, `cover_ratio`), not of the class
     (`projection_aggregator` is wrong). One tag per public calculation entry point; a class with two independent
     calculations gets two tags. Name the unit test that holds the examples in the KDoc if it exists.
   - **Function table** (second table, public functions of the `utils/` classes): a function with status `REVIEW` is
     either a sub-calculation of its own (it has a business name a spec would cite, is reused by other calculations
     or managers, and has or deserves its own test cases) -> add `@docs <snake_case quantity>` to its KDoc; or a step
     of the class's calculation -> no tag, list it in the summary as `step of <class tag>`. Never change visibility
     or move code; suggest `private` in the summary when a step is only used inside the file.
   - **`REVIEW` rows** (`utils/` classes with no context prefix, e.g. a month grid or a rounding helper): tag them only if
     they compute a business quantity with a formula a spec would cite; plain helpers stay untagged and are listed in
     the summary as "helper, no tag" so a person can object.
   - A class in a capability context that serves several products through a parameter or enum (`productGroup`,
     `dimension`, `transportMode`) keeps **one** tag: product variants are rules inside that spec, not separate IDs.
     Note it in the summary as `serves product1, product2`. Only a class with a product prefix of its own
     (`Product2Stress*`) belongs to a product context, and the prefix rule already puts it there.
   - A manager that clearly covers two features gets two tags (`@docs P1-001`, `@docs P1-002`) and a note in the summary;
     a person decides whether to split the spec later.
3. Never touch code, annotations, imports or formatting outside the comment block. Never invent a context: `BLOCKED` rows
   go to the summary as "add prefix `X` to contexts.yml", unchanged.
4. Run `python3 scripts/docs/gen-all.py` again and include `docs/_generated/*` (the `@docs` column of `components.md` and
   `docs-tags.md` must show the new tags). Run `python3 scripts/docs/tag-candidates.py` once more: no `PROPOSE` row may remain
   for the requested context(s).
5. Reply with the table `class | tag | reason (existing KDoc / new KDoc / two features)` and the blockers list, <= 25 lines.
   One change set per context, suitable for one PR; commit message `docs: @docs tags for <context>`.
