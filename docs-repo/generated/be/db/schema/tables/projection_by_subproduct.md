---
type: Document
title: "projection_by_subproduct"
description: "Monthly projection table per sub-product of the session (cumulative values over the horizon)."
generated:
  by: process:db-docs
  at: 2026-10-16
status: stable
---
# projection_by_subproduct

Monthly projection table per sub-product of the session (cumulative values over the horizon).

Created in `harbor-core/src/main/resources/db/migration/V5__projection.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `period` | date | no |  |  |  |
| `sub_product` | varchar(16) | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `value` | numeric(18, 2) | no |  |  |  |
| `landed_cost` | numeric(18, 2) | no |  |  | Value plus transport and handling costs for the month. |
| `cumulative_value` | numeric(18, 2) | no |  |  | Running total of value from the first month of the horizon. |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- unique `uq_projection_by_subproduct`: `session_id, period, sub_product`
