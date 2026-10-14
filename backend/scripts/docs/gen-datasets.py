#!/usr/bin/env python3
"""Dataset catalogue: every named dataset (local seed under scripts/db/seed, integration-test fixture under
src/test/resources/datasets) with its purpose, tables and row counts, dependencies, the tests that load it and
one sample row per table. Lets analysts and test designers cite a setup by name ("Given dataset "x" is loaded")
instead of describing rows, without opening the code repository. Names and shape only: the sample row is the
first tuple of each table and is included only when the header declares `synthetic: yes`.

Header contract (first comment block of the .sql file):
  -- dataset: <kebab-name>      -- purpose: <one sentence>      -- tables: a, b (optional)
  -- depends: x, y (optional)   -- synthetic: yes|no"""
import argparse
import os
import re

from _common import (read_text, write_text, source_files, resolve_out, rel_path, header, escape_cell, posix,
                     sort_key, utf8_stdout)

TUPLE_RX = re.compile(r'\((?P<tuple>(?:[^()]|\([^()]*\))*)\)')
INSERT_RX = re.compile(r'(?is)INSERT\s+INTO\s+(?P<table>[a-z_][a-z0-9_]*)\s*\((?P<cols>[^)]*)\)\s*VALUES\s*(?P<vals>.*?);')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/datasets.md')
    ap.add_argument('--sample-chars', type=int, default=140)
    a = ap.parse_args()
    root = os.path.abspath(a.root)

    rows = []
    unnamed = 0
    sql_files = sorted((f for f in source_files(root, ['*.sql']) if not re.search(r'/db/migration/', posix(f), re.I)), key=sort_key)
    for f in sql_files:
        t = read_text(f)
        rel = rel_path(root, f)
        # header: leading `-- key: value` lines
        hdr = {}
        for line in re.split(r'\r?\n', t):
            m = re.match(r'^\s*--\s*([a-z_]+)\s*:\s*(.*)$', line, re.I)
            if m:
                hdr[m.group(1)] = m.group(2).strip()
            elif line.strip() and not re.match(r'^\s*--', line):
                break
        if 'dataset' not in hdr:
            unnamed += 1
            continue
        kind = 'fixture' if re.search(r'/test/', posix(f), re.I) else 'seed'
        synthetic = hdr.get('synthetic', '').lower() == 'yes'

        # tables and row counts from INSERT statements; DELETE/UPDATE targets count as touched
        counts = {}
        samples = {}
        for ins in INSERT_RX.finditer(t):
            tbl = ins.group('table')
            vals0 = re.sub(r'(?is)\s+ON\s+CONFLICT.*$', '', ins.group('vals'))   # upsert clause is not a row
            tuples = list(TUPLE_RX.finditer(vals0))
            counts[tbl] = counts.get(tbl, 0) + len(tuples)
            if synthetic and tuples and tbl not in samples:
                cols = [c.strip() for c in ins.group('cols').split(',')]
                vals = [v.strip() for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", tuples[0].group('tuple'))]
                pairs = []
                for i in range(min(len(cols), len(vals))):
                    v = re.sub(r'::jsonb$', '', re.sub(r'^DATE\s+', '', vals[i], flags=re.I), flags=re.I)
                    if re.search(r"^gen_random_uuid\(\)$|^now\(\)$|^'?[0-9a-f]{8}-[0-9a-f]{4}-", v, re.I) or len(v) > 40:
                        continue   # skip generated and long values
                    pairs.append(f"{cols[i]}={v.strip(chr(39))}")
                s = ', '.join(pairs)
                if len(s) > a.sample_chars:
                    s = s[:a.sample_chars - 1] + '…'
                samples[tbl] = s
        for m in re.finditer(r'(?i)\b(?:DELETE\s+FROM|UPDATE)\s+([a-z_][a-z0-9_]*)', t):
            counts.setdefault(m.group(1), 0)
        tables = [x.strip() for x in hdr['tables'].split(',') if x.strip()] if 'tables' in hdr else list(counts)
        tables_text = ', '.join(f'`{x}` ({counts[x]})' if counts.get(x) else f'`{x}`' for x in tables)
        depends = hdr['depends'] if 'depends' in hdr and hdr['depends'] != '-' else ''
        rows.append({'Name': hdr['dataset'], 'Kind': kind, 'Purpose': hdr.get('purpose', ''), 'Tables': tables_text,
                     'TableList': tables, 'Depends': depends, 'Synthetic': synthetic, 'Samples': samples,
                     'Rel': rel, 'File': os.path.basename(f), 'Users': {}})

    # who loads it: @Sql("/datasets/<file>") or the dataset name / file name quoted in test sources, and the seed runner
    for f in source_files(root, ['*.kt', '*.java', '*.py']):
        if re.search(r'/scripts/docs/', posix(f), re.I):
            continue
        t = read_text(f)
        for r in rows:
            if re.search(re.escape(r['File']), t, re.I) or re.search('"' + re.escape(r['Name']) + '"', t, re.I):
                if f.lower().endswith('.py'):
                    who = os.path.basename(f)
                else:
                    cm = re.search(r'(?m)^\s*(?:class|object)\s+(\w+)', t)
                    who = cm.group(1) if cm else ''
                if who:
                    r['Users'][who] = True

    sb = [header('Datasets (BE)', 'scripts/db/seed + src/test/resources/datasets headers',
                 'Generated catalogue of the named synthetic datasets - local seeds and integration-test fixtures - with purpose, tables and row counts, dependencies, the tests that load them and one sample row per table; cite a dataset by name in Gherkin instead of describing rows.')]
    seeds = sum(1 for r in rows if r['Kind'] == 'seed')
    fix = sum(1 for r in rows if r['Kind'] == 'fixture')
    sb.append(f'{len(rows)} dataset(s): {seeds} seed(s) for the developer database (`scripts/db/seed-local.py`), {fix} integration-test fixture(s) (`@Sql("/datasets/<name>.sql")`). Row counts are tuples in `INSERT` statements; samples are the first row per table, shown only for datasets declared `synthetic: yes`.\n')
    sb.append('Use in test design: `Given dataset "<name>" is loaded` (step vocabulary in the docs repo, `test-design/README.md`); add explicit `Given` rows only for the values a scenario asserts on.\n\n')
    sb.append('| Dataset | Kind | Purpose | Tables (rows) | Depends on | Loaded by | Location |\n|---|---|---|---|---|---|---|\n')
    for r in sorted(rows, key=lambda r: sort_key(r['Name'])):
        users = ', '.join('`' + u + '`' for u in sorted(r['Users'], key=sort_key)) if r['Users'] else '(nothing yet)'
        flag = '' if r['Synthetic'] else ' **not declared synthetic - values withheld**'
        sb.append(f"| `{r['Name']}` | {r['Kind']} | {escape_cell(r['Purpose'])}{flag} | {r['Tables']} | {r['Depends']} | {users} | `{r['Rel']}` |\n")
    with_samples = [r for r in rows if r['Samples']]
    if with_samples:
        sb.append('\n## Sample rows\nFirst row of each table, synthetic datasets only; `id` columns and generated values omitted when long.\n\n')
        for r in sorted(with_samples, key=lambda r: sort_key(r['Name'])):
            for tbl, s in r['Samples'].items():
                sb.append(f"- `{r['Name']}` / `{tbl}`: {escape_cell(s)}\n")
    if unnamed:
        sb.append(f'\n_{unnamed} SQL file(s) outside the migrations have no `-- dataset:` header and are not catalogued._\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'datasets: {len(rows)} dataset(s) ({seeds} seed, {fix} fixture), {unnamed} unnamed sql file(s) -> {a.out}')


if __name__ == '__main__':
    main()
