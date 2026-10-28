---
type: Document
title: "cover_policy"
description: "Cover policies of a client per product group and sub-product: covered share, premium rate, validity."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# cover_policy

Cover policies of a client per product group and sub-product: covered share, premium rate, validity.

Created in `harbor-core/src/main/resources/db/migration/V6__cover.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `client_id` | uuid | no |  | FK -> [client_profile](client_profile.md) |  |
| `product_group` | varchar(16) | no |  |  |  |
| `sub_product` | varchar(16) | yes |  |  |  |
| `covered_share` | numeric(7, 4) | no |  |  | Share of the value covered by the policy (0 to 1). |
| `premium_rate` | numeric(9, 6) | no |  |  | Premium as a rate of the covered value. |
| `valid_from` | date | no |  |  |  |
| `valid_to` | date | yes |  |  |  |

## Relations

- `client_id` references [client_profile](client_profile.md) (`id`)

## Constraints

- check `ck_cover_policy_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
- check `ck_cover_policy_covered_share`: `(covered_share BETWEEN 0 AND 1)`
- check `ck_cover_policy_validity`: `(valid_to IS NULL OR valid_to >= valid_from)`
