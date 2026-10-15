---
type: Document
title: "Datasets (BE)"
description: "Generated catalogue of the named synthetic datasets - local seeds and integration-test fixtures - with purpose, tables and row counts, dependencies, the tests that load them and one sample row per table; cite a dataset by name in Gherkin instead of describing rows."
generated:
  by: process:gen-docs
  at: 2026-10-15
status: stable
---
# Datasets (BE)

> Generated from `scripts/db/seed + src/test/resources/datasets headers` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
5 dataset(s): 3 seed(s) for the developer database (`scripts/db/seed-local.py`), 2 integration-test fixture(s) (`@Sql("/datasets/<name>.sql")`). Row counts are tuples in `INSERT` statements; samples are the first row per table, shown only for datasets declared `synthetic: yes`.
Use in test design: `Given dataset "<name>" is loaded` (step vocabulary in the docs repo, `test-design/README.md`); add explicit `Given` rows only for the values a scenario asserts on.

| Dataset | Kind | Purpose | Tables (rows) | Depends on | Loaded by | Location |
|---|---|---|---|---|---|---|
| `adm-parameter-versions` | fixture | extra parameter_set versions on top of the Flyway seeds - a future tariff.rate for PRODUCT1/NRL that is listed but not yet in force, and a newer global peer.scaling_default - for scope and version resolution tests (ADM-001 BR-4, BR-6) | `parameter_set` (2) |  | (nothing yet) | `core/src/test/resources/datasets/adm-parameter-versions.sql` |
| `mtg-session-snapshot` | fixture | an open Product 1 session for BOREAL-SYN whose parameter snapshot holds tariff.rate.NRL = 0.04 while the live parameter_set already has a newer NRL version of 0.045 - the "parameter changed after the session started" situation (MTG-001 BR-2, ADM-001 BR-9) | `meeting_session` (1), `session_client_config` (1), `parameter_set` (1) | reference-clients | (nothing yet) | `core/src/test/resources/datasets/mtg-session-snapshot.sql` |
| `p1-baseline-12m` | seed | ACME-SYN with the last 12 full months of Product 1 actual movements - P1-STD inbound via Aldmoor by road (100 units a month) and P1-PRM outbound via Brightwater by rail (40 units a month) - enough for the overview, the role classification and a projection | `movement_monthly` (24) | reference-clients | (nothing yet) | `scripts/db/seed/20-p1-baseline-12m.sql` |
| `reference-clients` | seed | three synthetic clients with fixed ids - ACME-SYN (importer profile), BOREAL-SYN (exporter profile), CARROW-SYN (mixed) - the anchors every other dataset refers to | `client_profile` (3) |  | (nothing yet) | `scripts/db/seed/10-reference-clients.sql` |
| `sessions-open` | seed | one open Product 1 client session for ACME-SYN with a 24-month horizon, price basis VLD and a parameter snapshot taken from the seeded defaults - the session every session-scoped endpoint can be called with | `meeting_session` (1), `session_client_config` (1) | reference-clients, p1-baseline-12m | (nothing yet) | `scripts/db/seed/30-sessions-open.sql` |

## Sample rows
First row of each table, synthetic datasets only; `id` columns and generated values omitted when long.

- `adm-parameter-versions` / `parameter_set`: key=tariff.rate, scope_product_group=PRODUCT1, scope_country=NRL, scope_value=NULL, value=0.06, valid_from=2099-01-01, updated_by=fixture:a…
- `mtg-session-snapshot` / `meeting_session`: product_group=PRODUCT1, kind=CLIENT, representative_id=rep-syn-2, status=OPEN, started_at=2026-09-01
- `mtg-session-snapshot` / `session_client_config`: horizon_months=24, price_basis=NRL, cover_preference=PARTIAL
- `mtg-session-snapshot` / `parameter_set`: key=tariff.rate, scope_product_group=PRODUCT1, scope_country=NRL, scope_value=NULL, value=0.045, valid_from=2026-09-15, updated_by=fixture:…
- `p1-baseline-12m` / `movement_monthly`: product_group=PRODUCT1, sub_product=P1-STD, city=Aldmoor, transport_mode=ROAD, direction=IN, period=2025-10-01, quantity=100, value=1250.00
- `reference-clients` / `client_profile`: external_ref=REG-1001, name=Acme Goods Ltd., country=VLD, segment=TRADER
- `sessions-open` / `meeting_session`: product_group=PRODUCT1, kind=CLIENT, representative_id=rep-syn-1, status=OPEN
- `sessions-open` / `session_client_config`: horizon_months=24, price_basis=VLD, cover_preference=NONE

_1 SQL file(s) outside the migrations have no `-- dataset:` header and are not catalogued._
