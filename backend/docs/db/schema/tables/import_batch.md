# import_batch

One received movement file: its status and row counts.

Created in `harbor-core/src/main/resources/db/migration/V3__movements.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `source_file` | varchar(255) | no |  |  |  |
| `received_at` | timestamp | no |  |  |  |
| `rows_total` | integer | no | 0 |  |  |
| `rows_rejected` | integer | no | 0 |  | Rows the validator refused (unknown client, bad period, negative quantity). |
| `status` | varchar(16) | no |  |  |  |

## Relations

- referenced by [goods_movement](goods_movement.md).`batch_id`

## Constraints

- unique `uq_import_batch_source_file`: `source_file`
- check `ck_import_batch_status`: `(status IN ('RUNNING', 'DONE', 'FAILED'))`
