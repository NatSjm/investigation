-- dataset: adm-parameter-versions
-- purpose: extra parameter_set versions on top of the Flyway seeds - a future tariff.rate for PRODUCT1/NRL that is listed but not yet in force, and a newer global peer.scaling_default - for scope and version resolution tests (ADM-001 BR-4, BR-6)
-- tables: parameter_set
-- depends: -
-- synthetic: yes

DELETE FROM parameter_set WHERE updated_by = 'fixture:adm-parameter-versions';

INSERT INTO parameter_set (id, key, scope_product_group, scope_country, scope_value, value, valid_from, updated_by) VALUES
    (gen_random_uuid(), 'tariff.rate',          'PRODUCT1', 'NRL', NULL, 0.06, DATE '2099-01-01', 'fixture:adm-parameter-versions'),
    (gen_random_uuid(), 'peer.scaling_default', NULL,       NULL,  NULL, 1.5,  DATE '2026-01-01', 'fixture:adm-parameter-versions');
