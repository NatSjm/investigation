# Coverage checklist

## All features
- [ ] Happy path per actor (representative, administrator, client-facing vs preparation session)
- [ ] Each BR: positive + boundary + negative
- [ ] Validation errors (required, format, range) with exact error codes
- [ ] Authorisation: representative vs administrator vs read-only
- [ ] Session scope: missing `X-Harbor-Session` -> 428; closed session -> 409; unknown -> 404
- [ ] Audit / change-log entry produced where the spec says so

## Calculations
- [ ] First month and last month of the horizon; horizon 12 and 60
- [ ] Zero quantities, empty movement set, total below `role.min_volume`
- [ ] Importer, exporter and MIXED sign conventions
- [ ] Rounding (`HALF_EVEN`, scale 2 / 4) exactly as the calculation concept states
- [ ] Price basis per corridor side (VLD/NRL, CST/MRD) kept apart
- [ ] Idempotent recomputation produces identical results

## API
- [ ] Contract matches `generated/openapi/backend.yaml` (status codes, schemas, `operationId`)
- [ ] Filtering (`city`, `transportMode`, `dimension`) if present
- [ ] Idempotency on POST where specified (`runStressTest`, `regenerateReport`)

## Kafka
- [ ] Consumer idempotency (duplicate message)
- [ ] Out-of-order message
- [ ] Poison message -> DLQ
- [ ] Schema compatibility with `generated/asyncapi/backend.yaml` and with the payload schema `generated/be/events.md` names for the topic (`generated/asyncapi/schemas/**`, fields listed in `events.md`)

## UI
- [ ] Loading / empty / error states
- [ ] Charts render with min / max data points; dimension toggle switches series
- [ ] Modals validate before submit; PDF download button disabled until the report is rendered
- [ ] Accessibility basics (labels, keyboard)
