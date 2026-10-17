---
type: Document
title: "meeting_report"
description: "The meeting report of a closed session: payload sent for rendering, PDF path and rendering status."
generated:
  by: process:db-docs
  at: 2026-10-17
status: stable
---
# meeting_report

The meeting report of a closed session: payload sent for rendering, PDF path and rendering status.

Created in `harbor-core/src/main/resources/db/migration/V8__reports.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `session_id` | uuid | no |  | PK, FK -> [meeting_session](meeting_session.md) |  |
| `payload` | jsonb | no |  |  |  |
| `pdf_path` | varchar(512) | yes |  |  |  |
| `status` | varchar(16) | no | 'PENDING' |  | REQUESTED, RENDERED or FAILED. |
| `rendered_at` | timestamp | yes |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)

## Constraints

- check `ck_meeting_report_status`: `(status IN ('PENDING', 'REQUESTED', 'RENDERED', 'FAILED'))`
