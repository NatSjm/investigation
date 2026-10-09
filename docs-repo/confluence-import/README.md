# Confluence import (quarantine)

Raw legacy pages exported by `scripts/confluence-export.ps1` (Confluence REST → storage-format HTML → Markdown via
pandoc). Structure: `<SPACE>/<page-title>.md` with a header block `source`, `last_modified`, `author`
(and `confluence_id`, `url` when the export provides them).

## Quarantine rules

1. **Nothing in this folder is authoritative.** Pages are evidence of what people once believed, not of what the
   code does. The code and `generated/` win on every conflict; the conflict is recorded as an open question in the
   target spec and in the migration note.
2. Pages are migrated **one at a time** by the agent `confluence-migrator` (`@confluence-migrator
   confluence-import/HARBOR/<page>.md`) into typed concepts under `features/`, `domain/` or `architecture/`;
   the page is cited in the concept's `sources[]` with its `last_modified` date.
3. Processed pages move to `<SPACE>/_done/`; a page that contradicts the code is kept with a `superseded_by:` line
   pointing at the concept so the audit trail survives.
4. Terminology is translated only through `domain/glossary.md` (`Aliases` column); unknown terms are added to the
   glossary first.
5. After a space is fully migrated, the Confluence pages are replaced by a banner plus a link to the published copy
   (`scripts/confluence-publish.ps1`).
6. Attachments are not imported automatically; screenshots or tables containing client data must be dropped.
7. This folder is excluded from `okf-validate.ps1` and markdownlint; do not add frontmatter `type` here.

## Current pages (space `HARBOR`)

| Page | last_modified | Known state |
|---|---|---|
| `HARBOR/stress-test-calculation.md` | 2025-06-14 | **outdated** — threshold and formula differ from the code (see STR-001 open questions) |
| `HARBOR/meeting-flow.md` | 2025-09-02 | mostly correct — mentions a removed "export to spreadsheet" step |
| `HARBOR/product1-overview-tables.md` | 2025-07-21 | partly correct — lists three tables, misses the summary table |
