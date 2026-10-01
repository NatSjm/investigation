# scripts/docs (FE)

| Script | Needs | Output |
|---|---|---|
| `gen-*.ps1`, `gen-all.ps1 [-Check]` | PowerShell only | `docs/_generated/*.md` regex maps |
| `gen-graph-fe.ts` | the repo's existing `typescript` + `@types/node` devDependencies (no new library) | `docs/_generated/graph-export-fe.json` precise graph (TS compiler API) |

Run the exporter from the repo root so `node_modules` resolves:

```
npx tsc -p scripts/docs/tsconfig.gen.json
node scripts/docs/out/gen-graph-fe.js src docs/_generated/graph-export-fe.json
```

IDE note: in the investigation workspace (`code-repo-kit/fe/...`) there is no `node_modules`, so the editor shows
`Cannot find module 'typescript'` / implicit-any errors for `gen-graph-fe.ts`. They disappear in the real FE repo
(or after `npm i` in a folder whose `node_modules` contains `typescript` and `@types/node`). The file compiles
cleanly under `strict: true` - verified against `samples/fe-mini` (11 nodes, 9 edges).

If `@types/node` is not in the FE repo, add this shim next to the script instead of a new dependency:
`declare module 'fs'; declare module 'path';` in `node-shim.d.ts` and list it in `tsconfig.gen.json` `files`.
