#!/usr/bin/env python3
"""Parameter catalogue: every key of the parameter-key enum (`parameters.enum_name`) with the values seeded by the
migrations (`INSERT INTO <parameters.table>`), the classes that read it and the validator that bounds it. Lets agents
answer "which admin parameters exist, what is the default, who reads it" without opening the enum, the migrations
and the services. The MEANING of a key is documentation, not code: `docs-repo/domain/calculations/*.md`
(`## Parameters`) and the admin feature spec; `validate-frontmatter.py` cross-checks both against this file.
Layout keys read from docs-gen.json: parameters.{enum_name, table, key_column, value_column, scope_columns,
valid_from_column, validator_layer}, migrations, modules, source_root, test_pattern, exclude_paths."""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True  # no __pycache__ next to the scripts
from _common import (read_text, write_text, source_files, resolve_out, rel_path, line_number, header,
                     escape_cell, posix, sort_key, utf8_stdout, load_config, module_dirs, main_sources, package_of,
                     base_package, layer_of, module_of)

DEFAULTS = {
    'modules': [], 'source_root': 'src/main/kotlin', 'base_package': '', 'layers': {}, 'test_pattern': '', 'exclude_paths': [],
    'migrations': {'dir_pattern': '/db/migration/', 'file_patterns': ['V*.sql', 'R*.sql']},
    'parameters': {'enum_name': 'ParameterKey', 'table': 'parameter_set', 'key_column': 'key', 'value_column': 'value',
                   'scope_columns': ['scope_product_group', 'scope_country', 'scope_value'], 'valid_from_column': 'valid_from',
                   'validator_layer': 'validator'},
}


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out', default='docs/_generated/parameters.md')
    ap.add_argument('--config', default='')
    ap.add_argument('--enum-name', default='', help='overrides parameters.enum_name')
    ap.add_argument('--table', default='', help='overrides parameters.table')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    cfg = load_config(root, DEFAULTS, a.config)
    prm = cfg['parameters']
    enum_name = a.enum_name or prm['enum_name']
    table = a.table or prm['table']
    key_col, val_col, from_col = prm['key_column'].lower(), prm['value_column'].lower(), prm['valid_from_column'].lower()
    scope_cols = [c.lower() for c in prm['scope_columns']]
    mig = cfg['migrations']
    modules = module_dirs(root, cfg)
    files = main_sources(root, cfg, modules)

    # 1. keys: enum constants with their string key
    enum_files = [f for f in files if os.path.basename(f) == f'{enum_name}.kt' or os.path.basename(f) == f'{enum_name}.java']
    enum_file = enum_files[0] if enum_files else None
    keys = {}
    enum_rel = ''
    if enum_file:
        enum_rel = rel_path(root, enum_file)
        et = read_text(enum_file)
        for m in re.finditer(r'(?m)^\s*(?P<const>[A-Z][A-Z0-9_]*)\s*\(\s*"(?P<key>[^"]+)"\s*[,)]', et):
            keys[m.group('key')] = {'Const': m.group('const'), 'Line': line_number(et, m.start()),
                                   'Seeds': [], 'Readers': {}, 'Validators': {}}

    # 2. seeds: INSERT INTO <table> (...) VALUES (...), (...) in the migrations; column order taken from the column list
    unknown_seeds = {}
    seed_count = 0
    insert_rx = re.compile(r'(?is)INSERT\s+INTO\s+' + re.escape(table) + r'\s*\((?P<cols>[^)]*)\)\s*VALUES\s*(?P<vals>.*?);')
    sql_files = sorted((f for f in source_files(root, mig['file_patterns']) if re.search(re.escape(mig['dir_pattern']), posix(f), re.I)),
                       key=lambda p: sort_key(os.path.basename(p)))
    for f in sql_files:
        t = read_text(f)
        rel = rel_path(root, f)
        for ins in insert_rx.finditer(t):
            cols = [c.strip().lower() for c in ins.group('cols').split(',')]
            ix = {c: i for i, c in enumerate(cols)}
            if key_col not in ix or val_col not in ix:
                continue
            for tup in re.finditer(r'\((?P<tuple>(?:[^()]|\([^()]*\))*)\)', ins.group('vals')):
                cells = [re.sub(r'^DATE\s+', '', c.strip(), flags=re.I).strip("'") for c in tup.group('tuple').split(',')]

                def cell(col):
                    if col in ix and ix[col] < len(cells):
                        v = cells[ix[col]]
                        return '' if v == 'NULL' else v
                    return ''
                key = cell(key_col)
                scope = [x for x in (cell(c) for c in scope_cols) if x]
                scope_text = '/'.join(scope) if scope else 'global'
                frm = cell(from_col) if from_col else ''
                seed = f"{scope_text} = {cell(val_col)}" + (f' (from {frm})' if frm else '')
                seed_count += 1
                if key in keys:
                    keys[key]['Seeds'].append(seed)
                else:
                    unknown_seeds[key] = f"{rel}:{line_number(t, ins.start('vals') + tup.start())}"

    # 3. readers and validators: `<Enum>.CONST` references outside the enum
    const_to_key = {v['Const']: k for k, v in keys.items()}
    ref_rx = re.compile(re.escape(enum_name) + r'\.(?P<const>[A-Z][A-Z0-9_]*)\b')
    base_pkg = {}
    for f in files:
        if enum_file and f == enum_file:
            continue
        t = read_text(f)
        if not re.search(re.escape(enum_name) + r'\.', t, re.I):
            continue
        cm = re.search(r'(?m)^\s*(?:class|object|interface)\s+(\w+)', t)
        cls = cm.group(1) if cm else os.path.splitext(os.path.basename(f))[0]
        mod = module_of(root, f, modules)
        if mod not in base_pkg:
            base_pkg[mod] = base_package(cfg, [package_of(read_text(x)) for x in files if module_of(root, x, modules) == mod])
        layer = layer_of(package_of(t), base_pkg[mod], cfg['layers'])
        bucket = 'Validators' if layer.split('/')[0] == prm['validator_layer'] else 'Readers'
        for m in ref_rx.finditer(t):
            c = m.group('const')
            if c in const_to_key:
                keys[const_to_key[c]][bucket][cls] = True

    # 4. render
    scope_desc = ' / '.join(scope_cols) if scope_cols else 'none'
    sb = [header('Parameters (BE)', f'{enum_name} + {table} seeds',
                 f'Generated catalogue of the admin parameters: every {enum_name} key with its seeded defaults per scope, the classes that read it and the validator that bounds it; the meaning of a key is documented in domain/calculations and the admin spec.')]
    sb.append(f'{len(keys)} key(s), {seed_count} seeded value(s). Scope = {scope_desc}; `global` = no scope. Lookups take the most specific scope in force' + (f', then the newest `{from_col}`' if from_col else '') + '.\n')
    sb.append('Meaning, unit and business rule of each key: `domain/calculations/*.md` (`## Parameters`) and the admin feature spec; `scripts/validate-frontmatter.py` checks that every key below is documented there and that documents name only keys that exist here.\n\n')
    sb.append('| Key | Constant | Seeded defaults | Read by | Validated by | Location |\n|---|---|---|---|---|---|\n')
    for k in sorted(keys, key=sort_key):
        e = keys[k]
        seeds = '; '.join(sorted(e['Seeds'], key=sort_key)) if e['Seeds'] else '(no seed - must be created on the admin page)'
        readers = ', '.join('`' + r + '`' for r in sorted(e['Readers'], key=sort_key)) if e['Readers'] else '(no reader)'
        validators = ', '.join('`' + v + '`' for v in sorted(e['Validators'], key=sort_key))
        sb.append(f"| `{k}` | `{e['Const']}` | {escape_cell(seeds)} | {readers} | {validators} | `{enum_rel}:{e['Line']}` |\n")
    if unknown_seeds:
        sb.append('\n## Seeded keys without an enum constant\n')
        sb.append(f'Rows in the migrations whose key is not in `{enum_name}` - unreadable by the application until the constant exists.\n\n')
        for k in sorted(unknown_seeds, key=sort_key):
            sb.append(f'- `{k}` - `{unknown_seeds[k]}`\n')
    if not enum_file:
        sb.append(f'\n_No `{enum_name}` enum found under the source roots; set `parameters.enum_name` in docs-gen.json._\n')
    write_text(resolve_out(root, a.out), ''.join(sb))
    print(f'parameters: {len(keys)} key(s), {seed_count} seed(s), {len(unknown_seeds)} unknown seeded key(s) -> {a.out}')


if __name__ == '__main__':
    main()
