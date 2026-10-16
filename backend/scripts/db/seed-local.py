#!/usr/bin/env python3
"""Loads the named datasets of scripts/db/seed/*.sql into the local database (docker compose postgres by default).
--dataset: one or more dataset names (`-- dataset:` header). Default: every seed file, in file-name order.
--fixtures: also load the integration-test fixtures from harbor-core/src/test/resources/datasets (same header convention).
Examples:
  python3 scripts/db/seed-local.py
  python3 scripts/db/seed-local.py --dataset reference-clients p1-baseline-12m
  python3 scripts/db/seed-local.py --fixtures --database harbor_test"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sql_files(d):
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d), key=str.lower) if f.lower().endswith('.sql')]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dataset', nargs='*', default=[])
    ap.add_argument('--fixtures', action='store_true')
    ap.add_argument('--database', default='harbor')
    ap.add_argument('--compose-file', default=os.path.join(HERE, '../../init_docker_compose/docker-compose.yml'))
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(os.path.join(HERE, '../..'))
    wanted = []
    for v in a.dataset:
        wanted.extend(x.strip() for x in v.split(',') if x.strip())

    files = sql_files(os.path.join(HERE, 'seed'))
    if a.fixtures:
        files += sql_files(os.path.join(root, 'harbor-core/src/test/resources/datasets'))

    selected = []
    for f in files:
        with open(f, encoding='utf-8-sig', errors='replace') as fh:
            head = ''.join(fh.readline() for _ in range(10))
        m = re.search(r'(?m)^--\s*dataset:\s*(\S+)', head, re.I)
        name = m.group(1) if m else os.path.splitext(os.path.basename(f))[0]
        if not wanted or name in wanted:
            selected.append((name, f))
    if not selected:
        print(f"no dataset matched: {', '.join(wanted)}", file=sys.stderr)
        return 1

    for name, f in selected:
        rel = os.path.relpath(f, root).replace('\\', '/')
        if a.dry_run:
            print(f'would load {name}  ({rel})')
            continue
        print(f'loading {name}  ({rel})')
        # psql inside the compose container: no client installation needed on the developer machine
        with open(f, 'rb') as fh:
            r = subprocess.run(['docker', 'compose', '-f', a.compose_file, 'exec', '-T', 'postgres', 'psql',
                                '-v', 'ON_ERROR_STOP=1', '-q', '-U', 'harbor', '-d', a.database], stdin=fh)
        if r.returncode:
            print(f'psql failed for {name}', file=sys.stderr)
            return r.returncode
    print(f'done: {len(selected)} dataset(s) into {a.database}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
