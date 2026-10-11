---
name: okf
description: Author, maintain and consume this repo's Open Knowledge Format (OKF v0.2) bundle — Markdown concepts with YAML frontmatter (type, description, generated, verified, stale_after, sources). Use when creating or updating any doc under features/, domain/, architecture/ or generated/, when asked to "document X in OKF", or before relying on docs as context (read index.md first).
---

# OKF skill (Copilot port)

This whole docs repo is one OKF bundle (root `index.md` carries `okf_version: "0.2"`).
Source of truth for every rule: [reference/SPEC.md](reference/SPEC.md) — read the relevant § before
non-trivial work, not your memory of it. Ported from `scaccogatto/okf-skills` (MIT); see [PORTING.md](PORTING.md).

## The one hard rule (§11)
Every non-reserved `.md` file has parseable YAML frontmatter with a non-empty `type`. Reserved names:
`index.md`, `log.md` (no frontmatter, except root `index.md` → `okf_version`). Everything else is soft.
Consequence: folder `README.md` files are **not allowed** inside the bundle — use `index.md`.

## Conventions (this repo)
- One concept = one file; path minus `.md` is the concept id. Absolute bundle links: `/features/product1/P1-001.md`.
- `type` vocabulary (keep to these): `Feature Spec`, `Attested Computation`, `Glossary`, `Decision`,
  `Architecture View`, `Integration Map`, `HLD`, `Codebase Map`, `API Module`, `Kafka Topic`, `Table Group`,
  `API Surface`, `Flow` (cross-context behaviour under flows/), `Document` (misc prose), `Imported Page` (Confluence quarantine).
- Actors (§7): `copilot/<agent-name>` for agents (e.g. `copilot/doc-sync`), `human:<id>` for people,
  `process:<ci-job>` for CI. Use `human:` **only** for real human sign-off — trust tiers key off it.
- Lifecycle: `status: draft|stable|deprecated`; `stale_after` absolute ISO datetime. Feature specs default
  `stale_after` = verified + 90 days; generated concepts = generated + 30 days.
- Provenance: `sources[]` with `id`, `resource`, `title`, `last_modified`; per-claim footnotes `[^id]`.
  Confluence-migrated content MUST list the page as a source.
- Our extension keys stay (`id`, `code_refs`, `api`, `events`, `tables`, `calculations`, `jira`, `tests`).
- `log.md` (root) — lifecycle events only: created, deprecated, superseded, regenerated, verified. Append-only.

## Modes
### produce
1. Copy [templates/concept.md](templates/concept.md) (or the repo template for the type: `features/_template.md`,
   `domain/calculations/_template.md`, `architecture/adr/template.md`).
2. Fill `type`, `title`, `description` (one sentence — it becomes the index line), `tags`, `generated`,
   `sources` you actually read; cross-link related concepts.
3. Run `scripts/build-index.ps1` (rewrites all `index.md`), then validate (below).

### maintain
1. Find affected concepts (`search` by `resource`, code path via `docs-map.yml`, or topic).
2. Update body + `generated: { by: copilot/<agent>, at }`; keep existing `verified` only if the change is
   editorial — otherwise remove it (a human must re-verify). Deprecate, never silently delete.
3. `build-index.ps1`; `log.md` entry only for lifecycle events; validate.

### consume
1. Read root `index.md`, then the directory `index.md`, then only the concepts you need. Never list directories.
2. Weigh: `draft`/`deprecated`, past `stale_after`, or no `verified` ⇒ say so in your output.
3. Numbers covered by an `Attested Computation` come from its worked examples / executor — never re-derive.

## Validate before finishing
- Dev machine (no Python): `scripts/okf-validate.ps1 -Strict`
- CI / full checker: `python .github/skills/okf-validate/scripts/okf_validate.py . --strict` (see `okf-validate` skill).
Fix every ERROR; under `-Strict` fix warnings too.
