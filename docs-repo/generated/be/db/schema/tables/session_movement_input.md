---
type: Document
title: "session_movement_input"
description: "Movements modelled by hand during a session (the movement modal); they replace the imported history for the months they cover."
generated:
  by: process:db-docs
  at: 2026-10-18
status: stable
---
# session_movement_input

Movements modelled by hand during a session (the movement modal); they replace the imported history for the months they cover.

Created in `harbor-core/src/main/resources/db/migration/V4__session_inputs.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `period` | date | no |  |  |  |
| `sub_product` | varchar(16) | no |  |  |  |
| `city` | varchar(64) | yes |  |  |  |
| `transport_mode` | varchar(8) | yes |  |  |  |
| `direction` | varchar(3) | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `unit_price` | numeric(18, 4) | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- check `ck_session_movement_input_transport_mode`: `(transport_mode IS NULL OR transport_mode IN ('ROAD', 'RAIL', 'SEA', 'AIR'))`
- check `ck_session_movement_input_direction`: `(direction IN ('IN', 'OUT'))`
- check `ck_session_movement_input_quantity`: `(quantity >= 0)`
