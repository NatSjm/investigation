---
description: "Generate Gherkin test cases and synthetic fixtures for a feature from its context pack."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/tests-from-spec.prompt.md` in this repository as the agent `docs-repo/.github/agents/test-designer.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; run the checks the agent or prompt names once, after the last edit, and only for what you changed (`docs-repo/AGENTS.md`, Checks: `okf-validate.py --strict` for concepts, a `log.md` entry only for lifecycle events); a task that changed no file runs none; chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
