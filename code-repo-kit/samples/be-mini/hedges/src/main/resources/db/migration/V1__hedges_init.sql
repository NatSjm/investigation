CREATE TABLE hedge_proposal (
    id              UUID PRIMARY KEY,
    client_id       VARCHAR(32) NOT NULL,
    notional        NUMERIC(18, 2) NOT NULL,
    fixed_rate      NUMERIC(9, 6) NOT NULL,
    start_month     DATE NOT NULL,
    end_month       DATE NOT NULL,
    status          VARCHAR(16) NOT NULL DEFAULT 'DRAFT',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE hedge_cashflow (
    proposal_id     UUID NOT NULL REFERENCES hedge_proposal(id),
    month           DATE NOT NULL,
    amount          NUMERIC(18, 2) NOT NULL,
    PRIMARY KEY (proposal_id, month)
);

CREATE INDEX ix_hedge_proposal_client ON hedge_proposal(client_id);
