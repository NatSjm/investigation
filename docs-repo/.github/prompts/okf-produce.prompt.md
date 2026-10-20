---
name: okf-produce
description: Capture or refresh knowledge as OKF concepts (produce / maintain) and rebuild indexes.
argument-hint: "produce|maintain target"
agent: doc-sync
---
Mode: ${input:mode:produce|maintain}
Target: ${input:target:concept path, feature ID, or topic}
Sources read: ${input:sources:paths/URLs you want recorded in sources[]}

Follow `.github/skills/okf/SKILL.md` for the chosen mode. Set `generated.by: copilot/doc-sync`. Do not add
`verified` (a human does). Then, once after the last edit, run `python3 scripts/build-index.py` and
`python3 scripts/okf-validate.py --changed --strict`.
Report: concepts created/updated, index files touched, validation result (<= 10 lines).
