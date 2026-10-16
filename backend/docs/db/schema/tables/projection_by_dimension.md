# projection_by_dimension

Monthly projection per dimension value: city for Product 1, transport mode for Product 2 (dimension_kind says which).

Created in `harbor-core/src/main/resources/db/migration/V5__projection.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `period` | date | no |  |  |  |
| `dimension_kind` | varchar(16) | no |  |  | CITY or TRANSPORT_MODE. |
| `dimension_value` | varchar(64) | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `value` | numeric(18, 2) | no |  |  |  |
| `landed_cost` | numeric(18, 2) | no |  |  |  |
| `cumulative_value` | numeric(18, 2) | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- unique `uq_projection_by_dimension`: `session_id, period, dimension_kind, dimension_value`
- check `ck_projection_by_dimension_kind`: `(dimension_kind IN ('CITY', 'TRANSPORT_MODE'))`
