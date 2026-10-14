---
description: "Glossary-controlled rendering of an English concept in another language for Confluence publishing (build artifact, not committed)."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/translate-for-publish.prompt.md` in this repository as the agent `docs-repo/.github/agents/agent.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; finish with the validators the agent names (`okf-validate.py --strict`, `build-index.py`, a `log.md` entry); chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
