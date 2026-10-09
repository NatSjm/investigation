-- Meeting sessions (CLIENT meeting or PREPARATION dry run) and the per-session client configuration.

CREATE TABLE meeting_session (
    id uuid PRIMARY KEY,
    client_id uuid NOT NULL REFERENCES client_profile(id),
    product_group varchar(16) NOT NULL,
    kind varchar(16) NOT NULL,
    representative_id varchar(64) NOT NULL,
    status varchar(16) NOT NULL,
    started_at timestamp NOT NULL,
    closed_at timestamp,
    role_override varchar(16),
    role_override_reason varchar(500),
    parameter_snapshot jsonb,
    CONSTRAINT ck_meeting_session_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT ck_meeting_session_kind CHECK (kind IN ('CLIENT', 'PREPARATION')),
    CONSTRAINT ck_meeting_session_status CHECK (status IN ('OPEN', 'CLOSED')),
    CONSTRAINT ck_meeting_session_role_override CHECK (role_override IS NULL OR role_override IN ('IMPORTER', 'EXPORTER', 'MIXED', 'UNDETERMINED'))
);

CREATE INDEX ix_meeting_session_client ON meeting_session (client_id, product_group, status);
CREATE INDEX ix_meeting_session_started ON meeting_session (started_at DESC);

CREATE TABLE session_client_config (
    session_id uuid PRIMARY KEY REFERENCES meeting_session(id),
    horizon_months integer NOT NULL,
    price_basis varchar(3) NOT NULL,
    cover_preference varchar(16) NOT NULL DEFAULT 'NONE',
    CONSTRAINT ck_session_client_config_horizon CHECK (horizon_months BETWEEN 12 AND 60),
    CONSTRAINT ck_session_client_config_price_basis CHECK (price_basis IN ('VLD', 'NRL', 'CST', 'MRD')),
    CONSTRAINT ck_session_client_config_cover_preference CHECK (cover_preference IN ('NONE', 'PARTIAL', 'FULL'))
);
