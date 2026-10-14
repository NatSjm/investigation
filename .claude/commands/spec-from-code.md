---
description: "Refresh an existing feature spec against the current contracts, maps and graph; open source only for rules the artifacts cannot explain."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/spec-from-code.prompt.md` in this repository as the agent `docs-repo/.github/agents/spec-writer.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; finish with the validators the agent names (`okf-validate.py --strict`, `build-index.py`, a `log.md` entry); chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
