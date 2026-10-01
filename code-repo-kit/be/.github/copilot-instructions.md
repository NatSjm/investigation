# Copilot instructions - advisory backend (Kotlin / Spring / Maven / PostgreSQL / Kafka)

## Read in this order (cheapest first)
1. `docs/_generated/index.md` -> the map you need (`codebase-map`, `api-index`, `events`, `db-schema`, `docs-tags`).
   For "what depends on / what breaks if" questions: docs repo `generated/graph/<module>.md` or VS Code `#impact <node|file>` instead of the maps.
2. The module **facade** (`*Facade.kt` / `*UseCase.kt`) named in `codebase-map.md`.
3. Only then: the specific file + line range named in a map. Never walk directories.
4. Business rules / formulas: the docs repo (`advisory-docs`, `features/`, `domain/calculations/`) - cite the spec ID, do not re-derive from code.

Resolve a spec ID (`HEDGE-001`, `hedge_monthly_cashflow`) via `docs/_generated/docs-tags.md`, not by searching.

## Never open
`target/`, `build/`, generated sources, `*.iml`, lockfiles, `src/test/resources/**/*.json` fixtures > 100 lines,
Flyway migrations older than the current year unless the task is a DDL change.

## Conventions you must follow
- Module layout: `api/` (controller + facade + DTOs), `domain/`, `calc/`, `messaging/`, `persistence/`.
- Facades carry a KDoc paragraph describing responsibilities - keep it current when you change behaviour.
- Tag spec-relevant declarations with `@docs <ID>` in KDoc; CI regenerates `docs-tags.md` from it.
- Files <= 400 lines (`check-file-size.ps1` gate). Split before adding.
- Money: `BigDecimal`, `RoundingMode.HALF_EVEN`, scale from the spec. Dates: `YearMonth` for monthly series.
- Kafka topics are constants in `messaging/Topics` - never string literals.
- No client PII in tests, fixtures, logs or docs; synthetic data only.

## Output discipline
- Return diffs / edited files, not whole-file dumps in chat.
- When asked "how does X work", answer from the map + facade (<= 15 lines) and link `file:line`; expand only on request.
- After changing an endpoint, topic, table or `@docs`-tagged function run `scripts/docs/gen-all.ps1` and include the regenerated `docs/_generated/*` in the change.

## Context hygiene for humans
Prefer `#file`, `#sym`, `#selection` over `@workspace`; keep IntelliJ "Unload Modules" to the modules you touch;
VS Code: open `workspaces/<context>.code-workspace`, not the repo root.
