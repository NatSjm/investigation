---
type: Architecture View
title: Domain context map
description: Bounded contexts of the platform (Hedges, Loans, Stress test, Monthly computation, Graphs, Admin, Integration) and their dependencies.
tags: [domain, architecture]
status: stable
generated: { by: human:platform-team, at: 2026-09-30T19:00:00Z }
---

# Domain context map

- [Glossary](/domain/glossary.md) — canonical terminology.
- `calculations/` — one [Attested Computation](/.github/skills/okf/reference/SPEC.md) per financial calculation:
  formula + conventions + worked examples. Skill: `.github/skills/calculation-spec/SKILL.md`.

```mermaid
flowchart LR
  Loans --> Hedges
  Loans --> MonthlyCalc[Monthly computation]
  Hedges --> MonthlyCalc
  MonthlyCalc --> Stress[Stress test]
  MonthlyCalc --> Graphs
  Stress --> Graphs
  Admin -. limits, scenarios .-> Hedges
  Admin -. scenarios .-> Stress
  Integration[External services / Kafka] --> Loans
  Hedges --> Integration
```
