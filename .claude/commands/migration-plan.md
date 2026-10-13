---
description: "Plan the documentation migration for a context, a Confluence space or the whole repo - which lifecycle runs are due, in which order, with the command for each."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/migration-plan.prompt.md` in this repository as the agent `docs-repo/.github/agents/migration-lead.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; finish with the validators the agent names (`okf-validate.ps1 -Strict`, `build-index.ps1`, a `log.md` entry); chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
