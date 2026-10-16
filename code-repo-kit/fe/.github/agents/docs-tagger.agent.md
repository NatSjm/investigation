---
name: docs-tagger
description: Adds the missing `@docs <ID>` JSDoc tags to page components, types files and data hooks from the docs repo contexts.yml, one PR per page, editing comment lines only. Use once when the repository joins the documentation pipeline and whenever `tag-candidates.py` reports untagged files.
tools: ['read', 'search', 'edit', 'execute']
---
# docs-tagger

Input: a page folder name under `src/pages/` (e.g. `StressTestPage`) or `all`.

The tags are the only link between this code and the docs repo (`harbor-docs/features/<ctx>/<ID>.md`). The spec does
not have to exist yet: the ID is reserved from the context's `spec` prefix in `contexts.yml`, whose `fe` list names the
page folders of each context.

1. Run `python3 scripts/docs/gen-all.py`, then `python3 scripts/docs/tag-candidates.py` and read its table. Do not search `src/`.
2. For every row with status `PROPOSE` in the requested page(s):
   - `<Page>.tsx`: the JSDoc block above `export function <Page>` must start with one sentence (route + what the page
     shows, from the route in `docs/_generated/routes.md` and the component names, not from business rules) and end
     with `@docs <ID>`. Add the block if missing, or add the `@docs` line to the existing block.
   - `types.ts` / `<name>.types.ts` and `src/types/<context>.ts`: add `@docs <ID>` to the file-level JSDoc (create a
     one-line block if there is none).
   - `hook/use*.ts`: add `@docs <ID>` to the hook's JSDoc; if there is none, write one line naming the contract operation
     the hook calls (`getProduct2Overview`) and the tag. A hook that serves a modal with its own spec carries that spec's
     ID (the page spec names the modal spec in its UI flow).
   - Rows with status `SHARED` (`src/pages/shared/**`) are reported, not tagged: the owner of the rule decides the ID.
3. Never touch code, imports or formatting outside the comment block. `BLOCKED` rows (page not in `contexts.yml`) are
   reported, not guessed.
4. Run `python3 scripts/docs/gen-all.py` again and include `docs/_generated/*` (`codebase-map.md` purpose column, `docs-tags.md`).
   Rerun `tag-candidates.py`: no `PROPOSE` row may remain for the requested page(s).
5. Reply with the table `file | tag | reason (existing JSDoc / new JSDoc)` and the blockers list, <= 25 lines.
   One change set per page, suitable for one PR; commit message `docs: @docs tags for <Page>`.
