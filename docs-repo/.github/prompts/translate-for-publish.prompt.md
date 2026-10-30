---
name: translate-for-publish
description: Glossary-controlled rendering of an English concept in another language for Confluence publishing (build artifact, not committed).
argument-hint: "path language-code"
agent: agent
---
Translate `${input:path:features/product1/P1-001.md}` into `${input:lang:<language code>}` for Confluence readers.

Rules:
1. Read `domain/glossary.md` first; render every term through its `Term (<lang>)` column (the `Aliases` column only
   confirms a wording, never replaces the column). Terms with an empty cell: keep the English term in parentheses
   after your translation and list them at the end under `## Glossary gaps` so a human fills the cell (prompt
   `translate-glossary`).
2. Do not translate: IDs (`P1-001`, `BR-*`), code identifiers, endpoint paths, `operationId`s, Kafka topics,
   table/column names, formulas, numbers, Gherkin keywords, Mermaid blocks, frontmatter.
3. Prepend the banner: `> Machine translation of the English source in Git (<repo path>). The English version is authoritative; do not edit here.`
   (translated into the target language).
4. Write the result to `.publish/${input:lang}/${input:path}` (git-ignored). Never modify the English source.
Report in chat: number of glossary gaps only.
