# Confluence import (quarantine)

Raw imported pages, one Markdown file per Confluence page with a header block (`source`, `title`, `confluence_id`,
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
  <SPACE>/_done/<section>/       migrated or obsolete pages, mirrored by section (`scripts/import-done.py` moves them and re-points their links; one copy per page, replaced when a newer export is migrated again)
```

Import or re-import (idempotent; `--check` writes nothing and exits 1 when the quarantine is out of date):

```bash
python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --lang cs --base-url https://confluence.example.com
python3 scripts/confluence-import.py --src confluence-import/raw-html --space HARBOR --lang cs --base-url https://confluence.example.com --check
```

`--section business` imports one tree (links to the other tree still resolve), `--no-images` links the images where they
are in the export instead of copying them, `--body html` keeps the body as HTML under the header (the runbook's minimal
form). A page whose `confluence_id` already sits under `_done/` is skipped while the export is not newer than the
migrated copy (both `last_modified` dates must parse; an unparsed date never counts as newer). A page that disappeared
from the export loses its generated file and images (never anything under `_done/`, never a page without
`imported_from`).

**A page that changes after its migration.** When the export's `last_modified` is later than the migrated copy's, the
importer writes the page again as a fresh page in its section folder (`<SPACE>/<section>/<slug>.md`, `status:
imported`) with `supersedes_done:` naming the copy under `_done/` and `supersedes_done_modified:` the copy's date (its
own `last_modified` is the export's). The copy is not touched; the inventory row is the fresh page's with the state
`re-imported, migrated copy <path>` (the date cell says `re-imported` too), the console says the same, and a second run
changes nothing. The agent reruns on the fresh page as on any page (Run 2 again: the specs that cite the copy in
`sources[]` are the targets, the diff against the copy is the work), and `scripts/import-done.py` then **replaces** the
copy (rule 3). The `_attachments/<slug>/` folder of a re-imported page follows the newest export; the copy shares it
until it is replaced.

## Quarantine rules

1. **Nothing in this folder is authoritative.** Pages are evidence of what people once believed, not of what the
   code does. The code and `generated/` win on every conflict; the conflict is recorded as an open question in the
   target spec and in the migration note.
2. Pages are migrated **one at a time** by the agent `confluence-migrator` (`@confluence-migrator
   confluence-import/HARBOR/<page>.md`) into typed concepts under `features/`, `domain/` or `architecture/`;
   the page is cited in the concept's `sources[]` with its `last_modified` date.
3. Processed pages move to `<SPACE>/_done/<section>/` through `python3 scripts/import-done.py <page> --into
   <concept> [--into ...]`, never by hand: the script keeps the section from the page header, writes `status`,
   `migrated` (or `obsolete` with `reason`) and `superseded_by` naming every concept the page went into, and
   re-points the image and page links. `superseded_by` is the backward link (concept `sources[]` is the forward
   one): it answers "where did this page go", and a later rendering or the Confluence publisher builds the old page
   tree with redirects from these headers and `path:`.
   A page carrying `supersedes_done` (the newer export of a page already migrated, see above) **replaces** the copy
   it names: the old file is removed and the new one takes its place under `_done/<section>/` (a changed title or
   section changes the path; pages under `_done/` that linked the old copy are re-pointed), the old `superseded_by`
   entries are carried forward and merged with `--into` (so `--into` may be omitted when the rerun merged nothing
   new), and `earlier_migration:` keeps the copy's migration date and export date. The tree holds one copy per page;
   git history keeps the replaced one, no `<slug>.v<date>.md` is left beside it.
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
   In the generated inventory below only the **Known state** column is hand-edited (it survives a re-import; what to
   write: "Triage" below).

## Triage: the Known state column

**Where.** The last column, **Known state**, of the tables below: "Current pages" for hand-placed pages, and the
generated inventory (between its two `confluence-import:inventory` comment markers), one table per section, one row per
page. In the generated tables every other cell is rewritten on each import; replace the words `to triage` with your
note.

**Who reads it.** People. Nothing parses the note and no agent reads the table: `migration-lead` proposes targets for
unassigned pages in `migration/<scope>.md` (Lead notes), and you confirm or correct them here. When you start the run
for a page, quote its note in the request, for example
`@confluence-migrator confluence-import/<KEY>/business/<page>.md - triage: feature-spec, target ADM-001`.

**What to write.** Three parts, separated by commas, in any wording.

1. **Class**: what the page is about, which decides who takes it.

   | Class | The page describes | Goes to |
   |---|---|---|
   | `feature-spec` | a screen, a modal, business rules, or product behaviour across contexts | `confluence-migrator`, into `features/<context>/<ID>.md`; behaviour across contexts ends up in a flow (`flows/<name>.md`), which `architect` writes from the specs |
   | `calculation` | how a number is computed: a formula, thresholds, rounding, worked examples | `calc-auditor` (`/audit-calculation <page>`), into `domain/calculations/<name>.md`; never merged by hand |
   | `architecture` | what the application is, its parts, integrations, deployment | `architect` (`@architect <page>`, task "Imported page", after `/integrations-from-contracts`), into `architecture/`; a page on what the application is and who uses it goes to `architecture/overview.md` |
   | `decision` | why something was done one way | `architect` (`@architect <page>`), as an ADR under `architecture/adr/` |
   | `glossary` | term definitions | `confluence-migrator`, into `domain/glossary.md` |
   | `process` | how the team works (releases, reviews, onboarding), not what the product does | usually `obsolete`; a procedure that still matters, such as deployment, goes to `architect` as a document under `architecture/` |
   | `obsolete` | nothing the code does any more | `confluence-migrator` (or you): header `status: obsolete` with one line why, page moved to `<KEY>/_done/` |

   Product or process? A page that would still be true after the whole team was replaced is about the product
   (`feature-spec` or `architecture`); one that would change with the people is `process`. A page with two kinds of
   content gets both classes joined by `+` and says which part goes where: the migrator takes the page once and hands
   the formula part to the calc-auditor (or the architecture part to the architect); the last agent that takes the
   page moves it to `_done/`. A screen page that only quotes a threshold stays `feature-spec`: the migrator
   links the calculation instead of copying the value.

2. **Condition**, one of:
   - `current`
   - `partly outdated (<what is wrong>)`
   - `outdated`
   - `formula page`: the substance of the page is a computation; its class is `calculation`
   - `duplicate of <page>`
   - `contains client data (<where>)`: delete it from `raw-html/` and re-import before anyone migrates the page (rule 6)

   Pages older than the last major release are suspects by default.

3. **Target**, when you know it: a spec ID (`ADM-001`), a calculation name (`cover_ratio`), a flow (`flows/<name>.md`)
   or a concept path. Otherwise write `target unknown`: the migrator then finds the target from the page and reports
   it, while a wrong guess sends facts into the less suitable spec. A page about a screen or modal that no spec
   covers yet gets no target and no new spec from the migrator: it leaves a `candidate spec:` open question marked
   `in code` or `not in code`, the board lists it as a shaping decision, and the spec is written before the page is
   rerun: from the code (Run 1) when the code has the capability, by the analyst with proposed rules
   (`/analyse-request`, the page as the request text) when the page describes behaviour still to be built. The
   candidate takes the next free number; the existing specs of the context keep theirs either way.

**Examples of finished cells**

- `feature-spec, current, target ADM-001`
- `feature-spec, partly outdated (export step removed in 2025), target SES-001 and flows/meeting-journey.md`
- `feature-spec + calculation, current, screen rules to ADM-001, premium formula section to cover_ratio`
- `calculation, formula page, target cover_ratio`
- `architecture, current, target architecture/overview.md (purpose, users, system context)`
- `glossary, current`
- `obsolete, module decommissioned 2024`
- `duplicate of business/cover-quote-rules.md`
- `contains client data (screenshot), clean before migration`

**One line, no `|`.** A `|` splits the cell and the importer keeps only the last piece; use commas. The note is kept by
page path: a page renamed in Confluence gets a new file name and its row starts again at `to triage`, and a page
removed from the export loses its row.

**When the note is wrong.** It is a routing hint, not a fact. The migrator classifies the page itself (a formula page
labelled `feature-spec` still goes to the calc-auditor), checks every claim against `generated/`, and reports the
target it chose; the diff of every run is reviewed. The costly mistake is `obsolete` on a page that is not: nobody
migrates it until someone looks again.

**After migration.** When a page moves to `<KEY>/_done/<section>/` (`scripts/import-done.py`), its row takes the
`_done/` path and the importer fills the cell from the page header, for example `migrated 2026-10-28` or `obsolete`;
your triage note is replaced at that moment (the script prints the row). Replace it with a fuller sentence if you like, for example
`migrated 2026-10-28 into ADM-001, 2 conflicts as open questions`: it stays on later imports. In the "Current pages"
table you update the cell yourself.

**A page that changes while still in place.** A page not yet under `_done/` (a `not in code` candidate waiting for
its spec, a context without a skeleton) is rewritten by the next import with the new text and `last_modified`; its
Known state cell stays. Rerun the step the page is in: `/analyse-request` under the same slug when the page is the
text of a request (the analyst rewrites the analysis in place, `spec-writer` adjusts the proposed rules, a rule the
page no longer asks for is withdrawn, never deleted), the migrator when the page waits for a Run 1. A page already
under `_done/` is never rewritten in place and never moved back by hand: when the export is newer than the migrated
copy the importer writes the newer version as a fresh page in its section folder with `supersedes_done` naming the
copy ("A page that changes after its migration" above; inventory state `re-imported, migrated copy <path>`), the
agent reruns on that fresh page, and `scripts/import-done.py` replaces the copy, carrying its `superseded_by`
forward. When the export is not newer the importer skips the page and the inventory keeps the `_done/` row.

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
