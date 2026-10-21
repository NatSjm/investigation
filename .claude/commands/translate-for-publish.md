---
description: "Glossary-controlled rendering of an English concept in another language for Confluence publishing (build artifact, not committed)."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/translate-for-publish.prompt.md` in this repository in Copilot's built-in agent mode (the prompt says `agent: agent`; there is no agent file), with this argument: $ARGUMENTS

Rules: read the prompt file first and follow its procedure and the skills it references under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; run the checks the agent or prompt names once, after the last edit, and only for what you changed (`docs-repo/AGENTS.md`, Checks: `okf-validate.py --strict` for concepts, a `log.md` entry only for lifecycle events); a task that changed no file runs none; chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
