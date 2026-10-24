# Run checklist (copy into the review of each run)

## Run 1 - skeleton (`spec-writer`)
- [ ] API / Events / Data / UI flow filled from `generated/graph/<ctx>.md` and the contracts, names exact
- [ ] Summary / Actors / Business rules from the manager KDoc only (or the entry file the call named, for a second screen of a context with one entry class per screen); each BR one MUST / MUST NOT assertion
- [ ] `code_refs` from node locations (file only), `context`, `api`, `events`, `tables` set
- [ ] `api[]` holds only operations handled in this context; a called operation of another context is in the API table with `owned by <SPEC-ID>`
- [ ] every rule ends with a `(source: code manager#<method>)` marker naming the symbol it came from, never a line range
- [ ] `status: draft`, `generated.by: copilot/spec-writer`, no `verified`
- [ ] `docs-map.yml` mapping added or confirmed; `log.md` line "created <ID>"
- [ ] everything unsourced is under Open questions, not invented

## Run 2 - legacy merge (`confluence-migrator`)
- [ ] exactly one page processed
- [ ] only new facts merged; contradictions as `> ⚠️ CONFLICT (legacy: <page>)`; unverifiable as `> ❓ UNVERIFIED`
- [ ] no number, threshold or formula copied from the page
- [ ] `sources[]` entry `conf-<slug>` with `last_modified`; citations `[^conf-<slug>]`
- [ ] new terms in `domain/glossary.md` (Aliases column for the legacy wording)
- [ ] page moved to `confluence-import/<SPACE>/_done/` with header `status: migrated | obsolete`
- [ ] no client data, screenshots or personal names

## Run 3 - calculation (`calc-auditor`)
- [ ] exactly two source files opened: calculator and its unit test (named in chat with line ranges)
- [ ] `## Audit <date>` table with one row per claim; severities `MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED`
- [ ] worked examples replaced only by values copied from the test, test method named
- [ ] non-MATCH -> `status: draft` + open question naming the owner; `used_by` specs listed in chat
- [ ] legacy formula page header set to `obsolete | migrated`

## Run 4 - owner decision (human)
- [ ] each open question answered; decision recorded as a Change log row with date and reference
- [ ] each rule checked against the symbol its `(source: ...)` marker names (the method, not the file); the markers stay
- [ ] `verified: { by: human:<id>, at: <ISO> }` and `stale_after` (+90 days) added; `status: stable`
- [ ] legacy page keeps `superseded_by: <concept>` for the audit trail
- [ ] `build-index.py` run; badge shows *human-reviewed*
