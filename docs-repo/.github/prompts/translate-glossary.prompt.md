---
name: translate-glossary
description: Fill the `Term (<lang>)` column of domain/glossary.md - the one term the team uses for each concept in that language - from the frontend translation file and the imported pages in that language; a term found nowhere is proposed and listed under Open questions for an owner.
argument-hint: "language-code [translation-file ...] [overwrite]"
agent: agent
---
Fill the `Term (${input:lang:cs})` column of `domain/glossary.md`.
Translation file(s): `${input:i18n:../frontend/src/i18n/cs.json}` - the frontend's translation JSON for that language,
with its English counterpart beside it when there is one; a missing file is allowed and reported.

Rules:
1. Read `domain/glossary.md`. The column `Term (<lang>)` sits right after `Term`; add it when it is missing, with an
   empty cell in every row (the scripts find the columns by header, so the order of the other columns never changes).
   Change nothing else in the table: `Term`, `Definition`, `Aliases` and `Used in` stay as they are, and a non-empty
   `Term (<lang>)` cell is the owner's and stays unless the message says `overwrite`.
2. For every row with an empty cell find the word the team uses, in this order, stopping at the first hit:
   a. the translation file: the value whose key the English file (or the key name) ties to the term or one of its
      aliases, case-insensitively - the label the screen shows is what people say;
   b. an imported page in that language (`source_lang: <lang>` under `confluence-import/`, `_done/` included, and
      the raw export it names in `imported_from`): the word the page uses for the concept, read with the definition
      in mind, never matched on the English word alone;
   c. the `Aliases` cell when it already holds a word of that language;
   d. your own translation.
3. Write the nominative singular, lowercase unless a proper noun; one term per cell; the English word itself when
   (a) or (b) shows the team keeps it. A second wording found in (a) or (b) goes to `Aliases`, never into the cell.
   Identifiers in backticks and IDs are never translated. When the screen (a) and a page (b) disagree, the screen
   wins and the page's wording goes to `Aliases`. The same word for two terms is a collision: leave the second cell
   empty and ask under Open questions.
4. A term from (c) or (d) is a proposal: list it under `## Open questions` of the glossary (create the section after
   the table when it is missing) as `- [ ] <lang> "<term>" (<Term>): proposed, unsourced - owner confirms or replaces`,
   one line per term; the owner ticks the line or replaces the cell. Terms from (a) and (b) get no line.
5. Keep the frontmatter and the header prose; `status` and `generated` are the owner's. Then run
   `python3 scripts/gen-catalogue.py` (the catalogue carries the column), `python3 scripts/okf-validate.py --strict`
   and `python3 scripts/build-index.py`. The first fill of a column gets one line in the root `log.md`
   ("Glossary: `Term (<lang>)` column filled - <n> from the translation file, <n> from pages, <n> proposed"); a rerun
   that filled a few cells gets none.
Report in chat (<= 6 lines): cells filled from the translation file, from pages, proposed; collisions; cells left
empty; whether the translation file was found.
