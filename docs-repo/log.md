# Update Log

## 2026-09-30
* **Creation**: Bundle initialised as OKF v0.2 (prototype). Concepts: [HEDGE-001](/features/hedges/HEDGE-001.md),
  [hedge_monthly_cashflow](/domain/calculations/hedge_monthly_cashflow.md), [Glossary](/domain/glossary.md),
  [ADR-0001](/architecture/adr/0001-docs-as-code.md), [Integrations map](/architecture/integrations.md),
  [Codebase map](/generated/codebase-map.md).
* **Verification**: [HEDGE-001](/features/hedges/HEDGE-001.md) and
  [hedge_monthly_cashflow](/domain/calculations/hedge_monthly_cashflow.md) example-verified by `human:example-reviewer`.
* **Tooling**: `scripts/okf-validate.ps1` and `scripts/build-index.ps1` added; Copilot instructions, agents and CI
  updated to OKF rules (index-first reading, `copilot/<agent>` provenance, `-Strict` gate). Bundle validates with
  0 errors / 0 warnings; 8 `index.md` files generated.
