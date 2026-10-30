---
name: analyse-request
description: Take a request in free text (a question, or a change that may span several contexts and mix existing and new behaviour), walk the six context steps of the task-context skill (catalogue, one pack, documentation, graph, code last), answer it, and for a change request write the analysis document, confirm the reading with the analyst, then produce the request epic.
argument-hint: "the request in free text [question|analysis|work-items]"
agent: analyst
---
Request: ${input:request}
Mode: ${input:mode:question|analysis|work-items} (default `work-items`: analysis, confirmation, then the epic)

1. **Context, steps 1-6 of `.github/skills/task-context/SKILL.md`** - the same for every mode. Read
   `generated/catalogue.md`; name the subjects (a `question`: the narrowest subject that answers it - calculation for
   "how is it computed / classified", spec for "what does the screen show / allow", flow for "in which order across
   contexts", never `context:<name>`; a change: every part, plus `context:<name>` for every context that receives new
   work); build ONE pack: `python3 scripts/context-pack.py --task <subject> --task <subject> ...` (no budget); check
   the badges; read by the Contents (a `question`: the Subject and the section it names; a change: the whole pack) and
   follow the pointers the request needs; search the documentation folders and the graph freely, rebuilding once with
   a neighbour as another `--task` when the record should carry it; code last - through the maps, then freely for a
   question that still blocks - cited as `code-read <file:line>`, unverified, an Open question in the spec.
2. `question`: answer with citations (`BR-<ID>-<n>`, calculation, flow step, operationId), facts / unverified /
   unknown separated, one line on how you read the question and one on what you opened after the pack. Stop.
3. `analysis` and `work-items`: write `work-items/<slug>.md` from `work-items/_analysis-template.md` (Sources: the
   pack, the documents opened after it, every code range or file read with the question it answered); print the
   Reading line and the Parts table (<= 15 lines) and **stop for the analyst's confirmation**. Mode `analysis` ends here.
4. `work-items`, after confirmation: set `status: confirmed`; for every `new` / `changed` part make sure a (draft)
   rule, spec, proposed contract or draft calculation exists first (hand off to `spec-writer` / `architect` when it does
   not); then write `work-items/<slug>.yml` (`request:`, `analysis:`, `specs:`, stories with `depends_on` across
   contexts) and run `python3 scripts/validate-work-items.py work-items/<slug>.yml`.
Print story summaries, estimates, `depends_on`, open questions and the trust badges only.
4. A request that already has `work-items/<slug>.md` and changed before the code has it (a re-imported page,
   a changed ask): the same slug, steps 1 to 3 again with the document rewritten in place and the Reading confirmed
   again; `spec-writer` adjusts the proposed rules of the same spec (changed: same ID and marker; new: next number;
   no longer asked for: **withdrawn**, text kept) and the stories that cited them are re-cut (analyst agent step 4).
