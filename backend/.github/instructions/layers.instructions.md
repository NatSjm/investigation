---
applyTo: "**/src/main/kotlin/**"
description: "Package-by-layer rules for the application module: allowed dependencies between layers and sub-layers, and the business-prefix naming rule (prefix = bounded context)."
---
# Layers and naming (`harbor-core/src/main/kotlin/com/acme/harbor/<layer>/`)

Allowed dependency direction: `api` -> `manager` -> `service` -> `dao` / `utils` / `client` (constructor injection only;
`components.md` and the docs graph read the injected dependencies). The layer list with one-line roles is
`scripts/docs/docs-gen.json` (`layers`); sub-packages listed there (`dao/model`, `client/rest`, ...) are layers of their own.

| Layer | May inject / call | Must not |
|---|---|---|
| `api` (controllers), `api/technical` | `manager`, `mapper`, `validator`, `api/error`, `HttpHeadersFactory` | inject a `dao/*`, `service` or `client/*`; hold business logic |
| `api/error`, `api/model`, `api/validation` | Spring web types only | reach into `manager` or `dao/*` |
| `event` (listeners, publishers) | `manager`, `client/kafka`, `kafka-client` | inject a `dao/*` |
| `job` | `manager` | inject a `dao/*` |
| `manager` | `service`, `dao/repository`, `dao/service`, `client/rest`, `mapper`, `validator`, `utils`, `event` publishers | inject another context's repository (call its manager) |
| `service` | `dao/repository`, `dao/service`, `utils`, `client/rest`, `context` | inject a `manager` or a controller |
| `dao/repository` (Spring Data / JDBC) | `dao/model`, `dao/mapper`, `dao/converter` | inject services or managers |
| `dao/service` (persistence services) | `dao/repository`, `dao/specification`, `dao/model` | hold business rules (lookups and filtered listings only) |
| `dao/model` (entities), `dao/specification`, `dao/mapper`, `dao/converter` | `enums`, `model` | reference Spring beans |
| `client/rest` | generated clients of `resources/api/*.yaml` | contain business rules |
| `client/kafka` | `KafkaTemplate` from `config/KafkaConfig` | know topic names (the publishers in `event/` pass `Topics.X`) |
| `utils` | nothing (pure Kotlin, JDK + `enums` + `model`) | Spring annotations, `dao/*`, `client/*`, config reads |

- **Business-prefix naming = context.** A class starts with the prefix of its bounded context from the docs repo
  `contexts.yml` (`Product1Manager`, `ProjectionService`, `ProjectionRepository`, `StressTestController`), whatever its
  layer or sub-layer. A new prefix needs a `contexts.yml` line in the same change; classes matching no prefix are
  `shared` (keep those infrastructure-only: `HarborConstants`, `ProblemDetails`, `EventProducer`, ...).
- Suffix = stereotype: `*Controller` (api), `*Manager`, `*Service`, `*Repository` (dao/repository), `*DaoService`
  (dao/service), `*Specifications`, `*RowMapper`, `*Converter`, `*Client` (client/rest), `*Listener` / `*Publisher` /
  `*Requester` (event), `*Job`, `*Mapper`, `*Validator`, `*Calculator` / `*Aggregator` (utils).
- One manager per context with KDoc + `@docs <ID>`; it is the transactional boundary and the only cross-context entry point.
- After adding a class, a sub-package or an injected dependency run `scripts/docs/gen-all.py` and commit `components.md`;
  a new sub-package that should be its own layer is added to `layers` in `scripts/docs/docs-gen.json` first.
