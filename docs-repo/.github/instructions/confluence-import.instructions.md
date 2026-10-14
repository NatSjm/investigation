---
applyTo: "confluence-import/**"
description: Quarantine rules for imported legacy pages - evidence to be verified, never a source of truth.
---

# Imported legacy pages

- Files here are raw exports (`scripts/confluence-export.py`). They may be outdated, duplicated or wrong.
  Do not link to them from specs as facts; cite them in `sources[]` and verify every claim against
  `generated/` (contracts, maps, graph) or the code via `docs-tags.md` before it enters a concept.
- Do not edit a page in place except to add the header block (`source`, `last_modified`, `author`, `status: imported|migrated|obsolete`).
- Migrated pages move to `confluence-import/_done/`; obsolete pages get `status: obsolete` and one line why.
- Numbers, formulas, thresholds and field names in legacy pages are the most likely to be stale - a formula page
  is handled by `calc-auditor` (compare with the unit test), not copied by `confluence-migrator`.
- Never copy client data, screenshots with real data or personal names into concepts.
