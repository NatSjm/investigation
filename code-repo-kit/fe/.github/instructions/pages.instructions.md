---
applyTo: "src/pages/**"
description: "Page folders: <Page>.tsx with a JSDoc @docs tag, hooks in hook/, components in components/<Name>/ with an index.ts, tests beside the file, no fetching in components."
---
# Page folders (`src/pages/<Page>`)

- One folder per routed page, named like its component: `src/pages/<Page>/<Page>.tsx` is the entry the generators read.
  Its JSDoc block starts with one sentence (route + what the page shows) and carries `@docs <ID>` (e.g. `@docs STR-001`);
  `codebase-map.md` takes the purpose from that sentence, `docs-tags.md` the ID.
- `hook/use*.ts` wrap `api.GET/POST/PUT(...)` with the literal contract path and return typed data, tagged `@docs <ID>`
  (the ID of the spec whose rule they serve; a modal's hook carries the modal's spec, e.g. `P1-002`). Components in
  `components/<Name>/<Name>.tsx` with an `index.ts` barrel receive props and never fetch. `/session/**` calls pass
  `params: { header: sessionHeader(), ... }` (from `@/services/api/client`) because the contract requires
  `X-Harbor-Session`; never build that header by hand and never set it on client-level (`/clients`, `/sessions`, `/admin`) calls.
- Types shared by pages live in `src/types/<context>.ts`, derived from the generated contract
  (`import type { components } from '@/services/openapi/schema'`) instead of retyping fields, tagged `@docs <ID>`.
  Page-local types go in `<Page>/types.ts` or `<name>.types.ts` (both indexed by `types-index.md`).
- Pieces used by several pages (tables, modals, hooks) live in `src/pages/shared/{components,hook}/`, never in a sibling
  page; generic UI (table, modal, charts) in `src/components/`.
- Add or alter a screen -> add the object route in `src/routing/Routing.tsx` (or `SessionRoutes.tsx`) as
  `{ path: ROUTES.X, Component: XPage }` with the path constant in `src/constants/routes.ts`, then regenerate.
- Cross-window sync (representative window <-> client screen `/present/:sessionId`) goes only through
  `src/components/broadcast/sessionChannel.ts` and the hooks in `src/components/hook/`: use `usePresentationPublisher`
  / `usePresentationSubscriber` and extend the `PresentationMessage` union there. Never create a second
  `BroadcastChannel` or call `postMessage` elsewhere.
- Tests: `*.test.tsx` beside the file (vitest); mocks under `__mocks__/` <= 100 lines, synthetic data only.
- After changes to pages, hooks, types, routes or tags: `python3 scripts/docs/gen-all.py`, commit `docs/_generated/*`.
