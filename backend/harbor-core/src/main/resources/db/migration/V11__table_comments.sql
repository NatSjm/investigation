-- Table and column comments: the human-written data dictionary. The database documentation (docs/db, schema.json,
-- one page per table, ER diagram) is generated from these comments; keep them with the DDL they describe.

COMMENT ON TABLE client_profile IS 'A client of the platform: master data merged from the client registry, one row per external reference.';
COMMENT ON COLUMN client_profile.external_ref IS 'Identifier of the client in the client registry (CR-nnnn).';
COMMENT ON COLUMN client_profile.country IS 'Three-letter country code of the client seat.';
COMMENT ON COLUMN client_profile.segment IS 'Commercial segment used for peer simulation (SMALL, MID, LARGE).';

COMMENT ON TABLE client_role IS 'Role of a client per product group (IMPORTER, EXPORTER, MIXED, UNDETERMINED) as decided from its movements or overridden in a session.';
COMMENT ON COLUMN client_role.source IS 'How the role was decided: MOVEMENTS (computed) or SESSION (override by the representative).';
COMMENT ON COLUMN client_role.reason IS 'Free-text justification of a session override; empty for computed roles.';

COMMENT ON TABLE meeting_session IS 'A meeting with a client (CLIENT) or a preparation dry run (PREPARATION) for one product group; every session-scoped table hangs off it.';
COMMENT ON COLUMN meeting_session.kind IS 'CLIENT: with the client present; PREPARATION: rehearsal by the representative, never reported.';
COMMENT ON COLUMN meeting_session.status IS 'OPEN while inputs can change; CLOSED freezes the session and triggers the report.';
COMMENT ON COLUMN meeting_session.role_override IS 'Client role chosen in the session instead of the computed one; null = computed role applies.';
COMMENT ON COLUMN meeting_session.parameter_snapshot IS 'Copy of the parameter values at session start (JSON); calculations in the session read this, never the live parameter_set.';
COMMENT ON COLUMN meeting_session.report_requested_at IS 'When the meeting report was requested from the document service; null until the session is closed.';

COMMENT ON TABLE session_client_config IS 'Per-session choices of the client: projection horizon, price basis and cover preference.';
COMMENT ON COLUMN session_client_config.horizon_months IS 'Projection horizon in months (12 to 60).';
COMMENT ON COLUMN session_client_config.price_basis IS 'Port whose prices are the basis of the projection (VLD, NRL, CST, MRD).';
COMMENT ON COLUMN session_client_config.cover_preference IS 'NONE, PARTIAL or FULL cover wished by the client; drives the cover quote.';

COMMENT ON TABLE import_batch IS 'One received movement file: its status and row counts.';
COMMENT ON COLUMN import_batch.rows_rejected IS 'Rows the validator refused (unknown client, bad period, negative quantity).';

COMMENT ON TABLE goods_movement IS 'Daily movements as imported from the file exchange, one row per line of the file after validation.';
COMMENT ON COLUMN goods_movement.direction IS 'IN (import) or OUT (export) from the point of view of the client.';
COMMENT ON COLUMN goods_movement.transport_mode IS 'Transport mode of the movement (Product 2 dimension); null for Product 1.';
COMMENT ON COLUMN goods_movement.price_basis IS 'Port the unit price refers to.';

COMMENT ON TABLE movement_monthly IS 'Monthly aggregate of goods_movement per client, sub-product, city, transport mode and direction; the input of every projection.';
COMMENT ON COLUMN movement_monthly.value IS 'Quantity times unit price, summed over the month.';

COMMENT ON TABLE session_movement_input IS 'Movements modelled by hand during a session (the movement modal); they replace the imported history for the months they cover.';

COMMENT ON TABLE session_peer_simulation IS 'Peer simulation requested in a session: the peer segment and the scaling factor applied to the projection of the client.';
COMMENT ON COLUMN session_peer_simulation.scaling_factor IS 'Factor applied to the quantities of the client to simulate a peer of the chosen segment.';

COMMENT ON TABLE projection_by_subproduct IS 'Monthly projection table per sub-product of the session (cumulative values over the horizon).';
COMMENT ON COLUMN projection_by_subproduct.landed_cost IS 'Value plus transport and handling costs for the month.';
COMMENT ON COLUMN projection_by_subproduct.cumulative_value IS 'Running total of value from the first month of the horizon.';

COMMENT ON TABLE projection_by_dimension IS 'Monthly projection per dimension value: city for Product 1, transport mode for Product 2 (dimension_kind says which).';
COMMENT ON COLUMN projection_by_dimension.dimension_kind IS 'CITY or TRANSPORT_MODE.';

COMMENT ON TABLE projection_by_direction IS 'Monthly projection per direction (IN, OUT).';

COMMENT ON TABLE projection_summary IS 'Monthly totals of the session projection with the cover ratio.';
COMMENT ON COLUMN projection_summary.cover_ratio IS 'Covered value divided by total value for the month (0 to 1).';

COMMENT ON TABLE cover_policy IS 'Cover policies of a client per product group and sub-product: covered share, premium rate, validity.';
COMMENT ON COLUMN cover_policy.covered_share IS 'Share of the value covered by the policy (0 to 1).';
COMMENT ON COLUMN cover_policy.premium_rate IS 'Premium as a rate of the covered value.';

COMMENT ON TABLE cover_quote IS 'Quote requested from the cover provider for the uncovered value of a session.';
COMMENT ON COLUMN cover_quote.provider_ref IS 'Reference of the quote at the cover provider; null while the request is pending.';

COMMENT ON TABLE market_scenario IS 'Market scenario defined in a session: named shocks on prices and transport prices used by the stress test.';
COMMENT ON COLUMN market_scenario.kind IS 'PRESET (from the catalogue) or CUSTOM (edited in the session).';
COMMENT ON COLUMN market_scenario.shocks IS 'JSON list of shocks: target (price, transport), period range, relative change.';

COMMENT ON TABLE baseline_price IS 'Baseline price and transport price per product group, corridor and month, as loaded from market data.';
COMMENT ON COLUMN baseline_price.corridor IS 'Origin-destination corridor code (for example VLD-NRL).';
COMMENT ON COLUMN baseline_price.as_of IS 'Timestamp of the market data snapshot the row comes from.';

COMMENT ON TABLE stress_test_result IS 'Stress test output per session, scenario, month and dimension value: exposure and cumulative exposure.';
COMMENT ON COLUMN stress_test_result.exposure IS 'Value at risk for the month under the scenario.';
COMMENT ON COLUMN stress_test_result.transport_cost_delta IS 'Change of transport cost for the month caused by the scenario.';

COMMENT ON TABLE meeting_report IS 'The meeting report of a closed session: payload sent for rendering, PDF path and rendering status.';
COMMENT ON COLUMN meeting_report.status IS 'REQUESTED, RENDERED or FAILED.';

COMMENT ON TABLE parameter_set IS 'Admin parameters: one value per key and scope (product group, country, value), valid from a date.';
COMMENT ON COLUMN parameter_set.key IS 'Parameter key (ParameterKey enum in the backend).';
COMMENT ON COLUMN parameter_set.scope_value IS 'Free scope qualifier (city, sub-product) when the key is scoped that way.';

COMMENT ON TABLE shedlock IS 'ShedLock table: distributed locks of the scheduled jobs (one row per job name). Technical.';
