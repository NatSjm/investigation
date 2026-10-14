# scripts/docs (harbor-frontend)

| Script | Needs | Output |
|---|---|---|
| `gen-*.py`, `gen-all.py [--check]` | Python 3.11+ (standard library) | `docs/_generated/*.md` regex maps (`codebase-map`, `routes`, `types-index`, `docs-tags`, `index`) |
| `gen-graph-fe.ts` | the repo's existing `typescript` + `@types/node` devDependencies (no new library) | `docs/_generated/graph-export-fe.json` precise graph (TS compiler API) |

Run the exporter from the repo root so `node_modules` resolves:

```
npx tsc -p scripts/docs/tsconfig.gen.json
node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json
```

What the exporter sees: feature nodes from `src/features/<name>/`, exported hooks (`use*`) and components (PascalCase),
`calls` edges from `api.GET('/session/product1/overview', ...)`-style calls (literal contract path + method), `uses` /
`renders` edges resolved through the type checker (so barrel re-exports work) and `depends-on` edges between features.

IDE note: in the investigation workspace (`code-repo-kit/fe/...`) there is no `node_modules`, so the editor shows
`Cannot find module 'typescript'` / implicit-any errors for `gen-graph-fe.ts`. They disappear in the real frontend repo
(or after `npm i` in a folder whose `node_modules` contains `typescript` and `@types/node`). The file compiles
cleanly under `strict: true`.

If `@types/node` is not in the frontend repo, add this shim next to the script instead of a new dependency:
`declare module 'fs'; declare module 'path';` in `node-shim.d.ts` and list it in `tsconfig.gen.json` `files`.
