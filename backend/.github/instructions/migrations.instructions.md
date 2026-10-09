---
applyTo: "**/src/main/resources/db/migration/*.sql"
description: "Flyway migrations: new versioned file per change, one column per line, inline REFERENCES, never edit an applied migration."
---
# Flyway migrations (`core/src/main/resources/db/migration`)

- Never edit a migration that has been applied anywhere (any `V<n>` already on `main`). Add `V<next>__<short_name>.sql` instead,
  including for column renames and type changes (`ALTER TABLE ... ADD COLUMN`, backfill, drop in a later migration).
- One column per line in `CREATE TABLE`; type, nullability and default on the same line; primary key on the id line.
  `gen-db-schema.ps1` parses this layout into `docs/_generated/db-schema.md`.
- Foreign keys inline: `client_id uuid NOT NULL REFERENCES client_profile(id)` - the ER diagram is built from `REFERENCES`.
- Names: `snake_case` tables and columns, singular table names (`meeting_session`, `goods_movement`, `cover_policy`),
  `uuid` ids, `timestamp` for instants, `date` for monthly periods (first day of month), `numeric` for quantities/prices/values.
- Session-scoped tables carry `session_id uuid NOT NULL REFERENCES meeting_session(id)` as the first column after the id.
- No data migrations with business logic in SQL; grouping and aggregation belong to `harbor/utils`.
- After adding a migration run `scripts/docs/gen-all.ps1` and commit `db-schema.md` (and `components.md` if a DAO changed) with it.
