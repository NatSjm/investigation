#!/usr/bin/env python3
"""Approximate DB schema from Flyway SQL migrations (CREATE TABLE, ALTER TABLE ADD|DROP|RENAME|ALTER COLUMN, ADD|DROP
CONSTRAINT, DROP TABLE; read by _migrations.py). No database needed.
Migrations are the SQL files matching `migrations.file_patterns` under a folder matching `migrations.dir_pattern`
(docs-gen.json). Views are the files matching `migrations.view_patterns` under that folder or under any folder of
`migrations.view_dirs`. Liquibase changelogs (XML/YAML) are not parsed; point the pattern at the SQL-formatted changelogs."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, posix,
                     sort_key, utf8_stdout, load_config, module_dirs, main_sources)
from _migrations import parse_migrations, relations, type_text, erd_word, erd_label

DEFAULTS = {'modules': [], 'source_root': 'src/main/kotlin', 'test_pattern': '', 'exclude_paths': [],
            'migrations': {'dir_pattern': '/db/migration/', 'file_patterns': ['V*.sql', 'R*.sql'], 'view_patterns': [],
                           'view_dirs': []}}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/db-schema.md')
    ap.add_argument('--config', default='')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    mig = cfg['migrations']

    # columns as `type flags` (PK, NN, FK->parent; `(+<migration>)` when a later migration added the column), one
    # relationship per foreign key
    parsed = parse_migrations(root, mig)
    parents, _ = relations(parsed)
    tables = {}
    for tn, t in parsed.items():
        cols = {}
        for c in t['columns']:
            flags = [f for f, on in (('PK', c['primaryKey']), ('NN', not c['nullable'] and not c['primaryKey']),
                                     (f"FK->{c.get('references', {}).get('table', '')}", bool(c.get('references')))) if on]
            cols[c['name']] = f"{type_text(c)} {' '.join(flags)}".strip() + (f" (+{c['addedIn']})" if c.get('addedIn') else '')
        tables[tn] = {'cols': cols, 'src': t['source'], 'fks': parents.get(tn, [])}

    # views: SQL files matching migrations.view_patterns under the migrations folder or under any of migrations.view_dirs
    # (CREATE [OR REPLACE] VIEW ... AS SELECT ...)
    view_dirs = [mig['dir_pattern']] + list(mig.get('view_dirs') or [])
    views = {}
    for f in sorted((f for f in source_files(root, mig.get('view_patterns', []))
                     if any(re.search(re.escape(d), posix(f), re.I) for d in view_dirs)), key=sort_key):
        sql = read_text(f)
        rel = rel_path(root, f)
        for m in re.finditer(r'(?is)CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)\s+AS\s+(.*?);', sql):
            body = m.group(2)
            sel = re.split(r'(?is)\bFROM\b', body, maxsplit=1)[0]
            sel = re.sub(r'(?is)^\s*SELECT\s+', '', sel)
            cols = []
            for part in re.split(r',\s*(?![^()]*\))', sel):   # commas outside parentheses
                part = part.strip()
                am = re.search(r'(?is)\bAS\s+(\w+)\s*$', part)
                cols.append((am.group(1) if am else part.split('.')[-1].strip()).lower())
            froms = [x.lower() for x in re.findall(r'(?i)\b(?:FROM|JOIN)\s+(\w+)', body)]
            views[m.group(1).lower()] = {'cols': cols, 'from': sorted(set(froms), key=sort_key), 'src': rel}

    # which classes reference each table in code (@Table(name = "x"), JPA/JDBC SQL strings) - lets the docs graph
    # attribute a table to the bounded context (class-name prefix) that owns it instead of where the migrations live
    kt_files = main_sources(root, cfg, module_dirs(root, cfg))
    kt_text = {k: read_text(k) for k in kt_files}
    for tn in tables:
        rx = re.compile(r'(?i)["`\' ]' + re.escape(tn) + r'["`\' \s(,;]')
        mods = sorted(set(os.path.splitext(os.path.basename(k))[0] for k in kt_files if rx.search(kt_text[k])), key=sort_key)   # classes (one class per file)
        tables[tn]['usedIn'] = mods

    sb = [header('DB schema (approximate, from migrations)', f"migrations {', '.join(mig['file_patterns'])} under {mig['dir_pattern']}")]
    sb.append(f'{len(tables)} table(s). Derived by regex from migrations - types/constraints are indicative; verify against a real DB for DDL work.\n\n')
    sb.append('```mermaid\nerDiagram\n')
    for tn, tbl in tables.items():
        for fk in tbl['fks']:
            sb.append(f"  {erd_word(fk['table'])} ||--o{{ {erd_word(tn)} : {erd_label(fk['columns'])}\n")
    sb.append('```\n\n')
    for tn, tbl in tables.items():
        sb.append(f'## `{tn}`\nCreated in `{tbl["src"]}`\n')
        used = tbl['usedIn']
        sb.append('Used in: ' + (', '.join('`' + u + '`' for u in used) if used else '_no code reference found_') + '\n\n')
        sb.append('| Column | Type / flags |\n|---|---|\n')
        for c, spec in tbl['cols'].items():
            sb.append(f'| `{c}` | {escape_cell(spec)} |\n')
        sb.append('\n')
    if views:
        sb.append('## Views\n')
        sb.append('Statistical / reporting views defined next to the migrations (not versioned by Flyway; applied by the application or by hand).\n\n')
        sb.append('| View | Columns | From tables | Source |\n|---|---|---|---|\n')
        for vn in sorted(views, key=sort_key):
            v = views[vn]
            sb.append(f"| `{vn}` | {', '.join('`' + c + '`' for c in v['cols'])} | {', '.join('`' + x + '`' for x in v['from'])} | `{v['src']}` |\n")
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'db-schema: {len(tables)} table(s), {len(views)} view(s) -> {a.out}')


if __name__ == '__main__':
    main()
