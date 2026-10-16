#!/usr/bin/env python3
"""Runs all BE generators and writes docs/_generated/index.md (OKF-style reserved index for progressive disclosure).
Also refreshes the database documentation folder (`db_docs.dir`, default docs/db) with gen-db-docs.py unless
`db_docs.generate` is false (a database tool writes that folder) or the script is in `skip_generators`.
The generators read the repository layout from scripts/docs/docs-gen.json (modules, base package, layers, contract
paths, annotations ...); --config points them at another file.
--check: exit 1 if any generated file would change (CI freshness gate)."""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

from _common import read_text, write_text, utf8_stdout, load_config

GENERATORS = [
    ('gen-codebase-map.py', 'codebase-map.md'),
    ('gen-components.py', 'components.md'),
    ('gen-api-index.py', 'api-index.md'),
    ('gen-events.py', 'events.md'),
    ('gen-db-schema.py', 'db-schema.md'),
    ('gen-jobs.py', 'jobs.md'),
    ('gen-docs-tags.py', 'docs-tags.md'),
    ('gen-parameters.py', 'parameters.md'),
    ('gen-datasets.py', 'datasets.md'),
]
DEFAULTS = {'rest': {'open_api': ''}, 'asyncapi': '', 'external_contracts_dir': '', 'parameters': {'enum_name': 'ParameterKey'},
            'datasets': {'seed_dirs': ['scripts/db/seed'], 'fixture_dirs': []}, 'entry_layer': 'manager',
            'db_docs': {'dir': 'docs/db', 'generate': True}}

INDEX = """# Generated code maps

Read these before opening source. Each file is a few hundred tokens.
{contracts}
- [codebase-map.md](codebase-map.md): modules, technical layers with their classes, resource folders
- [components.md](components.md): one row per class - layer, stereotype, injected dependencies, tables, @docs, file:line
- [api-index.md](api-index.md): REST operations from the contract (method, path, operationId, handler, file:line)
- [events.md](events.md): Kafka topics with producers/consumers
- [db-schema.md](db-schema.md): tables and columns from migrations, ER diagram
- [jobs.md](jobs.md): scheduled jobs with their cron triggers
- [docs-tags.md](docs-tags.md): spec ID (`@docs`) to code location
- [parameters.md](parameters.md): admin parameter catalogue - every `{enum}` with seeded defaults per scope, readers and validator
- [datasets.md](datasets.md): named synthetic datasets (local seeds, integration-test fixtures) with tables, row counts, loaders and a sample row
- `{db_dir}/` (outside this folder): the database documentation - `schema.json`, one page per table with the column comments and relations, ER diagram

The folder layout the generators assume (modules, base package, layers, contract paths) is in `scripts/docs/docs-gen.json`;
the business context of a class is its name prefix (docs repo `contexts.yml`), read the `{entry}` of a context first.
"""


def norm(s):
    return re.sub(r'(?m)^  at: .*$', '', s).replace('\r', '')


def norm_db(s):
    """db docs: the generation date is the only line that may differ between two runs."""
    return re.sub(r'(?i)("generatedAt": "|on )\d{4}-\d{2}-\d{2}', r'\1<date>', s.replace('\r', ''))


def tree(d):
    out = {}
    for dp, dn, fn in os.walk(d):
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, d).replace(os.sep, '/')] = p
    return out


def contracts_line(cfg):
    parts = []
    if cfg['rest'].get('open_api'):
        parts.append(f"`{cfg['rest']['open_api']}` (REST; FE client and BE interfaces are generated from it)")
    if cfg.get('asyncapi'):
        parts.append(f"`{cfg['asyncapi']}` (Kafka)")
    if cfg.get('external_contracts_dir'):
        parts.append(f"`{cfg['external_contracts_dir']}/*.yaml` (external services)")
    return ('Contracts: ' + ',\n'.join(parts) + '.\n') if parts else ''


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', default='.')
    ap.add_argument('--out-dir', default='docs/_generated')
    ap.add_argument('--config', default='')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    here = os.path.dirname(os.path.abspath(__file__))
    cfg = load_config(root, DEFAULTS, a.config)
    target = os.path.join(root, a.out_dir)
    work = tempfile.mkdtemp(prefix='gen-docs-') if a.check else target
    os.makedirs(work, exist_ok=True)
    rel = work if a.check else a.out_dir
    extra = ['--config', a.config] if a.config else []
    skip = set(cfg.get('skip_generators', []))
    skipped_outputs = []
    for script, out in GENERATORS:
        if script in skip:
            skipped_outputs.append(out)
            print(f'{script}: skipped (skip_generators in docs-gen.json)')
            continue
        r = subprocess.run([sys.executable, os.path.join(here, script), '--root', root, '--out', rel + '/' + out] + extra)
        if r.returncode:
            sys.exit(r.returncode)
    db_cfg = cfg['db_docs']
    db_on = db_cfg.get('generate', True) and 'gen-db-docs.py' not in skip
    if db_on:
        db_out = os.path.join(tempfile.mkdtemp(prefix='gen-db-docs-'), 'db') if a.check else db_cfg['dir']
        r = subprocess.run([sys.executable, os.path.join(here, 'gen-db-docs.py'), '--root', root, '--out', db_out] + extra)
        if r.returncode:
            sys.exit(r.returncode)
    else:
        print(f"gen-db-docs.py: skipped ({db_cfg['dir']} is written by your database documentation tool)")
    index = INDEX.format(contracts=contracts_line(cfg), enum=cfg['parameters']['enum_name'], entry=cfg['entry_layer'], db_dir=db_cfg['dir'])
    index = '\n'.join(line for line in index.split('\n') if not any(f'[{o}]' in line for o in skipped_outputs))
    write_text(os.path.join(work, 'index.md'), index)
    if a.check:
        diff = 0
        for name in sorted(os.listdir(work), key=str.lower):
            cur = os.path.join(target, name)
            a_text = norm(read_text(cur)) if os.path.isfile(cur) else ''
            b_text = norm(read_text(os.path.join(work, name)))
            if a_text != b_text:
                print(f'STALE: {a.out_dir}/{name}')
                diff += 1
        shutil.rmtree(work, ignore_errors=True)
        if db_on:
            cur_t, new_t = tree(os.path.join(root, db_cfg['dir'])), tree(db_out)
            for name in sorted(set(cur_t) | set(new_t), key=str.lower):
                a_text = norm_db(read_text(cur_t[name])) if name in cur_t else ''
                b_text = norm_db(read_text(new_t[name])) if name in new_t else ''
                if a_text != b_text:
                    print(f"STALE: {db_cfg['dir']}/{name}")
                    diff += 1
            shutil.rmtree(os.path.dirname(db_out), ignore_errors=True)
        if diff:
            print(f'{diff} generated file(s) out of date. Run scripts/docs/gen-all.py', file=sys.stderr)
            sys.exit(1)
        print('generated docs up to date')


if __name__ == '__main__':
    main()
