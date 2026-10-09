---
name: okf-visualize
description: Render the docs bundle as a self-contained interactive HTML graph (viz.html) — concepts as nodes, links and sources as edges, trust tier and staleness badges. Use when asked to visualize, graph or explore the documentation, or for impact analysis (what links to a calculation / topic / table).
---

# Visualize the OKF bundle

Script vendored unchanged from `scaccogatto/okf-skills` (MIT, see `third-party/okf-skills/LICENSE`); this SKILL.md is rewritten for Copilot.

```
python .github/skills/okf-visualize/scripts/okf_visualize.py . -o viz.html --title "Harbor docs" --link "<repo url>"
```
Requires Python + `pyyaml` (CI or a workstation with Python). The page loads cytoscape/marked/dompurify from
`cdn.jsdelivr.net` — if your network blocks CDNs, vendor those three files and patch the script's `<script src>` lines.

Useful flags: `--layout cose|concentric|breadthfirst|circle|grid`, `--max-nodes N` (exit 1 above N — CI guard),
deep links `viz.html#features/product1/P1-001`.

Reading the graph for impact analysis: select a calculation or Kafka topic → **Cited by** lists every feature
spec that depends on it; badges show *unverified / machine-confirmed / human-reviewed* and *stale*. Report the
tier when you cite a concept; do not treat it as a gate.

CI publishes `viz.html` as a build artifact of `docs-quality.yml`; do not commit it.
