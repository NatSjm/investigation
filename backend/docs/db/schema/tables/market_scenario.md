# market_scenario

Market scenario defined in a session: named shocks on prices and transport prices used by the stress test.

Created in `harbor-core/src/main/resources/db/migration/V7__market_stress.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | uuid | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `name` | varchar(120) | no |  |  |  |
| `kind` | varchar(16) | no |  |  | PRESET (from the catalogue) or CUSTOM (edited in the session). |
| `shocks` | jsonb | no | '[]' |  | JSON list of shocks: target (price, transport), period range, relative change. |
| `created_by` | varchar(64) | no |  |  |  |
| `created_at` | timestamp | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)
- referenced by [stress_test_result](stress_test_result.md).`scenario_id`

## Constraints

- check `ck_market_scenario_kind`: `(kind IN ('REPRESENTATIVE', 'CLIENT'))`
