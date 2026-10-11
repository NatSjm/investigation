---
type: Glossary
title: Glossary
description: Canonical business terminology of the Harbor platform; agents must use these terms and add new ones here first.
tags: [domain]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# Glossary

Single source of terminology. One line per term, alphabetical. Agents MUST use these terms.
The repo is written in **English**. The `Aliases` column holds synonyms and source-language terms found in legacy
pages or searched for by people; they are never used in specs. When migrating a legacy page or publishing back to
its source language, agents translate terms only via this table; anything not listed here is added first, never
translated ad hoc. Identifiers in code (`ClientRole.IMPORTER`, `ProductGroup.product1`, ...) follow the blueprint
and are quoted verbatim.

| Term | Definition | Aliases | Used in |
|---|---|---|---|
| Actual movement | A goods movement parsed from a daily XLS file delivered by `file-exchange` into `goods_movement`, rolled up monthly into `movement_monthly` | real movement, imported movement | IMP-001, P1-001, `client_role_classification` |
| Baseline curve | Monthly price and transport price per product group and corridor delivered by `market-data` into `baseline_price`; the reference every scenario shocks | baseline, market curve | MKT-001, `scenario_price_path`, `stress_test_monthly` |
| Client | A company that moves goods on one or both product groups; identified by `client_profile.id`, linked to `client-registry` by `external_ref` | customer, account | CLI-001, MTG-001 |
| Corridor | The pair of countries a product group moves between: `VLD <-> NRL` for Product 1, `CST <-> MRD` for Product 2 | route, lane | P1-001, MKT-001 |
| Cover | A policy (`cover_policy`) that covers a share of the value of movements of a sub-product for a validity period | policy, protection | COV-001, `cover_ratio` |
| Presentation window | The client-facing second browser window of a CLIENT session (`/present/<sessionId>`): mirrors the representative's current step and filters over the BroadcastChannel `harbor.session.<sessionId>`, without navigation or controls | client screen, second screen, mirror window | PRS-001, MTG-001 |
| Cover ratio | Covered value divided by total value per month (scale 4); shown as charts on the overview pages | coverage | `cover_ratio`, P1-001, COV-001 |
| Cover share | `cover_policy.covered_share` — the fraction of value a policy covers (0..1) | covered share | `cover_ratio` |
| Dimension | The primary breakdown of a product group: **city** hubs (`Aldmoor`, `Brightwater`, `Carrow`, `Dunmere`) for Product 1, **transport modes** (`ROAD`, `RAIL`, `SEA`, `AIR`) for Product 2; API value `CITY` or `TRANSPORT_MODE` | breakdown, dimension kind | P1-001, P2-001, STR-001 |
| Exporter | Client role when the inbound share of movements is `<= role.exporter_threshold` (0.35) | `ClientRole.EXPORTER` | `client_role_classification`, STR-001 |
| Exposure | Stress-test quantity per month and dimension value: uncovered quantity × price difference × role sign | stress exposure | `stress_test_monthly`, STR-001 |
| Import batch | One processed XLS file (`import_batch`): source file, row counts, status; monitored on the admin Imports page | batch, import run | IMP-001, ADM-001 |
| Importer | Client role when the inbound share of movements is `>= role.importer_threshold` (0.65) | `ClientRole.IMPORTER` | `client_role_classification`, STR-001 |
| Landed cost | Value plus tariff, handling cost per city and transport cost per mode for one projection row | total cost, delivered cost | `monthly_projection`, P1-001 |
| Meeting | A real appointment between a representative and a client, held as a session of kind `CLIENT` | client meeting, appointment | MTG-001 |
| Mixed | Client role when the inbound share lies strictly between the exporter and importer thresholds | `ClientRole.MIXED`, two-way | `client_role_classification`, STR-001 |
| Modelled movement | A movement entered per month in the movement modal during a session (`session_movement_input`); overrides the actual movement of the same key | what-if movement, manual movement | P1-001, P2-001 |
| Parameter set | Admin-maintained numeric parameters (`parameter_set.key`, e.g. `role.min_volume`, `tariff.rate`, `handling.cost`); snapshotted into `meeting_session.parameter_snapshot` at session start | parameters, settings | ADM-001, MTG-001 |
| Peer simulation | Modelled movements of similar products at peer firms: segment median monthly quantity × `scaling_factor` (`session_peer_simulation`) | peer benchmark, peer series | P1-001, P2-001 |
| Premium rate | `cover_policy.premium_rate` — price of cover as a fraction of covered value; default `cover.default_premium_rate` (0.012) | premium | COV-001 |
| Preparation session | A dry run of a meeting by the representative alone (`kind = PREPARATION`); never changes the client role | dry run, prep session | MTG-001, CLI-001 |
| Price basis | The country whose price applies to a product group's values: `VLD` or `NRL` for Product 1, `CST` or `MRD` for Product 2 (`PriceBasis`) | pricing country | P1-001, MTG-001 |
| Product group | One of the two traded groups: `product1` (grades `P1-STD`, `P1-PRM`, `P1-ECO`) and `product2` (variants `P2-S`, `P2-M`, `P2-L`) (`ProductGroup`) | product line | all specs |
| Projection | Monthly figures (quantity, value, landed cost, cumulative value) over the session horizon in four cumulative tables: by sub-product, by dimension, by direction, summary | forecast, projection tables | `monthly_projection`, P1-001, P2-001 |
| Report payload | JSON snapshot of a closed session stored in `meeting_report.payload` and rendered to PDF by `document-service` | meeting report, report JSON | RPT-001 |
| Representative | Employee who runs meetings and preparation sessions for clients (`meeting_session.representative_id`) | account representative, rep | MTG-001, CLI-001 |
| Role override | Manual replacement of the computed client role during a session (`meeting_session.role_override` + reason); applied to `client_role` when a `CLIENT` session closes | manual role | MTG-001, CLI-001 |
| Scenario | A named set of shocks on top of the baseline curve for one session (`market_scenario`) | market scenario, what-if | MKT-001, STR-001 |
| Session | One meeting or preparation run (`meeting_session`); created when a product group is selected on the client overview; identified by `X-Harbor-Session` on every `/session/**` request | meeting session | MTG-001 |
| Shock | One entry of `market_scenario.shocks`: `fromMonth`, `priceChangePct`, `transportChangePct`, applied multiplicatively from that month on | price shock | `scenario_price_path`, MKT-001 |
| Stress test | Monthly table per scenario and dimension value of exposure, transport cost delta and cumulative exposure (`stress_test_result`) | what-if analysis | `stress_test_monthly`, STR-001 |
| Sub-product | Grade or variant inside a product group: `P1-STD`, `P1-PRM`, `P1-ECO`; `P2-S`, `P2-M`, `P2-L` | grade, variant | P1-001, P2-001, COV-001 |
| Transport price | Price per unit for moving goods on a corridor in the baseline curve or a scenario (`baseline_price.transport_price`); not the same as the admin parameter `transport.cost` per mode | freight price | `scenario_price_path`, `stress_test_monthly`, STR-001 |
