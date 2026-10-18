---
type: Document
title: "projection_summary"
description: "Monthly totals of the session projection with the cover ratio."
generated:
  by: process:db-docs
  at: 2026-10-18
status: stable
---
# projection_summary

Monthly totals of the session projection with the cover ratio.

Created in `harbor-core/src/main/resources/db/migration/V5__projection.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `period` | date | no |  |  |  |
| `total_quantity` | numeric(18, 4) | no |  |  |  |
| `total_value` | numeric(18, 2) | no |  |  |  |
| `total_landed_cost` | numeric(18, 2) | no |  |  |  |
| `cover_ratio` | numeric(7, 4) | no | 0 |  | Covered value divided by total value for the month (0 to 1). |
| `cumulative_value` | numeric(18, 2) | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- unique `uq_projection_summary`: `session_id, period`
