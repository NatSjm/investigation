---
name: context-pack
description: Build the task-scoped context pack for a spec, calculation, graph node or free-text task and summarise what it contains and what is missing.
argument-hint: "spec ID | calculation | node id | free text"
agent: agent
tools: ['read', 'execute']
---
Task: ${input:task:P1-001}
Budget (lines): ${input:budget:400}

1. Run `./scripts/context-pack.ps1 -Task "${input:task}" -Budget ${input:budget}`.
2. Read the produced `.context/*.md` file.
3. Reply in <= 12 lines: the subject resolved (spec / calculation / node / candidates), its trust badge, sections
   present, sections truncated or empty, open questions carried from the spec, and the legacy pages that mention it.
Do not open any other file.
