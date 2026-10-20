# Context pack - section markers

`scripts/context-pack.py` writes these H2 headings in this order. Agents and prompts refer to them by name.

| Heading | Source | Truncation rank (1 = never) |
|---|---|---|
| `## Subject` | resolution of `--task`; frontmatter of the spec / calculation / flow, or the `contexts.yml` entry of a context; `index.md` badge logic | 1 |
| `## Spec` | `features/<ctx>/<ID>.md` body | 1 (reduced to key sections if > 200 lines) |
| `## Calculation` | `domain/calculations/<name>.md` (Purpose, Inputs, Outputs, Formula, Conventions, Worked examples, Audit, Open questions; never the code block) when the subject is a calculation | 1 |
| `## Flow` | `flows/<name>.md` body when the subject is a flow | 1 (reduced to key sections if > 200 lines) |
| `## Context overview` | when the subject is `context:<name>`: its specs (or "none yet" with the ID the first one gets), the flows it takes part in, endpoints with operationId and summary, tables owned, calculations implemented by its classes, Kafka topics produced / consumed, classes by layer, FE pages with routes, its rows of `architecture/integrations.md`, the lines of `architecture/overview.md` that mention it, proposed contracts tagged with it - the overview for placing new work in the context | 1 |
| `## Specs in the flow` | for a flow subject: every spec of its `specs[]` with Summary and the business rules the flow text cites (`P1-001 BR-8`, `BR-STR-001-3`) | 2 |
| `## Calculations` | `domain/calculations/<name>.md` for every `calculations[]` entry | 2 |
| `## Flows` | `flows/<name>.md` for every `flows[]` entry of the spec plus every flow whose `specs[]` names the ID (Purpose, Trigger, Participants, Steps, Invariants) | 3 |
| `## Graph neighbourhood` | `scripts/graph-query.py --node spec:<ID> --depth 2` (or `context:`/`feature:` for a community); for a flow `--files <its code_refs> --depth 1`; class detail from `generated/be/components.md` | 2 |
| `## Contracts` | `generated/openapi/backend.yaml` path blocks for `api[]`; `generated/asyncapi/backend.yaml` channel names for `events[]` (a flow's `channels[]`; when the backend has no AsyncAPI document, the line points at `generated/be/events.md` instead) | 4 |
| `## Data` | the page of every `tables[]` entry from `generated/be/db/schema/tables/<table>.md` (table comment, columns with comments, relations, constraints; first 60 lines), else the `generated/be/db-schema.md` section | 4 |
| `## Related work items and tests` | `work-items/<ID>.yml` (`summary:` lines), `test-design/features/<ID>.feature` (`Scenario` lines) | 3 |
| `## Legacy pages` | `confluence-import/**/*.md` containing the ID or 2+ title keywords; first 5 lines each | 5 |
| `## Sources and limits` | list of files read with `generated.at` where present; truncated sections; the reading rule | 1 |

Header line format: `# Context pack: <task> - <resolved subject> - <badge> - built <ISO>`.

## Several subjects, one pack

`--task` may be repeated (`--task P1-002 --task STR-001 --task flows/session-inputs-recalculation.md`). The pack
keeps the headings above; inside a per-subject section (`Subject`, `Spec`, `Calculation`, `Flow`, `Context overview`,
`Specs in the flow`) every subject gets a block headed `### <task> (<kind>: <path>)` with the body's own headings
demoted under it. Shared sections (`Calculations`, `Flows`, `Graph neighbourhood`, `Contracts`, `Data`, `Related`,
`Legacy pages`) list each calculation, flow, contract operation, table, work item or page once, whichever subject
brought it; a calculation or flow that is itself a subject is not repeated as a linked one; the Kafka line and the
dataset list are unions. Header: `# Context pack: <task 1> + <task 2> - <n> subjects - built <ISO>`; the first line of
`## Subject` says how many. There is no budget unless `--budget N` is given: the pack holds everything its subjects
need, each item bounded on its own (a spec reduced to key sections above 200 lines, a table page 60 lines, a legacy
page 5, a graph neighbourhood 80 per subject). With `--budget`, the lower-ranked sections go first and the footer
names them; add a subject rather than splitting a task into several packs.

## Subject resolution

| `--task` | Resolved as |
|---|---|
| `P1-001` (`<PREFIX>-<NNN>`) | spec; without a file: graph neighbourhood of `spec:<ID>` only |
| `stress_test_monthly` (a file under `domain/calculations/`) | calculation |
| `flows/<name>.md`, `flow:<name>`, `FLOW-<name>` | flow |
| `context:<name>` (a key of `contexts.yml`) | context (overview + graph neighbourhood of `context:<name>`, or of its first page for an FE-only context) |
| `topic:…`, `table:…`, `feature:…`, `class:…`, `endpoint:…`, … | graph node (neighbourhood only) |
| anything else | free text - a fallback: read `generated/catalogue.md` and name the subjects instead |

Free-text resolution: the words of the task (>= 4 characters, function words dropped) are scored against every spec,
calculation and flow - a hit in `title`, `aliases` or the id counts 2, in `description`, `tags` or `contexts` 1; a
glossary alias in the text (customer -> Client, lane -> Corridor) adds the term's words and gives the concepts the
glossary lists the term under a bonus, and is reported as `glossary:` in the Subject. The best match is packed, up to
three runners-up are listed under `candidates:`. It is single-subject by construction: a request about several
contexts needs the subjects named (`--task` per subject), which is what the catalogue is for.
