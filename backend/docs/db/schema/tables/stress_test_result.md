# stress_test_result

Stress test output per session, scenario, month and dimension value: exposure and cumulative exposure.

Created in `harbor-core/src/main/resources/db/migration/V7__market_stress.sql`. Diagram: [ER overview](../erd/overview.mmd).

## Columns

| Column | Type | Nullable | Default | Key | Comment |
|---|---|---|---|---|---|
| `id` | bigserial | no |  | PK |  |
| `session_id` | uuid | no |  | FK -> [meeting_session](meeting_session.md) |  |
| `scenario_id` | uuid | no |  | FK -> [market_scenario](market_scenario.md) |  |
| `period` | date | no |  |  |  |
| `dimension_value` | varchar(64) | no |  |  |  |
| `exposure` | numeric(18, 2) | no |  |  | Value at risk for the month under the scenario. |
| `transport_cost_delta` | numeric(18, 2) | no |  |  | Change of transport cost for the month caused by the scenario. |
| `cumulative_exposure` | numeric(18, 2) | no |  |  |  |

## Relations

- `session_id` references [meeting_session](meeting_session.md) (`id`)
- `scenario_id` references [market_scenario](market_scenario.md) (`id`)

## Constraints

- unique `uq_stress_test_result`: `session_id, scenario_id, period, dimension_value`
