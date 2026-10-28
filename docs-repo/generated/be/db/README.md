---
type: Document
title: "Database documentation: harbor"
description: "postgresql, schema `public`; 21 table(s). Generated from the migrations by `scripts/docs/gen-db-docs.py` on 2026-10-25; descriptions are the `COMMENT ON` statements. Machine-readable: [schema.json](schema.json). Diagram: [ER overview](schema/erd/overview.mmd)."
generated:
  by: process:db-docs
  at: 2026-10-28
status: stable
---
# Database documentation: harbor

postgresql, schema `public`; 21 table(s). Generated from the migrations by `scripts/docs/gen-db-docs.py` on 2026-10-25; descriptions are the `COMMENT ON` statements. Machine-readable: [schema.json](schema.json). Diagram: [ER overview](schema/erd/overview.mmd).

| Table | Description | Columns |
|---|---|---|
| [baseline_price](schema/tables/baseline_price.md) | Baseline price and transport price per product group, corridor and month, as loaded from market data. | 7 |
| [client_profile](schema/tables/client_profile.md) | A client of the platform: master data merged from the client registry, one row per external reference. | 6 |
| [client_role](schema/tables/client_role.md) | Role of a client per product group (IMPORTER, EXPORTER, MIXED, UNDETERMINED) as decided from its movements or overridden in a session. | 7 |
| [cover_policy](schema/tables/cover_policy.md) | Cover policies of a client per product group and sub-product: covered share, premium rate, validity. | 8 |
| [cover_quote](schema/tables/cover_quote.md) | Quote requested from the cover provider for the uncovered value of a session. | 6 |
| [goods_movement](schema/tables/goods_movement.md) | Daily movements as imported from the file exchange, one row per line of the file after validation. | 12 |
| [import_batch](schema/tables/import_batch.md) | One received movement file: its status and row counts. | 6 |
| [market_scenario](schema/tables/market_scenario.md) | Market scenario defined in a session: named shocks on prices and transport prices used by the stress test. | 7 |
| [meeting_report](schema/tables/meeting_report.md) | The meeting report of a closed session: payload sent for rendering, PDF path and rendering status. | 5 |
| [meeting_session](schema/tables/meeting_session.md) | A meeting with a client (CLIENT) or a preparation dry run (PREPARATION) for one product group; every session-scoped table hangs off it. | 12 |
| [movement_monthly](schema/tables/movement_monthly.md) | Monthly aggregate of goods_movement per client, sub-product, city, transport mode and direction; the input of every projection. | 10 |
| [parameter_set](schema/tables/parameter_set.md) | Admin parameters: one value per key and scope (product group, country, value), valid from a date. | 9 |
| [projection_by_dimension](schema/tables/projection_by_dimension.md) | Monthly projection per dimension value: city for Product 1, transport mode for Product 2 (dimension_kind says which). | 9 |
| [projection_by_direction](schema/tables/projection_by_direction.md) | Monthly projection per direction (IN, OUT). | 8 |
| [projection_by_subproduct](schema/tables/projection_by_subproduct.md) | Monthly projection table per sub-product of the session (cumulative values over the horizon). | 8 |
| [projection_summary](schema/tables/projection_summary.md) | Monthly totals of the session projection with the cover ratio. | 8 |
| [session_client_config](schema/tables/session_client_config.md) | Per-session choices of the client: projection horizon, price basis and cover preference. | 4 |
| [session_movement_input](schema/tables/session_movement_input.md) | Movements modelled by hand during a session (the movement modal); they replace the imported history for the months they cover. | 9 |
| [session_peer_simulation](schema/tables/session_peer_simulation.md) | Peer simulation requested in a session: the peer segment and the scaling factor applied to the projection of the client. | 5 |
| [shedlock](schema/tables/shedlock.md) | ShedLock table: distributed locks of the scheduled jobs (one row per job name). Technical. | 4 |
| [stress_test_result](schema/tables/stress_test_result.md) | Stress test output per session, scenario, month and dimension value: exposure and cumulative exposure. | 8 |
