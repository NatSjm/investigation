---
name: task-context
description: Build and consume a task-scoped context pack (scripts/context-pack.py) so that an analyst, writer or tester agent reads only what the current task needs - spec, calculations, flows, graph neighbourhood, contracts, tables, related work items and legacy pages - instead of the repository or the code. Use at the start of every feature, calculation, change or ticket task.
---

# Task-scoped context packs

The bundle is bigger than any task. The pack is the **budgeted slice** of it for one task, assembled
deterministically by a script, so every agent starts from the same pack - sized by its subjects, each item bounded
on its own, nothing truncated unless `--budget N` is given - and can tell what it did not get.

## Build
```bash
python3 scripts/context-pack.py --task P1-001                       # spec ID
python3 scripts/context-pack.py --task stress_test_monthly          # calculation
python3 scripts/context-pack.py --task "topic:harbor.meetings.session-closed"   # graph node
python3 scripts/context-pack.py --task flows/session-inputs-recalculation.md    # flow: body + the rules it cites in each spec
python3 scripts/context-pack.py --task context:cover                 # context: everything it has, for placing new work
python3 scripts/context-pack.py --task P1-002 --task STR-001 --task flows/session-inputs-recalculation.md  # one pack, several subjects
python3 scripts/context-pack.py --task "transport mode toggle on the stress table" # free text -> candidates (fallback)
python3 scripts/context-pack.py --task P1-001 --budget 250 --print    # smaller, to stdout
```
Output: `.context/<slug>.md` (git-ignored). Attach it with `#file` (VS Code) or paste it (JetBrains / CLI).

**Free text first goes through the catalogue, not through the script's matcher.** `generated/catalogue.md`
(`python3 scripts/gen-catalogue.py`) lists on one page, one line each: every context (also the ones with code but no
spec yet), flow, spec with its aliases, calculation with its parameters, API endpoint, Kafka topic, table with its
owner, external service and glossary term with what people also call it. Read it, decide which lines the request is
about - several contexts and several kinds are normal - and build **one pack with a `--task` per subject** (spec ID,
calculation name, `flows/<name>.md`, `context:<name>`, graph node): the shared sections are merged and deduplicated,
nothing is truncated unless you pass `--budget`. A part of the request that matches no line is new work: add
`--task context:<name>` for the context it belongs to - its overview section lists the specs, endpoints, tables,
calculations, topics, classes by layer and pages that are already there, so the new piece can be placed next to the
nearest existing one. The script's own free-text resolution (title / description / tags / aliases keyword hits with
glossary aliases) is a fallback for one-subject requests and must not be trusted for cross-context ones.

## Anatomy (in priority order; lower sections are truncated first when over budget)
1. **Header** - subject, resolution (spec / calculation / node / candidates), trust badge
   (`status`, `human-reviewed | machine-confirmed | unverified`, `STALE`), `last_verified`, `stale_after`.
2. **Spec** - whole body when <= 200 lines, otherwise Summary, Business rules, API / Events, Data, Open questions.
   For a calculation subject **Calculation** (formula, worked examples), for a flow subject **Flow** (its body) and
   **Specs in the flow** (Summary + the rules the flow cites, per spec), for a context subject **Context overview**
   (specs, endpoints, tables, calculations, topics, classes by layer, pages, integrations, proposed contracts).
3. **Calculations** linked from the spec - Purpose, Formula, Conventions, Worked examples (never the Kotlin block).
4. **Flows** the spec takes part in (`flows:` in the spec or `specs:` in the flow) - Purpose, Trigger, Participants, Steps,
   Invariants and assumptions; the cross-context behaviour the single spec does not show.
5. **Graph neighbourhood** - `graph-query.py --node spec:<ID> --depth 2`: nodes by kind with `file:line`, edges,
   cross-community edges, heuristic marks.
6. **Contracts** - the `paths` blocks of `generated/openapi/backend.yaml` for the spec's `api[]` entries; channel
   names from `asyncapi/backend.yaml` for `events[]` (from `generated/be/events.md` when there is no AsyncAPI document).
7. **Data** - the `db-schema.md` sections for `tables[]`.
8. **Related** - `work-items/<ID>.yml` story summaries, `test-design/features/<ID>.feature` scenario names.
9. **Legacy** - `confluence-import/**` pages mentioning the ID or title keywords (listed, first lines only, marked unverified).
10. **Footer** - sources used, sections truncated, and the rule: *open nothing else unless a question below is
   unanswered; then only the `file:line` named above*.

See `references/pack-anatomy.md` for the exact section markers the agents rely on, how several subjects are merged
into one pack and how `--task` is resolved.

## Consume
- Read the pack once, top to bottom. Quote `BR-*`, node ids and `file:line` from it.
- Treat the trust badge as part of the answer: `draft` / `unverified` / `STALE` -> say it, label outputs `needs-spec-review`.
- `candidates:` in the header means the script's keyword matcher was used on free text and found several specs:
  go back to `generated/catalogue.md`, choose the subjects there and rebuild per subject; do not merge candidates blindly.
- A truncated section (`... (truncated: see <path>)`) tells you exactly which file to open if you need more.
- If the pack has no graph section, the graph is missing or stale: run `python3 scripts/gen-graph.py` or say so.

## When the pack is not enough (escalate in this order, stop at the first step that answers)
1. Rebuild without the `--budget` you set (there is none by default) - truncated sections come back.
2. Follow the pointer of the truncated or thin section: open that one file under `generated/` (schema, contract, map).
3. Go deeper in the graph: `python3 scripts/graph-query.py --node <id> --depth 3`, or start from the table / topic / class
   node in question - no files opened.
4. Rebuild with the neighbour the pack points at as another subject (`--task <ID> --task <linked calculation | spec
   of another context | flows/<name>.md | context:<name>>`): one pack, the shared sections merged, nothing read twice.
5. Open exactly the `file:line` the pack names, 40-120 lines, chosen by `write-feature-spec/references/source-priority.md`
   (unit test for edge cases, manager for intent, validator for error codes). Never a whole layer, never a code search.
6. Still missing -> it is a documentation gap, not a context problem: write it as an open question in the spec,
   hand off to `spec-writer` / `doc-sync`, label your output `needs-spec-review`. Never fill the gap from memory.

The analyst may do step 5 when steps 1-4 leave a question open that its answer or analysis needs, and may locate the
range itself through the maps (`graph-query.py --find`, `generated/be/components.md`, `generated/fe/codebase-map.md`,
`docs-tags.md`) - at most five ranges per task, each finding cited as `code-read <file:line>` and written as an Open
question (analyst agent, step 9). When a question still blocks its answer or analysis after the five ranges, the analyst
alone takes one free reading pass over `../backend` and `../frontend` (search, whole files, call chains; analyst agent
step 10): the findings carry the same `code-read` citation and Open question, the files read are listed in the analysis
document's Sources, and `coverage-matrix.py` counts the questions answered from code per spec. Step 6 stays the rule
for every other agent and for a question the pass leaves open.

## Why a script and not "just search"
Deterministic, budgeted, reviewable (the pack can be attached to the PR), cheap (one read instead of 10-20 tool
calls), and it carries provenance (which files, which generated-at dates) into the agent's reasoning.
