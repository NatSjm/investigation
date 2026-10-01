# Copilot instructions — Advisory Platform documentation repo

This repository is the **single source of truth** for functional and technical documentation of the
Financial Advisory Platform (hedges, loans, stress tests, monthly computations, admin, integrations).
Confluence is a *publish target*, not a source. Code repos (`fe/` React, `be/` Kotlin Spring) are *inputs*.

## Golden rules

1. **Never hand-edit `generated/`** — it is produced by CI from the FE/BE repos.
2. **Read maps before code.** To understand behaviour, consult in this order:
   1. `index.md` (bundle root) → the folder `index.md` for the area (progressive disclosure)
   2. `features/<context>/<ID>.md` (spec)
   3. `domain/calculations/*.md` (formulas + worked examples)
   4. `generated/graph/REPO_MAP.md` → `generated/graph/<community>.md` (architectural graph: endpoints, classes,
      topics, tables, FE features/routes, spec links, with `file:line`) — see skill `code-graph`
   5. `generated/codebase-map.md` (module → responsibility → entry files)
   6. `generated/api-surface/**` (public signatures only)
   7. `generated/openapi/*.yaml`, `generated/asyncapi/*.yaml`, `generated/db/schema.md`
   Only open FE/BE source files when the above are insufficient, and open the **smallest** file range possible.
3. **Every spec has frontmatter** conforming to `features/_template.md`. Keep `code_refs`, `jira`, `tests`
   and `last_verified` up to date whenever you touch a spec.
4. **Terminology** comes from `domain/glossary.md`. Do not invent synonyms; add new terms there first.
   **Language**: everything in this repo is **English** (specs, Gherkin, YAML, ADRs). Czech appears only in
   `confluence-import/` (raw pages), the glossary `Czech (cs)` column, and frontmatter `aliases`. When a user
   asks in Czech, answer in Czech but write files in English; translate domain terms only via the glossary.
5. **Traceability IDs** are mandatory: `<CTX>-<NNN>` (e.g. `HEDGE-012`). Work items, test cases and
   fixtures reference the feature ID.
6. Output formats:
   - Specs, ADRs, architecture → Markdown + Mermaid.
   - Work items → YAML per `work-items/_schema.yml`.
   - Test cases → Gherkin `.feature`; fixtures → JSON/CSV in `test-design/fixtures/`.
7. **Bank confidentiality**: never paste real client data, account numbers or credentials into docs, fixtures
   or examples. Use synthetic data (see `test-design/fixtures/README.md`).

## Token discipline

- Prefer `generated/api-surface` (signatures) over implementation; prefer `codebase-map.md` over directory listings.
- Do not read whole calculation services; the formulas are in `domain/calculations/`. If the doc is missing or
  outdated, read only the specific function named in `codebase-map.md` and then **fix the doc**.
- When summarising, write once to the doc; do not echo long content back into chat.
- Skills under `.github/skills/` are short by design; load `references/` only when the skill tells you to.

## Open Knowledge Format (OKF v0.2)

The repository root is **one OKF bundle** (`index.md` carries `okf_version: "0.2"`). Full rules: `.github/skills/okf/SKILL.md`.

- Every `.md` under `architecture/`, `domain/`, `features/`, `generated/` is a **concept** and MUST have
  frontmatter with `type` (e.g. `Feature Spec`, `Attested Computation`, `Decision`, `Glossary`, `Document`).
  Do **not** create `README.md` inside those folders — use a typed concept instead.
- `index.md` / `log.md` are reserved (no frontmatter, except `okf_version` in the root index). Never hand-edit
  `index.md`; run `scripts/build-index.ps1`. Append a dated `## YYYY-MM-DD` entry to `log.md` for notable changes.
- **Provenance**: set `generated.by: copilot/<agent-name>` and `generated.at` (ISO) when you produce or rewrite a
  concept; never write `verified[].by: human:<id>` yourself — only a person may add it. Cite evidence with
  `sources[]` + `[^id]` footnotes.
- `status` is `draft | stable | deprecated`; `stale_after` is an absolute ISO date.
- Before finishing any edit run `scripts/okf-validate.ps1 -Strict` and `scripts/build-index.ps1` (CI enforces both).

## Repository layout

| Path | Purpose |
|---|---|
| `architecture/` | arc42/C4 views, ADRs, integration & Kafka topic map |
| `domain/` | glossary, bounded contexts, calculation specs |
| `features/` | functional specs per bounded context |
| `generated/` | CI-produced artifacts from FE/BE (read-only) |
| `work-items/` | Jira epics/stories/subtasks as YAML |
| `test-design/` | Gherkin test cases and synthetic fixtures for the tests repo |
| `confluence-import/` | raw migrated Confluence pages (quarantine) |
| `scripts/` | Jira / Confluence / tests-repo sync scripts (REST); OKF validator + index builder |
| `third-party/` | licences/notices for vendored OKF tooling |
| `docs-map.yml` | code path → feature doc traceability |
| `index.md`, `log.md` | OKF bundle root index (generated) and change log (reserved files) |
