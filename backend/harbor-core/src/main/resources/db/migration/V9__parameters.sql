-- Parameter sets maintained on the admin page, plus the report_requested_at marker on sessions.

CREATE TABLE parameter_set (
    id uuid PRIMARY KEY,
    key varchar(64) NOT NULL,
    scope_product_group varchar(16),
    scope_country varchar(3),
    scope_value varchar(64),
    value numeric(18, 6) NOT NULL,
    valid_from date NOT NULL,
    updated_by varchar(64) NOT NULL,
    updated_at timestamp NOT NULL DEFAULT now(),
    CONSTRAINT ck_parameter_set_product_group CHECK (scope_product_group IS NULL OR scope_product_group IN ('PRODUCT1', 'PRODUCT2'))
);

CREATE UNIQUE INDEX uq_parameter_set_scope ON parameter_set (
    key,
    coalesce(scope_product_group, ''),
    coalesce(scope_country, ''),
    coalesce(scope_value, ''),
    valid_from
);

ALTER TABLE meeting_session ADD COLUMN report_requested_at timestamp;

-- Default values (blueprint section 3.4). Scope columns: product group, country (price basis), scope value (city / transport mode).

INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'role.min_volume', NULL, NULL, NULL, 100, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'role.importer_threshold', NULL, NULL, NULL, 0.65, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'role.exporter_threshold', NULL, NULL, NULL, 0.35, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'cover.default_premium_rate', NULL, NULL, NULL, 0.012, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'projection.horizon_months_default', NULL, NULL, NULL, 24, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'stress.rounding_scale', NULL, NULL, NULL, 2, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'peer.scaling_default', NULL, NULL, NULL, 1.0, DATE '2020-01-01', 'flyway');

-- tariff.rate per product group and country of the corridor
INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'tariff.rate', 'PRODUCT1', 'VLD', NULL, 0.05, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'tariff.rate', 'PRODUCT1', 'NRL', NULL, 0.04, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'tariff.rate', 'PRODUCT2', 'CST', NULL, 0.03, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'tariff.rate', 'PRODUCT2', 'MRD', NULL, 0.035, DATE '2020-01-01', 'flyway');

-- handling.cost per city hub (applies to both product groups)
INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'handling.cost', NULL, NULL, 'Aldmoor', 0.80, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'handling.cost', NULL, NULL, 'Brightwater', 0.95, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'handling.cost', NULL, NULL, 'Carrow', 0.70, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'handling.cost', NULL, NULL, 'Dunmere', 1.10, DATE '2020-01-01', 'flyway');

-- transport.cost per transport mode
INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'transport.cost', NULL, NULL, 'ROAD', 1.20, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'transport.cost', NULL, NULL, 'RAIL', 0.90, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'transport.cost', NULL, NULL, 'SEA', 0.60, DATE '2020-01-01', 'flyway'),
    (gen_random_uuid(), 'transport.cost', NULL, NULL, 'AIR', 3.50, DATE '2020-01-01', 'flyway');
