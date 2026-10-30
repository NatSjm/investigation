# Harbor - simulated business case (blueprint)

This file is the **single naming contract** for the simulated `backend/`, `frontend/` and `docs-repo/`.
Every identifier below (module, package, class, endpoint `operationId`, table, topic, route, spec ID,
calculation name, parameter key) must be used verbatim so that the generated maps, the graph and the docs join up.

The case is deliberately generic: a goods-trading company whose **account representatives meet clients** to
review product movements, offer **cover** (insurance) and model **market scenarios**. Nothing in the repository
refers to the real application or its industry.

## 1. Business story

- A **client** is a company that moves goods on one or both of two **product groups**:
  - **Product 1** (`product1`) on corridor **Veldora (`VLD`) <-> Norland (`NRL`)**; sub-products (grades) `P1-STD`, `P1-PRM`, `P1-ECO`;
    primary breakdown dimension: **city hubs** `Aldmoor`, `Brightwater`, `Carrow`, `Dunmere`.
  - **Product 2** (`product2`) on corridor **Castra (`CST`) <-> Meridia (`MRD`)**; sub-products (variants) `P2-S`, `P2-M`, `P2-L`;
    primary breakdown dimension: **transport modes** `ROAD`, `RAIL`, `SEA`, `AIR` (cities exist too, for the overview table).
  - The two countries of a corridor carry their own **price basis** (`priceBasis: VLD|NRL` / `CST|MRD`) - this imitates two currencies per product.
- A client is an **IMPORTER**, **EXPORTER** or **MIXED** per product group. Determined by the algorithm `client_role_classification`
  (12 months of actual movements) or set **manually** during a meeting (`role override`, with reason).
- A **meeting** is a **session** (`meeting_session`): `kind = CLIENT` (real meeting) or `PREPARATION` (dry run by the representative).
  Selecting a product group on the client overview page creates the session; from then on every request carries header
  **`X-Harbor-Session: <sessionId>`** and all `/session/**` endpoints are scoped by it.
- Movements are **actual** (parsed daily from XLS files delivered by the `file-exchange` service into `goods_movement`,
  rolled up monthly into `movement_monthly`) or **modelled** (entered per month in a modal during the meeting, `session_movement_input`).
  A second modal models movements of **similar products at peer firms** (`session_peer_simulation`).
- Per session the backend computes the **monthly projection** (calculation `monthly_projection`) over a planning horizon
  (12-60 months) into **four cumulative tables**: by sub-product, by dimension (city / transport mode), by direction, and the **summary**. Their **horizon totals** (`horizon_totals`: the same breakdowns summed over the horizon with share of value, derived, not persisted) travel with them as `tables.totals`.
  Grouping is done in Kotlin (`core/.../harbor/utils`), not in SQL, because the same aggregation is reused by cover, stress test and reports.
- **Cover**: policies (`cover_policy`) cover a share of value; the overview page shows **cover ratio** charts (`cover_ratio`);
  a quote for the uncovered part can be requested from the external `cover-provider`.
- **Market scenarios** page: representative and client define price/transport-price paths (`market_scenario`, calculation `scenario_price_path`)
  on top of a baseline curve from the external `market-data` service.
- **Stress test** page: monthly table per scenario (`stress_test_monthly`), chart of transport price over time per scenario,
  toggle: by **city** for Product 1, by **transport mode** for Product 2.
- Closing a meeting stores the report payload as JSON (`meeting_report.payload`), requests PDF rendering via Kafka from the external
  `document-service`; the **Meetings** page lists sessions with a **Download PDF** button.
- **Admin** (outside meetings): parameters (`parameter_set`) such as tariff rates, handling costs, thresholds; import batch monitor.
- Everything is **OpenAPI-first**: `backend/harbor-core/src/main/resources/openapi/openapi_harbor.yaml` is the contract; BE server interfaces and the FE client are generated from it.
  External service contracts live in `backend/harbor-core/src/main/resources/api/*.yaml`. Copies of all contracts are published to `docs-repo/generated/openapi/`.

## 2. Repositories and layout

```
backend/        Kotlin 1.9 / Spring Boot 3 / Maven (root pom + harbor-core + kafka-client) / PostgreSQL (Flyway) / Kafka   (simulated repo "harbor-backend")
frontend/       React 18 / TypeScript / react-router / openapi-fetch client                         (simulated repo "harbor-frontend")
docs-repo/      OKF v0.2 docs bundle + Copilot customisation + Python scripts                       (simulated repo "harbor-docs")
code-repo-kit/  reusable kit copied into the code repos (apply-kit.py)
harbor.code-workspace   multi-root workspace: the three repos side by side
```

Naming: company/platform **Harbor**; Maven groupId `com.harbor`; Kotlin base package `harbor` (the folder named after the
project under `src/main/kotlin/`); FE package name `harbor-frontend`. Git remotes are placeholders `https://git.example.com/harbor/<repo>`.

## 3. Backend structure (layered, package-by-layer)

```
backend/
  pom.xml                      root (parent) pom; <modules>: harbor-core, kafka-client
  core/                        the Spring Boot application (all business code)
    pom.xml
    src/main/kotlin/com/acme/harbor/  one folder per technical layer (below)
    src/main/resources/
      api/                     contracts of the EXTERNAL services (client-registry.yaml, market-data.yaml, cover-provider.yaml,
                               document-service.yaml, file-exchange.yaml) -> generated REST clients wrapped in client/rest/
      openapi/                 OUR contract: openapi_harbor.yaml (OpenAPI; BE server interfaces + FE client generated from it)
                               and harbor-events.yaml (AsyncAPI for the Kafka topics)
      db/migration/            Flyway V1__..V9__*.sql
      pdf/                     meeting report template (meeting-report.html, report.css) sent with the payload to document-service
      application.yml
    src/test/kotlin/harbor/    unit tests (utils/*Test.kt hold the worked examples)
  kafka-client/                Maven module: event contracts only - src/main/resources/avro/*.avsc (events Harbor publishes) and
    pom.xml                    src/main/resources/json_<service>/*.json (external events); payload classes generated at build
  init_docker_compose/         local environment: docker-compose.yml (postgres, kafka, wiremock for the 5 external services),
                               init-db.sql, wiremock/mappings/*.json, README.md
  README.md, .gitignore
```

Layers in `harbor-core/src/main/kotlin/com/acme/harbor/` (folder = package `com.acme.harbor.<layer>`; sub-packages `dao/{model,repository,service,mapper,specification,converter}`, `api/{error,technical}`, `client/{rest,kafka}`):

| Layer | Role | Classes (business prefix = bounded context, see `docs-repo/contexts.yml`) |
|---|---|---|
| `advice` | `@RestControllerAdvice` -> ProblemDetail | `GlobalExceptionAdvice` |
| `api` | REST controllers implementing the generated `*Api` interfaces (`override fun <operationId>`, no mapping annotations) | `ClientController`, `SessionController`, `Product1Controller`, `Product2Controller`, `CoverController`, `ScenarioController`, `StressTestController`, `ReportController`, `AdminController` |
| `client` | thin `@Component` wrappers over generated clients of the external services | `ClientRegistryClient`, `MarketDataClient`, `CoverProviderClient`, `DocumentServiceClient`, `FileExchangeClient` |
| `component` | infrastructure components | `SessionHeaderFilter`, `XlsMovementParser`, `WorkbookReader`, `ReportTemplateLoader` |
| `config` | Spring configuration | `HarborBackendApplication` (in package root `harbor`), `KafkaConfig`, `WebConfig`, `JacksonConfig`, `SchedulingConfig` |
| `context` | request/session context | `SessionContext`, `SessionScope`, `CurrentUser` |
| `dao/repository` (entities in `dao/model`, persistence services in `dao/service`) | Spring Data / JDBC repositories | `ClientProfileRepository`, `ClientRoleRepository`, `MeetingSessionRepository`, `SessionClientConfigRepository`, `ImportBatchRepository`, `GoodsMovementRepository`, `MovementMonthlyRepository`, `SessionMovementInputRepository`, `SessionPeerSimulationRepository`, `ProjectionRepository`, `CoverPolicyRepository`, `CoverQuoteRepository`, `MarketScenarioRepository`, `BaselinePriceRepository`, `StressTestResultRepository`, `MeetingReportRepository`, `ParameterRepository` |
| `databind` | Jackson (de)serializers | `MoneySerializer`, `PeriodDeserializer` |
| `enums` | enums | `ProductGroup`, `Direction`, `ClientRole`, `TransportMode`, `PriceBasis`, `SessionKind`, `SessionStatus`, `StressDimension` |
| `event` | Kafka listeners and publishers (topics + payloads come from `kafka-client`) | `MovementsLoadedPublisher`, `SessionEventsPublisher`, `ReportRenderRequester`, `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener`, `MarketPricesListener`, `ReportSessionClosedListener`, `ClientRoleSessionClosedListener`, `ReportRenderedListener` |
| `exception` | exceptions | `NotFoundException`, `SessionHeaderMissingException`, `SessionClosedException`, `ValidationException` |
| `job` | `@Scheduled` jobs | `DailyMovementImportJob` (`0 0 2 * * *`), `MonthlySnapshotJob` (`0 0 3 1 * *`) |
| `manager` | orchestration per bounded context, transactional boundary, KDoc + `@docs <spec ID>` (the entry point an agent reads first) | `ClientManager` (CLI-001), `MeetingManager` (SES-001), `ImportManager` (IMP-001), `Product1Manager` (P1-001), `Product2Manager` (P2-001), `CoverManager` (COV-001), `MarketManager` (MKT-001), `StressManager` (STR-001), `ReportManager` (RPT-001), `AdminManager` (ADM-001) |
| `mapper` | entity/DTO mappers | `ClientMapper`, `SessionMapper`, `ProjectionMapper`, `CoverMapper`, `ScenarioMapper`, `StressMapper`, `ReportMapper`, `ParameterMapper` |
| `model` | JPA entities and internal models | `ClientProfile`, `ClientRoleDecision`, `MeetingSession`, `SessionClientConfig`, `ImportBatch`, `GoodsMovement`, `MovementMonthly`, `SessionMovementInput`, `SessionPeerSimulation`, `ProjectionRow`, `CoverPolicy`, `CoverQuote`, `MarketScenario`, `BaselinePrice`, `StressTestResult`, `MeetingReport`, `Parameter` |
| `service` | business services used by managers | `ClientRoleService`, `ClientOverviewService`, `SessionScopeService`, `MovementImportService`, `ProjectionService`, `PeerSimulationService`, `CoverRatioService`, `CoverQuoteService`, `ScenarioService`, `StressTestService`, `ReportPayloadService`, `ParameterService` |
| `utils` | **calculations** (pure Kotlin, no Spring, KDoc + `@docs <calculation>`) and helpers | `RoleClassifier` (client_role_classification), `ProjectionAggregator` (monthly_projection), `CoverRatioCalculator` (cover_ratio), `ScenarioPricePath` (scenario_price_path), `StressTestCalculator` (stress_test_monthly), `PeerBenchmark` (peer_benchmark_simulation), `MonthGrid`, `Rounding` |
| `validator` | request validation | `MovementInputValidator`, `ScenarioValidator`, `ParameterValidator`, `RoleOverrideValidator` |

Every manager file starts with a KDoc block (`/** ... @docs <ID> */`) directly above `@Service class XxxManager(...)`.
Controllers are `@RestController class XxxController(...) : XxxApi` and implement `override fun <operationId>(...)` **without**
mapping annotations (they are on the generated interface). The API index is produced from `openapi/openapi_harbor.yaml` + `override fun` lookup.
Calculations live in `utils/` with a unit test in `harbor-core/src/test/kotlin/com/acme/harbor/utils/` whose cases are the **worked examples**
quoted in `docs-repo/domain/calculations/*.md`. Business context of a class = its name prefix (`Product1*`, `Stress*`, ...),
mapped in `docs-repo/contexts.yml` (contexts: clients, meetings, imports, product1, product2, cover, market, stress, reports, admin, and the FE-only presentation).

### 3.1 Kafka topics (`const val TOPIC` in the companion object of each listener and publisher in `harbor-core/.../event/`)

| Schema (`kafka-client/src/main/resources`) | Topic | Producer (`event/`) | Consumers (`event/`) |
|---|---|---|---|
| `avro/MovementsLoaded.avsc` | `harbor.imports.movements-loaded` | `MovementsLoadedPublisher` | `Product1ProjectionRefreshListener`, `Product2ProjectionRefreshListener` |
| `json_market-data/PricesUpdated.json` | `harbor.market.prices-updated` | external (market-data) | `MarketPricesListener` |
| `avro/SessionClosed.avsc` | `harbor.meetings.session-closed` | `SessionEventsPublisher` | `ReportSessionClosedListener`, `ClientRoleSessionClosedListener` |
| `avro/ReportRenderRequested.avsc` | `harbor.reports.render-requested` | `ReportRenderRequester` | external (document-service) |
| `json_document-service/ReportRendered.json` | `harbor.reports.rendered` | external (document-service) | `ReportRenderedListener` |

Producers call `producer.send(TOPIC, key, payload)`; consumers use `@KafkaListener(topics = [TOPIC], groupId = "${harbor.kafka.groups.<context>}")`.
Event payload classes, generated at build from the schemas (`com.acme.harbor.kafka.events[.<service>]`): `MovementsLoaded(batchId, clientIds, periodFrom, periodTo)`, `PricesUpdated(productGroup, corridor, asOf)`,
`SessionClosed(sessionId, clientId, productGroup, kind, roleOverride?)`, `ReportRenderRequested(sessionId, payloadRef, template)`, `ReportRendered(sessionId, pdfPath)`.
AsyncAPI description: `harbor-core/src/main/resources/openapi/harbor-events.yaml`.

### 3.2 Database (Flyway, `harbor-core/src/main/resources/db/migration`)

| Migration | Tables |
|---|---|
| `V1__clients.sql` | `client_profile(id uuid PK, external_ref, name, country, segment, created_at)`, `client_role(client_id FK, product_group, role, source, reason, decided_at)` |
| `V2__meetings.sql` | `meeting_session(id uuid PK, client_id FK, product_group, kind, representative_id, status, started_at, closed_at, role_override, role_override_reason, parameter_snapshot jsonb)`, `session_client_config(session_id FK, horizon_months, price_basis, cover_preference)` |
| `V3__movements.sql` | `import_batch(id, source_file, received_at, rows_total, rows_rejected, status)`, `goods_movement(id, client_id FK, batch_id FK, product_group, sub_product, city, transport_mode, direction, period date, quantity numeric, unit_price numeric, price_basis)`, `movement_monthly(client_id, product_group, sub_product, city, transport_mode, direction, period, quantity, value)` |
| `V4__session_inputs.sql` | `session_movement_input(id, session_id FK, period, sub_product, city, transport_mode, direction, quantity, unit_price)`, `session_peer_simulation(id, session_id FK, peer_segment, scaling_factor, generated_at)` |
| `V5__projection.sql` | `projection_by_subproduct(session_id FK, period, sub_product, quantity, value, landed_cost, cumulative_value)`, `projection_by_dimension(session_id, period, dimension_kind, dimension_value, quantity, value, landed_cost, cumulative_value)`, `projection_by_direction(session_id, period, direction, quantity, value, landed_cost, cumulative_value)`, `projection_summary(session_id, period, total_quantity, total_value, total_landed_cost, cover_ratio, cumulative_value)` |
| `V6__cover.sql` | `cover_policy(id, client_id FK, product_group, sub_product, covered_share numeric, premium_rate numeric, valid_from, valid_to)`, `cover_quote(id, session_id FK, requested_at, uncovered_value, premium, provider_ref)` |
| `V7__market_stress.sql` | `market_scenario(id, session_id FK, name, kind, shocks jsonb, created_by, created_at)`, `baseline_price(product_group, corridor, period, price, transport_price, as_of)`, `stress_test_result(session_id FK, scenario_id FK, period, dimension_value, exposure, transport_cost_delta, cumulative_exposure)` |
| `V8__reports.sql` | `meeting_report(session_id PK FK, payload jsonb, pdf_path, status, rendered_at)` |
| `V9__parameters.sql` | `parameter_set(id, key, scope_product_group, scope_country, scope_value, value numeric, valid_from, updated_by, updated_at)` + `ALTER TABLE meeting_session ADD COLUMN report_requested_at timestamp` |

### 3.3 REST API (`harbor-core/src/main/resources/openapi/openapi_harbor.yaml`, server base `/api/v1`)

| operationId | Method + path | Context | Notes |
|---|---|---|---|
| `searchClients` | `GET /clients?q=` | clients | proxies client-registry, merges local profile |
| `getClient` | `GET /clients/{clientId}` | clients | |
| `getClientOverview` | `GET /clients/{clientId}/overview` | clients | per product group: last-12-month volume, value, role, cover ratio, open sessions, sparkline data |
| `getClientRole` | `GET /clients/{clientId}/role?productGroup=` | clients | algorithm result + manual history |
| `createSession` | `POST /clients/{clientId}/sessions` | meetings | body `{productGroup, kind}` -> `201 {sessionId}` |
| `listSessions` | `GET /sessions?clientId=&status=&kind=` | meetings | Meetings page |
| `getSession` | `GET /sessions/{sessionId}` | meetings | |
| `closeSession` | `POST /sessions/{sessionId}/close` | meetings | emits session-closed |
| `setRoleOverride` | `PUT /sessions/{sessionId}/role` | meetings | body `{role, reason}` |
| `getProduct1Overview` | `GET /session/product1/overview?city=` | product1 | header `X-Harbor-Session` required; four tables + cover chart series |
| `putProduct1Movements` | `PUT /session/product1/movements` | product1 | modelled movements per month (modal 1) |
| `postProduct1PeerSimulation` | `POST /session/product1/peer-simulation` | product1 | modal 2 |
| `getProduct1Projection` | `GET /session/product1/projection` | product1 | the four tables |
| `getProduct2Overview` | `GET /session/product2/overview?transportMode=` | product2 | |
| `putProduct2Movements` | `PUT /session/product2/movements` | product2 | |
| `postProduct2PeerSimulation` | `POST /session/product2/peer-simulation` | product2 | |
| `getProduct2Projection` | `GET /session/product2/projection` | product2 | |
| `getCoverSummary` | `GET /session/cover/summary` | cover | cover ratio per month per sub-product |
| `requestCoverQuote` | `POST /session/cover/quotes` | cover | calls cover-provider |
| `listCoverPolicies` | `GET /clients/{clientId}/cover-policies` | cover | |
| `listScenarios` | `GET /session/scenarios` | market | |
| `createScenario` | `POST /session/scenarios` | market | |
| `updateScenario` | `PUT /session/scenarios/{scenarioId}` | market | |
| `deleteScenario` | `DELETE /session/scenarios/{scenarioId}` | market | |
| `getBaselinePrices` | `GET /session/market/baseline` | market | from `baseline_price` (fed by market-data) |
| `runStressTest` | `POST /session/stress-test` | stress | computes all scenarios |
| `getStressTest` | `GET /session/stress-test?dimension=` | stress | `dimension = CITY | TRANSPORT_MODE` |
| `getReport` | `GET /sessions/{sessionId}/report` | reports | JSON payload |
| `downloadReportPdf` | `GET /sessions/{sessionId}/report.pdf` | reports | `application/pdf` |
| `regenerateReport` | `POST /sessions/{sessionId}/report` | reports | |
| `listParameters` | `GET /admin/parameters?productGroup=` | admin | |
| `upsertParameter` | `PUT /admin/parameters/{key}` | admin | |
| `listImportBatches` | `GET /admin/imports` | admin | |
| `triggerImport` | `POST /admin/imports/run` | admin | |

External contracts (`harbor-core/src/main/resources/api/`): `client-registry.yaml` (`GET /registry/clients?q`, `GET /registry/clients/{ref}`),
`market-data.yaml` (`GET /prices/{productGroup}/{corridor}?from&to`, `GET /transport-prices/{productGroup}/{corridor}`),
`cover-provider.yaml` (`POST /quotes`), `document-service.yaml` (`POST /render`, `GET /documents/{id}`), `file-exchange.yaml` (`GET /files?since`, `GET /files/{id}/content`).

### 3.4 Parameters (`parameter_set.key`)

`role.min_volume` (100), `role.importer_threshold` (0.65), `role.exporter_threshold` (0.35), `tariff.rate` (per product group + country),
`handling.cost` (per city), `transport.cost` (per transport mode), `cover.default_premium_rate` (0.012), `projection.horizon_months_default` (24),
`stress.rounding_scale` (2), `peer.scaling_default` (1.0).

## 4. Calculations (`docs-repo/domain/calculations/<name>.md`, code in `backend/harbor-core/src/main/kotlin/com/acme/harbor/utils/`)

| Name | Class | Definition (authoritative in code; docs quote worked examples from the unit test) |
|---|---|---|
| `client_role_classification` | `RoleClassifier` | last 12 full months: `inbound = sum(qty, direction=IN)`, `outbound = sum(qty, direction=OUT)`; if `inbound+outbound < role.min_volume` -> `UNDETERMINED`; `share = inbound/(inbound+outbound)`; `share >= 0.65 -> IMPORTER`, `share <= 0.35 -> EXPORTER`, else `MIXED` |
| `monthly_projection` | `ProjectionAggregator` | per month `m` in horizon, per row: `value = qty * unitPrice * priceIndex(m)`; `landedCost = value * (1 + tariffRate(productGroup, country)) + qty * handlingCost(city) + qty * transportCost(mode)`; grouped into the four tables; `cumulative_value` = running sum over months; rounding `HALF_EVEN`, scale 2 |
| `cover_ratio` | `CoverRatioCalculator` | `coveredValue(m) = sum(value * coveredShare of matching policy valid in m)`; `coverRatio(m) = coveredValue / totalValue` (0 when total = 0), scale 4 |
| `scenario_price_path` | `ScenarioPricePath` | `price_s(m) = baseline(m) * prod(1 + shock.priceChangePct)` over shocks with `fromMonth <= m`; same for `transportPrice` with `transportChangePct` |
| `stress_test_monthly` | `StressTestCalculator` | per scenario, month, dimension value: `sign = +1 (IMPORTER) / -1 (EXPORTER) / 0 (MIXED -> use net direction qty)`; `exposure = uncoveredQty * (price_s(m) - baseline(m)) * sign`; `transportCostDelta = qty * (transport_s(m) - transportBaseline(m))`; `cumulativeExposure` running sum of `exposure + transportCostDelta` |
| `peer_benchmark_simulation` | `PeerBenchmark` | peer series = segment median monthly qty * `scalingFactor`; no spec yet (backlog) |

## 5. Frontend (`frontend/src`)

```
src/api/client.ts                  openapi-fetch client `api` (baseUrl /api/v1) + `sessionHeader()` typed helper (X-Harbor-Session from sessionStore, required by the contract on every /session/** call)
src/api/generated/schema.d.ts      openapi-typescript output (committed, trimmed to the paths above)
src/api/sessionStore.ts
src/app/routes.tsx, src/app/AdminRoutes.tsx, src/app/App.tsx, src/app/RootLayout.tsx (sidebar), src/app/SessionLayout.tsx (session steps, "Open client screen"), src/app/PresentationLayout.tsx (client window: no sidebar)
src/shared/ui/DataTable.tsx, src/shared/ui/Modal.tsx   shared component library (mapped by scripts/docs/gen-components.py)
src/shared/charts/LineChart.tsx, src/shared/charts/StackedBars.tsx
src/shared/utils/months.ts (month grid helpers), src/shared/utils/format.ts
src/features/<feature>/index.ts (barrel with /** @module ... @docs <ID> */), <feature>.types.ts, api/use*.ts hooks, ui/*.tsx
```

| Feature (= BE module name) | Routes (object routes in `src/app/routes.tsx`) | Hooks (`api/`) | UI |
|---|---|---|---|
| `clients` | `/clients` -> `ClientSearchPage`; `/clients/:clientId` -> `ClientOverviewPage` (product group cards with key indicators, sparkline charts, client info, "Start meeting" / "Prepare" buttons) | `useClientSearch`, `useClientOverview`, `useClientRole` | `ClientSearchPage.tsx`, `ClientOverviewPage.tsx`, `ProductGroupCard.tsx`, `ClientInfoPanel.tsx` |
| `meetings` | `/meetings` -> redirect; `/meetings/client` -> `ClientMeetingsPage` (kind CLIENT); `/meetings/preparation` -> `PreparationSessionsPage` (kind PREPARATION); `/session/:sessionId/summary` -> `SessionSummaryPage` | `useSessions`, `useCreateSession`, `useCloseSession` (publishes `session-closed`), `useRoleOverride` | `MeetingsListPage.tsx` (shared list), `ClientMeetingsPage.tsx`, `PreparationSessionsPage.tsx`, `SessionSummaryPage.tsx`, `RoleOverrideDialog.tsx` |
| `product1` | `/session/:sessionId/product1` -> `Product1OverviewPage` | `useProduct1Overview`, `useProduct1Movements`, `usePeerSimulation1` | `Product1OverviewPage.tsx`, `ProjectionTables.tsx` (4 tables), `CoverRatioChart.tsx`, `MovementInputModal.tsx`, `PeerSimulationModal.tsx`, `CitySelector.tsx` |
| `product2` | `/session/:sessionId/product2` -> `Product2OverviewPage` | `useProduct2Overview`, `useProduct2Movements`, `usePeerSimulation2` | `Product2OverviewPage.tsx`, `TransportModeSelector.tsx` (reuses product1 tables/modals via `shared`) |
| `market` | `/session/:sessionId/scenarios` -> `ScenariosPage` | `useScenarios`, `useBaselinePrices` | `ScenariosPage.tsx`, `ScenarioEditor.tsx`, `ShockRow.tsx` |
| `stress` | `/session/:sessionId/stress-test` -> `StressTestPage` | `useStressTest`, `useRunStressTest` | `StressTestPage.tsx`, `StressTable.tsx`, `TransportPriceChart.tsx`, `DimensionToggle.tsx` |
| `reports` | (used from meetings list) | `useReport`, `useDownloadReportPdf` | `DownloadPdfButton.tsx`, `ReportPreview.tsx` |
| `admin` | `/admin/parameters` -> `ParametersPage`; `/admin/imports` -> `ImportsPage` (in `AdminRoutes.tsx`) | `useParameters`, `useImportBatches` | `ParametersPage.tsx`, `ParameterRow.tsx`, `ImportsPage.tsx` |
| `cover` | (widgets embedded in product pages) | `useCoverSummary`, `useCoverQuote` | `CoverQuotePanel.tsx` |
| `presentation` (FE-only context `PRS`) | `/present/:sessionId` -> `PresentationLayout` -> `PresentationPage` (client-facing second window, no sidebar, no controls; mirrors product1 / product2 / scenarios / stress-test; "Waiting for the representative" otherwise) | `usePresentationPublisher`, `usePresentationSubscriber` (`channel.ts`, the only `BroadcastChannel` `harbor.session.<sessionId>`; messages `route`, `view`, `session-closed`, `hello` replay) | `PresentationPage.tsx`, `ProductMirror.tsx`, `ScenariosMirror.tsx`, `StressMirror.tsx` |

API calls in hooks use the generated client: `api.GET('/clients/{clientId}/overview', { params: { path: { clientId } } })` - the literal path string
is what the FE codebase map and the graph join on.

## 6. Docs repo (`docs-repo/`)

Bounded contexts and spec ID prefixes (one per BE class-name prefix group in `contexts.yml` / FE feature): `clients=CLI`, `meetings=SES`, `imports=IMP`, `product1=P1`,
`product2=P2`, `cover=COV`, `market=MKT`, `stress=STR`, `reports=RPT`, `admin=ADM`.

Deliberate state of the sample content (so the agents have real work to do):

| Artefact | State |
|---|---|
| `features/clients/CLI-001.md` Client search, overview and role classification | complete, `stable`, human-verified |
| `features/meetings/SES-001.md` Meeting session lifecycle and session header | complete, `stable` |
| `features/product1/P1-001.md` Product 1 overview: four projection tables, cover charts, movement and peer modals | complete, `stable` |
| `features/stress/STR-001.md` Stress test per scenario and dimension | complete, `draft` (awaiting verification against code) |
| `features/market/MKT-001.md` Market scenarios | draft skeleton with open questions |
| `features/reports/RPT-001.md` Meeting report and PDF | draft skeleton |
| `P2-001`, `COV-001`, `IMP-001`, `ADM-001` | **missing on purpose** -> appear as `code only` in `generated/graph/REPO_MAP.md` spec coverage (backlog for `/spec-skeleton-from-graph`) |
| `domain/calculations/client_role_classification.md`, `monthly_projection.md`, `stress_test_monthly.md` | complete with worked examples from the unit tests |
| `domain/calculations/cover_ratio.md`, `scenario_price_path.md` | draft |
| `peer_benchmark_simulation` | missing on purpose |
| `confluence-import/HARBOR/stress-test-calculation.md` | imported page, **deliberately outdated** (threshold 0.5, no transport delta) - the migrator/calc audit must detect the conflict |
| `confluence-import/HARBOR/meeting-flow.md`, `product1-overview-tables.md` | imported pages, partly correct |
| `work-items/P1-001.yml`, `test-design/features/STR-001.feature` + fixture | worked examples |
| `generated/be`, `generated/fe` | copies of `backend/docs/_generated`, `frontend/docs/_generated` (what CI publishes) |
| `generated/openapi/backend.yaml`, `generated/openapi/external/*.yaml`, `generated/asyncapi/backend.yaml` | copies of the contracts |
| `generated/graph/` | built by `scripts/gen-graph.py` |

Glossary terms (English canonical; `Term (cs)` holds the Czech term, `aliases` other-language synonyms): client, representative, meeting, session, preparation session,
product group, sub-product, corridor, price basis, importer, exporter, mixed, role override, actual movement, modelled movement, peer simulation,
projection, landed cost, cover, cover ratio, cover share, premium rate, baseline curve, scenario, shock, stress test, exposure, transport price,
dimension (city / transport mode), parameter set, import batch, report payload.
