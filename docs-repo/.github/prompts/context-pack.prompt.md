---
name: context-pack
description: Build the task-scoped context pack for a spec, calculation, graph node or free-text task and summarise what it contains and what is missing.
argument-hint: "spec ID | calculation | flows/<name>.md | context:<name> | node id | free text; several subjects separated by ' + '"
agent: agent
tools: ['read', 'execute']
---
Task: ${input:task:P1-001}

1. Run `python3 scripts/context-pack.py --task "${input:task}"` (no budget: the subjects whole, the computed sections, pointers for
   the linked documents). When the task names several
   subjects separated by ` + ` (`P1-002 + STR-001 + flows/session-inputs-recalculation.md`), pass each as its own
   `--task` (one merged pack); when it is free text that spans several contexts, read `generated/catalogue.md`, name the
   subjects yourself and run with those instead of the text.
2. Read the produced `.context/*.md` file, starting with its `## Contents`.
3. Reply in <= 12 lines: the subject resolved (spec / calculation / node / candidates), its trust badge, the sections
   present with their line ranges, the documents the pack points at (calculations, flows, imported pages) with their
   badges, open questions carried from the spec. Procedure after the pack: `.github/skills/task-context/SKILL.md`, steps 3-7.
Do not open any other file.
