-- dataset: sessions-open
-- purpose: one open Product 1 client session for ACME-SYN with a 24-month horizon, price basis VLD and a parameter snapshot taken from the seeded defaults - the session every session-scoped endpoint can be called with
-- tables: meeting_session, session_client_config
-- depends: reference-clients, p1-baseline-12m
-- synthetic: yes

DELETE FROM session_client_config WHERE session_id = '11111111-1111-4111-8111-111111111111';
DELETE FROM meeting_session WHERE id = '11111111-1111-4111-8111-111111111111';

INSERT INTO meeting_session (id, client_id, product_group, kind, representative_id, status, started_at, parameter_snapshot) VALUES
    ('11111111-1111-4111-8111-111111111111', 'aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'CLIENT', 'rep-syn-1', 'OPEN', now(),
     '{"role.min_volume": 100, "role.importer_threshold": 0.65, "role.exporter_threshold": 0.35, "cover.default_premium_rate": 0.012, "peer.scaling_default": 1.0, "stress.rounding_scale": 2, "tariff.rate.VLD": 0.05}'::jsonb);

INSERT INTO session_client_config (session_id, horizon_months, price_basis, cover_preference) VALUES
    ('11111111-1111-4111-8111-111111111111', 24, 'VLD', 'NONE');
