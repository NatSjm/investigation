#!/usr/bin/env python3
"""Maps changed code paths (relative to FE/BE repo roots, prefixed be/ or fe/) to affected docs using docs-map.yml.
Examples:
  python3 scripts/map-paths.py be/core/src/main/kotlin/harbor/manager/Product1Manager.kt fe/src/features/stress/index.ts
  git diff --name-only origin/main | sed 's#^#be/#' | python3 scripts/map-paths.py
Output: one line per path `<path> -> <spec>, <spec>`; unmapped paths show `UNMAPPED`. --json for machine output."""
import argparse
import json
import os
import re
import sys

from _common import repo_root, read_text, utf8_stdout


def load_map(repo):
    """Minimal YAML reader for docs-map.yml (paths/specs lists only) - avoids external modules."""
    mappings = []
    ignore = []
    cur = None
    section = ''
    for l in re.split(r'\r?\n', read_text(os.path.join(repo, 'docs-map.yml'))):
        if re.match(r'^\s*#', l) or not l.strip():
            continue
        if re.match(r'^mappings:', l, re.I):
            section = 'map'
            continue
        if re.match(r'^ignore:', l, re.I):
            section = 'ignore'
            continue
        if section == 'ignore':
            m = re.match(r'^\s*-\s*"?([^"#]+)"?', l, re.I)
            if m:
                ignore.append(m.group(1).strip())
                continue
        if section == 'map':
            m = re.match(r'^\s*-\s*paths:\s*\[(.*)\]', l, re.I)
            if m:
                cur = {'Paths': [x for x in (p.strip().strip('"') for p in m.group(1).split(',')) if x], 'Specs': []}
                mappings.append(cur)
                continue
            m = re.match(r'^\s*specs:\s*\[(.*?)\]', l, re.I)
            if m and cur is not None:
                cur['Specs'] = [x for x in (p.strip().strip('"') for p in m.group(1).split(',')) if x]
    return mappings, ignore


def test_glob(glob, path):
    rx = '^' + re.escape(glob).replace(r'\*\*/', '(.*/)?').replace(r'\*\*', '.*').replace(r'\*', '[^/]*') + '$'
    return re.match(rx, path, re.I) is not None


def map_paths(repo, changed_paths):
    """[(path, [specs])]; unmapped paths get ['UNMAPPED']."""
    mappings, ignore = load_map(repo)
    out = []
    for p in changed_paths:
        p = p.strip().replace('\\', '/')
        if not p:
            continue
        if any(test_glob(g, p) for g in ignore):
            continue
        specs = []
        for m in mappings:
            if any(test_glob(g, p) for g in m['Paths']):
                for s in m['Specs']:
                    if s not in specs:
                        specs.append(s)
        out.append((p, specs if specs else ['UNMAPPED']))
    return out


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='*')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    paths = list(a.paths)
    if not paths and not sys.stdin.isatty():
        paths = [l for l in sys.stdin.read().splitlines() if l.strip()]
    hits = map_paths(repo_root(__file__), paths)
    if a.json:
        print(json.dumps([{'path': p, 'specs': s} for p, s in hits], indent=2))
        return
    for p, s in hits:
        print(f"{p} -> {', '.join(s)}")


if __name__ == '__main__':
    main()
