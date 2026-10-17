---
type: Document
title: "Scheduled jobs (BE)"
description: "Generated map: Scheduled jobs (BE), derived from @Scheduled scan + @SchedulerLock locks; read instead of source files."
generated:
  by: process:gen-docs
  at: 2026-10-17
status: stable
---
# Scheduled jobs (BE)

> Generated from `@Scheduled scan + @SchedulerLock locks` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
2 job(s). Cron expressions are Spring 6-field (seconds first). Lock = `@SchedulerLock` name (one instance at a time) and its lockAtMostFor.

| Job | Trigger | Lock | Summary | Location |
|---|---|---|---|---|
| `DailyMovementImportJob.run` | cron `0 0 2 * * *` | `dailyMovementImport` (at most PT2H) | Daily import of the XLS movement files delivered by file-exchange. Runs at 02:00 server time; the same | `harbor-core/src/main/kotlin/com/acme/harbor/job/DailyMovementImportJob.kt:21` |
| `MonthlySnapshotJob.run` | cron `0 0 3 1 * *` | `monthlySnapshot` (at most PT1H) | Rolls the previous calendar month of `goods_movement` up into `movement_monthly`. | `harbor-core/src/main/kotlin/com/acme/harbor/job/MonthlySnapshotJob.kt:23` |
