-- Client profile (master data mirrored from client-registry) and the role decision history.

CREATE TABLE client_profile (
    id uuid PRIMARY KEY,
    external_ref varchar(64) NOT NULL,
    name varchar(200) NOT NULL,
    country varchar(3),
    segment varchar(64),
    created_at timestamp NOT NULL DEFAULT now(),
    CONSTRAINT uq_client_profile_external_ref UNIQUE (external_ref)
);

CREATE TABLE client_role (
    id bigserial PRIMARY KEY,
    client_id uuid NOT NULL REFERENCES client_profile(id),
    product_group varchar(16) NOT NULL,
    role varchar(16) NOT NULL,
    source varchar(16) NOT NULL,
    reason varchar(500),
    decided_at timestamp NOT NULL DEFAULT now(),
    CONSTRAINT ck_client_role_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT ck_client_role_role CHECK (role IN ('IMPORTER', 'EXPORTER', 'MIXED', 'UNDETERMINED')),
    CONSTRAINT ck_client_role_source CHECK (source IN ('ALGORITHM', 'MANUAL'))
);

CREATE INDEX ix_client_role_client ON client_role (client_id, product_group, decided_at DESC);
