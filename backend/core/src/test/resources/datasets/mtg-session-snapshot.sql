-- dataset: mtg-session-snapshot
-- purpose: an open Product 1 session for BOREAL-SYN whose parameter snapshot holds tariff.rate.NRL = 0.04 while the live parameter_set already has a newer NRL version of 0.045 - the "parameter changed after the session started" situation (MTG-001 BR-2, ADM-001 BR-9)
-- tables: meeting_session, session_client_config, parameter_set
-- depends: reference-clients
-- synthetic: yes

DELETE FROM session_client_config WHERE session_id = '11111111-1111-4111-8111-222222222222';
DELETE FROM meeting_session WHERE id = '11111111-1111-4111-8111-222222222222';
DELETE FROM parameter_set WHERE updated_by = 'fixture:mtg-session-snapshot';

INSERT INTO meeting_session (id, client_id, product_group, kind, representative_id, status, started_at, parameter_snapshot) VALUES
    ('11111111-1111-4111-8111-222222222222', 'aaaaaaaa-0000-4000-8000-000000000002', 'PRODUCT1', 'CLIENT', 'rep-syn-2', 'OPEN', DATE '2026-09-01',
     '{"role.min_volume": 100, "role.importer_threshold": 0.65, "role.exporter_threshold": 0.35, "cover.default_premium_rate": 0.012, "peer.scaling_default": 1.0, "stress.rounding_scale": 2, "tariff.rate.NRL": 0.04}'::jsonb);

INSERT INTO session_client_config (session_id, horizon_months, price_basis, cover_preference) VALUES
    ('11111111-1111-4111-8111-222222222222', 24, 'NRL', 'PARTIAL');

INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'tariff.rate', 'PRODUCT1', 'NRL', NULL, 0.045, DATE '2026-09-15', 'fixture:mtg-session-snapshot');
