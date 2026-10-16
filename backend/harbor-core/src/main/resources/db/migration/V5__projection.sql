-- The four cumulative projection tables of a session (output of calculation monthly_projection).
-- Rows are replaced as a whole on every recompute (product1.ProjectionRepository).

CREATE TABLE projection_by_subproduct (
    id bigserial PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    period date NOT NULL,
    sub_product varchar(16) NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    value numeric(18, 2) NOT NULL,
    landed_cost numeric(18, 2) NOT NULL,
    cumulative_value numeric(18, 2) NOT NULL,
    CONSTRAINT uq_projection_by_subproduct UNIQUE (session_id, period, sub_product)
);

CREATE TABLE projection_by_dimension (
    id bigserial PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    period date NOT NULL,
    dimension_kind varchar(16) NOT NULL,
    dimension_value varchar(64) NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    value numeric(18, 2) NOT NULL,
    landed_cost numeric(18, 2) NOT NULL,
    cumulative_value numeric(18, 2) NOT NULL,
    CONSTRAINT ck_projection_by_dimension_kind CHECK (dimension_kind IN ('CITY', 'TRANSPORT_MODE')),
    CONSTRAINT uq_projection_by_dimension UNIQUE (session_id, period, dimension_kind, dimension_value)
);

CREATE TABLE projection_by_direction (
    id bigserial PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    period date NOT NULL,
    direction varchar(3) NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    value numeric(18, 2) NOT NULL,
    landed_cost numeric(18, 2) NOT NULL,
    cumulative_value numeric(18, 2) NOT NULL,
    CONSTRAINT ck_projection_by_direction_direction CHECK (direction IN ('IN', 'OUT')),
    CONSTRAINT uq_projection_by_direction UNIQUE (session_id, period, direction)
);

CREATE TABLE projection_summary (
    id bigserial PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    period date NOT NULL,
    total_quantity numeric(18, 4) NOT NULL,
    total_value numeric(18, 2) NOT NULL,
    total_landed_cost numeric(18, 2) NOT NULL,
    cover_ratio numeric(7, 4) NOT NULL DEFAULT 0,
    cumulative_value numeric(18, 2) NOT NULL,
    CONSTRAINT uq_projection_summary UNIQUE (session_id, period)
);
