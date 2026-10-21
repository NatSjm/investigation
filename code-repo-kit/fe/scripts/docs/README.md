# scripts/docs (harbor-frontend)

| Script | Needs | Output |
|---|---|---|
| `gen-*.py`, `gen-all.py [--check]` | Python 3.11+ (standard library) | `docs/_generated/*.md` regex maps (`codebase-map`, `components`, `routes`, `types-index`, `docs-tags`, `index`); `--check` writes a throwaway copy into a system temp folder it creates and removes in a `finally` block (also after a failed generator or stale output), nothing under the repository; no bytecode cache (`sys.dont_write_bytecode`, children started with `-B`) |
| `tag-candidates.py --contexts <docs repo>/contexts.yml` | same | inventory for the docs-tagger agent (stdout or `--out`) |
| `gen-graph-fe.ts` | the repo's existing `typescript` (7.0 or later: the native compiler's `typescript/unstable/sync` and `typescript/unstable/ast` modules) + `@types/node` devDependencies (no new library) | `docs/_generated/graph-export-fe.json` precise graph (TS compiler API) |

## Layout: `docs-gen.json`
The generators do not hard-code the folder layout; they read `scripts/docs/docs-gen.json` next to them (or `--config <file>`).
Every key is optional and falls back to the values below (the Harbor layout):

| Key | Meaning | Harbor value |
|---|---|---|
| `pages_dir` | one folder per routed page | `src/pages` |
| `not_pages` | folders under `pages_dir` that are not pages (shared pieces); one row each | `["shared"]` |
| `page_entry` | file read for the page's purpose and `@docs` tag (`<Page>` = folder name, first match wins) | `["<Page>.tsx", "index.tsx", "index.ts"]` |
| `hook_dirs` | folder names whose `use*.ts` files are the page's data hooks | `["hook", "hooks", "api"]` |
| `components_dir` | folder name holding the page's components (`<Name>/` folders or `<Name>.tsx` files); `gen-components.py` lists them in its Page components table | `components` |
| `shared_dir` | the in-house component library: the Library table of `gen-components.py` | `src/components` |
| `app_dirs` | app shell (routing, layouts, channel modules, entry files): the `fe-app` row | `src/routing`, `src/components/layout`, `src/components/broadcast`, `src/components/hook`, `src/App.tsx`, `src/main.tsx` |
| `route_files` | files or folders scanned for react-router route objects / `<Route>` | `["src/routing"]` |
| `route_constants` | files with `export const ROUTES = { KEY: '/path' }` objects, resolved as `ROUTES.KEY` | `["src/constants/routes.ts"]` |
| `types` | globs of the files indexed by `gen-types-index.py` | `src/types/**/*.ts`, `src/pages/**/*.types.ts`, `src/pages/**/types.ts` |
| `exclude_paths` | never read (generated clients such as Orval or openapi-typescript output) | `["src/services/openapi", "src/api/generated"]` |
| `test_pattern` | regex on file names that marks tests, stories, specs | `\.(test\|spec\|stories)\.` |
| `api_call_pattern` | regex whose first non-empty group is the literal path of an API call | openapi-fetch / fetch / axios calls |
| `generated_client` | generated API client (Orval output) whose exported functions the hooks call: `dirs` (its folders, repo-relative; read by `gen-codebase-map.py` only, so they may stay in `exclude_paths`), `function_pattern` (group 1 = exported function name), `call_pattern` (first non-empty group = the literal path in the function body), `method_pattern` (first non-empty group = the HTTP method), `alias_pattern` (group 1 = the operation a wrapper such as `use<Name>` / `get<Name>QueryKey` belongs to). `dirs: []` = off | `dirs: []`; patterns = Orval's shapes (`export const <op> =`, `` `/path` `` / `'/path'`, `method: 'GET'` or `axios.get(`, `use|get<Op>[Suspense|Infinite][QueryKey|QueryOptions|MutationOptions|MutationKey|MutationFetcher|Url|Key]`) |

What a generator still assumes beyond the config: hooks are named `use<Name>`; components are PascalCase exports; the
page's purpose is the first sentence of the JSDoc above `export function <Page>`; `@docs <ID>` is one ID per `@docs`
line; a BroadcastChannel is opened in exactly one module per channel (`new BroadcastChannel(`), with the channel name
in a `*CHANNEL*` constant.

With a generated client (Orval) the hooks call generated functions instead of literal paths; set `generated_client.dirs`
to the generated folders and the `API calls` column lists those calls as `METHOD /path` (literal calls found by
`api_call_pattern` stay bare paths). `gen-codebase-map.py` reads every exported function of the generated files once:
the first literal path in its body (template or quoted string starting with `/`; host, leading `${baseURL}` and
`?query` dropped, `${param}` -> `{*}`) and its method (`method: 'GET'` or an `axios.get(`-style verb); a fetch-client
request function takes the path of the `get<Name>Url` helper it calls, and the helpers themselves take the method of
their operation. Wrapper names map back to the operation (`useListPets`, `getListPetsQueryKey`, `getListPetsQueryOptions`,
`getCreatePetsMutationOptions`, `getListPetsUrl`, `getListPetsKey`, Suspense/Infinite variants -> `listPets` /
`createPets`), so react-query and swr hooks resolve too. A hook contributes a call when it imports the name from a
generated folder (relative, `@/` or alias import, `import * as api` members included) and uses it; names the table
does not know are ignored, `*.msw.ts` mocks yield nothing (their paths start with `*`). The docs repository's
`gen-graph.py` folds a `METHOD /path` entry onto the backend endpoint with that method and path suffix, a bare path
onto every method as before.

Run the exporter from the repo root so `node_modules` resolves:

```
npx tsc -p scripts/docs/tsconfig.gen.json
node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json
```

What the exporter sees: one `feature:` node per page folder (and per `not_pages` folder), exported hooks (`use*`) and
components (PascalCase), `calls` edges from `api.GET('/session/product1/overview', ...)`-style calls (literal contract
path + method), `uses` / `renders` edges resolved through the type checker and `depends-on` edges between pages.
The exporter needs TypeScript 7 (the native compiler): the `typescript` package no longer exports the old
`ts.createProgram` API, so the script talks to the bundled compiler process through `typescript/unstable/sync` and
reads nodes through `typescript/unstable/ast` (both marked unstable by the TypeScript team; a later 7.x may rename
things, and then this script is the only file to touch). It opens every source file in that process, which picks the
project the way the language server does: the nearest `tsconfig.json` that includes the file (a Vite-style root config
that only lists `references` hands over to the referenced one), so `@/` aliases and barrel re-exports resolve; a file
no tsconfig includes lands in the inferred project (relative imports only). The console line names the config(s) used
and how many files each covered. `tsconfig.gen.json` compiles the script with `moduleResolution: bundler` (TypeScript 7
removed `node`/`node10`; the repository's own `tsconfig.json` must not carry `baseUrl` either, `paths` entries are
relative to it). An export made with the previous version (fixed compiler options, before 2026-10-21) had almost no
`renders` / `uses` edges: run it again.
The exporter keeps literal calls only: it does not read `generated_client` and emits no `calls` edge for a call to a
generated function; those come from the `API calls` column of `codebase-map.md` through the docs repository's graph.

IDE note: in the investigation workspace (`code-repo-kit/fe/...`) there is no `node_modules`, so the editor shows
`Cannot find module 'typescript/unstable/sync'` / implicit-any errors for `gen-graph-fe.ts`. They disappear in the real frontend repo
(or after `npm i` in a folder whose `node_modules` contains `typescript` and `@types/node`). The file compiles
cleanly under `strict: true`.

If `@types/node` is not in the frontend repo, add this shim next to the script instead of a new dependency:
`declare module 'fs'; declare module 'path';` in `node-shim.d.ts` and list it in `tsconfig.gen.json` `files`.
