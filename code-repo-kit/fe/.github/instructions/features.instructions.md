---
applyTo: "src/features/**"
---
# Feature folders

- Public surface = `index.ts` only. If you need something not exported, export it from the barrel deliberately (and say why).
- Add/alter a screen -> update `routes.md` by editing routes in `src/app/routes.tsx`, then regenerate.
- Types in `<name>.types.ts` mirror BE DTOs; when the BE `api-index.md` shows a new field, add it there first.
- Hooks in `api/` return typed data; components receive props - do not fetch in components.
- Tests: `*.test.tsx` beside the file; mocks under `__mocks__/` <= 100 lines.
