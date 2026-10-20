# Confluence import (quarantine)

Raw legacy pages, one Markdown file per Confluence page with a header block (`source`, `title`, `confluence_id`,
`url`, `author`, `last_modified`, `status`). Two ways in:

- **HTML export** (the standard "Export space to HTML", or the same pages re-arranged one folder per page): the export
  is kept as received under `raw-html/<section>/` (never edited, never read by agents) and
  `scripts/confluence-import.py` turns it into `<SPACE>/<section>/<slug>.md`, a section being one page tree of the
  space (here `business` and `technical`). Images the page shows are copied to `<SPACE>/_attachments/<slug>/` and
  linked relatively; the page tree survives in the `path:` and `parent:` headers; links between exported pages become
  links between the Markdown files. Everything else the body carries (tables, code, panels, expand sections, task
  lists) is converted to GitHub Markdown; what the converter does not know is kept as raw HTML with a comment.
- **REST export** (`scripts/confluence-export.py`, a stub): `<SPACE>/<page-title>.md` directly under the space folder,
  as the hand-placed example pages `HARBOR/meeting-flow.md` and `HARBOR/stress-test-calculation.md`.
- **A Markdown file from elsewhere** (a knowledge base another team generated, such as a tester's RAG knowledge base
  `rag.md`, or an onboarding page an agent wrote from the code): hand-placed as `<SPACE>/<name>.md` with the header
  block above (`source` = where it came from, `author`, `last_modified` = the day it was generated, `status: imported`)
  and a row in the "Current pages" table below. **Never under `raw-html/`**: that folder holds only the HTML export,
  the importer reads only `.html` files there and agents never open it, so a Markdown file put there is invisible.
  Without an `imported_from` header the importer never rewrites or removes it; `confluence-migrator` takes it section
  by section (`ENTERPRISE-PLAYBOOK.md`, "A knowledge base another team already generated").

```
confluence-import/
  README.md                      rules + inventory (the generated part sits between its markers)
  raw-html/<section>/            the HTML export as received (one folder per section = page tree)
  <SPACE>/<section>/<slug>.md    imported pages (header `imported_from` = regenerated, do not edit in place)
  <SPACE>/_attachments/<slug>/   images the pages show (binary, see .gitattributes)
  <SPACE>/_done/                 migrated or obsolete pages (same depth as a section, so image links keep working)
```

Import or re-import (idempotent; `--check` writes nothing and exits 1 when the quarantine is out of date):

```bash
python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --lang cs --base-url https://confluence.example.com
python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --lang cs --base-url https://confluence.example.com --check
```

`--section business` imports one tree (links to the other tree still resolve), `--no-images` links the images where they
are in the export instead of copying them, `--body html` keeps the body as HTML under the header (the runbook's minimal
form). A page whose `confluence_id` already sits under `_done/` is never rewritten; when the export is newer than the
migrated copy the inventory says so (Run 2 again). A page that disappeared from the export loses its generated file
and images (never anything under `_done/`, never a page without `imported_from`).

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
   (`scripts/confluence-publish.py`).
6. Only the images a page shows are imported (`_attachments/<slug>/`, listed in the page's `attachments:` header);
   other attachments are named in `attachments_not_imported:` and never copied. A screenshot or table containing
   client data is deleted from `raw-html/` before the import (or the generated copy before the commit) - the
   synthetic data rule applies to images too. An imported screenshot is evidence of what a screen looked like; a spec
   may link it from its screenshots section only when it shows synthetic data.
7. This folder is excluded from `okf-validate.py` and markdownlint; do not add frontmatter `type` here.
8. Pages with an `imported_from` header are generated: fix the export or the importer and re-run, never the page.
   In the generated inventory below only the **Known state** column is hand-edited (it survives a re-import).

## Current pages (space `HARBOR`)

| Page | last_modified | Known state |
|---|---|---|
| `HARBOR/stress-test-calculation.md` | 2025-06-14 | **outdated** — threshold and formula differ from the code (see STR-001 open questions) |
| `HARBOR/meeting-flow.md` | 2025-09-02 | mostly correct — mentions a removed "export to spreadsheet" step |
| `HARBOR/_done/product1-overview-tables.md` | 2025-07-21 | **migrated** 2026-10-12 into P1-001 — three tables (summary and totals missing), 2 conflicts recorded as open questions |

## Imported pages (space `HARBOR`, generated)

<!-- confluence-import:inventory HARBOR -->
> Generated by `scripts/confluence-import.py` from the HTML export; edit only the **Known state** column (kept on re-import). Pages: 4 imported, 0 already in `_done/`.

### business

| Page | confluence_id | last_modified | author | Images | Guessed context | Known state |
|---|---|---|---|---|---|---|
| `confluence-import/HARBOR/business/admin-parameters-page.md` | 48103700 | 2025-10-03 | John Roe | 1 | admin | to triage |
| `confluence-import/HARBOR/business/cover-quote-rules.md` | 48103701 | 2025-09-02 | Jane Doe | 0 | meetings, cover | to triage |

### technical

| Page | confluence_id | last_modified | author | Images | Guessed context | Known state |
|---|---|---|---|---|---|---|
| `confluence-import/HARBOR/technical/deployment-notes.md` | 48103801 | 2025-10-01 | Tom Brown | 1 | - | to triage |
| `confluence-import/HARBOR/technical/kafka-topics.md` | 48103800 | 2025-09-02 | Tom Brown | 0 | - | to triage |

<!-- /confluence-import:inventory HARBOR -->
