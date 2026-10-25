---
type: Document
title: "client_role"
description: "Role of a client per product group (IMPORTER, EXPORTER, MIXED, UNDETERMINED) as decided from its movements or overridden in a session."
generated:
  by: process:db-docs
  at: 2026-10-25
status: stable
---
# client_role

Role of a client per product group (IMPORTER, EXPORTER, MIXED, UNDETERMINED) as decided from its movements or overridden in a session.

Created in `harbor-core/src/main/resources/db/migration/V1__clients.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `client_id` | uuid | no |  | FK -> [client_profile](client_profile.md) |  |
| `product_group` | varchar(16) | no |  |  |  |
| `role` | varchar(16) | no |  |  |  |
| `source` | varchar(16) | no |  |  | How the role was decided: MOVEMENTS (computed) or SESSION (override by the representative). |
| `reason` | varchar(500) | yes |  |  | Free-text justification of a session override; empty for computed roles. |
| `decided_at` | timestamp | no | now() |  |  |

## Relations

- `client_id` references [client_profile](client_profile.md) (`id`)

## Constraints

- check `ck_client_role_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
- check `ck_client_role_role`: `(role IN ('IMPORTER', 'EXPORTER', 'MIXED', 'UNDETERMINED'))`
- check `ck_client_role_source`: `(source IN ('ALGORITHM', 'MANUAL'))`
