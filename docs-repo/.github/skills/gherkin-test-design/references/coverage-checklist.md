# Coverage checklist

## All features
- [ ] Happy path per actor
- [ ] Each BR: positive + boundary + negative
- [ ] Validation errors (required, format, range) with exact error codes
- [ ] Authorisation: advisor vs. admin vs. read-only
- [ ] Concurrency / optimistic locking where edit exists
- [ ] Audit entry produced

## Calculations
- [ ] First month, last month, month with 28/29/30/31 days
- [ ] Leap year, year boundary
- [ ] Zero, negative interest rate, extreme stress scenario
- [ ] Rounding (banker's vs. half-up — as specified in calculation doc)
- [ ] Currency conversion date (spot vs. fixing)
- [ ] Idempotent recomputation produces identical results

## API
- [ ] Contract matches `generated/openapi` (status codes, schemas)
- [ ] Pagination / filtering if present
- [ ] Idempotency key on POST where specified

## Kafka
- [ ] Consumer idempotency (duplicate message)
- [ ] Out-of-order message
- [ ] Poison message → DLQ
- [ ] Schema compatibility with `generated/asyncapi`

## UI
- [ ] Loading / empty / error states
- [ ] Graph renders with min/max data points
- [ ] Accessibility basics (labels, keyboard)
