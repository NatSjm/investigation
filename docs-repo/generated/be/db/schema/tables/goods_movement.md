---
type: Document
title: "goods_movement"
description: "Daily movements as imported from the file exchange, one row per line of the file after validation."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# goods_movement

Daily movements as imported from the file exchange, one row per line of the file after validation.

Created in `harbor-core/src/main/resources/db/migration/V3__movements.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `client_id` | uuid | no |  | FK -> [client_profile](client_profile.md) |  |
| `batch_id` | uuid | no |  | FK -> [import_batch](import_batch.md) |  |
| `product_group` | varchar(16) | no |  |  |  |
| `sub_product` | varchar(16) | no |  |  |  |
| `city` | varchar(64) | yes |  |  |  |
| `transport_mode` | varchar(8) | yes |  |  | Transport mode of the movement (Product 2 dimension); null for Product 1. |
| `direction` | varchar(3) | no |  |  | IN (import) or OUT (export) from the point of view of the client. |
| `period` | date | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `unit_price` | numeric(18, 4) | no |  |  |  |
| `price_basis` | varchar(3) | no |  |  | Port the unit price refers to. |

## Relations

- `client_id` references [client_profile](client_profile.md) (`id`)
- `batch_id` references [import_batch](import_batch.md) (`id`)

## Constraints

- check `ck_goods_movement_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
- check `ck_goods_movement_transport_mode`: `(transport_mode IS NULL OR transport_mode IN ('ROAD', 'RAIL', 'SEA', 'AIR'))`
- check `ck_goods_movement_direction`: `(direction IN ('IN', 'OUT'))`
- check `ck_goods_movement_period`: `(extract(day FROM period) = 1)`
- check `ck_goods_movement_quantity`: `(quantity > 0)`
- check `ck_goods_movement_price_basis`: `(price_basis IN ('VLD', 'NRL', 'CST', 'MRD'))`
