-- Cover policies of a client and quotes requested from cover-provider during a session.

CREATE TABLE cover_policy (
    id uuid PRIMARY KEY,
    client_id uuid NOT NULL REFERENCES client_profile(id),
    product_group varchar(16) NOT NULL,
    sub_product varchar(16),
    covered_share numeric(7, 4) NOT NULL,
    premium_rate numeric(9, 6) NOT NULL,
    valid_from date NOT NULL,
    valid_to date,
    CONSTRAINT ck_cover_policy_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT ck_cover_policy_covered_share CHECK (covered_share BETWEEN 0 AND 1),
    CONSTRAINT ck_cover_policy_validity CHECK (valid_to IS NULL OR valid_to >= valid_from)
);

CREATE INDEX ix_cover_policy_client ON cover_policy (client_id, product_group);

CREATE TABLE cover_quote (
    id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    requested_at timestamp NOT NULL,
    uncovered_value numeric(18, 2) NOT NULL,
    premium numeric(18, 2) NOT NULL,
    provider_ref varchar(128)
);

CREATE INDEX ix_cover_quote_session ON cover_quote (session_id, requested_at DESC);
