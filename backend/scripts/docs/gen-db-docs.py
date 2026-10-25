#!/usr/bin/env python3
"""Database documentation folder from the Flyway migrations: schema.json, one page per table, an ER diagram and an index.
Stands in for a database documentation tool (tbls, SchemaSpy, ...) when none runs in CI; teams that have such a tool
set `db_docs.generate: false` in docs-gen.json and the folder stays what the tool writes. The docs collector copies
the folder as it is, whoever produced it, so both must keep this layout:

  <db_docs.dir>/readme.md                  index: database, tables with their comment, link to the ER diagram
  <db_docs.dir>/schema.json                machine-readable schema (tables, columns, comments, relations)
  <db_docs.dir>/schema/erd/overview.mmd    Mermaid erDiagram of every table
  <db_docs.dir>/schema/tables/<table>.md   description (table comment), columns with comments, relations, constraints

Descriptions are the `COMMENT ON TABLE|COLUMN` statements of the migrations (the data dictionary lives with the DDL).
The DDL is read by _migrations.py (CREATE TABLE, ALTER TABLE ADD|DROP|RENAME|ALTER COLUMN, ADD|DROP CONSTRAINT,
DROP TABLE, COMMENT ON; schema-qualified and quoted names); types and constraints are indicative (regex, no DB).
Example: python3 scripts/docs/gen-db-docs.py --root . --out docs/db"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import write_text, sort_key, utf8_stdout, load_config, utc_date
from _migrations import parse_migrations, relations, type_text, erd_word, erd_label

DEFAULTS = {'migrations': {'dir_pattern': '/db/migration/', 'file_patterns': ['V*.sql', 'R*.sql']},
            'db_docs': {'dir': 'docs/db', 'generate': True, 'database': {'databaseType': 'postgresql', 'name': '', 'schema': 'public'}}}


def md_cell(s):
    return (s or '').replace('|', '\\|').replace('\n', ' ')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='', help='output folder relative to --root (default: db_docs.dir of docs-gen.json)')
    ap.add_argument('--config', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    out_rel = a.out or cfg['db_docs']['dir']
    out = out_rel if os.path.isabs(out_rel) else os.path.join(root, out_rel)
    tables = parse_migrations(root, cfg['migrations'])
    parents, children = relations(tables)
    names = sorted(tables, key=sort_key)
    db = dict(DEFAULTS['db_docs']['database'])
    db.update(cfg['db_docs'].get('database') or {})
    if not db.get('name'):
        db['name'] = os.path.basename(root)
    today = utc_date()

    # ---------- schema.json ----------
    js = {'database': db, 'generatedAt': today, 'generatedBy': 'scripts/docs/gen-db-docs.py (from the migrations)', 'tables': []}
    for tn in names:
        t = tables[tn]
        js['tables'].append({
            'name': tn, 'comment': t['comment'], 'source': t['source'],
            'columns': [{k: c[k] for k in ('autoUpdated', 'comment', 'default', 'digits', 'name', 'nullable', 'position', 'primaryKey', 'size', 'type')} for c in t['columns']],
            'parents': parents.get(tn, []), 'children': children.get(tn, []),
            'checks': t['checks'], 'uniques': t['uniques'],
        })
    # what this script owns under --out: schema.json, readme.md, schema/index.md, schema/tables/*.md, schema/erd/*.mmd.
    # Pages of tables dropped since the last run are removed file by file at the end; no folder is deleted and nothing
    # outside --out is touched
    os.makedirs(os.path.join(out, 'schema', 'tables'), exist_ok=True)
    os.makedirs(os.path.join(out, 'schema', 'erd'), exist_ok=True)
    written = set()

    def emit(path, text):
        write_text(path, text)
        written.add(os.path.normcase(os.path.abspath(path)))
    write_text(os.path.join(out, 'schema.json'), json.dumps(js, indent=2, ensure_ascii=False) + '\n')

    # ---------- ER diagram ----------
    # Mermaid erDiagram: `type name PK, FK` (the keys comma-separated), type and name single words, a relationship per
    # foreign key labelled with its column(s)
    erd = ['erDiagram\n']
    for tn in names:
        erd.append(f'  {erd_word(tn)} {{\n')
        for c in tables[tn]['columns']:
            keys = ', '.join(k for k, on in (('PK', c['primaryKey']), ('FK', bool(c.get('references')))) if on)
            erd.append(f"    {erd_word(c['type'])} {erd_word(c['name'])}{(' ' + keys) if keys else ''}\n")
        erd.append('  }\n')
    for tn in names:
        for p in parents.get(tn, []):
            erd.append(f"  {erd_word(p['table'])} ||--o{{ {erd_word(tn)} : {erd_label(p['columns'])}\n")
    emit(os.path.join(out, 'schema', 'erd', 'overview.mmd'), ''.join(erd))

    # ---------- one page per table ----------
    for tn in names:
        t = tables[tn]
        sb = [f'# {tn}\n\n', (t['comment'] or '_No table comment (COMMENT ON TABLE) in the migrations._') + '\n\n',
              f"Created in `{t['source']}`. Diagram: [ER overview](../erd/overview.mmd).\n\n",
              '## Columns\n\n| Column | Type | Nullable | Default | Key | Comment |\n|---|---|---|---|---|---|\n']
        for c in t['columns']:
            key = ', '.join(k for k in (('PK' if c['primaryKey'] else ''), (f"FK -> [{c['references']['table']}]({c['references']['table']}.md)" if c.get('references') else '')) if k)
            sb.append(f"| `{c['name']}` | {type_text(c)} | {'yes' if c['nullable'] else 'no'} | {md_cell(c['default'] or '')} | {key} | {md_cell(c['comment'])} |\n")
        rel_lines = []
        for p in parents.get(tn, []):
            rel_lines.append(f"- `{', '.join(p['columns'])}` references [{p['table']}]({p['table']}.md) (`{', '.join(p['parentColumns'])}`)")
        for c in children.get(tn, []):
            rel_lines.append(f"- referenced by [{c['table']}]({c['table']}.md).`{', '.join(c['columns'])}`")
        sb.append('\n## Relations\n\n' + ('\n'.join(rel_lines) if rel_lines else '_none_') + '\n')
        if t['checks'] or t['uniques']:
            sb.append('\n## Constraints\n\n')
            for u in t['uniques']:
                sb.append(f"- unique{(' `' + u['name'] + '`') if u['name'] else ''}: `{', '.join(u['columns'])}`\n")
            for ck in t['checks']:
                sb.append(f"- check{(' `' + ck['name'] + '`') if ck['name'] else ''}: `{ck['expression']}`\n")
        emit(os.path.join(out, 'schema', 'tables', f'{tn}.md'), ''.join(sb))
    # stale pages of our own output (tables dropped since the last run): files only, inside the two folders above
    for sub, ext in (('tables', '.md'), ('erd', '.mmd')):
        d = os.path.join(out, 'schema', sub)
        for fn in os.listdir(d):
            p = os.path.join(d, fn)
            if fn.lower().endswith(ext) and os.path.isfile(p) and os.path.normcase(os.path.abspath(p)) not in written:
                os.remove(p)

    # ---------- indexes ----------
    rows = ''.join(f"| [{tn}](schema/tables/{tn}.md) | {md_cell(tables[tn]['comment'])} | {len(tables[tn]['columns'])} |\n" for tn in names)
    write_text(os.path.join(out, 'readme.md'),
               f"# Database documentation: {db['name']}\n\n"
               f"{db['databaseType']}, schema `{db['schema']}`; {len(names)} table(s). Generated from the migrations by "
               f"`scripts/docs/gen-db-docs.py` on {today}; descriptions are the `COMMENT ON` statements. "
               'Machine-readable: [schema.json](schema.json). Diagram: [ER overview](schema/erd/overview.mmd).\n\n'
               '| Table | Description | Columns |\n|---|---|---|\n' + rows)
    write_text(os.path.join(out, 'schema', 'index.md'),
               f"# Tables of {db['name']}\n\n" + ''.join(f"- [{tn}](tables/{tn}.md): {tables[tn]['comment']}\n" for tn in names))
    print(f'db-docs: {len(names)} table(s) -> {out_rel}')


if __name__ == '__main__':
    main()
