---
type: Document
title: REST API index (BE)
generated:
  by: process:gen-docs
  at: 2026-10-01
status: stable
---
# REST API index (BE)

> Generated from `@RestController / @*Mapping scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
6 endpoint(s). DTO field lists: open the DTO file, not the controller.

| Method | Path | Handler | Params | Location |
|---|---|---|---|---|
| GET | `/api/v1/hedges/{clientId}/proposals` | `HedgeController.listProposals` | clientId: String | `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt:13` |
| POST | `/api/v1/hedges/{clientId}/proposals` | `HedgeController.createProposal` | clientId: String, req: CreateHedgeRequest | `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt:17` |
| DELETE | `/api/v1/hedges/{proposalId}` | `HedgeController.delete` | proposalId: String | `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt:25` |
| POST | `/api/v1/hedges/{proposalId}/stress-test` | `HedgeController.stressTest` | proposalId: String, scenario: StressScenarioDto | `hedges/src/main/kotlin/com/bank/adv/hedges/api/HedgeController.kt:21` |
| GET | `/api/v1/loans/{clientId}/schedule` | `LoanController.schedule` | clientId: String | `loans/src/main/kotlin/com/bank/adv/loans/LoanController.kt:10` |
| PUT | `/api/v1/loans/{loanId}` | `LoanController.update` | loanId: String, body: Any | `loans/src/main/kotlin/com/bank/adv/loans/LoanController.kt:13` |
