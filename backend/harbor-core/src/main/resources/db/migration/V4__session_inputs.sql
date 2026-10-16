-- Inputs entered during a meeting: modelled movements (modal 1) and peer simulation runs (modal 2).

CREATE TABLE session_movement_input (
    id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    period date NOT NULL,
    sub_product varchar(16) NOT NULL,
    city varchar(64),
    transport_mode varchar(8),
    direction varchar(3) NOT NULL,
    quantity numeric(18, 4) NOT NULL,
    unit_price numeric(18, 4) NOT NULL,
    CONSTRAINT ck_session_movement_input_transport_mode CHECK (transport_mode IS NULL OR transport_mode IN ('ROAD', 'RAIL', 'SEA', 'AIR')),
    CONSTRAINT ck_session_movement_input_direction CHECK (direction IN ('IN', 'OUT')),
    CONSTRAINT ck_session_movement_input_quantity CHECK (quantity >= 0)
);

CREATE INDEX ix_session_movement_input_session ON session_movement_input (session_id, period);

CREATE TABLE session_peer_simulation (
    id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    peer_segment varchar(64) NOT NULL,
    scaling_factor numeric(8, 4) NOT NULL,
    generated_at timestamp NOT NULL,
    CONSTRAINT ck_session_peer_simulation_scaling CHECK (scaling_factor > 0)
);

CREATE INDEX ix_session_peer_simulation_session ON session_peer_simulation (session_id, generated_at DESC);
