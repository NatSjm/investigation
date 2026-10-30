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
- [ ] exactly one page processed; every spec it touches named from the catalogue (a context given in the message was a primary target, not a filter)
- [ ] only new facts merged, each into the spec of the context that owns the behaviour; a cross-context sequence went to a flow or an Open question, not to two specs
- [ ] contradictions as `> ⚠️ CONFLICT (legacy: <page>)`; unverifiable as `> ❓ UNVERIFIED`
- [ ] no number, threshold or formula copied from the page
- [ ] `sources[]` entry `conf-<slug>` with `last_modified` in every spec touched; citations `[^conf-<slug>]`
- [ ] new terms in `domain/glossary.md` (Aliases column for the legacy wording)
- [ ] no spec created, no spec renumbered: a capability no spec covers is a `- [ ] candidate spec: <title> (legacy conf-<slug>; owner: migration lead; in code | not in code) - ...` line under the primary spec's Open questions (the board lists it as a shaping decision with the run that follows: Run 1 with the next free number when in code, `/analyse-request` with proposed rules when not)
- [ ] page moved by `scripts/legacy-done.py` (under `_done/<section>/`, `status: migrated | obsolete`, `superseded_by` naming every concept it went into, links re-pointed) - only when every context it describes has a spec and no candidate is pending; otherwise left in place with the pending part as an Open question
- [ ] the page title in the `aliases` of every spec touched
- [ ] an architecture, decision or process part was handed to `architect` (the last agent moves the page)
- [ ] no client data, screenshots or personal names

## Run 3 - calculation (`calc-auditor`)
- [ ] exactly two source files opened: calculator and its unit test (named in chat with line ranges)
- [ ] `## Audit <date>` table with one row per claim; severities `MATCH / DOC-STALE / CODE-SUSPECT / UNDOCUMENTED`
- [ ] worked examples replaced only by values copied from the test, test method named
- [ ] non-MATCH -> `status: draft` + open question naming the owner; `used_by` specs listed in chat
- [ ] legacy formula page cited in the concept's `sources[]`, moved by `scripts/legacy-done.py` (`superseded_by` the concept) when the auditor is the last agent to take it (screen rules merged by the migrator before, or none); screen rules of a mixed page handed to `confluence-migrator`, never merged by the auditor

## Run 4 - owner decision (human)
- [ ] each open question answered in place on its item with date, `human:<id>` and reference; one `features/<ctx>/log.md` line
- [ ] each rule checked against the symbol its `(source: ...)` marker names (the method, not the file); the markers stay
- [ ] `verified: { by: human:<id>, at: <ISO> }` and `stale_after` (+90 days) added; `status: stable`
- [ ] legacy page keeps `superseded_by: <concept>` for the audit trail
- [ ] `build-index.py` run; badge shows *human-reviewed*
