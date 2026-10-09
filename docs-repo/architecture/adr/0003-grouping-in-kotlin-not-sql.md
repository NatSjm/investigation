---
type: Decision
title: "ADR-0003: Group projection results in Kotlin (utils), not in SQL"
description: The four cumulative projection tables are aggregated by ProjectionAggregator in the utils layer so that cover, stress test and reports reuse exactly the same grouping and rounding.
tags: [adr, calculations, projection]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# ADR-0003: Group projection results in Kotlin (utils), not in SQL

- **Status**: Accepted
- **Date**: 2026-10-09
- **Deciders**: harbor-platform-team
- **Related**: [monthly_projection](/domain/calculations/monthly_projection.md),
  [P1-001](/features/product1/P1-001.md), [STR-001](/features/stress/STR-001.md)

## Context
Per session the backend computes a monthly projection over a planning horizon (12-60 months) and presents it as
**four cumulative tables**: by sub-product, by dimension (city for Product 1, transport mode for Product 2), by
direction, and the summary. The same per-row figures (`value`, `landed_cost`, `cumulative_value`) are needed by
the cover ratio charts, the stress test (uncovered quantity per dimension value) and the meeting report. Rounding
is `HALF_EVEN`, scale 2, and must be applied at the same point everywhere, otherwise totals differ between pages.

## Decision
Grouping and cumulative sums are implemented once in `core/src/main/kotlin/harbor/utils/ProjectionAggregator.kt` (pure Kotlin, no
Spring, no SQL). `ProjectionService` (called by `Product1Manager` / `Product2Manager`) loads the input rows (actual
`movement_monthly` merged with modelled `session_movement_input`), calls the aggregator and persists the result via `ProjectionDao` into
`projection_by_subproduct`, `projection_by_dimension`, `projection_by_direction`, `projection_summary`. Cover,
stress and reports read those tables or call the aggregator on the same inputs; none of them writes its own
`GROUP BY`.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| SQL views / `GROUP BY` per context | fast, close to data | four contexts re-implement rounding and cumulative sums; drift between pages |
| Materialised view refreshed by trigger | one place | rounding in SQL differs from Kotlin `BigDecimal`; hard to unit-test worked examples |
| Kotlin aggregator in `utils` (chosen) | single implementation, unit-tested, worked examples in docs | rows loaded into memory (bounded: ≤ 60 months × ≤ 12 sub-products × ≤ 4 dimension values) |

## Consequences
+ One unit test (`ProjectionAggregatorTest`) is the executor for the attested computation; docs quote its cases.
+ Stress test and cover ratio are guaranteed to see the same `value` per row as the overview page.
− Any change in grouping keys requires a coordinated change of the four `projection_*` tables (Flyway) and the
  spec P1-001 / P2-001.
