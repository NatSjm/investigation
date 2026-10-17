# Context pack - section markers

`scripts/context-pack.py` writes these H2 headings in this order. Agents and prompts refer to them by name.

| Heading | Source | Truncation rank (1 = never) |
|---|---|---|
| `## Subject` | resolution of `--task`; frontmatter of the spec / calculation; `index.md` badge logic | 1 |
| `## Spec` | `features/<ctx>/<ID>.md` body | 1 (reduced to key sections if > 200 lines) |
| `## Calculations` | `domain/calculations/<name>.md` for every `calculations[]` entry | 2 |
| `## Flows` | `flows/<name>.md` for every `flows[]` entry of the spec plus every flow whose `specs[]` names the ID (Purpose, Trigger, Participants, Steps, Invariants) | 3 |
| `## Graph neighbourhood` | `scripts/graph-query.py --node spec:<ID> --depth 2` (or `context:`/`feature:` for a community); class detail from `generated/be/components.md` | 2 |
| `## Contracts` | `generated/openapi/backend.yaml` path blocks for `api[]`; `generated/asyncapi/backend.yaml` channel names for `events[]` (when the backend has no AsyncAPI document, the line points at `generated/be/events.md` instead) | 4 |
| `## Data` | the page of every `tables[]` entry from `generated/be/db/schema/tables/<table>.md` (table comment, columns with comments, relations, constraints; first 60 lines), else the `generated/be/db-schema.md` section | 4 |
| `## Related work items and tests` | `work-items/<ID>.yml` (`summary:` lines), `test-design/features/<ID>.feature` (`Scenario` lines) | 3 |
| `## Legacy pages` | `confluence-import/**/*.md` containing the ID or 2+ title keywords; first 5 lines each | 5 |
| `## Sources and limits` | list of files read with `generated.at` where present; truncated sections; the reading rule | 1 |

Header line format: `# Context pack: <task> - <resolved subject> - <badge> - built <ISO>`.

Free-text resolution: tokens of the task (>= 4 chars) are scored against `title`, `description`, `tags`, `aliases`
of every spec and calculation; the best match is packed, up to two runners-up are listed under `candidates:`.
