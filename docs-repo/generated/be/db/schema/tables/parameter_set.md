---
type: Document
title: "parameter_set"
description: "Admin parameters: one value per key and scope (product group, country, value), valid from a date."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# parameter_set

Admin parameters: one value per key and scope (product group, country, value), valid from a date.

Created in `harbor-core/src/main/resources/db/migration/V9__parameters.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `key` | varchar(64) | no |  |  | Parameter key (ParameterKey enum in the backend). |
| `scope_product_group` | varchar(16) | yes |  |  |  |
| `scope_country` | varchar(3) | yes |  |  |  |
| `scope_value` | varchar(64) | yes |  |  | Free scope qualifier (city, sub-product) when the key is scoped that way. |
| `value` | numeric(18, 6) | no |  |  |  |
| `valid_from` | date | no |  |  |  |
| `updated_by` | varchar(64) | no |  |  |  |
| `updated_at` | timestamp | no | now() |  |  |

## Relations

_none_

## Constraints

- check `ck_parameter_set_product_group`: `(scope_product_group IS NULL OR scope_product_group IN ('PRODUCT1', 'PRODUCT2'))`
