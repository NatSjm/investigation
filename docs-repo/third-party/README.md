# Third-party notices

| Component | Origin | License | Vendored to |
|---|---|---|---|
| Open Knowledge Format specification v0.2 | [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format) © Google LLC | Apache-2.0 (`okf-spec-LICENSE.md`) | `.github/skills/okf/reference/SPEC.md` (verbatim, provenance header added as an HTML comment) |
| okf-skills scripts & templates (`okf_validate.py`, `okf_visualize.py`, `okf_init.py`, `templates/*.md`) | [scaccogatto/okf-skills](https://github.com/scaccogatto/okf-skills) © Marco Boffo | MIT (`okf-skills/LICENSE`, upstream `okf-skills/NOTICE`) | `.github/skills/okf*/scripts`, `.github/skills/okf/templates` |

## Licence compliance summary (not legal advice - confirm with your organisation's OSS policy owner)

| Obligation | MIT (okf-skills) | Apache-2.0 (OKF spec) | Status |
|---|---|---|---|
| Keep licence text | copyright + permission notice in all copies/substantial portions | copy of the licence with any redistribution (§4a) | `okf-skills/LICENSE`, `okf-spec-LICENSE.md` |
| Keep attribution / NOTICE | - | retain attribution notices (§4c); include NOTICE if upstream ships one (§4d) | SPEC.md header; upstream Google repo has no NOTICE; okf-skills NOTICE vendored |
| Mark modifications | not required (we still attribute) | modified files must carry prominent change notices (§4b) | SPEC.md is **unmodified**; Python scripts unmodified; `okf-validate.py`, `SKILL.md`, prompts are our rewrites and say so |
| Right to modify / create derivatives / use commercially / keep private | yes | yes (incl. patent grant) | the standard-library Python port and the Copilot rewrites are permitted derivative works |
| Copyleft / share-alike | none | none | no obligation to publish our changes or open-source the docs repo |
| Trademarks | - | no right to use Google marks beyond describing origin (§6) | we only name the format and link the source |

Internal use inside the organisation is not "distribution" in most readings, so even fewer obligations apply - but the notices
above are kept regardless, which is the conservative, audit-friendly position.

The `SKILL.md`, prompt, agent and script files in `.github/` and `scripts/` are rewritten for GitHub Copilot and are
this repository's own work; the Claude Code plugin manifest, Stop hook, MCP server and backfill subagents
were **not** ported (see `.github/skills/okf/PORTING.md`).

Security note: vendored Python requires `pyyaml` only. Pin by commit when adopting for real; review the
scripts before enabling them in your CI images.
