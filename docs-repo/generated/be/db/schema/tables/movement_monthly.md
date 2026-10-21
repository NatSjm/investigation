---
type: Document
title: "movement_monthly"
description: "Monthly aggregate of goods_movement per client, sub-product, city, transport mode and direction; the input of every projection."
generated:
  by: process:db-docs
  at: 2026-10-21
status: stable
---
# movement_monthly

Monthly aggregate of goods_movement per client, sub-product, city, transport mode and direction; the input of every projection.

Created in `harbor-core/src/main/resources/db/migration/V3__movements.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `client_id` | uuid | no |  | FK -> [client_profile](client_profile.md) |  |
| `product_group` | varchar(16) | no |  |  |  |
| `sub_product` | varchar(16) | no |  |  |  |
| `city` | varchar(64) | yes |  |  |  |
| `transport_mode` | varchar(8) | yes |  |  |  |
| `direction` | varchar(3) | no |  |  |  |
| `period` | date | no |  |  |  |
| `quantity` | numeric(18, 4) | no |  |  |  |
| `value` | numeric(18, 2) | no |  |  | Quantity times unit price, summed over the month. |

## Relations

- `client_id` references [client_profile](client_profile.md) (`id`)

## Constraints

- check `ck_movement_monthly_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
- check `ck_movement_monthly_direction`: `(direction IN ('IN', 'OUT'))`
