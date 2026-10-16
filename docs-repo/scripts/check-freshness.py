#!/usr/bin/env python3
"""CI gate for FE/BE PRs: if a mapped code path changed, the linked spec must have last_verified >= PR base date,
unless the PR carries label 'docs-not-affected'.
Example:
  python3 scripts/check-freshness.py --changed-paths $(git diff --name-only origin/main | sed 's#^#be/#') --since-date 2026-09-30"""
import argparse
import glob
import importlib.util
import os
import re
import sys
from datetime import date, datetime, timedelta

from _common import repo_root, read_text, utf8_stdout


def load_map_paths():
    spec = importlib.util.spec_from_file_location('map_paths', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map-paths.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--changed-paths', nargs='+', required=True)
    ap.add_argument('--since-date', default=(date.today() - timedelta(days=30)).isoformat())
    ap.add_argument('--allow-unmapped', action='store_true')
    a = ap.parse_args()
    repo = repo_root(__file__)
    since = datetime.fromisoformat(a.since_date).date()
    changed = [x for v in a.changed_paths for x in v.split(',') if x.strip()]
    hits = load_map_paths().map_paths(repo, changed)
    stale = []
    unmapped = []
    backlog = []
    for path, specs in hits:
        if 'UNMAPPED' in specs:
            unmapped.append(path)
            continue
        if 'BACKLOG' in specs:   # mapped context without a spec yet: nothing to verify, never a failure
            backlog.append(path)
            continue
        for spec in specs:
            for f in sorted(glob.glob(os.path.join(repo, spec))):
                if not os.path.isfile(f):
                    continue
                m = re.search(r'last_verified:\s*(\d{4}-\d{2}-\d{2})', read_text(f), re.I)
                lv = date.fromisoformat(m.group(1)) if m else None
                if lv is None or lv < since:
                    stale.append(f"{path} -> {spec} (last_verified={lv.isoformat() if lv else ''})")
    for s in dict.fromkeys(stale):
        print(f'STALE  {s}')
    for b in backlog:
        print(f'BACKLOG {b}')
    for u in unmapped:
        print(f'UNMAPPED {u}')
    if stale or (unmapped and not a.allow_unmapped):
        sys.exit(1)
    print('Freshness OK')


if __name__ == '__main__':
    main()
