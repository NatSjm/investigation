#!/usr/bin/env python3
"""Approximate DB schema from Flyway SQL migrations (CREATE TABLE / ALTER TABLE ADD|DROP COLUMN). No database needed."""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, posix,
                     sort_key, utf8_stdout)


def version_key(path):
    name = os.path.basename(path)
    m = re.match(r'^V(\d+(?:[._]\d+)*)__', name)
    if m:
        parts = [int(x) for x in re.split(r'[._]', m.group(1))]
        if len(parts) == 1:
            parts.append(0)
        return (tuple(parts), name)
    return ((9999, 0), name)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/db-schema.md')
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    tables = {}
    migrations = sorted((f for f in source_files(root, ['V*.sql', 'R*.sql']) if re.search(r'/(migration|db)/', posix(f), re.I)),
                        key=version_key)
    for f in migrations:
        sql = read_text(f)
        rel = rel_path(root, f)
        for m in re.finditer(r'(?is)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\((.*?)\)\s*;', sql):
            name = m.group(1).lower()
            cols = {}
            for line in re.split(r',\s*\r?\n', m.group(2), flags=re.I):
                l = line.strip()
                if re.match(r'^(PRIMARY\s+KEY|CONSTRAINT|UNIQUE|FOREIGN\s+KEY|CHECK)', l, re.I):
                    continue
                cm = re.match(r'^(\w+)\s+(\w+(?:\s*\([^)]*\))?)(.*)$', l)
                if cm:
                    col_name = cm.group(1).lower()
                    col_type = cm.group(2)
                    rest = cm.group(3)
                    flags = []
                    if re.search(r'PRIMARY\s+KEY', rest, re.I):
                        flags.append('PK')
                    if re.search(r'NOT\s+NULL', rest, re.I):
                        flags.append('NN')
                    fk = re.search(r'REFERENCES\s+(\w+)', rest)
                    if fk:
                        flags.append(f'FK->{fk.group(1).lower()}')
                    cols[col_name] = f"{col_type} {' '.join(flags)}".strip()
            tables[name] = {'cols': cols, 'src': rel}
        for m in re.finditer(r'(?i)ALTER\s+TABLE\s+(\w+)\s+ADD\s+(?:COLUMN\s+)?(\w+)\s+([^,;]+)', sql):
            tn = m.group(1).lower()
            if tn in tables:
                tables[tn]['cols'][m.group(2).lower()] = re.sub(r'\s+', ' ', m.group(3)).strip() + f' (+{rel})'
        for m in re.finditer(r'(?i)ALTER\s+TABLE\s+(\w+)\s+DROP\s+(?:COLUMN\s+)?(\w+)', sql):
            tn = m.group(1).lower()
            if tn in tables:
                tables[tn]['cols'].pop(m.group(2).lower(), None)

    # which classes reference each table in code (@Table(name = "x"), JPA/JDBC SQL strings) - lets the docs graph
    # attribute a table to the bounded context (class-name prefix) that owns it instead of where the migrations live
    kt_files = [f for f in source_files(root, ['*.kt']) if re.search(r'/src/main/', posix(f), re.I)]
    kt_text = {k: read_text(k) for k in kt_files}
    for tn in tables:
        rx = re.compile(r'(?i)["`\' ]' + re.escape(tn) + r'["`\' \s(,;]')
        mods = sorted(set(os.path.splitext(os.path.basename(k))[0] for k in kt_files if rx.search(kt_text[k])), key=sort_key)   # classes (one class per file)
        tables[tn]['usedIn'] = mods

    sb = [header('DB schema (approximate, from migrations)', 'Flyway V*.sql')]
    sb.append(f'{len(tables)} table(s). Derived by regex from migrations - types/constraints are indicative; verify against a real DB for DDL work.\n\n')
    sb.append('```mermaid\nerDiagram\n')
    for tn, tbl in tables.items():
        for c, spec in tbl['cols'].items():
            fk = re.search(r'FK->(\w+)', spec, re.I)
            if fk:
                sb.append(f'  {fk.group(1)} ||--o{{ {tn} : {c}\n')
    sb.append('```\n\n')
    for tn, tbl in tables.items():
        sb.append(f'## `{tn}`\nCreated in `{tbl["src"]}`\n')
        used = tbl['usedIn']
        sb.append('Used in: ' + (', '.join('`' + u + '`' for u in used) if used else '_no code reference found_') + '\n\n')
        sb.append('| Column | Type / flags |\n|---|---|\n')
        for c, spec in tbl['cols'].items():
            sb.append(f'| `{c}` | {escape_cell(spec)} |\n')
        sb.append('\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'db-schema: {len(tables)} table(s) -> {a.out}')


if __name__ == '__main__':
    main()
