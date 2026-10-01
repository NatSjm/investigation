---
type: Document
title: Codebase map (BE)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# Codebase map (BE)

> Generated from `pom.xml modules + annotation scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
Read the **facade** file of a module first; open `calc/`, `messaging/`, repositories only when the facade is not enough.

| Module | Purpose | Base package | Files | Entry points |
|---|---|---|---|---|
| `hedges` | Hedge proposals: monthly cash-flow computation, stress tests, proposal API | `com.bank.adv.hedges.api` | 4 | facades: `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeFacade.kt`<br>controllers: `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt`<br>listeners: `hedges/src/main/kotlin/com/bank/adv/hedges/messaging/HedgeEvents.kt` |
| `loans` | Loan proposals and repayment schedules | `com.bank.adv.loans` | 1 | controllers: `loans/src/main/kotlin/com/bank/adv/loans/LoanController.kt`<br>jobs: `loans/src/main/kotlin/com/bank/adv/loans/LoanController.kt` |
