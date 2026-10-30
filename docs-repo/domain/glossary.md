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
The repo is written in **English**: `Term` is the canonical English term, the one every file uses. `Term (cs)` is the
canonical Czech term - the one word the team uses for the concept; an agent that answers or writes in Czech renders
every term through this column, never by an ad-hoc translation, and an empty cell means no Czech term is agreed yet
(the English term is used and the gap reported). Another language gets its own `Term (<code>)` column; the scripts
read the columns by header. A language term is the nominative singular, lowercase unless a proper noun, and the
English word itself when that is what the team says; one term per cell, other wordings go to `Aliases`. The
`Aliases` column holds synonyms and other wordings in any language found in imported pages or searched for by
people; they are never used in specs. When migrating an imported page or publishing back to its source language,
agents translate terms only via this table; anything not listed here is added first, never translated ad hoc. A
language term an agent proposed and no owner confirmed is listed under Open questions (prompt `translate-glossary`
fills a column from the frontend translation file and the imported pages in that language). Identifiers in code
(`ClientRole.IMPORTER`, `ProductGroup.product1`, ...) follow the blueprint and are quoted verbatim.

| Term | Term (cs) | Definition | Aliases | Used in |
|---|---|---|---|---|
| Actual movement | skutečný pohyb | A goods movement parsed from a daily XLS file delivered by `file-exchange` into `goods_movement`, rolled up monthly into `movement_monthly` | real movement, imported movement | IMP-001, P1-001, `client_role_classification` |
| Baseline curve | výchozí křivka | Monthly price and transport price per product group and corridor delivered by `market-data` into `baseline_price`; the reference every scenario shocks | baseline, market curve | MKT-001, `scenario_price_path`, `stress_test_monthly` |
| Client | klient | A company that moves goods on one or both product groups; identified by `client_profile.id`, linked to `client-registry` by `external_ref` | customer, account | CLI-001, SES-001 |
| Corridor | koridor | The pair of countries a product group moves between: `VLD <-> NRL` for Product 1, `CST <-> MRD` for Product 2 | route, lane, Veldora - Norland (VLD <-> NRL) | P1-001, MKT-001 |
| Cover | krytí | A policy (`cover_policy`) that covers a share of the value of movements of a sub-product for a validity period | policy, protection | COV-001, `cover_ratio` |
| Cover ratio | poměr krytí | Covered value divided by total value per month (scale 4); shown as charts on the overview pages | coverage | `cover_ratio`, P1-001, COV-001 |
| Cover share | podíl krytí | `cover_policy.covered_share` — the fraction of value a policy covers (0..1) | covered share | `cover_ratio` |
| Dimension | dimenze | The primary breakdown of a product group: **city** hubs (`Aldmoor`, `Brightwater`, `Carrow`, `Dunmere`) for Product 1, **transport modes** (`ROAD`, `RAIL`, `SEA`, `AIR`) for Product 2; API value `CITY` or `TRANSPORT_MODE` | breakdown, dimension kind | P1-001, P2-001, STR-001 |
| Exporter | exportér | Client role when the inbound share of movements is `<= role.exporter_threshold` (0.35) | `ClientRole.EXPORTER` | `client_role_classification`, STR-001 |
| Exposure | expozice | Stress-test quantity per month and dimension value: uncovered quantity × price difference × role sign | stress exposure | `stress_test_monthly`, STR-001 |
| Import batch | importní dávka | One processed XLS file (`import_batch`): source file, row counts, status; monitored on the admin Imports page | batch, import run | IMP-001, ADM-001 |
| Importer | importér | Client role when the inbound share of movements is `>= role.importer_threshold` (0.65) | `ClientRole.IMPORTER` | `client_role_classification`, STR-001 |
| Landed cost | celkové dodací náklady | Value plus tariff, handling cost per city and transport cost per mode for one projection row | total cost, delivered cost | `monthly_projection`, P1-001 |
| Meeting | schůzka | A real appointment between a representative and a client, held as a session of kind `CLIENT` | client meeting, appointment | SES-001 |
| Mixed | smíšený | Client role when the inbound share lies strictly between the exporter and importer thresholds | `ClientRole.MIXED`, two-way | `client_role_classification`, STR-001 |
| Modelled movement | modelovaný pohyb | A movement entered per month in the movement modal during a session (`session_movement_input`); overrides the actual movement of the same key | what-if movement, manual movement | P1-002, P2-002 |
| Parameter set | sada parametrů | Admin-maintained numeric parameters (`parameter_set.key`, e.g. `role.min_volume`, `tariff.rate`, `handling.cost`); snapshotted into `meeting_session.parameter_snapshot` at session start | parameters, settings | ADM-001, SES-001 |
| Peer simulation | simulace srovnatelných firem | Modelled movements of similar products at peer firms: segment median monthly quantity × `scaling_factor` (`session_peer_simulation`) | peer benchmark, peer series | P1-003, P2-003 |
| Premium rate | sazba prémie | `cover_policy.premium_rate` — price of cover as a fraction of covered value; default `cover.default_premium_rate` (0.012) | premium | COV-001 |
| Preparation session | přípravné sezení | A dry run of a meeting by the representative alone (`kind = PREPARATION`); never changes the client role | dry run, prep session | SES-001, CLI-001 |
| Presentation window | prezentační okno | The client-facing second browser window of a CLIENT session (`/present/<sessionId>`): mirrors the representative's current step and filters over the BroadcastChannel `harbor.session.<sessionId>`, without navigation or controls | client screen, second screen, mirror window | PRS-001, SES-001 |
| Price basis | cenová báze | The country whose price applies to a product group's values: `VLD` or `NRL` for Product 1, `CST` or `MRD` for Product 2 (`PriceBasis`) | pricing country | P1-001, SES-001 |
| Product group | produktová skupina | One of the two traded groups: `product1` (grades `P1-STD`, `P1-PRM`, `P1-ECO`) and `product2` (variants `P2-S`, `P2-M`, `P2-L`) (`ProductGroup`) | product line | all specs |
| Projection | projekce | Monthly figures (quantity, value, landed cost, cumulative value) over the session horizon in four cumulative tables: by sub-product, by dimension, by direction, summary, plus the horizon totals of each table per key with share of value | forecast, projection tables, totals | `monthly_projection`, `horizon_totals`, P1-001, P2-001 |
| Report payload | data reportu | JSON snapshot of a closed session stored in `meeting_report.payload` and rendered to PDF by `document-service` | meeting report, report JSON | RPT-001 |
| Representative | obchodní zástupce | Employee who runs meetings and preparation sessions for clients (`meeting_session.representative_id`) | account representative, rep | SES-001, CLI-001 |
| Role override | ruční přepsání role | Manual replacement of the computed client role during a session (`meeting_session.role_override` + reason); applied to `client_role` when a `CLIENT` session closes | manual role | SES-001, CLI-001 |
| Scenario | scénář | A named set of shocks on top of the baseline curve for one session (`market_scenario`) | market scenario, what-if | MKT-001, STR-001 |
| Session | sezení | One meeting or preparation run (`meeting_session`); created when a product group is selected on the client overview; identified by `X-Harbor-Session` on every `/session/**` request | meeting session | SES-001 |
| Shock | šok | One entry of `market_scenario.shocks`: `fromMonth`, `priceChangePct`, `transportChangePct`, applied multiplicatively from that month on | price shock | `scenario_price_path`, MKT-001 |
| Stress test | stresový test | Monthly table per scenario and dimension value of exposure, transport cost delta and cumulative exposure (`stress_test_result`) | what-if analysis | `stress_test_monthly`, STR-001 |
| Sub-product | podprodukt | Grade or variant inside a product group: `P1-STD`, `P1-PRM`, `P1-ECO`; `P2-S`, `P2-M`, `P2-L` | grade, variant | P1-001, P2-001, COV-001 |
| Transport price | cena dopravy | Price per unit for moving goods on a corridor in the baseline curve or a scenario (`baseline_price.transport_price`); not the same as the admin parameter `transport.cost` per mode | freight price | `scenario_price_path`, `stress_test_monthly`, STR-001 |

## Open questions

Czech terms proposed by `translate-glossary` on 2026-10-30 without a translation-file value or a Czech page wording
(the Harbor frontend has no translation file and the imported pages are English); an owner confirms each or replaces it.

- [ ] cs "skutečný pohyb" (Actual movement): proposed, unsourced - owner confirms or replaces
- [ ] cs "výchozí křivka" (Baseline curve): proposed, unsourced - owner confirms or replaces
- [ ] cs "klient" (Client): proposed, unsourced - owner confirms or replaces
- [ ] cs "koridor" (Corridor): proposed, unsourced - owner confirms or replaces
- [ ] cs "krytí" (Cover): proposed, unsourced - owner confirms or replaces
- [ ] cs "poměr krytí" (Cover ratio): proposed, unsourced - owner confirms or replaces
- [ ] cs "podíl krytí" (Cover share): proposed, unsourced - owner confirms or replaces
- [ ] cs "dimenze" (Dimension): proposed, unsourced - owner confirms or replaces
- [ ] cs "exportér" (Exporter): proposed, unsourced - owner confirms or replaces
- [ ] cs "expozice" (Exposure): proposed, unsourced - owner confirms or replaces
- [ ] cs "importní dávka" (Import batch): proposed, unsourced - owner confirms or replaces
- [ ] cs "importér" (Importer): proposed, unsourced - owner confirms or replaces
- [ ] cs "celkové dodací náklady" (Landed cost): proposed, unsourced - owner confirms or replaces
- [ ] cs "schůzka" (Meeting): proposed, unsourced - owner confirms or replaces
- [ ] cs "smíšený" (Mixed): proposed, unsourced - owner confirms or replaces
- [ ] cs "modelovaný pohyb" (Modelled movement): proposed, unsourced - owner confirms or replaces
- [ ] cs "sada parametrů" (Parameter set): proposed, unsourced - owner confirms or replaces
- [ ] cs "simulace srovnatelných firem" (Peer simulation): proposed, unsourced - owner confirms or replaces
- [ ] cs "sazba prémie" (Premium rate): proposed, unsourced - owner confirms or replaces
- [ ] cs "přípravné sezení" (Preparation session): proposed, unsourced - owner confirms or replaces
- [ ] cs "prezentační okno" (Presentation window): proposed, unsourced - owner confirms or replaces
- [ ] cs "cenová báze" (Price basis): proposed, unsourced - owner confirms or replaces
- [ ] cs "produktová skupina" (Product group): proposed, unsourced - owner confirms or replaces
- [ ] cs "projekce" (Projection): proposed, unsourced - owner confirms or replaces
- [ ] cs "data reportu" (Report payload): proposed, unsourced - owner confirms or replaces
- [ ] cs "obchodní zástupce" (Representative): proposed, unsourced - owner confirms or replaces
- [ ] cs "ruční přepsání role" (Role override): proposed, unsourced - owner confirms or replaces
- [ ] cs "scénář" (Scenario): proposed, unsourced - owner confirms or replaces
- [ ] cs "sezení" (Session): proposed, unsourced - owner confirms or replaces
- [ ] cs "šok" (Shock): proposed, unsourced - owner confirms or replaces
- [ ] cs "stresový test" (Stress test): proposed, unsourced - owner confirms or replaces
- [ ] cs "podprodukt" (Sub-product): proposed, unsourced - owner confirms or replaces
- [ ] cs "cena dopravy" (Transport price): proposed, unsourced - owner confirms or replaces
