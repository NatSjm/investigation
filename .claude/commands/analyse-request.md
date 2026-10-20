---
description: "Take a request in free text (a question, or a change spanning several contexts with existing and new behaviour), resolve it through the catalogue, build one context pack, write the analysis document, confirm the reading, then produce the request epic."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/analyse-request.prompt.md` in this repository as the agent `docs-repo/.github/agents/analyst.agent.md`, with this argument: $ARGUMENTS

Rules: read the prompt file and the agent file first and follow their procedure and the skills they reference under `docs-repo/.github/skills/`; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; stop for the analyst's confirmation of the Reading before writing stories; run the checks of the agent's Checks table once, after the last edit, and only for what you changed; a question that changed no file runs none; chat summary under 15 lines. Never write `verified.by: human:*` and never edit `docs-repo/generated/**`.
