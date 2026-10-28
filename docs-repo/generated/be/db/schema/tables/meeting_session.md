---
type: Document
title: "meeting_session"
description: "A meeting with a client (CLIENT) or a preparation dry run (PREPARATION) for one product group; every session-scoped table hangs off it."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# meeting_session

A meeting with a client (CLIENT) or a preparation dry run (PREPARATION) for one product group; every session-scoped table hangs off it.

Created in `harbor-core/src/main/resources/db/migration/V2__meetings.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `client_id` | uuid | no |  | FK -> [client_profile](client_profile.md) |  |
| `product_group` | varchar(16) | no |  |  |  |
| `kind` | varchar(16) | no |  |  | CLIENT: with the client present; PREPARATION: rehearsal by the representative, never reported. |
| `representative_id` | varchar(64) | no |  |  |  |
| `status` | varchar(16) | no |  |  | OPEN while inputs can change; CLOSED freezes the session and triggers the report. |
| `started_at` | timestamp | no |  |  |  |
| `closed_at` | timestamp | yes |  |  |  |
| `role_override` | varchar(16) | yes |  |  | Client role chosen in the session instead of the computed one; null = computed role applies. |
| `role_override_reason` | varchar(500) | yes |  |  |  |
| `parameter_snapshot` | jsonb | yes |  |  | Copy of the parameter values at session start (JSON); calculations in the session read this, never the live parameter_set. |
| `report_requested_at` | timestamp | yes |  |  | When the meeting report was requested from the document service; null until the session is closed. |

## Relations

- `client_id` references [client_profile](client_profile.md) (`id`)
- referenced by [session_client_config](session_client_config.md).`session_id`
- referenced by [session_movement_input](session_movement_input.md).`session_id`
- referenced by [session_peer_simulation](session_peer_simulation.md).`session_id`
- referenced by [projection_by_subproduct](projection_by_subproduct.md).`session_id`
- referenced by [projection_by_dimension](projection_by_dimension.md).`session_id`
- referenced by [projection_by_direction](projection_by_direction.md).`session_id`
- referenced by [projection_summary](projection_summary.md).`session_id`
- referenced by [cover_quote](cover_quote.md).`session_id`
- referenced by [market_scenario](market_scenario.md).`session_id`
- referenced by [stress_test_result](stress_test_result.md).`session_id`
- referenced by [meeting_report](meeting_report.md).`session_id`

## Constraints

- check `ck_meeting_session_product_group`: `(product_group IN ('PRODUCT1', 'PRODUCT2'))`
- check `ck_meeting_session_kind`: `(kind IN ('CLIENT', 'PREPARATION'))`
- check `ck_meeting_session_status`: `(status IN ('OPEN', 'CLOSED'))`
- check `ck_meeting_session_role_override`: `(role_override IS NULL OR role_override IN ('IMPORTER', 'EXPORTER', 'MIXED', 'UNDETERMINED'))`
