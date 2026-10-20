---
name: analyse-request
description: Take a request in free text (a question, or a change that may span several contexts and mix existing and new behaviour), resolve it through the catalogue, build one context pack, write the analysis document, confirm the reading with the analyst, then produce the request epic.
argument-hint: "the request in free text [question|analysis|work-items]"
agent: analyst
---
Request: ${input:request}
Mode: ${input:mode:question|analysis|work-items} (default `work-items`: analysis, confirmation, then the epic)

1. Read `generated/catalogue.md`; name the subjects (specs, calculations, flows, `context:<name>` for every context
   that receives new work); build ONE pack: `python3 scripts/context-pack.py --task <subject> --task <subject> ...`.
2. `question`: answer from the pack with citations (`BR-<ID>-<n>`, calculation, flow step, operationId), facts /
   unverified / unknown separated, one line on how you read the question. Stop.
3. `analysis` and `work-items`: write `work-items/<slug>.md` from `work-items/_analysis-template.md`; print the
   Reading line and the Parts table (<= 15 lines) and **stop for the analyst's confirmation**. Mode `analysis` ends here.
4. `work-items`, after confirmation: set `status: confirmed`; for every `new` / `changed` part make sure a (draft)
   rule, spec, proposed contract or draft calculation exists first (hand off to `spec-writer` / `architect` when it does
   not); then write `work-items/<slug>.yml` (`request:`, `analysis:`, `specs:`, stories with `depends_on` across
   contexts) and run `python3 scripts/validate-work-items.py work-items/<slug>.yml`.
Print story summaries, estimates, `depends_on`, open questions and the trust badges only.
