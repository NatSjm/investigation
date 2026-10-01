# Graph neighbourhood -> Jira subtasks / test scope

Deterministic mapping used by `analyst` and `test-designer`. Start from `spec:<ID>` at depth 2
(`graph-query.ps1 -Node spec:<ID> -Depth 2` or `#impact spec:<ID>`).

| Node kind in radius | Jira subtask | Test layer tag | Fixture |
|---|---|---|---|
| `class:*Controller`, `endpoint:*` | `[BE] <METHOD path>: request/response + validation` | `@api` | request/response JSON |
| `class:*Facade`, `class:*Service` | `[BE] <Facade>: orchestration change` | `@api` (via endpoint) | - |
| `class:*Calculator` | `[BE] <Calculator>: formula + unit tests with worked examples` | `@calc` | rows from `domain/calculations/<id>.md` Worked examples |
| `class:*Repository`, `table:*` | `[DB] migration V<n>__<table>_<change>.sql` + `[BE] entity/repo` | `@api` | table seed JSON/CSV (synthetic) |
| `topic:*` produced | `[INT] <topic>: schema version + producer` | `@kafka` | event payload JSON |
| `topic:*` consumed-by | `[INT] <topic>: consumer idempotency + retry` | `@kafka` | duplicate / out-of-order payloads |
| `feature:*`, `hook:*` | `[FE] <feature>: api hook + types mirror` | `@ui` | mocked endpoint responses |
| `component:*`, `route:*` | `[FE] <route>: screen behaviour` | `@ui` | - |
| `spec:*` other than the start | `[DOC] update <ID> (cross-impact)` | - | - |

Rules of thumb
- One subtask per node; merge nodes of the same kind in the same class file.
- Each subtask <= 1 day; if a `class:*` node has degree > 8 in the graph, split by edge type.
- Edges marked `(heuristic)` -> add a `questions[]` entry instead of a subtask.
- Nodes in other communities (`(-> other)` mark) -> `depends_on` between stories, not a subtask.
