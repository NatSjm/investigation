-- dataset: reference-clients
-- purpose: three synthetic clients with fixed ids - ACME-SYN (importer profile), BOREAL-SYN (exporter profile), CARROW-SYN (mixed) - the anchors every other dataset refers to
-- tables: client_profile
-- depends: -
-- synthetic: yes

INSERT INTO client_profile (id, external_ref, name, country, segment, created_at) VALUES
    ('aaaaaaaa-0000-4000-8000-000000000001', 'REG-1001', 'Acme Goods Ltd.',        'VLD', 'TRADER',      now()),
    ('aaaaaaaa-0000-4000-8000-000000000002', 'REG-1002', 'Boreal Exports plc',     'NRL', 'PRODUCER',    now()),
    ('aaaaaaaa-0000-4000-8000-000000000003', 'REG-1003', 'Carrow Logistics GmbH',  'VLD', 'DISTRIBUTOR', now())
ON CONFLICT (id) DO NOTHING;
