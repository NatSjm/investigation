# Generated code maps

Read these before opening source. Each file is a few hundred tokens.
Contracts: `core/src/main/resources/openapi/harbor-api.yaml` (REST; FE client and BE interfaces are generated from it),
`core/src/main/resources/openapi/harbor-events.yaml` (Kafka), `core/src/main/resources/api/*.yaml` (external services).

- [codebase-map.md](codebase-map.md): modules, technical layers with their classes, resource folders
- [components.md](components.md): one row per class - layer, stereotype, injected dependencies, tables, @docs, file:line
- [api-index.md](api-index.md): REST operations from the contract (method, path, operationId, handler, file:line)
- [events.md](events.md): Kafka topics with producers/consumers
- [db-schema.md](db-schema.md): tables and columns from migrations, ER diagram
- [jobs.md](jobs.md): scheduled jobs with their cron triggers
- [docs-tags.md](docs-tags.md): spec ID (`@docs`) to code location
- [parameters.md](parameters.md): admin parameter catalogue - every `ParameterKey` with seeded defaults per scope, readers and validator
- [datasets.md](datasets.md): named synthetic datasets (local seeds, integration-test fixtures) with tables, row counts, loaders and a sample row
