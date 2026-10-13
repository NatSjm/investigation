-- dataset: p1-baseline-12m
-- purpose: ACME-SYN with the last 12 full months of Product 1 actual movements - P1-STD inbound via Aldmoor by road (100 units a month) and P1-PRM outbound via Brightwater by rail (40 units a month) - enough for the overview, the role classification and a projection
-- tables: movement_monthly
-- depends: reference-clients
-- synthetic: yes

DELETE FROM movement_monthly
 WHERE client_id = 'aaaaaaaa-0000-4000-8000-000000000001'
   AND product_group = 'PRODUCT1'
   AND period BETWEEN DATE '2025-10-01' AND DATE '2026-09-01';

INSERT INTO movement_monthly (client_id, product_group, sub_product, city, transport_mode, direction, period, quantity, value) VALUES
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2025-10-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2025-11-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2025-12-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-01-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-02-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-03-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-04-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-05-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-06-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-07-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-08-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-STD', 'Aldmoor', 'ROAD', 'IN', DATE '2026-09-01', 100, 1250.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2025-10-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2025-11-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2025-12-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-01-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-02-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-03-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-04-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-05-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-06-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-07-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-08-01', 40, 720.00),
    ('aaaaaaaa-0000-4000-8000-000000000001', 'PRODUCT1', 'P1-PRM', 'Brightwater', 'RAIL', 'OUT', DATE '2026-09-01', 40, 720.00);
