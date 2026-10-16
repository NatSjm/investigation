#!/usr/bin/env python3
"""Token-budget lint: fails when source files exceed a line cap (Copilot pulls whole files on #file / open editor).
No external tools. Put in CI as a warn-first, then blocking gate. Grandfather existing offenders via --baseline.
Used by harbor-backend (400 lines, *.kt) and harbor-frontend (300 lines, *.ts/*.tsx); copied to scripts/ by apply-kit.py.
Examples:
  python3 scripts/check-file-size.py --root . --max-lines 400 --include '*.kt' --baseline .filesize-baseline.txt
  python3 scripts/check-file-size.py --root . --max-lines 300 --include '*.ts' '*.tsx' --baseline .filesize-baseline.txt --write-baseline"""
import argparse
import os
import re
import sys


def like(s, pattern):
    rx = '^' + ''.join('.*' if c == '*' else '.' if c == '?' else re.escape(c) for c in pattern) + '$'
    return re.match(rx, s, re.I) is not None


def split_list(values):
    out = []
    for v in values or []:
        out.extend(x.strip() for x in v.split(',') if x.strip())
    return out


def count_lines(path):
    with open(path, 'r', encoding='utf-8-sig', errors='replace', newline='') as f:
        text = f.read()
    if not text:
        return 0
    parts = re.split(r'\r\n|\r|\n', text)
    return len(parts) - (1 if parts[-1] == '' else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default='.')
    ap.add_argument('--max-lines', type=int, default=400)
    ap.add_argument('--include', nargs='+', default=['*.kt', '*.java', '*.ts', '*.tsx'])
    ap.add_argument('--exclude-dirs', nargs='+', default=['target', 'build', 'node_modules', '.git', 'dist', 'coverage', 'generated', '_generated', 'openapi'])
    ap.add_argument('--baseline', default='')
    ap.add_argument('--write-baseline', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    include = split_list(a.include)
    excluded = set(d.lower() for d in split_list(a.exclude_dirs))
    known = set()
    if a.baseline and os.path.isfile(os.path.join(root, a.baseline)):
        with open(os.path.join(root, a.baseline), encoding='utf-8-sig') as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith('#'):
                    known.add(s)

    offenders = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((d for d in dirnames if d.lower() not in excluded), key=str.lower)
        for name in sorted(filenames, key=str.lower):
            if not any(like(name, p) for p in include):
                continue
            full = os.path.join(dirpath, name)
            n = count_lines(full)
            if n > a.max_lines:
                rel = os.path.relpath(full, root).replace('\\', '/')
                offenders.append({'File': rel, 'Lines': n, 'Grandfathered': rel in known})
    offenders.sort(key=lambda o: -o['Lines'])

    if a.write_baseline:
        lines = [f'# files allowed to exceed {a.max_lines} lines (shrink over time; do not add)'] + [o['File'] for o in offenders]
        with open(os.path.join(root, a.baseline), 'w', encoding='utf-8', newline='') as f:
            f.write('\n'.join(lines) + '\n')
        print(f'baseline written: {len(offenders)} file(s)')
        return 0

    for o in offenders:
        print(f"{o['Lines']:6}  {o['File']}{'  (baseline)' if o['Grandfathered'] else ''}")
    new = [o for o in offenders if not o['Grandfathered']]
    if new:
        print(f'{len(new)} file(s) exceed {a.max_lines} lines (not in baseline). Split them - large files cost tokens on every Copilot read.', file=sys.stderr)
        return 1
    print(f'file-size: OK ({len(offenders)} grandfathered)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
