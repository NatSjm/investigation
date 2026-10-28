---
type: Document
title: "cover_quote"
description: "Quote requested from the cover provider for the uncovered value of a session."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# cover_quote

Quote requested from the cover provider for the uncovered value of a session.

Created in `harbor-core/src/main/resources/db/migration/V6__cover.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `requested_at` | timestamp | no |  |  |  |
| `uncovered_value` | numeric(18, 2) | no |  |  |  |
| `premium` | numeric(18, 2) | no |  |  |  |
| `provider_ref` | varchar(128) | yes |  |  | Reference of the quote at the cover provider; null while the request is pending. |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)
