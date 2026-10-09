-- Market scenarios per session, the baseline curve fed by market-data, and the stress test results.

CREATE TABLE market_scenario (
    id uuid PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    name varchar(120) NOT NULL,
    kind varchar(16) NOT NULL,
    shocks jsonb NOT NULL DEFAULT '[]'::jsonb,
    created_by varchar(64) NOT NULL,
    created_at timestamp NOT NULL,
    CONSTRAINT ck_market_scenario_kind CHECK (kind IN ('REPRESENTATIVE', 'CLIENT'))
);

CREATE INDEX ix_market_scenario_session ON market_scenario (session_id, created_at);

CREATE TABLE baseline_price (
    id bigserial PRIMARY KEY,
    product_group varchar(16) NOT NULL,
    corridor varchar(8) NOT NULL,
    period date NOT NULL,
    price numeric(18, 4) NOT NULL,
    transport_price numeric(18, 4) NOT NULL,
    as_of timestamp NOT NULL,
    CONSTRAINT ck_baseline_price_product_group CHECK (product_group IN ('PRODUCT1', 'PRODUCT2')),
    CONSTRAINT uq_baseline_price UNIQUE (product_group, corridor, period)
);

CREATE TABLE stress_test_result (
    id bigserial PRIMARY KEY,
    session_id uuid NOT NULL REFERENCES meeting_session(id),
    scenario_id uuid NOT NULL REFERENCES market_scenario(id) ON DELETE CASCADE,
    period date NOT NULL,
    dimension_value varchar(64) NOT NULL,
    exposure numeric(18, 2) NOT NULL,
    transport_cost_delta numeric(18, 2) NOT NULL,
    cumulative_exposure numeric(18, 2) NOT NULL,
    CONSTRAINT uq_stress_test_result UNIQUE (session_id, scenario_id, period, dimension_value)
);
