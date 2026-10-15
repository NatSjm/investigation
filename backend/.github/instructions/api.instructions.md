---
applyTo: "**/harbor/api/**/*.kt,**/src/main/resources/openapi/*.yaml"
description: "Contract-first REST API: edit openapi/harbor-api.yaml first, regenerate the *Api interfaces, then implement override fun <operationId> in the controller in api/."
---
# REST API (contract-first)

1. **Contract first.** Add or change the operation in `core/src/main/resources/openapi/harbor-api.yaml` (unique `operationId`,
   request/response schemas under `components/schemas`, tag = context name from `contexts.yml`). The frontend client is
   generated from the same file, so schema names are shared.
2. **Regenerate.** `mvn -q -pl core -am -DskipTests generate-sources` produces the `*Api` interfaces in `core/target/generated-sources`.
   Never edit or commit generated code; never add `@*Mapping` annotations in controllers.
3. **Implement.** `@RestController class XxxController(private val manager: XxxManager) : XxxApi` in `harbor/api/` with
   `override fun <operationId>(...)` delegating to the manager. The controller maps DTOs, the manager holds the use case;
   controllers never inject a `*Dao` or a `*Service` directly.
4. **Session scope.** Every `/session/**` path item references `components/parameters/SessionHeader` (`X-Harbor-Session`).
   Controllers and managers obtain the session via `context/SessionContext`, never from the request directly.
5. **Maps.** Run `scripts/docs/gen-all.py`; `api-index.md` lists operations from `harbor-api.yaml` joined to the `override fun`
   implementation - an operation without implementation shows as `_not implemented_` and must not be left that way.
6. Errors: RFC 7807 `application/problem+json` via `advice/GlobalExceptionAdvice`; no controller-local error formats.
7. Cite the spec ID (`P1-001`, `SES-001`, ...) in the manager KDoc (`@docs`) and in the change description.
