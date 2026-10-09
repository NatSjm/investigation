---
applyTo: "src/features/**"
description: "Feature folders: barrel with @module/@docs, <name>.types.ts, hooks in api/, components in ui/, no fetching in components."
---
# Feature folders (`src/features/<name>`)

- Public surface = `index.ts` only, opened by `/** @module <name> - one sentence. @docs <ID> */` (e.g. `@module stress`, `@docs STR-001`).
  If you need something not exported, export it from the barrel deliberately and say why.
- `<name>.types.ts` holds the feature's exported types; derive them from the generated contract
  (`import type { components } from '@/api/generated/schema'`) instead of retyping fields, and tag with `@docs <ID>`.
- Hooks in `api/use*.ts` wrap `api.GET/POST/PUT(...)` with the literal contract path and return typed data; components in `ui/`
  receive props and never fetch. `/session/**` calls get `X-Harbor-Session` from the client middleware - do not set headers in hooks.
- Add or alter a screen -> add the object route in `src/app/routes.tsx` (or `AdminRoutes.tsx`), `path:` before `element:`, then regenerate.
- Shared tables/modals (e.g. projection tables reused by `product1` and `product2`) live in `src/shared/`, not in a sibling feature.
- Tests: `*.test.tsx` beside the file; mocks under `__mocks__/` <= 100 lines, synthetic data only.
- After changes to the barrel, types, routes or tags: `pwsh scripts/docs/gen-all.ps1`, commit `docs/_generated/*`.
