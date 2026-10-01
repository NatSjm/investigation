ALTER TABLE hedge_proposal ADD COLUMN advisor_id VARCHAR(32);
ALTER TABLE hedge_proposal ADD COLUMN stress_shift_bp INTEGER DEFAULT 0;
