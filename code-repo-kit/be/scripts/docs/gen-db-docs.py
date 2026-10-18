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
Parsed: CREATE TABLE, ALTER TABLE ADD|DROP COLUMN, COMMENT ON; types and constraints are indicative (regex, no DB).
Example: python3 scripts/docs/gen-db-docs.py --root . --out docs/db"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import read_text, write_text, source_files, posix, rel_path, sort_key, utf8_stdout, load_config, utc_date

DEFAULTS = {'migrations': {'dir_pattern': '/db/migration/', 'file_patterns': ['V*.sql', 'R*.sql']},
            'db_docs': {'dir': 'docs/db', 'generate': True, 'database': {'databaseType': 'postgresql', 'name': '', 'schema': 'public'}}}
SIZE_RX = re.compile(r'^(\w+)\s*\(\s*(\d+)(?:\s*,\s*(\d+))?\s*\)$')


def version_key(path):
    name = os.path.basename(path)
    m = re.match(r'^V(\d+(?:[._]\d+)*)__', name)
    if m:
        parts = [int(x) for x in re.split(r'[._]', m.group(1))]
        if len(parts) == 1:
            parts.append(0)
        return (tuple(parts), name)
    return ((9999, 0), name)


def split_columns(body):
    """Top-level comma split of a CREATE TABLE body (commas inside parentheses stay)."""
    parts, depth, cur = [], 0, []
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            parts.append(''.join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append(''.join(cur))
    return [re.sub(r'\s+', ' ', p.strip()) for p in parts if p.strip()]


def parse_type(t):
    m = SIZE_RX.match(t.strip())
    if not m:
        return t.strip().lower(), 0, 0
    return m.group(1).lower(), int(m.group(2)), int(m.group(3) or 0)


def parse_migrations(root, mig):
    tables = {}   # name -> {'columns': [col], 'source', 'comment', 'checks': [], 'uniques': []}
    files = sorted((f for f in source_files(root, mig['file_patterns']) if re.search(re.escape(mig['dir_pattern']), posix(f), re.I)), key=version_key)
    for f in files:
        sql = re.sub(r'(?m)--[^\n]*', '', read_text(f))
        rel = rel_path(root, f)
        for m in re.finditer(r'(?is)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)\s*;', sql):
            name = m.group(1).lower()
            t = {'columns': [], 'source': rel, 'comment': '', 'checks': [], 'uniques': []}
            for part in split_columns(m.group(2)):
                cm = re.match(r'^(?:CONSTRAINT\s+(\w+)\s+)?(PRIMARY\s+KEY|UNIQUE|FOREIGN\s+KEY|CHECK)\s*(.*)$', part, re.I)
                if cm:
                    kind = cm.group(2).upper().replace('  ', ' ')
                    if kind == 'PRIMARY KEY':
                        for c in re.findall(r'\w+', cm.group(3).split(')')[0]):
                            for col in t['columns']:
                                if col['name'] == c.lower():
                                    col['primaryKey'] = True
                    elif kind == 'FOREIGN KEY':
                        fm = re.match(r'\(([^)]*)\)\s*REFERENCES\s+(\w+)\s*(?:\(([^)]*)\))?', cm.group(3), re.I)
                        if fm:
                            cols = [x.strip().lower() for x in fm.group(1).split(',')]
                            pcols = [x.strip().lower() for x in (fm.group(3) or 'id').split(',')]
                            for col in t['columns']:
                                if col['name'] in cols:
                                    col['references'] = {'table': fm.group(2).lower(), 'columns': pcols, 'constraint': (cm.group(1) or '').lower()}
                    elif kind == 'CHECK':
                        t['checks'].append({'name': (cm.group(1) or '').lower(), 'expression': cm.group(3).strip()})
                    elif kind == 'UNIQUE':
                        t['uniques'].append({'name': (cm.group(1) or '').lower(), 'columns': [x.strip().lower() for x in re.findall(r'\w+', cm.group(3).split(')')[0])]})
                    continue
                dm = re.match(r'^(\w+)\s+(\w+(?:\s*\([^)]*\))?)(.*)$', part)
                if not dm:
                    continue
                rest = dm.group(3)
                typ, size, digits = parse_type(dm.group(2))
                col = {'name': dm.group(1).lower(), 'type': typ, 'size': size, 'digits': digits,
                       'nullable': not re.search(r'NOT\s+NULL', rest, re.I) and not re.search(r'PRIMARY\s+KEY', rest, re.I),
                       'primaryKey': bool(re.search(r'PRIMARY\s+KEY', rest, re.I)),
                       'default': None, 'autoUpdated': typ in ('serial', 'bigserial', 'smallserial') or bool(re.search(r'GENERATED\s+(?:ALWAYS|BY\s+DEFAULT)', rest, re.I)),
                       'comment': '', 'position': len(t['columns'])}
                dfm = re.search(r'DEFAULT\s+((?:\'[^\']*\'|\w+(?:\([^)]*\))?))', rest, re.I)
                if dfm:
                    col['default'] = dfm.group(1)
                fk = re.search(r'REFERENCES\s+(\w+)\s*(?:\(([^)]*)\))?', rest, re.I)
                if fk:
                    col['references'] = {'table': fk.group(1).lower(), 'columns': [x.strip().lower() for x in (fk.group(2) or 'id').split(',')], 'constraint': ''}
                cks = re.search(r'CHECK\s*(\(.*\))', rest, re.I)
                if cks:
                    t['checks'].append({'name': '', 'expression': cks.group(1)})
                t['columns'].append(col)
            tables[name] = t
        for m in re.finditer(r'(?i)ALTER\s+TABLE\s+(\w+)\s+ADD\s+(?:COLUMN\s+)?(\w+)\s+([^,;]+)', sql):
            tn = m.group(1).lower()
            if tn in tables:
                spec = re.sub(r'\s+', ' ', m.group(3)).strip()
                tm = re.match(r'^(\w+(?:\s*\([^)]*\))?)(.*)$', spec)
                typ, size, digits = parse_type(tm.group(1)) if tm else (spec.lower(), 0, 0)
                rest = tm.group(2) if tm else ''
                col = {'name': m.group(2).lower(), 'type': typ, 'size': size, 'digits': digits,
                       'nullable': not re.search(r'NOT\s+NULL', rest, re.I), 'primaryKey': False, 'default': None,
                       'autoUpdated': False, 'comment': '', 'position': len(tables[tn]['columns']), 'addedIn': rel}
                dfm = re.search(r'DEFAULT\s+((?:\'[^\']*\'|\w+(?:\([^)]*\))?))', rest, re.I)
                if dfm:
                    col['default'] = dfm.group(1)
                fk = re.search(r'REFERENCES\s+(\w+)\s*(?:\(([^)]*)\))?', rest, re.I)
                if fk:
                    col['references'] = {'table': fk.group(1).lower(), 'columns': [x.strip().lower() for x in (fk.group(2) or 'id').split(',')], 'constraint': ''}
                tables[tn]['columns'].append(col)
        for m in re.finditer(r'(?i)ALTER\s+TABLE\s+(\w+)\s+DROP\s+(?:COLUMN\s+)?(\w+)', sql):
            tn = m.group(1).lower()
            if tn in tables:
                tables[tn]['columns'] = [c for c in tables[tn]['columns'] if c['name'] != m.group(2).lower()]
        for m in re.finditer(r"(?is)COMMENT\s+ON\s+TABLE\s+(\w+)\s+IS\s+'((?:[^']|'')*)'", sql):
            tn = m.group(1).lower()
            if tn in tables:
                tables[tn]['comment'] = m.group(2).replace("''", "'").strip()
        for m in re.finditer(r"(?is)COMMENT\s+ON\s+COLUMN\s+(\w+)\.(\w+)\s+IS\s+'((?:[^']|'')*)'", sql):
            tn = m.group(1).lower()
            for col in tables.get(tn, {'columns': []})['columns']:
                if col['name'] == m.group(2).lower():
                    col['comment'] = m.group(3).replace("''", "'").strip()
    for t in tables.values():
        for i, col in enumerate(t['columns']):
            col['position'] = i
    return tables


def relations(tables):
    """parents / children per table from the column references."""
    parents = {tn: [] for tn in tables}
    children = {tn: [] for tn in tables}
    for tn, t in tables.items():
        for col in t['columns']:
            ref = col.get('references')
            if not ref:
                continue
            parents[tn].append({'table': ref['table'], 'columns': [col['name']], 'parentColumns': ref['columns'], 'constraint': ref['constraint']})
            children.setdefault(ref['table'], []).append({'table': tn, 'columns': [col['name']], 'parentColumns': ref['columns'], 'constraint': ref['constraint']})
    return parents, children


def type_text(col):
    if col['size'] and col['digits']:
        return f"{col['type']}({col['size']}, {col['digits']})"
    if col['size']:
        return f"{col['type']}({col['size']})"
    return col['type']


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
    erd = ['erDiagram\n']
    for tn in names:
        erd.append(f'  {tn} {{\n')
        for c in tables[tn]['columns']:
            keys = ' '.join(k for k, on in (('PK', c['primaryKey']), ('FK', bool(c.get('references')))) if on)
            erd.append(f"    {c['type']} {c['name']}{(' ' + keys) if keys else ''}\n")
        erd.append('  }\n')
    for tn in names:
        for p in parents.get(tn, []):
            erd.append(f"  {p['table']} ||--o{{ {tn} : {','.join(p['columns'])}\n")
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
