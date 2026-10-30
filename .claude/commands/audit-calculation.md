---
description: "Verify a calculation concept or an imported formula page against the implementation and its unit test; record findings, never silently change numbers."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/audit-calculation.prompt.md` in this repository as the agent `docs-repo/.github/agents/calc-auditor.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; run the checks the agent or prompt names once, after the last edit, and only for what you changed (`docs-repo/AGENTS.md`, Checks: `okf-validate.py --strict` for concepts, a `log.md` entry only for lifecycle events); a task that changed no file runs none; chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
