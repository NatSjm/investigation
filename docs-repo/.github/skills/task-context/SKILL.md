---
name: task-context
description: The context procedure of every documentation agent - six steps from the catalogue through one context pack (scripts/context-pack.py), the documentation folders and the graph to the code, the same for a question and a change request; how far each agent goes, what the pack contains and how it is read. Use at the start of every feature, calculation, change, question or ticket task.
---

# Working with context: six steps

The bundle is bigger than any task. Every task walks the same six steps outward from the cheapest source and
stops at the first step that answers: resolve the subjects, build one pack, check its trust, read what the task
needs, search the documentation, read code last. **A question and a change request take
the same steps**; they differ in what step 4 reads and in what follows the answer (a question stops, a change request
continues into the agent's own procedure: analysis document, confirmation, rules, work items). The bundle discloses
progressively - index to index, one line per concept, open only what you need - and the steps keep that principle:
the pack carries the subject whole and what no file shows, and points at everything one hop away.

## The pack

`python3 scripts/context-pack.py --task <subject> [--task <subject> ...]` writes `.context/<slug>.md` (git-ignored;
attach it with `#file` in VS Code, paste it in JetBrains or the CLI). It holds:

- **The subject, whole**: the spec body (reduced to its key sections above 200 lines), the calculation concept
  (Purpose, Inputs, Outputs, Formula with the sanctioned code shape, Conventions, Worked examples, Audit, Open
  questions), the flow body with the Summary and the cited rules of every spec it names, or the context overview
  (specs, endpoints, tables, calculations, topics, classes by layer, pages, integrations, proposed contracts) for
  placing new work - each with its trust badge.
- **The computed sections no file shows**: the depth-2 graph neighbourhood with `file:line` (for a flow the impact of
  its `code_refs`), the contract operations and Kafka payloads of the subject's `api[]` / `events[]`, the table pages of
  its `tables[]` with the named datasets touching them, the related work items and test scenarios, and - with several
  subjects - the merged slice: shared sections deduplicated, per-subject blocks headed `### <task>`.
- **Pointers** for everything one hop away: the calculations the spec uses (one line each: name, title, path, badge,
  description), the flows it takes part in (one line each plus the steps of the flow that name the subject), the
  imported pages that mention it (path, matched words, title; UNVERIFIED). A pointer is an invitation to open the
  document through the indexes at step 4, not a gap.
- **`## Contents`** at the top: the line range of every section and the start line of every `### ` part, so you open
  the part the task needs and, after a rebuild, only what came back. Every `## ` heading is a pack section;
  embedded documents are demoted under it.
- **`## Sources and limits`** at the end: the files read into the pack, the files it points at, what `--budget`
  truncated (nothing by default) and the reading rule. The pack is the **recorded slice** of the task: what the agent
  read first and what it was pointed at, at the generated-at dates of the maps. The analysis document cites it.

```bash
python3 scripts/context-pack.py --task P1-001                       # spec ID
python3 scripts/context-pack.py --task stress_test_monthly          # calculation (whole, with worked examples)
python3 scripts/context-pack.py --task flows/session-inputs-recalculation.md    # flow: body + the rules it cites in each spec
python3 scripts/context-pack.py --task context:cover                 # context: everything it has, for placing new work
python3 scripts/context-pack.py --task "topic:harbor.meetings.session-closed"   # graph node (neighbourhood only)
python3 scripts/context-pack.py --task P1-002 --task STR-001 --task flows/session-inputs-recalculation.md  # one pack, several subjects
python3 scripts/context-pack.py --task P1-001 --print               # also to stdout
```

Free text (`"transport mode toggle on the stress table"`) is resolved by the script's keyword matcher as a fallback
only, for one-subject requests; `candidates:` in the Subject means it found several. **Free text first goes through
the catalogue** (step 1), never through the matcher. `--budget N` still exists for a tool with a hard context limit
(lower-ranked sections are truncated first, the footer names them); no procedure in this repository uses it.

Section markers, ranks and how `--task` is resolved: `references/pack-anatomy.md`.

## The six steps

1. **Resolve the subjects.** A spec ID, a calculation name, a flow or a graph node is the subject. Free text: read
   `generated/catalogue.md` (`python3 scripts/gen-catalogue.py`; one line per context - also the ones with code but
   no spec yet -, flow, spec with aliases, calculation with parameters, endpoint, topic, table with owner, external
   service and glossary alias) and decide which lines the request is about. One subject or several - a flow plus two
   specs, an existing calculation plus a new one - are all normal. A part that matches no line is **new** work: note
   the context it belongs to (`contexts.yml`) and add `context:<name>` as a subject; its overview shows what the new
   piece sits next to. When several lines fit a question, take the narrowest that answers it: the calculation for
   "how is it computed or classified" (a glossary alias such as *Exporter* points at it), the spec for "what does the
   screen show or allow", the flow for "in which order across contexts"; `context:<name>` places new work and is never
   a question's subject. A grep over the documentation folders is allowed here to find a term the catalogue does not
   list; it names a subject, it does not replace step 2.
2. **Build one pack.** One `--task` per subject, no budget. The pack is the recorded slice: the subjects whole, the
   computed sections, the pointers. Never several packs for one task; add a subject instead.
3. **Trust check.** `draft`, `unverified` or `STALE` specs, calculations and flows are unreliable: say so in the
   output and label everything derived from them `needs-spec-review`. Imported pages (pointers at the end of the
   pack) are evidence, not rules. `candidates:` in the Subject -> back to step 1, name the subjects.
4. **Read what the task needs**, by the Contents. A question: the Subject with its badge and the section the question
   names (Business rules, Calculations, Flows, Contracts, Data); the rest is disclosed, not read. A change request or
   a writing task: the whole pack, every section feeds the output (graph for subtasks, tables for datasets, contracts
   for proposals). **Follow the pointers** the task needs: a linked calculation for its formula and worked examples,
   a linked flow for its trigger and invariants, an imported page for the fact it carries - one file each, opened through
   the path the pointer gives (the folder's `index.md` lists the rest with badges). Quote `BR-<ID>-<n>`, calculation
   names, flow steps, node ids and `file:line` from what you read. Every document you open after the pack goes into
   your Sources (the analysis document's Sources; one chat line for a question).
5. **Search the documentation freely.** When the pack and its pointers leave something thin: grep `features/`,
   `domain/`, `flows/`, `architecture/`, `contracts/`, `work-items/`, `test-design/`, `generated/` and the imported pages
   under `confluence-import/<SPACE>/` for the term and open the document that matches (never `raw-html/` or
   `_attachments/`); go deeper in the graph with `python3 scripts/graph-query.py --node <id> --depth 3` or from the
   table, topic or class node in question; open the one file a thin section points at under `generated/` (schema,
   contract, map). When a found document should be part of the recorded slice - the analysis document rests on it,
   or the epic will cite it - or a context in the pack's Graph neighbourhood that the request did not name turns out
   to change (the analyst's Parts table has a row for every such context), add it as a subject and rebuild **once** (`--task <ID> --task <neighbour>`); the
   Contents of the new pack tells you which lines are new, and only those are read. Opening the neighbour directly
   is always allowed; the rebuild is for the record, not a precondition.
6. **Read code, last.** Only when steps 1-5 leave a question open that the answer or the analysis needs - the state
   of a part, the owner of a behaviour, what the code does at an edge. In this order:
   - **Through the maps first.** Locate the range through a `file:line` the pack names, `python3
     scripts/graph-query.py --find <text>`, the rows of `generated/be/components.md`, `generated/fe/codebase-map.md`
     and `generated/fe/components.md`, or the `@docs` tags in `generated/be/docs-tags.md` / `generated/fe/docs-tags.md`
     - never by searching code or walking folders. Read 40-120 lines per range in `../backend` or `../frontend`
     (sibling checkouts), chosen by `.github/skills/write-feature-spec/references/source-priority.md`: the unit test
     for edge cases, the manager for intent, the validator for error codes. A handful of ranges, not a layer, not a
     whole file.
   - **Freely only when a located range does not answer and the question still blocks.** Search both repositories
     by text, open whole files, follow the chain from the controller through the service and validator to the test.
   Three disciplines for the whole step: **only for a blocking question** (curiosity, a check of what the pack already
   says and "is this intended" never earn it - code says what the system does, not whether it is wanted; those stay
   Open questions for the owner); **list what you read** (each range or file, how it was located, the question it
   answered - in the analysis document's Sources or one chat line); **still evidence, never a rule** (below).

**What code gives is evidence, never a rule** (step 6). Cite it as `code-read <file:line>` with the backend or
frontend commit of `generated/manifest.yml`; it is **unverified** and the output that rests on it is labelled
`needs-spec-review`. Append the question to the spec's **Open questions** as an evidence request answered from code,
its item naming `code-read`, so that `spec-writer` or the owner turns it into a rule and `coverage-matrix.py` counts
it in the **answered from code** column (documentation gaps that cost analyst time; the migration lead orders the next
spec runs by it). An acceptance criterion still cites a `BR-<ID>-<n>`: draft the rule first (analyst step 4, "nothing
new without a rule"). Code folders not reachable (web chat, a docs-only machine, a Copilot CLI session without the
sibling checkouts) -> record the question and stop.

**Exit.** Still open after the last step you may take -> it is a documentation gap, not a context problem: write it
as an Open question in the spec, hand off to `spec-writer` / `doc-sync` or the owner, label your output
`needs-spec-review`. Never fill a gap from memory. Then answer: every statement cites a `BR-<ID>-<n>`, a calculation,
a flow step or a contract operation, facts (stable, human-reviewed), unverified (draft, imported, `code-read`) and
unknown kept apart, one line on how you read the request (which subjects) and one on what you opened after the pack.
For an unknown that matters, append an evidence request to the spec's **Open questions**: the question, the documents
checked, the missing fact, the likely source location if the pack or the maps name one, why it matters. Never guess.
**A question stops here. A change request continues** into the agent's own procedure with the same pack.

## How far each agent goes

| Agent | Last step | Code |
|---|---|---|
| `analyst` | 6 | through the maps, then freely for a question that still blocks |
| `spec-writer` | 6 | the one manager file the graph names, at its `file:line` |
| `doc-sync` | 6 | the handler or manager `file:line` of the graph node, a narrow range, only when behaviour and not just a signature changed |
| `calc-auditor` | 6 | exactly two files: the calculator class and its unit test, located through `docs-tags.md` |
| `test-designer` | 5 | none - worked examples come from the calculation concepts the pack points at |
| `confluence-migrator`, `architect` | 5 | none |
| `impact-analyst` | the graph only (`generated/graph/`, `graph-query.py`), no pack | none |

An agent file carries a `## Context` section of three sentences and nothing more about packs, budgets or ranges: follow
this skill, steps 1-N, for every input (the same steps for a question and a change request; open the skill before the
first tool call); code is evidence, never a rule (`code-read <file:line>` with the commit of `generated/manifest.yml`,
unverified, `needs-spec-review`, an Open question of the spec); a question stops at the exit, a change request
continues with the same pack. The analyst agent is the model text. A new role is one row in this table.

## Reading a pack

- The **trust badge** is part of the answer: `draft` / `unverified` / `STALE` -> say it, label outputs `needs-spec-review`.
- No `## Graph neighbourhood` content: the graph is missing or stale - run `python3 scripts/gen-graph.py` or say so.
- A `## Spec` reduced to key sections, a table page cut at 60 lines, a flow pointer with its steps: the path beside it
  is the whole document; open it at step 4 when the task needs more.
- `## Sources and limits` lists what the pack read and what it points at: copy it into the analysis document's
  Sources together with what you opened yourself at steps 4-7.

## Why a pack and not "just search"

The pack is not there to keep an agent away from the documentation - the folders are open from step 4 on. It is
there for four things search cannot give: a **recorded starting point** (two runs of the same task start from the
same slice, the PR carries it), the **computed sections** (graph neighbourhood, merged slice of several subjects,
contracts and tables resolved from the subject's frontmatter - no file shows them), **trust in view** (every subject
and pointer carries its badge, so unverified material is visible before it is read) and **one read instead of
twenty tool calls** for the part every task needs. Details and the design argument: `CONCEPT.md`, "The context pack".
