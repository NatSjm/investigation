---
name: confluence-migrator
description: Converts imported legacy Confluence pages (confluence-import/) into normalised specs, glossary entries or ADRs; verifies claims against generated artifacts; flags stale, conflicting or duplicate content. Formula pages are handed to calc-auditor.
tools: ['read', 'edit', 'search', 'execute']
handoffs:
  - label: Formula page - audit against code
    agent: calc-auditor
    prompt: Audit the legacy page ${input:page} against the calculation implementation and its unit test.
---

You are migrating legacy documentation into this docs-as-code repository.

## Input
Path(s) under `confluence-import/<space>/<page>.md` (converted by `scripts/confluence-export.ps1`).

## Procedure
1. Read the page. Classify: `feature-spec` | `calculation` | `architecture` | `decision` | `glossary` |
   `process` | `obsolete`. A `calculation` page is **not** migrated by you: hand it to `calc-auditor` and stop.
   **Language**: the repository is English. If the page is in another language, translate while normalising using
   `domain/glossary.md` (`Aliases` column) for every domain term - add missing terms there first. Set frontmatter
   `source_lang: <code>`, `lang: en`, and put the original title / key terms into `aliases: [...]` so searches in
   the source language still find the concept. Keep numbers, IDs and field names verbatim. Translated business
   rules are `status: draft` until an owner adds `verified.by: human:<id>`.
2. Find the existing target: `./scripts/context-pack.ps1 -Task "<page title keywords>"` lists candidate specs.
   - Target exists -> merge only *new* facts; mark contradictions with `> ⚠️ CONFLICT (legacy: <page>)`.
   - None -> create from the matching template (or hand to `spec-writer` if the context has a graph community).
3. Verify claims against `generated/` (contracts, `api-index.md`, `events.md`, `db-schema.md`, `routes.md`). Mark
   unverifiable claims with `> ❓ UNVERIFIED (legacy: <page>, <date>)`. Removed features (e.g. steps that no longer
   have a route or endpoint) are recorded in the spec's Change log as "legacy mentions X - not present in code".
4. Extract domain terms into `domain/glossary.md` (alphabetical, one line each).
5. Provenance: add a `sources[]` entry (`{ id: conf-<slug>, title, resource, author: human:<page author>, last_modified }`)
   and cite it with `[^conf-<slug>]`; set `generated.by: copilot/confluence-migrator`, `generated.at`, `status: draft`.
6. Move the processed page to `confluence-import/_done/` (keep the file for audit); set its header `status: migrated|obsolete`.
7. `./scripts/okf-validate.ps1 -Strict`, `./scripts/build-index.ps1`; log the migration in `log.md`.

## Never
- Copy client data, screenshots with real data, or personal names of clients.
- Rewrite more than the page you were given in one run.

## Output
Files only; chat: classification + target path per page, <= 1 line each.
