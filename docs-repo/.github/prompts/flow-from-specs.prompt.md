---
name: flow-from-specs
description: Write or refresh a cross-context flow under flows/ that composes the rules of the specs it names, with steps from the graph and the two-way spec link.
argument-hint: "flow-name spec-ids [behaviour] (e.g. report-after-close SES-001 RPT-001; session-inputs-recalculation IMP-001 P1-002 COV-001 STR-001 RPT-001)"
agent: spec-writer
---
Flow to create or refresh: `flows/${input:name:report-after-close}.md` (`id: FLOW-${input:name:report-after-close}`).
Specs whose rules it composes: ${input:specs:SES-001 RPT-001} (space-separated spec IDs; `context:<name>` for a
context that has no spec yet). Behaviour in one sentence (optional): ${input:behaviour:none}.

A flow is behaviour across bounded contexts, or across windows or processes (`features/conventions.md`, "Shaping
specs" point 6): each spec keeps its local rule, the flow composes them in order. When every step the pack shows
belongs to one screen of one context, stop and say so: that is the UI flow section of that spec, not a flow.

1. Context: `.github/skills/task-context/SKILL.md`, steps 1-5, no code. One pack with a `--task` per spec given
   (`python3 scripts/context-pack.py --task SES-001 --task RPT-001`), plus `--task flows/<name>.md` when the flow
   exists and is refreshed. Read the pack by its Contents: the specs' rules, the depth-2 graph neighbourhood, the
   topics and tables.
2. Create the file from `flows/_template.md` (a refresh keeps the existing prose and changes only what the pack
   contradicts). **Trigger**, **Participants** and **Steps** from the graph: every step names a node id and its
   `file:line` from the pack, in the order the edges give (route -> hook -> endpoint -> class -> topic -> consumer ->
   table); a Mermaid `sequenceDiagram` above five steps, <= 25 nodes. `channels:` lists the browser channels, Kafka
   topics and external calls the steps cross; `code_refs:` the entry points only; `contexts:` from `contexts.yml`;
   `tags: [flow, <contexts>]`. **Data and state changes** from the `table:*` nodes and the window state the steps
   touch. **Failure behaviour** only from what the pack shows; what it does not show is an open question.
3. **Invariants** cite `BR-<ID>-<n>` of the specs given, one line each; never restate a rule's text. A behaviour the
   steps need that no spec owns is **not** a rule of the flow: write it under Open questions as a candidate rule for
   the owning context (`candidate rule: <behaviour> - owner <context>`). An imported page in the pack may contribute
   a step or an invariant: cite `[^conf-<slug>]`, mark it `❓ UNVERIFIED`, copy no threshold or formula.
4. Two-way link: `specs:` names every spec a step or an invariant cites, and each of those specs gets
   `/flows/<name>.md` in its frontmatter `flows:` (`validate-frontmatter.py` checks the pair). Nothing else in a spec
   changes.
5. Frontmatter: `status: draft`, `generated: { by: copilot/spec-writer, at: <ISO> }`, `stale_after` +90 days, no
   `verified`; `sources[]` for the entry files and the imported pages cited.
6. `python3 scripts/validate-frontmatter.py flows/<name>.md` and every touched spec, `python3 scripts/okf-validate.py
   --strict`, `python3 scripts/build-index.py`. One line in `flows/log.md` (`* **[<name>](<name>.md)**: created from
   <spec IDs> (<request>)`, or `refreshed: <what>`), one in each touched spec's `features/<ctx>/log.md`
   (`* **[<ID>](<ID>.md)**: flows + /flows/<name>.md`), and a root `log.md` line ("created FLOW-<name>").

Report <= 10 lines: which steps came from the graph, which rules the invariants compose, which specs were linked
back, and what is open (candidate rules, failure behaviour not shown by the pack).
