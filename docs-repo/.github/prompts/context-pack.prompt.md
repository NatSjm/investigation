---
name: context-pack
description: Build the task-scoped context pack for a spec, calculation, graph node or free-text task and summarise what it contains and what is missing.
argument-hint: "spec ID | calculation | flows/<name>.md | context:<name> | node id | free text; several subjects separated by ' + '"
agent: agent
tools: ['read', 'execute']
---
Task: ${input:task:P1-001}
Budget (lines): ${input:budget:500}

1. Run `python3 scripts/context-pack.py --task "${input:task}" --budget ${input:budget}`. When the task names several
   subjects separated by ` + ` (`P1-002 + STR-001 + flows/session-inputs-recalculation.md`), pass each as its own
   `--task` (one merged pack); when it is free text that spans several contexts, read `generated/catalogue.md`, name the
   subjects yourself and run with those instead of the text.
2. Read the produced `.context/*.md` file.
3. Reply in <= 12 lines: the subject resolved (spec / calculation / node / candidates), its trust badge, sections
   present, sections truncated or empty, open questions carried from the spec, and the legacy pages that mention it.
Do not open any other file.
