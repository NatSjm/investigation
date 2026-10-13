---
type: Document
title: "Parameters (BE)"
description: "Generated catalogue of the admin parameters: every ParameterKey key with its seeded defaults per scope, the classes that read it and the validator that bounds it; the meaning of a key is documented in domain/calculations and the admin spec."
generated:
  by: process:gen-docs
  at: 2026-10-13
status: stable
---
# Parameters (BE)

> Generated from `ParameterKey + parameter_set seeds` by `scripts/docs` (regex scan, no build required). Do not edit by hand.
10 key(s), 19 seeded value(s). Scope = product group / country / scope value; `global` = no scope. Lookups take the most specific scope in force, then the newest `valid_from`.
Meaning, unit and business rule of each key: `domain/calculations/*.md` (`## Parameters`) and the admin feature spec; `scripts/validate-frontmatter.ps1` checks that every key below is documented there and that documents name only keys that exist here.

| Key | Constant | Seeded defaults | Read by | Validated by | Location |
|---|---|---|---|---|---|
| `cover.default_premium_rate` | `COVER_DEFAULT_PREMIUM_RATE` | global = 0.012 (from 2020-01-01) | `CoverQuoteService`, `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:11` |
| `handling.cost` | `HANDLING_COST` | Aldmoor = 0.80 (from 2020-01-01); Brightwater = 0.95 (from 2020-01-01); Carrow = 0.70 (from 2020-01-01); Dunmere = 1.10 (from 2020-01-01) | `ProjectionInputAssembler` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:9` |
| `peer.scaling_default` | `PEER_SCALING_DEFAULT` | global = 1.0 (from 2020-01-01) | `MeetingManager`, `PeerSimulationService` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:14` |
| `projection.horizon_months_default` | `PROJECTION_HORIZON_MONTHS_DEFAULT` | global = 24 (from 2020-01-01) | `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:12` |
| `role.exporter_threshold` | `ROLE_EXPORTER_THRESHOLD` | global = 0.35 (from 2020-01-01) | `ClientRoleService`, `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:7` |
| `role.importer_threshold` | `ROLE_IMPORTER_THRESHOLD` | global = 0.65 (from 2020-01-01) | `ClientRoleService`, `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:6` |
| `role.min_volume` | `ROLE_MIN_VOLUME` | global = 100 (from 2020-01-01) | `ClientRoleService`, `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:5` |
| `stress.rounding_scale` | `STRESS_ROUNDING_SCALE` | global = 2 (from 2020-01-01) | `MeetingManager` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:13` |
| `tariff.rate` | `TARIFF_RATE` | PRODUCT1/NRL = 0.04 (from 2020-01-01); PRODUCT1/VLD = 0.05 (from 2020-01-01); PRODUCT2/CST = 0.03 (from 2020-01-01); PRODUCT2/MRD = 0.035 (from 2020-01-01) | `MeetingManager`, `ProjectionInputAssembler` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:8` |
| `transport.cost` | `TRANSPORT_COST` | AIR = 3.50 (from 2020-01-01); RAIL = 0.90 (from 2020-01-01); ROAD = 1.20 (from 2020-01-01); SEA = 0.60 (from 2020-01-01) | `ProjectionInputAssembler` | `ParameterValidator` | `core/src/main/kotlin/harbor/enums/ParameterKey.kt:10` |
