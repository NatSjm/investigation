# init_docker_compose - local environment

Everything harbor-backend needs to run on a developer machine. All data is synthetic.

| Service | Port | Purpose |
|---|---|---|
| `postgres` | 5432 | database `harbor` (user / password `harbor`), plus `harbor_test`; schema created by Flyway on application start |
| `kafka` | 9092 | single-node Kafka (KRaft); `kafka-init` creates the five Harbor topics and their `.DLT` topics |
| `wiremock` | 8089 | stubs of the five external services, one file per service in `wiremock/mappings/` |

## Start / stop

```
docker compose -f init_docker_compose/docker-compose.yml up -d
docker compose -f init_docker_compose/docker-compose.yml down          # keep data
docker compose -f init_docker_compose/docker-compose.yml down -v       # drop the database volume
```

Then run the application from the repository root (defaults in `core/src/main/resources/application.yml`
already point to localhost):

```
$env:HARBOR_CLIENT_REGISTRY_URL  = "http://localhost:8089"
$env:HARBOR_MARKET_DATA_URL      = "http://localhost:8089"
$env:HARBOR_COVER_PROVIDER_URL   = "http://localhost:8089"
$env:HARBOR_DOCUMENT_SERVICE_URL = "http://localhost:8089"
$env:HARBOR_FILE_EXCHANGE_URL    = "http://localhost:8089"
mvn -q -pl core -am spring-boot:run
```

## Files

- `docker-compose.yml` - the three services and the topic initialiser.
- `init-db.sql` - executed once on the first start of the postgres container (extension `pgcrypto`, UTC time zone,
  database `harbor_test`). Tables come from `core/src/main/resources/db/migration` (Flyway), never from here.
- Synthetic data: `scripts/db/seed-local.ps1` loads the named datasets of `scripts/db/seed/*.sql` through `psql` in the container (`-Fixtures` adds the integration-test datasets; `-Database harbor_test` targets the test database). Catalogue: `docs/_generated/datasets.md`.
- `wiremock/mappings/*.json` - one file per external contract in `core/src/main/resources/api/`:

| File | Contract | Stubs |
|---|---|---|
| `client-registry.json` | `client-registry.yaml` | `GET /registry/clients?q=`, `GET /registry/clients/{ref}` |
| `market-data.json` | `market-data.yaml` | `GET /prices/{productGroup}/{corridor}`, `GET /transport-prices/{productGroup}/{corridor}` |
| `cover-provider.json` | `cover-provider.yaml` | `POST /quotes` (premium = uncovered value x 0.012) |
| `document-service.json` | `document-service.yaml` | `POST /render`, `GET /documents/{id}` (placeholder PDF) |
| `file-exchange.json` | `file-exchange.yaml` | `GET /files?since=`, `GET /files/{id}/content` (three tab-separated movement rows) |

The paths of the five services do not overlap, so one WireMock instance serves all of them.

## Kafka events from the external side

market-data and document-service are not simulated on Kafka. To exercise the listeners publish a message by hand, e.g.

```
docker compose -f init_docker_compose/docker-compose.yml exec kafka kafka-console-producer.sh `
  --bootstrap-server localhost:9092 --topic harbor.market.prices-updated
{"productGroup":"product1","corridor":"VLD-NRL","asOf":"2026-10-01T06:00:00Z"}
```
