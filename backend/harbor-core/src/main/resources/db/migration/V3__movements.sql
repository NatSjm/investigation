-- Daily import batches, actual goods movements (one row per XLS line) and their monthly rollup.

CREATE TABLE import_batch (
    id uuid PRIMARY KEY,
    source_file varchar(255) NOT NULL,
    received_at timestamp NOT NULL,
    rows_total integer NOT NULL DEFAULT 0,
    rows_rejected integer NOT NULL DEFAULT 0,
    status varchar(16) NOT NULL,
    CONSTRAINT uq_import_batch_source_file UNIQUE (source_file),
    CONSTRAINT ck_import_batch_status CHECK (status IN ('RUNNING', 'DONE', 'FAILED'))
);

CREATE TABLE goods_movement (
    id bigserial PRIMARY KEY,
    client_id uuid NOT NULL REFERENCES client_profile(id),
    batch_id uuid NOT NULL REFERENCES import_batch(id),
    product_group varchar(16) NOT NULL,
    sub_product varchar(16) NOT NULL,
    city varchar(64),
    transport_mode varchar(8),
    direction varchar(3) NOT NULL,
    period date NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    unit_price numeric(18, 4) NOT NULL,
    price_basis varchar(3) NOT NULL,
    CONSTRAINT ck_goods_movement_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT ck_goods_movement_transport_mode CHECK (transport_mode IS NULL OR transport_mode IN ('ROAD', 'RAIL', 'SEA', 'AIR')),
    CONSTRAINT ck_goods_movement_direction CHECK (direction IN ('IN', 'OUT')),
    CONSTRAINT ck_goods_movement_period CHECK (extract(day FROM period) = 1),
    CONSTRAINT ck_goods_movement_quantity CHECK (quantity > 0),
    CONSTRAINT ck_goods_movement_price_basis CHECK (price_basis IN ('VLD', 'NRL', 'CST', 'MRD'))
);

CREATE INDEX ix_goods_movement_client_period ON goods_movement (client_id, product_group, period);
CREATE INDEX ix_goods_movement_batch ON goods_movement (batch_id);

CREATE TABLE movement_monthly (
    id bigserial PRIMARY KEY,
    client_id uuid NOT NULL REFERENCES client_profile(id),
    product_group varchar(16) NOT NULL,
    sub_product varchar(16) NOT NULL,
    city varchar(64),
    transport_mode varchar(8),
    direction varchar(3) NOT NULL,
    period date NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    value numeric(18, 2) NOT NULL,
    CONSTRAINT ck_movement_monthly_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT ck_movement_monthly_direction CHECK (direction IN ('IN', 'OUT'))
);

CREATE INDEX ix_movement_monthly_client_period ON movement_monthly (client_id, product_group, period);
CREATE INDEX ix_movement_monthly_period ON movement_monthly (period);
