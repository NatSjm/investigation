# scripts/docs (harbor-frontend)

| Script | Needs | Output |
|---|---|---|
| `gen-*.py`, `gen-all.py [--check]` | Python 3.11+ (standard library) | `docs/_generated/*.md` regex maps (`codebase-map`, `components`, `routes`, `types-index`, `docs-tags`, `index`); `--check` writes a throwaway copy into a system temp folder it creates and removes in a `finally` block (also after a failed generator or stale output), nothing under the repository; no bytecode cache (`sys.dont_write_bytecode`, children started with `-B`) |
| `tag-candidates.py --contexts <docs repo>/contexts.yml` | same | inventory for the docs-tagger agent (stdout or `--out`) |
| `gen-graph-fe.ts` | the repo's existing `typescript` + `@types/node` devDependencies (no new library) | `docs/_generated/graph-export-fe.json` precise graph (TS compiler API) |

## Layout: `docs-gen.json`
The generators do not hard-code the folder layout; they read `scripts/docs/docs-gen.json` next to them (or `--config <file>`).
Every key is optional and falls back to the values below (the Harbor layout):

| Key | Meaning | Harbor value |
|---|---|---|
| `pages_dir` | one folder per routed page | `src/pages` |
| `not_pages` | folders under `pages_dir` that are not pages (shared pieces); one row each | `["shared"]` |
| `page_entry` | file read for the page's purpose and `@docs` tag (`<Page>` = folder name, first match wins) | `["<Page>.tsx", "index.tsx", "index.ts"]` |
| `hook_dirs` | folder names whose `use*.ts` files are the page's data hooks | `["hook", "hooks", "api"]` |
| `components_dir` | folder name holding the page's components (`<Name>/` folders or `<Name>.tsx` files) | `components` |
| `shared_dir` | the in-house component library scanned by `gen-components.py` | `src/components` |
| `app_dirs` | app shell (routing, layouts, channel modules, entry files): the `fe-app` row | `src/routing`, `src/components/layout`, `src/components/broadcast`, `src/components/hook`, `src/App.tsx`, `src/main.tsx` |
| `route_files` | files or folders scanned for react-router route objects / `<Route>` | `["src/routing"]` |
| `route_constants` | files with `export const ROUTES = { KEY: '/path' }` objects, resolved as `ROUTES.KEY` | `["src/constants/routes.ts"]` |
| `types` | globs of the files indexed by `gen-types-index.py` | `src/types/**/*.ts`, `src/pages/**/*.types.ts`, `src/pages/**/types.ts` |
| `exclude_paths` | never read (generated clients such as Orval or openapi-typescript output) | `["src/services/openapi", "src/api/generated"]` |
| `test_pattern` | regex on file names that marks tests, stories, specs | `\.(test\|spec\|stories)\.` |
| `api_call_pattern` | regex whose first non-empty group is the literal path of an API call | openapi-fetch / fetch / axios calls |

What a generator still assumes beyond the config: hooks are named `use<Name>`; components are PascalCase exports; the
page's purpose is the first sentence of the JSDoc above `export function <Page>`; `@docs <ID>` is one ID per `@docs`
line; a BroadcastChannel is opened in exactly one module per channel (`new BroadcastChannel(`), with the channel name
in a `*CHANNEL*` constant. With a generated client (Orval) the `API calls` column stays empty because hooks call
generated functions instead of literal paths; the backend `api-index.md` plus `@docs` tags carry that link instead.

Run the exporter from the repo root so `node_modules` resolves:

```
npx tsc -p scripts/docs/tsconfig.gen.json
node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json
```

What the exporter sees: one `feature:` node per page folder (and per `not_pages` folder), exported hooks (`use*`) and
components (PascalCase), `calls` edges from `api.GET('/session/product1/overview', ...)`-style calls (literal contract
path + method), `uses` / `renders` edges resolved through the type checker and `depends-on` edges between pages.

IDE note: in the investigation workspace (`code-repo-kit/fe/...`) there is no `node_modules`, so the editor shows
`Cannot find module 'typescript'` / implicit-any errors for `gen-graph-fe.ts`. They disappear in the real frontend repo
(or after `npm i` in a folder whose `node_modules` contains `typescript` and `@types/node`). The file compiles
cleanly under `strict: true`.

If `@types/node` is not in the frontend repo, add this shim next to the script instead of a new dependency:
`declare module 'fs'; declare module 'path';` in `node-shim.d.ts` and list it in `tsconfig.gen.json` `files`.
