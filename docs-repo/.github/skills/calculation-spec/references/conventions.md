# Conventions vocabulary

## Day-count
`ACT/360`, `ACT/365`, `ACT/ACT`, `30/360`, `30E/360` — name the one the code uses; if none is explicit,
document what the code actually does and open a question.

## Rounding
`HALF_UP`, `HALF_EVEN` (banker's), `DOWN`; precision as decimal places per currency/quantity.
Say **where** rounding happens (per period vs. at the end).

## Dates
Business-day calendar used; roll convention (`FOLLOWING`, `MODIFIED_FOLLOWING`); time zone of "today".

## Rates
Fixed vs. floating; source of fixing; negative rate handling (floor at 0? pass through?).

## Scenarios (stress test)
Shock type (parallel, steepening, FX), magnitude units (bp, %), application point (spot vs. forward).
