---
type: Document
title: "shedlock"
description: "ShedLock table: distributed locks of the scheduled jobs (one row per job name). Technical."
generated:
  by: process:db-docs
  at: 2026-10-16
status: stable
---
# shedlock

ShedLock table: distributed locks of the scheduled jobs (one row per job name). Technical.

Created in `harbor-core/src/main/resources/db/migration/V10__shedlock.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `name` | varchar(64) | no |  | PK |  |
| `lock_until` | timestamp | no |  |  |  |
| `locked_at` | timestamp | no |  |  |  |
| `locked_by` | varchar(255) | no |  |  |  |

## Relations

_none_
