---
type: Document
title: Spec-to-code traceability (@docs tags)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# Spec-to-code traceability (@docs tags)

> Generated from `@docs <ID> tags in KDoc/JSDoc` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
5 tag(s). Resolve a spec/calculation ID here, then open only the listed location.

| Spec ID | Declaration | Summary | Location |
|---|---|---|---|
| `hedge_monthly_cashflow` | `class HedgeCashflowCalculator(private val rates: RateProvider)` | Monthly hedge cash-flow calculator. | `hedges/src/main/kotlin/com/bank/adv/hedges/calc/HedgeCashflowCalculator.kt:10` |
| `hedge_monthly_cashflow` | `fun monthlyCashflow(notional: BigDecimal, fixedRate: BigDecimal, month: YearMonth): BigDecimal` | Net monthly cash flow = notional * (fixedRate - floatingRate(month)) * dayCountFraction(month). | `hedges/src/main/kotlin/com/bank/adv/hedges/calc/HedgeCashflowCalculator.kt:17` |
| `hedge_stress_test` | `fun stress(notional: BigDecimal, fixedRate: BigDecimal, months: List<YearMonth>, shiftBp: Int): List<BigDecimal>` | Stress test: re-prices every month under a shifted curve (parallel shift in bp). | `hedges/src/main/kotlin/com/bank/adv/hedges/calc/HedgeCashflowCalculator.kt:26` |
| `HEDGE-001` | `class HedgeController(private val facade: HedgeFacade)` | Hedge proposal endpoints used by the meeting screen. | `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt:11` |
| `LOAN-RATES-JOB` | `fun refresh()` | Nightly refresh of reference rates. | `loans/src/main/kotlin/com/bank/adv/loans/LoanController.kt:21` |
