---
type: Decision
title: "ADR-0002: OpenAPI-first contracts for the backend API and external services"
description: backend/core/src/main/resources/openapi/harbor-api.yaml is the single contract; backend server interfaces and the frontend client are generated from it, external services are described by contracts in backend/core/src/main/resources/api, and copies are published to docs-repo/generated/openapi.
tags: [adr, openapi, contracts]
status: stable
generated: { by: human:platform-team, at: 2026-10-09T08:00:00Z }
---

# ADR-0002: OpenAPI-first contracts for the backend API and external services

- **Status**: Accepted
- **Date**: 2026-10-09
- **Deciders**: harbor-platform-team
- **Related**: [Integrations map](/architecture/integrations.md), [ADR-0001](/architecture/adr/0001-docs-as-code.md)

## Context
Harbor has one backend (`harbor-backend`, Maven modules `core` + `kafka_client`) and one frontend (`harbor-frontend`). Endpoint paths,
request/response shapes and the `X-Harbor-Session` header must be identical on both sides, and the docs repo must
be able to anchor specs to endpoints (`generated/openapi/backend.yaml#/paths/...`) without reading source code.
Five external services (`client-registry`, `market-data`, `cover-provider`, `document-service`, `file-exchange`)
are called through thin clients whose shapes also need to be stable and reviewable.

## Decision
- `backend/core/src/main/resources/openapi/harbor-api.yaml` (server base `/api/v1`) is **the** contract. Every operation has an `operationId`
  (e.g. `getProduct1Overview`), tags equal to the bounded context, and `/session/**` operations declare the
  `X-Harbor-Session` header parameter.
- The backend generates `*Api` interfaces into `core/target/` (not committed). Controllers are
  `@RestController class XxxController(...) : XxxApi` and implement `override fun <operationId>(...)` **without**
  mapping annotations; the annotations live on the generated interface.
- The frontend generates `src/api/generated/schema.d.ts` (openapi-typescript, committed and trimmed) and calls the
  API only through the `openapi-fetch` client in `src/api/client.ts`, whose middleware adds `X-Harbor-Session` from
  `sessionStore`. Hooks use literal path strings (`api.GET('/clients/{clientId}/overview', ...)`), which is what the
  frontend codebase map and the graph join on.
- External contracts live in `backend/core/src/main/resources/api/<name>.yaml`; `core` generates one `*Api`
  per service, wrapped by a `@Component` in the `client/` layer.
- Asynchronous messages are described in `backend/core/src/main/resources/openapi/harbor-events.yaml`; topic names are
  constants in `Topics.kt` (`kafka_client`).
- CI publishes copies to `docs-repo/generated/openapi/backend.yaml`, `generated/openapi/external/<name>.yaml`
  and `generated/asyncapi/backend.yaml`. Specs reference contracts only through these anchors.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Code-first (springdoc from annotations) | no extra authoring step | contract drifts per branch; frontend types lag; anchors unstable |
| OpenAPI-first (chosen) | one reviewable contract, generated both sides, stable anchors for docs | generation step in both builds; contract PRs need review discipline |
| Hand-written frontend client | flexible | duplicated paths/types, no compile-time check against the backend |

## Consequences
+ `generated/be/api-index.md` is produced from `harbor-api.yaml` + `override fun` lookup, so the API index is exact.
+ Spec tables cite `generated/openapi/backend.yaml#/paths/~1session~1product1~1overview` and the like.
− A new endpoint requires a contract change first; breaking changes need a version bump of the generated client.
