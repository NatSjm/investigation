# Graph neighbourhood -> Jira subtasks / test scope

Deterministic mapping used by `analyst` and `test-designer`. Start from `spec:<ID>` at depth 2
(the **Graph neighbourhood** section of the context pack, `graph-query.py --node spec:<ID> --depth 2` or `#impact spec:<ID>`).

| Node kind in radius | Jira subtask | Test layer tag | Fixture |
|---|---|---|---|
| `class:*Controller`, `endpoint:*` | `[BE] <operationId> (<METHOD path>): contract change in harbor-api.yaml + regenerate + implement override fun` | `@api` | request/response JSON per `components/schemas` |
| `class:*Manager`, `class:*Service` | `[BE] <Manager>: orchestration change` | `@api` (via endpoint) | - |
| `class:*Validator`, `class:*Mapper` (not graph nodes - found via `generated/be/components.md` deps of the manager/service) | `[BE] <Class>: validation / mapping change` | `@api` (via endpoint) | invalid / edge-case request JSON |
| `class:*Calculator`, `class:*Aggregator`, `class:*Classifier` (layer `utils/`) | `[BE] <Class>: formula + unit test cases (worked examples)` + `[DOC] domain/calculations/<id>.md` | `@calc` | rows from the calculation's Worked examples |
| `class:*Dao`, `table:*` | `[DB] migration V<n>__<table>_<change>.sql` + `[BE] model/dao` | `@api` | table seed JSON/CSV (synthetic) |
| `class:*Job` | `[BE] <Job>: schedule / batch behaviour` | `@api` (trigger via admin endpoint) | import file sample |
| `topic:*` produced | `[INT] <topic>: payload version + producer` | `@kafka` | event payload JSON |
| `topic:*` consumed-by | `[INT] <topic>: consumer idempotency + retry` | `@kafka` | duplicate / out-of-order payloads |
| external contract (`generated/openapi/external/*.yaml`) | `[INT] <service>: contract change + client regeneration` | `@api` (mocked service) | mocked responses |
| `feature:*`, `hook:*` | `[FE] <feature>: hook + regenerated client types (`npm run generate:api`)` | `@ui` | mocked endpoint responses |
| `channel:*` (BroadcastChannel) | `[FE] <channel>: message type + publisher + subscriber (both windows)` | `@ui` | message payload JSON per type |
| `component:*` in `shared-ui` | `[FE] <Component>: library change (props), then the features that render it` | `@ui` | - |
| `component:*`, `route:*` | `[FE] <route>: screen behaviour` | `@ui` | - |
| `spec:*` other than the start | `[DOC] update <ID> (cross-impact)` | - | - |

Rules of thumb
- `depends-on` edges -> subtasks along the injection chain controller -> manager -> service -> dao / utils / client;
  stop at the first class the change does not reach.
- One subtask per node; merge nodes of the same kind in the same class file.
- Each subtask <= 1 day; if a `class:*` node has degree > 8 in the graph, split by edge type.
- Edges marked `(heuristic)` -> add a `questions[]` entry instead of a subtask.
- Nodes in other communities (`(-> other)` mark) -> `depends_on` between stories, not a subtask.
