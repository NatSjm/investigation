---
name: docs-map-from-contexts
description: Draft the `mappings` rows of docs-map.yml (code path globs -> spec files) from contexts.yml and the real file trees of the backend and frontend repositories; every glob is verified against at least one file. Evidence only; the human reviews and commits.
argument-hint: "optional: backend path, frontend path, context (default all)"
agent: architect
---
Backend repository: ${input:backend:../harbor-backend}
Frontend repository: ${input:frontend:../harbor-frontend}
Scope: ${input:scope:all}

## Role
Draft `docs-map.yml` of this repository, or the rows of one context when a scope is given. The file maps code path
globs (prefixed `be/` and `fe/`, relative to the two repository roots) to the spec files they affect. It is read by
`scripts/map-paths.py`, `scripts/check-freshness.py`, the collector's PR body and `scripts/gen-graph.py`
(`implemented-by` edges), so a wrong glob silently hides a spec from reviewers.

## Inputs (read-only)
- `contexts.yml`: per context the spec prefix, the `fe` list of page folders and the `be` class-name prefixes.
- `docs-map.yml` as it is (keep its comment header, the `ignore` list and every row you cannot improve).
- `features/<ctx>/*.md`, `flows/*.md`, `domain/calculations/*.md`: the spec files that exist (rows may name specs that
  do not exist yet only as `specs: []` with a `# TODO: <PREFIX>-001` comment).
- The two repositories' file trees (list, do not read file bodies beyond the first lines of a page component or a
  types file to confirm what it is). `generated/be/components.md` and `generated/fe/codebase-map.md` when they exist.

## Procedure
1. For every context: BE globs `be/<main source root>/**/<Prefix>*.kt` for each `be` prefix (one glob per prefix, a wildcard entry `*StressTest` becomes `**/*StressTest*.kt`; the
   `**/` stands for any layer folder); FE globs `fe/<pages dir>/<Page>/**` for each page in `fe`, plus the context's
   types file (`fe/src/types/<context>.ts` or the `*.types.ts` of the page) and the shared pieces that belong to it
   (`fe/src/pages/shared/components/<Name>/**`, `fe/src/pages/shared/hook/use<Name>*.ts`) when the page component imports
   them and no other context owns them. Resource folders that belong to one context (PDF templates, import fixtures)
   get their own glob.
2. Cross-cutting rows: calculators (`utils/**` -> `domain/calculations/**`), messaging (event package, kafka client
   module, AsyncAPI file -> `architecture/integrations.md`), external clients and their contracts, the OpenAPI file
   -> every spec with an `api` entry.
3. `ignore`: tests, generated clients, READMEs - keep what is there, add the generated client folder of the frontend
   if it is missing.
4. Verify every glob against the trees: it must match at least one existing file; a glob matching files of two
   contexts is allowed only when both specs are listed (say so in a comment). Remove nothing that still matches.

## Output
**A. The rewritten `docs-map.yml`** (or the rows of the scope, in place), YAML as in the current file: one `- paths:`
list per context in the order of `contexts.yml`, then the cross-cutting rows, then `ignore`. Comments only where a
glob needs an explanation. No product names other than this product's.

**B. In chat, under 15 lines:** rows added or changed, the globs that matched no file (and what you did instead),
pieces under the shared folders you could not assign to one context, and three paths the human should run through
`python3 scripts/map-paths.py <path>` to confirm the mapping.

## Rules
- Evidence only: a glob exists because a file matched it; no guessed folders.
- Do not edit `contexts.yml` or any spec. Do not run scripts; the human runs `map-paths.py` and `gen-graph.py`.
- Paths relative to the repository roots with the `be/` / `fe/` prefix, forward slashes, `**` only for folder spans.
