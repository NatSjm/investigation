---
type: Document
title: "projection_by_direction"
description: "Monthly projection per direction (IN, OUT)."
generated:
  by: process:db-docs
  at: 2026-10-17
status: stable
---
# projection_by_direction

Monthly projection per direction (IN, OUT).

Created in `harbor-core/src/main/resources/db/migration/V5__projection.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `period` | date | no |  |  |  |
| `direction` | varchar(3) | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `value` | numeric(18, 2) | no |  |  |  |
| `landed_cost` | numeric(18, 2) | no |  |  |  |
| `cumulative_value` | numeric(18, 2) | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- unique `uq_projection_by_direction`: `session_id, period, direction`
- check `ck_projection_by_direction_direction`: `(direction IN ('IN', 'OUT'))`
