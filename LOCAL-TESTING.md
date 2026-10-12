# Local testing: run the apps, walk through them, and exercise the documentation tooling

Everything here is synthetic. Three clients come from the WireMock stub of the client registry, one movement file
from the file-exchange stub, baseline prices from the market-data stub. Paths are relative to `C:\projects\investigation`.

## 1. Prerequisites (already on this machine)

JDK 21, Docker Desktop, Node 24, PowerShell 7, and Maven unpacked (no install) at `C:\projects\tools\apache-maven-3.9.9`.
Nothing else. IntelliJ can replace the Maven command line (see "IntelliJ" below).

## 2. Start everything

```powershell
# 1. infrastructure: Postgres 16, Kafka (KRaft) with the five topics, WireMock with the five external services
docker compose -f backend\init_docker_compose\docker-compose.yml up -d
docker compose -f backend\init_docker_compose\docker-compose.yml ps        # all healthy, kafka-init exited 0

# 2. backend (first time: build; afterwards only the java line)
cd backend
C:\projects\tools\apache-maven-3.9.9\bin\mvn -B -DskipTests clean package   # ~2 min; `mvn -B test` runs the 27 unit tests
$env:HARBOR_CLIENT_REGISTRY_URL='http://localhost:8089'; $env:HARBOR_MARKET_DATA_URL='http://localhost:8089'
$env:HARBOR_COVER_PROVIDER_URL='http://localhost:8089'; $env:HARBOR_DOCUMENT_SERVICE_URL='http://localhost:8089'
$env:HARBOR_FILE_EXCHANGE_URL='http://localhost:8089'
java -jar core\target\core-1.0.0-SNAPSHOT.jar          # "Started HarborApplicationKt", Flyway applies V1..V9
cd ..

# 3. frontend
cd frontend
npm install                                             # first time
npm run generate:api                                    # types from ../backend/.../openapi/harbor-api.yaml
npm run dev                                             # http://localhost:5173, proxies /api -> 8080
```

Health: `http://localhost:8080/api/v1/actuator/health` returns `{"status":"UP"}`. WireMock admin: `http://localhost:8089/__admin/mappings`.

**IntelliJ instead of the java line.** Open `backend/pom.xml` as a Maven project (bundled Maven is fine, or point it at
`C:\projects\tools\apache-maven-3.9.9`), JDK 21, run the Maven phase `generate-sources` once so the OpenAPI
interfaces exist under `core/target/generated-sources/openapi/*/src/main/kotlin` (mark them as generated source
roots if they stay red), then a run configuration with main class `harbor.HarborApplicationKt`, module `core`, and
the five `HARBOR_*_URL` environment variables above. Unit tests: right-click `core/src/test/kotlin`.

## 3. Load synthetic data (one call)

The tables are empty after the first start. The daily import job also runs on a schedule, but trigger it by hand:

```powershell
curl -X POST http://localhost:8080/api/v1/admin/imports/run
```

This pulls `movements_2026-10-08.tsv` from the file-exchange stub (three rows: two for client CR-1001 on Product 1,
one for CR-2001 on Product 2), parses it, stores `goods_movement` and publishes `harbor.imports.movements-loaded`.
The Admin > Imports page shows the batch (3 rows, DONE). Re-running reports "(no new files)".

The client cards (12-month value, role) read `movement_monthly`, which the **monthly snapshot job** fills on the 1st
of each month at 03:00; there is no manual trigger, so locally the cards stay at zero and the role at UNDETERMINED
("total volume below role.min_volume"). For numbers in the projection tables use **Model movements** inside a session
(step 3 of the ten-minute test) or `PUT /session/product1/movements`; both are stored per session and recompute at once.

Clients exist in the stub registry: **Aldmoor Trading Co** (CR-1001, Product 1), **Carrow Goods Ltd** (CR-1002),
**Meridia Freight Works** (CR-2001, Product 2). A client gets a local profile the first time a search returns it.

## 4. The application, screen by screen

Open `http://localhost:5173`. The sidebar has Clients, Client meetings, Preparation sessions, Parameters, Imports.
No styling framework is used, so pages are plain HTML; the structure is what matters.

### Clients (`/clients`)
Search box (two characters minimum, e.g. `al`). Results: name, registry reference, country, segment. Click a name.

### Client overview (`/clients/:clientId`)
Heading with the client name. One **product group card** per group (Product 1, Product 2): the key indicators
(12-month value, movement count, role with its reason: IMPORTER / EXPORTER / MIXED / UNDETERMINED, computed by the
role classification calculation), a 12-month sparkline, and two buttons:
- **Start meeting** creates a CLIENT session for that product group and opens it.
- **Prepare** creates a PREPARATION session (a dry run without the client).
Below: **Client information** panel and a link "All meetings of this client".

### A session (`/session/:sessionId/...`)
The session layout shows client name, product group, kind and status, the button **Open client screen**, and the
four steps as links: **1. Overview, 2. Scenarios, 3. Stress test, 4. Summary**. Every request from here carries the
header `X-Harbor-Session`; without it the backend answers 428.

**Overview (Product 1)**: city hub selector (All, Aldmoor, Brightwater, Carrow, Dunmere); two buttons:
- **Model movements** opens a modal to enter modelled monthly movements (period, sub-product, city, direction,
  quantity, unit price); **Save and recompute** stores them for the session and recomputes the projection.
- **Peer simulation** opens a modal that models the movements of similar clients (peer segment, scaling factor).
Then the four cumulative tables: by sub-product, by city, by direction, and the summary (quantity, value, landed
cost, cover ratio, cumulative value per month over the horizon), the cover ratio chart and the **Cover** panel
with **Request quote for uncovered part** (goes to the cover-provider stub).
With no movements the tables are empty and the summary shows zeros; after the import or after modelling movements
they fill.

**Overview (Product 2)**: the same with a transport mode selector (ROAD, RAIL, SEA, AIR) instead of cities.

**Scenarios**: baseline prices from the market-data stub (price and transport price per month), the scenario
list, and a form to **Create scenario** (name, kind REPRESENTATIVE or CLIENT, shocks such as "transport +15% from
month 6"). Scenarios are per session; edit and delete inline.

**Stress test**: **Run stress test** computes, for every scenario, the monthly exposure table by city (Product 1)
or by transport mode (Product 2), using the dimension toggle **By city / By transport mode**, plus the transport
price chart per scenario. Without scenarios the page says so.

**Summary**: session facts, role override dialog (**Save changes**, with a reason field), report preview and
**Close session**. Closing stores the report payload, publishes `harbor.meetings.session-closed`, and returns to the
list of that session kind. The PDF is rendered by the document-service stub; **Download PDF** on the list pages
works for closed sessions.

### Client screen (`/present/:sessionId`)
Opened by **Open client screen** in a second window. No sidebar, no step links, no buttons. It shows the client
name and product group and mirrors what the representative is on: the four tables and cover chart for the product
step, the scenario list, or the stress tables and chart for the chosen dimension. Before any navigation it says
"Waiting for the representative"; after the session is closed, "Session closed". Try: put both windows side by
side, switch steps and change the city selector in the main window, watch the client window follow. Open the
client window late and it still catches up (the `hello` replay).

### Client meetings (`/meetings/client`) and Preparation sessions (`/meetings/preparation`)
Two lists of the same shape, filtered by session kind, with a status filter (All / Open / Closed), client, product
group, start and close times, **Continue** for open sessions and **Download PDF** for closed ones. `/meetings` redirects
to the client list.

### Admin
**Parameters** (`/admin/parameters`): the parameter sets used by the calculations (tariff rates, handling and
transport costs, role thresholds), editable inline per product group; seeded by migration V9.
**Imports** (`/admin/imports`): import batches with file name, rows total and rejected, status, and **Run import now**.

## 5. A ten-minute end-to-end test

1. Search `al`, open Aldmoor Trading Co: two product group cards (role UNDETERMINED with its reason, zero 12-month figures until the monthly snapshot runs), Client information, open sessions.
2. **Start meeting** on Product 1. The URL is `/session/<id>/product1`; the summary table has numbers.
3. **Model movements**: add a row (next month, P1-STD, Aldmoor, IN, 100, 12.50), **Save and recompute**; the tables change.
4. **Open client screen**; arrange the windows; change the city selector; the client window follows.
5. Scenarios: **Create scenario** "Transport +15% from month 6", kind REPRESENTATIVE.
6. Stress test: **Run stress test**; one table per scenario; toggle the dimension; the client window shows the same.
7. Summary: **Close session**. The client window says "Session closed"; the Client meetings list shows the session as CLOSED with **Download PDF**.
8. Preparation sessions: **Prepare** on a client creates one; it appears in the second list only.

API-level checks of the same flow, if you prefer curl:
```powershell
curl "http://localhost:8080/api/v1/clients?q=ald"
curl -X POST http://localhost:8080/api/v1/clients/<clientId>/sessions -H "Content-Type: application/json" -d '{"productGroup":"product1","kind":"CLIENT"}'
curl -H "X-Harbor-Session: <sessionId>" http://localhost:8080/api/v1/session/product1/overview
curl http://localhost:8080/api/v1/session/product1/overview            # -> 428 Precondition Required
curl "http://localhost:8080/api/v1/clients"                             # -> 400 (q missing)
```

## 6. Unit tests and type checks

```powershell
cd backend;  C:\projects\tools\apache-maven-3.9.9\bin\mvn -B test       # 27 tests: calculators + scenario validator
cd frontend; npm run typecheck; npm test; npm run build                 # 0 errors, 18 tests, vite build
```

## 7. The documentation tooling against the running state

```powershell
.\backend\scripts\docs\gen-all.ps1 -Root .\backend -Check               # maps match the code
.\frontend\scripts\docs\gen-all.ps1 -Root .\frontend -Check
cd docs-repo
.\scripts\publish-local.ps1; .\scripts\gen-graph.ps1; .\scripts\build-index.ps1
.\scripts\okf-validate.ps1 -Strict; .\scripts\validate-frontmatter.ps1; .\scripts\gen-graph.ps1 -Check
.\scripts\context-pack.ps1 -Task PRS-001 -Print                          # the pack of the presentation spec
.\scripts\graph-query.ps1 -Node "channel:harbor.session.{*}" -Depth 1    # who publishes / subscribes
.\scripts\migration-status.ps1 -Scope all                                # runs still due per context
```

In VS Code with Copilot (workspace root `docs-repo`): `/context-pack PRS-001`, `@analyst /jira-from-spec PRS-001`
(stories labelled needs-spec-review because the spec is a draft), `/audit-calculation stress_test_monthly`,
`/spec-skeleton-from-graph product2 P2-001`, `/migration-plan all`.

## 8. Stop

```powershell
taskkill /IM java.exe /F                                                 # backend
docker compose -f backend\init_docker_compose\docker-compose.yml down    # add -v to drop the database volume
```
The Vite server stops with Ctrl+C in its terminal.

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `no main manifest attribute` when starting the jar | `package` ran without `clean`, the jar was not repackaged | `mvn -B -DskipTests clean package` |
| Port 8080 in use | an earlier backend still running | `taskkill /IM java.exe /F` |
| Kafka container does not start | old image tag | the compose file uses `apache/kafka:3.7.2` |
| 428 on `/session/**` | header missing | the frontend adds it from the session store; in curl pass `X-Harbor-Session` |
| Tables stay empty | no movements yet | run the import (section 3) or model movements in the session |
| Import batch FAILED and never retried | a batch row with that file name exists | `delete from import_batch where status='FAILED'` in Postgres, run again |
| Search results change ids | client search is a write transaction now; restart the backend if you see this | rebuild + restart |
| `generated/` edits rejected | the Copilot hook protects CI-owned files | change the generator or the code |
