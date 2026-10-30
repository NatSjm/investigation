---
description: "Fill the `Term (<lang>)` column of docs-repo/domain/glossary.md from the frontend translation file and the imported pages in that language; unsourced terms are proposed under Open questions."
---
Run the GitHub Copilot prompt `docs-repo/.github/prompts/translate-glossary.prompt.md` in this repository in Copilot's built-in agent mode (the prompt says `agent: agent`; there is no agent file), with this argument: $ARGUMENTS

Rules: read the prompt file first and follow its procedure; treat `docs-repo` as the repository root (`../backend`, `../frontend` are the code repos); keep outputs in files; run the checks the prompt names once, after the last edit (`gen-catalogue.py`, `okf-validate.py --strict`, `build-index.py`); a root `log.md` line only for the first fill of a column; chat summary under 6 lines. Never write `verified.by: human:*`, never change the English `Term`, `Definition`, `Aliases` or `Used in` cells, and never edit `docs-repo/generated/**` by hand.
