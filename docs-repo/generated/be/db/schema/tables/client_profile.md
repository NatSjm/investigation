---
type: Document
title: "client_profile"
description: "A client of the platform: master data merged from the client registry, one row per external reference."
generated:
  by: process:db-docs
  at: 2026-10-17
status: stable
---
# client_profile

A client of the platform: master data merged from the client registry, one row per external reference.

Created in `harbor-core/src/main/resources/db/migration/V1__clients.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `external_ref` | varchar(64) | no |  |  | Identifier of the client in the client registry (CR-nnnn). |
| `name` | varchar(200) | no |  |  |  |
| `country` | varchar(3) | yes |  |  | Three-letter country code of the client seat. |
| `segment` | varchar(64) | yes |  |  | Commercial segment used for peer simulation (SMALL, MID, LARGE). |
| `created_at` | timestamp | no | now() |  |  |

## Relations

- referenced by [client_role](client_role.md).`client_id`
- referenced by [meeting_session](meeting_session.md).`client_id`
- referenced by [goods_movement](goods_movement.md).`client_id`
- referenced by [movement_monthly](movement_monthly.md).`client_id`
- referenced by [cover_policy](cover_policy.md).`client_id`

## Constraints

- unique `uq_client_profile_external_ref`: `external_ref`
