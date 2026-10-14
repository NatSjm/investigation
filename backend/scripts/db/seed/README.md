# Named datasets (local seeds)

Synthetic data for a developer database. One file per **dataset**; the file header is the contract that
`scripts/docs/gen-datasets.py` reads to build `docs/_generated/datasets.md` (collected into the docs repo as
`generated/be/datasets.md`), so analysts and test designers can cite a setup by name instead of describing rows.

```sql
-- dataset: p1-baseline-12m              required, kebab-case, unique across seeds and test fixtures
-- purpose: one sentence                 required
-- tables: client_profile, movement_monthly   optional; derived from INSERT/DELETE statements when missing
-- depends: reference-clients            optional; datasets that must be loaded first
-- synthetic: yes                        required; a dataset without it is flagged in the catalogue
```

Rules:
- Idempotent: start with `DELETE ... WHERE` on the rows you own or use `ON CONFLICT DO NOTHING`; the runner may be
  re-run any time.
- Synthetic only: fixed UUIDs, `<WORD>-SYN` client ids, round quantities, prices with 2 dp; never a production or
  UAT extract, even anonymised (`docs-repo/test-design/fixtures/README.md` has the patterns).
- Files run in name order (`10-`, `20-`, ...); `depends:` is documentation for the catalogue, not a resolver.
- Integration-test fixtures live in `core/src/test/resources/datasets/` with the same header and are listed in the
  same catalogue (kind `fixture`); tests load them with `@Sql("/datasets/<name>.sql")`.

Run: `scripts/db/seed-local.py` (all) or `scripts/db/seed-local.py --dataset p1-baseline-12m`.
