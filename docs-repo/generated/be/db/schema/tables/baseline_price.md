---
type: Document
title: "baseline_price"
description: "Baseline price and transport price per product group, corridor and month, as loaded from market data."
generated:
  by: process:db-docs
  at: 2026-10-25
status: stable
---
# baseline_price

Baseline price and transport price per product group, corridor and month, as loaded from market data.

Created in `harbor-core/src/main/resources/db/migration/V7__market_stress.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `product_group` | varchar(16) | no |  |  |  |
| `corridor` | varchar(8) | no |  |  | Origin-destination corridor code (for example VLD-NRL). |
| `period` | date | no |  |  |  |
| `price` | numeric(18, 4) | no |  |  |  |
| `transport_price` | numeric(18, 4) | no |  |  |  |
| `as_of` | timestamp | no |  |  | Timestamp of the market data snapshot the row comes from. |

## Relations

_none_

## Constraints

- unique `uq_baseline_price`: `product_group, corridor, period`
- check `ck_baseline_price_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
