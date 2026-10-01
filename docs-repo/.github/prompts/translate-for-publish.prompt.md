---
mode: agent
description: Glossary-controlled Czech rendering of an English concept for Confluence publishing (build artifact, not committed)
---
Translate `${input:path:features/hedges/HEDGE-001.md}` into Czech for Confluence readers.

Rules:
1. Read `domain/glossary.md` first; use the `Czech (cs)` column for every term in it. Terms not in the glossary:
   keep the English term in parentheses after your translation and list them at the end under
   `## Glossary gaps` so a human adds them.
2. Do not translate: IDs (`HEDGE-001`, `BR-*`), code identifiers, endpoint paths, Kafka topics, table/column names,
   formulas, numbers, Gherkin keywords, Mermaid blocks, frontmatter.
3. Prepend the banner: `> Strojový překlad anglického zdroje v Gitu (<repo path>). Závazná je anglická verze; zde neupravujte.`
4. Write the result to `.publish/cs/${input:path}` (git-ignored). Never modify the English source.
Report in chat: number of glossary gaps only.
