---
applyTo: "core/src/main/kotlin/**"
description: "Package-by-layer rules for core: allowed dependencies between layers and the business-prefix naming rule (prefix = bounded context)."
---
# Layers and naming (`core/src/main/kotlin/harbor/<layer>/`)

Allowed dependency direction: `api` -> `manager` -> `service` -> `dao` / `utils` / `client` (constructor injection only;
`components.md` and the docs graph read the injected dependencies).

| Layer | May inject / call | Must not |
|---|---|---|
| `api` (controllers) | `manager`, `mapper`, `validator` | inject a `dao`, `service` or `client`; hold business logic |
| `event` (listeners, publishers) | `manager`, `kafka_client` | inject a `dao` |
| `job` | `manager` | inject a `dao` |
| `manager` | `service`, `dao`, `client`, `mapper`, `validator`, `utils`, `event` publishers | inject another context's `dao` (call its manager) |
| `service` | `dao`, `utils`, `client`, `context` | inject a `manager` or a controller |
| `dao` | `model` | inject services or managers |
| `client` | generated clients of `resources/api/*.yaml` | contain business rules |
| `utils` | nothing (pure Kotlin, JDK + `enums`) | Spring annotations, `dao`, `client`, config reads |

- **Business-prefix naming = context.** A class starts with the prefix of its bounded context from the docs repo
  `contexts.yml` (`Product1Manager`, `ProjectionService`, `ProjectionDao`, `StressTestController`). A new prefix needs a
  `contexts.yml` line in the same change; classes matching no prefix are `shared` (keep those infrastructure-only).
- Suffix = stereotype: `*Controller` (api), `*Manager`, `*Service`, `*Dao`, `*Client`, `*Listener` / `*Publisher` / `*Requester`
  (event), `*Job`, `*Mapper`, `*Validator`, `*Calculator` / `*Aggregator` (utils).
- One manager per context with KDoc + `@docs <ID>`; it is the transactional boundary and the only cross-context entry point.
- After adding a class or changing an injected dependency run `scripts/docs/gen-all.ps1` and commit `components.md`.
