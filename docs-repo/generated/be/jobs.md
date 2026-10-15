---
type: Document
title: "Scheduled jobs (BE)"
description: "Generated map: Scheduled jobs (BE), derived from @Scheduled scan; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-15
status: stable
---
# Scheduled jobs (BE)

> Generated from `@Scheduled scan` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
2 job(s). Cron expressions are Spring 6-field (seconds first).

| Job | Trigger | Summary | Location |
|---|---|---|---|
| `DailyMovementImportJob.run` | cron `0 0 2 * * *` | Daily import of the XLS movement files delivered by file-exchange. Runs at 02:00 server time; the same | `core/src/main/kotlin/harbor/job/DailyMovementImportJob.kt:19` |
| `MonthlySnapshotJob.run` | cron `0 0 3 1 * *` | Rolls the previous calendar month of `goods_movement` up into `movement_monthly`. | `core/src/main/kotlin/harbor/job/MonthlySnapshotJob.kt:21` |
