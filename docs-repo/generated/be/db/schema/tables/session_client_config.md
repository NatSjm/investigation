---
type: Document
title: "session_client_config"
description: "Per-session choices of the client: projection horizon, price basis and cover preference."
generated:
  by: process:db-docs
  at: 2026-10-21
status: stable
---
# session_client_config

Per-session choices of the client: projection horizon, price basis and cover preference.

Created in `harbor-core/src/main/resources/db/migration/V2__meetings.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `session_id` | uuid | no |  | PK, FK -> [meeting_session](meeting_session.md) |  |
| `horizon_months` | integer | no |  |  | Projection horizon in months (12 to 60). |
| `price_basis` | varchar(3) | no |  |  | Port whose prices are the basis of the projection (VLD, NRL, CST, MRD). |
| `cover_preference` | varchar(16) | no | 'NONE' |  | NONE, PARTIAL or FULL cover wished by the client; drives the cover quote. |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- check `ck_session_client_config_horizon`: `(horizon_months BETWEEN 12 AND 60)`
- check `ck_session_client_config_price_basis`: `(price_basis IN ('VLD', 'NRL', 'CST', 'MRD'))`
- check `ck_session_client_config_cover_preference`: `(cover_preference IN ('NONE', 'PARTIAL', 'FULL'))`
